#!/usr/bin/env python3
"""
Tipalti Users Backup using REST API
Saves all users to a timestamped JSON file
"""

import json
import sys
from datetime import datetime
from tipalti_rest_api import TipaltiRestAPI
import config_rest


def backup_users():
    """Backup all users from Tipalti REST API to JSON file"""
    try:
        # Validate configuration
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        
        # Initialize REST API client
        print("🔗 Connecting to Tipalti REST API...")
        print(f"🌐 Environment: {'Sandbox' if is_sandbox else 'Production'}")
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        
        # Get OAuth token
        print("🔐 Authenticating with OAuth 2.0...")
        token = api._get_access_token()
        print(f"✅ Access token obtained: {token[:20]}...")
        
        # Get all payees
        print("👥 Fetching all users...")
        payees = api.get_payees_list()
        
        if not payees:
            print("❌ No users found or failed to retrieve users")
            return False
        
        print(f"📊 Found {len(payees)} users")
        
        # Get detailed information for each user (optional, for smaller lists)
        detailed_users = []
        if len(payees) <= 50:  # Only get details for small lists to avoid rate limits
            print("📋 Getting detailed information...")
            for i, payee in enumerate(payees, 1):
                payee_id = payee.get('id') or payee.get('payee_id')
                if not payee_id:
                    print(f"⚠️  User {i} has no ID, using basic info...")
                    detailed_users.append(payee)
                    continue
                
                print(f"  📝 Getting details for user {i}/{len(payees)}: {payee_id}")
                
                details = api.get_payee_details(payee_id)
                if details:
                    # Use detailed info
                    detailed_users.append(details)
                else:
                    # Fallback to basic info
                    detailed_users.append(payee)
        else:
            print("📊 Using basic user information (large dataset)")
            detailed_users = payees
        
        # Create timestamped backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_rest_{timestamp}.json"
        
        # Save to JSON file
        backup_data = {
            'backup_date': datetime.now().isoformat(),
            'backup_type': 'rest_api',
            'total_users': len(detailed_users),
            'environment': 'sandbox' if is_sandbox else 'production',
            'api_type': 'REST API v1',
            'users': detailed_users
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 Backup completed successfully!")
        print(f"📁 Saved {len(detailed_users)} users to: {filename}")
        print(f"🔧 Environment: {'Sandbox' if is_sandbox else 'Production'}")
        print(f"🚀 API Type: REST API v1 with OAuth 2.0")
        
        return True
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Please check your .env file and ensure all required OAuth variables are set")
        print("📖 See: https://documentation.tipalti.com/reference/quick-start")
        return False
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False


if __name__ == "__main__":
    print("🔄 Starting Tipalti Users Backup (REST API)")
    print("=" * 50)
    
    success = backup_users()
    
    if success:
        print("\n✨ REST API backup process completed successfully!")
        print("🔗 Using modern OAuth 2.0 authentication")
    else:
        print("\n💥 REST API backup process failed!")
        sys.exit(1) 