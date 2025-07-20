#!/usr/bin/env python3
"""
Tipalti Backup with IP Whitelist Detection
Detects IP issues and provides fix guidance
"""

import requests
import time
import hmac
import hashlib
import xml.etree.ElementTree as ET
import json
from datetime import datetime


def get_current_ip():
    """Get current public IP address"""
    try:
        response = requests.get('https://ipinfo.io/ip', timeout=5)
        return response.text.strip()
    except:
        return "Unable to detect"


def check_ip_whitelist_issue():
    """Check if we have IP whitelist issues by testing known payee ID"""
    
    print("🔍 Checking IP Whitelist Status...")
    
    # Test with a known real payee ID
    payer_name = "your_payer_name"
    master_key = "your_master_key_here"
    test_payee_id = "37617"  # Real payee ID from dashboard
    
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
                    return "ip_blocked"
                elif error_msg == "EncryptionKeyFailedValidation":
                    return "bad_credentials"
                elif error_msg == "PayeeUnknown":
                    return "ip_allowed_but_wrong_id"
                elif not error_msg:
                    return "working"
                else:
                    return f"other_error: {error_msg}"
        
        return "http_error"
        
    except Exception as e:
        return f"exception: {e}"


def create_ip_status_report():
    """Create a comprehensive IP and system status report"""
    
    print("🚀 Tipalti System Status & IP Whitelist Check")
    print("=" * 60)
    
    current_ip = get_current_ip()
    ip_status = check_ip_whitelist_issue()
    
    print(f"🌐 Current IP: {current_ip}")
    print(f"🔍 IP Status: {ip_status}")
    print()
    
    # Create status report
    status_report = {
        'timestamp': datetime.now().isoformat(),
        'system_check': {
            'current_ip': current_ip,
            'ip_status': ip_status,
            'payer_name': 'Uplify',
            'environment': 'production',
            'known_payees_count': 3857
        }
    }
    
    if ip_status == "ip_blocked":
        print("❌ IP ADDRESS BLOCKED")
        print("=" * 30)
        print("🚫 Error: InvalidPayerIpAddress")
        print(f"🌐 Your IP: {current_ip}")
        print("🔧 Solution: Add IP to Tipalti whitelist")
        print()
        print("📋 Instructions:")
        print("1. Login to Tipalti Dashboard")
        print("2. Go to Settings → API Configuration")
        print("3. Add IP to whitelist:", current_ip)
        print("4. Wait 5-10 minutes")
        print("5. Run backup again")
        print()
        
        status_report['issue'] = {
            'type': 'ip_whitelist_blocked',
            'blocked_ip': current_ip,
            'solution': 'Add IP to Tipalti whitelist',
            'next_steps': [
                'Login to Tipalti Dashboard',
                'Go to Settings → API Configuration',
                f'Add IP to whitelist: {current_ip}',
                'Wait 5-10 minutes for propagation',
                'Run backup again'
            ]
        }
        
    elif ip_status == "working":
        print("✅ IP ADDRESS WORKING")
        print("=" * 30)
        print("🎉 Your IP is whitelisted!")
        print("🚀 Ready to backup all 3,857 payees!")
        
        status_report['status'] = 'ready_for_backup'
        
    elif ip_status == "bad_credentials":
        print("❌ CREDENTIALS ISSUE") 
        print("=" * 30)
        print("🔑 Check payer name and master key")
        
        status_report['issue'] = {
            'type': 'invalid_credentials',
            'solution': 'Verify payer name and master key'
        }
        
    else:
        print("⚠️  UNKNOWN ISSUE")
        print("=" * 30)  
        print(f"Status: {ip_status}")
        
        status_report['issue'] = {
            'type': 'unknown',
            'details': ip_status
        }
    
    # Save status report
    filename = f"system_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(status_report, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Status report saved: {filename}")
    
    return ip_status == "working"


if __name__ == "__main__":
    ready_for_backup = create_ip_status_report()
    
    if ready_for_backup:
        print(f"\n🎉 SYSTEM READY!")
        print(f"🚀 Run: python backup_production_final.py")
        print(f"📊 Expected: Backup of all 3,857 payees")
    else:
        print(f"\n💡 SYSTEM NOT READY")
        print(f"🔧 Fix the issue above first")
        print(f"🔄 Then run this script again to verify") 