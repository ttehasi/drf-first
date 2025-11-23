from django.db import models


class DemoForm(models.Model):
    name_of_requester = models.CharField(verbose_name='ФИО запросившего')
    phone = models.CharField(verbose_name='Номер телефона запросифшего')
    org_name = models.CharField(verbose_name='Название организации')
    org_type = models.CharField(verbose_name='Тип организации')
    quantity_objects = models.IntegerField(verbose_name='Количество объектов')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки формы')
    
    class Meta:
        db_table = 'demoforms'
        verbose_name = 'Запрос'
        verbose_name_plural = 'Запросы'
        
    def __str__(self):
        return self.org_name