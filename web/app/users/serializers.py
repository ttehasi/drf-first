from rest_framework import serializers
from .models import User
from app.yard_control.models import (
    Yard,
    Automobile
)

class AutomobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automobile
        fields = ['auto_number', 'is_confirmed', 'expires_at']

class YardAddressSerializer(serializers.ModelSerializer):
    automobiles = serializers.SerializerMethodField()
    
    class Meta:
        model = Yard
        fields = ['address', 'automobiles']
    
    def get_automobiles(self, obj):
        user = self.context.get('user')
        if user:
            automobiles = Automobile.objects.filter(owner=user)
            return AutomobileSerializer(automobiles, many=True).data
        return []

class AccountDetailSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()
    name = serializers.CharField(source='get_full_name')
    addresses = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'phone', 'name', 'addresses']
    
    def get_addresses(self, obj):
        yards = Yard.objects.filter(users=obj)
        serializer = YardAddressSerializer(yards, many=True, context={'user': obj})
        
        addresses_dict = {}
        for yard_data in serializer.data:
            address = yard_data['address']
            automobiles = [auto['auto_number'] for auto in yard_data['automobiles']]
            addresses_dict[address] = automobiles
        
        return addresses_dict
