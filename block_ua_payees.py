#!/usr/bin/env python3
"""
Блокировка всех активных UA (Ukrainian) Payees
Массовая блокировка украинских payees через изменение статуса на SUSPENDED
"""

import json
import time
import csv
from datetime import datetime
from tipalti_rest_api import TipaltiRestAPI
import config_rest

def get_active_ua_payees(api):
    """Получить всех активных UA payees"""
    
    print("📥 Загружаем всех активных UA payees...")
    
    ua_payees = []
    limit = 100
    offset = 0
    page = 1
    
    while True:
        print(f"  📄 Страница {page} (offset: {offset})...", end=" ")
        
        try:
            # Параметры для текущей страницы
            params = {
                'limit': limit,
                'offset': offset,
                'status': 'ACTIVE'
            }
            
            # Прямой запрос к API
            response = api._make_request('GET', '/payees', params=params)
            
            # Получить payees с текущей страницы
            payees = response.get('items', [])
            total_count = response.get('totalCount', 0)
            
            if not payees:
                break
            
            # Фильтровать только UA payees
            page_ua_payees = []
            for payee in payees:
                if payee.get('status') == 'ACTIVE':
                    contact = payee.get('contactInformation', {})
                    beneficiary_country = contact.get('beneficiaryCountryCode', '')
                    payment_country = contact.get('paymentCountryCode', '')
                    
                    # Проверяем оба поля на UA
                    if beneficiary_country == 'UA' or payment_country == 'UA':
                        page_ua_payees.append({
                            'id': payee.get('id'),
                            'name': payee.get('name', 'No name'),
                            'status': payee.get('status'),
                            'beneficiary_country': beneficiary_country,
                            'payment_country': payment_country,
                            'email': contact.get('email', 'No email'),
                            'payee_data': payee  # Сохраняем полные данные
                        })
            
            ua_payees.extend(page_ua_payees)
            
            print(f"найдено {len(page_ua_payees)} UA payees (всего на странице: {len(payees)})")
            
            # Показать прогресс
            print(f"  📊 Всего UA payees найдено: {len(ua_payees)}")
            
            # Если получили меньше чем лимит, то это последняя страница
            if len(payees) < limit:
                break
            
            offset += limit
            page += 1
            
            # Небольшая пауза
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Ошибка на странице {page}: {e}")
            offset += limit
            page += 1
            continue
    
    print(f"\n✅ Поиск завершен! Найдено {len(ua_payees)} активных UA payees")
    return ua_payees

def suspend_payee(api, payee_info, dry_run=True):
    """Заблокировать одного payee"""
    
    payee_id = payee_info['id']
    
    if dry_run:
        return {
            'success': True,
            'action': 'DRY_RUN',
            'payee_id': payee_id,
            'message': 'Would suspend payee (dry run mode)'
        }
    
    try:
        # Данные для изменения статуса на SUSPENDED
        update_data = {
            'status': 'SUSPENDED'
        }
        
        # Выполнить PATCH запрос
        success = api.update_payee(payee_id, update_data)
        
        if success:
            return {
                'success': True,
                'action': 'SUSPENDED',
                'payee_id': payee_id,
                'message': 'Successfully suspended payee'
            }
        else:
            return {
                'success': False,
                'action': 'FAILED',
                'payee_id': payee_id,
                'message': 'API update_payee returned False'
            }
            
    except Exception as e:
        return {
            'success': False,
            'action': 'ERROR',
            'payee_id': payee_id,
            'message': f'Exception: {str(e)}'
        }

def block_ua_payees_batch(api, ua_payees, dry_run=True, batch_size=10, delay=1.0):
    """Массовая блокировка UA payees"""
    
    total_payees = len(ua_payees)
    successful = 0
    failed = 0
    results = []
    
    print(f"\n🚀 {'[DRY RUN] ' if dry_run else ''}Начинаем блокировку {total_payees} UA payees")
    print(f"📦 Размер батча: {batch_size}, пауза: {delay}s")
    print("=" * 80)
    
    for i in range(0, total_payees, batch_size):
        batch = ua_payees[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_payees + batch_size - 1) // batch_size
        
        print(f"\n📦 Батч {batch_num}/{total_batches} ({len(batch)} payees):")
        
        batch_results = []
        for j, payee in enumerate(batch):
            payee_num = i + j + 1
            
            print(f"  {payee_num:4d}/{total_payees} | {payee['id']} | {payee['email'][:30]:<30} | ", end="")
            
            # Заблокировать payee
            result = suspend_payee(api, payee, dry_run)
            
            # Добавить дополнительную информацию
            result.update({
                'payee_name': payee['name'],
                'payee_email': payee['email'],
                'beneficiary_country': payee['beneficiary_country'],
                'payment_country': payee['payment_country'],
                'processed_at': datetime.now().isoformat()
            })
            
            batch_results.append(result)
            results.append(result)
            
            # Показать результат
            if result['success']:
                successful += 1
                print(f"✅ {result['action']}")
            else:
                failed += 1
                print(f"❌ {result['action']}: {result['message']}")
            
            # Небольшая пауза между payees
            if not dry_run:
                time.sleep(0.2)
        
        # Показать статистику батча
        batch_success = sum(1 for r in batch_results if r['success'])
        batch_failed = len(batch_results) - batch_success
        
        print(f"  📊 Батч завершен: ✅ {batch_success} | ❌ {batch_failed}")
        
        # Пауза между батчами
        if i + batch_size < total_payees:  # Не ждать после последнего батча
            print(f"  ⏳ Пауза {delay}s перед следующим батчем...")
            time.sleep(delay)
    
    print("\n" + "=" * 80)
    print(f"🏁 {'[DRY RUN] ' if dry_run else ''}Блокировка завершена!")
    print(f"  📊 Всего обработано: {total_payees}")
    print(f"  ✅ Успешно: {successful}")
    print(f"  ❌ Ошибок: {failed}")
    
    if successful > 0:
        success_rate = (successful / total_payees) * 100
        print(f"  📈 Успешность: {success_rate:.1f}%")
    
    return results

def save_results_report(results, ua_payees, dry_run=True):
    """Сохранить отчет о результатах"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    prefix = 'dryrun_' if dry_run else ''
    
    # JSON отчет
    json_filename = f"{prefix}ua_payees_blocking_report_{timestamp}.json"
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'dry_run': dry_run,
        'total_payees': len(ua_payees),
        'total_processed': len(results),
        'successful': sum(1 for r in results if r['success']),
        'failed': sum(1 for r in results if not r['success']),
        'results': results
    }
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    # CSV отчет для удобства
    csv_filename = f"{prefix}ua_payees_blocking_summary_{timestamp}.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Payee ID', 'Name', 'Email', 'Beneficiary Country', 'Payment Country',
            'Action', 'Success', 'Message', 'Processed At'
        ])
        
        for result in results:
            writer.writerow([
                result['payee_id'],
                result['payee_name'],
                result['payee_email'],
                result['beneficiary_country'],
                result['payment_country'],
                result['action'],
                result['success'],
                result['message'],
                result['processed_at']
            ])
    
    print(f"\n💾 Отчеты сохранены:")
    print(f"  📄 JSON: {json_filename}")
    print(f"  📊 CSV: {csv_filename}")
    
    return json_filename, csv_filename

def main():
    """Основная функция"""
    
    print(f"🚫 БЛОКИРОВКА UA PAYEES - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Проверить конфигурацию
        config_rest.validate_config()
        client_id, client_secret, is_sandbox = config_rest.get_validated_config()
        
        print(f"🌐 Среда: {'Sandbox' if is_sandbox else 'Production'}")
        
        # Получить подтверждение пользователя
        print("\n⚠️  ВНИМАНИЕ! Вы собираетесь заблокировать ВСЕ активные UA payees!")
        print("   Это действие заблокирует всех украинских payees в системе.")
        
        # Сначала запуск в режиме dry run
        print("\n🔍 Сначала запускаем в режиме DRY RUN для проверки...")
        
        # Инициализация API
        api = TipaltiRestAPI(client_id, client_secret, is_sandbox)
        
        # Получить всех активных UA payees
        ua_payees = get_active_ua_payees(api)
        
        if not ua_payees:
            print("❌ Не найдено активных UA payees для блокировки")
            return
        
        print(f"\n📋 Найденные UA payees:")
        print(f"  🔢 Всего: {len(ua_payees)}")
        
        # Показать примеры
        print(f"  📝 Примеры (первые 5):")
        for i, payee in enumerate(ua_payees[:5]):
            print(f"    {i+1}. {payee['email']} | {payee['beneficiary_country']} -> {payee['payment_country']}")
        
        # DRY RUN
        print(f"\n🔍 Запускаем DRY RUN...")
        dry_results = block_ua_payees_batch(api, ua_payees, dry_run=True, batch_size=10, delay=0.5)
        
        # Сохранить DRY RUN отчет
        save_results_report(dry_results, ua_payees, dry_run=True)
        
        # Запросить подтверждение для реального выполнения
        print(f"\n" + "="*80)
        print(f"❓ DRY RUN завершен. Хотите выполнить РЕАЛЬНУЮ блокировку {len(ua_payees)} UA payees?")
        print(f"   Введите 'BLOCK UA PAYEES' для подтверждения:")
        
        user_input = input().strip()
        
        if user_input != 'BLOCK UA PAYEES':
            print("❌ Блокировка отменена пользователем")
            return
        
        # РЕАЛЬНАЯ БЛОКИРОВКА
        print(f"\n🚀 Запускаем РЕАЛЬНУЮ блокировку...")
        real_results = block_ua_payees_batch(api, ua_payees, dry_run=False, batch_size=5, delay=2.0)
        
        # Сохранить реальный отчет
        save_results_report(real_results, ua_payees, dry_run=False)
        
        print(f"\n🏆 БЛОКИРОВКА UA PAYEES ЗАВЕРШЕНА!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Операция прервана пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 