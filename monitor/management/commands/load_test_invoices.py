import random
import time
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from monitor.models import Empresa, Invoice
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Load test: create many invoices for a given user/cnpj to exercise charts and alerts'

    def add_arguments(self, parser):
        parser.add_argument('--user', dest='username', help='Username owning the company (ex: caique)')
        parser.add_argument('--cnpj', dest='cnpj', help='CNPJ of the company')
        parser.add_argument('--count', dest='count', type=int, default=200, help='Numero de notas criadas.')
        parser.add_argument('--cancel-prob', dest='cancel_prob', type=float, default=0.2, help='Probability each invoice will be cancelled')
        parser.add_argument('--update-prob', dest='update_prob', type=float, default=0.3, help='Probability to perform a total update after creation')
        parser.add_argument('--clear', action='store_true', help='Remove previous generated invoices starting with LOAD-')

    def handle(self, *args, **options):
        username = options.get('username')
        cnpj = options.get('cnpj')
        count = options.get('count') or 0
        cancel_prob = options.get('cancel_prob')
        update_prob = options.get('update_prob')
        clear = options.get('clear')

        empresa = None
        if username:
            user = User.objects.filter(username=username).first()
            if not user:
                self.stdout.write(self.style.ERROR(f'User not found: {username}'))
                return
            empresa = Empresa.objects.filter(user=user).first()
            if not empresa:
                self.stdout.write(self.style.ERROR(f'No empresa for user: {username}'))
                return
        elif cnpj:
            empresa = Empresa.objects.filter(cnpj=cnpj).first()
            if not empresa:
                self.stdout.write(self.style.ERROR(f'Empresa not found for CNPJ: {cnpj}'))
                return
        else:
            self.stdout.write(self.style.ERROR('You must provide --user or --cnpj'))
            return

        if clear:
            deleted = 0
            for inv in empresa.invoices.filter(invoice_id__startswith='LOAD-'):
                inv.delete()
                deleted += 1
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} previous LOAD- invoices'))

        created = 0
        updated = 0
        cancelled = 0
        base_ts = int(time.time())

        for i in range(count):
            invoice_id = f'LOAD-{base_ts}-{i}'
            total = round(random.uniform(10.0, 10000.0), 2)
            status = 'ISSUED'
            inv = Invoice.objects.create(empresa=empresa, invoice_id=invoice_id, total=total, status=status)
            created += 1

            # optionally update total
            if random.random() < update_prob:
                new_total = round(total * random.uniform(0.5, 1.5), 2)
                inv.total = new_total
                inv.save()
                updated += 1

            # optionally cancel
            if random.random() < cancel_prob:
                inv.status = 'CANCELLED'
                inv.save()
                cancelled += 1

            # small progress output occasionally
            if (i + 1) % 50 == 0:
                self.stdout.write(f'Created {i+1}/{count} invoices...')

        self.stdout.write(self.style.SUCCESS(f'Done. Created={created} Updated={updated} Cancelled={cancelled}'))
