from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any


SAFETY_PROFILES = {
    "readonly": ["Read", "Glob", "Grep"],
    "edit": ["Read", "Glob", "Grep", "Write", "Edit", "MultiEdit"],
    "trusted": [],
}


def build_bob_args(*, max_coins: int, safety_profile: str, yolo: bool = False) -> list[str]:
    profile = "trusted" if yolo else safety_profile
    if profile not in SAFETY_PROFILES:
        raise ValueError(f"Unknown Bob safety profile: {profile}")

    args = ["--accept-license", "-o", "stream-json", "--max-coins", str(max_coins)]
    if profile == "trusted":
        args.extend(["--approval-mode", "yolo"])
    else:
        for tool in SAFETY_PROFILES[profile]:
            args.extend(["--allowed-tools", tool])
    return args


@dataclass
class BobStreamState:
    session_id: str | None = None
    model: str | None = None
    completion_text: str = ""
    text_parts: list[str] = field(default_factory=list)
    usage: dict[str, Any] = field(default_factory=dict)
    status: str | None = None
    tool_calls: int = 0

    def consume(self, line: str) -> list[tuple[str, dict[str, Any]]]:
        stripped = line.strip()
        if not stripped:
            return []
        try:
            message = json.loads(stripped)
        except json.JSONDecodeError:
            self.text_parts.append(stripped)
            return [("diagnostic", {"text": line})]
        if not isinstance(message, dict):
            return []

        message_type = message.get("type")
        if message_type == "init":
            self.session_id = _string(message.get("session_id"))
            self.model = _string(message.get("model"))
            return [("progress", {"phase": "initialized", "sessionId": self.session_id, "model": self.model})]

        # Assistant deltas include private reasoning. Never forward them.
        if message_type == "message" and message.get("role") == "assistant" and message.get("delta") is True:
            return []

        if message_type == "text" and isinstance(message.get("text"), str):
            text = message["text"]
            if not text.lstrip().startswith('{"type":"'):
                self.text_parts.append(text)
            return []

        if message_type == "tool_use":
            tool_name = _string(message.get("tool_name")) or "unknown"
            parameters = message.get("parameters")
            if tool_name == "attempt_completion" and isinstance(parameters, dict):
                result = parameters.get("result")
                if isinstance(result, str):
                    self.completion_text = result.strip()
                return []
            self.tool_calls += 1
            return [("progress", {"phase": "tool_use", "tool": tool_name, "toolCalls": self.tool_calls})]

        if message_type == "tool_result":
            return [("progress", {"phase": "tool_result", "status": message.get("status")})]

        if message_type == "result":
            self.status = _string(message.get("status"))
            stats = message.get("stats")
            if isinstance(stats, dict):
                self.usage = {
                    "totalTokens": stats.get("total_tokens"),
                    "inputTokens": stats.get("input_tokens"),
                    "outputTokens": stats.get("output_tokens"),
                    "toolCalls": stats.get("tool_calls", self.tool_calls),
                    "durationMs": stats.get("duration_ms"),
                    "cost": stats.get("session_costs"),
                    "coinsSpent": stats.get("budget_spend"),
                    "coinsBudget": stats.get("max_budget"),
                }
            return [("usage", self.metadata())]
        return []

    @property
    def final_text(self) -> str:
        return self.completion_text or "\n".join(part.strip() for part in self.text_parts if part.strip()).strip()

    def metadata(self) -> dict[str, Any]:
        return {
            "sessionId": self.session_id,
            "model": self.model,
            "status": self.status,
            "usage": self.usage,
        }


def parse_bob_output(output: str) -> BobStreamState:
    state = BobStreamState()
    for line in output.splitlines():
        state.consume(line)
    return state


def _string(value: Any) -> str | None:
    return value if isinstance(value, str) else None
