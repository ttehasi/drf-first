from celery import shared_task

from app.yard_control.models import Automobile


@shared_task
def remove_guest_automobile_scheduled(auto_number):
    """
    Удаляет гостевую машину в точно запланированное время
    """
    try:
        auto = Automobile.objects.get(auto_number=auto_number, is_guest=True)
    except Automobile.DoesNotExist as e:
        return "Машина не найдена"
        
    auto.delete()
    
    return f"Удалена гостевая машина {auto_number}"
