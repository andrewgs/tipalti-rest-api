#!/usr/bin/env python3
"""
Debug script to test Tipalti API connection
"""

import requests
import hmac
import hashlib
import time
import xml.etree.ElementTree as ET
from datetime import datetime
import config


def debug_api_call():
    """Debug API call with detailed logging"""
    try:
        # Get configuration
        payer_name, master_key, is_sandbox = config.get_validated_config()
        
        print("🔍 DEBUG: Tipalti API Connection Test")
        print("=" * 50)
        print(f"📍 Payer Name: '{payer_name}'")
        print(f"🔑 Master Key: '{master_key[:20]}...' (length: {len(master_key)})")
        print(f"🌐 Sandbox Mode: {is_sandbox}")
        print(f"📡 API URL: {'https://api.sandbox.tipalti.com/v14/PayeeFunctions.asmx' if is_sandbox else 'https://api.tipalti.com/v14/PayeeFunctions.asmx'}")
        print()
        
        # Generate signature
        print("🔐 Generating HMAC signature...")
        timestamp = str(int(time.time()))
        idap_param = "test_user"
        signature_string = f"{payer_name}{timestamp}"  # Simple signature without idap
        print(f"📝 Signature String: '{signature_string}'")
        
        signature = hmac.new(
            master_key.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        print(f"🔏 Generated Signature: {signature}")
        print(f"⏰ Timestamp: {timestamp}")
        print()
        
        # Prepare SOAP request
        base_url = "https://api.sandbox.tipalti.com/v14/PayeeFunctions.asmx" if is_sandbox else "https://api.tipalti.com/v14/PayeeFunctions.asmx"
        
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <GetPayeeDetails xmlns="http://Tipalti.org/">
      <payerName>{payer_name}</payerName>
      <timestamp>{timestamp}</timestamp>
      <key>{signature}</key>
      <idap>{idap_param}</idap>
    </GetPayeeDetails>
  </soap12:Body>
</soap12:Envelope>"""
        
        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8; action="http://Tipalti.org/GetPayeeDetails"'
        }
        
        print("📤 SOAP Request:")
        print("Headers:", headers)
        print("Body:", soap_body)
        print()
        
        print("🌐 Sending request...")
        response = requests.post(base_url, data=soap_body, headers=headers)
        
        print("📥 Response received:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            print("✅ Success! Response body:")
            print(response.text[:1000] + "..." if len(response.text) > 1000 else response.text)
        else:
            print(f"❌ Error {response.status_code}: {response.reason}")
            print("Response body:")
            print(response.text[:2000] + "..." if len(response.text) > 2000 else response.text)
            
            # Try to parse error details
            if 'xml' in response.headers.get('content-type', '').lower():
                try:
                    root = ET.fromstring(response.text)
                    print("\n🔍 Parsed XML Error Details:")
                    for elem in root.iter():
                        if elem.text and elem.text.strip():
                            print(f"  {elem.tag}: {elem.text}")
                except Exception as parse_error:
                    print(f"Could not parse XML: {parse_error}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"💥 Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print(f"🚀 Starting API Debug - {datetime.now()}")
    debug_api_call() 