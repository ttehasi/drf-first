from django.db import models

from app.users.models import User, Guest


# Create your models here.
class Yard(models.Model):
    address = models.CharField(max_length=50, unique=True, verbose_name='адрес')
    andmin = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='admin_yards',
        verbose_name='Админ',
    )
    users = models.ManyToManyField(
        User,
        verbose_name='Пользователи двора',
        related_name='yards_user',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'yards'
        verbose_name = 'Двор'
        verbose_name_plural = 'Дворы'
        
        
class BlackList(models.Model):
    auto_numder = models.CharField(max_length=8, unique=True, verbose_name='автомобильный номер')
    yard = models.OneToOneField(
        Yard,
        on_delete=models.CASCADE,
        verbose_name='черный список двора',
        null=True
    )
    class Meta:
        db_table = 'blacklists'
        verbose_name = 'Черный список'
        verbose_name_plural = 'Черные списки'
        
        
class Automobile(models.Model):
    ...