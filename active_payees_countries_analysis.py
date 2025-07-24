#!/usr/bin/env python3
"""
Анализ активных payees по странам
Статистика по beneficiaryCountryCode и paymentCountryCode
"""

from tipalti_rest_api import TipaltiRestAPI
import config_rest
from datetime import datetime
from collections import defaultdict
import json

def get_all_active_payees(api):
    """Получить всех активных payees с детальной информацией"""
    
    active_payees = []
    limit = 100
    offset = 0
    page = 1
    
    print("📥 Загружаем всех активных payees...")
    
    while True:
        print(f"  📄 Страница {page} (offset: {offset})...", end=" ")
        
        try:
            # Параметры для текущей страницы
            params = {
                'limit': limit,
                'offset': offset,
                'status': 'ACTIVE'  # Фильтр только по активным
            }
            
            # Прямой запрос к API
            response = api._make_request('GET', '/payees', params=params)
            
            # Получить payees с текущей страницы
            payees = response.get('items', [])
            total_count = response.get('totalCount', 0)
            
            print(f"получено {len(payees)} активных payees (всего активных: {total_count})")
            
            if not payees:
                break
            
            # Добавить к общему списку только активных
            for payee in payees:
                if payee.get('status') == 'ACTIVE':
                    active_payees.append(payee)
            
            # Показать прогресс
            progress = (len(active_payees) / total_count) * 100 if total_count > 0 else 0
            print(f"  📊 Прогресс: {len(active_payees)}/{total_count} ({progress:.1f}%)")
            
            # Если получили меньше чем лимит, то это последняя страница
            if len(payees) < limit:
                break
            
            # Если достигли общего количества
            if len(active_payees) >= total_count:
                break
            
            offset += limit
            page += 1
            
        except Exception as e:
            print(f"❌ Ошибка на странице {page}: {e}")
            offset += limit
            page += 1
            continue
    
    print(f"\n✅ Загрузка завершена! Получено {len(active_payees)} активных payees")
    return active_payees

def analyze_active_payees_countries(active_payees):
    """Детальный анализ активных payees по странам"""
    
    print(f"\n🔍 АНАЛИЗ {len(active_payees)} АКТИВНЫХ PAYEES ПО СТРАНАМ")
    print("=" * 70)
    
    # Статистика по странам
    beneficiary_countries = defaultdict(int)
    payment_countries = defaultdict(int)
    country_combinations = defaultdict(int)
    
    # Детальная информация о payees
    payees_by_beneficiary_country = defaultdict(list)
    payees_by_payment_country = defaultdict(list)
    payees_details = []
    
    # Анализ каждого активного payee
    for i, payee in enumerate(active_payees):
        if (i + 1) % 100 == 0:
            print(f"  📈 Обработано {i + 1}/{len(active_payees)} активных payees...")
        
        # Основные поля
        payee_id = payee.get('id', 'UNKNOWN')
        status = payee.get('status', 'UNKNOWN')
        name = payee.get('name', 'No name')
        
        # Контактная информация
        contact = payee.get('contactInformation', {})
        beneficiary_country = contact.get('beneficiaryCountryCode', 'UNKNOWN')
        payment_country = contact.get('paymentCountryCode', 'UNKNOWN')
        email = contact.get('email', 'No email')
        
        # Дополнительные поля
        address = contact.get('address', {})
        city = address.get('city', 'No city') if isinstance(address, dict) else 'No city'
        
        # Статистика
        beneficiary_countries[beneficiary_country] += 1
        payment_countries[payment_country] += 1
        
        # Комбинация стран
        combo = f"{beneficiary_country} -> {payment_country}"
        country_combinations[combo] += 1
        
        # Детальная информация
        payee_info = {
            'id': payee_id,
            'name': name,
            'status': status,
            'beneficiary_country': beneficiary_country,
            'payment_country': payment_country,
            'email': email,
            'city': city
        }
        
        payees_details.append(payee_info)
        payees_by_beneficiary_country[beneficiary_country].append(payee_info)
        payees_by_payment_country[payment_country].append(payee_info)
    
    return {
        'beneficiary_countries': beneficiary_countries,
        'payment_countries': payment_countries,
        'country_combinations': country_combinations,
        'payees_by_beneficiary_country': payees_by_beneficiary_country,
        'payees_by_payment_country': payees_by_payment_country,
        'payees_details': payees_details
    }

def print_countries_report(analysis, total_active):
    """Вывести детальный отчет по странам"""
    
    beneficiary_countries = analysis['beneficiary_countries']
    payment_countries = analysis['payment_countries']
    country_combinations = analysis['country_combinations']
    payees_by_beneficiary_country = analysis['payees_by_beneficiary_country']
    payees_by_payment_country = analysis['payees_by_payment_country']
    
    # Статистика по beneficiaryCountryCode
    print("\n🏠 СТАТИСТИКА ПО BENEFICIARY COUNTRY CODE:")
    print("-" * 60)
    sorted_beneficiary = sorted(beneficiary_countries.items(), key=lambda x: x[1], reverse=True)
    for country, count in sorted_beneficiary:
        percentage = (count / total_active) * 100 if total_active else 0
        print(f"  {country}: {count:,} ({percentage:.1f}%)")
    
    # Статистика по paymentCountryCode
    print(f"\n💳 СТАТИСТИКА ПО PAYMENT COUNTRY CODE:")
    print("-" * 60)
    sorted_payment = sorted(payment_countries.items(), key=lambda x: x[1], reverse=True)
    for country, count in sorted_payment:
        percentage = (count / total_active) * 100 if total_active else 0
        print(f"  {country}: {count:,} ({percentage:.1f}%)")
    
    # Комбинации стран
    print(f"\n🔄 ТОП-20 КОМБИНАЦИЙ СТРАН (Beneficiary -> Payment):")
    print("-" * 60)
    sorted_combos = sorted(country_combinations.items(), key=lambda x: x[1], reverse=True)
    for combo, count in sorted_combos[:20]:
        percentage = (count / total_active) * 100 if total_active else 0
        print(f"  {combo}: {count:,} ({percentage:.1f}%)")
    
    # Детальные примеры по ключевым странам
    print(f"\n📋 ПРИМЕРЫ PAYEES ПО КЛЮЧЕВЫМ СТРАНАМ:")
    print("-" * 60)
    
    # Показать примеры для топ стран
    key_countries = ['UA', 'BY', 'EE', 'RU', '--', 'UNKNOWN']
    
    for country in key_countries:
        if country in payees_by_beneficiary_country:
            payees_list = payees_by_beneficiary_country[country]
            print(f"\n  🏠 BENEFICIARY: {country} ({len(payees_list)} шт.):")
            for payee in payees_list[:5]:  # Показать первые 5
                print(f"    - {payee['name']} | Email: {payee['email']} | Payment: {payee['payment_country']} | City: {payee['city']}")
        
        if country in payees_by_payment_country and country != 'UNKNOWN':
            payees_list = payees_by_payment_country[country]
            if len(payees_list) > 0:
                print(f"\n  💳 PAYMENT: {country} ({len(payees_list)} шт.):")
                for payee in payees_list[:5]:  # Показать первые 5
                    print(f"    - {payee['name']} | Email: {payee['email']} | Beneficiary: {payee['beneficiary_country']} | City: {payee['city']}")

def check_suspicious_countries(analysis):
    """Проверка на подозрительные страны (RU, BY)"""
    
    payees_details = analysis['payees_details']
    
    # Поиск RU или BY в любом из полей
    ru_by_payees = []
    for payee in payees_details:
        if (payee['beneficiary_country'] in ['RU', 'BY'] or 
            payee['payment_country'] in ['RU', 'BY']):
            ru_by_payees.append(payee)
    
    if ru_by_payees:
        print(f"\n⚠️ ВНИМАНИЕ! НАЙДЕНЫ АКТИВНЫЕ PAYEES С RU/BY:")
        print("-" * 60)
        print(f"Всего найдено: {len(ru_by_payees)}")
        
        for payee in ru_by_payees:
            print(f"  🚨 ID: {payee['id']}")
            print(f"     Name: {payee['name']}")
            print(f"     Email: {payee['email']}")
            print(f"     Beneficiary: {payee['beneficiary_country']}")
            print(f"     Payment: {payee['payment_country']}")
            print(f"     City: {payee['city']}")
            print()
    else:
        print(f"\n✅ НЕ НАЙДЕНО АКТИВНЫХ PAYEES С RU/BY В ОБОИХ ПОЛЯХ")

def main():
    """Основная функция"""
    
    print(f"🌍 АНАЛИЗ АКТИВНЫХ PAYEES ПО СТРАНАМ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Проверить конфигурацию
        config_rest.validate_config()
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        
        print(f"🌐 Среда: {'Sandbox' if is_sandbox else 'Production'}")
        
        # Инициализация API
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        
        # Получить всех активных payees
        active_payees = get_all_active_payees(api)
        
        if not active_payees:
            print("❌ Не найдено активных payees")
            return
        
        # Анализ по странам
        analysis = analyze_active_payees_countries(active_payees)
        
        # Отчет
        print_countries_report(analysis, len(active_payees))
        
        # Проверка на подозрительные страны
        check_suspicious_countries(analysis)
        
        # Сохранить детальный отчет
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"active_payees_countries_report_{timestamp}.json"
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'environment': 'sandbox' if is_sandbox else 'production',
            'total_active_payees': len(active_payees),
            'beneficiary_countries_stats': dict(analysis['beneficiary_countries']),
            'payment_countries_stats': dict(analysis['payment_countries']),
            'country_combinations_stats': dict(analysis['country_combinations']),
            'detailed_payees': analysis['payees_details']
        }
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Детальный отчет сохранен: {report_filename}")
        
        # Итоговая сводка
        print("\n" + "=" * 80)
        print("🏆 ИТОГОВАЯ СВОДКА ПО АКТИВНЫМ PAYEES:")
        print(f"  📊 Всего активных payees: {len(active_payees):,}")
        print(f"  🏠 Уникальных beneficiary стран: {len(analysis['beneficiary_countries'])}")
        print(f"  💳 Уникальных payment стран: {len(analysis['payment_countries'])}")
        print(f"  🔄 Уникальных комбинаций: {len(analysis['country_combinations'])}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Операция прервана пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 