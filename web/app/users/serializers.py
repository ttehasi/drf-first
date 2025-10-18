from rest_framework import serializers
from .models import (
    User,
    GuestEntry,
    Guest
)
from app.yard_control.models import (
    Yard,
    Automobile,
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


class GuestEntrySerializer(serializers.ModelSerializer):
    guest_auto_number = serializers.CharField(source='guest.auto_number')
    yard_address = serializers.CharField(source='yard.address', read_only=True)
    yard_id = serializers.CharField(source='yard.id')
    invite_by_name = serializers.CharField(source='invite_by.get_full_name', read_only=True)
    
    class Meta:
        model = GuestEntry
        fields = [
            'id',
            'guest_auto_number',
            'yard_address',
            'yard_id',
            'entry_timeout',
            'enter_time',
            'invite_by_name',
            'created_at'
        ]
        
        
class GuestEntryCreateSerializer(serializers.ModelSerializer):
    guest_auto_number = serializers.CharField(write_only=True)
    yard_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = GuestEntry
        fields = [
            'guest_auto_number',
            'yard_id',
            'entry_timeout',
        ]
    
    def create(self, validated_data):
        guest_auto_number = validated_data.pop('guest_auto_number')
        yard_id = validated_data.pop('yard_id')
        
        guest, created = Guest.objects.get_or_create(
            auto_number=guest_auto_number,
            defaults={'auto_number': guest_auto_number}
        )
        
        try:
            yard = Yard.objects.get(id=yard_id)
        except Yard.DoesNotExist:
            raise serializers.ValidationError({"yard_id": "Двор не найден"})
        
        user = self.context['request'].user
        
        guest_entry = GuestEntry.objects.create(
            guest=guest,
            yard=yard,
            invite_by=user,
            **validated_data
        )
        
        return guest_entry