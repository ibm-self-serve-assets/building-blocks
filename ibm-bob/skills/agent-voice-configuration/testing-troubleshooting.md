# Testing and Troubleshooting Guide

## Overview
Comprehensive testing strategies and troubleshooting solutions for voice-enabled agents. Covers functional testing, voice quality assessment, performance validation, and common issue resolution.

## Testing Categories

### Functional Testing
Verify agent performs intended functions correctly.

**Tests:**
- Happy path scenarios
- Edge cases
- Error conditions
- Tool invocations
- Collaborator routing
- Multi-turn conversations

### Voice Quality Testing
Assess voice interaction quality and naturalness.

**Tests:**
- STT accuracy across accents and environments
- TTS naturalness and clarity
- Response length appropriateness
- Conversation flow smoothness
- Confirmation effectiveness
- Pronunciation accuracy

### Performance Testing
Evaluate speed and reliability.

**Tests:**
- Response latency
- Concurrent user handling
- Error rates
- System resource usage
- Channel availability
- Integration reliability

### User Experience Testing
Assess overall user satisfaction.

**Tests:**
- Task completion rate
- User satisfaction scores
- Conversation length
- Escalation rate
- Error recovery effectiveness
- Channel preference

## Test Scenarios

### Basic Interaction
**Description:** Simple, successful interaction

**Steps:**
1. User initiates conversation
2. Agent greets and offers help
3. User states need
4. Agent fulfills request
5. Agent confirms completion

**Expected Outcome:** Task completed successfully in under 2 minutes

### Multi-Turn Conversation
**Description:** Complex interaction requiring multiple exchanges

**Steps:**
1. User starts with general request
2. Agent asks clarifying questions
3. User provides additional information
4. Agent uses tools to gather data
5. Agent provides comprehensive response

**Expected Outcome:** Agent gathers all needed information, provides accurate response

### Error Recovery
**Description:** Handling misunderstandings

**Steps:**
1. User speaks unclearly
2. Agent misunderstands
3. User corrects
4. Agent acknowledges and proceeds correctly

**Expected Outcome:** Agent recovers gracefully, completes task

### Escalation
**Description:** Transferring to human agent

**Steps:**
1. User has complex issue
2. Agent attempts to help
3. Agent recognizes need for escalation
4. Agent transfers with context

**Expected Outcome:** Smooth handoff with context preserved

### Channel-Specific Tests

**Phone:**
- Call quality across carriers
- DTMF input handling
- Call transfer functionality
- Hold music/messages
- Call recording (if enabled)

**WhatsApp:**
- Message delivery
- Media handling (images, audio)
- Rich formatting
- Quick replies
- Template messages

**SMS:**
- Message length handling
- Character encoding
- Delivery confirmation
- Opt-out handling
- Rate limiting

**Slack:**
- Direct message handling
- Channel mentions
- Thread support
- Rich formatting
- Interactive components

## Voice Quality Assessment

### STT Accuracy Testing

**Test Different Accents:**
- US English
- UK English
- Australian English
- Non-native speakers

**Test Different Environments:**
- Quiet room
- Office background noise
- Street noise
- Phone quality audio

**Test Different Speech Patterns:**
- Fast speech
- Slow speech
- Mumbled speech
- Clear enunciation

**Metrics:**
- Word Error Rate (WER)
- Sentence Error Rate (SER)
- Recognition confidence scores

### TTS Naturalness Testing

**Evaluate:**
- Voice quality and clarity
- Pronunciation accuracy
- Pacing and rhythm
- Emotional appropriateness
- Consistency across responses

**Test Cases:**
- Numbers and dates
- Technical terms
- Acronyms
- Foreign words
- Punctuation handling

### Response Length Testing

**Measure:**
- Time to speak each response
- User attention span
- Information retention
- Comprehension rate

**Target:**
- 15-30 seconds per response
- Complete thoughts
- Clear next steps

## Performance Testing

### Latency Testing

**Measure:**
- STT processing time
- Agent thinking time
- TTS generation time
- Total response time

**Targets:**
- STT: < 500ms
- Agent: < 1000ms
- TTS: < 500ms
- Total: < 2000ms

### Load Testing

**Test:**
- Concurrent conversations
- Peak traffic handling
- Resource utilization
- Error rates under load

**Scenarios:**
- 10 concurrent users
- 50 concurrent users
- 100 concurrent users
- Spike traffic

### Reliability Testing

**Test:**
- Uptime percentage
- Error recovery
- Failover handling
- Data consistency

**Targets:**
- 99.9% uptime
- < 1% error rate
- Automatic recovery
- No data loss

## Common Issues and Solutions

### Poor STT Accuracy

**Symptoms:**
- Frequent misunderstandings
- Wrong words transcribed
- Missing words
- Garbled transcripts

**Diagnosis:**
- Check audio quality and sample rate
- Verify language model selection
- Review background noise levels
- Test with different microphones

**Solutions:**
- Switch to telephony-optimized model for phone
- Enable noise reduction
- Adjust silence detection sensitivity
- Consider custom language model for domain terms
- Increase audio sample rate if possible

### Unnatural TTS

**Symptoms:**
- Robotic speech
- Awkward pacing
- Mispronunciations
- Monotone delivery

**Diagnosis:**
- Verify voice selection
- Check rate and pitch settings
- Review response text formatting
- Test with different voices

**Solutions:**
- Try different TTS voices
- Adjust rate for more natural pacing (-10% to +10%)
- Use conversational language in responses
- Add SSML pauses for better pacing
- Fix pronunciation with phoneme tags

### High Latency

**Symptoms:**
- Noticeable delay between speech and response
- Users repeating themselves
- Conversation feels sluggish

**Diagnosis:**
- Measure STT processing time
- Check agent processing time
- Verify TTS generation time
- Review network latency

**Solutions:**
- Enable streaming mode for STT/TTS
- Optimize agent instructions for faster processing
- Use regional endpoints closer to users
- Cache common responses
- Reduce tool invocation complexity

### Channel Integration Failure

**Symptoms:**
- Webhook not receiving events
- Messages not delivered
- Authentication errors
- Connection timeouts

**Diagnosis:**
- Verify webhook URL is correct and accessible
- Check SSL certificate validity
- Review authentication credentials
- Check firewall rules
- Test with curl/Postman

**Solutions:**
- Update webhook URL in provider console
- Renew SSL certificate
- Refresh authentication credentials
- Open required firewall ports
- Verify webhook signature validation

### Agent Not Responding

**Symptoms:**
- No response to user input
- Timeout errors
- Partial responses

**Diagnosis:**
- Check agent status in Orchestrate
- Verify credentials are valid
- Review agent logs
- Test agent directly (not through channel)

**Solutions:**
- Restart agent if needed
- Update expired credentials
- Fix errors in agent instructions
- Check tool availability
- Verify model access

### Voice Configuration Issues

**Symptoms:**
- Voice features not working
- STT/TTS errors
- Audio quality problems

**Diagnosis:**
- Verify voice config exists
- Check provider credentials
- Review audio settings
- Test STT and TTS separately

**Solutions:**
- Import voice configuration
- Update provider credentials
- Adjust audio parameters (sample rate, encoding)
- Use appropriate models for channel type

### Tool Invocation Failures

**Symptoms:**
- Tools not being called
- Tool errors
- Incomplete responses

**Diagnosis:**
- Verify tool exists and is assigned
- Check tool credentials
- Review tool logs
- Test tool independently

**Solutions:**
- Assign tool to agent
- Update tool credentials
- Fix tool implementation errors
- Add error handling to tool
- Simplify tool parameters

### Conversation Context Loss

**Symptoms:**
- Agent forgets previous information
- Repeats questions
- Inconsistent responses

**Diagnosis:**
- Check session management
- Review context handling
- Verify conversation history

**Solutions:**
- Implement proper context tracking
- Use conversation memory
- Store important information
- Reference previous exchanges

## Debugging Techniques

### Enable Verbose Logging
```bash
export LOG_LEVEL=DEBUG
wxo agent test --agent-name my-agent --verbose
```

### Test Components Individually

**Test STT:**
```bash
# Record audio and test transcription
wxo voice-config test-stt --config-name my-config --audio-file test.wav
```

**Test TTS:**
```bash
# Generate speech from text
wxo voice-config test-tts --config-name my-config --text "Hello world"
```

**Test Agent:**
```bash
# Test agent without voice
wxo agent test --agent-name my-agent --text "Hello"
```

### Monitor Real-Time Logs
```bash
# Watch agent logs
wxo agent logs --agent-name my-agent --follow
```

### Analyze Conversation Transcripts
- Review full conversation history
- Identify patterns in failures
- Check for misunderstandings
- Analyze response times

## Testing Checklist

### Pre-Deployment Testing
- [ ] All happy path scenarios pass
- [ ] Edge cases handled correctly
- [ ] Error recovery works
- [ ] STT accuracy acceptable (>90%)
- [ ] TTS sounds natural
- [ ] Response times under 2 seconds
- [ ] All channels functional
- [ ] Tool invocations successful
- [ ] Security review passed
- [ ] Load testing completed

### Post-Deployment Monitoring
- [ ] Monitor error rates
- [ ] Track response times
- [ ] Analyze user satisfaction
- [ ] Review conversation logs
- [ ] Check channel availability
- [ ] Monitor resource usage
- [ ] Track escalation rate
- [ ] Gather user feedback

## Performance Optimization

### Reduce Latency
- Use streaming STT/TTS
- Optimize agent instructions
- Cache common responses
- Use regional endpoints
- Minimize tool complexity

### Improve STT Accuracy
- Use appropriate acoustic model
- Enable noise reduction
- Adjust silence detection
- Train custom language model
- Improve audio quality

### Enhance TTS Quality
- Select appropriate voice
- Adjust rate and pitch
- Use SSML for control
- Test with target audience
- Iterate based on feedback

### Optimize Resource Usage
- Implement connection pooling
- Use efficient data structures
- Cache frequently accessed data
- Minimize external API calls
- Monitor and tune performance

## Troubleshooting Workflow

### Step 1: Identify Issue
- Gather symptoms
- Collect error messages
- Review logs
- Reproduce problem

### Step 2: Isolate Component
- Test each component separately
- Identify failing component
- Narrow down root cause

### Step 3: Implement Fix
- Apply appropriate solution
- Test fix thoroughly
- Verify no side effects
- Document resolution

### Step 4: Validate
- Run full test suite
- Monitor for recurrence
- Update documentation
- Share learnings

## Best Practices

### Testing
- Test early and often
- Include diverse test scenarios
- Test with real users when possible
- Automate regression tests
- Monitor production interactions

### Troubleshooting
- Start with logs
- Test components individually
- Use systematic approach
- Document solutions
- Share knowledge

### Monitoring
- Set up comprehensive logging
- Configure meaningful alerts
- Create useful dashboards
- Review metrics regularly
- Act on insights

### Continuous Improvement
- Analyze failures
- Gather user feedback
- Iterate on design
- Update documentation
- Share best practices

## Emergency Response

### Critical Issues
- Agent completely down
- Security breach
- Data loss
- Widespread failures

### Response Steps
1. Assess severity
2. Notify stakeholders
3. Implement emergency fix or rollback
4. Communicate status
5. Conduct post-mortem

### Communication Template
```
INCIDENT: [Brief description]
SEVERITY: [Critical/High/Medium/Low]
STATUS: [Investigating/Identified/Fixing/Resolved]
IMPACT: [Who/what is affected]
ETA: [Expected resolution time]
UPDATES: [Regular status updates]
```

## Testing Tools and Resources

### ADK Testing Commands
```bash
# Test agent
wxo agent test --agent-name my-agent

# Test voice config
wxo voice-config test --config-name my-config

# Test channel
wxo channel test --channel-name my-channel

# View logs
wxo agent logs --agent-name my-agent
```

### External Tools
- **Postman**: Test webhooks and APIs
- **curl**: Test HTTP endpoints
- **Wireshark**: Analyze network traffic
- **Audio recording tools**: Test STT accuracy
- **Load testing tools**: JMeter, Locust

### Monitoring Tools
- Application logs
- System metrics
- User analytics
- Error tracking
- Performance monitoring

## Documentation

### What to Document
- Test plans and results
- Known issues and workarounds
- Performance baselines
- Configuration changes
- Incident reports

### Where to Document
- Test reports
- Runbooks
- Knowledge base
- Incident logs
- Change logs

## Continuous Testing

### Automated Tests
- Unit tests for tools
- Integration tests for workflows
- End-to-end tests for scenarios
- Performance tests for load
- Security tests for vulnerabilities

### Manual Tests
- User acceptance testing
- Exploratory testing
- Usability testing
- Accessibility testing
- Cross-browser/device testing

### Monitoring as Testing
- Real user monitoring
- Synthetic monitoring
- Error tracking
- Performance monitoring
- User feedback collection