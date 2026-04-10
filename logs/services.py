"""
Serviço de logging para o sistema
Fornece funções utilitárias para registrar ações em todo o sistema
"""

from logs.models import SystemLog


def get_client_ip(request):
    """
    Obtém o IP real do cliente, considerando proxies
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """
    Obtém o User Agent do navegador
    """
    return request.META.get('HTTP_USER_AGENT', '')


def log_action(request=None, user=None, level='INFO', action_type='OTHER',
               title='', description='', module='', action_object_id=None,
               action_object_type='', old_values=None, new_values=None):
    """
    Registra uma ação no sistema
    
    Args:
        request: objeto request do Django (opcional)
        user: usuário (se não fornecido, tenta obter de request)
        level: nível do log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        action_type: tipo de ação (CREATE, UPDATE, DELETE, CANCEL, LOGIN, etc)
        title: título descritivo da ação
        description: descrição detalhada
        module: módulo/app que gerou a ação
        action_object_id: ID do objeto afetado
        action_object_type: tipo do objeto (Invoice, Empresa, etc)
        old_values: dicionário com valores antigos (para auditorias)
        new_values: dicionário com novos valores (para auditorias)
    """
    
    # Se não forneceu usuário, tenta obter de request
    if user is None and request and request.user.is_authenticated:
        user = request.user
    
    # Obtém informações da request
    ip_address = get_client_ip(request) if request else None
    user_agent = get_user_agent(request) if request else ''
    
    # Cria o log
    log = SystemLog.objects.create(
        user=user,
        level=level,
        action_type=action_type,
        title=title,
        description=description,
        module=module,
        action_object_id=action_object_id,
        action_object_type=action_object_type,
        ip_address=ip_address,
        user_agent=user_agent,
        old_values=old_values,
        new_values=new_values
    )
    
    return log


def log_invoice_action(request=None, user=None, invoice=None, action_type='OTHER',
                      old_values=None, new_values=None):
    """
    Registra ações relacionadas a notas fiscais
    """
    title = f"Nota Fiscal #{invoice.invoice_id}" if invoice else "Nota Fiscal"
    
    action_titles = {
        'CREATE': f'Criação da nota fiscal #{invoice.invoice_id}',
        'UPDATE': f'Atualização da nota fiscal #{invoice.invoice_id}',
        'DELETE': f'Exclusão da nota fiscal #{invoice.invoice_id}',
        'CANCEL': f'Cancelamento da nota fiscal #{invoice.invoice_id}',
    }
    
    title = action_titles.get(action_type, title)
    
    return log_action(
        request=request,
        user=user,
        level='INFO',
        action_type=action_type,
        title=title,
        description=f'Nota fiscal {invoice.invoice_id} ({invoice.total})',
        module='invoice',
        action_object_id=invoice.id if invoice else None,
        action_object_type='Invoice',
        old_values=old_values,
        new_values=new_values
    )


def log_error(request=None, user=None, title='', description='', module='',
              exception=None):
    """
    Registra erros do sistema
    """
    if exception:
        description = f"{description}\n\nException: {str(exception)}"
    
    return log_action(
        request=request,
        user=user,
        level='ERROR',
        action_type='ERROR',
        title=title,
        description=description,
        module=module
    )


def log_authentication(request=None, user=None, action='LOGIN'):
    """
    Registra login/logout
    """
    action_type = 'LOGIN' if action == 'LOGIN' else 'LOGOUT'
    username = user.username if user else 'Unknown'
    
    return log_action(
        request=request,
        user=user,
        level='INFO',
        action_type=action_type,
        title=f'{action} do usuário {username}',
        description=f'Usuário {username} realizou {action.lower()}',
        module='authentication'
    )


def get_logs_for_user(user, limit=50):
    """
    Obtém os últimos logs de um usuário
    """
    return SystemLog.objects.filter(user=user).order_by('-created_at')[:limit]


def get_logs_by_type(action_type, limit=50):
    """
    Obtém logs por tipo de ação
    """
    return SystemLog.objects.filter(action_type=action_type).order_by('-created_at')[:limit]


def get_logs_by_level(level, limit=50):
    """
    Obtém logs por nível
    """
    return SystemLog.objects.filter(level=level).order_by('-created_at')[:limit]


def get_logs_by_object(action_object_type, action_object_id):
    """
    Obtém logs relacionados a um objeto específico
    """
    return SystemLog.objects.filter(
        action_object_type=action_object_type,
        action_object_id=action_object_id
    ).order_by('-created_at')

