#!/usr/bin/env python3
"""
Test Tipalti REST API connection
Quick verification that OAuth 2.0 credentials work
"""

import sys
from tipalti_rest_api import TipaltiRestAPI
import config_rest


def test_rest_api():
    """Test REST API connection step by step"""
    
    print("🧪 Tipalti REST API Connection Test")
    print("=" * 50)
    
    try:
        # Step 1: Check configuration
        print("1. 📋 Checking configuration...")
        config_rest.validate_config()
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        
        print(f"   ✅ Client ID: {client_id}")
        print(f"   ✅ Client Secret: [Hidden - {len(client_secret)} chars]")
        print(f"   ✅ Environment: {'Sandbox' if is_sandbox else 'Production'}")
        
        # Step 2: Create API client
        print("\n2. 🔗 Creating API client...")
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        print(f"   ✅ API Base URL: {api.base_url}")
        print(f"   ✅ Auth URL: {api.auth_url}")
        
        # Step 3: Test OAuth authentication
        print("\n3. 🔐 Testing OAuth 2.0 authentication...")
        try:
            token = api._get_access_token()
            print(f"   ✅ Access token obtained: {token[:20]}...")
            print(f"   ✅ Token expires at: {api.token_expires_at}")
        except Exception as e:
            print(f"   ❌ OAuth authentication failed: {e}")
            return False
        
        # Step 4: Test API endpoints
        print("\n4. 👥 Testing payees endpoint...")
        try:
            payees = api.get_payees_list(limit=3)  # Just get a few for testing
            print(f"   ✅ API call successful")
            print(f"   ✅ Found {len(payees)} payees")
            
            if payees:
                print("\n   📋 Sample payee data:")
                sample = payees[0]
                for key, value in list(sample.items())[:5]:  # Show first 5 fields
                    print(f"      {key}: {value}")
            
        except Exception as e:
            print(f"   ❌ API endpoint test failed: {e}")
            return False
        
        print(f"\n🎉 All tests passed! REST API is working correctly.")
        print(f"🚀 Ready to run: python backup_users_rest.py")
        return True
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Please update .env with your OAuth 2.0 credentials:")
        print("   TIPALTI_CLIENT_ID=your_client_id")
        print("   TIPALTI_CLIENT_SECRET=your_client_secret") 
        print("   TIPALTI_SANDBOX=true")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def show_migration_info():
    """Show information about migrating from SOAP to REST"""
    
    print("\n" + "="*60)
    print("📖 SOAP to REST API Migration Guide")
    print("="*60)
    print()
    print("🔄 Changes made:")
    print("  • Replaced HMAC authentication with OAuth 2.0")
    print("  • Modern REST endpoints instead of SOAP XML") 
    print("  • JSON responses instead of XML parsing")
    print("  • Automatic token management and refresh")
    print("  • Built-in pagination handling")
    print()
    print("🆕 New files created:")
    print("  • tipalti_rest_api.py     - REST API client")
    print("  • config_rest.py          - OAuth configuration")
    print("  • backup_users_rest.py    - REST backup script")
    print("  • cleanup_users_rest.py   - REST cleanup script")
    print()
    print("🔧 New environment variables needed:")
    print("  TIPALTI_CLIENT_ID=your_client_id_from_dashboard")
    print("  TIPALTI_CLIENT_SECRET=your_client_secret_from_dashboard")
    print("  TIPALTI_SANDBOX=true")
    print()
    print("📖 Get credentials from:")
    print("  https://documentation.tipalti.com/reference/quick-start")
    print("  → Tipalti Dashboard → Settings → API Integration")
    print()


if __name__ == "__main__":
    show_migration_info()
    
    if test_rest_api():
        print("\n✨ REST API migration completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 REST API test failed - check your credentials")
        sys.exit(1) 