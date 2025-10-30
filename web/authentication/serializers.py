from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20, required=True)
    password = serializers.CharField(required=True)

class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=True)
    phone = serializers.CharField(max_length=20, required=True)
    password = serializers.CharField(required=True)
    password_confirm = serializers.CharField(required=True)

    def validate_full_name(self, value):
        list_atr = value.split(' ')
        for atr in range(len(list_atr)):
            list_atr[atr] = list_atr[atr][0].upper() + list_atr[atr][1:]
        return ' '.join(list_atr)
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'full_name', 'email']