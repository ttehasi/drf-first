from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer
from django.utils import timezone
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter
)
from drf_spectacular.types import OpenApiTypes

from rest_framework_simplejwt.views import TokenRefreshView

User = get_user_model()

class PhoneLoginView(APIView):

    @extend_schema(
        summary="Вход по номеру телефона",
        description="Аутентификация пользователя по номеру телефона и паролю",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "access": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
                        "refresh": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
                        "user": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "example": 1},
                                "phone": {"type": "string", "example": "+79991234567"},
                                "full_name": {"type": "string", "example": "Иван Иванов"},
                                "email": {"type": "string", "example": "ivan@example.com"}
                            }
                        }
                    }
                },
                description="Успешная аутентификация"
            ),
            400: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Неверные данные"},
                        "details": {"type": "object"}
                    }
                },
                description="Неверные данные или пользователь не найден"
            )
        },
        examples=[
            OpenApiExample(
                'Пример запроса',
                value={
                    'phone': '+79991234567',
                    'password': 'mysecretpassword'
                },
                request_only=True
            ),
            OpenApiExample(
                'Пример успешного ответа',
                value={
                    'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                    'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                    'user': {
                        'id': 1,
                        'phone': '+79991234567',
                        'full_name': 'Иван Иванов',
                        'email': 'ivan@example.com'
                    }
                },
                response_only=True
            )
        ]
    )

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Неверные данные', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        phone = serializer.validated_data['phone']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(phone=phone)
            
            if not user.check_password(password):
                return Response(
                    {'error': 'Неверный пароль'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Генерируем JWT токены
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user_data
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )

class PhoneRegisterView(APIView):

    @extend_schema(
        summary="Регистрация по номеру телефона",
        description="Создание нового пользователя с номером телефона и паролем",
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "access": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
                        "refresh": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
                        "user": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "example": 1},
                                "phone": {"type": "string", "example": "+79991234567"},
                                "full_name": {"type": "string", "example": "Иван Иванов"},
                                "email": {"type": "string", "example": "ivan@example.com"}
                            }
                        }
                    }
                },
                description="Пользователь успешно создан"
            ),
            400: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Неверные данные"},
                        "details": {"type": "object"}
                    }
                },
                description="Неверные данные или пользователь уже существует"
            ),
            500: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Ошибка при создании пользователя"}
                    }
                },
                description="Внутренняя ошибка сервера"
            )
        },
        examples=[
            OpenApiExample(
                'Пример запроса',
                value={
                    'full_name': 'иван иванов',
                    'phone': '+79991234567',
                    'password': 'mysecretpassword',
                    'password_confirm': 'mysecretpassword',
                    'email': 'ivan@example.com'
                },
                request_only=True
            ),
            OpenApiExample(
                'Пример успешного ответа',
                value={
                    'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                    'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                    'user': {
                        'id': 1,
                        'phone': '+79991234567',
                        'full_name': 'Иван Иванов',
                        'email': 'ivan@example.com'
                    }
                },
                response_only=True
            )
        ]
    )
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Неверные данные', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        phone = serializer.validated_data['phone']
        password = serializer.validated_data['password']
        full_name = serializer.validated_data['full_name']
        
        if User.objects.filter(phone=phone).exists():
            return Response(
                {'error': 'Пользователь с таким номером уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.create_user(
                phone=phone,
                password=password,
                full_name=full_name,
                email=serializer.validated_data.get('email', '')
            )
            
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user_data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Ошибка при создании пользователя: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Смена пароля",
        description="Изменение пароля текущего аутентифицированного пользователя",
        request=OpenApiTypes.OBJECT,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "example": "Пароль успешно изменен"
                        }
                    }
                },
                description="Пароль успешно изменен"
            ),
            400: OpenApiResponse(
                response={
                    "type": "object", 
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Текущий пароль неверен"
                        }
                    }
                },
                description="Неверные данные или пароль"
            )
        },
        examples=[
            OpenApiExample(
                'Пример запроса',
                value={
                    'current_password': 'oldpassword123',
                    'new_password': 'newpassword456'
                },
                request_only=True
            ),
            OpenApiExample(
                'Пример успешного ответа',
                value={
                    'message': 'Пароль успешно изменен'
                },
                response_only=True
            ),
            OpenApiExample(
                'Пример ошибки',
                value={
                    'error': 'Текущий пароль неверен'
                },
                response_only=True
            )
        ]
    )
    
    def post(self, request):
        """Смена пароля"""
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not current_password or not new_password:
            return Response(
                {'error': 'Все поля обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.check_password(current_password):
            return Response(
                {'error': 'Текущий пароль неверен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Пароль успешно изменен'})
    
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Выход из системы",
        description="Выход пользователя из системы с обновлением времени последнего выхода",
        request=None,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string", 
                            "example": "Successfully logged out"
                        },
                        "logout_time": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2024-01-15T14:30:00+03:00"
                        }
                    }
                },
                description="Успешный выход из системы"
            )
        },
        examples=[
            OpenApiExample(
                'Пример ответа',
                value={
                    "message": "Successfully logged out",
                    "logout_time": "2024-01-15T14:30:00+03:00"
                },
                response_only=True
            )
        ]
    )
    
    def post(self, request):
        request.user.last_logout = timezone.localtime(timezone.now())
        request.user.save()
        
        return Response({
            "message": "Successfully logged out",
            "logout_time": timezone.localtime(timezone.now()).isoformat()
        })


@extend_schema(
    summary="Обновление токена",
    description="Обновление access токена с помощью refresh токена",
    request=OpenApiTypes.OBJECT,
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "access": {
                        "type": "string",
                        "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                    }
                }
            },
            description="Токен успешно обновлен"
        ),
        401: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "Token is invalid or expired"
                    },
                    "code": {
                        "type": "string", 
                        "example": "token_not_valid"
                    }
                }
            },
            description="Неверный refresh токен"
        )
    },
    examples=[
        OpenApiExample(
            'Пример запроса',
            value={
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
            },
            request_only=True
        ),
        OpenApiExample(
            'Пример успешного ответа',
            value={
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
            },
            response_only=True
        ),
        OpenApiExample(
            'Пример ошибки',
            value={
                'detail': 'Token is invalid or expired',
                'code': 'token_not_valid'
            },
            response_only=True
        )
    ]
)
class CustomTokenRefreshView(TokenRefreshView):
    pass