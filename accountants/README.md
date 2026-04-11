# 👨‍💼 Módulo de Contadores - MEI Monitor

## 📋 Visão Geral

O módulo de contadores permite que profissionais de contabilidade gerenciem uma carteira de clientes MEI de forma centralizada, com controle total sobre notas fiscais, status de clientes e informações de faturamento.

---

## 🎯 Funcionalidades Principais

### 1. **Dashboard do Contador**
- Visão geral com métricas principais:
  - Total de clientes ativos
  - Total de notas emitidas
  - Notas em processamento
- Lista de clientes recentes
- Atalhos rápidos para ações principais

**URL:** `/accountants/`

### 2. **Gestão de Clientes**

#### 📌 Listar Clientes
- Visualização de toda a carteira de clientes
- Filtros por razão social, CNPJ e status
- Busca em tempo real
- Paginação com até 15 clientes por página

**URL:** `/accountants/clients/`

#### ➕ Adicionar Novo Cliente
- Vincular empresas já cadastradas no sistema
- Definir status (Ativo, Inativo, Suspenso)
- Configurar taxa mensal cobrada
- Adicionar observações sobre o cliente

**URL:** `/accountants/clients/add/`

#### ✏️ Editar Cliente
- Atualizar informações de status e taxa
- Modificar observações
- Gerenciar relacionamento com cliente

**URL:** `/accountants/clients/<id>/edit/`

#### 👁️ Detalhes do Cliente
- Visualização completa do cliente
- Lista de todas as notas fiscais
- Estatísticas de notas (total, emitidas, canceladas)
- Informações de filiação e taxa mensal
- Opção de criar novas notas
- Opção de cancelar notas existentes

**URL:** `/accountants/clients/<id>/`

### 3. **Gestão de Notas Fiscais**

#### 📄 Criar Nota para Cliente
- Interface simplificada para emissão
- Pré-seleção do cliente
- Redirecionamento para formulário completo

**URL:** `/accountants/clients/<id>/invoice/add/`

#### 🚫 Cancelar Nota
- **Importante:** Contadores podem CANCELAR notas mas NÃO PODEM EXCLUIR
- Confirmação antes de cancelar
- Histórico mantido no banco para auditoria
- Status muda para "CANCELLED"

**URL:** `/accountants/clients/<id>/invoice/<invoice_id>/cancel/`

### 4. **Perfil do Contador**

#### ⚙️ Editar Informações Profissionais
- Nome do studio/empresa de contabilidade
- CPF profissional
- Número de telefone
- Informações de plano (FREE, PREMIUM, ENTERPRISE)

**URL:** `/accountants/profile/`

---

## 🔐 Permissões e Segurança

### Controle de Acesso
- **Apenas contadores autenticados** podem acessar o módulo
- **Isolamento de dados:** Cada contador vê apenas seus próprios clientes
- **Validação de propriedade** em todas as operações (client_id, invoice_id)

### Restrições
- ❌ Contadores **NÃO PODEM** excluir notas (apenas cancelar)
- ❌ Contadores **NÃO PODEM** acessar dados de outros contadores
- ✅ Contadores **PODEM** visualizar todas as notas de seus clientes
- ✅ Contadores **PODEM** criar e cancelar notas

---

## 🗄️ Modelos de Dados

### `AccountantProfile`
```python
{
    user: OneToOneField(User),          # Usuário associado
    professional_name: str,              # Nome do studio/empresa
    cpf: str,                            # CPF único do contador
    phone: str,                          # Telefone de contato
    account_type: str,                   # FREE, PREMIUM, ENTERPRISE
    is_active: bool,                     # Status da conta
    created_at: datetime,                # Data de criação
    updated_at: datetime,                # Data de atualização
}
```

### `ClientAccount`
```python
{
    accountant: ForeignKey(AccountantProfile),  # Contador responsável
    empresa: ForeignKey(Empresa),               # Empresa MEI
    status: str,                                # ACTIVE, INACTIVE, SUSPENDED
    monthly_fee: Decimal,                       # Taxa mensal cobrada
    notes: str,                                 # Observações
    is_active: bool,                            # Ativado/Desativado
    created_at: datetime,                       # Data de vinculação
    updated_at: datetime,                       # Data de atualização
}
```

---

## 🔄 Fluxo de Trabalho

### 1️⃣ Onboarding do Contador
```
Contador se registra → Cria perfil profissional → Começa a adicionar clientes
```

### 2️⃣ Gerenciamento de Cliente
```
Adicionar Cliente → Emitir Notas → Visualizar Estatísticas → Cancelar (se necessário)
```

### 3️⃣ Emissão de Nota
```
Entra em Detalhes do Cliente → Clica "Nova Nota" → Redirecionado para criar nota
```

---

## 📊 Exemplos de Uso

### Criar um Contador
```python
from accounts.models import User
from accountants.models import AccountantProfile

user = User.objects.create_user(
    username='contador_silva',
    email='silva@contabil.com.br',
    password='senha_segura'
)

profile = AccountantProfile.objects.create(
    user=user,
    professional_name='Silva & Associados Contabilidade',
    cpf='123.456.789-00',
    phone='(11) 98765-4321',
    account_type='PREMIUM'
)
```

### Adicionar Cliente ao Contador
```python
from accountants.models import ClientAccount
from monitor.models import Empresa

empresa = Empresa.objects.get(id=1)
client = ClientAccount.objects.create(
    accountant=profile,
    empresa=empresa,
    status='ACTIVE',
    monthly_fee=150.00,
    notes='Cliente em crescimento, vigilância mensal necessária'
)
```

### Obter Estatísticas
```python
print(f"Clientes ativos: {profile.total_clients}")
print(f"Notas emitidas: {profile.total_invoices}")
print(f"Notas do cliente: {client.total_invoices}")
print(f"Notas emitidas: {client.issued_invoices}")
```

---

## 🛠️ Configurações (settings.py)

A app `accountants` já está configurada em `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...
    'accountants',
]
```

---

## 📱 URLs Disponíveis

| Rota | View | Método | Descrição |
|------|------|--------|-----------|
| `/accountants/` | `accountant_dashboard` | GET | Dashboard principal |
| `/accountants/profile/` | `accountant_profile_view` | GET, POST | Editar perfil |
| `/accountants/clients/` | `clients_list` | GET | Listar clientes |
| `/accountants/clients/add/` | `client_create` | GET, POST | Adicionar cliente |
| `/accountants/clients/<id>/` | `client_detail` | GET | Detalhes do cliente |
| `/accountants/clients/<id>/edit/` | `client_edit` | GET, POST | Editar cliente |
| `/accountants/clients/<id>/toggle/` | `client_toggle_status` | POST | Ativar/Desativar (AJAX) |
| `/accountants/clients/<id>/invoice/add/` | `invoice_create_for_client` | GET | Criar nota |
| `/accountants/clients/<id>/invoice/<inv_id>/cancel/` | `invoice_cancel_for_client` | GET, POST | Cancelar nota |

---

## 🎨 Templates

Todos os templates seguem o design system **ContraFlow Light**:
- `/templates/accountants/dashboard.html` - Dashboard
- `/templates/accountants/profile.html` - Perfil do contador
- `/templates/accountants/clients_list.html` - Lista de clientes
- `/templates/accountants/client_create.html` - Criar cliente
- `/templates/accountants/client_detail.html` - Detalhes do cliente
- `/templates/accountants/client_edit.html` - Editar cliente
- `/templates/accountants/invoice_cancel_confirm.html` - Confirmação de cancelamento

---

## 🔮 Próximas Melhorias

- [ ] Relatório de faturamento por cliente
- [ ] Exportar dados em CSV/PDF
- [ ] Integração com alertas de vencimento
- [ ] Agendamento de e-mails automáticos
- [ ] Dashboard analítico com gráficos
- [ ] API para integração com sistemas externos
- [ ] Suporte a múltiplas moedas
- [ ] Histórico de alterações com timestamps

---

## 💡 Dicas Importantes

1. **Isolamento de Dados:** O sistema valida automaticamente se o cliente pertence ao contador autenticado
2. **Cancelamento, não Exclusão:** Notas canceladas ficam no banco para auditoria
3. **Taxes e Fees:** Cada cliente pode ter uma taxa mensal diferente
4. **Status:** Use os diferentes status para gerenciar relacionamentos com clientes
5. **Observações:** O campo `notes` é ideal para guardar informações importantes

---

## 📞 Suporte

Para dúvidas ou sugestões, consulte a documentação do Django ou abra uma issue no repositório.

**Desenvolvido com ❤️ por MEI Monitor**

