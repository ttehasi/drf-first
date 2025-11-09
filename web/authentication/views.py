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
                response=UserSerializer,
                description="Успешная аутентификация",
                examples=[
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
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Неверные данные или пользователь не найден",
                examples=[
                    OpenApiExample(
                        'Пример ошибки',
                        value={
                            'error': 'Неверный пароль',
                            'details': {'phone': ['Это поле обязательно.']}
                        }
                    )
                ]
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
                response=OpenApiTypes.OBJECT,
                description="Пользователь успешно создан",
                examples=[
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
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Неверные данные или пользователь уже существует",
                examples=[
                    OpenApiExample(
                        'Пример ошибки',
                        value={
                            'error': 'Пользователь с таким номером уже существует',
                            'details': {'phone': ['Это поле обязательно.']}
                        }
                    )
                ]
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
        request={
            'type': 'object',
            'properties': {
                'current_password': {'type': 'string'},
                'new_password': {'type': 'string'}
            }
        },
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Пароль успешно изменен",
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        value={'message': 'Пароль успешно изменен'}
                    )
                ]
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Неверные данные или пароль",
                examples=[
                    OpenApiExample(
                        'Пример ошибки',
                        value={'error': 'Текущий пароль неверен'}
                    )
                ]
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
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Успешный выход из системы",
                examples=[
                    OpenApiExample(
                        'Пример ответа',
                        value={
                            "message": "Successfully logged out",
                            "logout_time": "2024-01-15T14:30:00+03:00"
                        }
                    )
                ]
            )
        }
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
    request={
        'type': 'object',
        'properties': {
            'refresh': {'type': 'string', 'example': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
        }
    },
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Токен успешно обновлен",
            examples=[
                OpenApiExample(
                    'Пример ответа',
                    value={
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                    }
                )
            ]
        )
    },
    examples=[
        OpenApiExample(
            'Пример запроса',
            value={
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
            },
            request_only=True
        )
    ]
)
class CustomTokenRefreshView(TokenRefreshView):
    pass