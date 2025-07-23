#!/usr/bin/env python3
"""
Tipalti RU Payees Deactivation Script
Безопасная деактивация всех payees с beneficiaryCountryCode = "RU"
через изменение статуса на BLOCKED
"""

import json
import time
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


def find_ru_payees(backup_data: dict, only_active: bool = False) -> list:
    """Find all RU payees (optionally only ACTIVE ones)"""
    ru_payees = []
    
    for user in backup_data.get('users', []):
        contact = user.get('contactInformation', {})
        if contact.get('beneficiaryCountryCode') == 'RU':
            # Skip already blocked if only_active is True
            if only_active and user['status'] in ['BLOCKED_BY_TIPALTI', 'BLOCKED', 'SUSPENDED']:
                continue
                
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


def deactivate_payee_via_rest_api(api: TipaltiRestAPI, payee: dict, dry_run: bool = True) -> dict:
    """Deactivate single payee by changing status to BLOCKED"""
    if dry_run:
        return {"success": True, "message": "DRY RUN - Would block payee", "payee_id": payee['id']}
    
    try:
        # Try different status values that might work
        status_options = ['BLOCKED', 'SUSPENDED', 'INACTIVE']
        
        for status in status_options:
            deactivate_data = {'status': status}
            
            # Try to update payee status
            success = api.update_payee(payee['id'], deactivate_data)
            
            if success:
                return {
                    "success": True, 
                    "message": f"Payee status changed to {status}", 
                    "payee_id": payee['id'],
                    "new_status": status
                }
        
        # If all status options failed
        return {
            "success": False, 
            "message": "All status update attempts failed", 
            "payee_id": payee['id']
        }
        
    except Exception as e:
        return {"success": False, "message": str(e), "payee_id": payee['id']}


def create_deactivation_report(results: list) -> str:
    """Create detailed deactivation report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"ru_payees_deactivation_report_{timestamp}.json"
    
    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]
    
    report = {
        "deactivation_date": datetime.now().isoformat(),
        "operation": "MASS_DEACTIVATION_RU_PAYEES",
        "total_processed": len(results),
        "successful_deactivations": len(successful),
        "failed_deactivations": len(failed),
        "success_rate": f"{len(successful)/len(results)*100:.1f}%" if results else "0%",
        "results": results,
        "summary": {
            "status_changes": {}
        }
    }
    
    # Count status changes
    for result in successful:
        new_status = result.get('new_status', 'UNKNOWN')
        report["summary"]["status_changes"][new_status] = \
            report["summary"]["status_changes"].get(new_status, 0) + 1
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report_file


def main():
    """Main deactivation process"""
    print("🔒 TIPALTI RU PAYEES DEACTIVATION SCRIPT")
    print("=" * 50)
    
    # Load backup data
    backup_file = "backup_rest_20250722_185837.json"
    print(f"📁 Loading backup from: {backup_file}")
    
    backup_data = load_backup_data(backup_file)
    if not backup_data:
        print("❌ Failed to load backup data. Exiting.")
        return False
    
    # Find RU payees
    all_ru_payees = find_ru_payees(backup_data, only_active=False)
    active_ru_payees = find_ru_payees(backup_data, only_active=True)
    
    print(f"\n🎯 Found {len(all_ru_payees)} total RU payees")
    print(f"🎯 Found {len(active_ru_payees)} ACTIVE RU payees (need deactivation)")
    
    # Show statistics
    status_counts = {}
    for payee in all_ru_payees:
        status = payee['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\n📊 Current status breakdown:")
    for status, count in status_counts.items():
        print(f"  {status}: {count} payees")
    
    if not active_ru_payees:
        print("\n✅ All RU payees are already deactivated!")
        return True
    
    # Show first 5 examples
    print(f"\n🔍 First 5 payees to deactivate:")
    for i, payee in enumerate(active_ru_payees[:5], 1):
        name = f"{payee['firstName']} {payee['lastName']}".strip() or payee['companyName'] or 'N/A'
        print(f"  {i}. {payee['refCode']} | {name} | {payee['email'][:30]}... | {payee['status']}")
    
    # Critical confirmation
    print(f"\n⚠️  DEACTIVATION CONFIRMATION ⚠️")
    print(f"You are about to BLOCK {len(active_ru_payees)} ACTIVE Russian payees!")
    print(f"This will prevent them from receiving future payments.")
    
    # Ask for confirmation
    confirm1 = input(f"\n❓ Type 'BLOCK {len(active_ru_payees)} RU PAYEES' to confirm: ")
    if confirm1 != f"BLOCK {len(active_ru_payees)} RU PAYEES":
        print("❌ Confirmation failed. Exiting.")
        return False
    
    # Choose mode
    mode = input("\n⚙️ Choose mode:\n  1. DRY RUN (show what would be blocked)\n  2. REAL DEACTIVATION\nEnter 1 or 2: ")
    
    dry_run = True
    if mode == "2":
        dry_run = False
        print("🔥 REAL DEACTIVATION MODE ACTIVATED")
    else:
        print("🔍 DRY RUN MODE - No actual changes")
    
    # Initialize REST API
    try:
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        print("🔐 REST API initialized successfully")
        
    except Exception as e:
        print(f"❌ Failed to initialize REST API: {e}")
        return False
    
    # Perform deactivations
    print(f"\n🚀 Starting {'DRY RUN' if dry_run else 'REAL'} deactivation process...")
    
    results = []
    success_count = 0
    failed_count = 0
    
    for i, payee in enumerate(active_ru_payees, 1):
        print(f"Processing {i}/{len(active_ru_payees)}: {payee['refCode']} | {payee['status']}")
        
        result = deactivate_payee_via_rest_api(api, payee, dry_run)
        results.append({
            **result,
            'payee_refCode': payee['refCode'],
            'payee_email': payee['email'],
            'original_status': payee['status']
        })
        
        if result['success']:
            success_count += 1
            status_msg = result.get('new_status', 'BLOCKED') if not dry_run else 'DRY RUN'
            print(f"  ✅ {result['message']} -> {status_msg}")
        else:
            failed_count += 1
            print(f"  ❌ {result['message']}")
        
        # Progress update every 50
        if i % 50 == 0:
            print(f"📊 Progress: {i}/{len(active_ru_payees)} | Success: {success_count} | Failed: {failed_count}")
        
        # Rate limiting to avoid API throttling
        if not dry_run and i % 10 == 0:
            time.sleep(1)  # 1 second pause every 10 requests
    
    # Create deactivation report
    report_file = create_deactivation_report(results)
    
    # Final summary
    print(f"\n🎯 DEACTIVATION SUMMARY:")
    print(f"📊 Total processed: {len(active_ru_payees)}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📈 Success rate: {success_count/len(active_ru_payees)*100:.1f}%")
    print(f"📋 Report saved: {report_file}")
    
    if not dry_run and success_count > 0:
        print(f"\n🔒 REAL DEACTIVATIONS COMPLETED!")
        print(f"⚠️  {success_count} RU payees have been BLOCKED in Tipalti")
        print(f"🚫 They will no longer be able to receive payments")
        
        # Suggest verification
        print(f"\n💡 NEXT STEPS:")
        print(f"1. 🔍 Run backup script again to verify status changes")
        print(f"2. 📧 Notify stakeholders about completed deactivation")
        print(f"3. 📊 Archive deactivation report for compliance")
    
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