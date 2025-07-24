#!/usr/bin/env python3
"""
Извлечение всех payees кроме указанных стран (BR, MX, US)
Создает CSV файл со всеми payees из остальных стран
"""

import json
import csv
import sys
from datetime import datetime
import glob


def find_latest_backup_file():
    """Найти последний файл бэкапа с cursor"""
    backup_files = glob.glob("payees_backup_cursor_*.json")
    
    if not backup_files:
        print("❌ Не найдено файлов бэкапа payees_backup_cursor_*.json")
        return None
    
    # Сортируем по времени создания (последний файл)
    backup_files.sort(reverse=True)
    latest_file = backup_files[0]
    
    print(f"📁 Используем файл: {latest_file}")
    return latest_file


def extract_payees_excluding_countries(filename, excluded_countries=['BR', 'MX', 'US']):
    """Извлечь payees исключая указанные страны"""
    
    print("🌍 ИЗВЛЕЧЕНИЕ PAYEES ИСКЛЮЧАЯ УКАЗАННЫЕ СТРАНЫ")
    print("=" * 60)
    print(f"🚫 Исключаемые страны: {', '.join(excluded_countries)}")
    print()
    
    try:
        # Читаем файл бэкапа
        print(f"📖 Чтение файла: {filename}")
        
        with open(filename, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # Извлекаем метаданные и payees
        metadata = backup_data.get('metadata', {})
        all_payees = backup_data.get('payees', [])
        
        print(f"📊 Метаданные бэкапа:")
        print(f"  ⏰ Время создания: {metadata.get('datetime', 'N/A')}")
        print(f"  👥 Всего payees в файле: {len(all_payees)}")
        print(f"  🌐 Среда: {metadata.get('environment', 'N/A')}")
        print()
        
        if not all_payees:
            print("❌ Нет данных payees в файле")
            return False
        
        # Фильтруем payees
        print(f"🔍 Фильтрация payees...")
        print(f"🚫 Исключаем страны: {excluded_countries}")
        
        filtered_payees = []
        excluded_count = {country: 0 for country in excluded_countries}
        excluded_total = 0
        
        for payee in all_payees:
            contact_info = payee.get('contactInformation', {})
            country_code = contact_info.get('beneficiaryCountryCode', '').strip()
            
            if country_code in excluded_countries:
                excluded_count[country_code] += 1
                excluded_total += 1
            else:
                filtered_payees.append(payee)
        
        print(f"📊 РЕЗУЛЬТАТЫ ФИЛЬТРАЦИИ:")
        print(f"  ✅ Payees включено: {len(filtered_payees)}")
        print(f"  🚫 Payees исключено: {excluded_total}")
        print(f"  📋 Детали исключений:")
        
        for country in excluded_countries:
            count = excluded_count[country]
            percentage = (count / len(all_payees) * 100) if len(all_payees) > 0 else 0
            print(f"    {country}: {count:,} payees ({percentage:.1f}%)")
        
        print()
        
        if not filtered_payees:
            print("❌ После фильтрации не осталось payees")
            return False
        
        # Анализируем оставшиеся страны
        from collections import Counter
        remaining_countries = Counter()
        
        for payee in filtered_payees:
            contact_info = payee.get('contactInformation', {})
            country_code = contact_info.get('beneficiaryCountryCode', '').strip()
            remaining_countries[country_code] += 1
        
        print(f"🌍 ОСТАВШИЕСЯ СТРАНЫ ({len(remaining_countries)} стран):")
        
        for country, count in remaining_countries.most_common(10):
            percentage = (count / len(filtered_payees) * 100) if len(filtered_payees) > 0 else 0
            display_country = country if country else '--'
            print(f"  {display_country}: {count:,} payees ({percentage:.1f}%)")
        
        if len(remaining_countries) > 10:
            other_count = sum(remaining_countries.values()) - sum(dict(remaining_countries.most_common(10)).values())
            print(f"  ... остальные {len(remaining_countries)-10} стран: {other_count:,} payees")
        
        print()
        
        # Создаем CSV файл
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"payees_excluding_{'_'.join(excluded_countries)}_{timestamp}.csv"
        
        print(f"💾 Создание CSV файла: {csv_filename}")
        
        # Заголовки CSV
        csv_headers = [
            'id',
            'refCode', 
            'status',
            'name',
            'firstName',
            'lastName',
            'email',
            'companyName',
            'beneficiaryCountryCode',
            'paymentCountryCode',
            'address_street',
            'address_city',
            'address_state',
            'address_zipCode',
            'phone',
            'createdDate',
            'lastModifiedDate'
        ]
        
        # Записываем CSV
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Записываем заголовки
            writer.writerow(csv_headers)
            
            # Записываем данные payees
            for payee in filtered_payees:
                contact_info = payee.get('contactInformation', {})
                address = contact_info.get('address', {}) if isinstance(contact_info.get('address'), dict) else {}
                
                row = [
                    payee.get('id', ''),
                    payee.get('refCode', ''),
                    payee.get('status', ''),
                    payee.get('name', ''),
                    contact_info.get('firstName', ''),
                    contact_info.get('lastName', ''),
                    contact_info.get('email', ''),
                    contact_info.get('companyName', ''),
                    contact_info.get('beneficiaryCountryCode', ''),
                    contact_info.get('paymentCountryCode', ''),
                    address.get('street', '') if isinstance(address, dict) else '',
                    address.get('city', '') if isinstance(address, dict) else '',
                    address.get('state', '') if isinstance(address, dict) else '',
                    address.get('zipCode', '') if isinstance(address, dict) else '',
                    contact_info.get('phone', ''),
                    payee.get('createdDate', ''),
                    payee.get('lastModifiedDate', '')
                ]
                
                writer.writerow(row)
        
        # Также создаем JSON отчет о фильтрации
        report_filename = f"filtering_report_excluding_{'_'.join(excluded_countries)}_{timestamp}.json"
        
        report_data = {
            "metadata": {
                "timestamp": timestamp,
                "datetime": datetime.now().isoformat(),
                "source_file": filename,
                "excluded_countries": excluded_countries,
                "total_payees_original": len(all_payees),
                "total_payees_filtered": len(filtered_payees),
                "total_payees_excluded": excluded_total,
                "countries_remaining": len(remaining_countries)
            },
            "exclusion_details": excluded_count,
            "remaining_countries": dict(remaining_countries),
            "csv_filename": csv_filename
        }
        
        print(f"📋 Создание отчета фильтрации: {report_filename}")
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print()
        print("🎉 ИЗВЛЕЧЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("=" * 60)
        print(f"📁 CSV файл: {csv_filename}")
        print(f"📊 Payees в CSV: {len(filtered_payees):,}")
        print(f"🌍 Стран в CSV: {len(remaining_countries)}")
        print(f"🚫 Исключено payees: {excluded_total:,}")
        print(f"📋 Отчет: {report_filename}")
        
        # Показываем статистику по статусам
        from collections import Counter
        status_count = Counter(payee.get('status', 'Unknown') for payee in filtered_payees)
        
        print()
        print("📊 СТАТИСТИКА ПО СТАТУСАМ:")
        for status, count in status_count.most_common():
            percentage = (count / len(filtered_payees) * 100) if len(filtered_payees) > 0 else 0
            print(f"  {status}: {count:,} payees ({percentage:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"💥 Ошибка извлечения: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Основная функция"""
    
    print("🌍 ИЗВЛЕЧЕНИЕ PAYEES ИСКЛЮЧАЯ СТРАНЫ")
    print("📊 Создаем CSV со всеми payees кроме BR, MX, US")
    print()
    
    # Ищем последний файл бэкапа
    backup_file = find_latest_backup_file()
    
    if not backup_file:
        sys.exit(1)
    
    # Список исключаемых стран
    excluded_countries = ['BR', 'MX', 'US']
    
    # Анализируем
    success = extract_payees_excluding_countries(backup_file, excluded_countries)
    
    if success:
        print("\n✅ Извлечение выполнено успешно!")
        sys.exit(0)
    else:
        print("\n❌ Извлечение завершилось с ошибкой!")
        sys.exit(1)


if __name__ == "__main__":
    main() 