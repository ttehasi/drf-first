from django.contrib import admin
from .models import (
    Yard,
    BlackList,
    Invite,
    Automobile,
    EntryHistory,
    OutHistory
)

class YardAdminFilter(admin.SimpleListFilter):
    """Фильтр для выбора двора в админке"""
    title = 'Двор'
    parameter_name = 'yard'
    
    def lookups(self, request, model_admin):
        if request.user.admin and not request.user.is_superuser:
            yards = Yard.objects.filter(admin=request.user)
            return [(yard.id, yard.address) for yard in yards]
        return []
    
    def queryset(self, request, queryset):
        if self.value() and request.user.admin and not request.user.is_superuser:
            return self.filter_queryset(queryset, self.value())
        return queryset
    
    def filter_queryset(self, queryset, yard_id):
        """Фильтрует queryset по выбранному двору"""
        model_name = queryset.model.__name__
        yard = Yard.objects.get(id=yard_id)
        
        if model_name == 'GuestEntry':
            return queryset.filter(yard=yard)
        elif model_name == 'BlackList':
            return queryset.filter(yard=yard)
        elif model_name == 'Invite':
            return queryset.filter(yard=yard)
        elif model_name == 'EntryHistory':
            return queryset.filter(yard=yard)
        elif model_name == 'OutHistory':
            return queryset.filter(yard=yard)
        elif model_name == 'Automobile':
            return queryset.filter(yards_auto=yard)
        return queryset


@admin.register(Automobile)
class AutomobileAdmin(admin.ModelAdmin):
    list_display = ['id', 'auto_number', 'owner', 'is_confirmed', 'is_guest', 'expires_at', 'created_at']
    list_filter = [YardAdminFilter, 'is_confirmed', 'is_guest', 'created_at']
    search_fields = ['auto_number']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.admin:
            return qs.filter(yards_auto__admin=request.user).distinct()
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


@admin.register(Yard)
class YardAdmin(admin.ModelAdmin):
    list_display = ['id', 'address', 'admin', 'users_count', 'automobiles_count', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    
    def users_count(self, obj):
        return obj.users.count()
    users_count.short_description = 'Кол-во пользователей'
    
    def automobiles_count(self, obj):
        return obj.automobiles.count()
    automobiles_count.short_description = 'Кол-во машин'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.admin:
            return qs.filter(admin=request.user)
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
        return request.user.is_superuser
    
    
@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'yard', 'created_at']
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
    
    
@admin.register(EntryHistory)
class EntryHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'yard', 'auto', 'created_at']
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

@admin.register(OutHistory)
class OutHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'yard', 'auto', 'created_at']
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

@admin.register(BlackList)
class BlackListAdmin(admin.ModelAdmin):
    list_display = ['id', 'auto_number', 'yard', 'created_at']
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
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if request.user.admin and not request.user.is_superuser:
            form.base_fields['yard'].queryset = Yard.objects.filter(admin=request.user)
        return form
    
    def has_add_permission(self, request):
        return request.user.is_authenticated and (request.user.is_superuser or request.user.admin)
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and request.user.admin:
            return obj.yard.admin == request.user
        return False
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and request.user.admin:
            return obj.yard.admin == request.user
        return False
    