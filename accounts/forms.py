from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from monitor.models import Empresa


class RegisterForm(UserCreationForm):
    cnpj = forms.CharField(max_length=14, required=True)
    razao_social = forms.CharField(max_length=255, required=True)

    class Meta:
        model = get_user_model()
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=commit)
        cnpj = self.cleaned_data.get("cnpj")
        razao_social = self.cleaned_data.get("razao_social")

        Empresa.objects.create(
            user=user,
            cnpj=cnpj,
            razao_social=razao_social,
            cidade="-",
            estado="-",
        )
        return user


class LoginForm(forms.Form):
    # kept simple; view uses AuthenticationForm by default
    pass
