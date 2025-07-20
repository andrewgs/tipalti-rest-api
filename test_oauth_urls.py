#!/usr/bin/env python3
"""
Test different OAuth URL patterns for Tipalti REST API
"""

import requests
import json

# Test different OAuth URL patterns
OAUTH_URLS = [
    "https://api.sandbox.tipalti.com/oauth/token",
    "https://api.sandbox.tipalti.com/v1/oauth/token", 
    "https://api.sandbox.tipalti.com/oauth2/token",
    "https://api.sandbox.tipalti.com/v1/oauth2/token",
    "https://sandbox.tipalti.com/oauth/token",
    "https://sandbox.tipalti.com/v1/oauth/token",
    "https://sandbox.tipalti.com/oauth2/token",
    "https://sandbox-api.tipalti.com/oauth/token",
    "https://developer.tipalti.com/oauth/token"
]

def test_oauth_urls():
    """Test various OAuth URL patterns to find the working one"""
    
    print("🧪 Testing Tipalti OAuth URL Patterns")
    print("=" * 50)
    
    # Mock OAuth request data
    test_payload = {
        'grant_type': 'client_credentials',
        'client_id': 'test_client_id',
        'client_secret': 'test_client_secret'
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    for i, url in enumerate(OAUTH_URLS, 1):
        print(f"{i:2}. Testing: {url}")
        
        try:
            response = requests.post(url, data=test_payload, headers=headers, timeout=10)
            
            if response.status_code == 404:
                print(f"    ❌ 404 Not Found - URL doesn't exist")
            elif response.status_code == 400:
                print(f"    ✅ 400 Bad Request - URL exists! (expected with fake credentials)")
                print(f"    📝 Response: {response.text[:100]}...")
                return url  # Found a working endpoint
            elif response.status_code == 401:
                print(f"    ✅ 401 Unauthorized - URL exists! (expected with fake credentials)")
                print(f"    📝 Response: {response.text[:100]}...")
                return url  # Found a working endpoint
            else:
                print(f"    🤔 {response.status_code} - {response.text[:100]}...")
                
        except requests.exceptions.ConnectTimeout:
            print(f"    ⏰ Timeout - URL might exist but slow")
        except requests.exceptions.ConnectionError:
            print(f"    🚫 Connection Error - URL likely doesn't exist")
        except Exception as e:
            print(f"    💥 Error: {e}")
    
    print("\n❌ No working OAuth endpoint found")
    return None

def test_api_base_urls():
    """Test different base API URL patterns"""
    
    print("\n🌐 Testing Tipalti API Base URLs")
    print("=" * 50)
    
    BASE_URLS = [
        "https://api.sandbox.tipalti.com",
        "https://api.sandbox.tipalti.com/v1", 
        "https://sandbox.tipalti.com/api",
        "https://sandbox.tipalti.com/api/v1",
        "https://sandbox-api.tipalti.com",
        "https://developer.tipalti.com/api"
    ]
    
    for i, url in enumerate(BASE_URLS, 1):
        print(f"{i:2}. Testing: {url}")
        
        try:
            # Try to get API info or documentation
            response = requests.get(f"{url}/", timeout=5)
            
            if response.status_code == 404:
                print(f"    ❌ 404 Not Found")
            elif response.status_code in [200, 401, 403]:
                print(f"    ✅ {response.status_code} - API base exists!")
                print(f"    📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
            else:
                print(f"    🤔 {response.status_code}")
                
        except requests.exceptions.ConnectTimeout:
            print(f"    ⏰ Timeout")
        except requests.exceptions.ConnectionError:
            print(f"    🚫 Connection Error")
        except Exception as e:
            print(f"    💥 Error: {e}")

if __name__ == "__main__":
    working_oauth_url = test_oauth_urls()
    test_api_base_urls()
    
    if working_oauth_url:
        print(f"\n🎉 Found working OAuth URL: {working_oauth_url}")
        print("💡 Update your tipalti_rest_api.py with this URL!")
    else:
        print(f"\n💡 Try checking Tipalti documentation or contact support for correct OAuth endpoints")
        print("📖 https://documentation.tipalti.com/reference/quick-start") 