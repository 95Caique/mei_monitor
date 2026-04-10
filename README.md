# 📊 MEI Monitor

Um sistema web robusto e intuitivo para monitoramento de limite MEI, gerenciamento de notas fiscais e alertas automáticos. Desenvolvido com Django para microempresários controlarem seu faturamento anual de forma eficiente.

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Django](https://img.shields.io/badge/Django-6.0+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Ativo-brightgreen)

---

## 🎯 Sobre o Projeto

O **MEI Monitor** é uma plataforma web criada para ajudar Microempresários Individuais (MEI) a:

- 📈 **Monitorar limite MEI**: Acompanhar em tempo real quanto já foi faturado do limite anual de R$ 81.000
- 📋 **Gerenciar notas fiscais**: Criar, editar, cancelar e visualizar todas as suas notas emitidas
- 🚨 **Receber alertas**: Ser notificado quando está próximo do limite MEI
- 📊 **Visualizar relatórios**: Análise detalhada do faturamento com gráficos
- 🔐 **Auditoria completa**: Registro de todas as ações para compliance

---

## ✨ Principais Funcionalidades

### 1. **Dashboard Inteligente**
- Visualização rápida do limite MEI com indicador visual
- Cards com estatísticas de notas (emitidas, canceladas, total)
- Últimas notas fiscais emitidas
- Alertas recentes em tempo real
- Informações da empresa

### 2. **Gerenciamento de Notas Fiscais**
- ✅ Criar notas fiscais com dados detalhados
- ✏️ Editar notas existentes
- ❌ Cancelar notas (não remove limite)
- 🗑️ Excluir notas permanentemente
- 📄 Visualizar histórico completo

### 3. **Sistema de Alertas**
- 🟢 Info: Informações gerais
- 🟡 Warning: Próximo do limite
- 🔴 Critical: Ultrapassou o limite
- Notificações via Telegram (integração)
- Histórico de alertas com datas

### 4. **Relatórios e Análises**
- 📈 Gráficos de faturamento (últimos 30 dias, anual)
- 📉 Faturamento por mês (últimos 12 meses)
- 🥧 Distribuição de notas por status
- 📊 Resumo anual com estatísticas
- 📥 Exportação de relatórios

### 5. **Sistema Robusto de Logs**
- 📋 Registro de todas as ações importantes
- 🔍 Filtros avançados (usuário, nível, tipo, data)
- 🔐 Logs imutáveis (não podem ser deletados)
- 👤 Rastreamento de IP e User Agent
- 📊 Auditorias completas com valores antigos/novos

### 6. **Responsividade**
- 📱 Interface totalmente responsiva para mobile
- 💻 Desktop otimizado
- 🎨 Design moderno e intuitivo
- ⚡ Performance rápida

---

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 6.0 (Python 3.12)
- **Database**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Components**: Bootstrap, FontAwesome Icons
- **Gráficos**: Chart.js
- **Notificações**: Telegram Bot API
- **Admin**: Django Admin customizado

---

## 📋 Pré-requisitos

- Python 3.12+
- pip (gerenciador de pacotes Python)
- Git
- SQLite (já incluído no Python)

---

## 🚀 Como Executar

### 1. **Clone o repositório**

```bash
git clone https://github.com/seu-usuario/mei_monitor.git
cd mei_monitor
```

### 2. **Crie um ambiente virtual**

```bash
python -m venv venv
```

### 3. **Ative o ambiente virtual**

**No Linux/Mac:**
```bash
source venv/bin/activate
```

**No Windows:**
```bash
venv\Scripts\activate
```

### 4. **Instale as dependências**

```bash
pip install -r requirements.txt
```

### 5. **Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### 6. **Execute as migrations**

```bash
python manage.py migrate
```

### 7. **Crie um superusuário (admin)**

```bash
python manage.py createsuperuser
```

Siga as instruções para criar seu usuário admin.

### 8. **Colete os arquivos estáticos**

```bash
python manage.py collectstatic --noinput
```

### 9. **Inicie o servidor**

```bash
python manage.py runserver
```

O servidor iniciará em `http://localhost:8000`

---

## 📱 Acessando o Sistema

### Interface Principal
- **URL**: `http://localhost:8000/`
- **Login**: Use as credenciais de superusuário criadas

### Admin Panel
- **URL**: `http://localhost:8000/admin/`
- **Acesso**: Superusuário
- **Funcionalidades**: 
  - Gerenciar empresas
  - Visualizar logs do sistema
  - Gerenciar usuários
  - Configurar alertas

### URLs Principais

| URL | Descrição |
|-----|-----------|
| `/` | Dashboard principal |
| `/invoices/` | Gerenciar notas fiscais |
| `/reports/` | Relatórios e análises |
| `/admin/` | Painel administrativo |
| `/admin/logs/systemlog/` | Visualizar logs do sistema |

---

## 📚 Estrutura do Projeto

```
mei_monitor/
├── accounts/              # App de autenticação e usuários
├── dashboard/             # App principal do dashboard
├── monitor/               # App de monitoramento de limite MEI
├── telegram_bot/          # Integração com Telegram
├── logs/                  # Sistema de logs e auditoria
├── adminpanel/            # Painel administrativo customizado
├── config/                # Configurações do Django
├── static/                # Arquivos estáticos (CSS, JS, imagens)
├── templates/             # Templates HTML
├── manage.py              # Script de gerenciamento Django
├── requirements.txt       # Dependências do projeto
└── README.md              # Este arquivo
```

---

## 🎮 Usando o Sistema

### 1. **Primeira Execução**

Ao fazer login pela primeira vez, você será solicitado a registrar sua empresa:
- CNPJ (apenas números)
- Razão Social
- Cidade e Estado
- Tipo (MEI ou ME)

### 2. **Adicionar Notas Fiscais**

1. Acesse "Gerenciar Notas Fiscais"
2. Clique em "+ Nova Nota"
3. Preencha os dados:
   - Número/ID da nota
   - Valor total
   - Status (Emitida/Rascunho)
4. Clique em "Emitir Nota Fiscal"

### 3. **Monitorar Limite MEI**

No dashboard, veja em tempo real:
- Percentual do limite utilizado
- Valor já faturado
- Limite MEI (R$ 81.000)
- Alertas se próximo do limite

### 4. **Consultar Relatórios**

Acesse "Relatórios" para:
- Gráficos de faturamento
- Estatísticas mensais/anuais
- Distribuição de notas
- Exportar dados

### 5. **Visualizar Logs**

No admin, acesse "Logs do Sistema" para:
- Ver todas as ações realizadas
- Filtrar por usuário, tipo, data
- Verificar alterações de valores
- Rastrear quem fez o quê e quando

---

## 🔧 Comandos Úteis Django

### Visualizar logs via terminal

```bash
python manage.py show_logs                    # Últimos 50 logs
python manage.py show_logs --user=seu_usuario # Filtrar por usuário
python manage.py show_logs --level=ERROR      # Apenas erros
python manage.py show_logs --hours=48         # Últimas 48 horas
```

### Criar fixtures (dados de exemplo)

```bash
python manage.py dumpdata > backup.json      # Exportar dados
python manage.py loaddata backup.json        # Importar dados
```

### Gerenciar banco de dados

```bash
python manage.py makemigrations              # Criar migrations
python manage.py migrate                     # Aplicar migrations
python manage.py dbshell                     # Acessar console BD
```

---

## 🔐 Segurança

- ✅ Autenticação com Django
- ✅ CSRF Protection
- ✅ SQL Injection Prevention
- ✅ XSS Protection
- ✅ Logs imutáveis para auditoria
- ✅ Senha criptografada
- ✅ Rastreamento de IP
- ✅ Permissões por usuário

---

## 📱 Responsividade

O sistema é totalmente responsivo:
- **Desktop**: Layout em 2 colunas, cards grandes
- **Tablet**: Layout adaptado
- **Mobile**: Layout em 1 coluna, elementos compactos

Testado em:
- ✅ Chrome (Desktop e Mobile)
- ✅ Firefox
- ✅ Safari
- ✅ Edge

---

## 🐛 Troubleshooting

### Erro de módulo não encontrado
```bash
pip install -r requirements.txt
```

### Erro de migrations
```bash
python manage.py migrate --run-syncdb
```

### Erro de permissão (Linux/Mac)
```bash
chmod +x manage.py
```

### Banco de dados corrompido
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## 🚀 Deploy em Produção

### Preparação

1. **Mude DEBUG para False** em `.env`
2. **Configure ALLOWED_HOSTS** com seu domínio
3. **Use um banco de dados robusto** (PostgreSQL recomendado)
4. **Configure variáveis de ambiente** seguras
5. **Use um servidor WSGI** (Gunicorn, uWSGI)
6. **Configure um reverse proxy** (Nginx, Apache)

### Exemplo com Gunicorn

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

---

## 📞 Suporte

- 📧 Email: contato@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/seu-usuario/mei_monitor/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/seu-usuario/mei_monitor/discussions)

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🤝 Contribuições

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📝 Changelog

### v1.0.0 - Lançamento Inicial
- ✅ Dashboard com limite MEI
- ✅ Gerenciamento de notas fiscais
- ✅ Sistema de alertas
- ✅ Relatórios com gráficos
- ✅ Sistema de logs e auditoria
- ✅ Interface responsiva
- ✅ Admin customizado

---

## 👨‍💻 Autor

**Caique**
- GitHub: [@seu-github](https://github.com/seu-usuario)
- Email: seu-email@example.com

---

## 🙏 Agradecimentos

- Django Team
- Python Community
- Chart.js
- FontAwesome Icons

---

## ⭐ Se você gostou do projeto, deixe uma estrela!

<div align="center">

Made with ❤️ by Caique

[⬆ Voltar ao Topo](#-mei-monitor)

</div>
