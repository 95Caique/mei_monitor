from django import forms
from .models import Empresa, Invoice


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ["cnpj", "razao_social", "cidade", "estado", "tipo", "mei_login", "mei_password"]
        widgets = {
            'mei_password': forms.PasswordInput(render_value=False),
        }

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj', '')
        # basic cleanup: remove non-digits
        import re
        digits = re.sub(r"\D", "", cnpj)
        if len(digits) != 14:
            raise forms.ValidationError('CNPJ deve ter 14 dígitos (somente números).')
        return digits


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoice_id', 'total', 'status']
