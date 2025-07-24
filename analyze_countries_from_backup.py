#!/usr/bin/env python3
"""
Анализ стран по beneficiaryCountryCode из бэкапа payees
Читает JSON файл и создает статистику по странам
"""

import json
import sys
from collections import defaultdict, Counter
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


def analyze_countries_from_backup(filename):
    """Анализ стран по beneficiaryCountryCode"""
    
    print("🌍 АНАЛИЗ СТРАН ПО BENEFICIARY COUNTRY CODE")
    print("=" * 60)
    
    try:
        # Читаем файл бэкапа
        print(f"📖 Чтение файла: {filename}")
        
        with open(filename, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # Извлекаем метаданные и payees
        metadata = backup_data.get('metadata', {})
        payees = backup_data.get('payees', [])
        
        print(f"📊 Метаданные бэкапа:")
        print(f"  ⏰ Время создания: {metadata.get('datetime', 'N/A')}")
        print(f"  👥 Всего payees: {metadata.get('total_payees', len(payees))}")
        print(f"  🌐 Среда: {metadata.get('environment', 'N/A')}")
        print()
        
        if not payees:
            print("❌ Нет данных payees в файле")
            return False
        
        # Анализируем страны
        print(f"🔍 Анализ {len(payees)} payees...")
        
        countries_count = Counter()
        countries_details = defaultdict(list)
        no_country_count = 0
        
        for payee in payees:
            contact_info = payee.get('contactInformation', {})
            country_code = contact_info.get('beneficiaryCountryCode', '').strip()
            
            if country_code:
                countries_count[country_code] += 1
                
                # Сохраняем детали для анализа
                countries_details[country_code].append({
                    'id': payee.get('id'),
                    'refCode': payee.get('refCode'),
                    'status': payee.get('status'),
                    'email': contact_info.get('email', ''),
                    'name': payee.get('name', '')
                })
            else:
                no_country_count += 1
        
        # Результаты анализа
        print("📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
        print("=" * 60)
        print(f"🌍 Всего уникальных стран: {len(countries_count)}")
        print(f"👥 Payees с указанной страной: {sum(countries_count.values())}")
        print(f"❓ Payees без страны: {no_country_count}")
        print()
        
        # Сортируем страны по количеству (по убыванию)
        sorted_countries = countries_count.most_common()
        
        print("🏆 СТРАНЫ ПО КОЛИЧЕСТВУ PAYEES:")
        print("=" * 60)
        print(f"{'Ранг':<4} {'Страна':<6} {'Количество':<10} {'Процент':<8} {'Статус'}")
        print("-" * 60)
        
        total_with_country = sum(countries_count.values())
        
        for rank, (country, count) in enumerate(sorted_countries, 1):
            percentage = (count / total_with_country * 100) if total_with_country > 0 else 0
            
            # Определяем статус страны
            if country in ['RU', 'BY', 'KZ']:
                status = "🔴 Санкции"
            elif country in ['UA']:
                status = "🟡 Внимание" 
            elif count >= 100:
                status = "🟢 Крупная"
            elif count >= 10:
                status = "🔵 Средняя"
            else:
                status = "⚪ Малая"
            
            print(f"{rank:<4} {country:<6} {count:<10} {percentage:>6.1f}% {status}")
        
        print("-" * 60)
        print(f"ИТОГО: {total_with_country} payees в {len(countries_count)} странах")
        print()
        
        # Топ-10 стран отдельно
        print("🎯 ТОП-10 СТРАН:")
        print("=" * 40)
        
        for rank, (country, count) in enumerate(sorted_countries[:10], 1):
            percentage = (count / total_with_country * 100) if total_with_country > 0 else 0
            print(f"{rank:2}. {country} - {count:,} payees ({percentage:.1f}%)")
        
        print()
        
        # Анализ санкционных стран
        sanctioned_countries = ['RU', 'BY', 'KZ', 'IR', 'KP']  # Расширенный список
        sanctioned_total = sum(countries_count.get(country, 0) for country in sanctioned_countries)
        
        if sanctioned_total > 0:
            print("🔴 САНКЦИОННЫЕ СТРАНЫ:")
            print("=" * 40)
            
            for country in sanctioned_countries:
                count = countries_count.get(country, 0)
                if count > 0:
                    percentage = (count / total_with_country * 100) if total_with_country > 0 else 0
                    print(f"{country}: {count:,} payees ({percentage:.1f}%)")
            
            print(f"\nИТОГО санкций: {sanctioned_total:,} payees ({sanctioned_total/total_with_country*100:.1f}%)")
            print()
        
        # Сохраняем детальный отчет
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"countries_analysis_{timestamp}.json"
        
        report_data = {
            "metadata": {
                "timestamp": timestamp,
                "datetime": datetime.now().isoformat(),
                "source_file": filename,
                "total_payees": len(payees),
                "payees_with_country": total_with_country,
                "payees_without_country": no_country_count,
                "total_countries": len(countries_count)
            },
            "statistics": {
                "countries_count": dict(countries_count),
                "countries_ranked": sorted_countries,
                "sanctioned_summary": {
                    country: countries_count.get(country, 0) 
                    for country in sanctioned_countries 
                    if countries_count.get(country, 0) > 0
                }
            },
            "details": dict(countries_details)
        }
        
        print(f"💾 Сохранение детального отчета: {report_filename}")
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        # Также создаем простой CSV со списком стран  
        csv_filename = f"countries_list_{timestamp}.csv"
        
        print(f"📋 Создание CSV списка: {csv_filename}")
        
        with open(csv_filename, 'w', encoding='utf-8') as f:
            f.write("Rank,Country_Code,Count,Percentage,Status\n")
            
            for rank, (country, count) in enumerate(sorted_countries, 1):
                percentage = (count / total_with_country * 100) if total_with_country > 0 else 0
                
                if country in ['RU', 'BY', 'KZ']:
                    status = "Sanctioned"
                elif country in ['UA']:
                    status = "Attention" 
                elif count >= 100:
                    status = "Large"
                elif count >= 10:
                    status = "Medium"
                else:
                    status = "Small"
                
                f.write(f"{rank},{country},{count},{percentage:.2f},{status}\n")
        
        print()
        print("🎉 АНАЛИЗ ЗАВЕРШЕН!")
        print("=" * 60)
        print(f"📊 Проанализировано: {len(payees)} payees")
        print(f"🌍 Найдено стран: {len(countries_count)}")
        print(f"📁 Детальный отчет: {report_filename}")
        print(f"📋 CSV список: {csv_filename}")
        
        return True
        
    except Exception as e:
        print(f"💥 Ошибка анализа: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Основная функция"""
    
    print("🌍 АНАЛИЗ СТРАН ИЗ BACKUP PAYEES")
    print("📊 Анализируем beneficiaryCountryCode")
    print()
    
    # Ищем последний файл бэкапа
    backup_file = find_latest_backup_file()
    
    if not backup_file:
        sys.exit(1)
    
    # Анализируем
    success = analyze_countries_from_backup(backup_file)
    
    if success:
        print("\n✅ Анализ выполнен успешно!")
        sys.exit(0)
    else:
        print("\n❌ Анализ завершился с ошибкой!")
        sys.exit(1)


if __name__ == "__main__":
    main() 