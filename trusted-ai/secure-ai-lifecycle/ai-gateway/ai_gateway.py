#!/usr/bin/env python3

import datetime
import json
import os

from openai import OpenAI

# --- Configuration Section ---
# Fill in the Gateway base URL and endpoint identifier.
# These can be found in the Guardium AI Security Gateway policy > Configure Endpoint.
# For testing directly with OpenAI, use: "https://api.openai.com/v1"
base_url = "GAI Gateway Base URL goes here"
endpoint_identifier = "Your endpoint identifier goes here"

# Define request headers. The endpoint identifier is required.
# Optional headers (e.g., session info) can be added for more granular auditing.
# See: https://demos.ibm-ai-security.com/_docs/docs/applications/ai_firewall#session-features
headers = {
    "Content-Type": "application/json",
    "x-alltrue-llm-endpoint-identifier": endpoint_identifier,
    # Example optional session header:
    # 'x-alltrue-llm-firewall-user-session': '{"user-session-id": "08082025-efr", "user-session-user-id": "erwinfr", "user-session-user-email": "email@domain.tld"}'
}

# Initialize OpenAI client.
# Example: export OPENAI_API_KEY="your-key-here"
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "replace-with-your-key"),
    base_url=base_url,
    default_headers=headers,
)

# Metadata attached to the request for logging in the AI Gateway audit logs.
current_timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
metadata = {
    "user_id": "demo-user",  # replace with your own user ID
    "timestamp": current_timestamp,
}


# --- Prompt Input Function ---
def get_user_input():
    """
    Collect multi-line user input from CLI until an empty line is entered.
    Returns the full prompt as a single string.
    """
    user_prompt = ""
    print("Enter your prompt below. Press ENTER twice to submit:")

    while True:
        line = input()
        if line:
            user_prompt += line + "\n"
        else:
            break

    print("\nFinal prompt input:\n")
    print(user_prompt)
    return user_prompt


# --- Main Function ---
def main():
    finalText = get_user_input()

    # Send prompt to OpenAI (via Gateway) with developer + user roles.
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "developer",
                "content": "You are a helpful assistant and your answer can contain technical language.",
            },
            {"role": "user", "content": finalText},
        ],
        model="gpt-3.5-turbo",
        metadata=metadata,
    )

    # Print raw API response
    print("\n--- Full Raw Response ---\n")
    print(chat_completion)

    # Print cleaned-up response for readability
    print("\n--- Cleaned Response ---\n")
    returned_prompt = chat_completion.choices[0].message.content
    print(returned_prompt.strip())


# --- Entry Point ---
if __name__ == "__main__":
    main()
