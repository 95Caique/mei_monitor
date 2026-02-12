from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from monitor.models import Empresa
from .forms import CreateUserAndEmpresaForm, EditUserForm

User = get_user_model()


def superuser_required(view_func):
    decorated = login_required(user_passes_test(lambda u: u.is_superuser)(view_func))
    return decorated


@superuser_required
def index(request):
    return render(request, 'admin_panel/index.html')


@superuser_required
def users_list(request):
    q = request.GET.get('q', '').strip()
    users = User.objects.filter(is_superuser=False)
    if q:
        users = users.filter(username__icontains=q) | users.filter(email__icontains=q)
    users = users.order_by('username')
    # For each user, fetch their empresa if exists
    users_with_empresas = []
    for u in users:
        empresa = Empresa.objects.filter(user=u).first()
        # if search by empresa fields, filter here
        if q:
            if empresa:
                if q.lower() not in (empresa.razao_social or '').lower() and q not in (empresa.cnpj or '') and q.lower() not in (u.username or '').lower() and q.lower() not in (u.email or '').lower():
                    continue
        users_with_empresas.append({'user': u, 'empresa': empresa})
    return render(request, 'admin_panel/users_list.html', {'users_with_empresas': users_with_empresas})


@superuser_required
def user_create(request):
    if request.method == 'POST':
        form = CreateUserAndEmpresaForm(request.POST)
        if form.is_valid():
            user, empresa = form.save()
            return redirect('adminpanel:users_list')
    else:
        form = CreateUserAndEmpresaForm()
    return render(request, 'admin_panel/user_create.html', {'form': form})


@superuser_required
def user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = EditUserForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user.email = data.get('email') or user.email
            user.is_active = data.get('is_active', user.is_active)
            user.is_staff = data.get('is_staff', user.is_staff)
            user.is_superuser = data.get('is_superuser', user.is_superuser)
            user.save()
            return redirect('adminpanel:users_list')
    else:
        form = EditUserForm(initial={'email': user.email, 'is_active': user.is_active, 'is_staff': user.is_staff, 'is_superuser': user.is_superuser})
    return render(request, 'admin_panel/user_edit.html', {'form': form, 'user': user})


@superuser_required
def user_toggle_active(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('adminpanel:users_list')
