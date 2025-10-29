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
    Automobile,
    Yard
)

# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import User, Guest
from django.utils import timezone
from datetime import timedelta

from app.yard_control.admin import YardAdminFilter


# class GuestentryFilter(admin.SimpleListFilter): # гостевые заявки фильтр
#     """Фильтр для выбора двора в админке"""
#     title = 'Статус'
#     parameter_name = 'status'
    
#     # def lookups(self, request, model_admin):
#     #     if request.user.admin and not request.user.is_superuser:
#     #         yards = Yard.objects.filter(admin=request.user)
#     #         return [(yard.id, yard.address) for yard in yards]
#     #     return []
    
#     # def queryset(self, request, queryset):
#     #     if self.value() and request.user.admin and not request.user.is_superuser:
#     #         return self.filter_queryset(queryset, self.value())
#     #     return queryset
    
#     # def lookups(self, request, model_admin):
#     #     if request.user.is_superuser:
#     #         yards = Yard.objects.all()
#     #         return [(yard.id, yard.address) for yard in yards]
#     #     elif getattr(request.user, 'admin', False):
#     #         yards = Yard.objects.filter(admin=request.user)
#     #         return [(yard.id, yard.address) for yard in yards]
#     #     return []
    
#     def lookups(self, request, model_admin):
#         if request.user.is_superuser:
#             yards = Yard.objects.all()
#             guestsentry = GuestEntry.objects.all()
#             return [(0, 'Неактивные'), (1, 'Активные')]
#         elif getattr(request.user, 'admin', False):
#             yards = Yard.objects.filter(admin=request.user)
#             return [(yard.id, yard.address) for yard in yards]
#         return []
    
#     def queryset(self, request, queryset):
#         if self.value():
#             if request.user.is_superuser:
#                 return self.filter_queryset(queryset, self.value())
#             elif getattr(request.user, 'admin', False):
#                 try:
#                     yard = Yard.objects.get(id=self.value(), admin=request.user)
#                     return self.filter_queryset(queryset, self.value())
#                 except Yard.DoesNotExist:
#                     return queryset.none()
#         return queryset
    
#     def filter_queryset(self, queryset, yard_id):
#         """Фильтрует queryset по выбранному двору"""
#         model_name = queryset.model.__name__
#         yard = Yard.objects.get(id=yard_id)
        
#         if model_name == 'GuestEntry':
            
#             return queryset.filter(yard=yard)
#         return queryset


@admin.register(GuestEntry)
class GuestEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'entry_timeout', 'guest', 'yard', 'enter_time', 'out_time', 'invite_by', 'created_at']
    # list_filter = [YardAdminFilter, 'created_at']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.admin:
            return qs.filter(yard__admin=request.user)
        return qs
    
    def get_list_filter(self, request):
        list_filter = ['created_at']
        yard_filter = YardAdminFilter(
        request=request,
        params=request.GET.copy(), 
        model=self.model,  # или self.model._meta
        model_admin=self
    )
        available_choices = yard_filter.lookups(request, self)
        self.choise_count = len(available_choices)
        choise_count = len(available_choices)
        if choise_count > 1:
            list_filter.insert(0, YardAdminFilter)
        return list_filter
    
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
    # list_display = ['id', 'first_name', 'last_name', 'phone', 'admin', 'is_staff', 'created_at']
    list_filter = [YardAdminFilter, 'admin', 'is_staff', 'is_active', 'created_at']
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
    
    def get_list_display(self, request):
        if request.user.is_superuser:
            return ['id', 'first_name', 'last_name', 'phone', 'admin', 'get_managed_yards', 'is_staff', 'created_at']
        return ['id', 'first_name', 'last_name', 'phone', 'created_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.admin:
            managed_yards = request.user.admin_yards.all()
            return qs.filter(yards_user__in=managed_yards).distinct()
        return qs
    
    def get_list_filter(self, request):
        if request.user.is_superuser:
            list_filter = [ 'admin', 'is_staff', 'is_active', 'created_at']
        else:
            list_filter = ['created_at']
        yard_filter = YardAdminFilter(
        request=request,
        params=request.GET.copy(), 
        model=self.model,  # или self.model._meta
        model_admin=self
    )
        available_choices = yard_filter.lookups(request, self)
        self.choise_count = len(available_choices)
        choise_count = len(available_choices)
        if choise_count > 1:
            list_filter.insert(0, YardAdminFilter)
        return list_filter
    
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
    list_display = ['id', 'auto_number', 'entry_count', 'average_enrty_time', 'created_at']
    # list_filter = [YardAdminFilter, 'created_at']
    search_fields = ['auto_number']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        self.request = request
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.admin:
            guest_entries = GuestEntry.objects.filter(yard__admin=request.user)
            guest_ids = guest_entries.values_list('guest_id', flat=True)
            return qs.filter(id__in=guest_ids)
        return qs
    
    def get_list_filter(self, request):
        list_filter = ['created_at']
        yard_filter = YardAdminFilter(
        request=request,
        params=request.GET.copy(), 
        model=self.model,  # или self.model._meta
        model_admin=self
    )
        available_choices = yard_filter.lookups(request, self)
        self.choise_count = len(available_choices)
        self.choise = available_choices
        choise_count = len(available_choices)
        if choise_count > 1:
            list_filter = [YardAdminFilter, 'created_at']
        else:
            list_filter = ['created_at']
        return list_filter
    
    def entry_count(self, obj):
        auto = Automobile.objects.get(auto_number=obj.auto_number)
        yard_id = self.request.GET.get('yard')
        if yard_id:
            yard = Yard.objects.get(id=yard_id)
            entry_queryset = EntryHistory.objects.filter(auto=auto, yard=yard)
            return entry_queryset.count()
        elif not yard_id and self.choise_count > 1:
            return 'Выберете конкретный двор'
        else:
            yard_id = self.choise[0][0]
            yard = Yard.objects.get(id=yard_id)
            entry_queryset = EntryHistory.objects.filter(auto=auto, yard=yard)
            return entry_queryset.count()
    entry_count.short_description = 'Количество посещений'
    
    def format_timedelta(self, td):
        total_seconds = int(td.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours == 0:
            return 'Менее часа'
        
        parts = []
        
        if days > 0:
            if days % 10 == 1 and days % 100 != 11:
                parts.append(f"{days} день")
            elif 2 <= days % 10 <= 4 and (days % 100 < 10 or days % 100 >= 20):
                parts.append(f"{days} дня")
            else:
                parts.append(f"{days} дней")
        
        if hours > 0:
            if hours % 10 == 1 and hours % 100 != 11:
                parts.append(f"{hours} час")
            elif 2 <= hours % 10 <= 4 and (hours % 100 < 10 or hours % 100 >= 20):
                parts.append(f"{hours} часа")
            else:
                parts.append(f"{hours} часов")
        
        return " ".join(parts)
    
    def average_enrty_time(self, obj):
        auto = Automobile.objects.get(auto_number=obj.auto_number)
        yard_id = self.request.GET.get('yard')
        if yard_id:
            yard = Yard.objects.get(id=yard_id)
            entry_queryset = EntryHistory.objects.filter(auto=auto, yard=yard)
            out_queryset = OutHistory.objects.filter(auto=auto, yard=yard)
            combined_history = list(entry_queryset) + list(out_queryset)
            combined_history.sort(key=lambda x: x.created_at)
            if len(combined_history) % 2 != 0:
                combined_history = combined_history[:-1]
            sum_time = timezone.now() - timezone.now()
            for index, history in enumerate(combined_history):
                if index % 2 == 0:
                    entry = history.created_at
                else:
                    sum_time += history.created_at - entry
            if out_queryset.count() == 0:
                return '-'
            aver_time = sum_time / out_queryset.count()
            return self.format_timedelta(aver_time)
        elif not yard_id and self.choise_count > 1:
            return 'Выберете конкретный двор'
        else:
            yard_id = self.choise[0][0]
            yard = Yard.objects.get(id=yard_id)
            entry_queryset = EntryHistory.objects.filter(auto=auto, yard=yard)
            out_queryset = OutHistory.objects.filter(auto=auto, yard=yard)
            combined_history = list(entry_queryset) + list(out_queryset)
            combined_history.sort(key=lambda x: x.created_at)
            if len(combined_history) % 2 != 0:
                combined_history = combined_history[:-1]
            sum_time = timezone.now() - timezone.now()
            for index, history in enumerate(combined_history):
                if index % 2 == 0:
                    entry = history.created_at
                else:
                    sum_time += history.created_at - entry
            if out_queryset.count() == 0:
                return '-'
            aver_time = sum_time / out_queryset.count()
            return self.format_timedelta(aver_time)
    average_enrty_time.short_description = 'Среднее время посещения'
    
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
