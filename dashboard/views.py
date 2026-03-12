from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from decimal import Decimal
import datetime
from django.http import HttpResponse, JsonResponse
import csv
from django.utils.dateparse import parse_date
from django.db.models import Q
import json
from django.db import IntegrityError, transaction


from monitor.models import Empresa
from monitor.forms import EmpresaForm, InvoiceForm, InvoiceEditForm
from monitor.models import Invoice, Alert


@login_required
def home(request):
    empresa = Empresa.objects.filter(user=request.user).first()
    alerts = []
    alerts_page = None
    alerts_compact_pages = []
    alerts_all_json = '[]'

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

        try:
            current = int(alerts_page.number)
        except Exception:
            current = 1
        total = paginator.num_pages

        def compact_pages(current, total, delta=2):
            pages = []
            if total <= (2 * delta + 5):
                return list(range(1, total + 1))
            pages.append(1)
            left = current - delta
            right = current + delta
            if left > 2:
                pages.append('...')
            for i in range(max(2, left), min(total - 1, right) + 1):
                pages.append(i)
            if right < total - 1:
                pages.append('...')
            pages.append(total)
            return pages

        alerts_compact_pages = compact_pages(current, total)
        try:
            alerts_list = list(all_alerts.order_by('-created_at').values('id','level','message','created_at'))
            alerts_all_json = json.dumps(alerts_list, default=str)
        except Exception:
            alerts_all_json = '[]'

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

    annual_total = Decimal('0.00')
    mei_limit_info = None
    if empresa:
        from django.utils import timezone
        now = timezone.now()
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        annual_qs = empresa.invoices.filter(status__iexact='ISSUED', created_at__gte=year_start)
        annual_agg = annual_qs.aggregate(total_sum=Sum('total'))
        annual_raw = annual_agg.get('total_sum')
        if annual_raw:
            try:
                annual_total = Decimal(annual_raw)
            except Exception:
                annual_total = Decimal('0.00')

        # Informações sobre o limite MEI
        mei_limit = Decimal('81000.00')
        remaining = mei_limit - annual_total
        percentage = (annual_total / mei_limit * 100) if mei_limit > 0 else 0

        # Determinar nível do alerta baseado na proximidade do limite
        if annual_total >= mei_limit:
            alert_level = 'danger'
            alert_message = f"Limite ultrapassado em R$ {annual_total - mei_limit:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        elif annual_total >= Decimal('80000.00'):
            alert_level = 'danger'
            alert_message = f"Muito próximo do limite! Restam apenas R$ {remaining:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        elif annual_total >= Decimal('75000.00'):
            alert_level = 'warning'
            alert_message = f"Atenção! Restam R$ {remaining:,.2f} para o limite".replace(',', 'X').replace('.', ',').replace('X', '.')
        elif annual_total >= Decimal('60000.00'):
            alert_level = 'warning'
            alert_message = f"Restam R$ {remaining:,.2f} para o limite anual".replace(',', 'X').replace('.', ',').replace('X', '.')
        elif annual_total >= Decimal('50000.00'):
            alert_level = 'info'
            alert_message = f"Você já utilizou {percentage:.1f}% do limite anual"
        else:
            alert_level = 'success'
            alert_message = f"Restam R$ {remaining:,.2f} para o limite anual".replace(',', 'X').replace('.', ',').replace('X', '.')

        mei_limit_info = {
            'annual_total': annual_total,
            'limit': mei_limit,
            'remaining': remaining,
            'percentage': float(percentage),
            'alert_level': alert_level,
            'alert_message': alert_message,
            'year': now.year
        }

    invoices_json = '[]'
    if empresa:
        invoices_list = list(empresa.invoices.order_by('-created_at').values('invoice_id','total','status','created_at'))
        invoices_json = json.dumps(invoices_list, default=str)

    return render(request, "dashboard/home.html", {"empresa": empresa, "alerts": alerts, "alerts_page": alerts_page, "alerts_compact_pages": alerts_compact_pages, "alerts_all_json": alerts_all_json, "total_invoices_sum": total_sum, "invoices_json": invoices_json, "annual_total": annual_total, "mei_limit_info": mei_limit_info})


@login_required
def create_invoice(request):
    empresa = Empresa.objects.filter(user=request.user).first()
    if not empresa:
        return redirect('dashboard')

    if request.method == 'POST':
        form = InvoiceForm(request.POST, empresa=empresa)
        if form.is_valid():
            # checar unicidade: não permitir same invoice_id para a mesma empresa
            invoice_id = form.cleaned_data.get('invoice_id')
            if empresa.invoices.filter(invoice_id=invoice_id).exists():
                form.add_error('invoice_id', 'Já existe uma nota com esse ID para a sua empresa.')
            else:
                invoice = form.save(commit=False)
                invoice.empresa = empresa
                try:
                    with transaction.atomic():
                        invoice.save()
                    return redirect('dashboard')
                except IntegrityError:
                    form.add_error(None, 'Erro ao salvar a nota: ID já existe (condição de concorrência).')
    else:
        form = InvoiceForm(empresa=empresa)
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


@login_required
def notifications_api(request):
    """API endpoint para buscar notificações em tempo real"""
    empresa = Empresa.objects.filter(user=request.user).first()
    if not empresa:
        return JsonResponse({'alerts': [], 'count': 0})

    # Buscar apenas alertas recentes (últimas 24 horas por padrão)
    from django.utils import timezone
    since = timezone.now() - timezone.timedelta(hours=24)

    # Permitir filtrar por timestamp do último check
    last_check = request.GET.get('since')
    if last_check:
        try:
            from django.utils.dateparse import parse_datetime
            parsed_since = parse_datetime(last_check)
            if parsed_since is not None:
                since = parsed_since
        except:
            pass

    # Buscar alertas novos (garantir que since nunca seja None)
    if since is None:
        since = timezone.now() - timezone.timedelta(hours=24)

    alerts = empresa.alerts.filter(created_at__gte=since).order_by('-created_at')[:10]

    # Converter para JSON
    alerts_data = []
    for alert in alerts:
        alerts_data.append({
            'id': alert.id,
            'level': alert.level,
            'message': alert.message,
            'created_at': alert.created_at.isoformat(),
            'level_display': {
                'INFO': 'Informativo',
                'WARNING': 'Atenção',
                'CRITICAL': 'Crítico'
            }.get(alert.level, alert.level)
        })

    # Contar alertas não lidos (últimas 24h)
    unread_count = empresa.alerts.filter(created_at__gte=since).count()

    return JsonResponse({
        'alerts': alerts_data,
        'count': unread_count,
        'timestamp': timezone.now().isoformat()
    })


@login_required
def manage_invoices(request):
    """View para listar e gerenciar todas as notas"""
    empresa = Empresa.objects.filter(user=request.user).first()
    if not empresa:
        return redirect('dashboard')

    # Filtros
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    invoices_qs = empresa.invoices.all()

    if search:
        invoices_qs = invoices_qs.filter(
            Q(invoice_id__icontains=search) |
            Q(total__icontains=search)
        )

    if status_filter:
        invoices_qs = invoices_qs.filter(status=status_filter)

    # Ordenação e paginação
    invoices_qs = invoices_qs.order_by('-created_at')
    paginator = Paginator(invoices_qs, 15)
    page = request.GET.get('page', 1)

    try:
        invoices_page = paginator.page(page)
    except PageNotAnInteger:
        invoices_page = paginator.page(1)
    except EmptyPage:
        invoices_page = paginator.page(paginator.num_pages)

    # Estatísticas
    total_invoices = empresa.invoices.count()
    issued_count = empresa.invoices.filter(status='ISSUED').count()
    cancelled_count = empresa.invoices.filter(status='CANCELLED').count()
    draft_count = empresa.invoices.filter(status='DRAFT').count()

    context = {
        'empresa': empresa,
        'invoices': invoices_page,
        'search': search,
        'status_filter': status_filter,
        'total_invoices': total_invoices,
        'issued_count': issued_count,
        'cancelled_count': cancelled_count,
        'draft_count': draft_count,
        'status_choices': [
            ('', 'Todos'),
            ('ISSUED', 'Emitidas'),
            ('CANCELLED', 'Canceladas'),
            ('DRAFT', 'Rascunho')
        ]
    }

    return render(request, 'dashboard/manage_invoices.html', context)


@login_required
def edit_invoice(request, invoice_id):
    """View para editar uma nota específica"""
    empresa = Empresa.objects.filter(user=request.user).first()
    if not empresa:
        return redirect('dashboard')

    try:
        invoice = Invoice.objects.get(id=invoice_id, empresa=empresa)
    except Invoice.DoesNotExist:
        from django.contrib import messages
        messages.error(request, 'Nota não encontrada.')
        return redirect('manage_invoices')

    if request.method == 'POST':
        # Criar form customizado que não valida uniqueness do invoice_id para edição
        form = InvoiceForm(request.POST, instance=invoice, empresa=empresa)

        # Remove validação de unicidade para edição
        form.fields['invoice_id'].validators = []

        if form.is_valid():
            # Validar unicidade manualmente apenas se o invoice_id mudou
            new_invoice_id = form.cleaned_data.get('invoice_id')
            if new_invoice_id != invoice.invoice_id:
                if empresa.invoices.filter(invoice_id=new_invoice_id).exists():
                    form.add_error('invoice_id', 'Já existe uma nota com esse ID para a sua empresa.')
                else:
                    try:
                        with transaction.atomic():
                            form.save()
                        from django.contrib import messages
                        messages.success(request, f'Nota {invoice.invoice_id} editada com sucesso!')
                        return redirect('manage_invoices')
                    except IntegrityError:
                        form.add_error('invoice_id', 'Erro ao salvar: ID já existe.')
            else:
                # Se o invoice_id não mudou, salvar normalmente
                try:
                    with transaction.atomic():
                        form.save()
                    from django.contrib import messages
                    messages.success(request, f'Nota {invoice.invoice_id} editada com sucesso!')
                    return redirect('manage_invoices')
                except Exception as e:
                    form.add_error(None, f'Erro ao salvar: {str(e)}')
    else:
        form = InvoiceForm(instance=invoice, empresa=empresa)

    context = {
        'form': form,
        'invoice': invoice,
        'empresa': empresa
    }

    return render(request, 'dashboard/edit_invoice.html', context)


@login_required
def cancel_invoice(request, invoice_id):
    """View para cancelar uma nota"""
    empresa = Empresa.objects.filter(user=request.user).first()
    if not empresa:
        return redirect('dashboard')

    try:
        invoice = Invoice.objects.get(id=invoice_id, empresa=empresa)
    except Invoice.DoesNotExist:
        from django.contrib import messages
        messages.error(request, 'Nota não encontrada.')
        return redirect('manage_invoices')

    if request.method == 'POST':
        if invoice.status == 'CANCELLED':
            from django.contrib import messages
            messages.warning(request, 'Esta nota já está cancelada.')
            return redirect('manage_invoices')

        # Cancelar a nota
        old_status = invoice.status
        invoice.status = 'CANCELLED'

        try:
            with transaction.atomic():
                invoice.save()

            from django.contrib import messages
            messages.success(request, f'Nota {invoice.invoice_id} cancelada com sucesso!')

            # O signal já vai criar o alert automaticamente

        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Erro ao cancelar nota: {str(e)}')

        return redirect('manage_invoices')

    context = {
        'invoice': invoice,
        'empresa': empresa
    }

    return render(request, 'dashboard/cancel_invoice.html', context)


@login_required
def delete_invoice(request, invoice_id):
    """View para excluir uma nota permanentemente"""
    empresa = Empresa.objects.filter(user=request.user).first()
    if not empresa:
        return redirect('dashboard')

    try:
        invoice = Invoice.objects.get(id=invoice_id, empresa=empresa)
    except Invoice.DoesNotExist:
        from django.contrib import messages
        messages.error(request, 'Nota não encontrada.')
        return redirect('manage_invoices')

    if request.method == 'POST':
        invoice_id_display = invoice.invoice_id

        try:
            with transaction.atomic():
                invoice.delete()

            from django.contrib import messages
            messages.success(request, f'Nota {invoice_id_display} excluída permanentemente!')

            # O signal já vai criar o alert automaticamente

        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Erro ao excluir nota: {str(e)}')

        return redirect('manage_invoices')

    context = {
        'invoice': invoice,
        'empresa': empresa
    }

    return render(request, 'dashboard/delete_invoice.html', context)
