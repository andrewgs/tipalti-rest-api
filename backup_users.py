#!/usr/bin/env python3
"""
Simple backup script for Tipalti users
Saves all users to a timestamped JSON file
"""

import json
import sys
from datetime import datetime
from tipalti_api import TipaltiAPI
import config


def backup_users():
    """Backup all users from Tipalti to JSON file"""
    try:
        # Validate configuration and get values
        payer_name, master_key, is_sandbox = config.get_validated_config()
        
        # Initialize API client
        print("Connecting to Tipalti API...")
        api = TipaltiAPI(payer_name, master_key, is_sandbox)
        
        # Get all payees
        print("Fetching all users...")
        payees = api.get_payees_list()
        
        if not payees:
            print("No users found or failed to retrieve users")
            return False
        
        print(f"Found {len(payees)} users")
        
        # Get detailed information for each user
        detailed_users = []
        for i, payee in enumerate(payees, 1):
            idap = payee.get('idap', payee.get('Idap', ''))
            if not idap:
                print(f"Warning: User {i} has no IDAP, skipping...")
                continue
            
            print(f"Getting details for user {i}/{len(payees)}: {idap}")
            
            details = api.get_payee_details(idap)
            if details:
                # Merge basic info with detailed info
                user_data = {**payee, **details}
                detailed_users.append(user_data)
            else:
                # Fallback to basic info if details unavailable
                detailed_users.append(payee)
        
        # Create timestamped backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.json"
        
        # Save to JSON file
        backup_data = {
            'backup_date': datetime.now().isoformat(),
            'total_users': len(detailed_users),
            'environment': 'sandbox' if is_sandbox else 'production',
            'payer_name': payer_name,
            'users': detailed_users
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Backup completed successfully!")
        print(f"📁 Saved {len(detailed_users)} users to: {filename}")
        print(f"🔧 Environment: {'Sandbox' if is_sandbox else 'Production'}")
        
        return True
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Please check your .env file and ensure all required variables are set")
        return False
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False


if __name__ == "__main__":
    print("🔄 Starting Tipalti Users Backup")
    print("=" * 40)
    
    success = backup_users()
    
    if success:
        print("\n✨ Backup process completed successfully!")
    else:
        print("\n💥 Backup process failed!")
        sys.exit(1) 