#!/usr/bin/env python3
"""
Test simple Tipalti API method - GetPayeesList
Without idap parameter that might be causing issues
"""

import requests
import time
import hmac
import hashlib
import config

def test_get_payees_list():
    """Test GetPayeesList method without idap parameter"""
    try:
        # Load configuration
        payer_name, master_key, is_sandbox = config.get_validated_config()
        
        print("🧪 Testing GetPayeesList Method")
        print("=" * 50)
        print(f"📍 Payer Name: '{payer_name}'")
        print(f"🌐 Environment: {'Sandbox' if is_sandbox else 'Production'}")
        
        # Generate signature without idap
        timestamp = str(int(time.time()))
        signature_string = f"{payer_name}{timestamp}"  # Only payer name + timestamp
        signature = hmac.new(
            master_key.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        print(f"📝 Signature String: '{signature_string}'")
        print(f"🔏 Generated Signature: {signature}")
        
        # SOAP request for GetPayeesList
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <GetPayeesList xmlns="http://Tipalti.org/">
      <payerName>{payer_name}</payerName>
      <timestamp>{timestamp}</timestamp>
      <key>{signature}</key>
    </GetPayeesList>
  </soap12:Body>
</soap12:Envelope>"""

        # Headers for SOAP 1.2
        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8; action="http://Tipalti.org/GetPayeesList"'
        }

        # API endpoint
        url = f"https://api.{'sandbox.' if is_sandbox else ''}tipalti.com/v14/PayeeFunctions.asmx"
        
        print(f"📡 API URL: {url}")
        print(f"📤 SOAP Request:")
        print(f"Headers: {headers}")
        print(f"Body: {soap_body}")
        print()
        
        # Send request
        print("🌐 Sending request...")
        response = requests.post(url, data=soap_body, headers=headers, timeout=30)
        
        print(f"📥 Response received:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            print("✅ Success! Response body:")
            print(response.text)
            
            if "EncryptionKeyFailedValidation" in response.text:
                print("\n❌ Still getting EncryptionKeyFailedValidation")
                return False
            elif "error" not in response.text.lower():
                print("\n🎉 API call successful! No errors detected.")
                return True
            else:
                print(f"\n⚠️  API responded but with errors")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_get_payees_list()
    if success:
        print("\n🎉 GetPayeesList method works!")
    else:
        print("\n💥 GetPayeesList method failed") 