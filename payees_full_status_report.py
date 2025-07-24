#!/usr/bin/env python3
"""
Полный отчет по статусам всех Payees (3000+)
Статистика по всем payees в системе Tipalti с корректной пагинацией
"""

from tipalti_rest_api import TipaltiRestAPI
import config_rest
from datetime import datetime
from collections import defaultdict
import json
import time

def get_all_payees_with_progress(api):
    """Получить всех payees з прогрессом загрузки"""
    
    all_payees = []
    limit = 100  # Размер страницы
    offset = 0
    page = 1
    
    print("📥 Загружаем всех payees...")
    
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
                # Нет больше данных
                print("  ✅ Загрузка завершена - больше нет данных")
                break
            
            # Добавить к общему списку
            all_payees.extend(payees)
            
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
            
            # Подготовка к следующей странице
            offset += limit
            page += 1
            
            # Небольшая пауза, чтобы не перегружать API
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Ошибка на странице {page}: {e}")
            # Попробуем продолжить со следующей страницы
            offset += limit
            page += 1
            continue
    
    print(f"\n✅ Загрузка завершена! Получено {len(all_payees)} payees")
    return all_payees

def analyze_payees_comprehensive(all_payees):
    """Комплексный анализ всех payees"""
    
    print(f"\n📊 АНАЛИЗ {len(all_payees)} PAYEES")
    print("=" * 60)
    
    # Статистика по статусам
    status_stats = defaultdict(int)
    country_stats = defaultdict(int)
    country_status_stats = defaultdict(lambda: defaultdict(int))
    
    # Детальные списки по ключевым группам
    ru_payees = []
    active_payees = []
    suspended_payees = []
    other_status_payees = []
    
    # Анализ каждого payee
    for i, payee in enumerate(all_payees):
        if (i + 1) % 500 == 0:
            print(f"  📈 Обработано {i + 1}/{len(all_payees)} payees...")
        
        # Основные поля
        payee_id = payee.get('id', 'UNKNOWN')
        status = payee.get('status', 'UNKNOWN')
        name = payee.get('name', 'No name')
        
        # Контактная информация
        contact = payee.get('contactInformation', {})
        country = contact.get('beneficiaryCountryCode', 'UNKNOWN')
        email = contact.get('email', 'No email')
        
        # Статистика
        status_stats[status] += 1
        country_stats[country] += 1
        country_status_stats[country][status] += 1
        
        # Подробная информация для ключевых групп
        payee_info = {
            'id': payee_id,
            'name': name,
            'status': status,
            'country': country,
            'email': email
        }
        
        # Российские payees
        if country == 'RU':
            ru_payees.append(payee_info)
        
        # По статусам
        if status == 'ACTIVE':
            active_payees.append(payee_info)
        elif status == 'SUSPENDED':
            suspended_payees.append(payee_info)
        else:
            other_status_payees.append(payee_info)
    
    return {
        'status_stats': status_stats,
        'country_stats': country_stats,
        'country_status_stats': country_status_stats,
        'ru_payees': ru_payees,
        'active_payees': active_payees,
        'suspended_payees': suspended_payees,
        'other_status_payees': other_status_payees
    }

def print_comprehensive_report(analysis, total_payees):
    """Вывести полный отчет"""
    
    status_stats = analysis['status_stats']
    country_stats = analysis['country_stats']
    country_status_stats = analysis['country_status_stats']
    ru_payees = analysis['ru_payees']
    active_payees = analysis['active_payees']
    suspended_payees = analysis['suspended_payees']
    
    # Общая статистика по статусам
    print("\n📈 ОБЩАЯ СТАТИСТИКА ПО СТАТУСАМ:")
    print("-" * 50)
    for status, count in sorted(status_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_payees) * 100 if total_payees else 0
        print(f"  {status}: {count:,} ({percentage:.1f}%)")
    
    print(f"\n📊 ИТОГО: {total_payees:,} payees")
    
    # Топ стран
    print(f"\n🌍 ТОП-15 СТРАН:")
    print("-" * 50)
    sorted_countries = sorted(country_stats.items(), key=lambda x: x[1], reverse=True)
    for country, count in sorted_countries[:15]:
        percentage = (count / total_payees) * 100 if total_payees else 0
        print(f"  {country}: {count:,} ({percentage:.1f}%)")
    
    # Детальная статистика по России
    if ru_payees:
        print(f"\n🇷🇺 ДЕТАЛЬНАЯ СТАТИСТИКА ПО РОССИИ:")
        print("-" * 50)
        ru_status_stats = country_status_stats['RU']
        total_ru = len(ru_payees)
        
        for status, count in sorted(ru_status_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_ru) * 100
            print(f"  {status}: {count:,} ({percentage:.1f}%)")
        
        print(f"\n  📊 Всего RU payees: {total_ru:,}")
        
        # Показать примеры разных статусов
        ru_by_status = defaultdict(list)
        for payee in ru_payees:
            ru_by_status[payee['status']].append(payee)
        
        print(f"\n  📋 Примеры RU payees по статусам:")
        for status, payees_list in ru_by_status.items():
            print(f"    {status} ({len(payees_list)} шт.):")
            for payee in payees_list[:3]:  # Показать первые 3
                print(f"      - {payee['name']} - {payee['email']}")
    
    # Краткая сводка по активным
    if active_payees:
        print(f"\n✅ АКТИВНЫЕ PAYEES ({len(active_payees):,}):")
        print("-" * 50)
        active_by_country = defaultdict(int)
        for payee in active_payees:
            active_by_country[payee['country']] += 1
        
        for country, count in sorted(active_by_country.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {country}: {count:,}")

def main():
    """Основная функция"""
    
    print(f"📊 ПОЛНЫЙ ОТЧЕТ ПО ВСЕМ PAYEES - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        # Проверить конфигурацию
        config_rest.validate_config()
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        
        print(f"🌐 Среда: {'Sandbox' if is_sandbox else 'Production'}")
        
        # Инициализация API
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        
        # Получить всех payees
        all_payees = get_all_payees_with_progress(api)
        
        if not all_payees:
            print("❌ Не удалось получить данные о payees")
            return
        
        # Анализ
        print(f"\n🔍 Анализируем {len(all_payees)} payees...")
        analysis = analyze_payees_comprehensive(all_payees)
        
        # Отчет
        print_comprehensive_report(analysis, len(all_payees))
        
        # Сохранить детальный отчет
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"full_payees_status_report_{timestamp}.json"
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'environment': 'sandbox' if is_sandbox else 'production',
            'total_payees': len(all_payees),
            'status_statistics': dict(analysis['status_stats']),
            'country_statistics': dict(analysis['country_stats']),
            'country_status_breakdown': {
                country: dict(statuses) 
                for country, statuses in analysis['country_status_stats'].items()
            },
            'ru_payees_count': len(analysis['ru_payees']),
            'active_payees_count': len(analysis['active_payees']),
            'suspended_payees_count': len(analysis['suspended_payees']),
            # Сохранить только краткую информацию для экономии места
            'sample_ru_payees': analysis['ru_payees'][:50],  # Первые 50
            'sample_active_payees': analysis['active_payees'][:50],
        }
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Детальный отчет сохранен: {report_filename}")
        
        # Итоговая сводка
        print("\n" + "=" * 70)
        print("🏆 ИТОГОВАЯ СВОДКА:")
        print(f"  📊 Всего payees: {len(all_payees):,}")
        print(f"  ✅ Активных: {len(analysis['active_payees']):,}")
        print(f"  🔒 Заблокированных: {len(analysis['suspended_payees']):,}")
        print(f"  🇷🇺 Российских: {len(analysis['ru_payees']):,}")
        
        if analysis['ru_payees']:
            ru_suspended = sum(1 for p in analysis['ru_payees'] if p['status'] == 'SUSPENDED')
            ru_active = sum(1 for p in analysis['ru_payees'] if p['status'] == 'ACTIVE')
            completion = (ru_suspended / len(analysis['ru_payees'])) * 100
            
            print(f"  🇷🇺 Активных RU: {ru_active:,}")
            print(f"  🇷🇺 Заблокированных RU: {ru_suspended:,}")
            print(f"  📈 Прогресс блокировки RU: {completion:.1f}%")
        
    except KeyboardInterrupt:
        print("\n⚠️ Операция прервана пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 