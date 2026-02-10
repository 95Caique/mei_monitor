from django import forms
from django.contrib.auth import get_user_model
from monitor.models import Empresa

User = get_user_model()


class CreateUserAndEmpresaForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)

    cnpj = forms.CharField(max_length=14)
    razao_social = forms.CharField(max_length=255)
    plano = forms.ChoiceField(choices=(('FREE','FREE'),('PRO','PRO')))
    ativa = forms.BooleanField(required=False, initial=True)

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(username=data['username'], email=data.get('email'), password=data['password'])
        empresa = Empresa.objects.create(
            user=user,
            cnpj=data['cnpj'],
            razao_social=data['razao_social'],
            cidade='-',
            estado='-',
            tipo='MEI',
            ativa=data.get('ativa', True),
        )
        return user, empresa


class EditUserForm(forms.Form):
    email = forms.EmailField(required=False)
    is_active = forms.BooleanField(required=False)
    is_staff = forms.BooleanField(required=False)
    is_superuser = forms.BooleanField(required=False)
