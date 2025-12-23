"""
IBM Guardium AI Security Gateway Client

A Python client for routing LLM requests through IBM Guardium AI Security Gateway.
This provides security monitoring, policy enforcement, and audit logging for AI interactions.

Features:
- Drop-in replacement for OpenAI client
- Automatic request routing through security gateway
- Session tracking and audit metadata
- Support for chat completions and streaming
- Flexible configuration via environment variables or parameters

Example:
    from guardium_ai_gateway import GuardiumAIGateway

    # Initialize client
    gateway = GuardiumAIGateway(
        gateway_url="https://gateway.example.com/v1",
        endpoint_identifier="my-endpoint",
        api_key="sk-..."
    )

    # Use like standard OpenAI client
    response = gateway.chat_completion(
        messages=[{"role": "user", "content": "Hello!"}],
        model="gpt-4"
    )
    print(response)
"""

import os
import datetime
from typing import Dict, Any, List, Optional, Iterator
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk


class GuardiumAIGateway:
    """
    Client for routing LLM requests through IBM Guardium AI Security Gateway.

    This class provides a clean API for integrating Guardium AI Security into
    your applications with minimal code changes. All OpenAI API calls are
    automatically routed through the security gateway for monitoring and
    policy enforcement.
    """

    def __init__(
        self,
        gateway_url: Optional[str] = None,
        endpoint_identifier: Optional[str] = None,
        api_key: Optional[str] = None,
        user_id: Optional[str] = None,
        additional_headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the Guardium AI Gateway client.

        Args:
            gateway_url: Base URL of the Guardium AI Gateway.
                Defaults to GUARDIUM_GATEWAY_URL env var.
                For direct OpenAI access (no gateway), use "https://api.openai.com/v1"
            endpoint_identifier: Endpoint identifier from Gateway policy configuration.
                Defaults to GUARDIUM_ENDPOINT_ID env var.
            api_key: OpenAI API key. Defaults to OPENAI_API_KEY env var.
            user_id: User ID for audit logging. Defaults to GUARDIUM_USER_ID env var
                or "default-user".
            additional_headers: Additional headers to include in requests (optional).

        Raises:
            ValueError: If required configuration is missing.

        Example:
            # Using environment variables
            gateway = GuardiumAIGateway()

            # Or pass directly
            gateway = GuardiumAIGateway(
                gateway_url="https://gateway.example.com/v1",
                endpoint_identifier="prod-endpoint",
                api_key="sk-..."
            )
        """
        self.gateway_url = gateway_url or os.getenv("GUARDIUM_GATEWAY_URL")
        self.endpoint_identifier = endpoint_identifier or os.getenv("GUARDIUM_ENDPOINT_ID")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.user_id = user_id or os.getenv("GUARDIUM_USER_ID", "default-user")

        if not self.gateway_url:
            raise ValueError(
                "Gateway URL must be provided via gateway_url parameter or "
                "GUARDIUM_GATEWAY_URL environment variable"
            )

        if not self.endpoint_identifier:
            raise ValueError(
                "Endpoint identifier must be provided via endpoint_identifier parameter or "
                "GUARDIUM_ENDPOINT_ID environment variable"
            )

        if not self.api_key:
            raise ValueError(
                "API key must be provided via api_key parameter or "
                "OPENAI_API_KEY environment variable"
            )

        # Build headers
        self.headers = {
            "Content-Type": "application/json",
            "x-alltrue-llm-endpoint-identifier": self.endpoint_identifier,
        }

        if additional_headers:
            self.headers.update(additional_headers)

        # Initialize OpenAI client with gateway configuration
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.gateway_url,
            default_headers=self.headers,
        )

    def _build_metadata(
        self,
        user_id: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build metadata for audit logging.

        Args:
            user_id: User ID override for this request.
            additional_metadata: Additional metadata to include.

        Returns:
            Metadata dictionary for the request.
        """
        metadata = {
            "user_id": user_id or self.user_id,
            "timestamp": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        }

        if additional_metadata:
            metadata.update(additional_metadata)

        return metadata

    def set_session_info(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None
    ) -> None:
        """
        Set session information for more granular auditing.

        This adds session tracking headers that appear in the Gateway audit logs.
        Call this method to update session info before making requests.

        Args:
            session_id: Unique session identifier.
            user_id: User ID for the session (optional).
            user_email: User email for the session (optional).

        Example:
            gateway.set_session_info(
                session_id="session-12345",
                user_id="john.doe",
                user_email="john.doe@example.com"
            )
        """
        import json

        session_data = {"user-session-id": session_id}
        if user_id:
            session_data["user-session-user-id"] = user_id
        if user_email:
            session_data["user-session-user-email"] = user_email

        self.headers["x-alltrue-llm-firewall-user-session"] = json.dumps(session_data)
        self.client.default_headers = self.headers

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ChatCompletion:
        """
        Create a chat completion request through the gateway.

        This is a drop-in replacement for openai.chat.completions.create().

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            model: Model to use (default: "gpt-3.5-turbo").
            temperature: Sampling temperature (optional).
            max_tokens: Maximum tokens to generate (optional).
            user_id: User ID override for this request (optional).
            metadata: Additional metadata for audit logs (optional).
            **kwargs: Additional arguments passed to OpenAI API.

        Returns:
            ChatCompletion response from the API.

        Example:
            response = gateway.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is AI?"}
                ],
                model="gpt-4",
                temperature=0.7
            )
            print(response.choices[0].message.content)
        """
        request_metadata = self._build_metadata(user_id, metadata)

        # Build request parameters
        params = {
            "messages": messages,
            "model": model,
            "metadata": request_metadata,
            **kwargs
        }

        if temperature is not None:
            params["temperature"] = temperature
        if max_tokens is not None:
            params["max_tokens"] = max_tokens

        return self.client.chat.completions.create(**params)

    def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Iterator[ChatCompletionChunk]:
        """
        Create a streaming chat completion request through the gateway.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            model: Model to use (default: "gpt-3.5-turbo").
            temperature: Sampling temperature (optional).
            max_tokens: Maximum tokens to generate (optional).
            user_id: User ID override for this request (optional).
            metadata: Additional metadata for audit logs (optional).
            **kwargs: Additional arguments passed to OpenAI API.

        Yields:
            ChatCompletionChunk objects as they arrive.

        Example:
            stream = gateway.chat_completion_stream(
                messages=[{"role": "user", "content": "Tell me a story"}],
                model="gpt-4"
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="")
        """
        request_metadata = self._build_metadata(user_id, metadata)

        # Build request parameters
        params = {
            "messages": messages,
            "model": model,
            "metadata": request_metadata,
            "stream": True,
            **kwargs
        }

        if temperature is not None:
            params["temperature"] = temperature
        if max_tokens is not None:
            params["max_tokens"] = max_tokens

        return self.client.chat.completions.create(**params)

    def simple_chat(
        self,
        prompt: str,
        system_message: str = "You are a helpful assistant.",
        model: str = "gpt-3.5-turbo",
        **kwargs
    ) -> str:
        """
        Simplified chat interface for single-turn conversations.

        Args:
            prompt: User prompt/question.
            system_message: System message to set assistant behavior
                (default: "You are a helpful assistant.").
            model: Model to use (default: "gpt-3.5-turbo").
            **kwargs: Additional arguments passed to chat_completion().

        Returns:
            Assistant's response as a string.

        Example:
            answer = gateway.simple_chat("What is the capital of France?")
            print(answer)  # "The capital of France is Paris."
        """
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]

        response = self.chat_completion(messages=messages, model=model, **kwargs)
        return response.choices[0].message.content

    def get_client(self) -> OpenAI:
        """
        Get the underlying OpenAI client for advanced usage.

        Use this if you need direct access to the OpenAI client for
        features not wrapped by GuardiumAIGateway.

        Returns:
            Configured OpenAI client instance.

        Example:
            client = gateway.get_client()
            # Use any OpenAI API method
            embeddings = client.embeddings.create(...)
        """
        return self.client


# Convenience function for quick setup
def create_gateway(
    gateway_url: Optional[str] = None,
    endpoint_identifier: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs
) -> GuardiumAIGateway:
    """
    Convenience function to create a GuardiumAIGateway instance.

    Args:
        gateway_url: Base URL of the Guardium AI Gateway.
        endpoint_identifier: Endpoint identifier from Gateway policy.
        api_key: OpenAI API key.
        **kwargs: Additional arguments passed to GuardiumAIGateway.

    Returns:
        Configured GuardiumAIGateway instance.

    Example:
        gateway = create_gateway(
            gateway_url="https://gateway.example.com/v1",
            endpoint_identifier="prod-endpoint"
        )
    """
    return GuardiumAIGateway(
        gateway_url=gateway_url,
        endpoint_identifier=endpoint_identifier,
        api_key=api_key,
        **kwargs
    )
