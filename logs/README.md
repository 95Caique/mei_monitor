# Sistema de Logs - MEI Monitor

## Visão Geral

O sistema de logs foi criado para registrar todas as ações importantes do sistema de forma robusta e auditável. Todos os logs são armazenados no banco de dados e podem ser visualizados no admin do Django.

## Estrutura

### Modelo: SystemLog

O modelo `SystemLog` armazena informações detalhadas sobre cada ação:

- **user**: Usuário que realizou a ação
- **level**: Nível do log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **action_type**: Tipo de ação (CREATE, UPDATE, DELETE, CANCEL, LOGIN, etc)
- **title**: Título descritivo da ação
- **description**: Descrição detalhada do que aconteceu
- **module**: Módulo/app que gerou a ação
- **action_object_id**: ID do objeto afetado
- **action_object_type**: Tipo do objeto (Invoice, Empresa, etc)
- **ip_address**: IP do cliente
- **user_agent**: User Agent do navegador
- **old_values**: Valores antigos (JSON) - para auditorias
- **new_values**: Novos valores (JSON) - para auditorias
- **created_at**: Data/hora do registro

## Como Usar

### 1. Logging Simples

```python
from logs.services import log_action

# Log simples
log_action(
    request=request,
    user=request.user,
    level='INFO',
    action_type='CREATE',
    title='Nota fiscal criada',
    description='Nota fiscal #001 foi criada com valor R$ 500,00',
    module='invoice'
)
```

### 2. Logging de Ações em Notas Fiscais

```python
from logs.services import log_invoice_action

# Logging automático com informações da nota
log_invoice_action(
    request=request,
    user=request.user,
    invoice=invoice_obj,
    action_type='CANCEL',  # CREATE, UPDATE, DELETE, CANCEL
    old_values={'status': 'ISSUED'},
    new_values={'status': 'CANCELLED'}
)
```

### 3. Logging de Erros

```python
from logs.services import log_error

try:
    # código que pode gerar erro
    pass
except Exception as e:
    log_error(
        request=request,
        user=request.user,
        title='Erro ao processar nota',
        description='Falha no processamento',
        module='invoice',
        exception=e
    )
```

### 4. Logging de Autenticação

```python
from logs.services import log_authentication

# Login
log_authentication(
    request=request,
    user=user,
    action='LOGIN'
)

# Logout
log_authentication(
    request=request,
    user=user,
    action='LOGOUT'
)
```

## Consultando Logs

### Via Admin

1. Acesse `http://localhost:8000/admin/logs/systemlog/`
2. Veja todos os logs registrados
3. Use os filtros para buscar por:
   - Nível (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - Tipo de ação (CREATE, UPDATE, DELETE, etc)
   - Módulo
   - Data
4. Use a busca para encontrar por título, descrição, usuário ou IP

### Via Django ORM

```python
from logs.models import SystemLog
from logs.services import get_logs_for_user, get_logs_by_type

# Todos os logs de um usuário
logs = get_logs_for_user(user, limit=50)

# Logs de um tipo específico
logs = get_logs_by_type('CANCEL', limit=50)

# Logs de um nível específico
from logs.services import get_logs_by_level
logs = get_logs_by_level('ERROR', limit=50)

# Logs de um objeto específico
from logs.services import get_logs_by_object
logs = get_logs_by_object('Invoice', invoice_id=123)
```

## Níveis de Log

- **DEBUG**: Informações de debug (verboso)
- **INFO**: Informações gerais (padrão)
- **WARNING**: Avisos importantes
- **ERROR**: Erros do sistema
- **CRITICAL**: Erros críticos

## Tipos de Ação

- **CREATE**: Criação de um novo objeto
- **UPDATE**: Atualização de um objeto existente
- **DELETE**: Exclusão de um objeto
- **CANCEL**: Cancelamento de um objeto
- **LOGIN**: Login de usuário
- **LOGOUT**: Logout de usuário
- **ERROR**: Erro do sistema
- **ALERT**: Alerta gerado
- **EXPORT**: Exportação de dados
- **IMPORT**: Importação de dados
- **OTHER**: Outras ações

## Boas Práticas

1. **Sempre registre ações importantes**: CREATE, UPDATE, DELETE, CANCEL
2. **Use níveis apropriados**: Não use ERROR para avisos normais
3. **Inclua contexto**: Adicione descrições detalhadas
4. **Rastreie mudanças**: Use old_values/new_values para auditorias
5. **Registre erros**: Sempre registre exceções com log_error()

## Exemplo Completo

```python
from logs.services import log_invoice_action
from logs.models import SystemLog

# Ao criar uma nota
invoice = Invoice.objects.create(
    empresa=empresa,
    invoice_id='001',
    total=1000.00,
    status='ISSUED'
)

log_invoice_action(
    request=request,
    user=request.user,
    invoice=invoice,
    action_type='CREATE'
)

# Ao atualizar uma nota
old_total = invoice.total
invoice.total = 1500.00
invoice.save()

log_invoice_action(
    request=request,
    user=request.user,
    invoice=invoice,
    action_type='UPDATE',
    old_values={'total': str(old_total)},
    new_values={'total': str(invoice.total)}
)

# Ao cancelar uma nota
old_status = invoice.status
invoice.status = 'CANCELLED'
invoice.save()

log_invoice_action(
    request=request,
    user=request.user,
    invoice=invoice,
    action_type='CANCEL',
    old_values={'status': old_status},
    new_values={'status': invoice.status}
)
```

## Segurança e Retenção

- Logs **não podem ser deletados** (proteção de auditoria)
- Logs **não podem ser editados** (imutabilidade)
- Todos os logs incluem IP do cliente
- Todos os logs rastreiam o usuário responsável
- Use índices de banco de dados para queries rápidas

## Performance

O modelo SystemLog possui índices otimizados para:
- Busca por usuário
- Busca por data
- Busca por tipo de ação
- Busca por nível
- Busca por módulo

Estes índices garantem performance mesmo com milhões de logs.

