from django.contrib import admin
from .models import (
    User,
    Guest,
    GuestEntry
)

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'phone', 'admin', 'created_at']
    
    
@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['id', 'auto_number', 'invite_by', 'created_at']
    
    
@admin.register(GuestEntry)
class GuestEntriesAdmin(admin.ModelAdmin):
    list_display = ['id', 'entry_timeout', 'enter_time', 'out_time', 'guest', 'yard', 'created_at']