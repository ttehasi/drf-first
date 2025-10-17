from django.urls import path
from .views import AccountDetailView

urlpatterns = [
    path('account/<int:pk>/', AccountDetailView.as_view(), name='account-detail'),
]