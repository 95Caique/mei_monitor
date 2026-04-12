from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

STATUS_MAP = {
    'ISSUED': 'Emitida',
    'CANCELLED': 'Cancelada',
    'DRAFT': 'Rascunho',
}

LEVEL_MAP = {
    'INFO': 'Info',
    'WARNING': 'Atenção',
    'CRITICAL': 'Crítico',
}


@register.filter
def status_pt(value):
    if not value:
        return ''
    return STATUS_MAP.get(value.upper(), value)


@register.filter
def level_pt(value):
    if not value:
        return ''
    return LEVEL_MAP.get(value.upper(), value)


@register.filter
def currency_pt(value):
    """Format a number as pt-BR currency without the R$ prefix, e.g. 735167.03 -> 735.167,03
    Robust to Decimal, float and string inputs.
    """
    try:
        v = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return value
    try:
        v = v.quantize(Decimal('0.01'))
        sign = '-' if v < 0 else ''
        if v < 0:
            v = -v
        int_part = int(v)
        frac = int((v - Decimal(int_part)) * 100)
        int_str = f"{int_part:,}".replace(',', '.')
        return f"{sign}{int_str},{frac:02d}"
    except Exception:
        return str(value)


@register.filter
def format_cnpj(value):
    """Format a CNPJ string to XX.XXX.XXX/XXXX-XX format
    Input: 89047826000110
    Output: 89.047.826/0001-10
    """
    if not value:
        return value
    
    # Remove non-digits
    cnpj = str(value).replace('.', '').replace('/', '').replace('-', '')
    
    # Validate length
    if len(cnpj) != 14:
        return value
    
    # Format: XX.XXX.XXX/XXXX-XX
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"
