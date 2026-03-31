import re
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from monitor.models import Empresa


def validar_cnpj(cnpj):
    cnpj = re.sub(r'\D', '', cnpj)

    if len(cnpj) != 14:
        return False

    if cnpj in (cnpj[0] * 14 for _ in range(1)):
        return False

    def calcular_digito(cnpj, peso):
        soma = sum(int(d) * p for d, p in zip(cnpj, peso))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    peso1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    peso2 = [6] + peso1

    digito1 = calcular_digito(cnpj[:12], peso1)
    digito2 = calcular_digito(cnpj[:12] + digito1, peso2)

    return cnpj[-2:] == digito1 + digito2


class RegisterForm(UserCreationForm):
    cnpj = forms.CharField(max_length=14, required=True)
    razao_social = forms.CharField(max_length=255, required=True)

    class Meta:
        model = get_user_model()
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()

        blacklist = {
            "email@email.com",
            "test@test.com",
            "admin@admin.com"
        }

        if email in blacklist:
            raise ValidationError("Digite um e-mail válido.")

        if re.match(r'^(.)\1+@', email):
            raise ValidationError("E-mail inválido.")

        dominios_bloqueados = ["tempmail.com", "mailinator.com"]
        dominio = email.split("@")[-1]

        if dominio in dominios_bloqueados:
            raise ValidationError("E-mails temporários não são permitidos.")

        return email

    def clean_username(self):
        username = self.cleaned_data.get("username", "")

        if username.isdigit():
            raise ValidationError("Usuário não pode ser apenas números.")

        if len(set(username)) == 1:
            raise ValidationError("Usuário inválido.")

        if len(username) < 3:
            raise ValidationError("Usuário muito curto.")

        return username

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get("cnpj")

        if not validar_cnpj(cnpj):
            raise ValidationError("CNPJ inválido.")

        # evita duplicado
        if Empresa.objects.filter(cnpj=cnpj).exists():
            raise ValidationError("Já existe uma empresa com este CNPJ.")

        return cnpj

    def clean_razao_social(self):
        nome = self.cleaned_data.get("razao_social")

        if len(nome) < 3:
            raise ValidationError("Nome muito curto.")

        if nome.isdigit():
            raise ValidationError("Nome inválido.")

        return nome

    def save(self, commit=True):
        user = super().save(commit=commit)

        Empresa.objects.create(
            user=user,
            cnpj=self.cleaned_data.get("cnpj"),
            razao_social=self.cleaned_data.get("razao_social"),
            cidade="-",
            estado="-",
        )

        return user