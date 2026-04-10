from django.contrib import admin
from .models import SystemLog


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    """
    Admin customizado para visualizar e gerenciar logs do sistema
    """
    
    list_display = ('title', 'level', 'action_type', 'user', 'module', 'created_at')
    list_filter = ('level', 'action_type', 'module', 'created_at')
    search_fields = ('title', 'description', 'user__username', 'ip_address')
    readonly_fields = (
        'user', 'level', 'action_type', 'title', 'description',
        'module', 'action_object_id', 'action_object_type',
        'ip_address', 'user_agent', 'old_values', 'new_values', 'created_at'
    )
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'level', 'action_type', 'title', 'created_at')
        }),
        ('Descrição', {
            'fields': ('description',)
        }),
        ('Contexto da Ação', {
            'fields': ('module', 'action_object_type', 'action_object_id')
        }),
        ('Dados de Auditoria', {
            'fields': ('old_values', 'new_values'),
            'classes': ('collapse',)
        }),
        ('Informações de Acesso', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        # Logs são criados automaticamente, não permitem adição manual
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Logs não podem ser deletados (auditoria)
        return False


