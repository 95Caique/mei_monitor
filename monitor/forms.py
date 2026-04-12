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
        import re
        digits = re.sub(r"\D", "", cnpj)
        if len(digits) != 14:
            raise forms.ValidationError('CNPJ deve ter 14 dígitos (somente números).')
        return digits


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoice_id', 'total', 'status']

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

    def clean_invoice_id(self):
        invoice_id = self.cleaned_data.get('invoice_id')
        if not invoice_id:
            return invoice_id
        if self.empresa is not None:
            from .models import Invoice
            if Invoice.objects.filter(empresa=self.empresa, invoice_id=invoice_id).exists():
                raise forms.ValidationError('Já existe uma nota com esse nome para a sua empresa.')
        return invoice_id


class InvoiceEditForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoice_id', 'total', 'status']

    def __init__(self, *args, empresa=None, instance=None, **kwargs):
        super().__init__(*args, instance=instance, **kwargs)
        self.empresa = empresa
        self.instance = instance

    def clean_invoice_id(self):
        invoice_id = self.cleaned_data.get('invoice_id')
        if not invoice_id:
            return invoice_id

        if self.instance and self.instance.invoice_id == invoice_id:
            return invoice_id

        if self.empresa is not None:
            from .models import Invoice
            if Invoice.objects.filter(empresa=self.empresa, invoice_id=invoice_id).exists():
                raise forms.ValidationError('Já existe uma nota com esse nome para a sua empresa.')
        return invoice_id
