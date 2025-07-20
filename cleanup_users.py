#!/usr/bin/env python3
"""
Tipalti Users Cleanup Script
Deactivates users inactive since 2025
"""

import sys
from datetime import datetime, date
from tipalti_api import TipaltiAPI
import config


def is_user_inactive(user_data, cutoff_date_str):
    """
    Determine if a user is inactive based on activity since cutoff date
    A user is inactive if no activity since 2025-01-01
    """
    cutoff_date = datetime.strptime(cutoff_date_str, '%Y-%m-%d').date()
    
    # Check if user is already inactive
    is_active = user_data.get('isActive', user_data.get('IsActive', 'true'))
    if str(is_active).lower() == 'false':
        return True, "Already inactive"
    
    # Check last login date
    last_login = user_data.get('lastLoginDate', user_data.get('LastLoginDate', ''))
    if last_login:
        try:
            login_date = datetime.strptime(last_login[:10], '%Y-%m-%d').date()
            if login_date < cutoff_date:
                return True, f"No login since {login_date}"
        except (ValueError, TypeError):
            pass  # Invalid date format, continue checking
    
    # Check last payment date
    last_payment = user_data.get('lastPaymentDate', user_data.get('LastPaymentDate', ''))
    if last_payment:
        try:
            payment_date = datetime.strptime(last_payment[:10], '%Y-%m-%d').date()
            if payment_date < cutoff_date:
                return True, f"No payment since {payment_date}"
        except (ValueError, TypeError):
            pass  # Invalid date format, continue checking
    
    # Check creation date - if created before cutoff and no recent activity
    created_date = user_data.get('createdDate', user_data.get('CreatedDate', ''))
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
    """Get list of inactive users from Tipalti"""
    print("Fetching all users from Tipalti...")
    
    all_users = api.get_payees_list()
    if not all_users:
        print("❌ Failed to retrieve users from API")
        return []
    
    print(f"📊 Found {len(all_users)} total users")
    print("🔍 Checking activity status...")
    
    inactive_users = []
    
    for i, user in enumerate(all_users, 1):
        idap = user.get('idap', user.get('Idap', ''))
        if not idap:
            print(f"⚠️  User {i} has no IDAP, skipping...")
            continue
        
        # Get detailed user information
        details = api.get_payee_details(idap)
        if details:
            user_data = {**user, **details}
        else:
            user_data = user
        
        # Check if user is inactive
        is_inactive, reason = is_user_inactive(user_data, cutoff_date)
        
        if is_inactive:
            user_info = {
                'idap': idap,
                'name': user_data.get('payeeName', user_data.get('PayeeName', 'Unknown')),
                'email': user_data.get('email', user_data.get('Email', 'Unknown')),
                'reason': reason,
                'data': user_data
            }
            inactive_users.append(user_info)
            print(f"  📋 {idap}: {user_info['name']} - {reason}")
        
        # Progress indicator
        if i % 10 == 0:
            print(f"  ⏳ Processed {i}/{len(all_users)} users...")
    
    return inactive_users


def cleanup_users():
    """Main cleanup function"""
    try:
        # Validate configuration and get values
        payer_name, master_key, is_sandbox = config.get_validated_config()
        
        print("🔄 Starting Tipalti Users Cleanup")
        print("=" * 50)
        print(f"🎯 Cutoff Date: {config.CUTOFF_DATE}")
        print(f"🔧 Environment: {'Sandbox' if is_sandbox else 'Production'}")
        print(f"🏢 Payer: {payer_name}")
        print()
        
        # Initialize API client
        api = TipaltiAPI(payer_name, master_key, is_sandbox)
        
        # Get inactive users
        inactive_users = get_inactive_users(api, config.CUTOFF_DATE)
        
        if not inactive_users:
            print("\n🎉 No inactive users found! All users are active.")
            return True
        
        print(f"\n📊 Found {len(inactive_users)} inactive users:")
        print("-" * 50)
        
        for user in inactive_users:
            print(f"  👤 {user['idap']}: {user['name']} ({user['email']})")
            print(f"     💭 Reason: {user['reason']}")
        
        print("-" * 50)
        
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
            idap = user['idap']
            name = user['name']
            
            print(f"⏳ Deactivating {i}/{len(inactive_users)}: {idap} ({name})...")
            
            try:
                success = api.deactivate_payee(idap)
                if success:
                    print(f"   ✅ Successfully deactivated {idap}")
                    success_count += 1
                else:
                    print(f"   ❌ Failed to deactivate {idap}")
                    failed_count += 1
            except Exception as e:
                print(f"   💥 Error deactivating {idap}: {e}")
                failed_count += 1
        
        # Summary
        print(f"\n🏁 Cleanup completed!")
        print(f"✅ Successfully deactivated: {success_count} users")
        if failed_count > 0:
            print(f"❌ Failed to deactivate: {failed_count} users")
        
        return failed_count == 0
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Please check your .env file and ensure all required variables are set")
        return False
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False


if __name__ == "__main__":
    print("🧹 Tipalti Users Cleanup Tool")
    print("=" * 40)
    print("⚠️  WARNING: This will deactivate inactive users!")
    print("💡 Run 'python backup_users.py' first to create a backup")
    print()
    
    proceed = input("Continue? (y/N): ").strip().lower()
    if proceed not in ['y', 'yes']:
        print("❌ Cleanup cancelled")
        sys.exit(0)
    
    success = cleanup_users()
    
    if success:
        print("\n🎉 Cleanup process completed successfully!")
    else:
        print("\n💥 Cleanup process failed or partially failed!")
        sys.exit(1) 