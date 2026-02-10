from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import TelegramProfileForm
from .models import TelegramProfile


@login_required
def edit_profile(request):
    profile, _ = TelegramProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = TelegramProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('telegram_profile')
    else:
        form = TelegramProfileForm(instance=profile)

    return render(request, 'telegram_bot/profile.html', {'form': form})
