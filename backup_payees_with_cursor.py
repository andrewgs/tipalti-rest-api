#!/usr/bin/env python3
"""
Tipalti Payees Backup с пагинацией через pageCursor
Использует современный REST API метод с pageInfo.nextPageCursor
"""

import json
import sys
from datetime import datetime
from tipalti_rest_api import TipaltiRestAPI
import config_rest


def backup_all_payees_with_cursor():
    """Backup всех payees используя pageCursor пагинацию"""
    
    print("💾 BACKUP ВСЕХ PAYEES С CURSOR ПАГИНАЦИЕЙ")
    print("=" * 60)
    
    try:
        # Инициализация API клиента
        config_rest.validate_config()
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        
        print(f"🌐 Среда: {'Sandbox' if is_sandbox else 'Production'}")
        print(f"🔗 API URL: {'https://api-p.tipalti.com/api/v1' if not is_sandbox else 'https://api.sandbox.tipalti.com/api/v1'}")
        
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        
        # Получаем токен
        print("🔐 Получение OAuth токена...")
        token = api._get_access_token()
        print(f"✅ Токен получен: {token[:20]}...")
        print()
        
        # Собираем все payees через cursor пагинацию
        all_payees = []
        page_cursor = None
        page_number = 1
        total_processed = 0
        
        print("📄 Начинаем сбор payees через cursor пагинацию...")
        
        while True:
            print(f"📄 Страница {page_number}...", end=" ")
            
            # Подготавливаем параметры запроса
            params = {}
            if page_cursor:
                params['pageCursor'] = page_cursor
                print(f"(cursor: {page_cursor[:10]}...)", end=" ")
            
            try:
                # Делаем запрос к API
                response = api._make_request('GET', '/payees', params=params)
                
                # Извлекаем данные
                payees_batch = response.get('items', [])
                page_info = response.get('pageInfo', {})
                
                print(f"получено {len(payees_batch)} payees")
                
                if not payees_batch:
                    print("    ⚠️ Пустая страница - завершаем")
                    break
                
                # Добавляем к общему списку
                all_payees.extend(payees_batch)
                total_processed += len(payees_batch)
                
                # Показываем статистику страницы
                print(f"    📊 Всего собрано: {total_processed} payees")
                
                # Проверяем наличие следующей страницы
                next_cursor = page_info.get('nextPageCursor')
                
                if not next_cursor:
                    print("    ✅ Больше страниц нет - завершаем")
                    break
                
                # Подготавливаемся к следующей странице
                page_cursor = next_cursor
                page_number += 1
                
                # Защита от бесконечного цикла
                if page_number > 100:  # При 3800 payees не должно быть больше ~40 страниц
                    print("    ⚠️ Превышен лимит страниц (100) - принудительная остановка")
                    break
                    
            except Exception as e:
                print(f"❌ Ошибка на странице {page_number}: {e}")
                break
        
        print()
        print(f"📊 ИТОГО СОБРАНО:")
        print(f"  📄 Страниц обработано: {page_number}")
        print(f"  👥 Payees получено: {len(all_payees)}")
        print(f"  🔄 Общих запросов: {total_processed}")
        
        if not all_payees:
            print("❌ Не удалось получить payees")
            return False
            
        # Подготавливаем данные для сохранения
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        backup_data = {
            "metadata": {
                "timestamp": timestamp,
                "datetime": datetime.now().isoformat(),
                "total_payees": len(all_payees),
                "environment": "production" if not is_sandbox else "sandbox",
                "api_method": "cursor_pagination",
                "api_base_url": api.base_url,
                "pages_processed": page_number,
                "backup_type": "full_payees_with_cursor"
            },
            "payees": all_payees
        }
        
        # Сохраняем в файл
        filename = f"payees_backup_cursor_{timestamp}.json"
        
        print(f"💾 Сохранение в файл: {filename}")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        print()
        print("🎉 BACKUP ЗАВЕРШЕН УСПЕШНО!")
        print("=" * 60)
        print(f"📁 Файл: {filename}")
        print(f"👥 Payees: {len(all_payees)}")
        print(f"📄 Страниц: {page_number}")
        print(f"⏰ Время: {backup_data['metadata']['datetime']}")
        print(f"🌐 Среда: {backup_data['metadata']['environment']}")
        print(f"🔄 Метод: cursor пагинация")
        
        # Показываем примеры данных
        if all_payees:
            print()
            print("📋 ПРИМЕР ДАННЫХ:")
            sample_payee = all_payees[0]
            print(f"  🆔 ID: {sample_payee.get('id', 'N/A')}")
            print(f"  🔢 RefCode: {sample_payee.get('refCode', 'N/A')}")
            print(f"  📊 Status: {sample_payee.get('status', 'N/A')}")
            print(f"  📛 Name: {sample_payee.get('name', 'N/A')}")
            
            contact = sample_payee.get('contactInformation', {})
            if contact:
                print(f"  📧 Email: {contact.get('email', 'N/A')}")
                print(f"  🌍 Country: {contact.get('beneficiaryCountryCode', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Основная функция"""
    
    print("🚀 TIPALTI PAYEES BACKUP")
    print("📡 Использует REST API с cursor пагинацией")
    print("🔗 Метод: GET /payees с pageCursor параметром")
    print()
    
    success = backup_all_payees_with_cursor()
    
    if success:
        print("\n✅ Backup выполнен успешно!")
        sys.exit(0)
    else:
        print("\n❌ Backup завершился с ошибкой!")
        sys.exit(1)


if __name__ == "__main__":
    main() 