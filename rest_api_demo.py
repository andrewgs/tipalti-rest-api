#!/usr/bin/env python3
"""
Tipalti REST API Demo
Interactive demonstration of modern REST endpoints
"""

from tipalti_hybrid_api import create_api_client
import json
from datetime import datetime


def rest_api_demo():
    """Interactive REST API demonstration"""
    
    print("🎯 Tipalti REST API Demo")
    print("=" * 50)
    print("🚀 Modern REST API Interface")
    print("📱 JSON Responses • 🔄 HTTP Methods • ⚡ Fast")
    print()
    
    try:
        # Create REST API client
        api = create_api_client()
        print()
        
        print("📋 Available REST Endpoints:")
        print("  GET  /health           - API health check")
        print("  GET  /payees           - List all payees") 
        print("  GET  /payees/{id}      - Get single payee")
        print("  POST /backup           - Create backup")
        print()
        
        # Demo endpoints
        endpoints = [
            ("GET /health", lambda: api.health_check()),
            ("GET /payees/{id}", lambda: api.get_payee("test")),
            ("GET /payees", lambda: api.list_payees(limit=3)),
            ("POST /backup", lambda: api.backup_all_payees())
        ]
        
        for i, (endpoint, func) in enumerate(endpoints, 1):
            print(f"{i}. Testing {endpoint}")
            print("-" * 30)
            
            try:
                result = func()
                
                if isinstance(result, dict):
                    # Show JSON response
                    print("📄 Response (JSON):")
                    print(json.dumps(result, indent=2, default=str)[:500] + "...")
                else:
                    print(f"📄 Response: {result}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                
            print()
            
            # Pause between requests
            import time
            time.sleep(1)
        
        print("✅ REST API Demo completed!")
        return True
        
    except Exception as e:
        print(f"💥 Demo failed: {e}")
        return False


def show_rest_features():
    """Show modern REST API features"""
    
    print("\n🌟 Modern REST API Features:")
    print("=" * 50)
    
    features = [
        "🔄 HTTP Methods (GET, POST, PUT, DELETE)",
        "📱 JSON Request/Response bodies", 
        "⚡ Fast and lightweight",
        "🔍 RESTful resource URLs (/payees, /payments)",
        "📊 Structured error responses",
        "🏗️  Standard HTTP status codes",
        "🛡️  Built-in authentication",
        "📋 Automatic pagination",
        "🎯 Type-safe payee objects",
        "💾 Modern backup format"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print()
    print("🔧 Usage Examples:")
    print("  api.get_payee('user123')      # GET /payees/user123") 
    print("  api.list_payees(limit=50)     # GET /payees?limit=50")
    print("  api.backup_all_payees()       # POST /backup")
    print("  api.health_check()            # GET /health")


if __name__ == "__main__":
    success = rest_api_demo()
    show_rest_features()
    
    if success:
        print(f"\n🎉 REST API is working!")
        print(f"🚀 Run: python backup_rest.py")
    else:
        print(f"\n💡 Update credentials for full functionality") 