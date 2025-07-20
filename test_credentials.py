#!/usr/bin/env python3
"""
Test different credential combinations to find working setup
"""

import requests
import time
import hmac
import hashlib
import xml.etree.ElementTree as ET
from typing import List, Tuple


def test_payer_variations(base_payer: str, master_key: str, is_sandbox: bool = False) -> List[str]:
    """Test different payer name variations"""
    
    variations = [
        base_payer,                    # Uplify  
        base_payer.upper(),            # UPLIFY
        base_payer.lower(),            # uplify
        base_payer.capitalize(),       # Uplify
        base_payer.replace('i', 'I'),  # UplIfy
    ]
    
    working_variations = []
    soap_url = f"https://api.{'sandbox.' if is_sandbox else ''}tipalti.com/v14/PayeeFunctions.asmx"
    
    print(f"🧪 Testing payer name variations against {soap_url}")
    print("=" * 60)
    
    for i, payer_variant in enumerate(variations, 1):
        print(f"{i}. Testing payer: '{payer_variant}'")
        
        try:
            # Generate signature
            timestamp = str(int(time.time()))
            signature_string = f"{payer_variant}test{timestamp}"
            signature = hmac.new(
                master_key.encode('utf-8'),
                signature_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # SOAP request
            soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <GetPayeeDetails xmlns="http://Tipalti.org/">
      <payerName>{payer_variant}</payerName>
      <timestamp>{timestamp}</timestamp>
      <key>{signature}</key>
      <idap>test</idap>
    </GetPayeeDetails>
  </soap12:Body>
</soap12:Envelope>"""

            headers = {
                'Content-Type': 'application/soap+xml; charset=utf-8; action="http://Tipalti.org/GetPayeeDetails"'
            }

            response = requests.post(soap_url, data=soap_body, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Parse response
                root = ET.fromstring(response.text)
                result_element = root.find('.//{http://Tipalti.org/}GetPayeeDetailsResult')
                
                if result_element is not None:
                    error_msg = None
                    for child in result_element:
                        if 'errorMessage' in child.tag:
                            error_msg = child.text
                            break
                    
                    if error_msg:
                        if error_msg == "EncryptionKeyFailedValidation":
                            print(f"   ❌ Invalid credentials")
                        elif error_msg == "PayeeNotFound":
                            print(f"   ✅ VALID CREDENTIALS! (Payee 'test' not found)")
                            working_variations.append(payer_variant)
                        else:
                            print(f"   ⚠️  Unknown error: {error_msg}")
                    else:
                        print(f"   🎉 SUCCESS! Payee data returned")
                        working_variations.append(payer_variant)
                else:
                    print(f"   ❓ No result element")
            else:
                print(f"   💥 HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Error: {e}")
            
        time.sleep(0.5)  # Rate limiting
        
    return working_variations


def test_common_payee_ids(payer_name: str, master_key: str, is_sandbox: bool = False) -> List[str]:
    """Test common payee ID patterns"""
    
    # More realistic payee ID patterns
    test_ids = [
        # Email patterns
        "admin@uplify.com", "test@uplify.com", "demo@uplify.com",
        "support@uplify.com", "billing@uplify.com",
        
        # Username patterns  
        "admin", "administrator", "test", "testuser", "demo", "demouser",
        "user1", "user001", "payee1", "payee001",
        
        # ID patterns
        "1", "100", "1000", "000001", 
        "P001", "P100", "P1000", "PAY001",
        "U001", "U100", "USER001",
        
        # Company patterns
        "uplify", "uplify-admin", "uplify_test",
        
        # Common business names
        "john.doe", "jane.smith", "test.user",
        "contractor1", "vendor1", "supplier1"
    ]
    
    working_ids = []
    soap_url = f"https://api.{'sandbox.' if is_sandbox else ''}tipalti.com/v14/PayeeFunctions.asmx"
    
    print(f"\n🔍 Testing common payee IDs with payer: {payer_name}")
    print("=" * 60)
    
    for i, payee_id in enumerate(test_ids, 1):
        print(f"{i:2d}. Testing payee ID: '{payee_id}'", end="")
        
        try:
            # Generate signature
            timestamp = str(int(time.time()))
            signature_string = f"{payer_name}{payee_id}{timestamp}"
            signature = hmac.new(
                master_key.encode('utf-8'),
                signature_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # SOAP request
            soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
  <soap12:Body>
    <GetPayeeDetails xmlns="http://Tipalti.org/">
      <payerName>{payer_name}</payerName>
      <timestamp>{timestamp}</timestamp>
      <key>{signature}</key>
      <idap>{payee_id}</idap>
    </GetPayeeDetails>
  </soap12:Body>
</soap12:Envelope>"""

            headers = {
                'Content-Type': 'application/soap+xml; charset=utf-8; action="http://Tipalti.org/GetPayeeDetails"'
            }

            response = requests.post(soap_url, data=soap_body, headers=headers, timeout=10)
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                result_element = root.find('.//{http://Tipalti.org/}GetPayeeDetailsResult')
                
                if result_element is not None:
                    error_msg = None
                    payee_name = None
                    
                    for child in result_element:
                        tag = child.tag.replace('{http://Tipalti.org/}', '')
                        if tag == 'errorMessage':
                            error_msg = child.text
                        elif tag == 'd':  # Display name
                            payee_name = child.text
                    
                    if error_msg == "EncryptionKeyFailedValidation":
                        print(f" ❌ Invalid credentials")
                        break  # No point continuing with wrong credentials
                    elif error_msg == "PayeeNotFound":
                        print(f" ⚪ Not found")  
                    elif error_msg:
                        print(f" ⚠️  {error_msg}")
                    else:
                        print(f" 🎉 FOUND! Name: {payee_name}")
                        working_ids.append(payee_id)
                else:
                    print(f" ❓ No result")
            else:
                print(f" 💥 HTTP {response.status_code}")
                
        except Exception as e:
            print(f" 💥 Error: {str(e)[:30]}...")
            
        if i % 10 == 0:  # Progress indicator
            time.sleep(1)  # Rate limiting
        else:
            time.sleep(0.2)
            
    return working_ids


def main():
    """Test credentials and find working payee IDs"""
    
    print("🧪 Tipalti Credentials & Payee ID Tester")
    print("=" * 60)
    
    base_payer = "Uplify"
    master_key = "j0YPT6AkeKPUl3z8+glS5S0mt4wjU9G4EuglK0/q/X659Qih7ds/GCBseRmmCDbS"
    
    # Test both environments
    for env_name, is_sandbox in [("Production", False), ("Sandbox", True)]:
        print(f"\n🌐 Testing {env_name} Environment")
        print("=" * 60)
        
        # Test payer variations
        working_payers = test_payer_variations(base_payer, master_key, is_sandbox)
        
        if working_payers:
            print(f"\n✅ Working payer names in {env_name}: {working_payers}")
            
            # Test payee IDs with first working payer
            working_payer = working_payers[0]
            working_payees = test_common_payee_ids(working_payer, master_key, is_sandbox)
            
            if working_payees:
                print(f"\n🎉 Found {len(working_payees)} working payee IDs in {env_name}:")
                for payee in working_payees:
                    print(f"  • {payee}")
            else:
                print(f"\n❌ No working payee IDs found in {env_name}")
        else:
            print(f"\n❌ No working payer names found in {env_name}")
            
        print("\n" + "="*60)


if __name__ == "__main__":
    main() 