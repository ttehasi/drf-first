from django.contrib import admin
from .models import (
    User,
    Guest,
    GuestEntry
)

from app.yard_control.models import (
    OutHistory,
    EntryHistory
)

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'phone', 'admin', 'created_at']
    
    
@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    # average_time_entry = admin.
    list_display = ['id', 'auto_number', 'created_at', ]
    
    # def average_time_entry(self, obj):
    #     entry_queryset = EntryHistory.objects.filter(auto_number=obj.auto_number)
    #     out_queryset = OutHistory.objects.filter(auto=obj.auto_number)
    #     return str(type(out_queryset))
    
    # average_time_entry.short_description = 'Среднее время посещения'
    
    
@admin.register(GuestEntry)
class GuestEntriesAdmin(admin.ModelAdmin):
    list_display = ['id', 'entry_timeout', 'enter_time', 'out_time', 'invite_by', 'guest', 'yard', 'created_at']