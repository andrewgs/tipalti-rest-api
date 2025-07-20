#!/usr/bin/env python3
"""
Tipalti REST API Client
Using OAuth 2.0 Client Credentials Flow
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class TipaltiRestAPI:
    """Modern Tipalti REST API client with OAuth 2.0 authentication"""
    
    def __init__(self, client_id: str, client_secret: str, is_sandbox: bool = True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.is_sandbox = is_sandbox
        
        # Set API endpoints based on environment
        if is_sandbox:
            self.base_url = "https://api.sandbox.tipalti.com/v1"
            self.auth_url = "https://api.sandbox.tipalti.com/v1/oauth/token"
        else:
            self.base_url = "https://api.tipalti.com/v1"
            self.auth_url = "https://api.tipalti.com/v1/oauth/token"
        
        self.access_token = None
        self.token_expires_at = None
    
    def _get_access_token(self) -> str:
        """Get OAuth 2.0 access token using client credentials flow"""
        
        # Check if token is still valid
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at):
            return self.access_token
        
        # Request new access token
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(self.auth_url, data=payload, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            # Calculate token expiration (subtract 60 seconds for safety margin)
            expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            return self.access_token
            
        except requests.RequestException as e:
            print(f"Failed to get access token: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            raise
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """Make authenticated REST API request"""
        
        # Get valid access token
        token = self._get_access_token()
        
        # Prepare headers
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Full URL
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            raise
    
    def get_payees_list(self, limit: int = 100, offset: int = 0, status: str = None) -> List[Dict]:
        """Get list of all payees from Tipalti REST API"""
        
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if status:
            params['status'] = status
        
        try:
            response = self._make_request('GET', '/v1/payees', params=params)
            
            # Extract payees from response
            payees = response.get('data', [])
            
            # Handle pagination - get all payees
            all_payees = payees.copy()
            total_count = response.get('total_count', len(payees))
            
            while len(all_payees) < total_count and len(payees) == limit:
                offset += limit
                params['offset'] = offset
                
                response = self._make_request('GET', '/v1/payees', params=params)
                payees = response.get('data', [])
                all_payees.extend(payees)
            
            return all_payees
            
        except Exception as e:
            print(f"Failed to get payees list: {e}")
            return []
    
    def get_payee_details(self, payee_id: str) -> Optional[Dict]:
        """Get detailed information for a specific payee"""
        
        try:
            response = self._make_request('GET', f'/v1/payees/{payee_id}')
            return response.get('data')
        except Exception as e:
            print(f"Failed to get payee details for {payee_id}: {e}")
            return None
    
    def update_payee(self, payee_id: str, data: Dict) -> bool:
        """Update payee information"""
        
        try:
            response = self._make_request('PATCH', f'/v1/payees/{payee_id}', data=data)
            return response.get('success', False)
        except Exception as e:
            print(f"Failed to update payee {payee_id}: {e}")
            return False
    
    def deactivate_payee(self, payee_id: str) -> bool:
        """Deactivate a payee"""
        
        update_data = {
            'status': 'inactive'  # or whatever the correct status field is
        }
        
        return self.update_payee(payee_id, update_data)
    
    def get_payments_list(self, payee_id: str = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get list of payments, optionally filtered by payee"""
        
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if payee_id:
            params['payee_id'] = payee_id
        
        try:
            response = self._make_request('GET', '/v1/payments', params=params)
            return response.get('data', [])
        except Exception as e:
            print(f"Failed to get payments list: {e}")
            return []


# Test connection function
def test_connection():
    """Test REST API connection with current credentials"""
    import config_rest
    
    try:
        config_rest.validate_config()
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        
        print("🔗 Testing Tipalti REST API Connection...")
        print(f"🌐 Environment: {'Sandbox' if is_sandbox else 'Production'}")
        print(f"📱 Client ID: {client_id}")
        
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        
        # Test authentication
        print("🔐 Getting OAuth access token...")
        token = api._get_access_token()
        print(f"✅ Token obtained: {token[:20]}...")
        
        # Test payees list
        print("👥 Fetching payees list...")
        payees = api.get_payees_list(limit=5)  # Just get first 5 for testing
        print(f"📊 Found {len(payees)} payees")
        
        if payees:
            print("📋 First payee sample:")
            first_payee = payees[0]
            for key, value in list(first_payee.items())[:5]:  # Show first 5 fields
                print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


if __name__ == "__main__":
    test_connection() 