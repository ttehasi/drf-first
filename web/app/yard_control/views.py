from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from datetime import datetime, timedelta
from .models import(
    EntryHistory,
    OutHistory,
    Yard,
    Automobile
)

from .serializers import (
    CombinedHistorySerializer,
    AutomobileSerializer,
    AutomobileCreateSerializer,
    CombinedHistoryCreateSerializer
)

class CombinedHistoryView(APIView):
    def get(self, request):
        yard_id = request.query_params.get('yard_id')
        auto_id = request.query_params.get('auto_id')
        auto_number = request.query_params.get('auto_number')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        entry_queryset = EntryHistory.objects.select_related('auto', 'yard')
        out_queryset = OutHistory.objects.select_related('auto', 'yard')
        
        if yard_id:
            entry_queryset = entry_queryset.filter(yard_id=yard_id)
            out_queryset = out_queryset.filter(yard_id=yard_id)
        
        if auto_id:
            entry_queryset = entry_queryset.filter(auto_id=auto_id)
            out_queryset = out_queryset.filter(auto_id=auto_id)
        
        if auto_number:
            entry_queryset = entry_queryset.filter(auto__auto_number__icontains=auto_number)
            out_queryset = out_queryset.filter(auto__auto_number__icontains=auto_number)
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d')
                entry_queryset = entry_queryset.filter(created_at__gte=date_from)
                out_queryset = out_queryset.filter(created_at__gte=date_from)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
                entry_queryset = entry_queryset.filter(created_at__lt=date_to)
                out_queryset = out_queryset.filter(created_at__lt=date_to)
            except ValueError:
                pass
        
        entry_history = list(entry_queryset)
        out_history = list(out_queryset)
        
        combined_history = []
        
        for entry in entry_history:
            combined_history.append({
                'id': entry.id,
                'event_type': 'entry',
                'created_at': entry.created_at,
                'auto': entry.auto,
                'yard': entry.yard
            })
        
        for out in out_history:
            combined_history.append({
                'id': out.id,
                'event_type': 'exit',
                'created_at': out.created_at,
                'auto': out.auto,
                'yard': out.yard
            })
        
        combined_history.sort(key=lambda x: x['created_at'], reverse=True)
        
        serializer = CombinedHistorySerializer(combined_history, many=True)
        
        return Response(serializer.data)


    def post(self, request):
        serializer = CombinedHistoryCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                event_type = serializer.validated_data['event_type']
                
                # Получение автомобиля
                auto_number = serializer.validated_data['auto_number'].upper()
                try:
                    auto = Automobile.objects.get(
                        auto_number=auto_number)
                except Automobile.DoesNotExist:
                    return Response({'error': f'Автомобиль с номером {auto_number} не найден'})                
                # Получение двора
                yard_id = serializer.validated_data['yard_id']
                try:
                    yard = Yard.objects.get(id=yard_id)
                except Yard.DoesNotExist:
                    return Response(
                        {'error': f'Двор с id {yard_id} не найден'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                if event_type == 'entry':
                    history_entry = EntryHistory.objects.create(
                        yard=yard,
                        auto=auto
                    )
                    history_data = {
                        'id': history_entry.id,
                        'event_type': 'entry',
                        'auto_number': auto.auto_number,
                        'yard_id': yard.id,
                        'created_at': history_entry.created_at
                    }
                else:  # exit
                    history_entry = OutHistory.objects.create(
                        yard=yard,
                        auto=auto
                    )
                    history_data = {
                        'id': history_entry.id,
                        'event_type': 'exit',
                        'auto_number': auto.auto_number,
                        'yard_id': yard.id,
                        'created_at': history_entry.created_at
                    }
                
                return Response(history_data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {'error': f'Ошибка при создании записи: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    
    
class AutomobileCreateAPIView(APIView):
    def post(self, request): # нужно еще добавить таску на expires at
        serializer = AutomobileCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



