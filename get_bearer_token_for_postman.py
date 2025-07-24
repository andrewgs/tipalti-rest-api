#!/usr/bin/env python3
"""
Получить Bearer токен для тестирования Tipalti REST API в Postman
"""

from tipalti_rest_api import TipaltiRestAPI
import config_rest
from datetime import datetime

def get_token_for_postman():
    """Получить bearer токен для использования в Postman"""
    
    print("🔐 ПОЛУЧЕНИЕ BEARER TOKEN ДЛЯ POSTMAN")
    print("=" * 60)
    
    try:
        # Получаем конфигурацию
        config_rest.validate_config()
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        
        print(f"🌐 Среда: {'Sandbox' if is_sandbox else 'Production'}")
        print(f"🆔 Client ID: {client_id}")
        print(f"🔑 Client Secret: {client_secret[:8]}{'*' * (len(client_secret)-8)}")
        print()
        
        # Создаем API клиент
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        
        # Получаем токен
        print("🔄 Получение Bearer токена...")
        token = api._get_access_token()
        
        print("✅ BEARER TOKEN ПОЛУЧЕН:")
        print("=" * 60)
        print(f"Bearer {token}")
        print("=" * 60)
        print()
        
        print("🔐 ИНФОРМАЦИЯ О ТОКЕНЕ:")
        print(f"  📏 Длина: {len(token)} символов")
        print(f"  ⏰ Действителен до: {api.token_expires_at}")
        print(f"  ⏳ Осталось времени: {api.token_expires_at - datetime.now()}")
        
        print()
        print("📡 НАСТРОЙКА POSTMAN:")
        print("  1. Откройте Postman")
        print("  2. Создайте новый запрос")
        print("  3. В Authorization Tab выберите:")
        print("     Type: Bearer Token")
        print(f"     Token: {token}")
        print("  4. ИЛИ в Headers добавьте:")
        print(f"     Key: Authorization")
        print(f"     Value: Bearer {token}")
        print("  5. Установите URL:")
        if is_sandbox:
            print("     https://api.sandbox.tipalti.com/api/v1/payees")
        else:
            print("     https://api-p.tipalti.com/api/v1/payees")
        print("  6. Метод: GET")
        
        print()
        print("🧪 ТЕСТОВЫЕ ENDPOINTS:")
        base_url = api.base_url
        print(f"  📋 Список payees: GET {base_url}/payees")
        print(f"  🔍 Конкретный payee: GET {base_url}/payees/{{payee_id}}")
        print(f"  📊 С параметрами: GET {base_url}/payees?status=ACTIVE&limit=10")
        print(f"  📈 С пагинацией: GET {base_url}/payees?limit=100&offset=0")
        
        print()
        print("⚠️ ВАЖНО:")
        print("  • Токен действителен примерно 1 час")
        print("  • После истечения запустите скрипт заново")
        print("  • НЕ передавайте токен третьим лицам")
        print("  • Добавьте Content-Type: application/json для POST/PATCH")
        
        return token
        
    except Exception as e:
        print(f"❌ Ошибка получения токена: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Основная функция"""
    token = get_token_for_postman()
    
    if token:
        print("\n🎉 ГОТОВО! Теперь можете тестировать API в Postman")
        print("\n💡 СОВЕТ: Скопируйте токен из вывода выше")
    else:
        print("\n❌ Не удалось получить токен")

if __name__ == "__main__":
    main() 