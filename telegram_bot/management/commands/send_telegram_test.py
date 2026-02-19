from django.core.management.base import BaseCommand
from django.conf import settings
from telegram_bot.services import send_message

class Command(BaseCommand):
    help = 'Enviar mensagem de teste para telegram usando TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID nas settings (ou usar --token/--chat)'

    def add_arguments(self, parser):
        parser.add_argument('--token', help='Telegram bot token (overrides settings)')
        parser.add_argument('--chat', help='Telegram chat id (overrides settings)')
        parser.add_argument('--text', help='Text to send', default='Teste do MEI Monitor')

    def handle(self, *args, **options):
        token = options.get('token') or getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        chat = options.get('chat') or getattr(settings, 'TELEGRAM_CHAT_ID', None)
        text = options.get('text')

        success = send_message(token, chat, text)
        if success:
            self.stdout.write(self.style.SUCCESS('Mensagem enviada com sucesso'))
        else:
            self.stderr.write('Falha ao enviar a mensagem')

