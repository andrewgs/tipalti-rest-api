#!/usr/bin/env python3
"""
Поиск конкретного payee в системе Tipalti
Ищем Matheus de Morais с ID 22737
"""

from tipalti_rest_api import TipaltiRestAPI
import config_rest
from datetime import datetime
import json

def search_payee_comprehensive(api, search_name="Matheus de Morais", search_id="22737"):
    """Поиск payee по имени и ID во всех возможных полях"""
    
    print(f"🔍 Ищем payee: '{search_name}' с ID '{search_id}'")
    print("=" * 60)
    
    all_payees = []
    found_payees = []
    limit = 100
    offset = 0
    page = 1
    
    print("📥 Сканируем всех payees в поисках совпадений...")
    
    while True:
        print(f"  📄 Страница {page} (offset: {offset})...", end=" ")
        
        try:
            params = {
                'limit': limit,
                'offset': offset
            }
            
            response = api._make_request('GET', '/payees', params=params)
            payees = response.get('items', [])
            total_count = response.get('totalCount', 0)
            
            print(f"получено {len(payees)} payees")
            
            if not payees:
                break
            
            # Поиск совпадений на текущей странице
            for payee in payees:
                payee_id = payee.get('id', '')
                ref_code = payee.get('refCode', '')
                name = payee.get('name', '')
                contact = payee.get('contactInformation', {})
                first_name = contact.get('firstName', '')
                last_name = contact.get('lastName', '')
                email = contact.get('email', '')
                company_name = contact.get('companyName', '')
                
                # Проверяем разные типы совпадений
                matches = []
                
                # По имени (с проверкой на None)
                full_name = f"{first_name} {last_name}".strip()
                if search_name and name and search_name.lower() in name.lower():
                    matches.append(f"name='{name}'")
                if search_name and full_name and search_name.lower() in full_name.lower():
                    matches.append(f"firstName+lastName='{full_name}'")
                if search_name and company_name and search_name.lower() in company_name.lower():
                    matches.append(f"companyName='{company_name}'")
                
                # По ID
                if search_id == ref_code:
                    matches.append(f"refCode='{ref_code}'")
                if search_id in payee_id:
                    matches.append(f"ID содержит '{search_id}'")
                
                # Если есть совпадения, добавляем в результаты
                if matches:
                    found_payees.append({
                        'payee': payee,
                        'matches': matches,
                        'match_score': len(matches)
                    })
            
            all_payees.extend(payees)
            
            # Показать прогресс
            progress = (len(all_payees) / total_count) * 100 if total_count > 0 else 0
            print(f"    📊 Обработано: {len(all_payees)}/{total_count} ({progress:.1f}%) | Найдено: {len(found_payees)}")
            
            if len(payees) < limit:
                break
            
            offset += limit
            page += 1
            
            # Ограничиваем для экономии времени, если уже нашли точное совпадение
            if any(match['match_score'] >= 2 for match in found_payees):
                print("  🎯 Найдено точное совпадение - можно остановить поиск")
                break
            
        except Exception as e:
            print(f"❌ Ошибка на странице {page}: {e}")
            offset += limit
            page += 1
            continue
    
    print(f"\n✅ Поиск завершен! Обработано {len(all_payees)} payees")
    
    return found_payees, all_payees

def display_found_payees(found_payees):
    """Показать найденных payees с детальной информацией"""
    
    if not found_payees:
        print("❌ Payee не найден!")
        return
    
    # Сортируем по количеству совпадений
    found_payees.sort(key=lambda x: x['match_score'], reverse=True)
    
    print(f"\n🎯 НАЙДЕНО {len(found_payees)} СОВПАДЕНИЙ:")
    print("=" * 80)
    
    for i, result in enumerate(found_payees, 1):
        payee = result['payee']
        matches = result['matches']
        contact = payee.get('contactInformation', {})
        
        print(f"\n🔍 РЕЗУЛЬТАТ #{i} (совпадений: {result['match_score']}):")
        print(f"  📋 Совпадения: {', '.join(matches)}")
        print(f"  " + "-" * 60)
        
        # Основная информация
        print(f"  🆔 Payee ID (полный): {payee.get('id', 'N/A')}")
        print(f"  🔢 RefCode: {payee.get('refCode', 'N/A')}")
        print(f"  📛 Name: {payee.get('name', 'N/A')}")
        print(f"  📊 Status: {payee.get('status', 'N/A')}")
        
        # Контактная информация
        print(f"  👤 First Name: {contact.get('firstName', 'N/A')}")
        print(f"  👤 Last Name: {contact.get('lastName', 'N/A')}")
        print(f"  🏢 Company: {contact.get('companyName', 'N/A')}")
        print(f"  📧 Email: {contact.get('email', 'N/A')}")
        
        # Адрес
        address_info = contact.get('address', {})
        if isinstance(address_info, dict):
            print(f"  🏠 Address: {address_info.get('line1', 'N/A')}")
            print(f"  🏙️ City: {address_info.get('city', 'N/A')}")
            print(f"  🗺️ State: {address_info.get('state', 'N/A')}")
            print(f"  📮 Postal Code: {address_info.get('postalCode', 'N/A')}")
        
        # Страны
        print(f"  🌍 Beneficiary Country: {contact.get('beneficiaryCountryCode', 'N/A')}")
        print(f"  💳 Payment Country: {contact.get('paymentCountryCode', 'N/A')}")
        
        # Даты
        print(f"  📅 Created: {payee.get('created', 'N/A')}")
        print(f"  🔄 Last Updated: {payee.get('lastUpdated', 'N/A')}")
        
        # Дополнительная информация
        print(f"  📞 Phone: {contact.get('phone', 'N/A')}")
        print(f"  🆔 Tax ID: {contact.get('taxId', 'N/A')}")
        
        # Показать полный JSON для первого (лучшего) результата
        if i == 1:
            print(f"\n  📄 ПОЛНЫЕ ДАННЫЕ PAYEE (JSON):")
            print("  " + "="*60)
            print(json.dumps(payee, indent=4, ensure_ascii=False))

def main():
    """Основная функция"""
    
    print(f"🔍 ПОИСК PAYEE 'Matheus de Morais' (ID: 22737) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Проверить конфигурацию
        config_rest.validate_config()
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        
        print(f"🌐 Среда: {'Sandbox' if is_sandbox else 'Production'}")
        
        # Инициализация API
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        
        # Поиск payee
        found_payees, all_payees = search_payee_comprehensive(api)
        
        # Показать результаты
        display_found_payees(found_payees)
        
        # Дополнительный анализ
        if found_payees:
            print(f"\n📊 АНАЛИЗ НАЙДЕННЫХ ДАННЫХ:")
            print("=" * 80)
            
            best_match = found_payees[0]
            payee = best_match['payee']
            
            print(f"✅ Лучшее совпадение:")
            print(f"  🔢 RefCode в системе: {payee.get('refCode', 'НЕТ')}")
            print(f"  🆔 Полный ID: {payee.get('id', 'НЕТ')}")
            print(f"  📛 Имя: {payee.get('contactInformation', {}).get('firstName', '')} {payee.get('contactInformation', {}).get('lastName', '')}")
            
            # Проверить, является ли 22737 refCode
            if payee.get('refCode') == '22737':
                print(f"  🎯 ПОДТВЕРЖДЕНО: 22737 - это refCode!")
            else:
                print(f"  ⚠️  22737 НЕ является refCode этого payee")
        
        else:
            print(f"\n❌ Payee 'Matheus de Morais' с ID 22737 НЕ найден в системе")
            print(f"   Возможные причины:")
            print(f"   - Неправильное имя или ID")
            print(f"   - Payee был удален")
            print(f"   - Находится в другом аккаунте/среде")
        
    except KeyboardInterrupt:
        print("\n⚠️ Операция прервана пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 