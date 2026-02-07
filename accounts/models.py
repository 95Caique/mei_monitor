from random import choices

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    cnpj = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        help_text="CNPJ dp MEI (Digite apenas números)"
    )

    plano = models.CharField(
        max_length=20,
        choices=(
            ("FREE", "Free"),
            ("PRO", "Pro"),
        ),
        default="FREE"
    )

    is_active = models.BooleanField(default=True)
    lgpd_consentimento = models.BooleanField(
        default=False,
        help_text="Usuário aceitou os termos LGPD"
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)
    cancelado_em = models.BooleanField(default=False)

    def __str__(self):
        return self.username