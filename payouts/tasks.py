import logging
import time
from celery import shared_task
from django.utils import timezone
from .models import PayoutRequest

logger = logging.getLogger(__name__)


@shared_task
def process_payout_request(payout_id):
    """
    Асинхронная задача обработки заявки на выплату.
    
    Имитирует обработку заявки:
    1. Изменяет статус на 'processing'
    2. Выполняет имитацию обработки (задержка, проверки)
    3. Изменяет статус на 'completed' или 'failed'
    """
    try:
        # Получаем заявку
        payout = PayoutRequest.objects.get(id=payout_id)
        
        logger.info(f'Начало обработки заявки #{payout_id}')
        
        # Изменяем статус на 'processing'
        payout.status = 'processing'
        payout.save(update_fields=['status', 'updated_at'])
        
        # Имитация обработки заявки
        # Проверка суммы (простая валидация)
        if payout.amount <= 0:
            logger.warning(f'Заявка #{payout_id}: некорректная сумма')
            payout.status = 'failed'
            payout.comment = (payout.comment or '') + '\nОшибка: некорректная сумма выплаты.'
            payout.save(update_fields=['status', 'comment', 'updated_at'])
            return {'status': 'failed', 'message': 'Некорректная сумма'}
        
        # Проверка реквизитов
        if not payout.recipient_details or len(payout.recipient_details.strip()) < 10:
            logger.warning(f'Заявка #{payout_id}: некорректные реквизиты')
            payout.status = 'failed'
            payout.comment = (payout.comment or '') + '\nОшибка: некорректные реквизиты получателя.'
            payout.save(update_fields=['status', 'comment', 'updated_at'])
            return {'status': 'failed', 'message': 'Некорректные реквизиты'}
        
        # Имитация задержки обработки (например, запрос к внешнему API)
        time.sleep(2)  # Имитация обработки
        
        # Имитация проверки (например, проверка лимитов)
        # В реальном приложении здесь могут быть проверки баланса, лимитов и т.д.
        if payout.amount > 1000000:  # Пример проверки лимита
            logger.warning(f'Заявка #{payout_id}: превышен лимит')
            payout.status = 'failed'
            payout.comment = (payout.comment or '') + '\nОшибка: превышен максимальный лимит выплаты.'
            payout.save(update_fields=['status', 'comment', 'updated_at'])
            return {'status': 'failed', 'message': 'Превышен лимит'}
        
        # Успешная обработка
        payout.status = 'completed'
        payout.comment = (payout.comment or '') + f'\nЗаявка успешно обработана: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'
        payout.save(update_fields=['status', 'comment', 'updated_at'])
        
        logger.info(f'Заявка #{payout_id} успешно обработана')
        
        return {
            'status': 'completed',
            'message': f'Заявка #{payout_id} успешно обработана',
            'payout_id': payout_id
        }
        
    except PayoutRequest.DoesNotExist:
        logger.error(f'Заявка #{payout_id} не найдена')
        return {'status': 'error', 'message': f'Заявка #{payout_id} не найдена'}
    
    except Exception as e:
        logger.error(f'Ошибка при обработке заявки #{payout_id}: {str(e)}')
        
        # Пытаемся обновить статус заявки на 'failed'
        try:
            payout = PayoutRequest.objects.get(id=payout_id)
            payout.status = 'failed'
            payout.comment = (payout.comment or '') + f'\nОшибка обработки: {str(e)}'
            payout.save(update_fields=['status', 'comment', 'updated_at'])
        except:
            pass
        
        return {'status': 'error', 'message': f'Ошибка обработки: {str(e)}'}

