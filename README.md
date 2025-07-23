# Tipalti API Integration Suite

🚀 **Полная система для работы с Tipalti API: backup, cleanup и restore payees данных**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![REST API](https://img.shields.io/badge/API-Official%20REST%20v1-green.svg)](https://documentation.tipalti.com/reference/get_api-v1-payees)

## 🎯 Основные функции

| Функция | REST API | SOAP API | Описание |
|---------|----------|----------|----------|
| **📥 Backup** | `backup_users_rest.py` | `backup_users.py` | Полный backup всех payees |
| **🧹 Cleanup** | `cleanup_users_rest.py` | `cleanup_users.py` | Удаление неактивных payees |
| **🔄 Restore** | Планируется | Планируется | Восстановление данных |

## 🚀 Рекомендуемый подход

### ✅ REST API (Основной)
```bash
# Получить OAuth2 credentials в Tipalti Dashboard
# Добавить в .env:
# TIPALTI_CLIENT_ID=your_client_id
# TIPALTI_CLIENT_SECRET=your_client_secret

python backup_users_rest.py       # Backup через REST API
python cleanup_users_rest.py      # Cleanup через REST API
```

### 🔧 SOAP API (Legacy)
```bash
python backup_users.py            # Backup через SOAP API
python cleanup_users.py           # Cleanup через SOAP API
```

## 📋 API файлы

### Основные API клиенты
- **`tipalti_rest_api.py`** - Официальный REST API v1 с OAuth2
- **`tipalti_api.py`** - Legacy SOAP API
- **`tipalti_hybrid_api.py`** - Гибридный подход (REST interface + SOAP backend)
- **`tipalti_rest_simple.py`** - Упрощенный REST клиент

### Конфигурация
- **`config_rest.py`** - Конфигурация для REST API
- **`config.py`** - Конфигурация для SOAP API

## 🔧 Установка

```bash
# Клонировать репозиторий
git clone <repository-url>
cd tipalti

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Настроить окружение
cp .env.example .env
# Отредактировать .env с вашими credentials
```

## 🔐 Настройка credentials

### REST API (рекомендуется)
```bash
# В Tipalti Dashboard:
# 1. Settings → API Configuration
# 2. Create OAuth2 Application
# 3. Copy client_id и client_secret

# В .env файле:
TIPALTI_CLIENT_ID=your_client_id
TIPALTI_CLIENT_SECRET=your_client_secret
TIPALTI_SANDBOX=false
```

### SOAP API (legacy)
```bash
# В .env файле:
TIPALTI_PAYER_NAME=your_payer_name
TIPALTI_MASTER_KEY=your_master_key
TIPALTI_SANDBOX=false
```

## 📊 Использование

### Backup payees данных
```bash
# REST API (рекомендуется)
python backup_users_rest.py

# Создаст файл: backup_rest_YYYYMMDD_HHMMSS.json
# Содержит все payees с полной информацией
```

### Cleanup неактивных payees
```bash
# REST API (рекомендуется) 
python cleanup_users_rest.py

# Найдет и предложит удалить неактивных payees
# Поддерживает dry-run режим
```

### Production backup
```bash
# Полный production backup
python backup_production_final.py

# Создает verified backup с проверкой credentials
```

## 📖 Документация

- **[REST API Reference](https://documentation.tipalti.com/reference/get_api-v1-payees)** - Официальная документация REST API
- **[README_REST.md](README_REST.md)** - Подробная документация по REST API
- **[SECURITY.md](SECURITY.md)** - Рекомендации по безопасности
- **[CHANGELOG.md](CHANGELOG.md)** - История изменений
- **[fix_ip_whitelist.md](fix_ip_whitelist.md)** - Решение проблем с IP whitelisting

## 🔍 Структура проекта

```
tipalti/
├── API клиенты
│   ├── tipalti_rest_api.py     # REST API v1 (основной)
│   ├── tipalti_api.py          # SOAP API (legacy)
│   ├── tipalti_hybrid_api.py   # Гибридный подход
│   └── tipalti_rest_simple.py  # Упрощенный REST
├── Основные функции
│   ├── backup_users_rest.py    # REST backup
│   ├── backup_users.py         # SOAP backup  
│   ├── cleanup_users_rest.py   # REST cleanup
│   └── cleanup_users.py        # SOAP cleanup
├── Конфигурация
│   ├── config_rest.py          # REST config
│   └── config.py               # SOAP config
└── Документация
    ├── README.md               # Главная документация
    ├── README_REST.md          # REST API документация
    └── SECURITY.md             # Безопасность
```

## 🚨 Важные замечания

1. **REST API - приоритет**: Используйте REST API для новых проектов
2. **OAuth2 credentials**: Требуются для REST API  
3. **IP Whitelisting**: Может потребоваться для production
4. **Rate Limiting**: REST API имеет лимиты запросов
5. **Backup перед cleanup**: Всегда делайте backup перед удалением данных

## 🤝 Поддержка

- **Официальная поддержка**: [tipalti_support_email.md](tipalti_support_email.md)
- **IP Whitelisting**: [fix_ip_whitelist.md](fix_ip_whitelist.md)
- **GitHub Issues**: Создавайте issues для вопросов

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE) файл 