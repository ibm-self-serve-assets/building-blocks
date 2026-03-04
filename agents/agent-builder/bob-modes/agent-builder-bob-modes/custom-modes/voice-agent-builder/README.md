# 🎙️ WxO Voice Agents Mode

A specialized Bob mode for building voice-enabled agents in watsonx Orchestrate using the ADK (Agent Development Kit).

## Overview

This mode helps you build complete voice-enabled agents directly in watsonx Orchestrate, including:
- Voice-enabled agents with optimized instructions
- Voice configurations (STT/TTS setup)
- Channel integrations (phone, WhatsApp, SMS, Slack)
- Custom tools and integrations
- Deployment automation

## Key Features

- **ADK-First Approach**: Builds agents directly in watsonx Orchestrate using ADK MCP tools
- **Voice Optimization**: Automatically optimizes agent responses for voice interactions
- **Multi-Channel Support**: Configure phone (Genesys), WhatsApp, SMS (Twilio), Slack, and webchat
- **Comprehensive Planning**: Creates detailed plans for review before implementation
- **Best Practices**: Searches ADK documentation for naming conventions and best practices
- **Minimal File Creation**: Focuses on building in the platform, not managing local files

## Setup & Installation

1. **Clone this repository**
   ```bash
   git clone <repo-url>
   ```

2. **Open the `voice-agent-builder` folder as the root folder in the Bob application**

3. **That's it!** — The `🎙️ WxO Voice Agents` mode will automatically appear in Bob's mode selector, ready to use.


## How to Use

1. **Select 🎙️ WxO Voice Agents** from the Bob mode selector
2. **Tell Bob what kind of agent you want to build**
   - Example: "Build a customer service voice agent for order management"
3. **Answer the discovery questions** (Bob will ask 2–3 at a time)
   - Use case and target users
   - Required capabilities and integrations
   - Voice channels needed
   - Language and audio quality requirements
4. **Review and approve the generated plan.md**
   - Bob creates a comprehensive implementation plan
   - Review architecture, approach, and timeline
   - Approve or request changes
5. **Bob builds everything** — tools, agents, connections, scripts, and docs
   - Creates voice configuration in watsonx Orchestrate
   - Builds agent with voice-optimized instructions
   - Sets up channel integrations
   - Creates custom tools if needed
   - Generates deployment scripts
6. **Run scripts/deploy.sh to deploy to watsonx Orchestrate**
   - Automated deployment with validation
   - Health checks and smoke tests
   - Rollback capability if needed

## What Bob Creates

### In watsonx Orchestrate (via ADK tools)
- **Agent**: Voice-enabled agent with optimized instructions
- **Voice Configuration**: STT/TTS provider setup
- **Channels**: Phone, WhatsApp, SMS, Slack integrations
- **Tools**: Custom Python tools for external integrations
- **Connections**: Secure credential management

### Local Files (Minimal)
- **plan.md**: Implementation plan for review
- **deployment.sh**: Automated deployment script
- **credentials.sample.yaml**: Template for credentials (never actual credentials)

## Voice Optimization

Bob automatically optimizes agents for voice interactions:
- **Concise Responses**: Keeps responses under 30 seconds when spoken
- **Conversational Language**: Uses natural, spoken language patterns
- **Confirmation Steps**: Adds confirmation for critical actions
- **No Visual Formatting**: Removes bullets, tables, and visual elements
- **Clear Next Steps**: Provides explicit guidance for users

## Supported Channels

### Phone (Genesys Audio Connector)
- Toll-free and local numbers
- IVR integration
- Call recording and analytics

### WhatsApp (Twilio)
- Rich media support
- Template messages
- Two-way conversations

### SMS (Twilio)
- Text-based interactions
- Opt-in/opt-out management
- Delivery tracking

### Slack (BYO)
- Direct messages
- Channel mentions
- Rich formatting

### Webchat
- Embedded on websites
- Voice input/output
- Customizable appearance

## ADK Documentation Integration

Bob always searches the watsonx Orchestrate ADK documentation before creating assets:
- **Best Practices**: Follows platform standards
- **Naming Conventions**: Uses consistent naming
- **Specifications**: Gets latest YAML formats
- **Examples**: Learns from documented patterns

## Example Use Cases

- **Customer Service**: Order tracking, returns, product questions
- **IT Support**: Password resets, ticket creation, system status
- **Appointment Scheduling**: Booking, rescheduling, reminders
- **FAQ Automation**: Common questions, troubleshooting
- **Lead Qualification**: Initial screening, information gathering

## Best Practices

1. **Start with Clear Requirements**: Be specific about use case and capabilities
2. **Review the Plan**: Always review plan.md before Bob starts building
3. **Test Incrementally**: Test each component as it's built
4. **Use Sample Credentials**: Never commit actual credentials to version control
5. **Monitor Voice Quality**: Test with real users and iterate
6. **Follow Naming Conventions**: Let Bob search ADK docs for standards

## File Structure

```
project/
├── plan.md                          # Implementation plan
├── deployment.sh                    # Deployment automation
├── credentials.sample.yaml          # Credential template
└── README.md                        # Project documentation (if requested)
```


