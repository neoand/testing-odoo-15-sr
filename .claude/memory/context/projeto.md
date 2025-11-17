# 📋 Contexto do Projeto - Detalhado

## História do Projeto

**Início:** Ambiente de testing para Odoo 15
**Objetivo:** Implementar e testar customizações para RealCred
**Status:** Em desenvolvimento ativo

## Módulos Instalados

### Core Odoo
- base
- web
- mail
- crm
- sale
- contacts

### Customizados
- **chatroom_sms_advanced** (v2.0)
  - Local: `./chatroom_sms_advanced/`
  - Backup: `./chatroom_sms_advanced_OLD_BACKUP/`
  - Função: Contact center SMS integrado ao CRM
  - API: Kolmeya

### Em Desenvolvimento
- temp_modules/ (módulos experimentais)

## Estrutura do Banco de Dados

**Tabelas Críticas:**
- `crm_lead` - Oportunidades
- `crm_stage` - Stages do CRM
- `res_partner` - Contatos/Empresas
- `res_users` - Usuários
- `res_groups` - Grupos de acesso
- `ir_model_access` - Permissões de modelo
- `ir_rule` - Record rules
- `chatroom_*` - Tabelas do SMS

## Perfis de Usuário

### Administrador
- Acesso total
- Configurações
- Desenvolvimento

### Gestor CRM
- Gerencia equipe
- Vê todas oportunidades da equipe
- Relatórios avançados

### Vendedor
- Próprias oportunidades
- Contatos próprios
- Acesso limitado

### Usuário Interno
- Visualização básica
- Sem edição
- Apenas leitura

## Integrações Ativas

### Kolmeya API
- **Endpoint:** (verificar em configs)
- **Autenticação:** API Key
- **Timeout:** 30s
- **Retry:** 3 tentativas
- **Rate limit:** (verificar)

### Email
- SMTP configurado
- Bounce handling
- Tracking

## Ambientes

### Testing (atual)
- Database: (nome a verificar)
- URL: (verificar)
- Usuário admin: (verificar)

### Produção
- (se houver, documentar)

## Dependências Externas

### Python Packages
- odoo==15.0
- psycopg2
- requests (para Kolmeya API)
- (verificar requirements.txt)

### Sistema
- PostgreSQL ≥12
- Python 3.8+
- Node.js (para assets)

## Backups

**Localização:** (documentar)
**Frequência:** (documentar)
**Última execução:** (atualizar)

## Logs

**Odoo:** `/var/log/odoo/odoo-server.log`
**PostgreSQL:** (localização)
**Nginx/Apache:** (se aplicável)

---

**Última atualização:** 2025-11-17
