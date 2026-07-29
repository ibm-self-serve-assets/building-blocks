"""
Connection Test Script for watsonx Orchestrate
Tests authentication and connectivity across all platforms
"""

import json
import os
import http.client
from urllib.parse import urlencode, urlparse


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


def detect_platform(service_url):
    """Detect platform based on service URL"""
    if not service_url:
        return None
    
    url_lower = service_url.lower()
    
    if "watson-orchestrate.cloud.ibm.com" in url_lower:
        return "ibm_cloud"
    if ".dl.watson-orchestrate.ibm.com" in url_lower:
        return "aws"
    return "on_prem"


def get_iam_token(api_key):
    """Generate IBM Cloud IAM token"""
    conn = http.client.HTTPSConnection("iam.cloud.ibm.com")
    
    try:
        payload = urlencode({
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key
        })
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        conn.request("POST", "/identity/token", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        
        if res.status != 200:
            return None, f"IAM token failed: {data}"
        
        parsed = json.loads(data)
        return parsed.get("access_token"), None
    
    except Exception as e:
        return None, str(e)
    
    finally:
        conn.close()


def get_jwt_token(api_key):
    """Generate JWT token for AWS/On-premises"""
    conn = http.client.HTTPSConnection("iam.platform.saas.ibm.com")
    
    try:
        payload = json.dumps({"apikey": api_key})
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        conn.request("POST", "/siusermgr/api/1.0/apikeys/token", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        
        if res.status != 200:
            return None, f"JWT token failed: {data}"
        
        parsed = json.loads(data)
        return parsed.get("token"), None
    
    except Exception as e:
        return None, str(e)
    
    finally:
        conn.close()


def extract_host_and_instance(service_url):
    """Extract host and instance ID from service URL"""
    parsed = urlparse(service_url)
    host = parsed.netloc
    
    path_parts = [part for part in parsed.path.split("/") if part]
    try:
        instance_index = path_parts.index("instances")
        instance_id = path_parts[instance_index + 1]
    except (ValueError, IndexError):
        return None, None, "Unable to extract instance ID from URL"
    
    return host, instance_id, None


def test_agents_endpoint(host, instance_id, token):
    """Test the agents list endpoint"""
    conn = http.client.HTTPSConnection(host)
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        path = f"/instances/{instance_id}/v1/orchestrate/agents?include_hidden=false"
        conn.request("GET", path, headers=headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        
        if res.status != 200:
            return False, f"Status {res.status}: {data}"
        
        parsed = json.loads(data)
        agents = parsed if isinstance(parsed, list) else parsed.get("agents", parsed.get("data", []))
        
        return True, f"Found {len(agents)} agent(s)"
    
    except Exception as e:
        return False, str(e)
    
    finally:
        conn.close()


def main():
    """Run connection tests"""
    print("\n" + "="*60)
    print("  watsonx Orchestrate Connection Test")
    print("="*60)
    
    # Load credentials
    env = load_env_file()
    api_key = (os.getenv("WATSONX_API_KEY") or env.get("WATSONX_API_KEY") or 
               os.getenv("WXO_API_KEY") or env.get("WXO_API_KEY"))
    service_url = (os.getenv("WATSONX_SERVICE_URL") or env.get("WATSONX_SERVICE_URL") or 
                   os.getenv("Service_instance_URL") or env.get("Service_instance_URL"))
    
    print("\n1. Checking credentials...")
    
    if not api_key:
        print("   ❌ API key not found")
        print("   Set WATSONX_API_KEY or WXO_API_KEY in .env file")
        return
    print("   ✓ API key found")
    
    if not service_url:
        print("   ❌ Service URL not found")
        print("   Set WATSONX_SERVICE_URL or Service_instance_URL in .env file")
        return
    print("   ✓ Service URL found")
    
    # Detect platform
    print("\n2. Detecting platform...")
    platform = detect_platform(service_url)
    
    platform_names = {
        "ibm_cloud": "IBM Cloud",
        "aws": "AWS",
        "on_prem": "On-premises"
    }
    
    if platform:
        print(f"   ✓ Platform: {platform_names.get(platform, platform)}")
    else:
        print("   ⚠️  Could not auto-detect platform")
        return
    
    # Extract connection details
    print("\n3. Parsing service URL...")
    host, instance_id, error = extract_host_and_instance(service_url)
    
    if error:
        print(f"   ❌ {error}")
        return
    
    print(f"   ✓ Host: {host}")
    print(f"   ✓ Instance ID: {instance_id}")
    
    # Test authentication
    print("\n4. Testing authentication...")
    
    if platform == "ibm_cloud":
        token, error = get_iam_token(api_key)
        auth_type = "IAM token"
    else:
        token, error = get_jwt_token(api_key)
        auth_type = "JWT token"
    
    if error:
        print(f"   ❌ {auth_type} generation failed")
        print(f"   Error: {error}")
        return
    
    print(f"   ✓ {auth_type} generated successfully")
    
    # Test API endpoint
    print("\n5. Testing API connectivity...")
    success, message = test_agents_endpoint(host, instance_id, token)
    
    if not success:
        print(f"   ❌ API test failed")
        print(f"   Error: {message}")
        return
    
    print(f"   ✓ API connection successful")
    print(f"   {message}")
    
    # Summary
    print("\n" + "="*60)
    print("  ✅ All tests passed!")
    print("="*60)
    print(f"\n  Platform:    {platform_names.get(platform, platform)}")
    print(f"  Host:        {host}")
    print(f"  Instance ID: {instance_id}")
    print(f"  Auth Type:   {auth_type}")
    print("\n  You can now use this configuration for integration.\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        raise

# Made with Bob
