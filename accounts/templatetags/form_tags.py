from django import template
register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})

@register.filter(name='format_cnpj')
def format_cnpj(cnpj):
    """Formata CNPJ: 11111111000191 -> 11.111.111/0001-91"""
    if not cnpj:
        return cnpj
    cnpj_str = str(cnpj).strip()
    # Remove formatação anterior se existir
    cnpj_str = ''.join(c for c in cnpj_str if c.isdigit())
    if len(cnpj_str) != 14:
        return cnpj_str
    return f"{cnpj_str[0:2]}.{cnpj_str[2:5]}.{cnpj_str[5:8]}/{cnpj_str[8:12]}-{cnpj_str[12:14]}"

