from django.urls import path
from .views import CombinedHistoryView, AutomobileCreateAPIView, AutoNumberAPIView
urlpatterns = [
    path('history/', CombinedHistoryView.as_view(), name='history'),
    path('add-auto/', AutomobileCreateAPIView.as_view(), name='create-auto'),
    path('auto-numbers/', AutoNumberAPIView.as_view(), name='auto-number')
]
