from django import forms
from .models import TelegramProfile


class TelegramProfileForm(forms.ModelForm):
    class Meta:
        model = TelegramProfile
        fields = ("chat_id", "enabled")
        widgets = {
            "chat_id": forms.TextInput(attrs={"placeholder": "Seu chat_id do Telegram"}),
        }
