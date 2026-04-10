from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

User = settings.AUTH_USER_MODEL


class SystemLog(models.Model):
    """
    Modelo para registrar todas as ações importantes do sistema
    """
    LOG_LEVELS = (
        ('DEBUG', 'Debug'),
        ('INFO', 'Informação'),
        ('WARNING', 'Aviso'),
        ('ERROR', 'Erro'),
        ('CRITICAL', 'Crítico'),
    )
    
    ACTION_TYPES = (
        ('CREATE', 'Criação'),
        ('UPDATE', 'Atualização'),
        ('DELETE', 'Exclusão'),
        ('CANCEL', 'Cancelamento'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('ERROR', 'Erro'),
        ('ALERT', 'Alerta'),
        ('EXPORT', 'Exportação'),
        ('IMPORT', 'Importação'),
        ('OTHER', 'Outro'),
    )
    
    # Dados do usuário
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_logs',
        db_index=True
    )
    
    # Tipo e nível
    level = models.CharField(
        max_length=10,
        choices=LOG_LEVELS,
        default='INFO',
        db_index=True
    )
    
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        default='OTHER',
        db_index=True
    )
    
    # Descrição
    title = models.CharField(
        max_length=255,
        help_text='Título ou descrição curta da ação'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Descrição detalhada do que aconteceu'
    )
    
    # Contexto
    module = models.CharField(
        max_length=100,
        db_index=True,
        help_text='Módulo ou app que gerou o log (ex: invoice, empresa, etc)'
    )
    
    action_object_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text='ID do objeto que foi modificado'
    )
    
    action_object_type = models.CharField(
        max_length=100,
        blank=True,
        help_text='Tipo de objeto (ex: Invoice, Empresa, etc)'
    )
    
    # IP e informações de acesso
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        db_index=True
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text='User Agent do navegador'
    )
    
    # Dados adicionais
    old_values = models.JSONField(
        null=True,
        blank=True,
        help_text='Valores antigos (para auditorias)'
    )
    
    new_values = models.JSONField(
        null=True,
        blank=True,
        help_text='Novos valores (para auditorias)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    
    # Meta
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Log do Sistema'
        verbose_name_plural = 'Logs do Sistema'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['level', '-created_at']),
            models.Index(fields=['action_type', '-created_at']),
            models.Index(fields=['module', '-created_at']),
        ]
    
    def __str__(self):
        return f"[{self.level}] {self.title} - {self.created_at.strftime('%d/%m/%Y %H:%M:%S')}"
    
    @classmethod
    def log(cls, user=None, level='INFO', action_type='OTHER', title='', 
            description='', module='', action_object_id=None, 
            action_object_type='', ip_address=None, user_agent='',
            old_values=None, new_values=None):
        """
        Método utilitário para criar logs facilmente
        """
        return cls.objects.create(
            user=user,
            level=level,
            action_type=action_type,
            title=title,
            description=description,
            module=module,
            action_object_id=action_object_id,
            action_object_type=action_object_type,
            ip_address=ip_address,
            user_agent=user_agent,
            old_values=old_values,
            new_values=new_values
        )

