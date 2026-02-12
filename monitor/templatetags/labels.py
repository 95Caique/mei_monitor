from django import template

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
    try:
        # format number with comma decimal
        return "{:,.2f}".format(float(value)).replace(',', 'X').replace('.', ',').replace('X', '.')
    except Exception:
        return value
