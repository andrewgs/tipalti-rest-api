#!/usr/bin/env python3
"""
Tipalti Users Cleanup Script (REST API)
Deactivates users inactive since 2025
"""

import sys
from datetime import datetime, date
from tipalti_rest_api import TipaltiRestAPI
import config_rest


def is_user_inactive(user_data, cutoff_date_str):
    """
    Determine if a user is inactive based on activity since cutoff date
    A user is inactive if no activity since 2025-01-01
    """
    cutoff_date = datetime.strptime(cutoff_date_str, '%Y-%m-%d').date()
    
    # Check if user is already inactive
    status = user_data.get('status', user_data.get('payee_status', 'active'))
    if str(status).lower() in ['inactive', 'disabled', 'suspended']:
        return True, "Already inactive"
    
    # Check last login date
    last_login = user_data.get('last_login_date', user_data.get('lastLoginDate', ''))
    if last_login:
        try:
            login_date = datetime.strptime(last_login[:10], '%Y-%m-%d').date()
            if login_date < cutoff_date:
                return True, f"No login since {login_date}"
        except (ValueError, TypeError):
            pass  # Invalid date format, continue checking
    
    # Check last payment date  
    last_payment = user_data.get('last_payment_date', user_data.get('lastPaymentDate', ''))
    if last_payment:
        try:
            payment_date = datetime.strptime(last_payment[:10], '%Y-%m-%d').date()
            if payment_date < cutoff_date:
                return True, f"No payment since {payment_date}"
        except (ValueError, TypeError):
            pass  # Invalid date format, continue checking
    
    # Check creation date - if created before cutoff and no recent activity
    created_date = user_data.get('created_at', user_data.get('createdDate', ''))
    if created_date:
        try:
            created = datetime.strptime(created_date[:10], '%Y-%m-%d').date()
            if created < cutoff_date and not last_login and not last_payment:
                return True, f"Created {created}, no recorded activity"
        except (ValueError, TypeError):
            pass
    
    # If no activity dates found and created before cutoff, consider inactive
    if not last_login and not last_payment and not created_date:
        return True, "No activity records found"
    
    return False, "Active user"


def get_inactive_users(api, cutoff_date):
    """Get list of inactive users from Tipalti REST API"""
    print("👥 Fetching all users from Tipalti...")
    
    all_users = api.get_payees_list()
    if not all_users:
        print("❌ Failed to retrieve users from API")
        return []
    
    print(f"📊 Found {len(all_users)} total users")
    print("🔍 Checking activity status...")
    
    inactive_users = []
    
    for i, user in enumerate(all_users, 1):
        user_id = user.get('id', user.get('payee_id', ''))
        user_name = user.get('name', user.get('display_name', 'Unknown'))
        user_email = user.get('email', 'Unknown')
        
        if not user_id:
            print(f"⚠️  User {i} has no ID, skipping...")
            continue
        
        # Check if user is inactive
        is_inactive, reason = is_user_inactive(user, cutoff_date)
        
        if is_inactive:
            user_info = {
                'id': user_id,
                'name': user_name,
                'email': user_email,
                'reason': reason,
                'data': user
            }
            inactive_users.append(user_info)
            print(f"  📋 {user_id}: {user_name} - {reason}")
        
        # Progress indicator
        if i % 20 == 0:
            print(f"  ⏳ Processed {i}/{len(all_users)} users...")
    
    return inactive_users


def cleanup_users():
    """Main cleanup function using REST API"""
    try:
        # Validate configuration and get values
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        
        print("🔄 Starting Tipalti Users Cleanup (REST API)")
        print("=" * 60)
        print(f"🎯 Cutoff Date: {config_rest.CUTOFF_DATE}")
        print(f"🌐 Environment: {'Sandbox' if is_sandbox else 'Production'}")
        print(f"🚀 API Type: REST API v1 with OAuth 2.0")
        print()
        
        # Initialize REST API client
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        
        # Authenticate
        print("🔐 Authenticating with OAuth 2.0...")
        token = api._get_access_token()
        print(f"✅ Access token obtained")
        
        # Get inactive users
        inactive_users = get_inactive_users(api, config_rest.CUTOFF_DATE)
        
        if not inactive_users:
            print("\n🎉 No inactive users found! All users are active.")
            return True
        
        print(f"\n📊 Found {len(inactive_users)} inactive users:")
        print("-" * 60)
        
        for user in inactive_users:
            print(f"  👤 {user['id']}: {user['name']} ({user['email']})")
            print(f"     💭 Reason: {user['reason']}")
        
        print("-" * 60)
        
        # Confirmation prompt
        response = input(f"\n❓ Deactivate {len(inactive_users)} inactive users? (y/N): ").strip().lower()
        
        if response not in ['y', 'yes']:
            print("❌ Cleanup cancelled by user")
            return False
        
        print(f"\n🚀 Starting deactivation process...")
        
        # Deactivate users one by one
        success_count = 0
        failed_count = 0
        
        for i, user in enumerate(inactive_users, 1):
            user_id = user['id']
            name = user['name']
            
            print(f"⏳ Deactivating {i}/{len(inactive_users)}: {user_id} ({name})...")
            
            try:
                success = api.deactivate_payee(user_id)
                if success:
                    print(f"   ✅ Successfully deactivated {user_id}")
                    success_count += 1
                else:
                    print(f"   ❌ Failed to deactivate {user_id}")
                    failed_count += 1
            except Exception as e:
                print(f"   💥 Error deactivating {user_id}: {e}")
                failed_count += 1
        
        # Summary
        print(f"\n🏁 Cleanup completed!")
        print(f"✅ Successfully deactivated: {success_count} users")
        if failed_count > 0:
            print(f"❌ Failed to deactivate: {failed_count} users")
        
        return failed_count == 0
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Please check your .env file and ensure all required OAuth variables are set")
        print("📖 See: https://documentation.tipalti.com/reference/quick-start")
        return False
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False


if __name__ == "__main__":
    print("🧹 Tipalti Users Cleanup Tool (REST API)")
    print("=" * 50)
    print("⚠️  WARNING: This will deactivate inactive users!")
    print("💡 Run 'python backup_users_rest.py' first to create a backup")
    print("🔗 Using modern REST API with OAuth 2.0")
    print()
    
    proceed = input("Continue? (y/N): ").strip().lower()
    if proceed not in ['y', 'yes']:
        print("❌ Cleanup cancelled")
        sys.exit(0)
    
    success = cleanup_users()
    
    if success:
        print("\n🎉 REST API cleanup process completed successfully!")
    else:
        print("\n💥 REST API cleanup process failed or partially failed!")
        sys.exit(1) 