from django.db import models
from django.conf import settings


class TelegramProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="telegram_profile",
    )
    chat_id = models.CharField(max_length=64, blank=True, null=True, help_text="Telegram chat id")
    enabled = models.BooleanField(default=False, verbose_name="Ativo", help_text="Indica se as notificações do Telegram estão ativadas para este usuário.")
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TelegramProfile(user={self.user.username}, enabled={self.enabled})"
