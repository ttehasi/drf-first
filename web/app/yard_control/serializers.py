from rest_framework import serializers
from .models import EntryHistory, OutHistory, Automobile, Yard

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
    auto = AutomobileSerializer()
    yard = YardSerializer()
    
    class Meta:
        fields = ['event_type', 'created_at', 'auto', 'yard']
        
        
class AutomobileCreateSerializer(serializers.ModelSerializer):
    yard_id = serializers.ImageField()
    
    class Meta:
        model = Automobile
        fields = ['auto_number', 'owner', 'yard_id']

    def validate_auto_number(self, value):
        if not value:
            raise serializers.ValidationError("Автомобильный номер обязателен")
        return value.upper()


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