#!/usr/bin/env python3
"""
Tipalti RU Payees Deletion Script
Безопасное удаление всех payees с beneficiaryCountryCode = "RU"
"""

import json
import sys
from datetime import datetime
from tipalti_rest_api import TipaltiRestAPI
import config_rest


def load_backup_data(backup_file: str) -> dict:
    """Load backup data to identify RU payees"""
    try:
        with open(backup_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading backup file: {e}")
        return None


def find_ru_payees(backup_data: dict) -> list:
    """Find all payees with beneficiaryCountryCode = 'RU'"""
    ru_payees = []
    
    for user in backup_data.get('users', []):
        contact = user.get('contactInformation', {})
        if contact.get('beneficiaryCountryCode') == 'RU':
            ru_payees.append({
                'id': user['id'],
                'refCode': user['refCode'],
                'status': user['status'],
                'email': contact.get('email', 'N/A'),
                'firstName': contact.get('firstName', ''),
                'lastName': contact.get('lastName', ''),
                'companyName': contact.get('companyName', '')
            })
    
    return ru_payees


def create_deletion_report(ru_payees: list) -> str:
    """Create detailed deletion report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"ru_payees_deletion_report_{timestamp}.json"
    
    # Count by status
    status_counts = {}
    for payee in ru_payees:
        status = payee['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    report = {
        "deletion_date": datetime.now().isoformat(),
        "total_ru_payees": len(ru_payees),
        "status_breakdown": status_counts,
        "payees_to_delete": ru_payees
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report_file


def delete_payee_via_rest_api(api: TipaltiRestAPI, payee_id: str, dry_run: bool = True) -> dict:
    """Delete single payee via REST API"""
    if dry_run:
        return {"success": True, "message": "DRY RUN - Would delete payee", "payee_id": payee_id}
    
    try:
        result = api.delete_payee(payee_id)
        result["payee_id"] = payee_id
        return result
    except Exception as e:
        return {"success": False, "message": str(e), "payee_id": payee_id}


def main():
    """Main deletion process"""
    print("🔥 TIPALTI RU PAYEES DELETION SCRIPT")
    print("=" * 50)
    
    # Load backup data
    backup_file = "backup_rest_20250722_185837.json"
    print(f"📁 Loading backup from: {backup_file}")
    
    backup_data = load_backup_data(backup_file)
    if not backup_data:
        print("❌ Failed to load backup data. Exiting.")
        return False
    
    # Find RU payees
    ru_payees = find_ru_payees(backup_data)
    print(f"\n🎯 Found {len(ru_payees)} RU payees to delete")
    
    # Show statistics
    status_counts = {}
    for payee in ru_payees:
        status = payee['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\n📊 Status breakdown:")
    for status, count in status_counts.items():
        print(f"  {status}: {count} payees")
    
    # Show first 5 examples
    print("\n🔍 First 5 examples:")
    for i, payee in enumerate(ru_payees[:5], 1):
        name = f"{payee['firstName']} {payee['lastName']}".strip() or payee['companyName'] or 'N/A'
        print(f"  {i}. {payee['refCode']} | {name} | {payee['email'][:30]}... | {payee['status']}")
    
    # Critical confirmation
    print(f"\n⚠️  CRITICAL WARNING ⚠️")
    print(f"You are about to delete {len(ru_payees)} payees from PRODUCTION Tipalti!")
    print(f"This action cannot be undone!")
    
    # Ask for confirmation
    confirm1 = input(f"\n❓ Type 'DELETE {len(ru_payees)} RU PAYEES' to confirm: ")
    if confirm1 != f"DELETE {len(ru_payees)} RU PAYEES":
        print("❌ Confirmation failed. Exiting.")
        return False
    
    confirm2 = input("❓ Type 'I UNDERSTAND THIS CANNOT BE UNDONE' to proceed: ")
    if confirm2 != "I UNDERSTAND THIS CANNOT BE UNDONE":
        print("❌ Final confirmation failed. Exiting.")
        return False
    
    # Choose mode
    mode = input("\n⚙️ Choose mode:\n  1. DRY RUN (show what would be deleted)\n  2. REAL DELETION\nEnter 1 or 2: ")
    
    dry_run = True
    if mode == "2":
        dry_run = False
        print("🔥 REAL DELETION MODE ACTIVATED")
    else:
        print("🔍 DRY RUN MODE - No actual deletions")
    
    # Create deletion report
    report_file = create_deletion_report(ru_payees)
    print(f"📋 Deletion report created: {report_file}")
    
    # Initialize REST API
    try:
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        
        # Update scope to include write permissions
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        # Update the scope in the API client to include write permissions
        print("🔐 Initializing REST API with write permissions...")
        
    except Exception as e:
        print(f"❌ Failed to initialize REST API: {e}")
        return False
    
    # Perform deletions
    print(f"\n🚀 Starting {'DRY RUN' if dry_run else 'REAL'} deletion process...")
    
    success_count = 0
    failed_count = 0
    
    for i, payee in enumerate(ru_payees, 1):
        print(f"Processing {i}/{len(ru_payees)}: {payee['refCode']} | {payee['status']}")
        
        result = delete_payee_via_rest_api(api, payee['id'], dry_run)
        
        if result['success']:
            success_count += 1
            print(f"  ✅ {result['message']}")
        else:
            failed_count += 1
            print(f"  ❌ {result['message']}")
        
        # Progress update every 100
        if i % 100 == 0:
            print(f"📊 Progress: {i}/{len(ru_payees)} | Success: {success_count} | Failed: {failed_count}")
    
    # Final summary
    print(f"\n🎯 DELETION SUMMARY:")
    print(f"📊 Total processed: {len(ru_payees)}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📋 Report saved: {report_file}")
    
    if not dry_run and success_count > 0:
        print(f"\n🔥 REAL DELETIONS COMPLETED!")
        print(f"⚠️  {success_count} RU payees have been permanently deleted from Tipalti")
    
    return True


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc() 