from django.urls import path
from .views import CombinedHistoryView


urlpatterns = [
    path('history/', CombinedHistoryView.as_view(), name='history'),    
]
