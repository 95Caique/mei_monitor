# ⚡ QUICK START - Módulo de Contadores

## 🚀 Começar Agora

### 1. Criar Contador de Teste
```bash
python manage.py create_test_accountant contador_silva --password senha123
```

### 2. Acessar
```
http://localhost:8000/accountants/
```

### 3. Login
```
Usuário: contador_silva
Senha: senha123
```

---

## 📱 URLs Principais

| Página | URL | O que faz |
|--------|-----|----------|
| 🏠 Dashboard | `/accountants/` | Métricas e clientes recentes |
| 👥 Clientes | `/accountants/clients/` | Lista com filtros e busca |
| ➕ Novo | `/accountants/clients/add/` | Adicionar cliente |
| 📋 Detalhes | `/accountants/clients/1/` | Ver cliente e suas notas |
| ✏️ Editar | `/accountants/clients/1/edit/` | Editar cliente |
| ⚙️ Perfil | `/accountants/profile/` | Editar dados do contador |

---

## ✨ Funcionalidades

### ✅ Pode Fazer
- 👥 Adicionar clientes MEI
- 📄 Ver todas as notas dos clientes
- 🚫 Cancelar notas (sem deletar)
- 💰 Definir taxa mensal por cliente
- 📝 Adicionar observações

### ❌ NÃO Pode Fazer
- 🗑️ Deletar notas (apenas cancelar)
- 👁️ Ver clientes de outro contador
- 🔧 Acessar admin

---

## 🗄️ Banco de Dados

### Tabelas Criadas
- `accountants_accountantprofile` - Dados do contador
- `accountants_clientaccount` - Clientes do contador

### Relacionamentos
```
User (1) ──── (1) AccountantProfile
                      │
                      ├─► (N) ClientAccount
                                │
                                └─► (1) Empresa
```

---

## 🔒 Segurança

✅ Cada contador vê apenas seus clientes
✅ Notas canceladas não são deletadas
✅ Histórico completo para auditoria
✅ Validação em todas as operações

---

## 🎨 Design

Todos os templates seguem o design **ContraFlow Light**:
- Cores padronizadas
- Layout responsivo
- Componentes reutilizáveis
- Funciona em mobile/tablet/desktop

---

## 📊 Dashboard Mostra

```
┌─────────────┬─────────────┬─────────────┐
│   👥 25     │   📄 542    │   ⏳ 89     │
│  Clientes   │   Notas     │   Em Proc.  │
│  Ativos     │  Emitidas   │   Notas     │
└─────────────┴─────────────┴─────────────┘

         Clientes Recentes
    ┌────────────────────┐
    │ Empresa A (CNPJ)   │
    │ Status: Ativo      │
    │ Taxa: R$ 150,00    │
    └────────────────────┘
```

---

## 💬 Exemplo de Fluxo

```
1. Contador acessa http://localhost:8000/accountants/
   ↓
2. Clica em "Novo Cliente"
   ↓
3. Digita CNPJ: "11111111000191"
   ↓
4. Sistema encontra empresa cadastrada
   ↓
5. Define status: "Ativo"
   ↓
6. Define taxa mensal: R$ 150,00
   ↓
7. Salva e é redirecionado
   ↓
8. Vê todas as notas do cliente
   ↓
9. Pode cancelar notas (sem deletar)
```

---

## 🆘 Troubleshooting

### Não vejo o link "Meus Clientes"
→ Você precisa ter um `AccountantProfile` criado

### Erro ao adicionar cliente
→ Verifique se o CNPJ da empresa está correto

### Não posso cancelar nota
→ Apenas notas com status ISSUED podem ser canceladas

### Erro ao migrar
→ Execute: `python manage.py migrate accountants`

---

## 📚 Documentação Completa

Para mais detalhes, consulte:
- `accountants/README.md` - Documentação técnica
- `ACCOUNTANTS_SUMMARY.md` - Resumo de funcionalidades
- `COMMIT_INSTRUCTIONS.md` - Instruções para commit

---

## 🎯 Próximos Passos

1. ✅ Criar contador de teste
2. ✅ Adicionar seus clientes
3. ✅ Criar notas para os clientes
4. ✅ Testar cancelamento de notas
5. ✅ Editar informações do cliente
6. ✅ Visualizar estatísticas

---

**Pronto? Comece agora:**
```bash
python manage.py create_test_accountant seu_nome --password sua_senha
```

Acesse: http://localhost:8000/accountants/

