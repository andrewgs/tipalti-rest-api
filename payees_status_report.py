#!/usr/bin/env python3
"""
Полный отчет по статусам Payees
Статистика по всем payees в системе Tipalti
"""

from tipalti_rest_api import TipaltiRestAPI
import config_rest
from datetime import datetime
from collections import defaultdict
import json

def get_full_payees_statistics():
    """Получить полную статистику по всем payees"""
    
    print(f"📊 ПОЛНЫЙ ОТЧЕТ ПО PAYEES - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Инициализация API
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        
        print(f"🌐 Среда: {'Sandbox' if is_sandbox else 'Production'}")
        print("📥 Загружаем все payees...")
        
        # Получить всех payees (функция автоматически обрабатывает пагинацию)
        all_payees = api.get_payees_list(limit=1000)  # Большой лимит для эффективности
        
        print(f"👥 Всего найдено payees: {len(all_payees)}")
        print()
        
        # Статистика по статусам
        status_stats = defaultdict(int)
        country_stats = defaultdict(int)
        country_status_stats = defaultdict(lambda: defaultdict(int))
        ru_payees = []
        
        # Анализ каждого payee
        for payee in all_payees:
            status = payee.get('status', 'UNKNOWN')
            status_stats[status] += 1
            
            # Получить страну
            contact = payee.get('contactInformation', {})
            country = contact.get('beneficiaryCountryCode', 'UNKNOWN')
            country_stats[country] += 1
            country_status_stats[country][status] += 1
            
            # Собрать RU payees для детального анализа
            if country == 'RU':
                ru_payees.append({
                    'id': payee.get('id'),
                    'name': payee.get('name', 'No name'),
                    'status': status,
                    'email': contact.get('email', 'No email')
                })
        
        # Вывод общей статистики
        print("📈 ОБЩАЯ СТАТИСТИКА ПО СТАТУСАМ:")
        print("-" * 40)
        for status, count in sorted(status_stats.items()):
            percentage = (count / len(all_payees)) * 100 if all_payees else 0
            print(f"  {status}: {count} ({percentage:.1f}%)")
        
        print(f"\n📊 ИТОГО: {len(all_payees)} payees")
        
        # Топ стран
        print(f"\n🌍 ТОП-10 СТРАН:")
        print("-" * 40)
        sorted_countries = sorted(country_stats.items(), key=lambda x: x[1], reverse=True)
        for country, count in sorted_countries[:10]:
            percentage = (count / len(all_payees)) * 100 if all_payees else 0
            print(f"  {country}: {count} ({percentage:.1f}%)")
        
        # Детальная статистика по RU
        if ru_payees:
            print(f"\n🇷🇺 СТАТИСТИКА ПО РОССИИ:")
            print("-" * 40)
            ru_status_stats = country_status_stats['RU']
            total_ru = len(ru_payees)
            
            for status, count in sorted(ru_status_stats.items()):
                percentage = (count / total_ru) * 100
                print(f"  {status}: {count} ({percentage:.1f}%)")
            
            print(f"\n  📊 Всего RU payees: {total_ru}")
            
            # Показать несколько примеров
            print(f"\n  📋 Примеры RU payees:")
            for payee in ru_payees[:5]:
                print(f"    - {payee['name']} ({payee['status']}) - {payee['email']}")
        
        # Сохранить детальный отчет
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"payees_status_report_{timestamp}.json"
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'environment': 'sandbox' if is_sandbox else 'production',
            'total_payees': len(all_payees),
            'status_statistics': dict(status_stats),
            'country_statistics': dict(country_stats),
            'country_status_breakdown': {
                country: dict(statuses) 
                for country, statuses in country_status_stats.items()
            },
            'ru_payees_details': ru_payees
        }
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Детальный отчет сохранен: {report_filename}")
        
        return {
            'total': len(all_payees),
            'active': status_stats.get('ACTIVE', 0),
            'suspended': status_stats.get('SUSPENDED', 0),
            'ru_total': len(ru_payees),
            'ru_active': ru_status_stats.get('ACTIVE', 0),
            'ru_suspended': ru_status_stats.get('SUSPENDED', 0)
        }
        
    except Exception as e:
        print(f"❌ Ошибка при получении статистики: {e}")
        return None

def main():
    """Основная функция"""
    
    try:
        # Проверить конфигурацию
        config_rest.validate_config()
        
        # Получить статистику
        stats = get_full_payees_statistics()
        
        if stats:
            print("\n" + "=" * 60)
            print("🏆 КРАТКАЯ СВОДКА:")
            print(f"  📊 Всего payees: {stats['total']}")
            print(f"  ✅ Активных: {stats['active']}")
            print(f"  🔒 Заблокированных: {stats['suspended']}")
            
            if stats['ru_total'] > 0:
                print(f"\n🇷🇺 По России:")
                print(f"  📊 Всего RU: {stats['ru_total']}")
                print(f"  ✅ Активных RU: {stats['ru_active']}")
                print(f"  🔒 Заблокированных RU: {stats['ru_suspended']}")
                
                if stats['ru_total'] > 0:
                    completion = (stats['ru_suspended'] / stats['ru_total']) * 100
                    print(f"  📈 Прогресс блокировки: {completion:.1f}%")
        
    except KeyboardInterrupt:
        print("\n⚠️ Операция прервана пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main() 