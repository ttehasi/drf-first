from django.contrib import admin

from .models import DemoForm


@admin.register(DemoForm)
class DemoFormAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_of_requester', 'org_name', 'org_type', 'quantity_objects', 'created_at']
    readonly_fields = ['created_at']
    
    def has_module_permission(self, request):
        """Разрешает доступ к модулю в админке"""
        return request.user.is_authenticated and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        """Разрешает ПРОСМОТР данных"""
        return request.user.is_authenticated and request.user.is_superuser
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser