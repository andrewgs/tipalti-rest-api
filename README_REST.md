# Tipalti REST API

🚀 Modern REST API interface for Tipalti with JSON responses and HTTP methods.

## 🌟 Features

- **REST Endpoints**: GET, POST, PUT, DELETE
- **JSON Responses**: Structured, type-safe data
- **Modern Architecture**: Hybrid REST/SOAP design
- **Health Checks**: API monitoring and status
- **Automatic Backup**: JSON backup with timestamps
- **Type Safety**: PayeeInfo dataclasses
- **Error Handling**: Structured error responses

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | API health check |
| `GET` | `/payees` | List all payees |
| `GET` | `/payees/{id}` | Get single payee |
| `POST` | `/backup` | Create backup |

## 🔧 Installation

```bash
# Install dependencies
pip install requests python-dotenv lxml

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

## 💫 Quick Start

### REST API Client

```python
from tipalti_hybrid_api import create_api_client

# Create client
api = create_api_client()

# Health check
health = api.health_check()
print(health['status'])  # 'healthy'

# Get payee
payee = api.get_payee('user123')
print(payee.name)

# List payees
payees = api.list_payees(limit=50)

# Create backup
backup = api.backup_all_payees()
print(f"Saved: {backup['filename']}")
```

### Command Line

```bash
# Run backup
python backup_rest.py

# API demo
python rest_api_demo.py

# Test connection
python tipalti_hybrid_api.py
```

## 📊 Response Format

### Payee Object
```json
{
  "id": "user123",
  "name": "John Doe", 
  "email": "john@example.com",
  "status": "active",
  "payment_method": "PayPal",
  "raw_data": { ... }
}
```

### Health Check
```json
{
  "status": "healthy",
  "timestamp": "2025-07-20T14:04:57.002985",
  "environment": "sandbox",
  "payer_name": "UPLIFY",
  "authentication": "working"
}
```

### Backup Response
```json
{
  "success": true,
  "filename": "backup_hybrid_20250720_140503.json",
  "total_payees": 42,
  "data": {
    "timestamp": "2025-07-20T14:05:03.254205",
    "environment": "sandbox",
    "api_type": "hybrid_rest_soap",
    "payees": [...]
  }
}
```

## ⚡ Architecture

This is a **Hybrid REST API** that provides modern REST interface while using SOAP internally:

```
REST Client → Hybrid API → SOAP Backend → Tipalti
     ↓           ↓              ↓
  JSON        Python       XML/SOAP
```

Benefits:
- **Modern Interface**: REST + JSON for developers
- **Reliable Backend**: Proven SOAP API underneath  
- **Best of Both**: REST usability + SOAP stability

## 🛠️ Configuration

Create `.env`:
```bash
# Tipalti API Configuration
TIPALTI_PAYER_NAME=your_payer_name
TIPALTI_MASTER_KEY=your_master_key
TIPALTI_SANDBOX=true
```

## 🔍 Error Handling

```python
try:
    payee = api.get_payee('user123')
    if payee:
        print(f"Found: {payee.name}")
    else:
        print("Payee not found")
except Exception as e:
    print(f"API Error: {e}")
```

## 📁 File Structure

```
tipalti-rest/
├── tipalti_hybrid_api.py   # Hybrid REST/SOAP client
├── backup_rest.py          # Modern backup script
├── rest_api_demo.py        # Interactive demo
├── config.py               # Configuration helper
├── .env                    # Environment variables
└── README_REST.md          # This file
```

## 🎯 Examples

See `rest_api_demo.py` for interactive examples of all endpoints.

---

**🚀 Modern REST API ready to use!** 