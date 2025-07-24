#!/usr/bin/env python3
"""
Создание списка payees с исключением указанных ID
1. Получает всех payees из аккаунта Tipalti
2. Проверяет наличие указанных ID в системе
3. Создает CSV со всеми payees кроме исключенных
"""

from tipalti_rest_api import TipaltiRestAPI
import config_rest
from datetime import datetime
import csv
import json
import time

# Список ID для исключения (из сообщения пользователя)
EXCLUDED_PAYEE_IDS = [
    922, 1177, 1191, 1434, 1929, 2055, 2116, 2330, 3226, 3258, 3356, 3906, 4305, 5361, 
    10280, 10770, 11912, 12662, 13496, 13614, 14575, 15208, 15673, 15699, 16619, 17513, 
    18212, 18375, 20820, 21006, 21016, 21087, 21251, 21873, 22226, 22737, 22848, 24582, 
    24708, 24799, 24977, 25776, 25786, 26220, 26485, 26837, 26875, 26979, 27119, 27188, 
    27390, 27462, 27464, 27862, 32323, 32810, 33015, 33114, 33219, 33310, 33421, 33427, 
    33665, 33905, 33997, 34003, 34630, 34693, 34698, 34705, 34953, 35121, 35553, 36156, 
    36164, 36169, 36200, 36315, 36369, 36688, 36807, 36972, 37010, 37039, 37073, 37102
]

def get_all_payees_with_details(api):
    """Получить всех payees с полной информацией"""
    
    print("📥 Загружаем всех payees из аккаунта...")
    
    all_payees = []
    limit = 100
    offset = 0
    page = 1
    
    while True:
        print(f"  📄 Страница {page} (offset: {offset})...", end=" ")
        
        try:
            # Параметры для текущей страницы
            params = {
                'limit': limit,
                'offset': offset
            }
            
            # Прямой запрос к API
            response = api._make_request('GET', '/payees', params=params)
            
            # Получить payees с текущей страницы
            payees = response.get('items', [])
            total_count = response.get('totalCount', 0)
            
            print(f"получено {len(payees)} payees (всего в системе: {total_count})")
            
            if not payees:
                print("  ✅ Загрузка завершена - больше нет данных")
                break
            
            # Обработать каждого payee
            for payee in payees:
                payee_id = payee.get('id', '')
                contact = payee.get('contactInformation', {})
                
                # Извлечь детальную информацию
                payee_info = {
                    'id': payee_id,
                    'refCode': payee.get('refCode', ''),
                    'status': payee.get('status', ''),
                    'name': payee.get('name', 'No name'),
                    'email': contact.get('email', ''),
                    'firstName': contact.get('firstName', ''),
                    'lastName': contact.get('lastName', ''),
                    'companyName': contact.get('companyName', ''),
                    'beneficiaryCountryCode': contact.get('beneficiaryCountryCode', ''),
                    'paymentCountryCode': contact.get('paymentCountryCode', ''),
                    'created': payee.get('created', ''),
                    'lastUpdated': payee.get('lastUpdated', '')
                }
                
                all_payees.append(payee_info)
            
            # Показать прогресс
            progress = (len(all_payees) / total_count) * 100 if total_count > 0 else 0
            print(f"  📊 Прогресс: {len(all_payees)}/{total_count} ({progress:.1f}%)")
            
            # Если получили меньше чем лимит, то это последняя страница
            if len(payees) < limit:
                print("  ✅ Загрузка завершена - получена последняя страница")
                break
            
            # Если достигли общего количества
            if len(all_payees) >= total_count:
                print("  ✅ Загрузка завершена - получены все payees")
                break
            
            offset += limit
            page += 1
            
            # Небольшая пауза, чтобы не перегружать API
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Ошибка на странице {page}: {e}")
            offset += limit
            page += 1
            continue
    
    print(f"\n✅ Загрузка завершена! Получено {len(all_payees)} payees")
    return all_payees

def check_excluded_ids_presence(all_payees, excluded_ids):
    """Проверить наличие исключаемых ID в системе"""
    
    print(f"\n🔍 Проверяем наличие {len(excluded_ids)} исключаемых ID в системе...")
    
    # Создать словарь для быстрого поиска
    payees_by_refcode = {}
    payees_by_id = {}
    
    for payee in all_payees:
        # Поиск по refCode (обычно это числовой ID)
        ref_code = payee.get('refCode', '')
        if ref_code:
            try:
                ref_code_int = int(ref_code)
                payees_by_refcode[ref_code_int] = payee
            except ValueError:
                pass
        
        # Поиск по полному ID
        payees_by_id[payee['id']] = payee
    
    found_ids = []
    missing_ids = []
    found_payees = []
    
    print(f"\n📋 Результаты поиска:")
    
    for excluded_id in excluded_ids:
        # Поиск по refCode
        if excluded_id in payees_by_refcode:
            payee = payees_by_refcode[excluded_id]
            found_ids.append(excluded_id)
            found_payees.append(payee)
            print(f"  ✅ {excluded_id:5d} | refCode: {payee['refCode']} | {payee['email'][:40]:<40} | {payee['status']}")
        else:
            missing_ids.append(excluded_id)
            print(f"  ❌ {excluded_id:5d} | НЕ НАЙДЕН в системе")
    
    print(f"\n📊 Статистика проверки:")
    print(f"  ✅ Найдено: {len(found_ids)}")
    print(f"  ❌ Не найдено: {len(missing_ids)}")
    
    if missing_ids:
        print(f"\n⚠️  ВНИМАНИЕ! Не найденные ID:")
        for missing_id in missing_ids:
            print(f"    - {missing_id}")
        print(f"  Возможно, эти payees были удалены или ID неверные")
    
    return found_ids, missing_ids, found_payees

def create_exclusion_csv(all_payees, excluded_ids):
    """Создать CSV со всеми payees кроме исключенных"""
    
    print(f"\n📝 Создаем CSV файл со всеми payees кроме исключенных...")
    
    # Создать set для быстрой проверки исключений
    excluded_refcodes = set()
    for payee in all_payees:
        ref_code = payee.get('refCode', '')
        if ref_code:
            try:
                ref_code_int = int(ref_code)
                if ref_code_int in excluded_ids:
                    excluded_refcodes.add(ref_code)
            except ValueError:
                pass
    
    # Фильтровать payees
    included_payees = []
    excluded_payees = []
    
    for payee in all_payees:
        ref_code = payee.get('refCode', '')
        
        # Проверить, нужно ли исключить
        should_exclude = False
        if ref_code in excluded_refcodes:
            should_exclude = True
        
        if should_exclude:
            excluded_payees.append(payee)
        else:
            included_payees.append(payee)
    
    print(f"  📊 Всего payees: {len(all_payees)}")
    print(f"  🚫 Исключено: {len(excluded_payees)}")
    print(f"  ✅ Включено в CSV: {len(included_payees)}")
    
    # Создать CSV файл
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"payees_excluding_specified_ids_{timestamp}.csv"
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Заголовки
        writer.writerow([
            'ID', 'RefCode', 'Status', 'Name', 'Email', 'FirstName', 'LastName', 
            'CompanyName', 'BeneficiaryCountry', 'PaymentCountry', 'Created', 'LastUpdated'
        ])
        
        # Данные
        for payee in included_payees:
            writer.writerow([
                payee['id'],
                payee['refCode'],
                payee['status'],
                payee['name'],
                payee['email'],
                payee['firstName'],
                payee['lastName'],
                payee['companyName'],
                payee['beneficiaryCountryCode'],
                payee['paymentCountryCode'],
                payee['created'],
                payee['lastUpdated']
            ])
    
    # Также создать список только ID для удобства
    ids_only_filename = f"payee_ids_excluding_specified_{timestamp}.csv"
    with open(ids_only_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['PayeeID'])
        for payee in included_payees:
            writer.writerow([payee['id']])
    
    # Создать список только RefCode для удобства
    refcodes_only_filename = f"payee_refcodes_excluding_specified_{timestamp}.csv"
    with open(refcodes_only_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['RefCode'])
        for payee in included_payees:
            if payee['refCode']:
                writer.writerow([payee['refCode']])
    
    print(f"\n💾 Файлы созданы:")
    print(f"  📄 Полная информация: {csv_filename}")
    print(f"  🆔 Только ID: {ids_only_filename}")
    print(f"  🔢 Только RefCode: {refcodes_only_filename}")
    
    return csv_filename, ids_only_filename, refcodes_only_filename, included_payees, excluded_payees

def save_detailed_report(all_payees, excluded_ids, found_ids, missing_ids, found_payees, 
                        included_payees, excluded_payees):
    """Сохранить детальный отчет"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"payees_exclusion_report_{timestamp}.json"
    
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'total_payees_in_system': len(all_payees),
        'requested_exclusions': len(excluded_ids),
        'found_exclusions': len(found_ids),
        'missing_exclusions': len(missing_ids),
        'final_included_payees': len(included_payees),
        'final_excluded_payees': len(excluded_payees),
        'requested_exclusion_ids': excluded_ids,
        'found_exclusion_ids': found_ids,
        'missing_exclusion_ids': missing_ids,
        'found_exclusion_payees': found_payees,
        'statistics': {
            'exclusion_success_rate': (len(found_ids) / len(excluded_ids)) * 100 if excluded_ids else 0,
            'total_excluded_percentage': (len(excluded_payees) / len(all_payees)) * 100 if all_payees else 0
        }
    }
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"  📊 Детальный отчет: {report_filename}")
    return report_filename

def main():
    """Основная функция"""
    
    print(f"📋 СОЗДАНИЕ СПИСКА PAYEES С ИСКЛЮЧЕНИЯМИ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Проверить конфигурацию
        config_rest.validate_config()
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        
        print(f"🌐 Среда: {'Sandbox' if is_sandbox else 'Production'}")
        print(f"🚫 Количество ID для исключения: {len(EXCLUDED_PAYEE_IDS)}")
        
        # Показать первые несколько исключаемых ID
        print(f"📝 Первые 10 исключаемых ID: {EXCLUDED_PAYEE_IDS[:10]}")
        if len(EXCLUDED_PAYEE_IDS) > 10:
            print(f"   ... и еще {len(EXCLUDED_PAYEE_IDS) - 10}")
        
        # Инициализация API
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        
        # Шаг 1: Получить всех payees
        all_payees = get_all_payees_with_details(api)
        
        if not all_payees:
            print("❌ Не удалось получить список payees")
            return
        
        # Шаг 2: Проверить наличие исключаемых ID
        found_ids, missing_ids, found_payees = check_excluded_ids_presence(all_payees, EXCLUDED_PAYEE_IDS)
        
        # Шаг 3: Создать CSV с исключениями
        csv_file, ids_file, refcodes_file, included_payees, excluded_payees = create_exclusion_csv(
            all_payees, EXCLUDED_PAYEE_IDS
        )
        
        # Шаг 4: Сохранить детальный отчет
        report_file = save_detailed_report(
            all_payees, EXCLUDED_PAYEE_IDS, found_ids, missing_ids, found_payees,
            included_payees, excluded_payees
        )
        
        # Итоговая статистика
        print(f"\n" + "=" * 80)
        print(f"🏆 ЗАДАЧА ВЫПОЛНЕНА!")
        print(f"  📊 Всего payees в системе: {len(all_payees):,}")
        print(f"  🚫 Запрошено исключить: {len(EXCLUDED_PAYEE_IDS)}")
        print(f"  ✅ Найдено и исключено: {len(found_ids)}")
        print(f"  ❌ Не найдено: {len(missing_ids)}")
        print(f"  📄 Финальный список содержит: {len(included_payees):,} payees")
        
        if missing_ids:
            success_rate = (len(found_ids) / len(EXCLUDED_PAYEE_IDS)) * 100
            print(f"  📈 Успешность исключения: {success_rate:.1f}%")
        else:
            print(f"  🎉 Все указанные ID найдены и исключены!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Операция прервана пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 