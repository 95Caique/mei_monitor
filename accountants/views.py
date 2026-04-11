from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta

from .models import AccountantProfile, ClientAccount
from .forms import AccountantProfileForm, ClientAccountForm, ClientAccountUpdateForm
from monitor.models import Invoice


def is_accountant(user):
    """Verifica se é contador"""
    return hasattr(user, 'accountant_profile') and user.accountant_profile.is_active


@login_required
def accountant_dashboard(request):
    """Dashboard para contadores"""
    if not is_accountant(request.user):
        messages.error(request, "Você não tem acesso a esta página.")
        return redirect('dashboard')
    
    profile = request.user.accountant_profile
    clients = profile.clients.all()
    
    # Estatísticas
    total_clients = clients.filter(is_active=True).count()
    total_invoices = Invoice.objects.filter(
        empresa_id__in=clients.values_list('empresa', flat=True)
    ).count()
    issued_invoices = Invoice.objects.filter(
        empresa_id__in=clients.values_list('empresa', flat=True),
        status='ISSUED'
    ).count()
    
    context = {
        'profile': profile,
        'total_clients': total_clients,
        'total_invoices': total_invoices,
        'issued_invoices': issued_invoices,
        'recent_clients': clients[:5],
    }
    return render(request, 'accountants/dashboard.html', context)


@login_required
def accountant_profile_view(request):
    """Editar perfil do contador"""
    if not is_accountant(request.user):
        messages.error(request, "Você não tem acesso a esta página.")
        return redirect('dashboard')
    
    profile = request.user.accountant_profile
    
    if request.method == 'POST':
        form = AccountantProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "✓ Perfil atualizado com sucesso!")
            return redirect('accountants:dashboard')
    else:
        form = AccountantProfileForm(instance=profile)
    
    return render(request, 'accountants/profile.html', {'form': form, 'profile': profile})


@login_required
def clients_list(request):
    """Listar clientes do contador"""
    if not is_accountant(request.user):
        messages.error(request, "Você não tem acesso a esta página.")
        return redirect('dashboard')
    
    profile = request.user.accountant_profile
    clients = profile.clients.select_related('empresa')
    
    # Filtros
    search_q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    
    if search_q:
        clients = clients.filter(
            Q(empresa__razao_social__icontains=search_q) |
            Q(empresa__cnpj__icontains=search_q)
        )
    
    if status_filter:
        clients = clients.filter(status=status_filter)
    
    # Paginação
    paginator = Paginator(clients, 15)
    page_num = request.GET.get('page', 1)
    page = paginator.get_page(page_num)
    
    context = {
        'page': page,
        'search_q': search_q,
        'status_filter': status_filter,
        'status_choices': ClientAccount.STATUS_CHOICES,
    }
    return render(request, 'accountants/clients_list.html', context)


@login_required
def client_detail(request, client_id):
    """Detalhes do cliente e suas notas"""
    if not is_accountant(request.user):
        messages.error(request, "Você não tem acesso a esta página.")
        return redirect('dashboard')
    
    client = get_object_or_404(
        ClientAccount,
        id=client_id,
        accountant=request.user.accountant_profile
    )
    
    # Notas do cliente
    invoices = Invoice.objects.filter(empresa=client.empresa).order_by('-created_at')
    
    # Paginação
    paginator = Paginator(invoices, 20)
    page_num = request.GET.get('page', 1)
    page = paginator.get_page(page_num)
    
    context = {
        'client': client,
        'page': page,
    }
    return render(request, 'accountants/client_detail.html', context)


@login_required
def client_create(request):
    """Adicionar novo cliente"""
    if not is_accountant(request.user):
        messages.error(request, "Você não tem acesso a esta página.")
        return redirect('dashboard')
    
    profile = request.user.accountant_profile
    
    if request.method == 'POST':
        form = ClientAccountForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.accountant = profile
            
            # Verificar se já existe
            existing = ClientAccount.objects.filter(
                accountant=profile,
                empresa=form.empresa
            ).first()
            
            if existing:
                messages.warning(request, "⚠️ Este cliente já está vinculado à sua conta.")
                return redirect('accountants:client_detail', client_id=existing.id)
            
            client.save()
            messages.success(request, f"✓ Cliente {client.empresa.razao_social} adicionado com sucesso!")
            return redirect('accountants:client_detail', client_id=client.id)
    else:
        form = ClientAccountForm()
    
    return render(request, 'accountants/client_create.html', {'form': form})


@login_required
def client_edit(request, client_id):
    """Editar cliente"""
    if not is_accountant(request.user):
        messages.error(request, "Você não tem acesso a esta página.")
        return redirect('dashboard')
    
    client = get_object_or_404(
        ClientAccount,
        id=client_id,
        accountant=request.user.accountant_profile
    )
    
    if request.method == 'POST':
        form = ClientAccountUpdateForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "✓ Cliente atualizado com sucesso!")
            return redirect('accountants:client_detail', client_id=client.id)
    else:
        form = ClientAccountUpdateForm(instance=client)
    
    return render(request, 'accountants/client_edit.html', {
        'form': form,
        'client': client,
    })


@login_required
@require_POST
def client_toggle_status(request, client_id):
    """Ativar/Desativar cliente (AJAX)"""
    if not is_accountant(request.user):
        return JsonResponse({'error': 'Sem permissão'}, status=403)
    
    client = get_object_or_404(
        ClientAccount,
        id=client_id,
        accountant=request.user.accountant_profile
    )
    
    client.is_active = not client.is_active
    client.save()
    
    return JsonResponse({
        'success': True,
        'is_active': client.is_active,
        'message': '✓ Status atualizado'
    })


@login_required
def invoice_create_for_client(request, client_id):
    """Criar nota para cliente (redirecionado do gerenciador)"""
    if not is_accountant(request.user):
        messages.error(request, "Você não tem acesso a esta página.")
        return redirect('dashboard')
    
    client = get_object_or_404(
        ClientAccount,
        id=client_id,
        accountant=request.user.accountant_profile
    )
    
    # Redirecionar para criar nota com empresa pré-selecionada
    return redirect(f"{request.build_absolute_uri('/invoices/')}?empresa={client.empresa.id}")


@login_required
def invoice_cancel_for_client(request, invoice_id, client_id):
    """Cancelar nota de cliente"""
    if not is_accountant(request.user):
        messages.error(request, "Você não tem acesso a esta página.")
        return redirect('dashboard')
    
    client = get_object_or_404(
        ClientAccount,
        id=client_id,
        accountant=request.user.accountant_profile
    )
    
    invoice = get_object_or_404(Invoice, id=invoice_id, empresa=client.empresa)
    
    if request.method == 'POST':
        invoice.status = 'CANCELLED'
        invoice.save()
        messages.success(request, f"✓ Nota {invoice.invoice_id} cancelada com sucesso!")
        return redirect('accountants:client_detail', client_id=client.id)
    
    return render(request, 'accountants/invoice_cancel_confirm.html', {
        'invoice': invoice,
        'client': client,
    })

