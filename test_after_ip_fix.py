#!/usr/bin/env python3
"""
Quick Test After IP Fix
Run this after adding IP to Tipalti whitelist
"""

import requests
import time
import hmac
import hashlib
import xml.etree.ElementTree as ET


def quick_payee_test():
    """Quick test with real payee IDs after IP fix"""
    
    print("🧪 Quick Test After IP Whitelist Fix")
    print("=" * 50)
    
    # Real payee data from user
    test_payees = [
        {"id": "37617", "name": "Diogo Martins da Silva", "email": "dms02031995dms@gmail.com"},
        {"id": "18827", "name": "leandro silva", "email": "trakinaboy85@gmail.com"}
    ]
    
    payer_name = "Uplify"
    master_key = "j0YPT6AkeKPUl3z8+glS5S0mt4wjU9G4EuglK0/q/X659Qih7ds/GCBseRmmCDbS"
    
    success_count = 0
    
    for payee in test_payees:
        payee_id = payee["id"]
        expected_name = payee["name"]
        
        print(f"🔍 Testing Payee {payee_id} ({expected_name})")
        
        try:
            timestamp = str(int(time.time()))
            signature_string = f"{payer_name}{payee_id}{timestamp}"
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

            response = requests.post(
                "https://api.tipalti.com/v14/PayeeFunctions.asmx", 
                data=soap_body, 
                headers=headers, 
                timeout=15
            )
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                result_element = root.find('.//{http://Tipalti.org/}GetPayeeDetailsResult')
                
                if result_element is not None:
                    result = {}
                    for child in result_element:
                        tag = child.tag.replace('{http://Tipalti.org/}', '')
                        result[tag] = child.text
                    
                    error_msg = result.get('errorMessage')
                    
                    if error_msg == "InvalidPayerIpAddress":
                        print(f"   ❌ Still blocked - IP not whitelisted yet")
                        print(f"   💡 Wait 5-10 more minutes and try again")
                        break
                    elif error_msg:
                        print(f"   ⚠️  API Error: {error_msg}")
                    else:
                        # SUCCESS!
                        actual_name = result.get('d', 'N/A')
                        actual_email = result.get('e', 'N/A')
                        
                        print(f"   🎉 SUCCESS!")
                        print(f"   📧 Name: {actual_name}")
                        print(f"   📧 Email: {actual_email}")
                        success_count += 1
            else:
                print(f"   💥 HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Exception: {e}")
            
        time.sleep(1)
    
    print("\n" + "=" * 50)
    
    if success_count > 0:
        print(f"🎉 SUCCESS! IP whitelist is working!")
        print(f"✅ Found {success_count} payees successfully")
        print(f"🚀 Ready to backup all 3,857 payees!")
        print()
        print("🔥 Run full backup now:")
        print("   python backup_production_final.py")
        return True
    else:
        print(f"❌ IP still blocked or other issues")
        print(f"💡 Try again in a few minutes")
        print(f"🔄 Or contact Tipalti support")
        return False


if __name__ == "__main__":
    quick_payee_test() 