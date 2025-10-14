from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    admin = models.BooleanField(null=True)
    phone = models.CharField(verbose_name='Телефон', unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'
        
    def __str__(self):
        return self.phone
        

class Guest(models.Model):
    auto_number = models.CharField(max_length=8, unique=True, verbose_name='автомобильный номер')
    invite_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='guests',
        verbose_name='Админ',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'guests'
        verbose_name = 'Гостя'
        verbose_name_plural = 'Гости'
        
    def __str__(self):
        return self.auto_number
        
        
class GuestEntry(models.Model):
    entry_timeout = models.DateTimeField()
    enter_time = models.DateTimeField()
    out_time = models.DateTimeField()
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'guestentries'
        verbose_name = 'Гостевого входа'
        verbose_name_plural = 'Гостевые входы'
        
    def __str__(self):
        return self.guest