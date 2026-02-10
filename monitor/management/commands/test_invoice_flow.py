from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from monitor.models import Empresa, Invoice, Alert

User = get_user_model()


class Command(BaseCommand):
    help = 'Test invoice flow: create invoice and print alert counts'

    def handle(self, *args, **options):
        user = User.objects.filter(username='testclient').first()
        if not user:
            self.stdout.write('No testclient user')
            return
        empresa = Empresa.objects.filter(user=user).first()
        if not empresa:
            self.stdout.write('No empresa for testclient')
            return
        self.stdout.write(f'Empresa: {empresa}')
        inv = Invoice.objects.create(empresa=empresa, invoice_id='CMD-TST-1', total=55.0, status='ISSUED')
        self.stdout.write(f'Created invoice {inv}')
        alerts = Alert.objects.filter(empresa=empresa)
        self.stdout.write(f'Alerts for empresa: {alerts.count()}')
        for a in alerts:
            self.stdout.write(f'- {a.level} {a.message} at {a.created_at}')
