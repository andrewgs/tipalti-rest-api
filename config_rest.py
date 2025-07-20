#!/usr/bin/env python3
"""
Tipalti REST API Configuration
OAuth 2.0 Client Credentials
"""

import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed, using environment variables directly")

# Tipalti REST API OAuth Configuration  
CLIENT_ID = os.getenv('TIPALTI_CLIENT_ID')
CLIENT_SECRET = os.getenv('TIPALTI_CLIENT_SECRET')
IS_SANDBOX = os.getenv('TIPALTI_SANDBOX', 'true').lower() == 'true'

# Cleanup Configuration
CUTOFF_DATE = '2025-01-01'

def validate_config():
    """Validate that required configuration is present"""
    missing = []
    
    if not CLIENT_ID:
        missing.append('TIPALTI_CLIENT_ID')
    
    if not CLIENT_SECRET:
        missing.append('TIPALTI_CLIENT_SECRET')
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    return True

def get_validated_config() -> tuple[str, str, bool]:
    """Get validated configuration values"""
    validate_config()
    # At this point we know the values are not None due to validation
    # Type assertion since we've validated they exist
    assert CLIENT_ID is not None, "CLIENT_ID should not be None after validation"
    assert CLIENT_SECRET is not None, "CLIENT_SECRET should not be None after validation"
    return CLIENT_ID, CLIENT_SECRET, IS_SANDBOX 