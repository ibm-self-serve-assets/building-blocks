# Voice Agent Workflow Patterns

## Overview
Step-by-step workflows for building new voice agents and migrating existing text agents to voice. These patterns ensure consistent, high-quality voice agent development.

## Workflow 1: Building New Voice Agent Demo

### Phase 1: Requirements Gathering

#### Step 1: Explore Environment
Check existing resources in watsonx Orchestrate:
```bash
wxo agent list
wxo voice-config list
wxo channel list
wxo phone-config list
wxo tool list
```

Search ADK documentation:
- "voice agent architecture best practices"
- "voice agent design patterns"

#### Step 2: Interactive Requirements Gathering
Use `ask_followup_question` to gather:

**Use Case Questions:**
- What is the primary use case for this voice agent?
- Who are the target users?
- What problems will this agent solve?

**Functionality Questions:**
- What key capabilities should the agent have?
- What external systems or APIs will it integrate with?
- Do you need any custom tools created?

**Voice Requirements:**
- Which voice channels do you need? (phone, WhatsApp, SMS, Slack)
- What languages should the agent support?
- Do you have preferences for STT/TTS providers?
- What audio quality requirements do you have?

Search ADK documentation:
- "voice agent use cases examples"
- "voice agent architecture patterns"

### Phase 2: Design and Planning

#### Step 1: Design Agent Architecture
Search ADK documentation:
- "agent architecture best practices"
- "voice agent design patterns"

Design components:
- Agent instructions and behavior
- Voice configuration (STT/TTS)
- Channel integration strategy
- Tool requirements
- Collaborator agents (if needed)

#### Step 2: Create Implementation Plan
Generate comprehensive `plan.md` for user review with sections:
- Project Overview
- Requirements Summary
- Agent Design (instructions, tools, collaborators)
- Voice Configuration Strategy
- Channel Integration Plan
- Implementation Steps (using ADK tools)
- Testing Strategy

Present for review using `ask_followup_question` with suggestions:
- Approve the plan and start building in watsonx Orchestrate
- Request changes to architecture or approach
- Add or modify requirements
- Discuss specific technical details

### Phase 3: Implementation

#### Step 1: Create Voice Configuration
Search ADK documentation:
- "voice configuration YAML specification"
- "STT TTS provider configuration"

Process:
1. Search ADK docs for voice config specification
2. Create voice config YAML based on requirements
3. Use `import_voice_config` to create in Orchestrate
4. Verify creation with `list_voice_configs`

Example:
```yaml
spec_version: v1
kind: VoiceConfiguration
name: my-voice-config
description: Voice configuration for customer service agent

stt_provider:
  provider: watson_stt
  model: en-US_Telephony
  settings:
    smart_formatting: true
    profanity_filter: false
    end_of_phrase_silence_time: 0.8
    split_transcript_at_phrase_end: true

tts_provider:
  provider: watson_tts
  voice: en-US_MichaelV3Voice
  settings:
    rate: "0%"
    pitch: "0%"

audio_config:
  sample_rate: 8000
  encoding: mulaw
  channels: 1
```

#### Step 2: Create Agent
Search ADK documentation:
- "agent YAML specification voice_configuration"
- "agent instructions best practices"

Process:
1. Search ADK docs for agent specification
2. Design voice-optimized instructions
3. Select appropriate tools and collaborators
4. Use `create_or_update_agent` to build in Orchestrate
5. Verify creation with `list_agents`

Voice instruction guidelines:
- Keep responses under 30 seconds when spoken
- Use natural, conversational language
- Confirm critical information before actions
- Provide clear next steps
- Avoid visual formatting (bullets, tables)

Example agent creation:
```json
{
  "options": {
    "name": "customer-service-voice",
    "description": "Voice-enabled customer service agent",
    "kind": "native",
    "instructions": "You are a friendly customer service agent...\n\nVoice Guidelines:\n- Keep responses under 30 seconds\n- Use conversational language\n- Confirm critical information",
    "tools": ["order_lookup", "process_return"],
    "llm": "watsonx/meta-llama/llama-3-2-90b-vision-instruct"
  }
}
```

#### Step 3: Configure Channels
Search ADK documentation for specific channel type:
- "[channel_type] configuration specification"
- "[channel_type] setup steps"

**Phone Channel:**
1. Search ADK docs for phone config spec
2. Create phone config YAML
3. Use `import_phone_config`
4. Use `attach_agent_to_phone_config`
5. Configure webhook in Genesys

**Messaging Channels (WhatsApp/SMS):**
1. Search ADK docs for channel spec
2. Create channel configuration
3. Use `create_or_update_channel`
4. Configure webhook in provider (Twilio/Slack)

**Webchat:**
1. Use `generate_webchat_embed` to get HTML code
2. Provide embed code to user

#### Step 4: Create Required Tools (if needed)
Search ADK documentation:
- "python tool creation"
- "tool metadata specification"

Process:
1. Search ADK docs for tool specifications
2. Design tool functionality
3. Create tool using `create_tool` or `import_tool`
4. Assign tool to agent using `create_or_update_agent`

#### Step 5: Test and Validate
Testing approach:
- Use `list_agents` to verify agent exists
- Use `list_voice_configs` to verify voice config
- Use `list_channels` to verify channels
- Test voice interaction through each channel
- Verify audio quality and response times
- Test error handling and edge cases

## Workflow 2: Migrating Existing Text Agent to Voice

### Phase 1: Analysis

#### Step 1: Analyze Existing Agent
Use ADK tools:
- `list_agents` - Find the agent
- Export agent to review details

Search ADK documentation:
- "migrating text agent to voice"
- "voice optimization best practices"

Analysis points:
- Review agent instructions for voice compatibility
- Check response lengths (should be under 30 seconds)
- Identify visual formatting to remove
- Assess need for confirmation steps

#### Step 2: Gather Voice Requirements
Use `ask_followup_question` to ask:
- Which voice channels do you need?
- What STT/TTS providers do you prefer?
- What languages should the agent support?
- What's your expected call/message volume?

### Phase 2: Planning

#### Step 1: Create Enhancement Plan
Generate comprehensive `plan.md` with sections:
- Current Agent Analysis
- Voice Optimization Strategy
- Required Changes to Instructions
- Voice Configuration Setup
- Channel Integration Plan
- Testing Strategy

Search ADK documentation:
- "voice agent migration steps"
- "voice response optimization"

Present plan for review using `ask_followup_question`.

### Phase 3: Implementation

#### Step 1: Create Voice Configuration
Search ADK documentation:
- "voice configuration YAML specification"

Process:
1. Search ADK docs for voice config spec
2. Create voice config YAML
3. Use `import_voice_config`

#### Step 2: Update Agent with Voice Optimization
Search ADK documentation:
- "agent instructions best practices"
- "voice optimization techniques"

Process:
1. Modify instructions for voice (concise, conversational)
2. Add confirmation steps for critical actions
3. Remove visual formatting
4. Reference voice configuration
5. Use `create_or_update_agent` to update

Optimization changes:
- Shorten responses (15-30 seconds)
- Use conversational language
- Add confirmation for critical actions
- Remove bullets, use "first, second, third"

#### Step 3: Configure Voice Channels
Search ADK documentation:
- "[channel_type] configuration specification"

Use appropriate ADK tools:
- `import_phone_config` (for phone)
- `create_or_update_channel` (for messaging)
- `generate_webchat_embed` (for webchat)

Process:
1. Search ADK docs for channel specs
2. Create channel configurations
3. Use appropriate ADK tools to set up
4. Configure webhooks in providers

#### Step 4: Test Voice Interactions
Testing approach:
- Compare text vs voice interactions
- Verify response lengths are appropriate
- Test confirmation flows
- Check audio quality
- Validate error handling

## Workflow 3: Multi-Language Voice Agent

### Recommended Approach
Create separate voice configs for better control:

1. Create `voice_config_en.yaml` with English settings
2. Create `voice_config_es.yaml` with Spanish settings
3. Configure agent to use appropriate config based on language

### Agent Instructions Addition
```
## Language Handling
- Detect user's language from first utterance
- Switch to appropriate language for responses
- Maintain language consistency throughout conversation
- Offer language switch option if needed
```

## ADK Tool Usage Workflow

### Step 1: Identify What to Build
Determine what resource needs to be created in Orchestrate.

### Step 2: Search ADK Documentation
**ALWAYS search for specifications, best practices, and naming conventions BEFORE creating assets.**

Required searches:
- [resource] YAML specification
- [resource] best practices
- [resource] naming conventions
- [resource] examples

Why important: Ensures consistency with platform standards, follows established patterns, and uses appropriate naming conventions.

### Step 3: Prepare Configuration
Create YAML or prepare parameters based on ADK docs.

### Step 4: Use ADK MCP Tool
Execute appropriate ADK tool to create in Orchestrate.

Common tools:
- `create_or_update_agent`
- `import_voice_config`
- `create_or_update_channel`
- `import_phone_config`
- `create_tool`
- `import_tool`

### Step 5: Verify Creation
Use list_* tools to confirm resource was created:
- `list_agents`
- `list_voice_configs`
- `list_channels`
- `list_phone_configs`
- `list_tools`

### Step 6: Document What Was Built
Explain to user what was created and next steps.

## Mandatory ADK Searches

### Before Voice Config Creation
**Trigger:** Creating or modifying voice configuration

Required searches:
- "voice configuration YAML specification" - Get current spec format and required fields
- "STT TTS provider configuration" - Get latest provider settings

### Before Agent Creation
**Trigger:** Creating or modifying agent

Required searches:
- "agent YAML specification voice_configuration" - Get current agent spec with voice field
- "agent instructions best practices" - Get latest instruction guidelines

### Before Channel Setup
**Trigger:** Configuring any channel

Required searches:
- "[channel_type] configuration specification" - Get current channel spec format
- "[channel_type] setup steps" - Get latest setup procedures

### Before Tool Creation
**Trigger:** Creating custom tools

Required searches:
- "python tool creation" - Get tool creation guidelines
- "tool metadata specification" - Get tool spec format

## Completion Criteria

Before declaring a voice agent project complete, verify:
- [ ] All requirements have been addressed
- [ ] plan.md created and approved by user
- [ ] Voice configuration created in watsonx Orchestrate
- [ ] Agent created/updated in watsonx Orchestrate
- [ ] Channels configured in watsonx Orchestrate
- [ ] All resources verified using list_* tools
- [ ] Testing completed successfully
- [ ] ADK documentation searched at all critical steps
- [ ] User understands how to access and use the agent

## Best Practices

- **ALWAYS** search ADK docs for best practices and naming conventions BEFORE creating any asset
- **Create MINIMAL files** - only plan.md is required, avoid usage.md, guide.md, etc.
- **Always use ADK MCP tools** to build directly in watsonx Orchestrate
- Search ADK documentation for specifications before creating any resource
- Create plan.md before implementation for user review
- Use `ask_followup_question` for requirements gathering
- Verify resource creation with list_* tools
- Optimize agent instructions for voice interactions
- Test thoroughly before declaring completion
- Document configuration decisions in plan.md, not separate files
- Be transparent about ADK documentation searches
- Cite documentation sources in explanations