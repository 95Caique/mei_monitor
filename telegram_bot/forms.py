from django import forms
from .models import TelegramProfile


class TelegramProfileForm(forms.ModelForm):
    test_message = forms.CharField(required=False, widget=forms.TextInput(attrs={"placeholder": "Escreva sua mensagem de teste (opcional)"}))

    class Meta:
        model = TelegramProfile
        fields = ("bot_token", "chat_id", "enabled")
        widgets = {
            "chat_id": forms.TextInput(attrs={"placeholder": "Seu chat_id do Telegram"}),
            "bot_token": forms.TextInput(attrs={"placeholder": "Token do bot (ex: 123456:ABC-DEF...)"}),
        }

    def clean_chat_id(self):
        v = self.cleaned_data.get('chat_id')
        if v:
            return v.strip()
        return v

    def clean_bot_token(self):
        v = self.cleaned_data.get('bot_token')
        if v:
            return v.strip()
        return v
