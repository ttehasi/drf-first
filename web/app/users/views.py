from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import AccountDetailSerializer

class AccountDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = AccountDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден"}, 
                status=status.HTTP_404_NOT_FOUND
            )