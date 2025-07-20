import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed, using environment variables directly")

# Tipalti API Configuration
PAYER_NAME = os.getenv('TIPALTI_PAYER_NAME')
MASTER_KEY = os.getenv('TIPALTI_MASTER_KEY')
IS_SANDBOX = os.getenv('TIPALTI_SANDBOX', 'true').lower() == 'true'

# Cleanup Configuration
CUTOFF_DATE = '2025-01-01'

def validate_config():
    """Validate that required configuration is present"""
    missing = []
    
    if not PAYER_NAME:
        missing.append('TIPALTI_PAYER_NAME')
    
    if not MASTER_KEY:
        missing.append('TIPALTI_MASTER_KEY')
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    return True

def get_validated_config() -> tuple[str, str, bool]:
    """Get validated configuration values"""
    validate_config()
    # At this point we know the values are not None due to validation
    # Type assertion since we've validated they exist
    assert PAYER_NAME is not None, "PAYER_NAME should not be None after validation"
    assert MASTER_KEY is not None, "MASTER_KEY should not be None after validation"
    return PAYER_NAME, MASTER_KEY, IS_SANDBOX 