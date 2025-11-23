from django.urls import path
from .views import (
    CreateDemoView
)
urlpatterns = [
    path('demos/', CreateDemoView.as_view(), name='get-create-demo'),
]
