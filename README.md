# Tipalti REST API Integration

🚀 **Modern REST API system for Tipalti with hybrid SOAP/REST architecture, JSON responses, and production-ready backup functionality.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![REST API](https://img.shields.io/badge/API-REST%2BSOAP-orange.svg)](https://documentation.tipalti.com)

## 🌟 Features

- **🔄 Hybrid REST/SOAP Architecture**: Modern REST interface with SOAP backend
- **📱 JSON Responses**: Clean, structured JSON data format  
- **🔍 Type Safety**: Python dataclasses for payee objects
- **🛡️ Production Ready**: IP whitelisting, error handling, monitoring
- **💾 Automated Backup**: Complete payee data backup system
- **📊 Health Monitoring**: API status checks and diagnostics
- **🧪 Comprehensive Testing**: Multiple test scripts and validation tools

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | API health check |
| `GET` | `/payees` | List all payees |
| `GET` | `/payees/{id}` | Get single payee details |
| `POST` | `/backup` | Create payee backup |

## 🔧 Installation

### Prerequisites
- Python 3.8+
- Tipalti account with API access
- Valid Tipalti credentials (Payer name + Master key)

### Setup

```bash
# Clone repository
git clone https://github.com/andrewgs/tipalti-rest-api.git
cd tipalti-rest-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Tipalti credentials
```

### Environment Configuration

Create `.env` file:
```bash
# Tipalti API Configuration
TIPALTI_PAYER_NAME=your_payer_name
TIPALTI_MASTER_KEY=your_master_key
TIPALTI_SANDBOX=false  # true for sandbox, false for production
```

## 🚀 Quick Start

### REST API Usage

```python
from tipalti_hybrid_api import create_api_client

# Create API client
api = create_api_client()

# Health check
health = api.health_check()
print(f"API Status: {health['status']}")

# Get payee details
payee = api.get_payee('12345')
if payee:
    print(f"Payee: {payee.name} ({payee.email})")

# List payees
payees = api.list_payees(limit=50)
print(f"Found {len(payees)} payees")

# Create backup
backup = api.backup_all_payees()
print(f"Backup saved: {backup['filename']}")
```

### Command Line Tools

```bash
# Health check & API demo
python rest_api_demo.py

# Create production backup
python backup_production_final.py

# Monitor API status
python monitor_ip_fix.py

# Test specific payee IDs
python test_real_payees.py
```

## 📊 Response Format

### Payee Object
```json
{
  "id": "12345",
  "name": "John Doe",
  "email": "john@company.com", 
  "status": "active",
  "payment_method": "PayPal",
  "created_date": "2023-01-15",
  "raw_data": {...}
}
```

### Backup Response
```json
{
  "success": true,
  "filename": "backup_20250720_141908.json",
  "total_payees": 3857,
  "data": {
    "timestamp": "2025-07-20T14:19:08.159194",
    "environment": "production",
    "payer_name": "YourPayer",
    "payees": [...]
  }
}
```

## 🏗️ Architecture

```
REST Client → Hybrid API → SOAP Backend → Tipalti
     ↓           ↓              ↓
  JSON        Python       XML/SOAP
```

**Benefits:**
- **Modern Interface**: REST + JSON for developers
- **Reliable Backend**: Proven SOAP API infrastructure
- **Best of Both**: REST usability + SOAP stability

## 📁 Project Structure

```
tipalti-rest-api/
├── 🎯 Core API Files
│   ├── tipalti_hybrid_api.py      # Main REST API wrapper
│   ├── tipalti_api.py             # Legacy SOAP client  
│   ├── config.py                  # Configuration management
│   └── requirements.txt           # Dependencies
│
├── 💾 Backup & Production Tools  
│   ├── backup_production_final.py # Production backup script
│   ├── backup_rest.py             # REST backup interface
│   └── backup_users.py            # Legacy SOAP backup
│
├── 🧪 Testing & Monitoring
│   ├── rest_api_demo.py          # Interactive API demo
│   ├── test_real_payees.py       # Real payee ID testing
│   ├── monitor_ip_fix.py         # IP whitelist monitoring
│   └── troubleshoot_ip.py        # IP diagnostic tools
│
├── 📚 Documentation
│   ├── README.md                 # This file
│   ├── README_REST.md            # REST API documentation  
│   ├── fix_ip_whitelist.md       # IP whitelist guide
│   └── tipalti_support_email.md  # Support email template
│
└── 🔧 Configuration
    ├── .env.example              # Environment template
    ├── .gitignore                # Git ignore rules
    └── venv/                     # Virtual environment
```

## 🛠️ Development

### Key Components

1. **TipaltiHybridAPI** (`tipalti_hybrid_api.py`)
   - Modern REST interface
   - Automatic SOAP translation
   - Type-safe responses

2. **PayeeInfo Dataclass**
   - Structured payee data
   - Type validation
   - JSON serialization

3. **Production Backup System**
   - Complete data export
   - Metadata tracking
   - Error recovery

### Testing

```bash
# Test API connection
python test_real_payees.py

# Test REST endpoints
python rest_api_demo.py

# Monitor system health
python backup_with_ip_fix.py
```

## 🔐 Security & IP Whitelisting

### Tipalti IP Whitelist Setup
1. Login to Tipalti Dashboard
2. Go to **Settings** → **API Configuration**
3. Add your IP address with:
   - Source type: **API**
   - Status: **Active**
   - Address type: **DNS IP/Host**

### Troubleshooting IP Issues
```bash
# Check current IP
python backup_with_ip_fix.py

# Monitor whitelist status
python monitor_ip_fix.py

# Comprehensive diagnostics
python troubleshoot_ip.py
```

## 📈 Production Usage

### Backup 3,857+ Payees
```bash
# Full production backup
python backup_production_final.py

# Expected output:
# ✅ Credentials verified
# ✅ API health check passed  
# 💾 Backup saved: backup_verified_20250720.json
# 📊 Total payees: 3,857
```

### Automated Monitoring
```bash
# Continuous health monitoring
python monitor_ip_fix.py

# Will check every 60 seconds until API access is restored
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

### Tipalti Support
- **Email**: support@tipalti.com
- **Documentation**: https://documentation.tipalti.com
- **Template email**: See `tipalti_support_email.md`

### Common Issues
- **InvalidPayerIpAddress**: Check IP whitelist configuration
- **EncryptionKeyFailedValidation**: Verify credentials
- **Connection timeout**: Check network and firewall

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for production payee data management
- Supports 3,857+ active payees
- Modern REST architecture over legacy SOAP
- Production-tested and battle-ready

---

**🚀 Ready to backup your Tipalti payees with modern REST API!** 