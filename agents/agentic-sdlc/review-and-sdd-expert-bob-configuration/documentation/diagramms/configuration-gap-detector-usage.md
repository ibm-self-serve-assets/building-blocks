# Configuration Gap Detector Usage Diagram

This document explains the [`configuration-gap-detector-usage.drawio`](configuration-gap-detector-usage.drawio:1) diagram that visualizes how the Configuration Gap Detector mode is used when an active mode cannot fully address a user request.

## Diagram Purpose

The diagram provides a visual explanation of:

- How a user request is first processed by the currently active mode
- How the system decides whether the existing configuration is sufficient
- The success path when no configuration gap exists
- The escalation path when a capability, workflow, or domain gap is detected
- How the Configuration Gap Detector researches and proposes a targeted solution

## Target Audience

**Primary Users:** Maintainers and advanced users working with the custom mode system, especially those extending [`modes/custom_modes.yaml`](../../modes/custom_modes.yaml:1) and the related prompt assets.

**Use Cases:**
- Understanding when the Configuration Gap Detector should be used
- Explaining the self-healing configuration concept to contributors
- Showing how gap detection differs from a normal successful review flow
- Onboarding maintainers who need to add new skills or modes
- Reviewing the user approval step before any proposed configuration change

## Diagram Structure

### Step 1: Active Mode Processes Request

The flow starts with a **User Request** that is handled by the currently active mode.

That mode:
- Attempts to solve the task
- Reads relevant skills
- Applies its methodology
- Analyzes the codebase or request context

This step represents normal Bob behavior before any escalation is needed.

### Decision Point: Configuration Sufficient?

A central decision node determines whether the current configuration is enough to address the request.

**Yes path**
- The active mode completes the task
- Findings or recommendations are delivered
- No additional configuration work is required

**No path**
- A configuration gap is identified
- The gap may be caused by missing domain knowledge, incomplete workflow coverage, or a new class of requirement not addressed by the existing setup

### Step 2B: Gap Detected

The diagram captures the main types of gaps:

- Missing domain knowledge
- Insufficient workflow coverage
- New requirement type detected

This is the trigger point for switching to the Configuration Gap Detector mode.

### Step 3: Switch to Configuration Gap Detector Mode

Once a gap is detected, the system switches to **Configuration Gap Detector** mode.

This mode:
- Explains the identified gap
- Provides context about what is missing
- Reframes the task as a configuration and capability analysis problem

### Step 4: Research Best Practices

The diagram shows a dedicated research step where the mode uses browser-backed investigation to gather authoritative information.

Research targets include:
- Official documentation
- Industry standards
- Framework best practices
- Cross-source validation

This step is important because proposed additions should be evidence-based rather than speculative.

### Step 5: Analyze Configuration Gap

After research, the mode analyzes the gap against the current setup.

The analysis should:
- Review existing modes and skills
- Identify what is missing
- Explain why the current configuration is insufficient
- Provide factual evidence for the identified gap

### Step 6: Propose New Mode or Skill

The output of the analysis is a targeted proposal.

The proposal may recommend:
- A new **mode** when role, behavior, or workflow orchestration is missing
- A new **skill** when specialized task knowledge is missing

The diagram emphasizes that the proposal should be:
- Minimal
- Targeted
- Research-backed
- Easy to integrate into the existing system

### Step 7: User Reviews Proposal

The final step is explicitly user-controlled.

The user:
- Reviews the proposed mode or skill
- Evaluates supporting research sources
- Approves or requests changes
- Decides whether implementation should proceed

This ensures there is no automatic configuration mutation without human approval.

## Key Features Highlighted in the Diagram

### Self-Healing Configuration

The diagram presents the Configuration Gap Detector as a self-healing mechanism for the Bob setup.

It helps by:
- Detecting coverage gaps automatically
- Proposing narrowly scoped improvements
- Preserving a modular architecture

### Research-Backed Recommendations

The mode does not invent solutions in isolation. It performs external research and cites authoritative sources to support its proposals.

### Modular Expansion

The diagram reinforces a design principle of adding only what is necessary:
- Minimal additions
- No unnecessary duplication
- Clean integration with existing modes and skills

### User Governance

Even when a good proposal exists, the user remains in control of whether and how the configuration evolves.

## Example Gap Scenarios

The example scenarios shown in the diagram illustrate typical triggers for this mode:

- **IoT Architecture Review**
  - Existing skills do not cover IoT-specific concerns
  - A new IoT-oriented architecture review skill may be proposed

- **Blockchain Security**
  - Current security coverage may not address blockchain-specific threats
  - A blockchain-focused security skill may be proposed

- **ML System Architecture**
  - Existing pattern coverage may not be sufficient for ML systems
  - A machine-learning architecture skill may be proposed

- **Healthcare Compliance**
  - Specialized regulatory knowledge such as HIPAA may be missing
  - A healthcare compliance skill may be proposed

- **Edge Computing**
  - Edge-specific deployment and runtime concerns may not be represented
  - An edge architecture skill may be proposed

## Visual Elements

### Color Coding

Based on the current diagram:

- **Blue (#DAE8FC)**: User input
- **Yellow (#FFF2CC)**: Active mode processing
- **Red/Pink (#F8CECC)**: Decision point
- **Orange (#FFE6CC)**: Gap detected
- **Purple (#E1D5E7)**: Configuration Gap Detector processing
- **Green (#D5E8D4)**: Success path and key positive features
- **Gray (#F5F5F5)**: User review and approval

### Connection Semantics

- **Standard arrows**: Sequential flow between steps
- **Labeled YES/NO arrows**: Decision outcomes from the sufficiency check
- **Multiple input arrows into proposal step**: Combined research and analysis inputs

## Usage Guidance

Use the Configuration Gap Detector when:

- A task appears outside the scope of current modes
- Existing modes produce incomplete or unsatisfactory results
- A new domain emerges that is not supported by current skills
- A workflow stage in the SDLC appears underrepresented
- You want to assess whether the current setup needs extension before further work

This usage aligns with the role of the **🔍 Configuration Gap Detector** mode in the custom configuration.

## Maintenance Notes

When updating the Configuration Gap Detector workflow:

1. Keep the flow aligned with actual mode-switching behavior
2. Add new example scenarios if new gaps become common
3. Update the proposal logic if the distinction between modes and skills changes
4. Keep the user approval step explicit in both the diagram and documentation
5. Ensure the visual legend stays consistent with diagram colors and semantics

## Related Files

- Diagram: [`configuration-gap-detector-usage.drawio`](configuration-gap-detector-usage.drawio:1)
- Modes Configuration: [`modes/custom_modes.yaml`](../../modes/custom_modes.yaml:1)
- Skills Overview: [`skills/README.md`](../../skills/README.md:1)
- Existing Mode Overview: [`custom-modes-overview.md`](custom-modes-overview.md:1)