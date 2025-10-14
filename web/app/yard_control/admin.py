from django.contrib import admin
from .models import (
    Yard,
    BlackList,
    Invite,
    Automobile
)

# Register your models here.
@admin.register(Yard)
class YardAdmin(admin.ModelAdmin):
    list_display = ['id', 'address', 'admin', 'created_at']
    
    
@admin.register(BlackList)
class BlackListAdmin(admin.ModelAdmin):
    list_display = ['id', 'auto_number', 'yard', 'created_at']
    
    
@admin.register(Automobile)
class AutomobileAdmin(admin.ModelAdmin):
    list_display = ['id', 'auto_number', 'is_confirmed', 'owner', 'expires_at', 'created_at']
    

@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'yard', 'created_at']