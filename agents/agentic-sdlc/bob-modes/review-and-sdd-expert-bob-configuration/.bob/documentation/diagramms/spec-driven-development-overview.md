# Spec-Driven Development Overview Diagram

This document explains the planned [`spec-driven-development-overview.drawio`](spec-driven-development-overview.drawio:1) diagram that visualizes the Spec-Driven Development mode and its supporting assets.

## Diagram Purpose

The diagram should provide a concise visual overview of:

- The **Spec-Driven Development** mode as a dedicated requirements and specification-focused mode
- The relationship between the main mode and the **Requirements Management** skill
- The supporting guidance documents used to onboard and assist users
- The workflow from requirements discovery to implementation handoff
- The integration points between SDD and other Bob modes

## Target Audience

**Primary Users:** Developers, solution architects, product owners, and maintainers who work with [`prompts/spec-driven-development.md`](../prompts/spec-driven-development.md:1) and the related SDD guidance files.

**Use Cases:**
- Understanding what the SDD mode is responsible for
- Explaining how SDD connects requirements, specifications, and prompts
- Onboarding new users to the SDD documentation set
- Showing how requirements work flows into architecture review and implementation
- Maintaining consistency when extending the SDD mode or its supporting assets

## Diagram Structure

### Main Mode

**Spec-Driven Development (`spec-driven-development`)**
- Central mode for specification-first work
- Guides users through requirements gathering and analysis
- Supports specification creation for functional and non-functional concerns
- Helps craft higher-quality prompts for SDLC activities
- Connects requirements to later delivery phases through traceability

### Core Capability Areas

The diagram should show four primary capability groups taken from [`spec-driven-development.md`](../prompts/spec-driven-development.md:1):

1. **Requirements Management**
   - Elicit and document functional requirements
   - Capture non-functional requirements and constraints
   - Analyze stakeholder needs
   - Prioritize and validate requirements

2. **Specification Creation**
   - Turn requirements into structured specifications
   - Support multiple formats such as user stories and technical specs
   - Define acceptance criteria and constraints
   - Improve clarity, testability, and completeness

3. **Prompt Engineering for SDLC**
   - Help users structure prompts with context and objectives
   - Improve prompt quality for AI-assisted development
   - Provide reusable templates and examples
   - Encourage iterative prompt refinement

4. **SDLC Integration**
   - Connect specifications to planning, analysis, design, implementation, testing, deployment, and maintenance
   - Preserve traceability across lifecycle stages
   - Reduce ambiguity during delivery
   - Support better validation and stakeholder alignment

### Supporting Skill

**Requirements Management Skill**
- Implemented in [`skills/requirements-management-skill.md`](../../skills/requirements-management-skill.md:1)
- Provides deeper requirements engineering guidance
- Covers elicitation, prioritization, traceability, validation, and change management
- Acts as the specialist skill underpinning the SDD mode

### Supporting Documentation

The diagram should include the main documentation assets around the mode:

1. [`prompts/SDD-README.md`](../prompts/SDD-README.md:1)
   - Comprehensive documentation hub
   - End-to-end workflows
   - Best practices and resource references

2. [`prompts/SDD-QUICK-START.md`](../prompts/SDD-QUICK-START.md:1)
   - Fast onboarding guide
   - Scenario-based entry points
   - Quick actions and templates

3. [`prompts/SDD-SUMMARY.md`](../prompts/SDD-SUMMARY.md:1)
   - Implementation summary
   - Asset inventory and fulfilled requirements
   - High-level orientation for maintainers

4. [`prompts/sdd-interactive-guide.md`](../prompts/sdd-interactive-guide.md:1)
   - Step-by-step interactive guidance
   - Prompt crafting workflow
   - SDLC-specific examples and validation support

### Downstream Integration

The diagram should also show where SDD hands work off to other modes, based on guidance in [`prompts/SDD-README.md`](../prompts/SDD-README.md:392):

- **Architecture Review**
  - Validates technical decisions and specifications

- **Code Mode**
  - Implements approved specifications

- **Orchestrator**
  - Coordinates complex, multi-step specification work

- **Ask Mode**
  - Clarifies concepts and requirements questions

## Recommended Visual Elements

### Color Coding

- **Blue (#4A90E2)**: Main SDD mode
- **Green (#50C878)**: Specialist skill
- **Yellow (#FFD966)**: Documentation and guides
- **Purple (#7B68EE)**: Integration with other modes
- **Gray (#F5F5F5)**: Containers and supporting layout blocks

### Connection Types

- **Solid arrows**: Primary workflow or ownership relationship
- **Dashed arrows**: Supporting/reference relationship
- **Directional arrows to other modes**: Handoff or collaboration points

## Suggested Workflow View

A compact workflow section in the diagram should show:

1. Stakeholder and context discovery
2. Requirements elicitation and documentation
3. Specification creation and refinement
4. Prompt crafting and validation
5. Technical validation with Architecture Review
6. Implementation handoff to Code mode

This reflects the workflows documented in [`prompts/SDD-README.md`](../prompts/SDD-README.md:124) and the phased process in [`prompts/spec-driven-development.md`](../prompts/spec-driven-development.md:89).

## Maintenance Notes

When updating the SDD ecosystem:

1. Keep the mode, skill, and supporting documents aligned
2. Reflect new documentation assets in the diagram
3. Update integration links if SDD workflows change
4. Preserve terminology consistency across the mode and overview
5. Keep this overview synchronized with the actual draw.io diagram

## Related Files

- Main Mode: [`documentation/guides/spec-driven-development.md`](../guides/spec-driven-development.md:1)
- Requirements Skill: [`skills/requirements-management-skill.md`](../../skills/requirements-management-skill.md:1)
- Guide: [`documentation/SDD-README.md`](../SDD-README.md:1)
- Quick Start: [`prompts/SDD-QUICK-START.md`](../prompts/SDD-QUICK-START.md:1)
- Summary: [`prompts/SDD-SUMMARY.md`](../prompts/SDD-SUMMARY.md:1)
- Interactive Guide: [`prompts/sdd-interactive-guide.md`](../prompts/sdd-interactive-guide.md:1)