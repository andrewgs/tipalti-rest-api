#!/usr/bin/env python3
"""
Tipalti REST API Backup Script
Modern REST API interface with JSON responses
"""

import sys
from datetime import datetime
from tipalti_hybrid_api import TipaltiHybridAPI, create_api_client


def main():
    """Run REST API backup"""
    print("🚀 Tipalti REST API Backup")
    print("=" * 50)
    print("🔗 Modern REST API with JSON responses")
    print("📡 Using hybrid SOAP/REST architecture")
    print()

    try:
        # Create REST API client
        api = create_api_client()
        print()

        # Health check
        print("🔍 Health Check...")
        health = api.health_check()
        print()

        if health['status'] != 'healthy':
            print("❌ API unhealthy - cannot proceed")
            sys.exit(1)

        # Create backup using REST API
        print("💾 Creating backup via REST API...")
        backup_result = api.backup_all_payees()

        if backup_result['success']:
            print("\n🎉 REST API backup completed!")
            print(f"📁 File: {backup_result['filename']}")
            print(f"📊 Total payees: {backup_result['total_payees']}")
            print(f"🗓️  Timestamp: {backup_result['data']['timestamp']}")
            print(f"🌐 Environment: {backup_result['data']['environment']}")
            print(f"🏢 Payer: {backup_result['data']['payer_name']}")
            print(f"⚡ API Type: {backup_result['data']['api_type']}")
        else:
            print("❌ Backup failed")
            sys.exit(1)

    except Exception as e:
        print(f"💥 Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 