from rest_framework import serializers
from .models import (
    EntryHistory,
    OutHistory,
    Automobile,
    Yard,
    Invite
)

from app.users.serializers import UserSerializer

class AutomobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automobile
        fields = ['id', 'auto_number', 'owner', 'expires_at']

class YardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Yard
        fields = ['id', 'address']

# class EntryHistorySerializer(serializers.ModelSerializer):
#     auto = AutomobileSerializer()
#     yard = YardSerializer()
#     event_type = serializers.SerializerMethodField()
    
#     class Meta:
#         model = EntryHistory
#         fields = ['id', 'yard', 'auto', 'created_at', 'event_type']
    
#     def get_event_type(self, obj):
#         return 'entry'

# class OutHistorySerializer(serializers.ModelSerializer):
#     auto = AutomobileSerializer()
#     yard = YardSerializer()
#     event_type = serializers.SerializerMethodField()
    
#     class Meta:
#         model = OutHistory
#         fields = ['id', 'yard', 'auto', 'created_at', 'event_type']
    
#     def get_event_type(self, obj):
#         return 'exit'
    
    
class CombinedHistorySerializer(serializers.Serializer):
    event_type = serializers.CharField()
    created_at = serializers.DateTimeField()
    auto_number = serializers.CharField()
    yard = YardSerializer()
    
    class Meta:
        fields = ['event_type', 'created_at', 'auto_number', 'yard']
        
        
class AutomobileCreateSerializer(serializers.Serializer):
    yard_id = serializers.ListField()
    auto_number = serializers.CharField()
    # owner = serializers.IntegerField()
    
    class Meta:
        # model = Automobile
        fields = ['auto_number', 'yard_id']

    # def validate_auto_number(self, value):
    #     if not value:
    #         raise serializers.ValidationError("Автомобильный номер обязателен")
    #     return value.upper()


class CombinedHistoryCreateSerializer(serializers.Serializer):
    event_type = serializers.CharField()
    auto_number = serializers.CharField()
    yard_id = serializers.IntegerField()
    
    class Meta:
        fields = ['event_type', 'auto_number', 'yard_id']
        
    def validate_event_type(self, value):
        if value not in ['exit', 'entry']:
            raise serializers.ValidationError('event_type может быть только "exit" или "entry"')
        return value
        
    def validate_auto_number(self, value):
        if not value:
            raise serializers.ValidationError("Автомобильный номер обязателен")
        return value.upper()
        
    def validate_yard_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("yard_id должен быть положительным числом")
        return value
    
    
class AutomobileNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automobile
        fields = ['auto_number']
        
        
class InviteGetSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    yard = YardSerializer()
    class Meta:
        model = Invite
        fields = ['id', 'user', 'yard', 'created_at']
        
        
class DeleteAutoSerializer(serializers.Serializer):
    auto_number = serializers.CharField()
    
    def validate_auto_number(self, value):
        if not Automobile.objects.filter(auto_number=value).exists():
            raise serializers.ValidationError("Автомобиль с таким номером не найден")
        return value
    

class InvitePostSerializer(serializers.Serializer):
    type = serializers.CharField()
    yard_id = serializers.IntegerField()
    
    def validate_type(self, value):
        if not value  in ['accept', 'reject']:
            return serializers.ValidationError('Тип запроса должен быть accept или reject')
        return value