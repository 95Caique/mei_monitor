from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = ('Enviar notificações ao Telegram (wrapper em português)\n\nEste comando delega para o comando existente '
            '`send_telegram_notifications`.')

    def handle(self, *args, **options):
        call_command('send_telegram_notifications')
        self.stdout.write(self.style.SUCCESS('Comando wrapper `enviar_notificacoes_telegram` executado com sucesso.'))

