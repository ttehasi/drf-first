from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status, generics
from django.db import transaction
from django.utils import timezone
from django.db.utils import IntegrityError
from datetime import datetime, timedelta
from .tasks import check_automobile_confirmation
from .models import(
    EntryHistory,
    OutHistory,
    Yard,
    Automobile,
    Invite,
    ConfirmAutoInYard
)

from app.users.models import (
    User, 
    GuestEntry,
    Guest
)

from .serializers import (
    CombinedHistorySerializer,
    AutomobileNumberSerializer,
    AutomobileCreateSerializer,
    CombinedHistoryCreateSerializer,
    InviteGetSerializer,
    DeleteAutoSerializer
)

class CombinedHistoryView(APIView):
    def get(self, request):
        yard_id = request.query_params.get('yard_id')
        # auto_id = request.query_params.get('auto_id')
        auto_number = request.query_params.get('auto_number')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        entry_queryset = EntryHistory.objects.select_related('yard')
        out_queryset = OutHistory.objects.select_related('yard')
        
        if yard_id:
            entry_queryset = entry_queryset.filter(yard_id=yard_id)
            out_queryset = out_queryset.filter(yard_id=yard_id)
        
        # if auto_id:
        #     entry_queryset = entry_queryset.filter(auto_id=auto_id)
        #     out_queryset = out_queryset.filter(auto_id=auto_id)
        
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
                'auto_number': entry.auto_number,
                'yard': entry.yard
            })
        
        for out in out_history:
            combined_history.append({
                'id': out.id,
                'event_type': 'exit',
                'created_at': out.created_at,
                'auto_number': out.auto_number,
                'yard': out.yard
            })
        
        combined_history.sort(key=lambda x: x['created_at'], reverse=True)
        
        serializer = CombinedHistorySerializer(combined_history, many=True)
        
        return Response(serializer.data)


    def post(self, request):
        
        serializer = CombinedHistoryCreateSerializer(data=request.data)
        now = timezone.localtime(timezone.now())
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
                    if auto.is_guest:
                        guest = Guest.objects.get(auto_number=auto_number)
                        guest_entry = GuestEntry.objects.filter(guest=guest,
                                                             enter_time__isnull=True,
                                                             entry_timeout__gte=now,
                                                             yard=yard).first()
                        if guest_entry:
                            guest_entry.enter_time = now
                            guest_entry.save()
                        else:
                            return Response({'error': 'Гостевой доступ не найден'})
                    history_entry = EntryHistory.objects.create(
                        yard=yard,
                        auto_number=auto.auto_number
                    )
                    history_data = {
                        'id': history_entry.id,
                        'event_type': 'entry',
                        'auto_number': auto.auto_number,
                        'yard_id': yard.id,
                        'created_at': history_entry.created_at
                    }
                else:  # exit
                    if auto.is_guest:
                        guest = Guest.objects.get(auto_number=auto_number)
                        guest_entry = GuestEntry.objects.filter(guest=guest,
                                                             out_time__isnull=True,
                                                             entry_timeout__gte=now,
                                                             yard=yard).first()
                        if guest_entry:
                            guest_entry.out_time = now
                            guest_entry.save()
                        else:
                            raise ValueError({'error': 'Гостевой доступ не найден'})
                    history_entry = OutHistory.objects.create(
                        yard=yard,
                        auto_number=auto.auto_number
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
    def post(self, request):
        serializer = AutomobileCreateSerializer(data=request.data)
        # if serializer.is_valid():
        #     return Response({'ee': 12})
        # return Response({121: serializer.error_messages})
        if serializer.is_valid():
            # Подготавливаем данные для создания
            # validated_data['expires_at'] = timezone.now() + timedelta(days=14)
            # validated_data['is_confirmed'] = False
            valid_number = serializer.data['auto_number'].upper()
            # Получаем двор
            try:
                current_yards = [Yard.objects.get(id=int(i)) for i in serializer.data['yard_id']]
            except Yard.DoesNotExist:
                return Response({'error': 'Дворов с таким id нет'})
            
            # Получаем владельца
            try:
                owner = User.objects.get(id=serializer.data['owner'])
            except User.DoesNotExist:
                Response({'error': 'Владелец с таким id не найден'})
            
            # Создаем или получаем авто
            try:
                automobile = Automobile.objects.get(auto_number=valid_number)
            except Automobile.DoesNotExist:
                automobile = Automobile.objects.create(
                    auto_number=valid_number,
                    owner=owner,
                    expires_at=timezone.now() + timedelta(days=14),
                    # is_confirmed=False
                )
                
            for yard in current_yards:
                yard_automobiles = yard.automobiles.all()
                if automobile in yard_automobiles:
                    return Response({'error': 'Этот автомобиль уже есть в этом дворе'})

                yard.automobiles.add(automobile)
                ConfirmAutoInYard.objects.create(
                    auto=automobile,
                    yard=yard,
                    is_confirmed=False
                )
            # except IntegrityError:
            #     return Response({'error': 'Автомобиль с таким номером уже есть'})
            # Создаем задачу проверки через 14 дней
            try:
                task_result = check_automobile_confirmation.apply_async(
                    args=[automobile.id, serializer.data['yard_id']],
                    countdown=14 * 24 * 60 * 60  # 14 дней в секундах
                )
                
                
                # Формируем ответ
                response_data = {
                    'auto_number': automobile.auto_number,
                    'owner': automobile.owner.id,
                    'add_to_yard_id': serializer.data['yard_id'],
                }
                # response_serializer = AutomobileCreateSerializer(automobile)
                # response_data = response_serializer.data
                response_data['task_id'] = task_result.id
                response_data['check_date'] = automobile.expires_at.isoformat()
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                # Все равно возвращаем созданный автомобиль
                # response_serializer = AutomobileCreateSerializer(automobile)
                response_data = {
                    'auto_number': automobile.auto_number,
                    'owner': automobile.owner.id,
                    'add_to_yard_id': serializer.data['yard_id'],
                    'mess': 'Таска на проверку временного доступа не создана, но авто добавлено'
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
        
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
            black_list = yard.blacklist_set.all()
            black_auto = [black.auto_number for black in black_list]
            autos = yard.automobiles.all()
            auto = [
                {
                    'yard_id': yard.id,
                    'automobiles': [auto.auto_number for auto in autos if auto.auto_number not in black_auto],
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
        
        
class InviteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        invites = Invite.objects.filter(user=request.user)
        serializer = InviteGetSerializer(invites, many=True)
        return Response(serializer.data)
    
    
class AutoDeleteView(APIView):
    def delete(self, request, *args, **kwargs):
        serializer = DeleteAutoSerializer(data=request.data)
        if serializer.is_valid():
            auto_number = serializer.validated_data['auto_number']
            auto = Automobile.objects.get(auto_number=auto_number)
            auto.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)