#!/usr/bin/env python3
"""
Test different Tipalti API method names
"""

import requests
import hmac
import hashlib
import time
import config


def test_different_methods():
    """Test different method names"""
    payer_name, master_key, is_sandbox = config.get_validated_config()
    base_url = "https://api.sandbox.tipalti.com/v14/PayeeFunctions.asmx"
    
    timestamp = str(int(time.time()))
    signature_string = f"{payer_name}{timestamp}"
    signature = hmac.new(
        master_key.encode('utf-8'),
        signature_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Different method names to test
    methods = [
        "GetPayeesList",
        "GetPayeesDataList", 
        "GetPayees",
        "GetAllPayees",
        "GetPayeeList",
        "GetPayeeDetails",
        "ListPayees",
        "RetrievePayees"
    ]
    
    for method in methods:
        print(f"\n🧪 Testing method: {method}")
        
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <{method} xmlns="http://Tipalti.org/">
      <payerName>{payer_name}</payerName>
      <timestamp>{timestamp}</timestamp>
      <key>{signature}</key>
    </{method}>
  </soap12:Body>
</soap12:Envelope>"""

        headers = {
            'Content-Type': f'application/soap+xml; charset=utf-8; action="http://Tipalti.org/{method}"'
        }
        
        try:
            response = requests.post(base_url, data=soap_body, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS with method: {method}")
                print("Response preview:", response.text[:300])
                return method
            else:
                print(f"❌ Status {response.status_code}")
                if "was not recognized" not in response.text:
                    print(f"📍 Different error (progress!): {response.text[:200]}")
                    
        except Exception as e:
            print(f"💥 Exception: {e}")
    
    print("\n❓ None of the tested methods worked.")
    print("💡 The issue might be:")
    print("   1. Invalid payer_name: 'your_payer_name' (placeholder)")
    print("   2. API requires different authentication")
    print("   3. Different API endpoint needed")
    
    return None


if __name__ == "__main__":
    print("🔬 Testing different Tipalti API method names...")
    result = test_different_methods() 