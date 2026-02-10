from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    plano = models.CharField(
        max_length=20,
        choices=(
            ("FREE", "Free"),
            ("PRO", "Pro"),
        ),
        default="FREE",
    )

    lgpd_consentimento = models.BooleanField(
        default=False,
        help_text="Usuário aceitou os termos LGPD",
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username