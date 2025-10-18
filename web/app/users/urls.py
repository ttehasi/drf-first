from django.urls import path
from .views import (
    AccountDetailView,
    CurrentGuestEntriesAPIView,
    GuestEntryCreateView,
)

urlpatterns = [
    path('account/<int:pk>/', AccountDetailView.as_view(), name='account-detail'),
    path('current-guests/', CurrentGuestEntriesAPIView.as_view(), name='list-current-guests'),
    path('create-guestentry/', GuestEntryCreateView.as_view(), name='create-guestentry')
]