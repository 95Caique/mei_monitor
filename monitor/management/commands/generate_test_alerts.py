from django.core.management.base import BaseCommand
from django.utils import timezone
from monitor.models import Empresa, Alert
from django.contrib.auth import get_user_model
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate test alerts for active empresas (useful for testing notifications and dashboard)'

    def add_arguments(self, parser):
        parser.add_argument('--for-user', dest='username', help='Generate alerts only for this username')
        parser.add_argument('--max-alerts', dest='max_alerts', type=int, default=2, help='Maximum alerts to create per empresa')
        parser.add_argument('--simulate', action='store_true', help='Do not create alerts, only simulate and print')

    def handle(self, *args, **options):
        username = options.get('username')
        max_alerts = options.get('max_alerts')
        simulate = options.get('simulate')

        empresas = Empresa.objects.filter(ativa=True)
        if username:
            empresas = empresas.filter(user__username=username)

        total_created = 0
        levels = ['INFO', 'WARNING', 'CRITICAL']
        messages = [
            'Atualização cadastral detectada.',
            'Pendência fiscal encontrada.',
            'Mudança no status do registro.',
            'Possível bloqueio em análise.',
            'Documento vencido próximo do prazo.'
        ]

        if not empresas.exists():
            self.stdout.write('No active empresas found for given criteria.')
            return

        for e in empresas:
            n = random.randint(0, max_alerts)
            highest = 'INFO'
            created_for_empresa = 0
            for i in range(n):
                lvl = random.choices(levels, weights=(60, 30, 10), k=1)[0]
                msg = random.choice(messages)
                if simulate:
                    self.stdout.write(f'[SIM] {e.cnpj} -> [{lvl}] {msg}')
                else:
                    Alert.objects.create(empresa=e, level=lvl, message=msg)
                    total_created += 1
                    created_for_empresa += 1
                if levels.index(lvl) > levels.index(highest):
                    highest = lvl

            status_map = {'INFO': 'ok', 'WARNING': 'attention', 'CRITICAL': 'critical'}
            e.status = status_map.get(highest, 'unknown')
            e.last_checked = timezone.now()
            e.save()

            if not simulate:
                self.stdout.write(f'Empresa {e.cnpj}: created {created_for_empresa} alerts; status set to {e.status}')
            else:
                self.stdout.write(f'Empresa {e.cnpj}: simulated {created_for_empresa} alerts; would set status {status_map.get(highest)}')

        self.stdout.write(f'Total alerts created: {total_created}')
