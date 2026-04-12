from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from .forms import RegisterForm, UserProfileForm, ChangePasswordForm


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(request.GET.get("next", "dashboard"))
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def profile(request):
    """View para editar perfil do usuário"""
    
    if request.method == 'POST':
        # Verificar qual formulário foi enviado
        if 'profile-form' in request.POST:
            form = UserProfileForm(request.POST, request.FILES, instance=request.user)
            password_form = ChangePasswordForm(request.user)
            
            if form.is_valid():
                form.save()
                request.user.refresh_from_db()
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('profile')
        
        elif 'password-form' in request.POST:
            form = UserProfileForm(instance=request.user)
            password_form = ChangePasswordForm(request.user, request.POST)
            
            if password_form.is_valid():
                # Alterar senha
                new_password = password_form.cleaned_data['new_password1']
                request.user.set_password(new_password)
                request.user.save()
                
                messages.success(request, 'Senha alterada com sucesso!')
                # Re-fazer login para não perder a sessão
                login(request, request.user)
                return redirect('profile')
        else:
            form = UserProfileForm(instance=request.user)
            password_form = ChangePasswordForm(request.user)
    else:
        form = UserProfileForm(instance=request.user)
        password_form = ChangePasswordForm(request.user)
    
    context = {
        'form': form,
        'password_form': password_form,
    }
    
    return render(request, 'accounts/profile.html', context)
