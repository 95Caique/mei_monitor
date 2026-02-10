from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from monitor.models import Empresa
from monitor.forms import EmpresaForm, InvoiceForm


@login_required
def home(request):
    empresa = Empresa.objects.filter(user=request.user).first()
    alerts = []

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
        alerts = empresa.alerts.all()[:10]
    return render(request, "dashboard/home.html", {"empresa": empresa, "alerts": alerts})


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
