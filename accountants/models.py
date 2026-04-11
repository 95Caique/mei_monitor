from django.db import models
from django.contrib.auth import get_user_model
from monitor.models import Empresa

User = get_user_model()


class AccountantProfile(models.Model):
    """Perfil profissional do contador"""
    ACCOUNT_TYPE_CHOICES = (
        ('FREE', 'Plano Gratuito'),
        ('PREMIUM', 'Plano Premium'),
        ('ENTERPRISE', 'Plano Enterprise'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='accountant_profile')
    professional_name = models.CharField(max_length=200, help_text="Nome profissional/studio")
    cpf = models.CharField(max_length=14, unique=True)
    phone = models.CharField(max_length=20)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='FREE')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Contador"
        verbose_name_plural = "Perfis de Contadores"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.professional_name} ({self.user.username})"

    @property
    def total_clients(self):
        """Total de clientes ativos"""
        return self.clients.filter(is_active=True).count()

    @property
    def total_invoices(self):
        """Total de notas emitidas pelos clientes"""
        from monitor.models import Invoice
        client_empresas = self.clients.filter(is_active=True).values_list('empresa', flat=True)
        return Invoice.objects.filter(empresa_id__in=client_empresas).count()


class ClientAccount(models.Model):
    """Cliente vinculado a um contador"""
    STATUS_CHOICES = (
        ('ACTIVE', 'Ativo'),
        ('INACTIVE', 'Inativo'),
        ('SUSPENDED', 'Suspenso'),
    )

    accountant = models.ForeignKey(AccountantProfile, on_delete=models.CASCADE, related_name='clients')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='accountant_clients')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Taxa mensal cobrada")
    notes = models.TextField(blank=True, help_text="Observações sobre o cliente")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente de Contador"
        verbose_name_plural = "Clientes de Contadores"
        unique_together = ('accountant', 'empresa')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.empresa.razao_social} → {self.accountant.professional_name}"

    @property
    def total_invoices(self):
        """Total de notas do cliente"""
        from monitor.models import Invoice
        return Invoice.objects.filter(empresa=self.empresa).count()

    @property
    def issued_invoices(self):
        """Notas emitidas (status ISSUED)"""
        from monitor.models import Invoice
        return Invoice.objects.filter(empresa=self.empresa, status='ISSUED').count()

    @property
    def cancelled_invoices(self):
        """Notas canceladas (status CANCELLED)"""
        from monitor.models import Invoice
        return Invoice.objects.filter(empresa=self.empresa, status='CANCELLED').count()
