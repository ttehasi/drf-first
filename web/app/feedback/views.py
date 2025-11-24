from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import DemoForm
from .serializers import DemoFormSerializer
from rest_framework.views import APIView


class CreateDemoView(generics.CreateAPIView):
    queryset = DemoForm.objects.all()
    serializer_class = DemoFormSerializer
