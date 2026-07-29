"""
watsonx Orchestrate Integration Library
Provides easy-to-use functions for integrating with watsonx Orchestrate agents
Supports IBM Cloud, AWS, and On-premises deployments
"""

import json
import os
import http.client
import time
from urllib.parse import urlencode, urlparse
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List


def load_env_file(path=".env"):
    """Load environment variables from .env file"""
    env = {}
    if not os.path.exists(path):
        return env

    with open(path, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip()
    return env


class WatsonxOrchestrateClient:
    """Client for interacting with watsonx Orchestrate API"""
    
    def __init__(self, env_file=".env"):
        """
        Initialize the client with credentials from environment
        
        Args:
            env_file: Path to .env file (default: ".env")
        """
        # Load environment
        env = load_env_file(env_file)
        
        # Get platform
        self.platform = os.getenv('WATSONX_PLATFORM') or env.get('WATSONX_PLATFORM', 'ibm_cloud')
        
        # Get credentials
        self.api_key = os.getenv('WATSONX_API_KEY') or env.get('WATSONX_API_KEY') or env.get('WXO_API_KEY')
        
        # Get service URL or instance ID
        service_url = os.getenv('WATSONX_SERVICE_URL') or env.get('WATSONX_SERVICE_URL') or env.get('Service_instance_URL')
        self.instance_id = os.getenv('WATSONX_INSTANCE_ID') or env.get('WATSONX_INSTANCE_ID')
        
        # Extract host and instance from service URL if provided
        if service_url:
            self.host, extracted_instance = self._extract_host_and_instance(service_url)
            if not self.instance_id:
                self.instance_id = extracted_instance
        else:
            # Default host for AWS/IBM Cloud
            self.host = "api.dl.watson-orchestrate.ibm.com"
        
        # Token management
        self._token = None
        self._token_expiry = None
        
        # Validate credentials
        self._validate_credentials()
    
    def _validate_credentials(self):
        """Validate that required credentials are present"""
        if not self.api_key:
            raise ValueError("WATSONX_API_KEY (or WXO_API_KEY) not found in environment")
        if not self.instance_id:
            raise ValueError("WATSONX_INSTANCE_ID not found in environment")
    
    def _extract_host_and_instance(self, service_instance_url: str) -> tuple:
        """
        Extract the API host and instance ID from the service instance URL.
        
        Service URL format:
          https://api.{region}.watson-orchestrate.cloud.ibm.com/instances/{instance_id}
        
        Args:
            service_instance_url: Full service URL
            
        Returns:
            Tuple of (host, instance_id)
        """
        parsed = urlparse(service_instance_url)
        host = parsed.netloc
        
        path_parts = [part for part in parsed.path.split("/") if part]
        try:
            instance_index = path_parts.index("instances")
            instance_id = path_parts[instance_index + 1]
        except (ValueError, IndexError) as exc:
            raise ValueError(f"Unable to determine instance ID from URL: {service_instance_url}") from exc
        
        return host, instance_id
    
    def _get_token(self) -> str:
        """Get valid authentication token, refreshing if necessary"""
        if self._token and self._token_expiry:
            # Check if token is still valid (with 5 min buffer)
            if datetime.now() < (self._token_expiry - timedelta(minutes=5)):
                return self._token
        
        # Generate new token based on platform
        if self.platform == 'ibm_cloud':
            return self._generate_iam_token()
        else:
            return self._generate_jwt_token()
    
    def _generate_iam_token(self) -> str:
        """Generate IAM token for IBM Cloud"""
        conn = http.client.HTTPSConnection("iam.cloud.ibm.com")
        
        try:
            payload = urlencode({
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.api_key
            })
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
            
            conn.request("POST", "/identity/token", payload, headers)
            res = conn.getresponse()
            data = json.loads(res.read().decode('utf-8'))
            
            if res.status != 200:
                raise Exception(f"IAM token generation failed: {data}")
            
            self._token = data['access_token']
            self._token_expiry = datetime.now() + timedelta(seconds=data['expires_in'])
            
            return self._token
            
        finally:
            conn.close()
    
    def _generate_jwt_token(self) -> str:
        """Generate JWT token for AWS"""
        conn = http.client.HTTPSConnection("iam.platform.saas.ibm.com")
        
        try:
            payload = json.dumps({"apikey": self.api_key})
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            conn.request("POST", "/siusermgr/api/1.0/apikeys/token", payload, headers)
            res = conn.getresponse()
            data = json.loads(res.read().decode('utf-8'))
            
            if res.status != 200:
                raise Exception(f"JWT token generation failed: {data}")
            
            self._token = data['token']
            self._token_expiry = datetime.now() + timedelta(seconds=data['expires_in'])
            
            return self._token
            
        finally:
            conn.close()
    
    def list_agents(self, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """
        List all available agents
        
        Args:
            include_hidden: Include hidden agents
            
        Returns:
            List of agent dictionaries
        """
        token = self._get_token()
        conn = http.client.HTTPSConnection(self.host)
        
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
            
            path = f"/instances/{self.instance_id}/v1/orchestrate/agents?include_hidden={str(include_hidden).lower()}"
            
            conn.request("GET", path, headers=headers)
            res = conn.getresponse()
            data = res.read()
            
            if res.status >= 400:
                raise Exception(f"API error {res.status}: {data.decode('utf-8')}")
            
            parsed = json.loads(data.decode('utf-8'))
            agents = parsed if isinstance(parsed, list) else parsed.get("agents", parsed.get("data", []))
            
            return agents
            
        finally:
            conn.close()
    
    def invoke_agent(self, agent_id: str, message: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Invoke an agent with a message
        
        Args:
            agent_id: The agent ID
            message: The message to send
            thread_id: Optional existing thread ID
            
        Returns:
            Run details with run_id, thread_id, etc.
        """
        token = self._get_token()
        conn = http.client.HTTPSConnection(self.host)
        
        try:
            # CRITICAL: Message must be object with role and content
            payload = {
                "agent_id": agent_id,
                "message": {
                    "role": "user",
                    "content": message
                }
            }
            
            if thread_id:
                payload["thread_id"] = thread_id
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            path = f"/instances/{self.instance_id}/v1/orchestrate/runs"
            conn.request("POST", path, json.dumps(payload), headers)
            res = conn.getresponse()
            data = res.read()
            
            if res.status >= 400:
                raise Exception(f"API error {res.status}: {data.decode('utf-8')}")
            
            return json.loads(data.decode('utf-8'))
            
        finally:
            conn.close()
    
    def get_run_details(self, run_id: str) -> Dict[str, Any]:
        """
        Get details of a specific run
        
        Args:
            run_id: The run ID
            
        Returns:
            Complete run details including response
        """
        token = self._get_token()
        conn = http.client.HTTPSConnection(self.host)
        
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }
            
            path = f"/instances/{self.instance_id}/v1/orchestrate/runs/{run_id}"
            conn.request("GET", path, headers=headers)
            res = conn.getresponse()
            data = res.read()
            
            if res.status >= 400:
                raise Exception(f"API error {res.status}: {data.decode('utf-8')}")
            
            return json.loads(data.decode('utf-8'))
            
        finally:
            conn.close()
    
    def wait_for_completion(self, run_id: str, max_wait: int = 30) -> Dict[str, Any]:
        """
        Poll run status until completed or timeout
        
        Args:
            run_id: The run ID
            max_wait: Maximum seconds to wait
            
        Returns:
            Complete run details when status is 'completed'
        """
        start_time = time.time()
        poll_interval = 1
        
        while time.time() - start_time < max_wait:
            run_details = self.get_run_details(run_id)
            status = run_details.get('status')
            
            if status == 'completed':
                return run_details
            elif status == 'failed':
                raise RuntimeError(f"Run failed: {run_details.get('last_error')}")
            elif status == 'cancelled':
                raise RuntimeError("Run was cancelled")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Run did not complete within {max_wait} seconds")
    
    def extract_response(self, run_details: Dict[str, Any]) -> str:
        """
        Extract agent response from run details
        
        Args:
            run_details: Complete run details
            
        Returns:
            The agent's response text
        """
        try:
            result = run_details['result']
            data = result['data']
            message = data['message']
            content = message['content']
            text = content[0]['text']
            return text
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Failed to extract response: {e}")
    
    def send_message(self, agent_id: str, message: str, thread_id: Optional[str] = None) -> tuple:
        """
        Complete workflow: Send message and get response
        
        Args:
            agent_id: The agent ID
            message: The message to send
            thread_id: Optional existing thread ID
            
        Returns:
            Tuple of (response_text, thread_id)
        """
        # Invoke agent
        result = self.invoke_agent(agent_id, message, thread_id)
        run_id = result['run_id']
        new_thread_id = result.get('thread_id', thread_id)
        
        # Wait for completion
        run_details = self.wait_for_completion(run_id)
        
        # Extract and return response
        response = self.extract_response(run_details)
        return response, new_thread_id
    
    def chat_completions(self, agent_id: str, message: str) -> str:
        """
        OpenAI-compatible chat completions endpoint
        
        Args:
            agent_id: The agent ID
            message: The message to send
            
        Returns:
            The agent's response text
        """
        token = self._get_token()
        conn = http.client.HTTPSConnection(self.host)
        
        try:
            payload = json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "stream": False
            })
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            path = f"/instances/{self.instance_id}/v1/orchestrate/{agent_id}/chat/completions"
            
            conn.request("POST", path, body=payload, headers=headers)
            res = conn.getresponse()
            data = res.read().decode("utf-8")
            
            if res.status >= 400:
                raise Exception(f"API error {res.status}: {data}")
            
            parsed = json.loads(data)
            return parsed['choices'][0]['message']['content']
            
        finally:
            conn.close()


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = WatsonxOrchestrateClient()
    
    # List agents
    print("Available agents:")
    agents = client.list_agents()
    for agent in agents:
        agent_name = agent.get("name") or agent.get("display_name", "unknown")
        agent_id = agent.get("agent_id") or agent.get("id", "unknown")
        print(f"- {agent_name}: {agent_id}")
    
    # Send a message (uncomment and add your agent ID)
    # agent_id = "your-agent-id"
    # response, thread_id = client.send_message(agent_id, "Hello, how can you help me?")
    # print(f"\nAgent: {response}")
    # print(f"Thread ID: {thread_id}")

# Made with Bob
