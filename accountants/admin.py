from django.contrib import admin
from .models import AccountantProfile, ClientAccount


@admin.register(AccountantProfile)
class AccountantProfileAdmin(admin.ModelAdmin):
    list_display = ('professional_name', 'user', 'account_type', 'is_active', 'created_at')
    list_filter = ('account_type', 'is_active', 'created_at')
    search_fields = ('professional_name', 'cpf', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informações Profissionais', {
            'fields': ('user', 'professional_name', 'cpf', 'phone')
        }),
        ('Plano', {
            'fields': ('account_type', 'is_active')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ClientAccount)
class ClientAccountAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'accountant', 'status', 'is_active', 'created_at')
    list_filter = ('status', 'is_active', 'accountant', 'created_at')
    search_fields = ('empresa__razao_social', 'empresa__cnpj', 'accountant__professional_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Relacionamentos', {
            'fields': ('accountant', 'empresa')
        }),
        ('Status e Configuração', {
            'fields': ('status', 'is_active', 'monthly_fee')
        }),
        ('Notas', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at')
        }),
    )
