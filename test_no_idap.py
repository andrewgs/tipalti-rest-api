#!/usr/bin/env python3
"""
Test GetPayeeDetails without idap parameter
Sometimes the idap parameter causes signature validation issues
"""

import requests
import time
import hmac
import hashlib
import config

def test_without_idap():
    """Test GetPayeeDetails method without idap parameter"""
    try:
        # Load configuration
        payer_name, master_key, is_sandbox = config.get_validated_config()
        
        print("🧪 Testing GetPayeeDetails WITHOUT idap parameter")
        print("=" * 60)
        print(f"📍 Payer Name: '{payer_name}'")
        print(f"🌐 Environment: {'Sandbox' if is_sandbox else 'Production'}")
        
        # Generate simple signature: payer + timestamp only
        timestamp = str(int(time.time()))
        signature_string = f"{payer_name}{timestamp}"
        signature = hmac.new(
            master_key.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        print(f"📝 Signature String: '{signature_string}'")
        print(f"🔏 Generated Signature: {signature}")
        
        # SOAP request WITHOUT idap parameter
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <GetPayeeDetails xmlns="http://Tipalti.org/">
      <payerName>{payer_name}</payerName>
      <timestamp>{timestamp}</timestamp>
      <key>{signature}</key>
    </GetPayeeDetails>
  </soap12:Body>
</soap12:Envelope>"""

        # Headers for SOAP 1.2
        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8; action="http://Tipalti.org/GetPayeeDetails"'
        }

        # API endpoint
        url = f"https://api.{'sandbox.' if is_sandbox else ''}tipalti.com/v14/PayeeFunctions.asmx"
        
        print(f"📡 API URL: {url}")
        print()
        print("📤 SOAP Request (without idap):")
        print("Headers:", headers)
        print("Body preview:")
        print(soap_body[:500] + "...")
        print()
        
        # Send request
        print("🌐 Sending request...")
        response = requests.post(url, data=soap_body, headers=headers, timeout=30)
        
        print(f"📥 Response received:")
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            response_text = response.text
            print("✅ HTTP 200! Response body:")
            print(response_text)
            
            if "EncryptionKeyFailedValidation" in response_text:
                print("\n❌ Still getting EncryptionKeyFailedValidation")
                print("💡 This suggests the Master Key or Payer Name is incorrect")
                return False
            elif "error" not in response_text.lower() or "success" in response_text.lower():
                print("\n🎉 SUCCESS! No encryption validation errors!")
                return True
            else:
                print(f"\n⚠️  Got a different error:")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔬 Testing Tipalti API without idap parameter")
    print("This helps identify if idap is causing signature validation issues")
    print()
    
    success = test_without_idap()
    if success:
        print("\n🎉 Test passed! Credentials are working!")
        print("🚀 You can now run: python backup_users.py")
    else:
        print("\n💥 Test failed - credentials still invalid")
        print("📋 Double-check Tipalti dashboard settings") 