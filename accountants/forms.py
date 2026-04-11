from django import forms
from .models import AccountantProfile, ClientAccount
from monitor.models import Empresa


class AccountantProfileForm(forms.ModelForm):
    class Meta:
        model = AccountantProfile
        fields = ['professional_name', 'cpf', 'phone']
        widgets = {
            'professional_name': forms.TextInput(attrs={
                'placeholder': 'Nome do studio/empresa de contabilidade',
                'class': 'form-control'
            }),
            'cpf': forms.TextInput(attrs={
                'placeholder': '000.000.000-00',
                'class': 'form-control',
                'maxlength': '14'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '(00) 99999-9999',
                'class': 'form-control',
                'maxlength': '20'
            }),
        }


class ClientAccountForm(forms.ModelForm):
    empresa_cnpj = forms.CharField(
        max_length=18,
        label="CNPJ da Empresa",
        widget=forms.TextInput(attrs={
            'placeholder': '00.000.000/0000-00',
            'class': 'form-control',
        })
    )

    class Meta:
        model = ClientAccount
        fields = ['status', 'monthly_fee', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'monthly_fee': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'class': 'form-control',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Observações sobre o cliente...',
                'rows': 4,
                'class': 'form-control'
            }),
        }

    def clean_empresa_cnpj(self):
        cnpj = self.cleaned_data.get('empresa_cnpj')
        # Remove formatting
        cnpj_clean = cnpj.replace('.', '').replace('/', '').replace('-', '')
        
        try:
            empresa = Empresa.objects.get(cnpj=cnpj_clean)
            self.empresa = empresa
            return cnpj
        except Empresa.DoesNotExist:
            raise forms.ValidationError(f"Nenhuma empresa encontrada com o CNPJ {cnpj}")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.empresa = self.empresa
        if commit:
            instance.save()
        return instance


class ClientAccountUpdateForm(forms.ModelForm):
    class Meta:
        model = ClientAccount
        fields = ['status', 'monthly_fee', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'monthly_fee': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'class': 'form-control',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Observações sobre o cliente...',
                'rows': 4,
                'class': 'form-control'
            }),
        }

