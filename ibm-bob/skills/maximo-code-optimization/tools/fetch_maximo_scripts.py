import requests
import json
import os
import sys

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Maximo configuration - Read from environment variables
MAXIMO_URL = os.getenv('MAXIMO_URL', '')
API_KEY = os.getenv('MAXIMO_API_KEY', '')

# Validate required environment variables
if not MAXIMO_URL:
    print("[ERROR] MAXIMO_URL environment variable is not set")
    print("Please set it using: export MAXIMO_URL='https://your-maximo-server.com'")
    sys.exit(1)

if not API_KEY:
    print("[ERROR] MAXIMO_API_KEY environment variable is not set")
    print("Please set it using: export MAXIMO_API_KEY='your-api-key-here'")
    sys.exit(1)

API_ENDPOINT = f"{MAXIMO_URL}/maximo/api/os/MXAPIAUTOSCRIPT"

# Directory structure
ORIGINAL_DIR = "maximo-scripts/original"
OPTIMIZED_DIR = "maximo-scripts/optimized"
REPORTS_DIR = "maximo-scripts/reports"

def create_directories():
    """Create necessary directories if they don't exist"""
    for directory in [ORIGINAL_DIR, OPTIMIZED_DIR, REPORTS_DIR]:
        os.makedirs(directory, exist_ok=True)
    print("[OK] Directory structure created")

def fetch_scripts():
    """Fetch automation scripts from Maximo API"""
    headers = {
        'apikey': API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Fetching scripts from: {API_ENDPOINT}")
        response = requests.get(API_ENDPOINT, headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print("[OK] Successfully fetched data from Maximo API")
        
        # Debug: Show response structure
        scripts_key = 'rdfs:member' if 'rdfs:member' in data else 'member'
        if scripts_key in data:
            print(f"Number of scripts found: {len(data[scripts_key])}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error fetching scripts: {e}")
        return None

def fetch_script_details(script_url):
    """Fetch detailed script information from individual script URL"""
    headers = {
        'apikey': API_KEY,
        'Content-Type': 'application/json',
        'properties': '*'  # Request all properties
    }
    
    try:
        # Fix URL to use uppercase MXAPIAUTOSCRIPT
        script_url = script_url.replace('/mxapiautoscript/', '/MXAPIAUTOSCRIPT/')
        
        # Add query parameter to get all fields
        full_url = f"{script_url}?lean=1&oslc.properties=*"
        response = requests.get(full_url, headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Debug: show available fields for first script
        if 'autoscript' in data:
            print(f"  Script: {data.get('autoscript', 'N/A')}")
            print(f"  Available fields: {list(data.keys())[:10]}")  # Show first 10 keys
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error fetching script details: {e}")
        return None

def save_scripts(data):
    """Save individual scripts to files"""
    # Handle both 'member' and 'rdfs:member' keys
    scripts_key = 'rdfs:member' if 'rdfs:member' in data else 'member'
    
    if not data or scripts_key not in data:
        print("[ERROR] No scripts found in API response")
        return 0
    
    script_refs = data[scripts_key]
    saved_count = 0
    
    print(f"\nFetching details for {len(script_refs)} scripts...")
    
    for idx, script_ref in enumerate(script_refs, 1):
        # Get the script URL from the reference
        script_url = script_ref.get('rdf:resource') or script_ref.get('href')
        
        if not script_url:
            print(f"[ERROR] No URL found for script reference {idx}")
            continue
        
        print(f"\n[{idx}/{len(script_refs)}] Fetching: {script_url}")
        
        # Fetch full script details
        script_data = fetch_script_details(script_url)
        
        if not script_data:
            continue
        
        # Extract script information
        script_name = script_data.get('autoscript', 'UNKNOWN')
        script_language = script_data.get('scriptlanguage', 'python').lower()
        script_source = script_data.get('source', '')
        
        if not script_source:
            print(f"[WARNING] No source code found for {script_name}")
            continue
        
        # Determine file extension
        extension = '.py' if script_language in ['python', 'jython'] else '.js'
        filename = f"{script_name}{extension}"
        filepath = os.path.join(ORIGINAL_DIR, filename)
        
        # Save the script
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(script_source)
            print(f"[OK] Saved: {filename} ({len(script_source)} bytes)")
            saved_count += 1
        except Exception as e:
            print(f"[ERROR] Error saving {filename}: {e}")
    
    return saved_count

def main():
    print("=" * 60)
    print("Maximo Automation Script Fetcher")
    print("=" * 60)
    
    # Create directory structure
    create_directories()
    
    # Fetch scripts from API
    data = fetch_scripts()
    
    if data:
        # Save scripts to files
        count = save_scripts(data)
        print("=" * 60)
        print(f"[OK] Successfully saved {count} scripts to {ORIGINAL_DIR}/")
        print("=" * 60)
    else:
        print("=" * 60)
        print("[ERROR] Failed to fetch scripts from Maximo API")
        print("=" * 60)

if __name__ == "__main__":
    main()

# Made with Bob
