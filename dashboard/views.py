from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
        # paginate alerts, 10 per page
        page = request.GET.get('page', 1)
        paginator = Paginator(all_alerts, 10)
        try:
            alerts_page = paginator.page(page)
        except PageNotAnInteger:
            alerts_page = paginator.page(1)
        except EmptyPage:
            alerts_page = paginator.page(paginator.num_pages)
        alerts = alerts_page.object_list
    return render(request, "dashboard/home.html", {"empresa": empresa, "alerts": alerts, "alerts_page": alerts_page})


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
