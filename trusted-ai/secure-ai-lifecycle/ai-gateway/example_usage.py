"""
Example usage of IBM Guardium AI Security Gateway Client.

This script demonstrates various ways to use the GuardiumAIGateway class
in your applications.
"""

import os
from guardium_ai_gateway import GuardiumAIGateway, create_gateway


def example_basic_usage():
    """Basic usage example with environment variables."""
    print("=" * 70)
    print("Example 1: Basic Usage")
    print("=" * 70)

    # Set environment variables (or export them in your shell):
    # export GUARDIUM_GATEWAY_URL="https://gateway.example.com/v1"
    # export GUARDIUM_ENDPOINT_ID="your-endpoint-id"
    # export OPENAI_API_KEY="sk-..."

    gateway = GuardiumAIGateway()

    # Simple single-turn chat
    response = gateway.simple_chat(
        prompt="What is artificial intelligence?",
        model="gpt-3.5-turbo"
    )

    print("\nResponse:")
    print(response)
    print()


def example_with_parameters():
    """Example passing configuration as parameters."""
    print("=" * 70)
    print("Example 2: Configuration via Parameters")
    print("=" * 70)

    gateway = GuardiumAIGateway(
        gateway_url="https://gateway.example.com/v1",
        endpoint_identifier="prod-endpoint",
        api_key=os.getenv("OPENAI_API_KEY"),
        user_id="john.doe"
    )

    # Multi-turn conversation
    messages = [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "How do I read a file in Python?"},
    ]

    response = gateway.chat_completion(
        messages=messages,
        model="gpt-4",
        temperature=0.7,
        max_tokens=500
    )

    print("\nResponse:")
    print(response.choices[0].message.content)
    print()


def example_streaming():
    """Example using streaming responses."""
    print("=" * 70)
    print("Example 3: Streaming Responses")
    print("=" * 70)

    gateway = GuardiumAIGateway()

    messages = [
        {"role": "user", "content": "Tell me a short story about AI."}
    ]

    print("\nStreaming response:")
    stream = gateway.chat_completion_stream(
        messages=messages,
        model="gpt-3.5-turbo"
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)

    print("\n")


def example_with_session_tracking():
    """Example with session tracking for granular auditing."""
    print("=" * 70)
    print("Example 4: Session Tracking")
    print("=" * 70)

    gateway = GuardiumAIGateway()

    # Set session info for audit logging
    gateway.set_session_info(
        session_id="session-12345",
        user_id="jane.smith",
        user_email="jane.smith@example.com"
    )

    response = gateway.simple_chat(
        prompt="What are the benefits of AI security?",
        metadata={"department": "security", "project": "ai-audit"}
    )

    print("\nResponse:")
    print(response)
    print("\nSession info has been logged in Gateway audit logs.")
    print()


def example_multi_turn_conversation():
    """Example of a multi-turn conversation."""
    print("=" * 70)
    print("Example 5: Multi-Turn Conversation")
    print("=" * 70)

    gateway = GuardiumAIGateway()

    # Start conversation
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"}
    ]

    response1 = gateway.chat_completion(messages=messages, model="gpt-3.5-turbo")
    assistant_message = response1.choices[0].message.content

    print("\nUser: What is machine learning?")
    print(f"Assistant: {assistant_message}")

    # Continue conversation
    messages.append({"role": "assistant", "content": assistant_message})
    messages.append({"role": "user", "content": "Can you give me an example?"})

    response2 = gateway.chat_completion(messages=messages, model="gpt-3.5-turbo")

    print("\nUser: Can you give me an example?")
    print(f"Assistant: {response2.choices[0].message.content}")
    print()


def example_advanced_usage():
    """Example of advanced usage with custom OpenAI features."""
    print("=" * 70)
    print("Example 6: Advanced Usage")
    print("=" * 70)

    gateway = GuardiumAIGateway()

    # Use developer role for technical content
    messages = [
        {
            "role": "developer",
            "content": "You are an expert system that provides technical answers."
        },
        {"role": "user", "content": "Explain OAuth 2.0"}
    ]

    response = gateway.chat_completion(
        messages=messages,
        model="gpt-4",
        temperature=0.3,  # Lower temperature for factual content
        max_tokens=800,
        user_id="tech-team",
        metadata={
            "category": "technical-docs",
            "reviewed": False
        }
    )

    print("\nResponse:")
    print(response.choices[0].message.content)
    print()


def example_direct_client_access():
    """Example using direct OpenAI client for unsupported features."""
    print("=" * 70)
    print("Example 7: Direct Client Access")
    print("=" * 70)

    gateway = GuardiumAIGateway()

    # Get underlying client for advanced features
    client = gateway.get_client()

    # Use any OpenAI API feature
    # For example, generate embeddings:
    # embeddings = client.embeddings.create(
    #     input="The food was delicious and the waiter was friendly",
    #     model="text-embedding-ada-002"
    # )

    print("\nDirect client access allows you to use any OpenAI API feature")
    print("while still routing through the Guardium Gateway.")
    print()


def example_convenience_function():
    """Example using the convenience function."""
    print("=" * 70)
    print("Example 8: Using Convenience Function")
    print("=" * 70)

    # Quick setup with create_gateway()
    gateway = create_gateway(
        gateway_url="https://gateway.example.com/v1",
        endpoint_identifier="prod-endpoint",
        user_id="demo-user"
    )

    response = gateway.simple_chat("Hello, how can you help me today?")

    print("\nResponse:")
    print(response)
    print()


def example_interactive_cli():
    """Interactive CLI example (like original script)."""
    print("=" * 70)
    print("Example 9: Interactive CLI")
    print("=" * 70)

    gateway = GuardiumAIGateway()

    print("\nEnter your prompt below. Press ENTER twice to submit:")

    user_prompt = ""
    while True:
        line = input()
        if line:
            user_prompt += line + "\n"
        else:
            break

    if user_prompt.strip():
        response = gateway.simple_chat(
            prompt=user_prompt.strip(),
            system_message="You are a helpful assistant and your answer can contain technical language."
        )

        print("\n--- Response ---\n")
        print(response)
    else:
        print("No prompt entered.")


def example_error_handling():
    """Example with error handling."""
    print("=" * 70)
    print("Example 10: Error Handling")
    print("=" * 70)

    try:
        # This will fail if environment variables are not set
        gateway = GuardiumAIGateway()

        response = gateway.simple_chat("Test prompt")
        print(f"\nResponse: {response}")

    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
        print("\nMake sure to set the required environment variables:")
        print("  - GUARDIUM_GATEWAY_URL")
        print("  - GUARDIUM_ENDPOINT_ID")
        print("  - OPENAI_API_KEY")

    except Exception as e:
        print(f"\nError: {e}")
        print("Check your gateway configuration and network connectivity.")

    print()


if __name__ == "__main__":
    # Run examples (uncomment the ones you want to try)

    # Basic examples
    # example_basic_usage()
    # example_with_parameters()

    # Streaming
    # example_streaming()

    # Session tracking
    # example_with_session_tracking()

    # Conversations
    # example_multi_turn_conversation()

    # Advanced
    # example_advanced_usage()
    # example_direct_client_access()

    # Utilities
    # example_convenience_function()
    example_error_handling()

    # Interactive (uncomment to use)
    # example_interactive_cli()

    print("\nTo run specific examples, uncomment them in the __main__ block.")
