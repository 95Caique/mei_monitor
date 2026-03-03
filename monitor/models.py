from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Empresa(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="empresas"
    )

    cnpj = models.CharField(
        max_length=14,
        unique=True,
        help_text="Digite apenas números"
    )

    razao_social = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)

    mei_login = models.CharField(max_length=255, blank=True, null=True, help_text='Login/CPF do MEI para integração')
    mei_password = models.CharField(max_length=255, blank=True, null=True, help_text='Senha (guarde com segurança)')

    tipo = models.CharField(
        max_length=10,
        choices=(
            ("MEI", "MEI"),
            ("ME", "ME"),
        ),
        default="MEI"
    )

    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    # new fields
    last_checked = models.DateTimeField(null=True, blank=True)
    # Default status set to a simple, human-friendly value for new empresas
    # Previously defaulted to "unknown" which showed as UNKNOWN in the UI
    status = models.CharField(max_length=50, default="ATIVO")

    def __str__(self):
        return f"{self.cnpj} - {self.razao_social}"


class Alert(models.Model):
    LEVEL_CHOICES = (
        ("INFO", "Informativo"),
        ("WARNING", "Aviso"),
        ("CRITICAL", "Crítico"),
    )
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='alerts')
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='INFO')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.level}] {self.empresa.cnpj} - {self.message[:50]}"


class Invoice(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='invoices')
    invoice_id = models.CharField(max_length=128, verbose_name ='Preencha o numero da nota',
    help_text='Preencha o numero ou dê um nome à nota para identificação')
    total = models.DecimalField(max_digits=12,verbose_name ='Total Faturado', decimal_places=2)
    status = models.CharField(max_length=20,
    choices=(('ISSUED','Emitida'),('CANCELLED','Cancelada'),('DRAFT','Rascunho')), default='Emitida')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_remote = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = ('empresa', 'invoice_id')

    def __str__(self):
        return f"Invoice {self.invoice_id} ({self.empresa.cnpj}) - {self.total} - {self.status}"
