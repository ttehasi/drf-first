from django.urls import path
from .views import (
    CombinedHistoryView,
    AutomobileCreateAPIView, 
    AutoNumberAPIView,
    InviteAPIView,
    AutoDeleteView
)
urlpatterns = [
    path('history/', CombinedHistoryView.as_view(), name='history'),
    path('add-auto/', AutomobileCreateAPIView.as_view(), name='create-auto'),
    path('auto-numbers/', AutoNumberAPIView.as_view(), name='auto-number'),
    path('invites/', InviteAPIView.as_view(), name='invites'),
    path('delete-auto/', AutoDeleteView.as_view(), name='delete-auto')
]
