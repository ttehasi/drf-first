from celery import shared_task
from django.utils import timezone

from .models import (
    BlackList,
    OutHistory,
    EntryHistory,
    ConfirmAutoInYard,
    Yard
)


@shared_task(bind=True, max_retries=3)
def check_automobile_confirmation(self, automobile_id, yards_id=None):
    try:
        from .models import Automobile
        
        
        # получаем автомобиль
        automobile = Automobile.objects.get(id=automobile_id)
        
        for yard_id in yards_id:
            # Подсчет количества дней во дворе
            days_in_courtyard = calculate_days_in_courtyard(automobile.auto_number, yard_id)
            
            yard = Yard.objects.get(id=yard_id)
            
            confirmed_in_curr_yard = ConfirmAutoInYard.objects.get(yard=yard, auto=automobile)
            if days_in_courtyard >= 11:
                # Подтверждаем автомобиль
                confirmed_in_curr_yard.is_confirmed = True
                confirmed_in_curr_yard.save()
            else:
                # Удаляем автомобиль
                auto_number = automobile.auto_number
                BlackList.objects.create(
                    auto_number=auto_number,
                    yard=yard
                )
                yard.automobiles.remove(automobile)
        
        return {
            'automobile_id': automobile_id,
            'auto_number': automobile.auto_number,
            'checked_at': timezone.now().isoformat()
        }
        
    except Automobile.DoesNotExist:
        return None
    except Exception as e:
        self.retry(countdown=300, max_retries=3)

def calculate_days_in_courtyard(auto_number, yard_id):
    """
    Подсчет количества дней, которые автомобиль был во дворе
    За последние 14 дней от даты создания
    """
    try:
        
        out_history = OutHistory.objects.filter(yard_id=yard_id, auto_number=auto_number).count()
        entry_history = EntryHistory.objects.filter(yard_id=yard_id, auto_number=auto_number).count()
        
        return (out_history + entry_history) // 2 # Надо еще дописать логику подсчета ночей 
        
        
        # import random
        # days_count = random.randint(8, 14)  # Для тестирования разных сценариев
        
        # return days_count
        
    except Exception as e:
        raise ValueError('Что-то при подсчете дней пошло не так')

# @shared_task  # надо как-то пердать yard_id
# def check_all_pending_automobiles():
#     try:
#         from .models import Automobile
        
#         now = timezone.now()
#         # Ищем автомобили, у которых истек expires_at и они не подтверждены
#         expired_automobiles = Automobile.objects.filter(
#             expires_at__lte=now,
#             is_confirmed=False
#         )
        
#         checked_count = 0
#         for automobile in expired_automobiles:
#             # Запускаем задачу для каждого автомобиля
#             check_automobile_confirmation.delay(automobile.id)
#             checked_count += 1
        
#         return f"Обработано {checked_count} автомобилей"
        
#     except Exception as e:
#         return f"Ошибка: {str(e)}"