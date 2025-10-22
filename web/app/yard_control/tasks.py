from celery import shared_task
from django.utils import timezone

from .models import (
    BlackList,
    OutHistory,
    EntryHistory
)


@shared_task(bind=True, max_retries=3)
def check_automobile_confirmation(self, automobile_id, yard_id):
    try:
        from .models import Automobile
        
        
        # Просто получаем автомобиль - без проверок в кэше
        automobile = Automobile.objects.get(id=automobile_id)
        
        # Подсчет количества дней во дворе
        days_in_courtyard = calculate_days_in_courtyard(automobile, yard_id)
        
        
        if days_in_courtyard >= 11:
            # Подтверждаем автомобиль
            automobile.is_confirmed = True
            automobile.save()
            result = "confirmed"
        else:
            # Удаляем автомобиль
            auto_number = automobile.auto_number
            BlackList.objects.create(
                auto_number=auto_number,
                yard=yard_id
            )
            result = "move to black list"
        
        return {
            'automobile_id': automobile_id,
            'auto_number': automobile.auto_number if result == "confirmed" else auto_number,
            'days_in_courtyard': days_in_courtyard,
            'result': result,
            'checked_at': timezone.now().isoformat()
        }
        
    except Automobile.DoesNotExist:
        return None
    except Exception as e:
        self.retry(countdown=300, max_retries=3)

def calculate_days_in_courtyard(automobile, yard_id):
    """
    Подсчет количества дней, которые автомобиль был во дворе
    За последние 14 дней от даты создания
    """
    try:
        
        out_history = OutHistory.objects.filter(yard_id=yard_id, auto=automobile).count()
        entry_history = EntryHistory.objects.filter(yard_id=yard_id, auto=automobile).count()
        
        return (out_history + entry_history) // 2 # Надо еще дописать логику подсчета ночей 
        
        
        import random
        days_count = random.randint(8, 14)  # Для тестирования разных сценариев
        
        return days_count
        
    except Exception as e:
        raise ValueError('Что-то при подсчете дней пошло не так')

@shared_task
def check_all_pending_automobiles():
    try:
        from .models import Automobile
        
        now = timezone.now()
        # Ищем автомобили, у которых истек expires_at и они не подтверждены
        expired_automobiles = Automobile.objects.filter(
            expires_at__lte=now,
            is_confirmed=False
        )
        
        checked_count = 0
        for automobile in expired_automobiles:
            # Запускаем задачу для каждого автомобиля
            # Без проверок в кэше - пусть сама задача разберется
            check_automobile_confirmation.delay(automobile.id)
            checked_count += 1
        
        return f"Обработано {checked_count} автомобилей"
        
    except Exception as e:
        return f"Ошибка: {str(e)}"