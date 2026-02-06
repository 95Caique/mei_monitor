from django import forms
from .models import User

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'cnpj', 'ativo', 'password', 'lgpd_consentimento']


        def save(self, commit=True):
            user = super().save(commit=False)
            user.set_password(self.cleaned_data['password'])
            if commit:
                user.save()
            return user