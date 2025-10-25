from django.contrib import admin
from django.db import models
from .models import (
    User,
    Guest,
    GuestEntry
)

from app.yard_control.models import (
    OutHistory,
    EntryHistory,
    Automobile
)

# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import User, Guest


from app.yard_control.admin import YardAdminFilter


@admin.register(GuestEntry)
class GuestEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'guest', 'yard', 'enter_time', 'out_time', 'invite_by', 'created_at']
    list_filter = [YardAdminFilter, 'created_at']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.admin:
            return qs.filter(yard__admin=request.user)
        return qs
    
    def has_module_permission(self, request):
        """Разрешает доступ к модулю в админке"""
        return request.user.is_authenticated and (request.user.is_superuser or request.user.admin)

    def has_view_permission(self, request, obj=None):
        """Разрешает ПРОСМОТР данных"""
        return request.user.is_authenticated and (request.user.is_superuser or request.user.admin)
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

class CustomUserAdmin(UserAdmin):
    list_display = ['id', 'first_name', 'last_name', 'phone', 'admin', 'get_managed_yards', 'is_staff', 'created_at']
    list_filter = ['admin', 'is_staff', 'is_active', 'created_at']
    readonly_fields = ['created_at']
    search_fields = ['username', 'phone']
    
    fieldsets = (
        (None, {'fields': ('username',)}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('Permissions'), {
            'fields': ('admin', 'is_active', 'is_staff', 'is_superuser'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'phone', 'is_staff', 'password1', 'password2'),
        }),
    )
    
    def get_managed_yards(self, obj):
        """Показывает какие дворы администрирует пользователь"""
        yards = obj.admin_yards.all()
        return ", ".join([yard.address for yard in yards]) if yards else "-"
    get_managed_yards.short_description = 'Управляемые дворы'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.admin:
            managed_yards = request.user.admin_yards.all()
            return qs.filter(yards_user__in=managed_yards).distinct()
        return qs
    
    def has_module_permission(self, request):
        """Разрешает доступ к модулю в админке"""
        return request.user.is_authenticated and (request.user.is_superuser or request.user.admin)

    def has_view_permission(self, request, obj=None):
        """Разрешает ПРОСМОТР данных"""
        return request.user.is_authenticated and (request.user.is_superuser or request.user.admin)
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

@admin.register(User)
class UserAdmin(CustomUserAdmin):
    pass


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['id', 'auto_number', 'created_at']
    list_filter = ['created_at']
    search_fields = ['auto_number']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.admin:
            guest_entries = GuestEntry.objects.filter(yard__admin=request.user)
            guest_ids = guest_entries.values_list('guest_id', flat=True)
            return qs.filter(id__in=guest_ids)
        return qs
    
    def has_module_permission(self, request):
        """Разрешает доступ к модулю в админке"""
        return request.user.is_authenticated and (request.user.is_superuser or request.user.admin)

    def has_view_permission(self, request, obj=None):
        """Разрешает ПРОСМОТР данных"""
        return request.user.is_authenticated and (request.user.is_superuser or request.user.admin)
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
