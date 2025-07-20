#!/usr/bin/env python3
"""
Comprehensive IP Whitelist Troubleshooting
Tests different scenarios and provides detailed diagnostics
"""

import requests
import time
import hmac
import hashlib
import xml.etree.ElementTree as ET
import json
from datetime import datetime


def test_basic_connectivity():
    """Test basic internet and Tipalti connectivity"""
    
    print("🌐 Testing Basic Connectivity")
    print("-" * 40)
    
    # Test internet
    try:
        response = requests.get('https://google.com', timeout=5)
        print("✅ Internet connection: Working")
    except:
        print("❌ Internet connection: Failed")
        return False
    
    # Test Tipalti endpoint
    try:
        response = requests.get('https://api.tipalti.com', timeout=10)
        print(f"✅ Tipalti endpoint: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Tipalti endpoint: {e}")
        return False
    
    return True


def test_different_endpoints():
    """Test different Tipalti API endpoints"""
    
    print("\n🔗 Testing Different API Endpoints")
    print("-" * 40)
    
    endpoints = [
        "https://api.tipalti.com/v14/PayeeFunctions.asmx",
        "https://api.tipalti.com/v13/PayeeFunctions.asmx", 
        "https://api.tipalti.com/PayeeFunctions.asmx",
        "https://tipalti.com/api/v14/PayeeFunctions.asmx"
    ]
    
    payer_name = "Uplify"
    master_key = "j0YPT6AkeKPUl3z8+glS5S0mt4wjU9G4EuglK0/q/X659Qih7ds/GCBseRmmCDbS"
    test_payee_id = "37617"
    
    for i, endpoint in enumerate(endpoints, 1):
        print(f"{i}. Testing: {endpoint}")
        
        try:
            timestamp = str(int(time.time()))
            signature_string = f"{payer_name}{test_payee_id}{timestamp}"
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
      <idap>{test_payee_id}</idap>
    </GetPayeeDetails>
  </soap12:Body>
</soap12:Envelope>"""

            headers = {
                'Content-Type': 'application/soap+xml; charset=utf-8; action="http://Tipalti.org/GetPayeeDetails"'
            }

            response = requests.post(endpoint, data=soap_body, headers=headers, timeout=10)
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                result_element = root.find('.//{http://Tipalti.org/}GetPayeeDetailsResult')
                
                if result_element is not None:
                    result = {}
                    for child in result_element:
                        tag = child.tag.replace('{http://Tipalti.org/}', '')
                        result[tag] = child.text
                    
                    error_msg = result.get('errorMessage', 'No error')
                    print(f"   📊 Response: {error_msg}")
                    
                    if error_msg != "InvalidPayerIpAddress":
                        print(f"   🎉 DIFFERENT RESULT! May work with this endpoint")
                        return endpoint, error_msg
                else:
                    print(f"   ❓ No result element")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Error: {e}")
        
        time.sleep(1)
    
    return None, None


def test_ip_variations():
    """Test different IP formats that might work"""
    
    print("\n🔢 Testing Different IP Formats")
    print("-" * 40)
    
    base_ip = "84.115.224.136"
    ip_formats = [
        base_ip,                    # 84.115.224.136
        f"{base_ip}/32",           # 84.115.224.136/32
        f"{base_ip}/24",           # 84.115.224.136/24  
        "84.115.224.0/24",         # Network range
        "84.115.224.*",            # Wildcard
    ]
    
    print("💡 Try these IP formats in Tipalti Dashboard:")
    for i, ip_format in enumerate(ip_formats, 1):
        print(f"{i}. {ip_format}")
    
    return ip_formats


def comprehensive_diagnosis():
    """Run comprehensive diagnosis"""
    
    print("🔧 TIPALTI IP WHITELIST TROUBLESHOOTING")
    print("=" * 60)
    print(f"🕒 Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"🌐 Current IP: 84.115.224.136")
    print()
    
    # Basic connectivity
    if not test_basic_connectivity():
        return False
    
    # Different endpoints
    working_endpoint, error_msg = test_different_endpoints()
    
    # IP format suggestions
    ip_formats = test_ip_variations()
    
    # Summary and recommendations
    print("\n" + "=" * 60)
    print("📋 TROUBLESHOOTING SUMMARY")
    print("=" * 60)
    
    if working_endpoint:
        print(f"🎉 Found different result with: {working_endpoint}")
        print(f"📊 Error message: {error_msg}")
    else:
        print("❌ All endpoints show same IP blocking")
    
    print("\n🔧 RECOMMENDED ACTIONS:")
    print("1️⃣ DOUBLE-CHECK TIPALTI DASHBOARD:")
    print("   • Go to Settings → API Configuration")
    print("   • Verify IP: 84.115.224.136 is listed")
    print("   • Status should be: Active")
    print("   • Source type should be: API")
    
    print("\n2️⃣ TRY DIFFERENT IP FORMATS:")
    for ip_format in ip_formats:
        print(f"   • {ip_format}")
    
    print("\n3️⃣ CHECK OTHER SECTIONS:")
    print("   • Security Settings")
    print("   • User Permissions") 
    print("   • API Access Control")
    
    print("\n4️⃣ CONTACT TIPALTI SUPPORT:")
    print("   • Email: support@tipalti.com")
    print("   • Subject: API IP Whitelist Not Working")
    print("   • Include: Payer 'Uplify', IP 84.115.224.136")
    print("   • Mention: InvalidPayerIpAddress error")
    
    print("\n5️⃣ TRY ALTERNATIVE APPROACHES:")
    print("   • VPN to different location")
    print("   • Contact your IT team")
    print("   • Ask Tipalti for current whitelisted IPs")
    
    # Save detailed report
    report = {
        'timestamp': datetime.now().isoformat(),
        'ip_address': '84.115.224.136',
        'issue': 'InvalidPayerIpAddress persisting after 30+ minutes',
        'endpoints_tested': 4,
        'working_endpoint': working_endpoint,
        'different_error': error_msg,
        'recommended_ip_formats': ip_formats,
        'next_steps': [
            'Verify IP in Tipalti Dashboard',
            'Try different IP formats',
            'Contact Tipalti support',
            'Try VPN/different network'
        ]
    }
    
    filename = f"ip_troubleshooting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Detailed report saved: {filename}")
    
    return True


if __name__ == "__main__":
    comprehensive_diagnosis() 