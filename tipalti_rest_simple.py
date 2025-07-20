#!/usr/bin/env python3
"""
Simple Tipalti REST API Client
Try different authentication methods and endpoints
"""

import requests
import json
from typing import Dict, List, Optional
import config_rest


class TipaltiSimpleRestAPI:
    """Simple REST API client with multiple authentication attempts"""
    
    def __init__(self, client_id: str, client_secret: str, is_sandbox: bool = True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.is_sandbox = is_sandbox
        
        # Try different base URLs
        self.base_urls = [
            f"https://api.{'sandbox.' if is_sandbox else ''}tipalti.com",
            f"https://api.{'sandbox.' if is_sandbox else ''}tipalti.com/v1",
            f"https://api.{'sandbox.' if is_sandbox else ''}tipalti.com/api/v1",
            f"https://{'sandbox.' if is_sandbox else ''}tipalti.com/api",
        ]
        
    def test_endpoints(self):
        """Test different API endpoints to find working ones"""
        print("🌐 Testing Tipalti REST API Endpoints")
        print("=" * 50)
        
        for i, base_url in enumerate(self.base_urls, 1):
            print(f"\n{i}. Testing base URL: {base_url}")
            
            # Test basic API info endpoint
            try:
                response = requests.get(f"{base_url}/", timeout=10)
                print(f"   GET /: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ Base API available!")
                    print(f"   Content-Type: {response.headers.get('content-type')}")
                    if len(response.text) < 200:
                        print(f"   Content preview: {response.text[:100]}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            # Test common REST endpoints
            endpoints_to_test = [
                "/payees",
                "/v1/payees", 
                "/api/payees",
                "/users",
                "/v1/users",
                "/payments",
                "/v1/payments"
            ]
            
            for endpoint in endpoints_to_test:
                try:
                    # Try with Bearer token
                    headers = {
                        'Authorization': f'Bearer {self.client_secret}',
                        'Content-Type': 'application/json'
                    }
                    
                    response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                    
                    if response.status_code != 404:
                        print(f"   GET {endpoint}: {response.status_code} (Bearer)")
                        if response.status_code == 401:
                            print(f"      💡 Endpoint exists but needs different auth")
                        elif response.status_code == 200:
                            print(f"      🎉 Success! Working endpoint found!")
                            return base_url, endpoint
                            
                except:
                    pass  # Skip connection errors
                    
                try:
                    # Try with Basic Auth
                    response = requests.get(
                        f"{base_url}{endpoint}", 
                        auth=(self.client_id, self.client_secret),
                        timeout=5
                    )
                    
                    if response.status_code != 404:
                        print(f"   GET {endpoint}: {response.status_code} (Basic)")
                        if response.status_code == 401:
                            print(f"      💡 Endpoint exists but needs different auth")
                        elif response.status_code == 200:
                            print(f"      🎉 Success! Working endpoint found!")
                            return base_url, endpoint
                            
                except:
                    pass  # Skip connection errors
                    
                try:
                    # Try with API Key header
                    headers = {
                        'X-API-Key': self.client_secret,
                        'Content-Type': 'application/json'
                    }
                    
                    response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                    
                    if response.status_code != 404:
                        print(f"   GET {endpoint}: {response.status_code} (API-Key)")
                        if response.status_code == 401:
                            print(f"      💡 Endpoint exists but needs different auth")
                        elif response.status_code == 200:
                            print(f"      🎉 Success! Working endpoint found!")
                            return base_url, endpoint
                            
                except:
                    pass  # Skip connection errors
        
        print(f"\n❌ No working REST endpoints found")
        return None, None
    
    def test_webhooks_or_graphql(self):
        """Test for webhooks or GraphQL endpoints"""
        print(f"\n🔍 Testing alternative API patterns...")
        
        base_url = f"https://api.{'sandbox.' if self.is_sandbox else ''}tipalti.com"
        
        # Test GraphQL
        try:
            graphql_payload = {
                "query": "{ __schema { types { name } } }"
            }
            
            response = requests.post(
                f"{base_url}/graphql",
                json=graphql_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code != 404:
                print(f"   GraphQL /graphql: {response.status_code}")
                
        except:
            pass
            
        # Test webhooks endpoint
        try:
            response = requests.get(f"{base_url}/webhooks", timeout=5)
            if response.status_code != 404:
                print(f"   Webhooks /webhooks: {response.status_code}")
        except:
            pass


def test_rest_api():
    """Test REST API with different approaches"""
    try:
        config_rest.validate_config()
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        
        print("🔄 Tipalti REST API Testing")
        print("=" * 50)
        print(f"🔑 Client ID: {client_id}")
        print(f"🌐 Environment: {'Sandbox' if is_sandbox else 'Production'}")
        
        api = TipaltiSimpleRestAPI(client_id, client_secret, is_sandbox)
        
        # Test endpoints
        working_base, working_endpoint = api.test_endpoints()
        
        if working_base and working_endpoint:
            print(f"\n🎉 Found working endpoint!")
            print(f"   Base URL: {working_base}")
            print(f"   Endpoint: {working_endpoint}")
            return True
        else:
            # Try alternative patterns
            api.test_webhooks_or_graphql()
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing Tipalti REST API with different approaches")
    print("📡 This will try various endpoints and authentication methods")
    print()
    
    success = test_rest_api()
    
    if success:
        print(f"\n✅ REST API endpoint found!")
    else:
        print(f"\n💡 No public REST endpoints available")
        print(f"📞 You may need to contact Tipalti support for REST API access")
        print(f"🔗 Or use the SOAP API which we know works") 