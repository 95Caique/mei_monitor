import os
import json
import random
from django.core.management.base import BaseCommand
from monitor.models import Empresa, Invoice
from django.utils import timezone

REMOTE_DIR = '/tmp/mei_remote'


def ensure_remote_dir():
    os.makedirs(REMOTE_DIR, exist_ok=True)


def remote_file_path(cnpj):
    return os.path.join(REMOTE_DIR, f"{cnpj}.json")


def generate_initial_remote(cnpj):
    invoices = []
    count = random.randint(1, 3)
    for i in range(count):
        invoice_id = f'INIT-{i+1}'
        total = round(random.uniform(50, 5000), 2)
        status = random.choice(['ISSUED', 'CANCELLED'])
        invoices.append({'invoice_id': invoice_id, 'total': total, 'status': status, 'created_at': timezone.now().isoformat()})
    return invoices


def write_remote(cnpj, invoices):
    path = remote_file_path(cnpj)
    with open(path, 'w') as f:
        json.dump(invoices, f, default=str)


def load_remote(cnpj):
    path = remote_file_path(cnpj)
    if not os.path.exists(path):
        inv = generate_initial_remote(cnpj)
        write_remote(cnpj, inv)
        return inv
    with open(path, 'r') as f:
        return json.load(f)


def mutate_remote(cnpj):
    invoices = load_remote(cnpj)
    action = random.choice(['create', 'update', 'delete'])
    if action == 'create' or not invoices:
        invoice_id = f'MUT-{random.randint(100,999)}'
        invoices.append({'invoice_id': invoice_id, 'total': round(random.uniform(10,3000),2), 'status': 'ISSUED', 'created_at': timezone.now().isoformat()})
    elif action == 'update':
        inv = random.choice(invoices)
        inv['total'] = round(inv.get('total', 0) * random.uniform(0.5, 1.5),2)
        inv['status'] = random.choice(['ISSUED','CANCELLED'])
    elif action == 'delete':
        invoices.pop(random.randrange(len(invoices)))
    write_remote(cnpj, invoices)
    return invoices


class Command(BaseCommand):
    help = 'Poll MEI accounts (simulated). If --mutate-remote is provided simulates a change on the remote before polling.'

    def add_arguments(self, parser):
        parser.add_argument('--mutate-remote', action='store_true', help='Simulate a change on the remote state before polling')
        parser.add_argument('--for-user', dest='username', help='Run only for a specific user')

    def handle(self, *args, **options):
        ensure_remote_dir()
        username = options.get('username')
        mutate = options.get('mutate_remote')

        qs = Empresa.objects.filter(ativa=True)
        if username:
            qs = qs.filter(user__username=username)

        if not qs.exists():
            self.stdout.write('No active empresas found to poll.')
            return

        for empresa in qs:
            cnpj = empresa.cnpj
            self.stdout.write(f'Polling {empresa.razao_social} ({cnpj})')
            if mutate:
                self.stdout.write(' - mutating remote state')
                mutate_remote(cnpj)

            remote = load_remote(cnpj)
            # Build maps
            remote_map = {r['invoice_id']: r for r in remote}
            local_invoices = {inv.invoice_id: inv for inv in empresa.invoices.all()}

            for inv_id, remote_inv in remote_map.items():
                if inv_id in local_invoices:
                    local = local_invoices[inv_id]
                    changed = False
                    if float(local.total) != float(remote_inv['total']):
                        local.total = remote_inv['total']
                        changed = True
                    if local.status != remote_inv['status']:
                        local.status = remote_inv['status']
                        changed = True
                    if changed:
                        local.save()
                        self.stdout.write(f' - updated local invoice {inv_id}')
                else:
                    # mark invoices created from remote as is_remote=True so local user-created invoices are preserved
                    Invoice.objects.create(empresa=empresa, invoice_id=inv_id, total=remote_inv['total'], status=remote_inv['status'], is_remote=True)
                    self.stdout.write(f' - created local invoice {inv_id}')

            local_ids = set(local_invoices.keys())
            remote_ids = set(remote_map.keys())
            to_delete = local_ids - remote_ids
            for inv_id in to_delete:
                local = local_invoices.get(inv_id)
                # only delete invoices that originated from the remote source
                if local and getattr(local, 'is_remote', False):
                    local.delete()
                    self.stdout.write(f' - deleted remote invoice {inv_id}')
                else:
                    self.stdout.write(f' - keeping local invoice {inv_id} (not remote)')

            empresa.last_checked = timezone.now()
            empresa.save(update_fields=['last_checked'])

        self.stdout.write('Polling done.')
