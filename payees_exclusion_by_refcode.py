#!/usr/bin/env python3
"""
Создание списка payees с исключением по refCode
1. Получает всех payees из аккаунта Tipalti
2. Проверяет наличие указанных refCode в системе
3. Создает CSV со всеми payees кроме исключенных по refCode
"""

from tipalti_rest_api import TipaltiRestAPI
import config_rest
from datetime import datetime
import csv
import json
import time

# Список refCode для исключения (из сообщения пользователя)
EXCLUDED_REFCODES = [
    922, 1177, 1191, 1434, 1929, 2055, 2116, 2330, 3226, 3258, 3356, 3906, 4305, 5361, 
    10280, 10770, 11912, 12662, 13496, 13614, 14575, 15208, 15673, 15699, 16619, 17513, 
    18212, 18375, 20820, 21006, 21016, 21087, 21251, 21873, 22226, 22737, 22848, 24582, 
    24708, 24799, 24977, 25776, 25786, 26220, 26485, 26837, 26875, 26979, 27119, 27188, 
    27390, 27462, 27464, 27862, 32323, 32810, 33015, 33114, 33219, 33310, 33421, 33427, 
    33665, 33905, 33997, 34003, 34630, 34693, 34698, 34705, 34953, 35121, 35553, 36156, 
    36164, 36169, 36200, 36315, 36369, 36688, 36807, 36972, 37010, 37039, 37073, 37102
]

def get_all_payees_comprehensive(api):
    """Получить всех payees с максимальной пагинацией"""
    
    print("📥 Загружаем ВСЕ payees из аккаунта (расширенный поиск)...")
    
    all_payees = []
    limit = 100
    offset = 0
    page = 1
    max_empty_pages = 5  # Максимум пустых страниц подряд
    empty_pages = 0
    
    while True:
        print(f"  📄 Страница {page} (offset: {offset})...", end=" ")
        
        try:
            # Параметры для текущей страницы - БЕЗ фильтров
            params = {
                'limit': limit,
                'offset': offset
                # Убираем любые фильтры для получения ВСЕХ payees
            }
            
            # Прямой запрос к API
            response = api._make_request('GET', '/payees', params=params)
            
            # Получить payees с текущей страницы
            payees = response.get('items', [])
            total_count = response.get('totalCount', 0)
            
            print(f"получено {len(payees)} payees (всего заявлено: {total_count})")
            
            if not payees:
                empty_pages += 1
                print(f"  ⚠️ Пустая страница {empty_pages}/{max_empty_pages}")
                
                if empty_pages >= max_empty_pages:
                    print("  ✅ Достигнут лимит пустых страниц - завершаем")
                    break
                
                # Продолжаем поиск
                offset += limit
                page += 1
                continue
            else:
                empty_pages = 0  # Сбрасываем счетчик пустых страниц
            
            # Обработать каждого payee
            for payee in payees:
                payee_id = payee.get('id', '')
                ref_code = payee.get('refCode', '')
                contact = payee.get('contactInformation', {})
                
                # Извлечь детальную информацию
                payee_info = {
                    'id': payee_id,
                    'refCode': ref_code,
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
            if total_count > 0:
                progress = (len(all_payees) / total_count) * 100
                print(f"  📊 Прогресс: {len(all_payees)}/{total_count} ({progress:.1f}%)")
            else:
                print(f"  📊 Загружено: {len(all_payees)} payees")
            
            # Если получили меньше чем лимит, это может быть последняя страница
            if len(payees) < limit:
                print("  ✅ Получено меньше лимита - возможно последняя страница")
                # Но продолжаем еще несколько страниц на всякий случай
            
            offset += limit
            page += 1
            
            # Пауза чтобы не перегружать API
            time.sleep(0.1)
            
            # Защита от бесконечного цикла
            if page > 1000:  # Максимум 1000 страниц
                print("  ⚠️ Достигнут лимит страниц (1000) - принудительное завершение")
                break
            
        except Exception as e:
            print(f"❌ Ошибка на странице {page}: {e}")
            empty_pages += 1
            if empty_pages >= max_empty_pages:
                print("  ❌ Слишком много ошибок - завершаем")
                break
            offset += limit
            page += 1
            continue
    
    print(f"\n✅ Загрузка завершена! Получено {len(all_payees)} payees")
    
    # Показать статистику по refCode
    refcodes = [p['refCode'] for p in all_payees if p['refCode']]
    if refcodes:
        refcodes_int = []
        for rc in refcodes:
            try:
                refcodes_int.append(int(rc))
            except ValueError:
                pass
        
        if refcodes_int:
            print(f"📊 Статистика refCode:")
            print(f"  🔢 Всего с refCode: {len(refcodes)}")
            print(f"  📈 Диапазон: {min(refcodes_int)} - {max(refcodes_int)}")
            print(f"  🎯 Уникальных: {len(set(refcodes_int))}")
    
    return all_payees

def check_refcodes_presence(all_payees, excluded_refcodes):
    """Проверить наличие исключаемых refCode в системе"""
    
    print(f"\n🔍 Проверяем наличие {len(excluded_refcodes)} исключаемых refCode в системе...")
    
    # Создать словарь для быстрого поиска по refCode
    payees_by_refcode = {}
    
    for payee in all_payees:
        ref_code = payee.get('refCode', '')
        if ref_code:
            try:
                ref_code_int = int(ref_code)
                payees_by_refcode[ref_code_int] = payee
            except ValueError:
                # Нечисловой refCode - пропускаем
                pass
    
    print(f"📋 В системе найдено {len(payees_by_refcode)} payees с числовыми refCode")
    print(f"🔍 Диапазон refCode в системе: {min(payees_by_refcode.keys())} - {max(payees_by_refcode.keys())}")
    
    found_refcodes = []
    missing_refcodes = []
    found_payees = []
    
    print(f"\n📋 Результаты поиска исключаемых refCode:")
    
    for excluded_refcode in excluded_refcodes:
        if excluded_refcode in payees_by_refcode:
            payee = payees_by_refcode[excluded_refcode]
            found_refcodes.append(excluded_refcode)
            found_payees.append(payee)
            email_display = (payee['email'][:40] + "...") if len(payee['email']) > 40 else payee['email']
            print(f"  ✅ {excluded_refcode:5d} | {email_display:<43} | {payee['status']}")
        else:
            missing_refcodes.append(excluded_refcode)
            print(f"  ❌ {excluded_refcode:5d} | НЕ НАЙДЕН в системе")
    
    print(f"\n📊 Статистика проверки:")
    print(f"  ✅ Найдено: {len(found_refcodes)}")
    print(f"  ❌ Не найдено: {len(missing_refcodes)}")
    
    if missing_refcodes:
        print(f"\n⚠️  НЕ НАЙДЕННЫЕ REFCODE:")
        # Показать не найденные блоками по 10
        for i in range(0, len(missing_refcodes), 10):
            batch = missing_refcodes[i:i+10]
            print(f"    {', '.join(map(str, batch))}")
    
    if found_refcodes:
        print(f"\n✅ НАЙДЕННЫЕ REFCODE:")
        for i in range(0, len(found_refcodes), 10):
            batch = found_refcodes[i:i+10]
            print(f"    {', '.join(map(str, batch))}")
    
    return found_refcodes, missing_refcodes, found_payees

def create_exclusion_csv_by_refcode(all_payees, excluded_refcodes):
    """Создать CSV со всеми payees кроме исключенных по refCode"""
    
    print(f"\n📝 Создаем CSV файлы с исключением по refCode...")
    
    # Создать set исключаемых refCode для быстрой проверки
    excluded_refcodes_set = set(excluded_refcodes)
    
    # Фильтровать payees
    included_payees = []
    excluded_payees = []
    
    for payee in all_payees:
        ref_code = payee.get('refCode', '')
        
        should_exclude = False
        if ref_code:
            try:
                ref_code_int = int(ref_code)
                if ref_code_int in excluded_refcodes_set:
                    should_exclude = True
            except ValueError:
                # Нечисловой refCode - не исключаем
                pass
        
        if should_exclude:
            excluded_payees.append(payee)
        else:
            included_payees.append(payee)
    
    print(f"  📊 Всего payees: {len(all_payees)}")
    print(f"  🚫 Исключено по refCode: {len(excluded_payees)}")
    print(f"  ✅ Включено в финальный список: {len(included_payees)}")
    
    # Создать файлы
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. Полный CSV
    csv_filename = f"payees_excluding_refcodes_{timestamp}.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'RefCode', 'Status', 'Name', 'Email', 'FirstName', 'LastName', 
            'CompanyName', 'BeneficiaryCountry', 'PaymentCountry', 'Created', 'LastUpdated'
        ])
        
        for payee in included_payees:
            writer.writerow([
                payee['id'], payee['refCode'], payee['status'], payee['name'],
                payee['email'], payee['firstName'], payee['lastName'], payee['companyName'],
                payee['beneficiaryCountryCode'], payee['paymentCountryCode'],
                payee['created'], payee['lastUpdated']
            ])
    
    # 2. Только ID
    ids_filename = f"payee_ids_excluding_refcodes_{timestamp}.csv"
    with open(ids_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['PayeeID'])
        for payee in included_payees:
            writer.writerow([payee['id']])
    
    # 3. Только refCode
    refcodes_filename = f"payee_refcodes_excluding_specified_{timestamp}.csv"
    with open(refcodes_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['RefCode'])
        for payee in included_payees:
            if payee['refCode']:
                writer.writerow([payee['refCode']])
    
    # 4. Исключенные payees (для справки)
    excluded_filename = f"excluded_payees_by_refcode_{timestamp}.csv"
    with open(excluded_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'RefCode', 'Status', 'Name', 'Email', 'FirstName', 'LastName', 
            'CompanyName', 'BeneficiaryCountry', 'PaymentCountry', 'Created', 'LastUpdated'
        ])
        
        for payee in excluded_payees:
            writer.writerow([
                payee['id'], payee['refCode'], payee['status'], payee['name'],
                payee['email'], payee['firstName'], payee['lastName'], payee['companyName'],
                payee['beneficiaryCountryCode'], payee['paymentCountryCode'],
                payee['created'], payee['lastUpdated']
            ])
    
    print(f"\n💾 Созданные файлы:")
    print(f"  📄 Основной список: {csv_filename}")
    print(f"  🆔 Только ID: {ids_filename}")
    print(f"  🔢 Только RefCode: {refcodes_filename}")
    print(f"  🚫 Исключенные: {excluded_filename}")
    
    return csv_filename, ids_filename, refcodes_filename, excluded_filename, included_payees, excluded_payees

def main():
    """Основная функция"""
    
    print(f"📋 СОЗДАНИЕ СПИСКА PAYEES С ИСКЛЮЧЕНИЕМ ПО REFCODE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Проверить конфигурацию
        config_rest.validate_config()
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        
        print(f"🌐 Среда: {'Sandbox' if is_sandbox else 'Production'}")
        print(f"🚫 Количество refCode для исключения: {len(EXCLUDED_REFCODES)}")
        
        # Показать диапазон исключаемых refCode
        min_refcode = min(EXCLUDED_REFCODES)
        max_refcode = max(EXCLUDED_REFCODES)
        print(f"📝 Диапазон исключаемых refCode: {min_refcode} - {max_refcode}")
        print(f"   Первые 10: {EXCLUDED_REFCODES[:10]}")
        print(f"   Последние 10: {EXCLUDED_REFCODES[-10:]}")
        
        # Инициализация API
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        
        # Шаг 1: Получить всех payees с расширенным поиском
        all_payees = get_all_payees_comprehensive(api)
        
        if not all_payees:
            print("❌ Не удалось получить список payees")
            return
        
        # Шаг 2: Проверить наличие исключаемых refCode
        found_refcodes, missing_refcodes, found_payees = check_refcodes_presence(all_payees, EXCLUDED_REFCODES)
        
        # Шаг 3: Создать CSV с исключениями по refCode
        csv_file, ids_file, refcodes_file, excluded_file, included_payees, excluded_payees = create_exclusion_csv_by_refcode(
            all_payees, EXCLUDED_REFCODES
        )
        
        # Итоговая статистика
        print(f"\n" + "=" * 80)
        print(f"🏆 ЗАДАЧА ВЫПОЛНЕНА!")
        print(f"  📊 Всего payees в системе: {len(all_payees):,}")
        print(f"  🚫 Запрошено исключить refCode: {len(EXCLUDED_REFCODES)}")
        print(f"  ✅ Найдено и исключено: {len(found_refcodes)}")
        print(f"  ❌ Не найдено: {len(missing_refcodes)}")
        print(f"  📄 Финальный список содержит: {len(included_payees):,} payees")
        
        if found_refcodes:
            success_rate = (len(found_refcodes) / len(EXCLUDED_REFCODES)) * 100
            print(f"  📈 Успешность исключения: {success_rate:.1f}%")
        
        if missing_refcodes:
            print(f"  ⚠️  {len(missing_refcodes)} refCode не найдены - возможно удалены или неактуальны")
        
    except KeyboardInterrupt:
        print("\n⚠️ Операция прервана пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 