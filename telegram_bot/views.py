from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import TelegramProfileForm
from .models import TelegramProfile
from .services import send_message
from django.conf import settings


@login_required
def edit_profile(request):
    profile, _ = TelegramProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = TelegramProfileForm(request.POST, instance=profile)
        if form.is_valid():
            tp = form.save()
            test_text = form.cleaned_data.get('test_message')
            if test_text:
                token = tp.bot_token or getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
                chat = tp.chat_id
                ok = send_message(token, chat, test_text)
                if ok:
                    messages.success(request, 'Mensagem de teste enviada com sucesso!')
                else:
                    messages.error(request, 'Falha ao enviar a mensagem de teste. Verifique o token/chat_id.')
            else:
                messages.success(request, 'Configurações salvas.')
            return redirect('telegram_bot:profile')
    else:
        form = TelegramProfileForm(instance=profile)

    return render(request, 'telegram_bot/profile.html', {'form': form, 'profile': profile})
