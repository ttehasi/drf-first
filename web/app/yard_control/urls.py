from django.urls import path
from .views import CombinedHistoryView, AutomobileCreateAPIView


urlpatterns = [
    path('history/', CombinedHistoryView.as_view(), name='history'),
    path('add-auto/', AutomobileCreateAPIView.as_view(), name='create-auto')
]
