#!/usr/bin/env python3
"""
Tipalti RU Payees Management Script
Альтернативные методы "удаления" RU payees:
1. Массовая блокировка через поддержку Tipalti
2. Экспорт списка для ручного управления
3. Создание отчета для compliance команды
"""

import json
import csv
from datetime import datetime


def load_ru_payees(backup_file: str) -> list:
    """Load and filter RU payees from backup"""
    with open(backup_file, 'r') as f:
        data = json.load(f)
    
    ru_payees = []
    for user in data['users']:
        contact = user.get('contactInformation', {})
        if contact.get('beneficiaryCountryCode') == 'RU':
            ru_payees.append({
                'id': user['id'],
                'refCode': user['refCode'],
                'status': user['status'],
                'email': contact.get('email', ''),
                'firstName': contact.get('firstName', ''),
                'lastName': contact.get('lastName', ''),
                'companyName': contact.get('companyName', ''),
                'address': contact.get('address', ''),
                'city': contact.get('city', ''),
                'country': contact.get('beneficiaryCountryCode', ''),
                'created': user.get('created', ''),
                'lastPayment': user.get('lastPayment', ''),
                'totalPaid': user.get('totalPaidAmount', 0)
            })
    return ru_payees


def create_deletion_csv(ru_payees: list) -> str:
    """Create CSV file for Tipalti support mass deletion"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"ru_payees_for_deletion_{timestamp}.csv"
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Headers for Tipalti support
        writer.writerow([
            'Payee_ID', 'RefCode', 'Email', 'FirstName', 'LastName', 
            'CompanyName', 'Status', 'Country', 'Reason_For_Deletion',
            'Total_Paid_Amount', 'Last_Payment_Date'
        ])
        
        for payee in ru_payees:
            writer.writerow([
                payee['id'],
                payee['refCode'],
                payee['email'],
                payee['firstName'],
                payee['lastName'],
                payee['companyName'],
                payee['status'],
                payee['country'],
                'Compliance requirement - Russian payees removal',
                payee['totalPaid'],
                payee['lastPayment']
            ])
    
    return csv_file


def create_support_request_text(ru_payees: list, csv_file: str) -> str:
    """Create support request text for Tipalti"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    support_text = f"""
TIPALTI SUPPORT REQUEST - MASS PAYEE DELETION
=============================================
Date: {timestamp}
Request Type: Mass Payee Deletion
Reason: Compliance requirement - Russian payees removal

SUMMARY:
- Total payees to delete: {len(ru_payees)}
- Country filter: Russian Federation (RU)
- Attached CSV: {csv_file}

STATUS BREAKDOWN:
"""
    
    status_counts = {}
    for payee in ru_payees:
        status = payee['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        support_text += f"- {status}: {count} payees\n"
    
    support_text += f"""

BUSINESS JUSTIFICATION:
Due to compliance requirements and sanctions, we need to remove all 
Russian payees from our system. This includes both active and inactive 
payees to ensure full compliance.

REQUESTED ACTIONS:
1. Permanently delete all payees listed in attached CSV
2. Ensure all payment history is archived for audit purposes
3. Block future registrations from Russian addresses
4. Confirm completion with deletion report

URGENCY: High Priority
Contact: [Your contact information]

CSV FILE ATTACHED: {csv_file}
Total records: {len(ru_payees)}
"""
    
    return support_text


def create_compliance_report(ru_payees: list) -> str:
    """Create detailed compliance report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"ru_payees_compliance_report_{timestamp}.json"
    
    # Analysis
    total_paid = sum(float(p.get('totalPaid', 0)) for p in ru_payees)
    active_count = sum(1 for p in ru_payees if p['status'] == 'ACTIVE')
    
    report = {
        "report_date": datetime.now().isoformat(),
        "summary": {
            "total_ru_payees": len(ru_payees),
            "active_payees": active_count,
            "inactive_payees": len(ru_payees) - active_count,
            "total_amount_paid": total_paid,
            "compliance_status": "REQUIRES_IMMEDIATE_ACTION"
        },
        "status_breakdown": {},
        "high_value_payees": [],  # Payees with >$1000 total
        "recent_active": [],      # Active in last 30 days
        "payees": ru_payees
    }
    
    # Status breakdown
    for payee in ru_payees:
        status = payee['status']
        report["status_breakdown"][status] = report["status_breakdown"].get(status, 0) + 1
        
        # High value payees
        if float(payee.get('totalPaid', 0)) > 1000:
            report["high_value_payees"].append({
                'refCode': payee['refCode'],
                'email': payee['email'],
                'totalPaid': payee['totalPaid']
            })
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report_file


def main():
    """Main process"""
    print("🇷🇺 TIPALTI RU PAYEES MANAGEMENT TOOL")
    print("=" * 50)
    
    # Load RU payees
    backup_file = "backup_rest_20250722_185837.json"
    print(f"📁 Loading RU payees from {backup_file}")
    
    ru_payees = load_ru_payees(backup_file)
    print(f"🎯 Found {len(ru_payees)} Russian payees")
    
    # Show breakdown
    status_counts = {}
    for payee in ru_payees:
        status = payee['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\n📊 Status breakdown:")
    for status, count in status_counts.items():
        print(f"  {status}: {count} payees")
    
    # Create management files
    print("\n📋 Creating management files...")
    
    # 1. CSV for Tipalti support
    csv_file = create_deletion_csv(ru_payees)
    print(f"✅ CSV for support: {csv_file}")
    
    # 2. Support request text
    support_text = create_support_request_text(ru_payees, csv_file)
    support_file = f"tipalti_support_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(support_file, 'w', encoding='utf-8') as f:
        f.write(support_text)
    print(f"✅ Support request: {support_file}")
    
    # 3. Compliance report
    report_file = create_compliance_report(ru_payees)
    print(f"✅ Compliance report: {report_file}")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. 📧 Email Tipalti support with: {support_file}")
    print(f"2. 📎 Attach CSV file: {csv_file}")
    print(f"3. 📊 Share compliance report: {report_file}")
    print(f"4. ⏰ Follow up for deletion confirmation")
    print(f"\n💡 Alternative: Contact your Tipalti Account Manager")
    print(f"   They can arrange mass deletion faster than support tickets")
    
    return True


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc() 