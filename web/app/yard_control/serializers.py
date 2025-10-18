from rest_framework import serializers
from .models import EntryHistory, OutHistory, Automobile, Yard

class AutomobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automobile
        fields = ['id', 'auto_number']

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
        
        
class AutomobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automobile
        fields = ['id', 'auto_number', 'is_confirmed', 'owner']

    def validate_auto_number(self, value):
        if not value:
            raise serializers.ValidationError("Автомобильный номер обязателен")
        return value.upper()