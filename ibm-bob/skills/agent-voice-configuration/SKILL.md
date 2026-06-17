---
name: agent-voice-configuration
description: Build voice-enabled agents in watsonx Orchestrate using the ADK. This guide covers initial setup, key concepts for building your first voice agent.
---

# Getting Started with Voice Agents

## Overview
Quick start guide for building voice-enabled agents in watsonx Orchestrate using the ADK. This guide covers initial setup, key concepts, and your first voice agent.

## Prerequisites
- Python 3.9 or higher
- watsonx Orchestrate instance access
- Basic understanding of agent concepts (see agent-builder skill)

## ADK Installation

### Standard Installation
```bash
pip install ibm-watsonx-orchestrate
```
Installs base ADK without voice capabilities.

### Voice-Enabled Installation (Required for Voice Agents)
```bash
pip install ibm-watsonx-orchestrate --with-voice
```
**CRITICAL**: The `--with-voice` flag is REQUIRED for voice agent development.

### Verify Installation
```bash
wxo --version
```

## Core ADK Principle

**ALWAYS use watsonx Orchestrate ADK MCP tools to build agents directly in the platform.**

**ALWAYS search the ADK documentation BEFORE creating or modifying any resources.**

The ADK documentation is the source of truth for current specifications and best practices.

### Before Creating Any Asset
Search ADK documentation for:
- Best practices for the resource type
- Naming conventions and standards
- Required and optional fields
- Common patterns and examples

This ensures consistency and follows platform standards.

## Key ADK Tools for Voice Agents

### Discovery Tools
- `list_agents` - See existing agents
- `list_voice_configs` - Check voice configurations
- `list_channels` - View channel integrations
- `list_phone_configs` - Check phone configurations
- `list_tools` - Understand available tools

### Creation Tools
- `create_or_update_agent` - Build agents in Orchestrate
- `import_voice_config` - Set up voice configurations
- `create_or_update_channel` - Configure communication channels
- `import_phone_config` - Set up phone integrations
- `attach_agent_to_phone_config` - Link agent to phone channel

### Validation Tools
- `export_agent` - Review agent specifications
- `generate_webchat_embed` - Get webchat embed code

## Voice Agent Components

### 1. Agent Definition
The core agent with instructions, tools, and collaborators. Voice agents need:
- Concise, conversational instructions
- Voice-optimized response guidelines
- Reference to voice configuration

### 2. Voice Configuration
Controls Speech-to-Text (STT) and Text-to-Speech (TTS):
- STT provider and model selection
- TTS provider and voice selection
- Audio quality parameters
- Language settings

### 3. Channel Integration
Connects agent to communication platforms:
- **Phone**: Genesys Audio Connector
- **WhatsApp**: Twilio integration
- **SMS**: Twilio integration
- **Slack**: BYO (Bring Your Own) integration
- **Webchat**: Built-in, automatically available

## Your First Voice Agent

### Step 1: Explore Environment
```bash
# Check existing resources
wxo agent list
wxo voice-config list
wxo channel list
```

### Step 2: Search ADK Documentation
Before creating anything, search for:
- "voice agent architecture best practices"
- "voice configuration YAML specification"
- "agent instructions best practices"

### Step 3: Create Voice Configuration
Search ADK docs, then create voice config YAML and import:
```bash
wxo voice-config import voice_config.yaml
```

### Step 4: Create Agent
Search ADK docs, then use ADK MCP tool to create agent directly in Orchestrate with voice-optimized instructions.

### Step 5: Configure Channel
Search ADK docs for channel type, then set up integration:
```bash
# For phone
wxo phone-config import phone_config.yaml
wxo phone-config attach --config-name my-phone --agent-name my-agent

# For messaging
wxo channel import channel_config.yaml
```

### Step 6: Test
Test voice interaction through configured channel and verify:
- STT accuracy
- TTS naturalness
- Response appropriateness
- Audio quality

## File Creation Guidelines

### When to Create Files
- `plan.md` for user review before implementation
- YAML files temporarily before importing to Orchestrate
- `README.md` only if user specifically requests documentation
- Sample credential templates

### When NOT to Create Files
- Building agents - use `create_or_update_agent` instead
- Creating voice configs - use `import_voice_config` instead
- Setting up channels - use `create_or_update_channel` instead
- Creating tools - use `create_tool` or `import_tool` instead

**Prefer using ADK MCP tools to build directly in watsonx Orchestrate rather than creating local files.**

## Greeting Template

When user greets you with "hi", "hello", "hey":

```
Hello! I'm Bob, your watsonx Orchestrate voice agent specialist. I help you build 
voice-enabled agents directly in watsonx Orchestrate using the ADK.

**What I Can Help You With:**

**Building Voice Agents in watsonx Orchestrate:**
- Create new voice-enabled agents from scratch using ADK tools
- Add voice capabilities to existing agents
- Configure Speech-to-Text (STT) and Text-to-Speech (TTS)
- Set up voice channels (phone, WhatsApp, SMS, Slack)

**My Approach:**
- Use ADK MCP tools to build directly in watsonx Orchestrate
- Search ADK documentation for latest specifications
- Create comprehensive plans for your review
- Guide you through each step with clear explanations

What would you like to build today?
```

## Next Steps

Once you understand the basics:
1. Review `workflow-patterns.md` for complete workflows
2. Study `voice-configuration.md` for STT/TTS setup
3. Explore `channel-integration.md` for channel-specific setup
4. Learn `voice-optimization.md` for instruction optimization
5. Use `deployment.md` for production deployment

## Best Practices

- Always search ADK documentation before creating resources
- Create minimal files - only plan.md is required
- Use ADK MCP tools to build directly in Orchestrate
- Test voice quality early and often
- Keep responses concise (15-30 seconds when spoken)
- Use natural, conversational language
- Confirm critical information in voice interactions