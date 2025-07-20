#!/usr/bin/env python3
"""
Find real payee IDs in Tipalti Production
Using correct credentials: Uplify + Production
"""

import requests
import time
import hmac
import hashlib
import xml.etree.ElementTree as ET
import string
import itertools


def test_payee_id(payer_name: str, master_key: str, payee_id: str, is_sandbox: bool = False) -> dict:
    """Test a single payee ID and return detailed result"""
    
    soap_url = f"https://api.{'sandbox.' if is_sandbox else ''}tipalti.com/v14/PayeeFunctions.asmx"
    
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
                result = {}
                for child in result_element:
                    tag = child.tag.replace('{http://Tipalti.org/}', '')
                    result[tag] = child.text
                
                return {
                    'payee_id': payee_id,
                    'status': 'found' if not result.get('errorMessage') else 'error',
                    'error': result.get('errorMessage'),
                    'name': result.get('d'),  # Display name
                    'email': result.get('e'),  # Email
                    'data': result
                }
            else:
                return {'payee_id': payee_id, 'status': 'no_result', 'error': 'No result element'}
        else:
            return {'payee_id': payee_id, 'status': 'http_error', 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        return {'payee_id': payee_id, 'status': 'exception', 'error': str(e)}


def comprehensive_payee_search():
    """Comprehensive search for real payee IDs"""
    
    print("🔍 Comprehensive Payee ID Search - Uplify Production")
    print("=" * 70)
    
    payer_name = "Uplify"
    master_key = "j0YPT6AkeKPUl3z8+glS5S0mt4wjU9G4EuglK0/q/X659Qih7ds/GCBseRmmCDbS"
    is_sandbox = False
    
    found_payees = []
    
    # 1. Email patterns for Uplify
    print("\n📧 Testing email patterns...")
    email_patterns = [
        # Uplify domain
        f"{name}@uplify.com" for name in [
            "admin", "administrator", "support", "billing", "finance", "accounting",
            "test", "demo", "help", "contact", "info", "sales", "team",
            "john", "jane", "user", "payee", "vendor", "contractor"
        ]
    ] + [
        # Common domains
        f"{name}@{domain}" for name in ["admin", "test", "demo", "uplify"] 
        for domain in ["gmail.com", "outlook.com", "yahoo.com"]
    ]
    
    for i, email in enumerate(email_patterns[:20], 1):  # Test first 20
        print(f"{i:2d}. {email:<30}", end=" ")
        result = test_payee_id(payer_name, master_key, email, is_sandbox)
        
        if result['status'] == 'found':
            print(f"🎉 FOUND! {result['name']}")
            found_payees.append(result)
        elif result['error'] == 'PayeeUnknown':
            print("⚪ Not found")
        elif result['error'] == 'EncryptionKeyFailedValidation':
            print("❌ Wrong credentials - stopping")
            break
        else:
            print(f"⚠️  {result['error']}")
            
        if i % 5 == 0:
            time.sleep(1)  # Rate limiting
        else:
            time.sleep(0.3)
    
    # 2. Sequential IDs
    print(f"\n🔢 Testing sequential numeric IDs...")
    for i in [1, 2, 3, 5, 10, 100, 1000, 1001, 1002, 2000]:
        print(f"ID {i:<10}", end=" ")
        result = test_payee_id(payer_name, master_key, str(i), is_sandbox)
        
        if result['status'] == 'found':
            print(f"🎉 FOUND! {result['name']}")
            found_payees.append(result)
        elif result['error'] == 'PayeeUnknown':
            print("⚪ Not found")
        else:
            print(f"⚠️  {result['error']}")
        time.sleep(0.3)
    
    # 3. Common usernames
    print(f"\n👤 Testing common usernames...")
    usernames = [
        "admin", "administrator", "root", "user", "test", "demo",
        "uplify", "uplifytech", "uplify_admin", "uplify-test",
        "john.doe", "jane.smith", "user001", "payee001",
        "contractor", "vendor", "supplier", "client"
    ]
    
    for i, username in enumerate(usernames, 1):
        print(f"{i:2d}. {username:<20}", end=" ")
        result = test_payee_id(payer_name, master_key, username, is_sandbox)
        
        if result['status'] == 'found':
            print(f"🎉 FOUND! {result['name']}")
            found_payees.append(result)
        elif result['error'] == 'PayeeUnknown':
            print("⚪ Not found")
        else:
            print(f"⚠️  {result['error']}")
        time.sleep(0.3)
    
    # 4. UUID patterns (if they use UUIDs)
    print(f"\n🆔 Testing UUID-like patterns...")
    uuid_patterns = [
        "00000000-0000-0000-0000-000000000001",
        "11111111-1111-1111-1111-111111111111"
    ] + [f"uplify-{i}" for i in range(1, 6)]
    
    for pattern in uuid_patterns:
        print(f"UUID {pattern:<40}", end=" ")
        result = test_payee_id(payer_name, master_key, pattern, is_sandbox)
        
        if result['status'] == 'found':
            print(f"🎉 FOUND! {result['name']}")
            found_payees.append(result)
        elif result['error'] == 'PayeeUnknown':
            print("⚪ Not found")
        else:
            print(f"⚠️  {result['error']}")
        time.sleep(0.3)
    
    # Results
    print(f"\n" + "="*70)
    print(f"📊 SEARCH RESULTS")
    print(f"="*70)
    
    if found_payees:
        print(f"🎉 Found {len(found_payees)} real payees:")
        for payee in found_payees:
            print(f"  • ID: {payee['payee_id']}")
            print(f"    Name: {payee['name']}")
            print(f"    Email: {payee['email']}")
            print()
        
        return found_payees
    else:
        print("❌ No payees found")
        print("\n💡 Suggestions:")
        print("  1. Contact Uplify team for real payee IDs")
        print("  2. Check Tipalti dashboard for payee list")
        print("  3. Try GetPayeesList SOAP method (if available)")
        return []


if __name__ == "__main__":
    comprehensive_payee_search() 