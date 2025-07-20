#!/usr/bin/env python3
"""
Test different SOAPAction formats for Tipalti API
"""

import requests
import hmac
import hashlib
import time
import config


def test_soap_actions():
    """Test different SOAPAction formats"""
    payer_name, master_key, is_sandbox = config.get_validated_config()
    base_url = "https://api.sandbox.tipalti.com/v14/PayeeFunctions.asmx"
    
    timestamp = str(int(time.time()))
    signature_string = f"{payer_name}{timestamp}"
    signature = hmac.new(
        master_key.encode('utf-8'),
        signature_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
              xmlns:tip="http://Tipalti.org/">
  <soap:Header/>
  <soap:Body>
    <tip:GetPayeesList>
      <tip:payerName>{payer_name}</tip:payerName>
      <tip:timestamp>{timestamp}</tip:timestamp>
      <tip:key>{signature}</tip:key>
    </tip:GetPayeesList>
  </soap:Body>
</soap:Envelope>"""

    # Different SOAPAction formats to test
    soap_actions = [
        "",  # Empty
        "GetPayeesList",  # Just method name
        "http://tempuri.org/GetPayeesList",  # tempuri.org (common default)
        "urn:Tipalti/GetPayeesList",  # URN format
        "Tipalti.org/GetPayeesList",  # Without http
        "http://Tipalti.org/IPayeeFunctions/GetPayeesList",  # With interface
    ]
    
    for i, soap_action in enumerate(soap_actions, 1):
        print(f"\n🧪 Test {i}/{len(soap_actions)}: SOAPAction = '{soap_action}'")
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': f'"{soap_action}"' if soap_action else '""'
        }
        
        try:
            response = requests.post(base_url, data=soap_body, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS with SOAPAction: '{soap_action}'")
                print("Response preview:", response.text[:200])
                return True
            else:
                print(f"❌ Status {response.status_code}")
                if response.status_code != 500:
                    print("Different error - may be progress!")
                    print("Response:", response.text[:300])
                    
        except Exception as e:
            print(f"💥 Exception: {e}")
    
    return False


if __name__ == "__main__":
    print("🔬 Testing different SOAPAction formats...")
    success = test_soap_actions()
    
    if not success:
        print("\n❓ None of the common SOAPAction formats worked.")
        print("💡 This might be due to:")
        print("   1. Invalid payer_name (currently: 'your_payer_name')")
        print("   2. Invalid master_key")
        print("   3. API version or endpoint issues")
        print("   4. Different SOAP namespace required") 