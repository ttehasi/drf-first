from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import User, GuestEntry
from .serializers import (
    AccountDetailSerializer,
    GuestEntrySerializer,
    GuestEntryCreateSerializer,
)
from django.utils import timezone
from django.db import models


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
            
            
class CurrentGuestEntriesAPIView(generics.ListAPIView):
    """
    API для получения текущих гостевых доступов
    """
    serializer_class = GuestEntrySerializer
    
    def get_queryset(self):
        now = timezone.now()
        
        queryset = GuestEntry.objects.filter(
            # enter_time__isnull=False,
            out_time__isnull=True
        ).filter(
            # models.Q(entry_timeout__isnull=False) & 
            models.Q(entry_timeout__gte=now)
        ).select_related('guest', 'yard', 'invite_by')
        
        # по двору
        yard_id = self.request.query_params.get('yard_id')
        if yard_id:
            queryset = queryset.filter(yard_id=yard_id)
            
        # по пригласившему
        invite_by_id = self.request.query_params.get('invite_by_id')
        if invite_by_id:
            queryset = queryset.filter(invite_by_id=invite_by_id)
             
        # по номеру автомобиля
        auto_number = self.request.query_params.get('auto_number')
        if auto_number:
            queryset = queryset.filter(guest__auto_number__icontains=auto_number)
        
        return queryset.order_by('-enter_time')
    
    def list(self, request, *args, **kwargs):
        # try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            response_data = {
                'count': queryset.count(),
                'current_time': timezone.now().isoformat(),
                'active_guests': serializer.data
            }
            
            return Response(response_data)
            
        # except Exception as e:
        #     return Response(
        #         {'error': str(e)}, 
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )
        
        
class GuestEntryCreateView(generics.CreateAPIView):
    queryset = GuestEntry.objects.all()
    serializer_class = GuestEntryCreateSerializer
    permission_classes = [permissions.IsAuthenticated] # означает что только авторизированные могут добавть заявку
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        response_serializer = GuestEntrySerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)