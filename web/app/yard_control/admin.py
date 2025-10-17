from django.contrib import admin
from .models import (
    Yard,
    BlackList,
    Invite,
    Automobile,
    EntryHistory,
    OutHistory
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
    

@admin.register(EntryHistory)
class EntryHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'yard', 'auto', 'created_at']
    
    
@admin.register(OutHistory)
class OutHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'yard', 'auto', 'created_at']