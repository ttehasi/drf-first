from django.db import models
from django.utils.html import format_html


class Automobile(models.Model):
    auto_number = models.CharField(max_length=9, unique=True, verbose_name='автомобильный номер')
    is_guest = models.BooleanField(verbose_name='Гостевое авто', default=False)
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='automobiles',
        verbose_name='Владелец',
        null=True,
        blank=True
    )
    expires_at = models.DateTimeField(verbose_name='Временный доступ', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    
    class Meta:
        db_table = 'automobiles'
        verbose_name = 'Автомобиля'
        verbose_name_plural = 'Автомобили'
        
    def __str__(self):
        return self.auto_number


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
    automobiles = models.ManyToManyField(
        Automobile,
        verbose_name='Машины двора',
        related_name='yards_auto',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')

    class Meta:
        db_table = 'yards'
        verbose_name = 'Двора'
        verbose_name_plural = 'Дворы'
        
    def __str__(self):
        return self.address
    
    
class ConfirmAutoInYard(models.Model):
    is_confirmed = models.BooleanField(verbose_name='Подтверждена', default=False)
    auto = models.ForeignKey(
        Automobile,
        on_delete=models.CASCADE,
        verbose_name='машина',
        null=True,
    )
    yard = models.ForeignKey(
        Yard,
        on_delete=models.CASCADE,
        verbose_name='двор',
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    
    def __str__(self):
        return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">') if self.is_confirmed \
            else format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')
        
        
class BlackList(models.Model):
    auto_number = models.CharField(max_length=9, verbose_name='автомобильный номер')
    yard = models.ForeignKey(
        Yard,
        on_delete=models.CASCADE,
        verbose_name='черный список двора',
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    
    class Meta:
        db_table = 'blacklists'
        verbose_name = 'Черного списка'
        verbose_name_plural = 'Черные списки'
        unique_together = ['auto_number', 'yard']
        
    def __str__(self):
        return self.auto_number
        
        
class Invite(models.Model): 
    user_phone = models.CharField(verbose_name='Телефон пользователя', blank=True)
    yard = models.ForeignKey(
        Yard,
        on_delete=models.CASCADE,
        related_name='invites',
        verbose_name='в какой двор приглашение',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    
    class Meta:
        db_table = 'invites'
        verbose_name = 'Приглашения'
        verbose_name_plural = 'Приглашения'
        
    def __str__(self):
        return self.user_phone
    
    
class EntryHistory(models.Model):
    yard = models.ForeignKey(
        Yard,
        on_delete=models.PROTECT,
        related_name='entry_history',
        verbose_name='какого двора история',
    )
    # auto = models.ForeignKey(
    #     Automobile,
    #     verbose_name='авто', 
    #     on_delete=models.PROTECT
    # )
    auto_number = models.CharField(max_length=9, verbose_name='автомобильный номер', null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата проезда')

    class Meta:
        db_table = 'entryhistories'
        verbose_name = 'Истроия въездов'
        verbose_name_plural = 'Истории въездов'

    def __str__(self):
        return self.auto_number
    

class OutHistory(models.Model):
    yard = models.ForeignKey(
        Yard,
        on_delete=models.PROTECT,
        related_name='out_history',
        verbose_name='какого двора история',
    )
    # auto = models.ForeignKey(
    #     Automobile,
    #     verbose_name='авто', 
    #     on_delete=models.PROTECT
    # )
    auto_number = models.CharField(max_length=9, verbose_name='автомобильный номер', null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата проезда')

    class Meta:
        db_table = 'outhistories'
        verbose_name = 'Истроия выездов'
        verbose_name_plural = 'Истрории выездов'

    def __str__(self):
        return self.auto_number