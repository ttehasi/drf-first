from django.urls import path
from .views import (
    PhoneLoginView, 
    PhoneRegisterView,
    ChangePasswordView,
    LogoutView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', PhoneLoginView.as_view(), name='login'),
    path('register/', PhoneRegisterView.as_view(), name='register'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]