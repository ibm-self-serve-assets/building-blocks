"""
IBM Concert API Connection Test Script
Tests API connectivity and displays sample data structures
"""

import logging
from config import setup_logging, validate_config
from api.concert_api import ConcertAPIClient

# Setup logging
logger = setup_logging()

def test_api_connection():
    """Test IBM Concert API connection and display sample data"""
    
    print("=" * 80)
    print("IBM Concert API Connection Test")
    print("=" * 80)
    print()
    
    # Validate configuration
    try:
        validate_config()
        print("✓ Configuration validated successfully")
        print()
    except ValueError as e:
        print(f"✗ Configuration validation failed: {str(e)}")
        print()
        print("Please check your .env file and ensure all required variables are set:")
        print("  - CONCERT_BASE_URL")
        print("  - C_API_KEY")
        print("  - INSTANCE_ID")
        return False
    
    # Initialize API client
    try:
        client = ConcertAPIClient()
        print("✓ API client initialized")
        print()
    except Exception as e:
        print(f"✗ Failed to initialize API client: {str(e)}")
        return False
    
    # Test CVE endpoint
    print("-" * 80)
    print("Testing CVE Endpoint")
    print("-" * 80)
    try:
        cves = client.get_cves(limit=1)
        if cves:
            print(f"✓ Successfully retrieved {len(cves)} CVE(s)")
            print(f"  Sample CVE structure: {list(cves[0].keys())}")
            print(f"  Sample CVE ID: {cves[0].get('cve', 'N/A')}")
            print(f"  Sample Risk Score: {cves[0].get('highest_finding_risk_score', 'N/A')}")
        else:
            print("⚠ No CVEs found (this may be normal if no CVEs exist)")
        print()
    except Exception as e:
        print(f"✗ CVE endpoint test failed: {str(e)}")
        print()
    
    # Test Applications endpoint
    print("-" * 80)
    print("Testing Applications Endpoint")
    print("-" * 80)
    try:
        apps = client.get_applications(limit=1)
        if apps:
            print(f"✓ Successfully retrieved {len(apps)} application(s)")
            print(f"  Sample application structure: {list(apps[0].keys())}")
            print(f"  Sample application name: {apps[0].get('name', 'N/A')}")
            print(f"  Sample status: {apps[0].get('resilience_status', 'N/A')}")
        else:
            print("⚠ No applications found (this may be normal if no applications exist)")
        print()
    except Exception as e:
        print(f"✗ Applications endpoint test failed: {str(e)}")
        print()
    
    # Test Certificates endpoint
    print("-" * 80)
    print("Testing Certificates Endpoint")
    print("-" * 80)
    try:
        certs = client.get_certificates(limit=1)
        if certs:
            print(f"✓ Successfully retrieved {len(certs)} certificate(s)")
            print(f"  Sample certificate structure: {list(certs[0].keys())}")
            print(f"  Sample certificate ID: {certs[0].get('id', 'N/A')}")
            print(f"  Sample status: {certs[0].get('status', 'N/A')}")
        else:
            print("⚠ No certificates found (this may be normal if no certificates exist)")
        print()
    except Exception as e:
        print(f"✗ Certificates endpoint test failed: {str(e)}")
        print()
    
    print("=" * 80)
    print("API Connection Test Complete")
    print("=" * 80)
    print()
    print("If all tests passed, you can now run the dashboard:")
    print("  python app.py")
    print()
    print("The dashboard will be available at: http://127.0.0.1:8050")
    print()
    
    return True


if __name__ == "__main__":
    test_api_connection()

# Made with Bob
