from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        """Создает и возвращает пользователя с phone и password"""
        if not phone:
            raise ValueError('The Phone field must be set')
        
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        """Создает и возвращает суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone, password, **extra_fields)


class User(AbstractUser):
    admin = models.BooleanField(default=False, verbose_name='статус админа')
    phone = models.CharField(verbose_name='Телефон', unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    full_name = models.CharField(verbose_name='ФИО', blank=True)
    
    username = None
        
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'
        
    def __str__(self):
        return self.phone
        

class Guest(models.Model):
    auto_number = models.CharField(max_length=9, unique=True, verbose_name='автомобильный номер')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')

    class Meta:
        db_table = 'guests'
        verbose_name = 'Гостя'
        verbose_name_plural = 'Гости'
        
    def __str__(self):
        return self.auto_number
        
        
class GuestEntry(models.Model):
    entry_timeout = models.DateTimeField(null=True, verbose_name='таймаут на въезд', blank=True)
    enter_time = models.DateTimeField(null=True, verbose_name='время заезда', blank=True)
    out_time = models.DateTimeField(null=True, verbose_name='время выезда', blank=True)
    guest = models.ForeignKey(
        Guest,
        on_delete=models.PROTECT,
        related_name='guestentries',
        verbose_name='Гость',
    )
    yard = models.ForeignKey(
        'yard_control.Yard',
        on_delete=models.PROTECT,
        related_name='guestentries',
        verbose_name='двор',
    )
    invite_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='guests',
        verbose_name='Пригласивший',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')

    class Meta:
        db_table = 'guestentries'
        verbose_name = 'Гостевой заявки'
        verbose_name_plural = 'Гостевые заявки'
        
    def __str__(self):
        return self.guest.auto_number