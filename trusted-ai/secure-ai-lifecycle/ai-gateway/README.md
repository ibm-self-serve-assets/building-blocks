# IBM Guardium AI Security Gateway Client

A Python client for routing LLM requests through IBM Guardium AI Security Gateway. This provides security monitoring, policy enforcement, and comprehensive audit logging for your AI interactions.

## What's in This Directory

- **`guardium_ai_gateway.py`** - Production-ready Python class for integrating Guardium AI Security Gateway into your applications. Drop-in replacement for OpenAI client with added security features.

- **`example_usage.py`** - Comprehensive examples demonstrating different usage patterns and features (10 different examples including interactive CLI, streaming, session tracking, and more).

- **`requirements.txt`** - Python dependencies (just `openai`).

## Features

- **Drop-in Replacement**: Minimal code changes to add security to existing OpenAI integrations
- **Security Monitoring**: All requests routed through Guardium AI Security Gateway
- **Policy Enforcement**: Automatic application of security policies configured in the gateway
- **Audit Logging**: Comprehensive logging with session tracking and custom metadata
- **Flexible Configuration**: Support for environment variables or direct parameters
- **Streaming Support**: Full support for streaming responses
- **Session Tracking**: Granular auditing with user session information

## Quick Start

### Installation

```bash
# Install dependencies
pip install openai

# Copy guardium_ai_gateway.py to your project
cp guardium_ai_gateway.py /path/to/your/project/
```

### Basic Usage

```python
from guardium_ai_gateway import GuardiumAIGateway

# Initialize with environment variables
# (Set GUARDIUM_GATEWAY_URL, GUARDIUM_ENDPOINT_ID, OPENAI_API_KEY)
gateway = GuardiumAIGateway()

# Simple chat
response = gateway.simple_chat("What is AI security?")
print(response)
```

### Configuration

Set these environment variables:

```bash
export GUARDIUM_GATEWAY_URL="https://your-gateway.example.com/v1"
export GUARDIUM_ENDPOINT_ID="your-endpoint-identifier"
export OPENAI_API_KEY="sk-..."
export GUARDIUM_USER_ID="your-user-id"  # Optional, defaults to "default-user"
```

Or pass configuration directly:

```python
gateway = GuardiumAIGateway(
    gateway_url="https://your-gateway.example.com/v1",
    endpoint_identifier="your-endpoint-identifier",
    api_key="sk-...",
    user_id="john.doe"
)
```

## Usage Examples

### 1. Simple Single-Turn Chat

```python
from guardium_ai_gateway import GuardiumAIGateway

gateway = GuardiumAIGateway()

answer = gateway.simple_chat(
    prompt="What is machine learning?",
    model="gpt-4"
)
print(answer)
```

### 2. Multi-Turn Conversation

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is Python?"}
]

response = gateway.chat_completion(
    messages=messages,
    model="gpt-3.5-turbo",
    temperature=0.7
)

print(response.choices[0].message.content)

# Continue conversation
messages.append({
    "role": "assistant",
    "content": response.choices[0].message.content
})
messages.append({
    "role": "user",
    "content": "Can you show me an example?"
})

response2 = gateway.chat_completion(messages=messages)
```

### 3. Streaming Responses

```python
stream = gateway.chat_completion_stream(
    messages=[{"role": "user", "content": "Tell me a story"}],
    model="gpt-4"
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### 4. Session Tracking for Auditing

```python
# Set session info for granular audit logging
gateway.set_session_info(
    session_id="session-12345",
    user_id="jane.smith",
    user_email="jane.smith@example.com"
)

# All subsequent requests will include this session info
response = gateway.simple_chat(
    prompt="What are security best practices?",
    metadata={"department": "security", "project": "compliance"}
)
```

### 5. Advanced Usage

```python
# Use developer role and custom metadata
messages = [
    {
        "role": "developer",
        "content": "You are an expert technical assistant."
    },
    {"role": "user", "content": "Explain API authentication"}
]

response = gateway.chat_completion(
    messages=messages,
    model="gpt-4",
    temperature=0.3,
    max_tokens=1000,
    user_id="tech-team",
    metadata={
        "category": "technical-docs",
        "sensitivity": "internal"
    }
)
```

### 6. Direct Client Access

```python
# Get underlying OpenAI client for advanced features
client = gateway.get_client()

# Use any OpenAI API feature while routing through gateway
embeddings = client.embeddings.create(
    input="Sample text",
    model="text-embedding-ada-002"
)
```

## Finding Your Configuration

### Gateway URL and Endpoint Identifier

1. Log in to IBM Guardium AI Security console
2. Navigate to **Gateway Policy > Configure Endpoint**
3. Find your:
   - **Gateway Base URL** (e.g., `https://gateway.example.com/v1`)
   - **Endpoint Identifier** (unique ID for your endpoint)

### Testing Without Gateway

To test with OpenAI directly (bypassing the gateway):

```python
gateway = GuardiumAIGateway(
    gateway_url="https://api.openai.com/v1",  # Direct OpenAI
    endpoint_identifier="test",  # Any value
    api_key="sk-..."
)
```

## API Reference

### GuardiumAIGateway

Main client class for gateway interactions.

#### `__init__(gateway_url, endpoint_identifier, api_key, user_id, additional_headers)`

Initialize the gateway client.

**Parameters:**
- `gateway_url` (str): Base URL of the Guardium AI Gateway
- `endpoint_identifier` (str): Endpoint identifier from Gateway policy
- `api_key` (str): OpenAI API key
- `user_id` (str, optional): User ID for audit logging
- `additional_headers` (dict, optional): Additional request headers

#### `simple_chat(prompt, system_message, model, **kwargs)`

Simplified chat interface for single-turn conversations.

**Parameters:**
- `prompt` (str): User question/prompt
- `system_message` (str): System message (default: "You are a helpful assistant.")
- `model` (str): Model name (default: "gpt-3.5-turbo")
- `**kwargs`: Additional arguments

**Returns:** str - Assistant's response

#### `chat_completion(messages, model, temperature, max_tokens, user_id, metadata, **kwargs)`

Create a chat completion request (like OpenAI's API).

**Parameters:**
- `messages` (list): List of message dicts with 'role' and 'content'
- `model` (str): Model name (default: "gpt-3.5-turbo")
- `temperature` (float, optional): Sampling temperature
- `max_tokens` (int, optional): Maximum tokens
- `user_id` (str, optional): User ID override
- `metadata` (dict, optional): Custom audit metadata
- `**kwargs`: Additional OpenAI parameters

**Returns:** ChatCompletion - Full API response

#### `chat_completion_stream(messages, model, temperature, max_tokens, user_id, metadata, **kwargs)`

Create a streaming chat completion request.

**Parameters:** Same as `chat_completion()`

**Returns:** Iterator[ChatCompletionChunk] - Stream of response chunks

#### `set_session_info(session_id, user_id, user_email)`

Set session tracking information for audit logs.

**Parameters:**
- `session_id` (str): Unique session identifier
- `user_id` (str, optional): User ID for the session
- `user_email` (str, optional): User email for the session

#### `get_client()`

Get the underlying OpenAI client for advanced features.

**Returns:** OpenAI - Configured OpenAI client instance

### Convenience Functions

#### `create_gateway(gateway_url, endpoint_identifier, api_key, **kwargs)`

Quick gateway creation helper.

**Returns:** GuardiumAIGateway instance

## Sample Migration Guide

If you're using a basic OpenAI integration:

#### Before (Direct OpenAI)
```python
# Direct OpenAI approach
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

chat_completion = client.chat.completions.create(
    messages=[...],
    model="gpt-3.5-turbo"
)
```

#### After (With Guardium Gateway)
```python
# Guardium Gateway approach
from guardium_ai_gateway import GuardiumAIGateway

gateway = GuardiumAIGateway()

response = gateway.chat_completion(
    messages=[...],
    model="gpt-3.5-turbo"
)
```

## Error Handling

```python
from guardium_ai_gateway import GuardiumAIGateway
from openai import OpenAIError

try:
    gateway = GuardiumAIGateway()
    response = gateway.simple_chat("Hello")

except ValueError as e:
    # Configuration error
    print(f"Configuration error: {e}")

except OpenAIError as e:
    # OpenAI API error
    print(f"API error: {e}")

except Exception as e:
    # Other errors
    print(f"Unexpected error: {e}")
```

## Best Practices

1. **Environment Variables**: Use environment variables for credentials, never hardcode them
2. **Session Tracking**: Use `set_session_info()` for better audit trails
3. **Metadata**: Add relevant metadata to help with compliance and auditing
4. **Error Handling**: Always wrap API calls in try-except blocks
5. **User IDs**: Use meaningful user IDs to track usage by person/team

## Security Notes

- All requests are routed through Guardium AI Security Gateway
- The gateway applies security policies before forwarding to OpenAI
- Comprehensive audit logs are maintained in the gateway
- Session information helps track usage at a granular level
- Custom metadata enhances compliance reporting

## Support

For more information:
- **Guardium AI Security**: https://demos.ibm-ai-security.com/_docs/docs/applications/ai_firewall
- **Session Features**: https://demos.ibm-ai-security.com/_docs/docs/applications/ai_firewall#session-features
