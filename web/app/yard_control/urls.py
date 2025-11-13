from django.urls import path
from .views import (
    CombinedHistoryView,
    AutomobileCreateAPIView, 
    AutoNumberAPIView,
    InviteAPIView,
    AutoDeleteView,
    UsersAutomobiles,
    UserCombinedHistoryView
)
urlpatterns = [
    path('history/', CombinedHistoryView.as_view(), name='history'),
    path('user-history/', UserCombinedHistoryView.as_view(), name='user-history'),
    path('add-auto/', AutomobileCreateAPIView.as_view(), name='create-auto'),
    path('auto-numbers/', AutoNumberAPIView.as_view(), name='auto-number'),
    path('invites/', InviteAPIView.as_view(), name='invites'),
    path('delete-auto/', AutoDeleteView.as_view(), name='delete-auto'),
    path('user-auto/', UsersAutomobiles.as_view(), name='user-auto')
]
