import os
from celery import Celery

# Установка переменной окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Создание экземпляра Celery
app = Celery('app')

# Загрузка настроек из Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач из всех приложений
app.autodiscover_tasks()
