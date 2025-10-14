from django.db import models

from app.users.models import User


# Create your models here.
class Yard(models.Model):
    address = models.CharField(max_length=50, unique=True, verbose_name='адрес')
    admin = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='admin_yards',
        verbose_name='Админ',
    )
    users = models.ManyToManyField(
        'users.User',
        verbose_name='Пользователи двора',
        related_name='yards_user',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'yards'
        verbose_name = 'Двора'
        verbose_name_plural = 'Дворы'
        
    def __str__(self):
        return self.address
        
        
class BlackList(models.Model):
    auto_number = models.CharField(max_length=8, unique=True, verbose_name='автомобильный номер')
    yard = models.OneToOneField(
        Yard,
        on_delete=models.CASCADE,
        verbose_name='черный список двора',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blacklists'
        verbose_name = 'Черного списка'
        verbose_name_plural = 'Черные списки'
        
    def __str__(self):
        return self.auto_number
        
        
class Automobile(models.Model):
    auto_number = models.CharField(max_length=8, unique=True, verbose_name='автомобильный номер')
    is_confirmed = models.BooleanField(verbose_name='Подтверждена')
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='automobiles',
        verbose_name='Владелец',
    )
    expires_at = models.DateTimeField(verbose_name='Временный доступ')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'automobiles'
        verbose_name = 'Автомобиля'
        verbose_name_plural = 'Автомобили'
        
    def __str__(self):
        return self.auto_number
        
class Invite(models.Model):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='my_invites',
        verbose_name='кто пригласил',
    )
    yard = models.ForeignKey(
        Yard,
        on_delete=models.PROTECT,
        related_name='invites',
        verbose_name='в какой двор приглашение',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'invites'
        verbose_name = 'Приглашения'
        verbose_name_plural = 'Приглашения'
        
    def __str__(self):
        return self.user