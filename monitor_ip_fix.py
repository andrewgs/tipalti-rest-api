#!/usr/bin/env python3
"""
Monitor IP Whitelist Status
Periodically checks when IP whitelist starts working
"""

import requests
import time
import hmac
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime


def check_ip_status():
    """Check if IP whitelist is working"""
    
    payer_name = "Uplify"
    master_key = "j0YPT6AkeKPUl3z8+glS5S0mt4wjU9G4EuglK0/q/X659Qih7ds/GCBseRmmCDbS"
    test_payee_id = "37617"  # Real payee from user data
    
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
            timeout=10
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
                    return "blocked", "IP still blocked"
                elif error_msg:
                    return "other_error", error_msg
                else:
                    # SUCCESS!
                    payee_name = result.get('d', 'N/A')
                    return "working", f"Found payee: {payee_name}"
        
        return "http_error", f"HTTP {response.status_code}"
        
    except Exception as e:
        return "exception", str(e)


def monitor_whitelist():
    """Monitor IP whitelist status until it works"""
    
    print("🔄 Monitoring IP Whitelist Status")
    print("=" * 50)
    print("⏱️  Checking every 60 seconds...")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    start_time = datetime.now()
    check_count = 0
    
    try:
        while True:
            check_count += 1
            elapsed = datetime.now() - start_time
            elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
            
            print(f"🔍 Check #{check_count} (Elapsed: {elapsed_str})")
            
            status, message = check_ip_status()
            
            if status == "working":
                print(f"   🎉 SUCCESS! {message}")
                print()
                print("🚀 IP WHITELIST IS WORKING!")
                print("=" * 30)
                print("✅ Tipalti API access granted")
                print("📊 Ready to backup all 3,857 payees")
                print()
                print("🔥 Run full backup now:")
                print("   python backup_production_final.py")
                break
                
            elif status == "blocked":
                print(f"   ⏱️  Still blocked - waiting for propagation...")
                
            elif status == "other_error":
                print(f"   ⚠️  API Error: {message}")
                
            else:
                print(f"   💥 {status}: {message}")
            
            # Wait suggestions based on time elapsed
            if elapsed.total_seconds() < 300:  # Less than 5 minutes
                print(f"   💡 Normal - whitelist changes take 5-15 minutes")
            elif elapsed.total_seconds() < 900:  # Less than 15 minutes  
                print(f"   ⏳ Still within normal range - be patient")
            else:  # More than 15 minutes
                print(f"   🤔 Taking longer than usual - may need to check settings")
            
            print()
            
            # Wait 60 seconds before next check
            for i in range(60, 0, -1):
                print(f"\r⏱️  Next check in {i:2d} seconds...", end="", flush=True)
                time.sleep(1)
            print("\r" + " " * 30 + "\r", end="")  # Clear countdown line
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Monitoring stopped by user")
        print(f"⏱️  Total elapsed time: {elapsed_str}")
        print(f"🔢 Total checks performed: {check_count}")
        print()
        print("💡 You can run manual test anytime:")
        print("   python test_after_ip_fix.py")


if __name__ == "__main__":
    monitor_whitelist() 