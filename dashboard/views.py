from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from decimal import Decimal
import datetime
from django.http import HttpResponse
import csv
from django.utils.dateparse import parse_date
from django.db.models import Q
import json


from monitor.models import Empresa
from monitor.forms import EmpresaForm, InvoiceForm


@login_required
def home(request):
    empresa = Empresa.objects.filter(user=request.user).first()
    alerts = []
    alerts_page = None

    if not empresa:
        if request.method == 'POST':
            form = EmpresaForm(request.POST)
            if form.is_valid():
                empresa = form.save(commit=False)
                empresa.user = request.user
                empresa.ativa = True
                empresa.save()
                return redirect('dashboard')
        else:
            form = EmpresaForm()
        return render(request, 'dashboard/home.html', {'empresa': None, 'form': form, 'alerts': alerts})

    if empresa:
        all_alerts = empresa.alerts.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(all_alerts, 20)
        try:
            alerts_page = paginator.page(page)
        except PageNotAnInteger:
            alerts_page = paginator.page(1)
        except EmptyPage:
            alerts_page = paginator.page(paginator.num_pages)
        alerts = alerts_page.object_list

    total_sum = Decimal('0.00')
    if empresa:
        qs = empresa.invoices.filter(status__iexact='ISSUED')
        agg = qs.aggregate(total_sum=Sum('total'))
        raw = agg.get('total_sum')
        if raw is None:
            try:
                total_sum = sum((Decimal(inv.total) for inv in qs), Decimal('0.00'))
            except Exception:
                total_sum = Decimal('0.00')
        else:
            try:
                total_sum = Decimal(raw)
            except Exception:
                try:
                    total_sum = Decimal(str(raw))
                except Exception:
                    total_sum = Decimal('0.00')

    invoices_json = '[]'
    if empresa:
        invoices_list = list(empresa.invoices.order_by('-created_at').values('invoice_id','total','status','created_at'))
        invoices_json = json.dumps(invoices_list, default=str)

    return render(request, "dashboard/home.html", {"empresa": empresa, "alerts": alerts, "alerts_page": alerts_page, "total_invoices_sum": total_sum, "invoices_json": invoices_json})


@login_required
def create_invoice(request):
    empresa = Empresa.objects.filter(user=request.user).first()
    if not empresa:
        return redirect('dashboard')

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.empresa = empresa
            invoice.save()
            return redirect('dashboard')
    else:
        form = InvoiceForm()
    return render(request, 'dashboard/create_invoice.html', {'form': form})


@login_required
def reports(request):
    empresa = Empresa.objects.filter(user=request.user).first()
    if not empresa:
        return redirect('dashboard')

    start_param = request.GET.get('start')
    end_param = request.GET.get('end')
    today = datetime.date.today()
    if start_param:
        start_date = parse_date(start_param)
    else:
        start_date = today - datetime.timedelta(days=29)
    if end_param:
        end_date = parse_date(end_param)
    else:
        end_date = today

    invoices_qs = empresa.invoices.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)

    status_counts_qs = invoices_qs.values('status').annotate(count=Count('id'))
    status_counts = list(status_counts_qs)
    STATUS_PT = {'ISSUED':'Emitida','CANCELLED':'Cancelada','DRAFT':'Rascunho'}
    status_labels = [STATUS_PT.get(s.get('status','').upper(), s.get('status','') or 'UNKNOWN') for s in status_counts]
    status_data = [s.get('count',0) for s in status_counts]

    daily_qs = invoices_qs.annotate(day=TruncDay('created_at')).values('day').annotate(total=Sum('total'), count=Count('id')).order_by('day')
    daily = []
    for d in daily_qs:
        day_val = d.get('day')
        if hasattr(day_val, 'isoformat'):
            d['day'] = day_val.isoformat()
        # ensure total is float
        try:
            d['total'] = float(d.get('total') or 0)
        except Exception:
            d['total'] = 0
        daily.append(d)

    invoices_list = list(invoices_qs.order_by('-created_at').values('invoice_id','total','status','created_at'))
    invoices_json = json.dumps(invoices_list, default=str)

    invoices_12 = empresa.invoices.filter(created_at__date__gte=(today - datetime.timedelta(days=365)))
    monthly_qs = invoices_12.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('total'), count=Count('id')).order_by('month')
    monthly_map = {}
    for m in monthly_qs:
        mv = m.get('month')
        if hasattr(mv, 'strftime'):
            key = mv.strftime('%Y-%m')
        else:
            key = str(mv)[:7]
        try:
            total_val = float(m.get('total') or 0)
        except Exception:
            total_val = 0.0
        monthly_map[key] = {'total': total_val, 'count': m.get('count', 0)}

    monthly = []
    for i in range(11, -1, -1):
        month_date = (today.replace(day=1) - datetime.timedelta(days=0)).replace(day=1) - datetime.timedelta(days=i*30)
    monthly = []
    year = today.year
    month = today.month
    months = []
    for offset in range(11, -1, -1):
        y = year
        m = month - offset
        while m <= 0:
            m += 12
            y -= 1
        months.append((y, m))
    for (y, m) in months:
        key = f"{y:04d}-{m:02d}"
        iso_month = f"{y:04d}-{m:02d}-01T00:00:00"
        data = monthly_map.get(key, {'total': 0.0, 'count': 0})
        monthly.append({'month': iso_month, 'total': float(data['total']), 'count': int(data.get('count', 0))})

    daily_json = json.dumps(daily)
    monthly_json = json.dumps(monthly)

    yearly = empresa.invoices.annotate(year=TruncYear('created_at')).values('year').annotate(total=Sum('total'), count=Count('id')).order_by('year')

    context = {
        'empresa': empresa,
        'status_counts': status_counts,
        'status_labels': status_labels,
        'status_data': status_data,
        'daily': list(daily),
        'monthly': list(monthly),
        'daily_json': daily_json,
        'monthly_json': monthly_json,
        'yearly': list(yearly),
        'start_date': start_date,
        'end_date': end_date,
        'invoices_json': invoices_json,
    }
    return render(request, 'dashboard/reports.html', context)


@login_required
def reports_export(request):
    empresa = Empresa.objects.filter(user=request.user).first()
    if not empresa:
        return redirect('dashboard')

    start_param = request.GET.get('start')
    end_param = request.GET.get('end')
    start_date = parse_date(start_param) if start_param else None
    end_date = parse_date(end_param) if end_param else None

    qs = empresa.invoices.all()
    if start_date:
        qs = qs.filter(created_at__date__gte=start_date)
    if end_date:
        qs = qs.filter(created_at__date__lte=end_date)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="invoices_{empresa.cnpj}.csv"'
    writer = csv.writer(response)
    writer.writerow(['invoice_id','created_at','status','total'])
    for inv in qs.order_by('-created_at'):
        writer.writerow([inv.invoice_id, inv.created_at.isoformat(), inv.status, str(inv.total)])
    return response

