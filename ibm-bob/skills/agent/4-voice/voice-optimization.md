# Voice Optimization Guide

## Overview
Techniques for optimizing agent instructions and responses for natural, effective voice interactions. Voice agents require different approaches than text agents.

## Core Principles

### Voice vs Text Differences
- **Voice is ephemeral**: Users can't re-read responses
- **Voice is sequential**: Information must be presented linearly
- **Voice is conversational**: Natural speech patterns expected
- **Voice is error-prone**: Misunderstandings more common

### Optimization Goals
- Keep responses concise and digestible
- Use natural, conversational language
- Confirm critical information
- Provide clear next steps
- Handle errors gracefully

## Response Length Optimization

### Target Length
- **Ideal:** 15-30 seconds per response (roughly 40-80 words)
- **Maximum:** 30 seconds before user attention wanes
- **Minimum:** Complete enough to be useful

### Techniques

**Break Long Information into Multiple Turns**
```
Bad (too long):
"Your order #12345 was placed on January 15th and includes 3 items: 
a blue widget ($29.99), a red gadget ($49.99), and a green doohickey ($19.99). 
The total was $99.97 plus $8.50 shipping. It shipped on January 17th via 
UPS Ground with tracking number 1Z999AA10123456784 and is expected to 
arrive on January 22nd between 9 AM and 5 PM."

Good (concise with offer for more):
"Your order 12345 shipped on January 17th and should arrive by January 22nd. 
Would you like the tracking number or details about the items?"
```

**Use Progressive Disclosure**
Start with essential information, offer details:
```
"I found your reservation for tomorrow at 7 PM. 
Would you like to modify the time, party size, or cancel?"
```

**Offer to Provide More Details**
```
"Your account balance is $1,234.56. 
Would you like to hear recent transactions or payment options?"
```

## Conversational Language

### Use Contractions
```
Bad: "I do not have access to that information."
Good: "I don't have access to that information."

Bad: "We will process your request."
Good: "We'll process your request."
```

### Use Simple Sentences
```
Bad: "The system, which was updated last week, now requires authentication."
Good: "The system was updated last week. It now requires authentication."
```

### Use Active Voice
```
Bad: "Your order was shipped by our warehouse."
Good: "Our warehouse shipped your order."

Bad: "The payment will be processed by the system."
Good: "The system will process your payment."
```

### Use Conversational Markers
```
Bad: "Furthermore, the policy states..."
Good: "Also, the policy states..."

Bad: "Subsequently, we will..."
Good: "Next, we'll..."

Bad: "Moreover, you should..."
Good: "Plus, you should..."
```

## Formatting for Voice

### Avoid Visual Formatting

**Don't Use:**
- Bullet points and numbered lists
- Tables and charts
- URLs and email addresses (spell them out if needed)
- Special characters and symbols
- Markdown or HTML formatting

**Instead Use:**
```
Bad: "Here are your options:
• Option A
• Option B  
• Option C"

Good: "You have three options. First, option A. Second, option B. Third, option C."

Bad: "Visit example.com for more info"
Good: "Visit example dot com for more info"

Bad: "Your total is $50.00"
Good: "Your total is fifty dollars"
```

### Describe Data Verbally
```
Bad: Trying to describe a table
Good: "Sales increased 20% in Q1, 15% in Q2, and 25% in Q3."
```

## Pronunciation Guidance

### Using SSML (Speech Synthesis Markup Language)

**Phoneme Tag - Specify Exact Pronunciation**
```xml
<phoneme alphabet="ipa" ph="təˈmeɪtoʊ">tomato</phoneme>
```

**Say-As Tag - Interpret Text as Specific Type**
```xml
<say-as interpret-as="telephone">555-1234</say-as>
<say-as interpret-as="date" format="mdy">12/31/2023</say-as>
<say-as interpret-as="currency">$50.00</say-as>
```

**Break Tag - Insert Pauses**
```xml
<break time="500ms"/>
<break strength="medium"/>
```

**Emphasis Tag - Add Emphasis**
```xml
<emphasis level="strong">important</emphasis>
```

### Common Pronunciation Issues

**Acronyms**
```
Problem: TTS may spell out or mispronounce acronyms
Solution: Spell out on first use, use phonetic spelling if needed

Bad: "API"
Good: "A P I" or "application programming interface"
```

**Numbers**
```
Problem: Large numbers can be unclear
Solution: Break into manageable chunks, use words for context

Bad: "1,234,567"
Good: "one point two million" or "about one and a quarter million"
```

**Technical Terms**
```
Problem: Technical jargon may be mispronounced
Solution: Use common terms or provide pronunciation guidance

Bad: "SQL database"
Good: "S Q L database" or "sequel database" (depending on preference)
```

## Pacing and Pauses

### Natural Pauses
- Add pauses between major topics
- Pause before important information
- Use pauses to indicate turn-taking

### Pacing Control

**Slow Down When:**
- Providing important information (phone numbers, addresses)
- Explaining complex concepts
- User seems confused

**Speed Up When:**
- Providing familiar information
- User is in a hurry

### Example with Pauses
```
"I found your order. <pause> It shipped yesterday. <pause> 
The tracking number is <slow> 1 Z 9 9 9 A A 1 0 1 2 3 4 5 6 7 8 4 </slow>. 
<pause> Would you like me to text that to you?"
```

## Confirmation and Verification

### When to Confirm
- Before taking irreversible actions
- When dealing with sensitive data
- After collecting multiple pieces of information
- When user seems uncertain

### Confirmation Techniques

**Explicit Confirmation**
Directly ask for confirmation:
```
"I heard you say your order number is 12345. Is that correct?"
```

**Implicit Confirmation**
Repeat information while proceeding:
```
"Okay, looking up order 12345 for you now."
```

**Summary Confirmation**
Summarize multiple items:
```
"So you want to return the blue widget and keep the other items. 
Should I proceed?"
```

## Voice-Specific Instructions Template

Add to agent instructions:
```
## Voice Interaction Guidelines

**Response Length:**
- Keep responses under 30 seconds when spoken
- Break long information into multiple turns
- Offer to provide more details if needed

**Language Style:**
- Use natural, conversational language
- Use contractions (don't, can't, we'll)
- Use simple, clear sentences
- Avoid technical jargon unless necessary

**Formatting:**
- Don't use bullet points or numbered lists
- Say "first, second, third" instead of numbers
- Spell out URLs and email addresses
- Describe data verbally, not visually

**Confirmation:**
- Confirm critical information before acting
- Repeat important details back to user
- Ask for explicit confirmation on irreversible actions

**Error Handling:**
- Acknowledge when you don't understand
- Ask user to rephrase or provide alternatives
- Offer DTMF input as fallback if available

**Pacing:**
- Speak clearly and at moderate pace
- Pause between major topics
- Slow down for important information
```

## Conversation Design Patterns

### Linear Pattern
Sequential steps toward a goal:
```
Greeting → Get order number → Look up order → Provide status
```
**Best for:** Simple, goal-oriented tasks

### Branching Pattern
Different paths based on user input:
```
Greeting → Issue type → Specific troubleshooting path
```
**Best for:** Multiple service options

### Mixed Initiative Pattern
User and agent can both drive conversation:
```
Open-ended customer service where either party can introduce topics
```
**Best for:** Complex, exploratory conversations

## Error Handling

### Recognition Errors (STT Misunderstands)
```
"I'm sorry, I didn't quite catch that. Could you repeat it?"
"I'm not sure I understood. Did you say [what I heard]?"
"Let me make sure I have this right. You said [confirmation]?"
```

### Understanding Errors (Agent Doesn't Understand Intent)
```
"I'm sorry, I'm not sure how to help with that. Could you rephrase?"
"I didn't understand. Would you like to [option A] or [option B]?"
"Let me offer some options. You can [list options]."
```

### System Errors (Technical Failures)
```
"I'm having trouble accessing that information right now. 
Can I call you back in a few minutes?"
"The system is temporarily unavailable. 
Would you like to try again or speak with someone?"
```

### Progressive Assistance
Gradually increase help level:
1. Simple reprompt
2. Provide examples
3. Offer menu of options
4. Transfer to human

## Testing Voice Optimization

### Response Length Test
- Read responses aloud
- Time each response
- Aim for 15-30 seconds
- Break longer responses

### Naturalness Test
- Does it sound conversational?
- Would you say this in person?
- Are there awkward phrases?
- Is pacing natural?

### Comprehension Test
- Can user understand without seeing text?
- Is information clear when spoken?
- Are numbers and details easy to follow?
- Is confirmation effective?

### Error Recovery Test
- How does agent handle misunderstandings?
- Are error messages helpful?
- Can user easily recover?
- Are alternatives provided?

## Optimization Checklist

**Before Deployment:**
- [ ] Responses under 30 seconds when spoken
- [ ] Conversational language used throughout
- [ ] No visual formatting (bullets, tables)
- [ ] Critical information confirmed
- [ ] Clear next steps provided
- [ ] Error handling implemented
- [ ] Pronunciation tested
- [ ] Pacing feels natural
- [ ] Tested with diverse voices/accents
- [ ] User feedback incorporated

## Best Practices

- Keep responses concise (15-30 seconds)
- Use conversational language and contractions
- Confirm critical information before acting
- Provide clear next steps
- Avoid visual formatting
- Test with diverse voices and accents
- Read responses aloud during development
- Iterate based on user testing
- Monitor real conversations for improvements
- Update instructions based on common issues

## Common Mistakes to Avoid

**Too Much Information**
```
Bad: Providing entire product catalog in one response
Good: Offering top 3 options with ability to hear more
```

**Too Formal**
```
Bad: "I shall endeavor to assist you with your inquiry."
Good: "I'll help you with that."
```

**Visual Descriptions**
```
Bad: "As shown in the table below..."
Good: "Here are the three main points..."
```

**No Confirmation**
```
Bad: Immediately processing order cancellation
Good: "Just to confirm, you want to cancel order 12345. Is that right?"
```

**Unclear Next Steps**
```
Bad: "Your order is processing."
Good: "Your order is processing. You'll get a confirmation email in a few minutes."
```

## Advanced Techniques

### Context-Aware Responses
Adjust based on conversation history:
```
First mention: "Your order number is 12345"
Later reference: "That order" or "Order 12345"
```

### Personality Consistency
Maintain consistent tone:
```
Friendly: "Great! Let me help you with that."
Professional: "Certainly. I'll assist you with that request."
```

### Emotional Intelligence
Recognize and respond to user emotion:
```
Frustrated user: "I understand this is frustrating. Let me help resolve this quickly."
Happy user: "I'm glad I could help! Is there anything else?"
```

### Proactive Guidance
Anticipate user needs:
```
"I see you're checking order status. Would you also like to know the delivery date?"