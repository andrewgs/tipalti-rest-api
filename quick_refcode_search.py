#!/usr/bin/env python3
"""
Быстрый поиск payee по refCode
Ищем payee с refCode = 22737
"""

from tipalti_rest_api import TipaltiRestAPI
import config_rest
import json

def find_payee_by_refcode(api, target_refcode="22737"):
    """Найти payee с определенным refCode"""
    
    print(f"🔍 Ищем payee с refCode = {target_refcode}")
    print("=" * 50)
    
    limit = 100
    offset = 0
    page = 1
    
    while True:
        print(f"📄 Страница {page}...", end=" ")
        
        try:
            params = {
                'limit': limit,
                'offset': offset
            }
            
            response = api._make_request('GET', '/payees', params=params)
            payees = response.get('items', [])
            
            print(f"получено {len(payees)} payees")
            
            if not payees:
                break
            
            # Поиск по refCode
            for payee in payees:
                ref_code = payee.get('refCode', '')
                
                if ref_code == target_refcode:
                    print(f"\n🎯 НАЙДЕН! Payee с refCode = {target_refcode}")
                    return payee
            
            if len(payees) < limit:
                break
            
            offset += limit  
            page += 1
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            offset += limit
            page += 1
            continue
    
    print(f"\n❌ Payee с refCode = {target_refcode} НЕ найден")
    return None

def display_payee_info(payee):
    """Показать полную информацию о payee"""
    
    if not payee:
        return
    
    contact = payee.get('contactInformation', {})
    
    print(f"\n📋 ПОЛНАЯ ИНФОРМАЦИЯ О PAYEE:")
    print("=" * 60)
    
    # Основные поля
    print(f"🆔 Полный ID: {payee.get('id', 'N/A')}")
    print(f"🔢 RefCode: {payee.get('refCode', 'N/A')}")
    print(f"📛 Name (поле name): {payee.get('name', 'N/A')}")
    print(f"📊 Status: {payee.get('status', 'N/A')}")
    
    # Контактная информация
    print(f"\n👤 КОНТАКТНАЯ ИНФОРМАЦИЯ:")
    print(f"  First Name: {contact.get('firstName', 'N/A')}")
    print(f"  Last Name: {contact.get('lastName', 'N/A')}")
    print(f"  Company: {contact.get('companyName', 'N/A')}")
    print(f"  Email: {contact.get('email', 'N/A')}")
    print(f"  Phone: {contact.get('phone', 'N/A')}")
    
    # Адрес
    address = contact.get('address', {})
    if address and isinstance(address, dict):
        print(f"\n🏠 АДРЕС:")
        print(f"  Line 1: {address.get('line1', 'N/A')}")
        print(f"  Line 2: {address.get('line2', 'N/A')}")
        print(f"  City: {address.get('city', 'N/A')}")
        print(f"  State: {address.get('state', 'N/A')}")
        print(f"  Postal Code: {address.get('postalCode', 'N/A')}")
    
    # Страны
    print(f"\n🌍 ГЕОГРАФИЯ:")
    print(f"  Beneficiary Country: {contact.get('beneficiaryCountryCode', 'N/A')}")
    print(f"  Payment Country: {contact.get('paymentCountryCode', 'N/A')}")
    
    # Даты и дополнительная информация
    print(f"\n📅 ДАТЫ:")
    print(f"  Created: {payee.get('created', 'N/A')}")
    print(f"  Last Updated: {payee.get('lastUpdated', 'N/A')}")
    
    print(f"\n💰 ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:")
    print(f"  Tax ID: {contact.get('taxId', 'N/A')}")
    
    # Полный JSON
    print(f"\n📄 ПОЛНЫЕ ДАННЫЕ (JSON):")
    print("=" * 60)
    print(json.dumps(payee, indent=2, ensure_ascii=False))

def main():
    """Основная функция"""
    
    print(f"🔍 ПОИСК PAYEE ПО REFCODE = 22737")
    print("=" * 60)
    
    try:
        # Инициализация
        config_rest.validate_config()
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        
        print(f"🌐 Среда: {'Sandbox' if is_sandbox else 'Production'}")
        
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        
        # Поиск
        payee = find_payee_by_refcode(api, "22737")
        
        # Результат 
        if payee:
            display_payee_info(payee)
            
            # Проверим, является ли это Matheus de Morais
            contact = payee.get('contactInformation', {})
            first_name = contact.get('firstName', '')
            last_name = contact.get('lastName', '')
            full_name = f"{first_name} {last_name}".strip()
            
            print(f"\n🎯 ПРОВЕРКА ИМЕНИ:")
            print(f"  Полное имя: {full_name}")
            
            if "matheus" in full_name.lower() and "morais" in full_name.lower():
                print(f"  ✅ ПОДТВЕРЖДЕНО: Это Matheus de Morais!")
            elif "matheus" in full_name.lower():
                print(f"  ⚠️  Имя содержит 'Matheus', но фамилия может отличаться")
            else:
                print(f"  ❌ Имя НЕ совпадает с 'Matheus de Morais'")
                
        else:
            print(f"\n❌ РЕЗУЛЬТАТ: Payee с refCode = 22737 НЕ найден в системе")
            print(f"   Возможные причины:")
            print(f"   - RefCode неверный")
            print(f"   - Payee был удален")
            print(f"   - Находится в другом аккаунте")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 