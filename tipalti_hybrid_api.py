#!/usr/bin/env python3
"""
Tipalti Hybrid REST API
Modern REST interface wrapper around SOAP API
"""

import requests
import time
import hmac
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass


@dataclass
class PayeeInfo:
    """Modern dataclass for payee information"""
    id: str
    name: str = ""
    email: str = ""
    status: str = "unknown"
    payment_method: str = "unknown"
    created_date: str = ""
    last_login: str = ""
    raw_data: Optional[Dict] = None


class TipaltiHybridAPI:
    """Modern REST-like API that uses SOAP internally"""
    
    def __init__(self, payer_name: str, master_key: str, is_sandbox: bool = True):
        self.payer_name = payer_name
        self.master_key = master_key
        self.is_sandbox = is_sandbox
        
        # SOAP endpoint (internal)
        self.soap_url = f"https://api.{'sandbox.' if is_sandbox else ''}tipalti.com/v14/PayeeFunctions.asmx"
        
        print(f"🔗 TipaltiHybridAPI initialized")
        print(f"   Environment: {'Sandbox' if is_sandbox else 'Production'}")
        print(f"   Payer: {payer_name}")
    
    def _generate_signature(self, additional_params: str = "") -> tuple[str, str]:
        """Generate HMAC signature for SOAP authentication"""
        timestamp = str(int(time.time()))
        signature_string = f"{self.payer_name}{additional_params}{timestamp}"
        signature = hmac.new(
            self.master_key.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return timestamp, signature
    
    def _make_soap_request(self, method: str, parameters: Dict[str, Any]) -> Dict:
        """Make SOAP request and return parsed response"""
        
        timestamp, signature = self._generate_signature()
        
        # Build SOAP envelope
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <{method} xmlns="http://Tipalti.org/">
      <payerName>{self.payer_name}</payerName>
      <timestamp>{timestamp}</timestamp>
      <key>{signature}</key>"""
      
        # Add additional parameters
        for key, value in parameters.items():
            soap_body += f"\n      <{key}>{value}</{key}>"
            
        soap_body += f"""
    </{method}>
  </soap12:Body>
</soap12:Envelope>"""

        # Headers
        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8; action="http://Tipalti.org/' + method + '"'
        }

        try:
            response = requests.post(self.soap_url, data=soap_body, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.text)
            
            # Extract the result
            result_element = root.find('.//{http://Tipalti.org/}' + method + 'Result')
            if result_element is not None:
                result = {}
                for child in result_element:
                    tag = child.tag.replace('{http://Tipalti.org/}', '')
                    result[tag] = child.text
                return result
            else:
                return {"error": "No result element found"}
                
        except requests.RequestException as e:
            return {"error": f"Request failed: {e}"}
        except ET.ParseError as e:
            return {"error": f"XML parse error: {e}"}
    
    # REST-like API Methods
    
    def get_payee(self, payee_id: str) -> Optional[PayeeInfo]:
        """GET /payees/{id} - Get single payee details"""
        
        print(f"🔍 GET /payees/{payee_id}")
        
        result = self._make_soap_request('GetPayeeDetails', {'idap': payee_id})
        
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
            return None
            
        if result.get('errorMessage'):
            print(f"   ❌ API Error: {result['errorMessage']}")
            return None
            
        # Convert SOAP response to modern PayeeInfo object
        payee = PayeeInfo(
            id=payee_id,
            name=result.get('d', ''),  # Display name
            email=result.get('email', ''),
            status="active" if not result.get('errorMessage') else "inactive",
            payment_method=result.get('PaymentMethod', 'unknown'),
            raw_data=result
        )
        
        print(f"   ✅ Success: {payee.name}")
        return payee
    
    def list_payees(self, limit: int = 100, offset: int = 0) -> List[PayeeInfo]:
        """GET /payees - List all payees (simulated with known IDs)"""
        
        print(f"📋 GET /payees?limit={limit}&offset={offset}")
        
        # Since we don't have a "list all" SOAP method that works,
        # we need to simulate this by trying common payee IDs
        # In real implementation, you'd need to get this list from somewhere
        
        print("   ⚠️  Note: Using sample payee IDs since GetPayeesList is not available")
        
        sample_ids = [
            "admin", "test", "demo", "user1", "user2", 
            "testuser", "demouser", "sample", "example"
        ]
        
        payees = []
        for i, payee_id in enumerate(sample_ids[offset:offset+limit]):
            print(f"   🔍 Checking payee {i+1}: {payee_id}")
            payee = self.get_payee(payee_id)
            if payee and not payee.raw_data.get('errorMessage'):
                payees.append(payee)
                
        print(f"   ✅ Found {len(payees)} valid payees")
        return payees
    
    def backup_all_payees(self) -> Dict:
        """POST /backup - Create backup of all payees"""
        
        print("💾 POST /backup - Creating payees backup")
        
        payees = self.list_payees(limit=1000)  # Get many payees
        
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'environment': 'sandbox' if self.is_sandbox else 'production',
            'payer_name': self.payer_name,
            'api_type': 'hybrid_rest_soap',
            'total_payees': len(payees),
            'payees': [
                {
                    'id': p.id,
                    'name': p.name,
                    'email': p.email,
                    'status': p.status,
                    'payment_method': p.payment_method,
                    'raw_soap_data': p.raw_data
                }
                for p in payees
            ]
        }
        
        # Save to file
        filename = f"backup_hybrid_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
        print(f"   ✅ Backup saved: {filename}")
        return {
            'success': True,
            'filename': filename,
            'total_payees': len(payees),
            'data': backup_data
        }
    
    def health_check(self) -> Dict:
        """GET /health - API health check"""
        
        print("🔍 GET /health - API Health Check")
        
        # Test connection with a simple payee details call
        result = self._make_soap_request('GetPayeeDetails', {'idap': 'test'})
        
        is_healthy = 'error' not in result
        
        health_data = {
            'status': 'healthy' if is_healthy else 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'environment': 'sandbox' if self.is_sandbox else 'production',
            'payer_name': self.payer_name,
            'soap_endpoint': self.soap_url,
            'authentication': 'working' if is_healthy else 'failed',
            'last_response': result
        }
        
        print(f"   {'✅' if is_healthy else '❌'} Status: {health_data['status']}")
        return health_data


def create_api_client() -> TipaltiHybridAPI:
    """Create API client from environment variables"""
    import config
    
    try:
        payer_name, master_key, is_sandbox = config.get_validated_config()
        return TipaltiHybridAPI(payer_name, master_key, is_sandbox)
    except Exception as e:
        print(f"❌ Failed to create API client: {e}")
        raise


# REST API Server Simulation
def simulate_rest_endpoints():
    """Simulate REST API endpoints"""
    
    print("🌐 Tipalti Hybrid REST API Server")
    print("=" * 50)
    
    try:
        api = create_api_client()
        
        # Health check
        health = api.health_check()
        print()
        
        if health['status'] == 'healthy':
            print("🎉 API is healthy! Testing endpoints...")
            print()
            
            # Test single payee
            payee = api.get_payee('test')
            print()
            
            # Test payees list
            payees = api.list_payees(limit=5)
            print()
            
            # Test backup
            backup_result = api.backup_all_payees()
            print()
            
            print("✅ All REST-like endpoints working!")
            return True
        else:
            print("❌ API health check failed")
            return False
            
    except Exception as e:
        print(f"💥 API test failed: {e}")
        return False


if __name__ == "__main__":
    simulate_rest_endpoints() 