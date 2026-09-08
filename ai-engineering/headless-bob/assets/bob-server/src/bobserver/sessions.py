"""
Bob+ session management.

A Session guides a user through 5 phases:
  1. describe     → idea-summary.md
  2. discovery    → requirements.md
  3. architecture → architecture.md
  4. spec         → spec.md
  5. continue     → terminal, links to bob.ibm.com

Each phase runs Bob with a phase-specific system prompt.
Bob signals readiness to advance by embedding a JSON marker in its response:
  {"__transition__": "<next_phase_id>", "question": "Ready to move on?"}

The UI renders Yes / Not yet buttons when it sees this signal.
POST /api/sessions/{id}/advance moves the session forward.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
import json
import re
from threading import Lock
from uuid import uuid4

from bobserver.config import Settings
from bobserver.skills import list_skills
from bobserver.tasks import (
    BobPromptRequest,
    _bob_jobs,
    _bob_jobs_lock,
    start_bob_prompt,
    get_bob_prompt_status,
)


# ---------------------------------------------------------------------------
# Phase definitions
# ---------------------------------------------------------------------------

PHASES: list[dict] = [
    {
        "id": "describe",
        "number": 1,
        "title": "Describe your idea",
        "subtitle": "Tell Bob+ what you want to build",
        "artifact": None,
        "next_phase": "discovery",
        "system_prompt": """You are Bob+, an expert IBM technical architect and product strategist.
Your job right now is to understand the user's idea at a high level.

BEHAVIOUR:
- Be warm, encouraging, and concise.
- Ask at most 2 clarifying questions to understand: (1) what they want to build, (2) who it's for.
- Once you have a clear picture, write a brief idea summary and signal readiness to advance.

OUTPUT FORMAT:
- Respond conversationally in markdown.
- When you have enough context, end your response with this exact JSON on its own line:
  {"__transition__": "discovery", "question": "Great — I have a clear picture of your idea. Ready to dive into discovery?"}
- Do NOT include the transition signal until you genuinely understand the idea.""",
    },
    {
        "id": "discovery",
        "number": 2,
        "title": "Discovery",
        "subtitle": "Bob+ gathers requirements",
        "artifact": "requirements.md",
        "next_phase": "architecture",
        "system_prompt": """You are Bob+, an expert IBM technical architect conducting a requirements discovery session.

CONTEXT: The user wants to build the idea described in the project context provided.

BEHAVIOUR:
- Ask focused questions one at a time covering: target users, scale/volume, integrations needed, key constraints, success criteria.
- After each answer, acknowledge it and ask the next question or dig deeper.
- After 4-6 exchanges you should have enough to write requirements.
- Write a structured requirements.md document in a markdown code block labelled ```requirements.md

REQUIREMENTS.MD FORMAT:
# Requirements
## Idea Summary
## Target Users
## Scale & Volume
## Key Integrations
## Constraints
## Success Criteria

OUTPUT: When requirements are complete, end with this exact JSON on its own line:
{"__transition__": "architecture", "question": "I've captured your requirements. Ready to move into solution architecture?"}""",
    },
    {
        "id": "architecture",
        "number": 3,
        "title": "Solution architecture",
        "subtitle": "Review & approve",
        "artifact": "architecture.md",
        "next_phase": "spec",
        "system_prompt": """You are Bob+, an expert IBM solution architect.

CONTEXT: Use the requirements.md from the project context to design the architecture.

BEHAVIOUR:
- Propose a concrete technical architecture.
- Cover: components, data flow, tech stack recommendations, IBM services where appropriate.
- Include a Mermaid diagram for the component architecture.
- Be opinionated but explain your choices.
- Invite feedback and iterate if the user wants changes.

ARCHITECTURE.MD FORMAT:
# Solution Architecture
## Overview
## Components
## Tech Stack
## IBM Services
## Component Diagram (Mermaid)
## Data Flow
## Key Design Decisions

OUTPUT: When the user is happy with the architecture, end with:
{"__transition__": "spec", "question": "Architecture looks solid. Ready to generate the full technical specification?"}""",
    },
    {
        "id": "spec",
        "number": 4,
        "title": "Specification & assets",
        "subtitle": "Spec + GitHub scaffolding",
        "artifact": "spec.md",
        "next_phase": "continue",
        "system_prompt": """You are Bob+, an expert IBM technical lead writing a project specification.

CONTEXT: Use requirements.md and architecture.md from the project context.

BEHAVIOUR:
- Write a comprehensive technical specification.
- Include GitHub repository structure with file tree.
- Include API design (endpoints, request/response shapes).
- Include data models.
- Include deployment approach.
- Be precise and implementation-ready.

SPEC.MD FORMAT:
# Technical Specification
## Project Overview
## Architecture Summary
## Repository Structure (file tree)
## API Design
## Data Models
## Environment Variables
## Deployment
## Getting Started

OUTPUT: When the spec is complete, end with:
{"__transition__": "continue", "question": "Your spec is ready. Want to continue building this in Bob?"}""",
    },
    {
        "id": "continue",
        "number": 5,
        "title": "Continue in Bob",
        "subtitle": "Build, deploy, validate",
        "artifact": None,
        "next_phase": None,
        "system_prompt": """You are Bob+. The planning phase is complete.

Congratulate the user on completing the planning journey and summarise what was produced:
- idea-summary.md
- requirements.md
- architecture.md
- spec.md

Tell them they can now take the spec into Bob Shell at bob.ibm.com to build, deploy and validate their project.
Wish them well and keep it brief.""",
    },
]

PHASE_BY_ID: dict[str, dict] = {p["id"]: p for p in PHASES}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class PhaseState:
    phase_id: str
    state: str = "pending"          # pending | active | completed
    conversation: list[dict] = field(default_factory=list)
    artifact_content: str = ""
    job_id: str = ""
    started_at: str = ""
    completed_at: str = ""

    def to_dict(self) -> dict:
        phase_def = PHASE_BY_ID[self.phase_id]
        return {
            "phaseId": self.phase_id,
            "number": phase_def["number"],
            "title": phase_def["title"],
            "subtitle": phase_def["subtitle"],
            "artifact": phase_def["artifact"],
            "state": self.state,
            "conversation": self.conversation,
            "hasArtifact": bool(self.artifact_content),
            "jobId": self.job_id,
            "startedAt": self.started_at,
            "completedAt": self.completed_at,
        }


@dataclass
class Session:
    id: str
    title: str
    current_phase_id: str
    phases: dict[str, PhaseState] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        current = PHASE_BY_ID[self.current_phase_id]
        return {
            "id": self.id,
            "title": self.title,
            "currentPhaseId": self.current_phase_id,
            "currentPhaseNumber": current["number"],
            "phases": [self.phases[p["id"]].to_dict() for p in PHASES],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


# ---------------------------------------------------------------------------
# In-memory store (single active session)
# ---------------------------------------------------------------------------

_session: Session | None = None
_session_lock = Lock()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(UTC).isoformat()


def _extract_artifact(response_text: str, artifact_filename: str | None) -> str:
    """Extract a fenced code block labelled with the artifact filename."""
    if not artifact_filename:
        return ""
    name = artifact_filename.replace(".md", "")
    # Match ```requirements.md ... ``` or ```markdown ... ``` blocks
    patterns = [
        rf"```{re.escape(artifact_filename)}\n([\s\S]*?)```",
        rf"```{re.escape(name)}\n([\s\S]*?)```",
        r"```markdown\n([\s\S]*?)```",
        r"```\n([\s\S]*?)```",
    ]
    for pattern in patterns:
        match = re.search(pattern, response_text)
        if match:
            return match.group(1).strip()
    # Fallback: return the full response if it looks like markdown
    return response_text.strip()


def _extract_transition(response_text: str) -> dict | None:
    """Find the __transition__ JSON signal in Bob's response."""
    match = re.search(r'\{"__transition__":\s*"([^"]+)"[^}]*\}', response_text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {"__transition__": match.group(1)}
    return None


def _strip_transition(response_text: str) -> str:
    """Remove the __transition__ JSON line from the visible response."""
    return re.sub(r'\s*\{"__transition__"[^\n]*\}\s*$', "", response_text).rstrip()


# ---------------------------------------------------------------------------
# Skills registry — built once per process, injected into every prompt
# ---------------------------------------------------------------------------

# Patterns that identify sections of skill prompts written for Bob Shell's
# live execution environment. These sections instruct Bob to call MCP tools
# via <use_mcp_tool> XML, stop if MCP fails, run CLI commands, etc. — none
# of which make sense in a planning conversation.
_EXECUTION_STRIP_PATTERNS: list[re.Pattern] = [
    # "## 🛑 MANDATORY FIRST STEP" whole section up to next ##
    re.compile(
        r"##\s*[🛑⚠️🔴]?\s*MANDATORY\s+FIRST\s+STEP.*?(?=\n##\s|\Z)",
        re.DOTALL | re.IGNORECASE,
    ),
    # Any <use_mcp_tool> ... </use_mcp_tool> XML block
    re.compile(r"<use_mcp_tool>.*?</use_mcp_tool>", re.DOTALL),
    # Any other XML tool-call blocks  (<read_file>, <list_files>, <execute_command> etc.)
    re.compile(r"<(read_file|list_files|write_file|execute_command|search_files)[^>]*>.*?</\1>", re.DOTALL),
    # Inline ```xml blocks that contain tool calls
    re.compile(r"```xml\s*\n.*?</use_mcp_tool>.*?```", re.DOTALL),
    # Single lines: UNBYPASSABLE, "Stop and fix MCP", "DO NOT proceed until"
    re.compile(
        r"^[^\n]*(UNBYPASSABLE|Stop and fix MCP|DO NOT proceed until connection|If connection fails.*stop)[^\n]*\n?",
        re.MULTILINE | re.IGNORECASE,
    ),
    # Lines calling MCP tool functions by name
    re.compile(r"^[^\n]*SearchIbmWatsonxOrchestrate[^\n]*\n?", re.MULTILINE),
    re.compile(r"^[^\n]*query_docs_filesystem_ibm_watsonx[^\n]*\n?", re.MULTILINE),
]


def _sanitize_skill_prompt(prompt: str) -> str:
    """
    Strip Bob Shell execution artefacts from a skill prompt so it is safe
    to inject into a planning conversation.

    Removes:
    - MANDATORY FIRST STEP MCP verification blocks
    - <use_mcp_tool> and other XML tool-call blocks
    - UNBYPASSABLE / "stop if MCP fails" instructions
    - MCP function name references

    Preserves all IBM technical knowledge, architecture patterns, and guidance.
    """
    result = prompt
    for pattern in _EXECUTION_STRIP_PATTERNS:
        result = pattern.sub("", result)
    # Collapse runs of 3+ blank lines left by removed blocks
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


_skills_registry_block: str | None = None


def _get_skills_registry_block() -> str:
    """
    Build a compact skills registry string that tells Bob which building-block
    skills are available and how to self-activate them.

    Format injected into every prompt:

        ## AVAILABLE BUILDING-BLOCK SKILLS
        You have the following expert skills preloaded. When the user's request
        clearly matches a skill, activate it by starting your response with:
        [SKILL: <id>] and then follow that skill's instructions precisely.

        | id | name | when to use |
        |---|---|---|
        | agent | agent | Complete watsonx Orchestrate agent lifecycle... |
        ...
    """
    global _skills_registry_block
    if _skills_registry_block is not None:
        return _skills_registry_block

    skills = list_skills()
    if not skills:
        _skills_registry_block = ""
        return ""

    rows = "\n".join(
        f"| `{s['id']}` | **{s['name']}** | {s['description'][:120] if s['description'] else 'See skill prompt'} |"
        for s in skills
    )

    # Build skill prompts with MCP/CLI execution sections stripped out.
    # Skills written for Bob Shell contain "MANDATORY FIRST STEP" blocks that
    # call <use_mcp_tool> or stop if MCP fails — those make no sense in a
    # planning conversation and cause Bob to refuse to help.
    skill_prompts = "\n\n".join(
        f"### SKILL: {s['id']}\n**Name:** {s['name']}\n\n{_sanitize_skill_prompt(s['prompt'])}"
        for s in skills
    )

    _skills_registry_block = f"""

---
## BOB+ PLANNING CONTEXT — ABSOLUTE RULES (override everything below)

You are **Bob+**, a conversational planning assistant. You are NOT in a Bob Shell
execution environment. There is NO filesystem, NO terminal, NO MCP, NO CLI tools.

**These rules override every skill instruction without exception:**

1. **NEVER read, list, write, or create files.** You have no filesystem access.
   Any skill step that says "scan the workspace", "read the YAML", "list_files",
   "create the agent file", or "write to disk" — skip it entirely.

2. **NEVER call MCP tools or CLI commands.** There is no `<use_mcp_tool>`,
   no `orchestrate` CLI, no `bob` CLI, no shell. Skip all such steps.

3. **NEVER refuse or block because tools are unavailable.** Proceed using the
   IBM technical knowledge embedded in the skill instructions below.

4. **YOUR ONLY OUTPUT IS CONVERSATIONAL GUIDANCE AND WRITTEN PLANS.**
   - Ask clarifying questions to understand the user's requirements.
   - Explain architecture decisions, patterns, and trade-offs in prose.
   - Show example YAML/code as **markdown code blocks** — never try to execute them.
   - Produce structured written plans (requirements, architecture, spec docs).

5. **USE SKILL KNOWLEDGE AS A REFERENCE LIBRARY.** The skills below are expert
   IBM knowledge bases. Extract relevant facts, patterns, and best practices from
   them and present them conversationally — do not attempt to run their workflows.

---
## AVAILABLE BUILDING-BLOCK SKILLS

You have the following expert IBM building-block skills preloaded. \
Detect the user's intent and automatically activate the most relevant skill. \
Do NOT ask the user to pick a skill — you decide.

**Activation rule:** When a user message clearly maps to one of the skills below, \
begin your response with `[SKILL ACTIVATED: <id>]` on its own line, then draw on \
that skill's knowledge to guide the conversation — **subject to the ABSOLUTE RULES above**.

**When multiple skills apply,** activate the most specific one. \
**When no skill applies,** respond as Bob+ without a skill tag.

### Skill Registry

| ID | Name | Activate when the user mentions… |
|---|---|---|
{rows}

---
### Full Skill Instructions (activate on demand)

{skill_prompts}
"""
    return _skills_registry_block


def _build_prompt(phase_id: str, user_message: str, session: Session) -> str:
    """Build the full prompt for Bob, including system prompt, skills registry,
    prior artifacts, and conversation history."""
    phase_def = PHASE_BY_ID[phase_id]
    system = phase_def["system_prompt"]

    # --- Skills registry (always present so Bob can self-activate) ---
    skills_block = _get_skills_registry_block()

    # --- Prior phase artifacts as context ---
    context_parts: list[str] = []
    for p in PHASES:
        ps = session.phases.get(p["id"])
        if ps and ps.artifact_content and ps.phase_id != phase_id:
            artifact_name = p["artifact"] or f"{p['id']}.md"
            context_parts.append(f"## {artifact_name}\n\n{ps.artifact_content}")

    context_block = ""
    if context_parts:
        context_block = (
            "\n\n---\n## PROJECT CONTEXT (from previous phases)\n\n"
            + "\n\n---\n\n".join(context_parts)
        )

    # --- Current phase conversation history ---
    phase_state = session.phases.get(phase_id)
    history_lines: list[str] = []
    if phase_state:
        # Exclude the very last user message — we append it separately below
        prior = [
            m for m in phase_state.conversation
            if not (m["role"] == "user" and m["content"] == user_message)
        ]
        for msg in prior:
            role_label = "User" if msg["role"] == "user" else "Bob+"
            history_lines.append(f"{role_label}: {msg['content']}")

    history_block = ""
    if history_lines:
        history_block = (
            "\n\n---\n## CONVERSATION SO FAR (current phase)\n\n"
            + "\n\n".join(history_lines)
        )

    return (
        f"{system}"
        f"{skills_block}"
        f"{context_block}"
        f"{history_block}"
        f"\n\n---\n\nUser: {user_message}"
        f"\n\nBob+:"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_session(title: str, settings: Settings) -> dict:
    global _session
    with _session_lock:
        session_id = f"session-{uuid4().hex[:8]}"
        now = _now()
        phases = {
            p["id"]: PhaseState(phase_id=p["id"], state="pending")
            for p in PHASES
        }
        # Activate the first phase
        phases["describe"].state = "active"
        phases["describe"].started_at = now

        _session = Session(
            id=session_id,
            title=title or "New Project",
            current_phase_id="describe",
            phases=phases,
            created_at=now,
            updated_at=now,
        )
        return _session.to_dict()


def get_current_session() -> dict | None:
    with _session_lock:
        return _session.to_dict() if _session else None


def send_message(session_id: str, user_message: str, settings: Settings) -> dict:
    """
    Send a user message in the current phase.
    Runs a synchronous Bob job and returns the response with transition info.
    """
    with _session_lock:
        if _session is None or _session.id != session_id:
            raise KeyError(f"Session {session_id} not found.")
        session = _session
        phase_id = session.current_phase_id
        phase_state = session.phases[phase_id]
        phase_def = PHASE_BY_ID[phase_id]

    # Add user message to conversation
    with _session_lock:
        phase_state.conversation.append({
            "role": "user",
            "content": user_message,
            "timestamp": _now(),
        })

    # Build prompt and run Bob
    prompt = _build_prompt(phase_id, user_message, session)
    bob_request = BobPromptRequest(
        prompt=prompt,
        timeoutSeconds=180,
        safetyProfile="readonly",
        maxCoins=20,
        workspaceMode="isolated",
    )

    from bobserver.tasks import run_bob_prompt
    result = run_bob_prompt(bob_request, settings)

    raw_response = result.log or result.error or "Bob did not return a response."

    # Extract transition signal and artifact
    transition = _extract_transition(raw_response)
    clean_response = _strip_transition(raw_response)

    # Extract artifact if present
    artifact_content = ""
    if phase_def["artifact"]:
        artifact_content = _extract_artifact(raw_response, phase_def["artifact"])

    with _session_lock:
        # Save artifact if found
        if artifact_content:
            phase_state.artifact_content = artifact_content

        # Add Bob response to conversation
        phase_state.conversation.append({
            "role": "assistant",
            "content": clean_response,
            "timestamp": _now(),
            "transition": transition,
        })
        session.updated_at = _now()

    return {
        "sessionId": session_id,
        "phaseId": phase_id,
        "message": {
            "role": "assistant",
            "content": clean_response,
            "timestamp": _now(),
        },
        "transition": transition,
        "artifactUpdated": bool(artifact_content),
        "bobJobId": result.id,
        "bobState": result.state,
    }


def advance_phase(session_id: str, settings: Settings) -> dict:
    """Advance to the next phase."""
    with _session_lock:
        if _session is None or _session.id != session_id:
            raise KeyError(f"Session {session_id} not found.")
        session = _session
        current_phase_id = session.current_phase_id
        phase_def = PHASE_BY_ID[current_phase_id]
        next_phase_id = phase_def["next_phase"]

        if next_phase_id is None:
            raise ValueError("Already at the final phase.")

        now = _now()

        # Mark current phase completed
        session.phases[current_phase_id].state = "completed"
        session.phases[current_phase_id].completed_at = now

        # Activate next phase
        session.phases[next_phase_id].state = "active"
        session.phases[next_phase_id].started_at = now
        session.current_phase_id = next_phase_id
        session.updated_at = now

    # Send an opening message from Bob for the new phase
    opening_prompt = f"The user has moved into the {PHASE_BY_ID[next_phase_id]['title']} phase. Start the phase with a brief introduction and your first question or action."
    try:
        response = send_message(session_id, opening_prompt, settings)
    except Exception:
        response = {}

    with _session_lock:
        return {**_session.to_dict(), "openingMessage": response.get("message")}


def get_artifact(session_id: str, phase_id: str) -> str:
    with _session_lock:
        if _session is None or _session.id != session_id:
            raise KeyError(f"Session {session_id} not found.")
        phase_state = _session.phases.get(phase_id)
        if not phase_state or not phase_state.artifact_content:
            raise FileNotFoundError(f"No artifact for phase {phase_id}.")
        return phase_state.artifact_content


def delete_session(session_id: str) -> None:
    global _session
    with _session_lock:
        if _session is None or _session.id != session_id:
            raise KeyError(f"Session {session_id} not found.")
        _session = None
