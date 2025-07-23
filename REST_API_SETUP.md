# Настройка REST API для Tipalti

🎯 **Подготовка к работе с официальным REST API Tipalti для backup ваших 3K+ payees**

## 📋 Что нужно сделать

1. **Получить OAuth2 credentials в Tipalti Dashboard**
2. **Настроить .env файл**  
3. **Протестировать подключение**
4. **Запустить backup**

## 🔧 Шаг 1: Получение OAuth2 Credentials

### 1.1 Войдите в Tipalti Dashboard
- **Production**: https://payer.tipalti.com/
- **Sandbox**: https://payer.sandbox.tipalti.com/

### 1.2 Перейдите в API Settings
1. В левом меню: **Settings** → **API Configuration**
2. Найдите секцию **"OAuth 2.0 Applications"** или **"REST API"**
3. Если секции нет - обратитесь в поддержку Tipalti

### 1.3 Создайте OAuth2 Application
1. Нажмите **"Create Application"** или **"Add OAuth2 App"**
2. Заполните форму:
   - **Name**: `Backup Script` (или любое описательное имя)
   - **Grant Type**: `Client Credentials`
   - **Scopes**: `read` (минимум для чтения payees)
   - **Description**: `API for payees backup and management`

### 1.4 Сохраните credentials
После создания приложения вы получите:
- **Client ID** - публичный идентификатор
- **Client Secret** - секретный ключ (показывается только один раз!)

⚠️ **ВАЖНО**: Сохраните Client Secret сразу - он больше не будет показан!

## 🔐 Шаг 2: Настройка .env файла

Добавьте OAuth2 credentials в ваш `.env` файл:

```bash
# REST API OAuth2 Credentials
TIPALTI_CLIENT_ID=your_actual_client_id_here
TIPALTI_CLIENT_SECRET=your_actual_client_secret_here
TIPALTI_SANDBOX=false

# Existing SOAP credentials (оставьте как есть)
TIPALTI_PAYER_NAME=Uplify
TIPALTI_MASTER_KEY=your_existing_master_key
```

### Пример корректного .env файла:
```bash
# REST API OAuth2 - для новых методов
TIPALTI_CLIENT_ID=abc123def456ghi789
TIPALTI_CLIENT_SECRET=xyz789uvw456rst123qwe456asd789
TIPALTI_SANDBOX=false

# SOAP API - legacy (оставляем для совместимости)  
TIPALTI_PAYER_NAME=Uplify
TIPALTI_MASTER_KEY=your_existing_key_here
```

## 🧪 Шаг 3: Тестирование подключения

### 3.1 Запуск теста REST API
```bash
# Активировать окружение
source venv/bin/activate

# Запустить тест подключения
python -c "
from tipalti_rest_api import TipaltiRestAPI
import config_rest

try:
    client_id, client_secret, is_sandbox = config_rest.get_validated_config()
    api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
    
    print('🔐 Getting OAuth token...')
    token = api._get_access_token()
    print(f'✅ Success! Token: {token[:20]}...')
    
    print('👥 Testing payees endpoint...')
    payees = api.get_payees_list(limit=3)
    print(f'✅ Found {len(payees)} payees')
    
    print('🎉 REST API готов к работе!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    print('💡 Check your OAuth2 credentials in .env file')
"
```

### 3.2 Ожидаемый результат
```
🔐 Getting OAuth token...
✅ Success! Token: eyJ0eXAiOiJKV1QiLCJhb...
👥 Testing payees endpoint...
✅ Found 3 payees
🎉 REST API готов к работе!
```

## 🚀 Шаг 4: Запуск backup

После успешного тестирования:

```bash
# Backup всех payees через REST API
python backup_users_rest.py
```

Ожидаемый результат:
```
🔗 Connecting to Tipalti REST API...
🌐 Environment: Production
🔐 Authenticating with OAuth 2.0...
✅ Access token obtained: eyJ0eXAiOiJKV1QiLCJ...
👥 Fetching all users...
📊 Found 3247 users

🎉 Backup completed successfully!
📁 Saved 3247 users to: backup_rest_20250720_160000.json
🔧 Environment: Production
🚀 API Type: REST API v1 with OAuth 2.0
```

## 🔍 Структура backup файла

REST API backup создает файл вида:
```json
{
  "backup_date": "2025-07-20T16:00:00.000000",
  "backup_type": "rest_api",
  "total_users": 3247,
  "environment": "production", 
  "api_type": "REST API v1",
  "users": [
    {
      "id": "payee_123",
      "name": "John Doe",
      "email": "john@company.com",
      "status": "active",
      "created_date": "2023-01-15T10:30:00Z",
      "payment_methods": ["paypal", "ach"],
      // ... полная информация о payee
    }
  ]
}
```

## ❓ Возможные проблемы

### Client ID/Secret не работают
1. Проверьте что credentials скопированы правильно
2. Убедитесь что приложение активно в Dashboard
3. Проверьте что используете правильные scopes

### "Invalid scope" ошибка
1. В Dashboard добавьте scope `read` для приложения
2. Может потребоваться `write` для cleanup операций

### "Application not found"
1. Проверьте Client ID 
2. Убедитесь что приложение создано в правильной среде (Production/Sandbox)

### Rate Limiting
REST API имеет лимиты:
- **100 запросов/минуту** для большинства endpoints
- **10 запросов/секунду** максимум

## 📞 Поддержка

Если возникли проблемы:

1. **Tipalti Support**: support@tipalti.com
2. **Тема письма**: "REST API OAuth2 Setup - Payee Backup"
3. **Информация для включения**:
   - Ваш Payer Name
   - Client ID (НЕ включайте Client Secret!)
   - Описание проблемы

## ✅ Checklist

- [ ] Вошел в Tipalti Dashboard
- [ ] Создал OAuth2 Application
- [ ] Скопировал Client ID и Client Secret
- [ ] Обновил .env файл
- [ ] Протестировал подключение
- [ ] Запустил успешный backup
- [ ] Проверил backup файл

После выполнения всех шагов ваша система будет готова для работы с официальным REST API Tipalti! 🚀 