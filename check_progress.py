#!/usr/bin/env python3
"""
Quick Progress Checker
Быстрая проверка прогресса блокировки RU payees
"""

from tipalti_rest_api import TipaltiRestAPI
import config_rest
from datetime import datetime

def main():
    print(f"📊 PROGRESS CHECK - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 40)
    
    try:
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        
        # Get sample of payees
        response = api._make_request('GET', '/payees', params={'limit': 100})
        
        if isinstance(response, dict) and 'items' in response:
            ru_stats = {}
            for payee in response['items']:
                contact = payee.get('contactInformation', {})
                if contact.get('beneficiaryCountryCode') == 'RU':
                    status = payee.get('status', 'UNKNOWN')
                    ru_stats[status] = ru_stats.get(status, 0) + 1
            
            total_ru = sum(ru_stats.values())
            suspended = ru_stats.get('SUSPENDED', 0)
            active = ru_stats.get('ACTIVE', 0)
            
            print(f"📈 Sample results (first 100 payees):")
            print(f"  RU payees found: {total_ru}")
            print(f"  🔒 SUSPENDED: {suspended}")
            print(f"  ⚠️ ACTIVE: {active}")
            
            if total_ru > 0:
                completion = (suspended / total_ru) * 100
                print(f"  📊 Sample completion: {completion:.1f}%")
                
                if suspended > 13:  # More than initial 13
                    print(f"  🎉 Progress detected! (+{suspended - 13} new)")
                elif active == 0:
                    print(f"  🏆 Sample fully completed!")
            
        else:
            print("❌ Could not fetch data")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 