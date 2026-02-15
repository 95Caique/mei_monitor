from django.core.management.base import BaseCommand
from django.conf import settings
from telegram_bot.models import TelegramProfile
from monitor.models import Empresa, Alert
import logging

from telegram_bot.services import send_message

logger = logging.getLogger(__name__)

LEVEL_PT = {
    'INFO': 'Informe',
    'WARNING': 'Atenção',
    'CRITICAL': 'Crítico',
}


class Command(BaseCommand):
    help = "Enviar notificações do Telegram para usuários habilitados (executado pelo cron)"

    def handle(self, *args, **options):
        token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
        profiles = TelegramProfile.objects.filter(enabled=True).select_related("user")
        if not profiles.exists():
            self.stdout.write("Nenhum perfil do Telegram conectado, nada a fazer.")
            return

        for profile in profiles:
            user = profile.user
            empresas = Empresa.objects.filter(user=user, ativa=True)
            pending_alerts = Alert.objects.filter(empresa__in=empresas, notified=False).order_by('created_at')
            if not pending_alerts.exists():
                self.stdout.write(f"Não há alertas pendentes para {user.username}")
                continue

            for alert in pending_alerts:
                level = LEVEL_PT.get(alert.level.upper(), alert.level)
                text = f"[{level}] {alert.message}"
                sent = send_message(token, profile.chat_id, text)
                if sent:
                    alert.notified = True
                    alert.save(update_fields=['notified'])
                    self.stdout.write(f"Alerta enviado{alert.id} to {user.username}")
                else:
                    self.stdout.write(f"Falha ao enviar alerta {alert.id} to {user.username}")
