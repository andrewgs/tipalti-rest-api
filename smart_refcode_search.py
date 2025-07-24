#!/usr/bin/env python3
"""
Умный поиск payee по refCode с диагностикой
Ищем refCode = 22737 с проверкой пагинации
"""

from tipalti_rest_api import TipaltiRestAPI
import config_rest
import json

def smart_search_refcode(api, target_refcode="22737"):
    """Умный поиск с диагностикой"""
    
    print(f"🔍 УМНЫЙ ПОИСК refCode = {target_refcode}")
    print("=" * 60)
    
    all_refcodes = set()  # Для отслеживания дубликатов
    found_payee = None
    limit = 100
    offset = 0
    page = 1
    empty_pages = 0
    max_empty_pages = 3
    
    print(f"🎯 Целевой refCode: {target_refcode}")
    print(f"📊 Лимит на страницу: {limit}")
    print()
    
    while True:
        print(f"📄 Страница {page} (offset: {offset})...", end=" ")
        
        try:
            params = {
                'limit': limit,
                'offset': offset
            }
            
            response = api._make_request('GET', '/payees', params=params)
            payees = response.get('items', [])
            total_count = response.get('totalCount', 0)
            
            print(f"получено {len(payees)} payees (API говорит всего: {total_count})")
            
            if not payees:
                empty_pages += 1
                print(f"    ⚠️ Пустая страница! ({empty_pages}/{max_empty_pages})")
                
                if empty_pages >= max_empty_pages:
                    print("    🛑 Слишком много пустых страниц - останавливаемся")
                    break
                
                offset += limit
                page += 1
                continue
            else:
                empty_pages = 0
            
            # Анализ страницы
            page_refcodes = []
            for payee in payees:
                ref_code = payee.get('refCode', '')
                
                if ref_code:
                    if ref_code in all_refcodes:
                        print(f"    🔄 ДУБЛИКАТ: refCode {ref_code} уже был!")
                    else:
                        all_refcodes.add(ref_code)
                        page_refcodes.append(ref_code)
                    
                    # Проверяем целевой refCode
                    if ref_code == target_refcode:
                        print(f"    🎯 НАЙДЕН! refCode = {target_refcode}")
                        found_payee = payee
                        break
            
            # Показать статистику страницы
            if page_refcodes:
                min_ref = min(int(r) for r in page_refcodes if r.isdigit())
                max_ref = max(int(r) for r in page_refcodes if r.isdigit())
                print(f"    📊 RefCode диапазон: {min_ref} - {max_ref} | Уникальных: {len(page_refcodes)}")
            
            # Если нашли - можем остановиться
            if found_payee:
                break
            
            # Логика остановки
            if len(payees) < limit:
                print(f"    ✅ Последняя страница (получено {len(payees)} < {limit})")
                break
            
            # Проверка разумного лимита страниц
            expected_pages = (total_count + limit - 1) // limit if total_count > 0 else 50
            if page > expected_pages + 5:  # +5 для безопасности
                print(f"    ⚠️ Превышен ожидаемый лимит страниц ({expected_pages}) - останавливаемся")
                break
            
            offset += limit
            page += 1
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            offset += limit
            page += 1
            continue
    
    print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"  📄 Обработано страниц: {page}")
    print(f"  🔢 Уникальных refCode: {len(all_refcodes)}")
    print(f"  🎯 Найден целевой refCode: {'ДА' if found_payee else 'НЕТ'}")
    
    # Показать диапазон всех refCode
    if all_refcodes:
        numeric_refs = [int(r) for r in all_refcodes if r.isdigit()]
        if numeric_refs:
            print(f"  📊 Диапазон всех refCode: {min(numeric_refs)} - {max(numeric_refs)}")
            
            # Проверить, входит ли целевой refCode в диапазон
            target_int = int(target_refcode)
            if target_int < min(numeric_refs):
                print(f"  ⚠️ Целевой refCode {target_int} МЕНЬШЕ минимального {min(numeric_refs)}")
            elif target_int > max(numeric_refs):
                print(f"  ⚠️ Целевой refCode {target_int} БОЛЬШЕ максимального {max(numeric_refs)}")
            else:
                print(f"  ✅ Целевой refCode {target_int} в диапазоне, но не найден")
    
    return found_payee

def display_payee_details(payee):
    """Показать детали найденного payee"""
    
    if not payee:
        return
        
    contact = payee.get('contactInformation', {})
    
    print(f"\n🎯 НАЙДЕННЫЙ PAYEE:")
    print("=" * 60)
    print(f"🔢 RefCode: {payee.get('refCode')}")
    print(f"🆔 ID: {payee.get('id')}")
    print(f"📊 Status: {payee.get('status')}")
    print(f"📛 Name: {payee.get('name', 'N/A')}")
    print(f"👤 First Name: {contact.get('firstName', 'N/A')}")
    print(f"👤 Last Name: {contact.get('lastName', 'N/A')}")
    print(f"📧 Email: {contact.get('email', 'N/A')}")
    print(f"🏢 Company: {contact.get('companyName', 'N/A')}")
    print(f"🌍 Country: {contact.get('beneficiaryCountryCode', 'N/A')}")
    
    # Проверка имени
    first_name = contact.get('firstName', '').lower()
    last_name = contact.get('lastName', '').lower()
    
    print(f"\n🔍 ПРОВЕРКА ИМЕНИ MATHEUS DE MORAIS:")
    if 'matheus' in first_name and 'morais' in last_name:
        print(f"  ✅ СОВПАДЕНИЕ! Это действительно Matheus de Morais")
    elif 'matheus' in first_name:
        print(f"  ⚠️ Имя Matheus найдено, но фамилия: {contact.get('lastName', 'N/A')}")
    else:
        print(f"  ❌ Это НЕ Matheus de Morais")
        print(f"      Фактическое имя: {contact.get('firstName', 'N/A')} {contact.get('lastName', 'N/A')}")

def main():
    """Основная функция"""
    
    print(f"🔍 УМНЫЙ ПОИСК PAYEE ПО REFCODE")
    print("=" * 60)
    
    try:
        # Инициализация
        config_rest.validate_config()
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        
        print(f"🌐 Среда: {'Sandbox' if is_sandbox else 'Production'}")
        
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        
        # Поиск
        payee = smart_search_refcode(api, "22737")
        
        # Результат
        if payee:
            display_payee_details(payee)
            
            print(f"\n🎉 ВЫВОД:")
            print(f"  ✅ Payee с refCode = 22737 НАЙДЕН в системе")
            print(f"  📝 Ваш список из 86 refCode нужно проверять именно по этому полю")
            
        else:
            print(f"\n❌ РЕЗУЛЬТАТ:")
            print(f"  Payee с refCode = 22737 НЕ НАЙДЕН в системе")
            print(f"  Возможные причины:")
            print(f"  - RefCode больше максимального в системе")
            print(f"  - Payee был удален")
            print(f"  - Данные из другой системы/аккаунта")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 