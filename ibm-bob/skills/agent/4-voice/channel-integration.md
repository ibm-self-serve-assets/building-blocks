# Channel Integration Guide

## Overview
Complete guide for connecting voice agents to communication platforms including phone systems, messaging apps, and collaboration tools. Each channel type has specific configuration requirements and setup procedures.

## Channel Types

### Phone
- **Provider:** Genesys Audio Connector
- **Use Cases:** Customer service hotlines, support call centers, automated phone systems (IVR)
- **Requirements:** Genesys Cloud organization, Audio Connector license, API credentials

### WhatsApp
- **Provider:** Twilio
- **Use Cases:** Customer support via WhatsApp, appointment scheduling, order status updates
- **Requirements:** Twilio account, WhatsApp Business API access, WhatsApp-enabled phone number

### SMS
- **Provider:** Twilio
- **Use Cases:** SMS-based customer service, appointment reminders, two-way SMS conversations
- **Requirements:** Twilio account, SMS-enabled phone number

### Slack
- **Provider:** Slack (BYO - Bring Your Own)
- **Use Cases:** Internal IT support bot, HR assistance bot, team collaboration assistant
- **Requirements:** Slack workspace, Slack app created, bot token and signing secret

### Webchat
- **Provider:** Built-in
- **Use Cases:** Website customer support, product assistance, lead generation
- **Requirements:** None - automatically available for all agents

## Phone Channel Configuration

### YAML Specification
```yaml
spec_version: v1
kind: PhoneConfiguration
name: my-phone-config
description: Genesys phone integration for customer service

channel_type: genesys_audio_connector
channel_config:
  security:
    api_key: ${GENESYS_API_KEY}
    client_secret: ${GENESYS_CLIENT_SECRET}
```

### Setup Workflow

#### Step 1: Create Phone Configuration
**ADK Search:**
- "phone configuration YAML specification"
- "Genesys Audio Connector setup"

**Actions:**
1. Create phone config YAML file
2. Import using: `wxo phone-config import phone-config.yaml`

#### Step 2: Attach Agent to Phone Config
```bash
wxo phone-config attach --config-name my-phone-config --agent-name my-agent --environment draft
```
**Result:** Webhook URL provided for Genesys configuration

#### Step 3: Configure Genesys
1. Log into Genesys Cloud
2. Navigate to Admin > Integrations
3. Create new Audio Connector integration
4. Enter webhook URL from step 2
5. Configure routing and phone numbers

#### Step 4: Test Phone Integration
1. Call the configured phone number
2. Verify agent responds correctly
3. Test conversation flow
4. Validate audio quality

### Best Practices
- Use separate phone configs for different environments
- Test with various phone types (mobile, landline, VoIP)
- Monitor call quality metrics
- Configure appropriate timeout values
- Set up call recording if required for compliance

## WhatsApp Channel Configuration

### YAML Specification
```yaml
spec_version: v1
kind: Channel
agent_name: my-agent
environment: draft
channel_type: twilio_whatsapp
name: my-whatsapp-channel
description: WhatsApp channel for customer support

channel_config:
  account_sid: ${TWILIO_ACCOUNT_SID}
  auth_token: ${TWILIO_AUTH_TOKEN}
  from_number: "whatsapp:+14155238886"
```

### Setup Workflow

#### Step 1: Set Up Twilio WhatsApp
1. Create Twilio account
2. Request WhatsApp Business API access
3. Configure WhatsApp-enabled phone number

#### Step 2: Create Channel Configuration
**ADK Search:**
- "WhatsApp channel configuration"
- "Twilio WhatsApp setup"

**Actions:**
1. Create channel YAML file
2. Import using: `wxo channel import whatsapp-channel.yaml`

#### Step 3: Configure Twilio Webhook
1. Get webhook URL from channel creation
2. In Twilio console, configure WhatsApp webhook
3. Set webhook URL for incoming messages

#### Step 4: Test WhatsApp Integration
1. Send test message to WhatsApp number
2. Verify agent responds
3. Test conversation flow

## SMS Channel Configuration

### YAML Specification
```yaml
spec_version: v1
kind: Channel
agent_name: my-agent
environment: draft
channel_type: twilio_sms
name: my-sms-channel
description: SMS channel for customer support

channel_config:
  account_sid: ${TWILIO_ACCOUNT_SID}
  auth_token: ${TWILIO_AUTH_TOKEN}
  from_number: "+15551234567"
```

### Setup Workflow

#### Step 1: Set Up Twilio SMS
1. Create Twilio account
2. Purchase SMS-enabled phone number

#### Step 2: Create Channel Configuration
**ADK Search:**
- "SMS channel configuration"
- "Twilio SMS setup"

**Actions:**
1. Create channel YAML file
2. Import using: `wxo channel import sms-channel.yaml`

#### Step 3: Configure Twilio Webhook
1. Get webhook URL from channel creation
2. In Twilio console, configure SMS webhook
3. Set webhook URL for incoming messages

#### Step 4: Test SMS Integration
1. Send test SMS to phone number
2. Verify agent responds
3. Test conversation flow

### Messaging Best Practices
- Keep messages concise for SMS (160 character limit)
- Use WhatsApp for richer media and longer messages
- Implement rate limiting to avoid spam flags
- Handle opt-out requests properly
- Test with various phone carriers

## Slack Channel Configuration

### YAML Specification
```yaml
spec_version: v1
kind: Channel
agent_name: my-agent
environment: draft
channel_type: byo_slack
name: my-slack-channel
description: Slack channel for internal support

channel_config:
  bot_token: ${SLACK_BOT_TOKEN}
  signing_secret: ${SLACK_SIGNING_SECRET}
```

### Setup Workflow

#### Step 1: Create Slack App
1. Go to api.slack.com/apps
2. Create new app from scratch
3. Select workspace

#### Step 2: Configure Slack App
1. Enable Socket Mode
2. Add Bot Token Scopes: `chat:write`, `im:history`, `im:read`
3. Install app to workspace
4. Copy Bot User OAuth Token
5. Copy Signing Secret from Basic Information

#### Step 3: Create Channel Configuration
**ADK Search:**
- "Slack channel configuration"
- "Slack bot setup"

**Actions:**
1. Create channel YAML file
2. Import using: `wxo channel import slack-channel.yaml`

#### Step 4: Configure Slack Event Subscriptions
1. Get webhook URL from channel creation
2. In Slack app settings, enable Event Subscriptions
3. Set Request URL to webhook URL
4. Subscribe to bot events: `message.im`

#### Step 5: Test Slack Integration
1. Send direct message to bot in Slack
2. Verify agent responds
3. Test conversation flow

### Slack Best Practices
- Use Socket Mode for easier development
- Request minimal required scopes
- Test in development workspace first
- Handle Slack-specific formatting (markdown)
- Implement proper error handling for Slack API

## Webchat Configuration

### Description
Webchat is automatically available for all agents. No separate configuration needed. Generate embed code to add to websites.

### Setup Workflow

#### Step 1: Generate Embed Code
```bash
wxo channel generate-webchat-embed --agent-name my-agent --environment draft
```
**Result:** HTML/JavaScript embed code

#### Step 2: Add to Website
1. Copy generated embed code
2. Paste before closing `</body>` tag in HTML
3. Customize appearance if needed

#### Step 3: Test Webchat
1. Load website with embed code
2. Click chat widget
3. Test conversation flow
4. Verify voice features work (if enabled)

### Customization Options
- Widget position (bottom-right, bottom-left)
- Color scheme
- Welcome message
- Avatar image
- Voice input/output toggle

## Channel-Specific Considerations

### Phone Channel
**Audio Quality:**
- Use 8000 Hz sample rate
- Use mulaw encoding
- Test with various phone types

**Latency:**
- Minimize processing time
- Use streaming mode when possible
- Optimize agent instructions

**Error Handling:**
- Provide DTMF fallback
- Handle dropped calls gracefully
- Implement retry logic

### Messaging Channels (WhatsApp/SMS)
**Message Length:**
- SMS: 160 character limit
- WhatsApp: 4096 character limit
- Break long responses into multiple messages

**Media Support:**
- WhatsApp supports images, audio, video
- SMS is text-only
- Consider channel capabilities in responses

**Asynchronous Nature:**
- Users may respond hours later
- Maintain conversation context
- Handle session timeouts

### Slack Channel
**Workspace Integration:**
- Respect workspace permissions
- Handle private vs public channels
- Support slash commands if needed

**Rich Formatting:**
- Use Slack markdown
- Support interactive components
- Handle attachments properly

### Webchat Channel
**Browser Compatibility:**
- Test across browsers
- Handle mobile devices
- Ensure responsive design

**Voice Features:**
- Microphone permissions
- Browser audio support
- Fallback to text if voice unavailable

## Multi-Channel Strategy

### Consistent Experience
- Use same agent across channels
- Maintain conversation context
- Provide channel-appropriate responses

### Channel-Specific Optimization
- Adjust response length per channel
- Use channel-specific features
- Handle media appropriately

### Routing Strategy
- Route based on user preference
- Consider channel capabilities
- Enable seamless channel switching

## Testing Channels

### Functional Testing
- Test basic conversation flow
- Verify tool invocations work
- Test error handling
- Validate authentication

### Integration Testing
- Test webhook connectivity
- Verify credential authentication
- Test provider-specific features
- Validate message delivery

### Performance Testing
- Test concurrent users
- Measure response latency
- Monitor error rates
- Check resource usage

### User Experience Testing
- Test with real users
- Gather feedback
- Measure satisfaction
- Track completion rates

## Troubleshooting

### Webhook Not Receiving Events
**Symptoms:** No messages reaching agent

**Checks:**
- Verify webhook URL is correct and accessible
- Check SSL certificate validity
- Review authentication credentials
- Check firewall rules

**Solutions:**
- Test webhook URL with curl or Postman
- Verify credentials are correct and not expired
- Check webhook configuration in provider console
- Review server logs for errors

### Authentication Failures
**Symptoms:** 401/403 errors

**Checks:**
- Verify credentials are current
- Check token expiration
- Review permission scopes
- Validate API key format

**Solutions:**
- Regenerate credentials
- Update environment variables
- Request additional scopes
- Check provider documentation

### Message Delivery Issues
**Symptoms:** Messages not sent/received

**Checks:**
- Verify phone number format
- Check account balance (Twilio)
- Review rate limits
- Check message content

**Solutions:**
- Use E.164 format for phone numbers
- Add credits to account
- Implement rate limiting
- Sanitize message content

### Poor Audio Quality (Phone)
**Symptoms:** Choppy or distorted audio

**Checks:**
- Verify sample rate (should be 8000 for phone)
- Check encoding (should be mulaw)
- Review network connectivity
- Test with different phones

**Solutions:**
- Use correct audio configuration
- Optimize network path
- Enable jitter buffer
- Test with different carriers

## Best Practices

### Security
- Never expose credentials in code
- Use environment variables
- Rotate credentials regularly
- Implement webhook signature verification

### Reliability
- Implement retry logic
- Handle timeouts gracefully
- Monitor webhook health
- Set up alerting

### Performance
- Optimize response times
- Use connection pooling
- Implement caching where appropriate
- Monitor latency metrics

### User Experience
- Provide clear error messages
- Handle edge cases gracefully
- Support multiple input methods
- Enable seamless escalation

### Monitoring
- Track message volume
- Monitor error rates
- Measure response times
- Analyze user satisfaction