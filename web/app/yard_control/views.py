from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from .tasks import check_automobile_confirmation
from .models import(
    EntryHistory,
    OutHistory,
    Yard,
    Automobile
)

from app.users.models import User

from .serializers import (
    CombinedHistorySerializer,
    AutomobileNumberSerializer,
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
            
    
    
# class AutomobileCreateAPIView(APIView):
#     def post(self, request): # нужно еще добавить таску на expires at
#         serializer = AutomobileCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AutomobileCreateAPIView(APIView):
    def post(self, request):
        serializer = AutomobileCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Подготавливаем данные для создания
            validated_data = serializer.validated_data.copy()
            # validated_data['expires_at'] = timezone.now() + timedelta(days=14)
            # validated_data['is_confirmed'] = False
            
            # Создаем автомобиль
            automobile = Automobile.objects.create(
                auto_number=validated_data['auto_number'],
                owner=validated_data['owner'],
                expires_at=timezone.now() + timedelta(days=14),
                is_confirmed=False
            )
            
            # Создаем задачу проверки через 14 дней
            try:
                task_result = check_automobile_confirmation.apply_async(
                    args=[automobile.id, validated_data['yard_id']],
                    countdown=14 * 24 * 60 * 60  # 14 дней в секундах
                )
                
                
                # Формируем ответ
                response_serializer = AutomobileCreateSerializer(automobile)
                response_data = response_serializer.data
                response_data['task_id'] = task_result.id
                response_data['check_date'] = automobile.expires_at.isoformat()
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                
                # Все равно возвращаем созданный автомобиль
                response_serializer = AutomobileCreateSerializer(automobile)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AutoNumberAPIView(generics.ListAPIView):
    serializer_class = AutomobileNumberSerializer
    def list(self, request, *args, **kwargs):
        yard_id = request.query_params.get('yard_id')
        if yard_id:
            try:
                queryset = Yard.objects.get(id=yard_id)
            except Yard.DoesNotExist:
                return Response({'error': 'двор с таким id не найден'})
            
            autos = queryset.automobiles.all()
            response = {
                'yard_id': yard_id,
                'count_auto': autos.count(),
                'auto_numbers': [auto.auto_number for auto in autos]
            }
            return Response(response)
        queryset = Yard.objects.all()
        numbers = []
        for yard in queryset:
            autos = yard.automobiles.all()
            auto = [
                {
                    'yard_id': yard.id,
                    'automobiles': [auto.auto_number for auto in autos],
                    'yard_auto_count': [auto.auto_number for auto in autos].__len__()
                }
            ]
            numbers.append(auto)
        response = {
            'count_auto': Automobile.objects.all().count(),
            'auto_numbers': numbers
        }
        return Response(response)
        # if yard_id:
        #     queryset = queryset.filter(=yard_id) # дописать фильтрацию авто по двору
        # serializer = self.get_serializer(queryset, many=True)
        # response = {
        #     'auto_numbers': serializer.data
        # }
        # return Response(response)