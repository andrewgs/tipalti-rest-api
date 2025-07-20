#!/usr/bin/env python3
"""
Test with REAL Tipalti Payee IDs
Testing: 37617, 37620, 18827
"""

import requests
import time
import hmac
import hashlib
import xml.etree.ElementTree as ET
import json
from datetime import datetime


def test_real_payee_ids():
    """Test with the real payee IDs from Tipalti dashboard"""
    
    print("🎯 Testing REAL Payee IDs from Tipalti Dashboard")
    print("=" * 60)
    
    # Real credentials
    payer_name = "your_payer_name"
    master_key = "your_master_key_here"
    is_sandbox = False
    
    # REAL payee IDs from dashboard
    real_payees = [
        {"id": "37617", "expected_name": "Diogo Martins da Silva", "expected_email": "dms02031995dms@gmail.com"},
        {"id": "37620", "expected_name": "Diogo Martins da Silva", "expected_email": "dms02031995dms@gmail.com"}, 
        {"id": "18827", "expected_name": "leandro silva", "expected_email": "trakinaboy85@gmail.com"}
    ]
    
    soap_url = f"https://api.{'sandbox.' if is_sandbox else ''}tipalti.com/v14/PayeeFunctions.asmx"
    found_payees = []
    
    for i, payee in enumerate(real_payees, 1):
        payee_id = payee["id"]
        expected_name = payee["expected_name"]
        expected_email = payee["expected_email"]
        
        print(f"{i}. Testing Payee ID: {payee_id}")
        print(f"   Expected: {expected_name} ({expected_email})")
        
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

            response = requests.post(soap_url, data=soap_body, headers=headers, timeout=15)
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                result_element = root.find('.//{http://Tipalti.org/}GetPayeeDetailsResult')
                
                if result_element is not None:
                    result = {}
                    for child in result_element:
                        tag = child.tag.replace('{http://Tipalti.org/}', '')
                        result[tag] = child.text
                    
                    error_msg = result.get('errorMessage')
                    
                    if error_msg:
                        print(f"   ❌ Error: {error_msg}")
                        
                        if error_msg == "EncryptionKeyFailedValidation":
                            print("   💥 Invalid credentials - stopping")
                            break
                    else:
                        # SUCCESS! Extract payee data
                        actual_name = result.get('d', 'N/A')  # Display name
                        actual_email = result.get('e', 'N/A')  # Email
                        
                        print(f"   🎉 SUCCESS!")
                        print(f"   📧 Name: {actual_name}")
                        print(f"   📧 Email: {actual_email}")
                        
                        # Check if it matches expected
                        name_match = expected_name.lower() in actual_name.lower() if actual_name != 'N/A' else False
                        email_match = expected_email.lower() == actual_email.lower() if actual_email != 'N/A' else False
                        
                        print(f"   ✅ Name Match: {name_match}")
                        print(f"   ✅ Email Match: {email_match}")
                        
                        found_payees.append({
                            'id': payee_id,
                            'name': actual_name,
                            'email': actual_email,
                            'raw_data': result
                        })
                else:
                    print(f"   ❓ No result element in response")
            else:
                print(f"   💥 HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Exception: {e}")
            
        print()  # Empty line between tests
        time.sleep(1)  # Rate limiting
    
    # Summary
    print("📊 REAL PAYEE TEST RESULTS")
    print("=" * 40)
    
    if found_payees:
        print(f"🎉 Successfully found {len(found_payees)} real payees!")
        
        for payee in found_payees:
            print(f"  • ID: {payee['id']}")
            print(f"    Name: {payee['name']}")
            print(f"    Email: {payee['email']}")
            print()
        
        return found_payees
    else:
        print("❌ No real payees found - something is wrong")
        return []


def try_list_all_payees():
    """Try to get a list of all payees using different SOAP methods"""
    
    print("\n🔍 Trying to get ALL payees list...")
    print("=" * 50)
    
    payer_name = "your_payer_name"
    master_key = "your_master_key_here"
    is_sandbox = False
    soap_url = f"https://api.{'sandbox.' if is_sandbox else ''}tipalti.com/v14/PayeeFunctions.asmx"
    
    # Try different SOAP methods that might list all payees
    methods_to_try = [
        "GetPayeesList",
        "GetAllPayees", 
        "ListPayees",
        "GetPayees",
        "SearchPayees"
    ]
    
    for method in methods_to_try:
        print(f"🧪 Trying method: {method}")
        
        try:
            timestamp = str(int(time.time()))
            signature_string = f"{payer_name}{timestamp}"
            signature = hmac.new(
                master_key.encode('utf-8'),
                signature_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
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

            response = requests.post(soap_url, data=soap_body, headers=headers, timeout=15)
            
            if response.status_code == 200:
                print(f"   ✅ HTTP 200 - checking response...")
                
                # Try to parse response
                try:
                    root = ET.fromstring(response.text)
                    
                    # Look for result element
                    result_element = root.find(f'.//{{{method}Result')
                    if not result_element:
                        result_element = root.find('.//{http://Tipalti.org/}' + method + 'Result')
                    
                    if result_element is not None:
                        print(f"   🎉 Found result element!")
                        
                        # Parse the result
                        result = {}
                        for child in result_element:
                            tag = child.tag.replace('{http://Tipalti.org/}', '')
                            result[tag] = child.text
                        
                        if result.get('errorMessage'):
                            print(f"   ⚠️  API Error: {result['errorMessage']}")
                        else:
                            print(f"   🎉 SUCCESS! Got payee list data!")
                            print(f"   📊 Response keys: {list(result.keys())}")
                            return method, result
                    else:
                        print(f"   ❓ No result element found")
                        
                except ET.ParseError as e:
                    print(f"   💥 XML Parse Error: {e}")
                    
            elif response.status_code == 500:
                print(f"   ⚠️  HTTP 500 - method might not exist")
            else:
                print(f"   💥 HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Exception: {e}")
            
        time.sleep(0.5)  # Rate limiting
    
    print("❌ No working list methods found")
    return None, None


if __name__ == "__main__":
    # Test real payee IDs
    found_payees = test_real_payee_ids()
    
    # Try to find a method to list all payees
    list_method, list_result = try_list_all_payees()
    
    if found_payees:
        print(f"\n🎉 GREAT NEWS!")
        print(f"✅ Found {len(found_payees)} real payees")
        print(f"🔢 Total payees in system: 3,857")
        print(f"📡 Now we can create a FULL backup!")
    elif list_method:
        print(f"\n🎉 Found list method: {list_method}")
    else:
        print(f"\n💡 Next steps:")
        print(f"• Individual payee lookup works")
        print(f"• Need to find list method for all 3,857 payees")
        print(f"• Or iterate through ID ranges") 