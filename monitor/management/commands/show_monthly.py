from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from monitor.models import Empresa
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Count
import datetime
import json

User = get_user_model()

class Command(BaseCommand):
    help = 'Show monthly aggregates for last 12 months for a given username'

    def add_arguments(self, parser):
        parser.add_argument('--user', dest='username', required=True, help='Username to show data for')

    def handle(self, *args, **options):
        username = options.get('username')
        user = User.objects.filter(username=username).first()
        if not user:
            self.stdout.write(self.style.ERROR(f'User not found: {username}'))
            return
        empresa = Empresa.objects.filter(user=user).first()
        if not empresa:
            self.stdout.write(self.style.ERROR(f'Empresa not found for user: {username}'))
            return

        today = datetime.date.today()
        invoices_12 = empresa.invoices.filter(created_at__date__gte=(today - datetime.timedelta(days=365)))
        monthly_qs = invoices_12.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('total'), count=Count('id')).order_by('month')

        monthly_map = {}
        for m in monthly_qs:
            mv = m.get('month')
            key = mv.strftime('%Y-%m') if hasattr(mv, 'strftime') else str(mv)[:7]
            monthly_map[key] = {'total': float(m.get('total') or 0), 'count': m.get('count', 0)}

        year = today.year
        month = today.month
        months = []
        for offset in range(11, -1, -1):
            y = year
            mo = month - offset
            while mo <= 0:
                mo += 12
                y -= 1
            months.append((y, mo))

        monthly = []
        for (y, mo) in months:
            key = f"{y:04d}-{mo:02d}"
            iso_month = f"{y:04d}-{mo:02d}-01T00:00:00"
            data = monthly_map.get(key, {'total': 0.0, 'count': 0})
            monthly.append({'month': iso_month, 'total': float(data['total']), 'count': int(data.get('count', 0))})

        self.stdout.write(json.dumps(monthly, ensure_ascii=False, indent=2))
