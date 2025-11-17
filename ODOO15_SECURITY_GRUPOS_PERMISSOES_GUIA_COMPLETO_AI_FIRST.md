# ODOO 15 - GUIA COMPLETO DE SEGURANÇA, GRUPOS E PERMISSÕES (AI-FIRST)

**Versão:** 3.0
**Data:** 17/11/2025 (Atualizado com contexto servidor e correção admin)
**Propósito:** Documentação completa e profissional para configuração de permissões no Odoo 15
**Formato:** AI-First (otimizado para LLMs e assistentes de IA)
**Última Atualização:** Incident Admin Locked 16/11/2025 + Contexto Servidor Completo

---

## 🚨 AVISOS CRÍTICOS - LEIA PRIMEIRO

### ⚠️ INCIDENT 1: Internal User Removido (17/11/2025)
Foi descoberto um bug crítico na gestão de grupos implied que removeu incorretamente o grupo "Internal User" de 33 usuários, causando falha completa de permissões em TODOS os módulos.

**LIÇÃO CRÍTICA:** Implied groups são verificados em **RUNTIME**, **NÃO criam registros físicos** em `res_groups_users_rel`. O grupo Internal User (ID: 1) **DEVE estar fisicamente atribuído** aos usuários.

Ver seção [5.6 ATENÇÃO: Comportamento REAL de Implied Groups](#5-6-real-implied) para detalhes completos.

### ⚠️ INCIDENT 2: Admin User Locked (16/11/2025)
Admin (uid=2) ficou completamente travado devido à falta de grupos críticos essenciais.

**DESCOBERTA CRÍTICA:** Admin (uid=2) NÃO é superuser - é um usuário NORMAL que precisa de grupos explícitos. Por padrão, deve ter "all application security groups".

**GRUPOS ESSENCIAIS DO ADMIN:**
- Internal User (ID: 1) - BASE CRÍTICO
- Access Rights (ID: 2) - ADMIN ESSENCIAL
- Settings (ID: 3) - ADMIN ESSENCIAL
- Todos os grupos Administrator de cada módulo instalado

Ver seção [0.4 Admin vs Superuser](#0-4-admin-superuser) para detalhes completos.

---

## ÍNDICE

**0. [CONTEXTO DO SERVIDOR E ACESSO (LLM CONTEXT)](#0-contexto-servidor) 🆕**
   - [0.1 Informações do Servidor](#0-1-servidor-info)
   - [0.2 Como Acessar (SSH, PostgreSQL)](#0-2-acesso-servidor)
   - [0.3 Estrutura de Arquivos](#0-3-estrutura-arquivos)
   - **[0.4 Admin vs Superuser - DIFERENÇA CRÍTICA](#0-4-admin-superuser) 🚨 NOVO**
   - [0.5 Referências Oficiais Consultadas](#0-5-referencias)

1. [Fundamentos de Segurança no Odoo 15](#1-fundamentos)
2. [Access Rights (ir.model.access)](#2-access-rights)
3. [Record Rules (ir.rule)](#3-record-rules)
4. [Groups (res.groups)](#4-groups)
5. [Hierarquia e Implied Groups](#5-hierarquia)
   - **[5.6 ATENÇÃO: Comportamento REAL de Implied Groups](#5-6-real-implied) 🚨 CRÍTICO**
6. [Field-Level Security](#6-field-security)
7. [Best Practices](#7-best-practices)
   - **[7.9 GRUPOS PROTEGIDOS - NUNCA REMOVER](#7-9-protected-groups) 🚨**
   - **[7.10 Script de Validação Diária](#7-10-validation-script) 🚨**
8. [Troubleshooting](#8-troubleshooting)
   - **[8.7 Incident Report: Internal User Removido](#8-7-incident-internal-user) 🚨**
   - **[8.8 Incident Report: Admin User Locked](#8-8-incident-admin-locked) 🚨 NOVO**
9. [SQL Queries de Referência](#9-sql-reference)
10. [Casos de Uso Comuns](#10-casos-uso)
11. **[Lessons Learned - Incidents 2025](#11-lessons-learned) 🚨**

---

## 0. CONTEXTO DO SERVIDOR E ACESSO (LLM CONTEXT) {#0-contexto-servidor}

> **PROPÓSITO DESTA SEÇÃO:** Fornecer contexto completo para LLMs/Assistentes de IA sobre como acessar e navegar no servidor Odoo, possibilitando diagnóstico e correção de problemas de permissões sem necessidade de contexto externo.

---

### 0.1 Informações do Servidor {#0-1-servidor-info}

#### Servidor Principal

| Propriedade | Valor |
|-------------|-------|
| **Nome** | odoo-rc |
| **IP Externo** | 35.199.79.229 |
| **IP Interno** | 10.128.0.2 |
| **Domínio** | odoo.semprereal.com |
| **Provedor** | Google Cloud Platform (GCP) |
| **SO** | Ubuntu Linux |
| **Odoo Version** | 15.0 Community |
| **Python** | 3.8.10 |

#### Banco de Dados

| Propriedade | Valor |
|-------------|-------|
| **SGBD** | PostgreSQL 12 |
| **Database** | realcred |
| **Host** | localhost (no servidor) |
| **Porta** | 5432 |
| **Usuário PostgreSQL** | postgres |
| **Usuário Odoo** | odoo15 |
| **Senha Odoo** | T5ZJpyeBDTyh |

#### Configuração Odoo

| Propriedade | Valor |
|-------------|-------|
| **Config File** | `/etc/odoo-server.conf` |
| **Admin Password** | HI5Rdi5UikL9jjLy |
| **HTTP Port** | 8069 (internal) |
| **Longpolling Port** | 8072 |
| **Workers** | 9 |
| **Log File** | `/var/log/odoo/odoo-server.log` |
| **Service Name** | odoo-server.service |
| **Data Dir** | `/odoo/filestore` |

---

### 0.2 Como Acessar (SSH, PostgreSQL) {#0-2-acesso-servidor}

#### Acesso SSH ao Servidor

**Método 1: SSH direto (se configurado alias)**
```bash
ssh odoo-rc
```

**Método 2: SSH com IP**
```bash
ssh usuario@35.199.79.229
# OU
ssh usuario@10.128.0.2  # (se na mesma VPC GCP)
```

**Método 3: Via Google Cloud Console**
```bash
gcloud compute ssh odoo-rc --zone=<sua-zona>
```

#### Acesso ao PostgreSQL

**Opção 1: Do servidor (local)**
```bash
# SSH primeiro
ssh odoo-rc

# Conectar como usuário postgres
sudo -u postgres psql realcred

# OU conectar como usuário odoo15
psql postgresql://odoo15:T5ZJpyeBDTyh@localhost:5432/realcred
```

**Opção 2: Do Mac local (se há túnel/acesso direto)**
```bash
# Criar túnel SSH
ssh -L 5433:localhost:5432 odoo-rc

# Em outro terminal
psql postgresql://odoo15:T5ZJpyeBDTyh@localhost:5433/realcred
```

**Opção 3: Conexão direta interna (do Mac se configurado)**
```bash
psql postgresql://odoo15:T5ZJpyeBDTyh@10.128.0.2:5432/realcred
```

#### Comandos Essenciais do Servidor

**Gerenciar Odoo:**
```bash
# Status
sudo systemctl status odoo-server

# Restart
sudo systemctl restart odoo-server

# Stop
sudo systemctl stop odoo-server

# Start
sudo systemctl start odoo-server

# Logs em tempo real
sudo tail -f /var/log/odoo/odoo-server.log

# Logs com filtro
sudo tail -100 /var/log/odoo/odoo-server.log | grep -i "error\|warning"
```

**Backup do Banco:**
```bash
# Backup compactado
sudo -u postgres pg_dump realcred -F c -f /tmp/backup_$(date +%Y%m%d_%H%M%S).dump

# Backup SQL
sudo -u postgres pg_dump realcred > /tmp/backup_$(date +%Y%m%d_%H%M%S).sql

# Verificar tamanho
ls -lh /tmp/backup*.dump
```

**Restaurar Backup:**
```bash
# Parar Odoo primeiro
sudo systemctl stop odoo-server

# Restaurar (formato custom)
sudo -u postgres pg_restore -d realcred --clean /tmp/backup.dump

# Restaurar (formato SQL)
sudo -u postgres psql realcred < /tmp/backup.sql

# Reiniciar Odoo
sudo systemctl start odoo-server
```

**Upload/Download de Arquivos:**
```bash
# Upload do Mac para servidor
scp arquivo.sql odoo-rc:/tmp/

# Download do servidor para Mac
scp odoo-rc:/tmp/arquivo.sql ~/Downloads/

# Upload de diretório
scp -r diretorio/ odoo-rc:/tmp/
```

---

### 0.3 Estrutura de Arquivos {#0-3-estrutura-arquivos}

#### Diretórios Principais

```
/odoo/
├── odoo-server/              # Código fonte Odoo 15
│   ├── addons/               # Módulos padrão (433 módulos)
│   ├── odoo/                 # Core do Odoo
│   └── odoo-bin              # Executável principal
│
├── custom/                   # Módulos customizados
│   ├── addons_custom/        # Módulos da empresa
│   │   ├── realcred_permissions/  # Módulo de permissões
│   │   ├── contact_center_sms/    # SMS Center
│   │   └── ...
│   ├── helpdesk/
│   ├── l10n_br_base/        # Localização Brasil
│   ├── social/
│   ├── addons-whatsapp-connector/
│   ├── om_account_accountant/
│   └── hr_attendance_pro/
│
└── filestore/               # Arquivos do Odoo
    ├── addons/
    ├── filestore/           # Anexos, imagens, PDFs
    └── sessions/            # Sessões (5.7 GB!)

/etc/
└── odoo-server.conf         # Configuração principal

/var/log/odoo/
└── odoo-server.log          # Logs do sistema
```

#### Arquivos de Configuração Importantes

**`/etc/odoo-server.conf`**
```ini
[options]
admin_passwd = HI5Rdi5UikL9jjLy
http_port = 8069
logfile = /var/log/odoo/odoo-server.log
addons_path = /odoo/odoo-server/addons,/odoo/custom/addons_custom,/odoo/custom/helpdesk,/odoo/custom/l10n_br_base,/odoo/custom/social,/odoo/custom/addons-whatsapp-connector,/odoo/custom/om_account_accountant,/odoo/custom/hr_attendance_pro
dbfilter = realcred
workers = 9
limit_memory_hard = 6442450944
limit_memory_soft = 8589934592
```

#### Módulos Customizados - Permissões

**Módulo Principal:** `/odoo/custom/addons_custom/realcred_permissions/`

```
realcred_permissions/
├── __manifest__.py
├── security/
│   ├── ir.model.access.csv      # Access rights
│   └── security.xml             # Grupos e record rules
├── data/
│   └── grupos_padrao.xml
└── models/
    └── ...
```

**Arquivo CSV de Access Rights:**
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_res_partner_internal_user_crud,res.partner.internal.user.crud,base.model_res_partner,base.group_user,1,1,1,1
access_crm_lead_operacional,crm.lead.operacional,crm.model_crm_lead,realcred_permissions.group_operacional,1,1,1,1
```

---

### 0.4 Admin vs Superuser - DIFERENÇA CRÍTICA {#0-4-admin-superuser}

> **ATENÇÃO:** Esta é uma descoberta CRÍTICA do incident de 16/11/2025. Muitos desenvolvedores confundem admin com superuser.

#### Conceitos Fundamentais

**SUPERUSER (OdooBot - UID=1)**

```python
┌─────────────────────────────────────────────────┐
│ SUPERUSER (OdooBot)                             │
├─────────────────────────────────────────────────┤
│ User ID: 1                                      │
│ Login: OdooBot / __system__                     │
│ Tipo: Conta sistema do Odoo                    │
│                                                 │
│ CARACTERÍSTICAS:                                │
│ ✅ BYPASSA todas as regras de segurança        │
│ ✅ Não está sujeito a Access Rights            │
│ ✅ Não está sujeito a Record Rules             │
│ ✅ Pode acessar qualquer modelo/registro       │
│ ✅ Usado internamente pelo Odoo                │
│ ✅ Ativado via Developer Mode → "Become Superuser" │
│                                                 │
│ GRUPOS NECESSÁRIOS:                             │
│ ❌ NENHUM - Não precisa de grupos!             │
│                                                 │
│ QUANDO É USADO:                                 │
│ - Instalação de módulos                        │
│ - Migrações de dados                           │
│ - Operações internas do sistema                │
│ - Debugging (modo desenvolvedor)               │
└─────────────────────────────────────────────────┘
```

**ADMIN USER (admin - UID=2)**

```python
┌─────────────────────────────────────────────────┐
│ ADMIN USER (administrator)                      │
├─────────────────────────────────────────────────┤
│ User ID: 2 (normalmente)                        │
│ Login: admin                                    │
│ Tipo: Usuário NORMAL com privilégios           │
│                                                 │
│ CARACTERÍSTICAS:                                │
│ ❌ NÃO BYPASSA regras de segurança             │
│ ⚠️  ESTÁ SUJEITO a Access Rights               │
│ ⚠️  ESTÁ SUJEITO a Record Rules                │
│ ✅ Pode configurar o sistema (se tiver grupos) │
│ ✅ Usuário para administração diária           │
│                                                 │
│ GRUPOS NECESSÁRIOS (ESSENCIAIS):                │
│ ✅ Internal User (ID: 1) - BASE                │
│ ✅ Access Rights (ID: 2) - ADMIN               │
│ ✅ Settings (ID: 3) - ADMIN                    │
│ ✅ Todos Administrator de cada módulo          │
│                                                 │
│ CONFIGURAÇÃO PADRÃO ODOO:                       │
│ "The admin account is (by default) a member    │
│  of all application security groups"           │
│                                                 │
│ SE FALTAR GRUPOS:                               │
│ ❌ JavaScript errors (context undefined)       │
│ ❌ Módulos não carregam                        │
│ ❌ Interface administrativa não funciona       │
│ ❌ Admin fica "locked" (travado)               │
└─────────────────────────────────────────────────┘
```

#### Tabela Comparativa

| Característica | SUPERUSER (uid=1) | ADMIN (uid=2) |
|----------------|-------------------|---------------|
| **Bypassa Access Rights** | ✅ SIM | ❌ NÃO |
| **Bypassa Record Rules** | ✅ SIM | ❌ NÃO |
| **Precisa de grupos** | ❌ NÃO | ✅ SIM |
| **Uso em produção** | ❌ Emergências | ✅ Administração |
| **Login direto** | ❌ NÃO (modo dev) | ✅ SIM |
| **Sujeito a permissões** | ❌ NÃO | ✅ SIM |

#### Grupos Essenciais do Admin

**GRUPOS BASE (NUNCA podem faltar):**

```sql
-- Verificar grupos essenciais do admin
SELECT
    g.id,
    g.name,
    g.category_id,
    c.name as categoria,
    CASE
        WHEN EXISTS(SELECT 1 FROM res_groups_users_rel WHERE uid = 2 AND gid = g.id)
        THEN '✅ OK'
        ELSE '❌ FALTA - CRÍTICO!'
    END as status
FROM res_groups g
LEFT JOIN ir_module_category c ON g.category_id = c.id
WHERE g.id IN (1, 2, 3)
ORDER BY g.id;
```

**Resultado esperado:**
```
 id |     name      | categoria      | status
----+---------------+----------------+--------
  1 | Internal User | User types     | ✅ OK
  2 | Access Rights | Administration | ✅ OK
  3 | Settings      | Administration | ✅ OK
```

**GRUPOS ADICIONAIS (Recomendados para admin):**

```sql
-- Listar TODOS os grupos Administrator que admin DEVERIA ter
SELECT
    g.id,
    g.name,
    c.name as categoria,
    CASE
        WHEN EXISTS(SELECT 1 FROM res_groups_users_rel WHERE uid = 2 AND gid = g.id)
        THEN '✅ TEM'
        ELSE '❌ FALTA'
    END as status
FROM res_groups g
JOIN ir_module_category c ON g.category_id = c.id
WHERE g.name ILIKE '%administrator%'
ORDER BY c.name, g.name;
```

#### Como Corrigir Admin Locked

**Sintomas de Admin Locked:**
- ❌ Erro JavaScript: `TypeError: Cannot read properties of undefined (reading 'context')`
- ❌ Módulos não carregam na interface
- ❌ "Some modules could not be started"
- ❌ Missing dependencies errors
- ❌ Interface administrativa não funciona

**Script de Correção:**

```sql
-- Script completo em: CORRECAO_ADMIN_LOCKED_20251116.sql

BEGIN;

-- 1. Adicionar grupos CRÍTICOS base
INSERT INTO res_groups_users_rel (uid, gid)
SELECT 2, g.id
FROM res_groups g
WHERE g.id IN (1, 2, 3)  -- Internal User, Access Rights, Settings
  AND NOT EXISTS(SELECT 1 FROM res_groups_users_rel WHERE uid = 2 AND gid = g.id)
ON CONFLICT (uid, gid) DO NOTHING;

-- 2. Adicionar TODOS os grupos Administrator
INSERT INTO res_groups_users_rel (uid, gid)
SELECT 2, g.id
FROM res_groups g
WHERE g.name ILIKE '%administrator%'
  AND NOT EXISTS(SELECT 1 FROM res_groups_users_rel WHERE uid = 2 AND gid = g.id)
ON CONFLICT (uid, gid) DO NOTHING;

-- 3. Validar
SELECT COUNT(*) as total_grupos FROM res_groups_users_rel WHERE uid = 2;
-- Esperado: 40+ grupos

COMMIT;
```

**Após correção SQL:**
```bash
# Reiniciar Odoo
sudo systemctl restart odoo-server

# Verificar logs
sudo tail -50 /var/log/odoo/odoo-server.log | grep -i error

# Testar login
# Acessar: https://odoo.semprereal.com
```

#### Referências Oficiais sobre Admin vs Superuser

**Fonte 1: Odoo Tricks (Security Guide)**
- URL: https://odootricks.tips/about/building-blocks/security/superuser-admin/
- **Citação:** "The admin account is (by default) a member of all application security groups"
- **Citação:** "Superuser mode allows the user to bypass record rules and access rights"

**Fonte 2: GitHub Odoo 15.0**
- URL: https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/security/base_groups.xml
- **Grupos definidos:**
  - `group_erp_manager` (Access Rights)
  - `group_system` (Settings) → implica `group_erp_manager`
  - `group_user` (Internal User)

**Fonte 3: GitHub Odoo 15.0 - res_users_data.xml**
- URL: https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/res_users_data.xml
- **Admin user definition:** `<field name="groups_id" eval="[Command.set([])]"/>`
- **NOTA:** No XML, admin começa SEM grupos, mas na inicialização do banco, Odoo adiciona os grupos automaticamente

**Fonte 4: Documentação Oficial Odoo 15**
- URL: https://www.odoo.com/documentation/15.0/applications/general/users.html
- **Citação:** "From a security standpoint it is recommended to use the admin account (base.user_admin) only in exceptional circumstances"

---

### 0.5 Referências Oficiais Consultadas {#0-5-referencias}

#### Documentação Oficial Odoo

| Recurso | URL | Descrição |
|---------|-----|-----------|
| **Users (Odoo 15)** | https://www.odoo.com/documentation/15.0/applications/general/users.html | Gestão de usuários e access rights |
| **Security (Backend)** | https://www.odoo.com/documentation/15.0/developer/reference/backend/security.html | Access rights, record rules, field access |
| **ORM API** | https://www.odoo.com/documentation/15.0/developer/reference/backend/orm.html | Modelos, métodos, domínios |

#### GitHub Oficial Odoo

| Arquivo | URL | Conteúdo |
|---------|-----|----------|
| **base_groups.xml** | https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/security/base_groups.xml | Definição dos grupos base (Internal User, Settings, Access Rights) |
| **res_users_data.xml** | https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/res_users_data.xml | Configuração do admin user |
| **res_users.py** | https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/models/res_users.py | Modelo de usuários, método _default_groups() |

#### Guides e Tutoriais

| Recurso | URL | Tópicos Cobertos |
|---------|-----|------------------|
| **Odoo Tricks - Superuser vs Admin** | https://odootricks.tips/about/building-blocks/security/superuser-admin/ | Diferença crítica entre superuser e admin |
| **Odoo Tricks - User Access Groups** | https://odootricks.tips/about/building-blocks/security/user-access-groups/ | Como funcionam os grupos de acesso |
| **Odoo Tricks - Record Rules** | https://odootricks.tips/about/building-blocks/security/record-rules/ | Record rules explicadas |
| **Serpent CS - Security Guide** | https://www.serpentcs.com/blog/odoo-module-487/users-groups-access-rights-and-record-rules-in-odoo-230 | Guia completo de segurança |
| **VentorTech - Access Rights** | https://ventor.tech/odoo/odoo-access-rights/ | Estrutura de access rights |

#### Forums e Q&A

| Tópico | URL | Assunto |
|--------|-----|---------|
| **Admin Group Management** | https://www.odoo.com/forum/help-1/hot-to-manage-admin-group-12088 | Gestão do grupo admin |
| **Access Rights vs Settings** | https://www.odoo.com/forum/help-1/administration-settings-and-access-rights-7270 | Diferença entre Access Rights e Settings |
| **Which user is Administrator** | https://stackoverflow.com/questions/71392759/how-do-i-know-which-user-is-administrator-in-odoo | Como identificar admin |

#### Incidents Documentados Neste Projeto

| Incident | Data | Arquivo | Descrição |
|----------|------|---------|-----------|
| **Internal User Removido** | 17/11/2025 | `INCIDENT_REPORT_INTERNAL_USER_20251117.md` | 33 usuários perderam grupo Internal User |
| **Admin User Locked** | 16/11/2025 | `SOLUCAO_ADMIN_LOCKED_EXECUTAR_AGORA.md` | Admin ficou travado por falta de grupos |

#### Comandos de Validação Rápida

**Verificar grupos do admin:**
```bash
ssh odoo-rc "sudo -u postgres psql realcred -c \"
SELECT COUNT(*) as total_grupos FROM res_groups_users_rel WHERE uid = 2;
\""
```

**Verificar grupos críticos:**
```bash
ssh odoo-rc "sudo -u postgres psql realcred -c \"
SELECT g.id, g.name,
    CASE WHEN EXISTS(SELECT 1 FROM res_groups_users_rel WHERE uid = 2 AND gid = g.id)
    THEN '✅' ELSE '❌' END as status
FROM res_groups g WHERE g.id IN (1,2,3);
\""
```

**Verificar módulos instalados:**
```bash
ssh odoo-rc "sudo -u postgres psql realcred -c \"
SELECT name, state FROM ir_module_module WHERE state = 'installed' ORDER BY name;
\""
```

---

## 1. FUNDAMENTOS DE SEGURANÇA NO ODOO 15 {#1-fundamentos}

### 1.1 Arquitetura de Segurança em Camadas

O Odoo 15 implementa segurança em **4 camadas hierárquicas**:

```
┌─────────────────────────────────────────────────────┐
│ Layer 1: ACCESS RIGHTS (ir.model.access)           │
│ ➜ Controla CRUD por modelo + grupo                 │
│ ➜ Decisão: SIM/NÃO para operação inteira           │
│ ➜ Aditivo: União de todos os grupos do usuário     │
└─────────────────────────────────────────────────────┘
                    ↓ SE PERMITIDO
┌─────────────────────────────────────────────────────┐
│ Layer 2: RECORD RULES - Global (ir.rule)           │
│ ➜ Regras SEM grupo específico                      │
│ ➜ RESTRITIVAS: Limitam acesso (multi-company)      │
│ ➜ Aplicadas com AND lógico                         │
└─────────────────────────────────────────────────────┘
                    ↓ SE PASSAR
┌─────────────────────────────────────────────────────┐
│ Layer 3: RECORD RULES - Group (ir.rule)            │
│ ➜ Regras COM grupo específico                      │
│ ➜ PERMISSIVAS: Concedem acesso                     │
│ ➜ Aplicadas com OR lógico entre grupos             │
└─────────────────────────────────────────────────────┘
                    ↓ SE PASSAR
┌─────────────────────────────────────────────────────┐
│ Layer 4: FIELD-LEVEL ACCESS                        │
│ ➜ Restrições em campos específicos                 │
│ ➜ groups attribute em campos do modelo             │
└─────────────────────────────────────────────────────┘
```

### 1.2 Princípios Fundamentais

**PRINCÍPIO 1: Deny by Default**
- Se não há access right para um modelo, acesso é NEGADO
- Se não há record rule, acesso é PERMITIDO (após access rights)

**PRINCÍPIO 2: Access Rights são Aditivos**
- Usuário em grupos A (read+create) e B (write) = read+write+create
- União de todas as permissões de todos os grupos

**PRINCÍPIO 3: Record Rules Globais são Restritivas**
- Rules sem grupo: limitam acesso (multi-company, por exemplo)
- Aplicadas com AND (todas devem passar)

**PRINCÍPIO 4: Record Rules de Grupo são Permissivas**
- Rules com grupo: concedem acesso
- Aplicadas com OR (qualquer uma permite)

**PRINCÍPIO 5: Least Privilege**
- Usuários devem ter APENAS as permissões necessárias
- Evitar acesso desnecessário a dados sensíveis

---

## 2. ACCESS RIGHTS (ir.model.access) {#2-access-rights}

### 2.1 Estrutura da Tabela `ir_model_access`

```sql
CREATE TABLE ir_model_access (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,              -- Nome descritivo da regra
    model_id INTEGER NOT NULL,          -- FK para ir_model
    group_id INTEGER,                   -- FK para res_groups (NULL = todos)
    perm_read BOOLEAN DEFAULT FALSE,    -- Permissão de leitura
    perm_write BOOLEAN DEFAULT FALSE,   -- Permissão de escrita
    perm_create BOOLEAN DEFAULT FALSE,  -- Permissão de criação
    perm_unlink BOOLEAN DEFAULT FALSE,  -- Permissão de exclusão
    active BOOLEAN DEFAULT TRUE
);
```

### 2.2 Campos e Significado

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `name` | VARCHAR | ✅ SIM | Nome descritivo (ex: "crm.lead.user") |
| `model_id` | INTEGER | ✅ SIM | Referência ao modelo (ir.model.id) |
| `group_id` | INTEGER | ❌ NÃO | Grupo ao qual se aplica (NULL = todos os usuários) |
| `perm_read` | BOOLEAN | ❌ NÃO | Se TRUE, permite leitura (SELECT) |
| `perm_write` | BOOLEAN | ❌ NÃO | Se TRUE, permite edição (UPDATE) |
| `perm_create` | BOOLEAN | ❌ NÃO | Se TRUE, permite criação (INSERT) |
| `perm_unlink` | BOOLEAN | ❌ NÃO | Se TRUE, permite exclusão (DELETE) |
| `active` | BOOLEAN | ❌ NÃO | Se FALSE, regra desabilitada |

### 2.3 Comportamento de `group_id`

**group_id = NULL (Vazio):**
- Aplica-se a TODOS os usuários, incluindo:
  - Internal Users
  - Portal Users
  - Public Users (não autenticados)
- **Uso comum:** Dar acesso público a modelos como `res.country`, `res.currency`

**group_id = <ID do Grupo>:**
- Aplica-se APENAS a usuários membros desse grupo
- **Uso comum:** Permissões específicas por função (vendas, compras, etc.)

### 2.4 Lógica de Avaliação

```python
# Pseudocódigo de como o Odoo avalia access rights

def check_access(user, model, operation):
    # Buscar todos os access rights do modelo
    access_rights = ir_model_access.search([
        ('model_id.model', '=', model),
        ('active', '=', True)
    ])

    # Buscar grupos do usuário
    user_groups = user.groups_id.ids

    # Verificar se algum access right concede permissão
    for access in access_rights:
        # Se group_id é NULL, aplica a todos
        if not access.group_id:
            if access[f'perm_{operation}']:
                return True

        # Se group_id está nos grupos do usuário
        elif access.group_id.id in user_groups:
            if access[f'perm_{operation}']:
                return True

    # Se nenhum access right concedeu, negar
    return False
```

### 2.5 Exemplos Práticos

#### Exemplo 1: Acesso Público de Leitura

```sql
-- Permitir que TODOS os usuários leiam países
INSERT INTO ir_model_access (name, model_id, group_id, perm_read, perm_write, perm_create, perm_unlink)
SELECT 'res.country.public', m.id, NULL, true, false, false, false
FROM ir_model m
WHERE m.model = 'res.country';
```

#### Exemplo 2: Acesso Completo para Grupo

```sql
-- Permitir que grupo "Sales / User" tenha acesso completo a crm.lead
INSERT INTO ir_model_access (name, model_id, group_id, perm_read, perm_write, perm_create, perm_unlink)
SELECT 'crm.lead.user', m.id, 13, true, true, true, true
FROM ir_model m
WHERE m.model = 'crm.lead';
```

#### Exemplo 3: Somente Leitura para Grupo

```sql
-- Permitir que grupo "HR / Officer" leia funcionários mas não edite
INSERT INTO ir_model_access (name, model_id, group_id, perm_read, perm_write, perm_create, perm_unlink)
SELECT 'hr.employee.officer.read', m.id, 20, true, false, false, false
FROM ir_model m
WHERE m.model = 'hr.employee';
```

### 2.6 Queries de Verificação

```sql
-- Ver TODOS os access rights de um modelo
SELECT
    a.id,
    a.name,
    m.model,
    g.name as grupo,
    a.perm_read as ler,
    a.perm_write as editar,
    a.perm_create as criar,
    a.perm_unlink as deletar
FROM ir_model_access a
JOIN ir_model m ON a.model_id = m.id
LEFT JOIN res_groups g ON a.group_id = g.id
WHERE m.model = 'crm.lead'
  AND a.active = true
ORDER BY g.name NULLS FIRST;

-- Ver permissões de um usuário específico para um modelo
SELECT DISTINCT
    u.login,
    m.model,
    bool_or(a.perm_read) as pode_ler,
    bool_or(a.perm_write) as pode_editar,
    bool_or(a.perm_create) as pode_criar,
    bool_or(a.perm_unlink) as pode_deletar
FROM res_users u
LEFT JOIN res_groups_users_rel rel ON u.id = rel.uid
LEFT JOIN ir_model_access a ON (a.group_id = rel.gid OR a.group_id IS NULL)
JOIN ir_model m ON a.model_id = m.id
WHERE u.login = 'usuario@example.com'
  AND m.model = 'crm.lead'
  AND a.active = true
GROUP BY u.login, m.model;
```

---

## 3. RECORD RULES (ir.rule) {#3-record-rules}

### 3.1 Estrutura da Tabela `ir_rule`

```sql
CREATE TABLE ir_rule (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,              -- Nome descritivo
    model_id INTEGER NOT NULL,          -- FK para ir_model
    domain_force VARCHAR,               -- Domínio Python (filtro)
    perm_read BOOLEAN DEFAULT TRUE,     -- Aplicar na leitura
    perm_write BOOLEAN DEFAULT TRUE,    -- Aplicar na escrita
    perm_create BOOLEAN DEFAULT TRUE,   -- Aplicar na criação
    perm_unlink BOOLEAN DEFAULT TRUE,   -- Aplicar na exclusão
    global BOOLEAN DEFAULT FALSE,       -- Se TRUE, regra global
    active BOOLEAN DEFAULT TRUE
);

-- Tabela de relacionamento entre regras e grupos
CREATE TABLE rule_group_rel (
    rule_group_id INTEGER,              -- FK para ir_rule
    group_id INTEGER                    -- FK para res_groups
);
```

### 3.2 Campos e Significado

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `name` | VARCHAR | ✅ SIM | Nome descritivo (ex: "Personal Leads") |
| `model_id` | INTEGER | ✅ SIM | Modelo ao qual a regra se aplica |
| `domain_force` | VARCHAR | ✅ SIM | Domínio de filtro (sintaxe Python) |
| `perm_read` | BOOLEAN | ❌ NÃO | Se TRUE, aplica regra em leituras |
| `perm_write` | BOOLEAN | ❌ NÃO | Se TRUE, aplica regra em escritas |
| `perm_create` | BOOLEAN | ❌ NÃO | Se TRUE, aplica regra em criações |
| `perm_unlink` | BOOLEAN | ❌ NÃO | Se TRUE, aplica regra em exclusões |
| `global` | BOOLEAN | ❌ NÃO | Se TRUE, regra global (restritiva) |
| `groups` | M2M | ❌ NÃO | Grupos aos quais a regra se aplica |

### 3.3 IMPORTANTE: Significado dos Campos `perm_*`

**⚠️ ATENÇÃO:** Os campos `perm_read`, `perm_write`, `perm_create`, `perm_unlink` em `ir.rule` têm significado DIFERENTE de `ir.model.access`:

- **Em ir.model.access:** `perm_create = TRUE` significa "CONCEDE permissão de criar"
- **Em ir.rule:** `perm_create = TRUE` significa "APLICA ESTA REGRA ao criar"

**Exemplo:**
```python
# Regra que se aplica APENAS em leituras e escritas (NÃO em criações)
{
    'name': 'Ver Apenas Próprios',
    'perm_read': True,     # Aplica regra ao ler
    'perm_write': True,    # Aplica regra ao editar
    'perm_create': False,  # NÃO aplica regra ao criar
    'perm_unlink': True,   # Aplica regra ao deletar
}
```

### 3.4 Record Rules Globais vs Grupo

#### Regras Globais (global = TRUE)

**Características:**
- Sem grupos associados (rule_group_rel vazio)
- **RESTRITIVAS:** Limitam acesso
- Aplicadas com **AND** lógico (todas devem passar)
- **Uso principal:** Multi-company, restrições de segurança

**Exemplo:**
```sql
-- Regra global: usuários só veem registros da sua empresa
INSERT INTO ir_rule (name, model_id, domain_force, global, perm_read, perm_write, perm_create, perm_unlink)
SELECT
    'Multi-Company Rule',
    m.id,
    '[(''company_id'', ''in'', company_ids)]',
    true,  -- GLOBAL
    true, true, true, true
FROM ir_model m
WHERE m.model = 'crm.lead';
```

#### Regras de Grupo (global = FALSE)

**Características:**
- Com grupos associados (rule_group_rel preenchido)
- **PERMISSIVAS:** Concedem acesso
- Aplicadas com **OR** lógico (qualquer uma permite)
- **Uso principal:** Acesso por função, hierarquia

**Exemplo:**
```sql
-- Regra de grupo: vendedores veem apenas seus leads
INSERT INTO ir_rule (name, model_id, domain_force, global, perm_read, perm_write, perm_create, perm_unlink)
SELECT
    'Personal Leads',
    m.id,
    '[''|'', (''user_id'', ''='', user.id), (''user_id'', ''='', False)]',
    false,  -- NÃO GLOBAL
    true, true, true, true
FROM ir_model m
WHERE m.model = 'crm.lead';

-- Associar ao grupo "Sales / User: Own Documents Only" (ID: 13)
INSERT INTO rule_group_rel (rule_group_id, group_id)
SELECT
    (SELECT id FROM ir_rule WHERE name = 'Personal Leads' AND model_id = (SELECT id FROM ir_model WHERE model = 'crm.lead')),
    13;
```

### 3.5 Sintaxe de Domínio (domain_force)

#### Estrutura Básica

Domínios são listas Python com notação polonesa prefixada:

```python
# Sintaxe básica: [(campo, operador, valor)]
[('user_id', '=', user.id)]

# Com operadores lógicos: ['|', condição1, condição2]
# OU lógico
['|', ('user_id', '=', user.id), ('user_id', '=', False)]

# E lógico (implícito, mas pode usar '&')
['&', ('active', '=', True), ('company_id', '=', user.company_id.id)]

# NÃO lógico
['!', ('state', '=', 'cancelled')]
```

#### Operadores Disponíveis

| Operador | Descrição | Exemplo |
|----------|-----------|---------|
| `=` | Igual | `('user_id', '=', user.id)` |
| `!=` | Diferente | `('state', '!=', 'done')` |
| `>` | Maior que | `('create_date', '>', '2025-01-01')` |
| `>=` | Maior ou igual | `('amount', '>=', 1000)` |
| `<` | Menor que | `('priority', '<', 3)` |
| `<=` | Menor ou igual | `('date', '<=', fields.Date.today())` |
| `in` | Em lista | `('state', 'in', ['draft', 'open'])` |
| `not in` | Não em lista | `('user_id', 'not in', [1, 2])` |
| `like` | Contém (case-sensitive) | `('name', 'like', '%test%')` |
| `ilike` | Contém (case-insensitive) | `('email', 'ilike', '%gmail%')` |
| `=like` | Padrão SQL LIKE | `('code', '=like', 'SALE/%')` |
| `=ilike` | Padrão SQL ILIKE | `('ref', '=ilike', 'inv/%')` |
| `child_of` | Filho de (hierarquia) | `('category_id', 'child_of', [1])` |
| `parent_of` | Pai de (hierarquia) | `('parent_id', 'parent_of', [10])` |

#### Variáveis Especiais

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `user` | Objeto do usuário atual | `user.id`, `user.company_id.id` |
| `user.id` | ID do usuário | `('user_id', '=', user.id)` |
| `user.company_id` | Empresa do usuário | `('company_id', '=', user.company_id.id)` |
| `user.team_id` | Equipe do usuário | `('team_id', '=', user.team_id.id)` |
| `company_ids` | Lista de empresas | `('company_id', 'in', company_ids)` |
| `time` | Módulo time Python | `time.strftime('%Y-01-01')` |
| `False` | Booleano False | `('user_id', '=', False)` |
| `True` | Booleano True | `('active', '=', True)` |

### 3.6 Exemplos Avançados de Domínios

#### Exemplo 1: Leads Pessoais OU Sem Responsável

```python
domain = ['|', ('user_id', '=', user.id), ('user_id', '=', False)]
# SQL equivalente: WHERE (user_id = <current_user>) OR (user_id IS NULL)
```

#### Exemplo 2: Leads da Equipe do Usuário

```python
domain = [
    '|',
    ('team_id', '=', user.team_id.id),
    ('team_id.user_id', '=', user.id)
]
# SQL: WHERE (team_id = <user_team>) OR (team_id.user_id = <user_id>)
```

#### Exemplo 3: Multi-Company com Registros Sem Empresa

```python
domain = [
    '|',
    ('company_id', '=', False),
    ('company_id', 'in', company_ids)
]
# SQL: WHERE (company_id IS NULL) OR (company_id IN (<user_companies>))
```

#### Exemplo 4: Acesso Baseado em Estágio + Usuário

```python
domain = [
    '|',
    '&',
    ('user_id', '=', user.id),
    ('stage_edit', '=', True),
    ('user_id', '=', False)
]
# SQL: WHERE ((user_id = <user>) AND (stage_edit = TRUE)) OR (user_id IS NULL)
```

#### Exemplo 5: Registros dos Últimos 30 Dias

```python
domain = [
    ('create_date', '>=', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
]
```

### 3.7 Operadores Lógicos

#### OU Lógico ('|')

```python
# Prefixo: '|' antes de exatamente 2 condições
['|', condição1, condição2]

# Múltiplos ORs: encadear '|'
['|', '|', cond1, cond2, cond3]
# Equivalente a: cond1 OR cond2 OR cond3

['|', '|', '|', cond1, cond2, cond3, cond4]
# Equivalente a: cond1 OR cond2 OR cond3 OR cond4
```

#### E Lógico ('&')

```python
# Implícito: condições sequenciais são AND
[cond1, cond2, cond3]
# Equivalente a: cond1 AND cond2 AND cond3

# Explícito: prefixo '&' antes de exatamente 2 condições
['&', cond1, cond2]

# Múltiplos ANDs: encadear '&'
['&', '&', cond1, cond2, cond3]
```

#### NÃO Lógico ('!')

```python
# Prefixo: '!' antes de exatamente 1 condição
['!', ('state', '=', 'cancelled')]
# Equivalente a: NOT (state = 'cancelled')

# Pode combinar com outros operadores
['&', ('active', '=', True), '!', ('state', '=', 'done')]
# Equivalente a: active = TRUE AND NOT (state = 'done')
```

#### Combinações Complexas

```python
# (A OR B) AND C
['&', '|', condA, condB, condC]

# A OR (B AND C)
['|', condA, '&', condB, condC]

# (A AND B) OR (C AND D)
['|', '&', condA, condB, '&', condC, condD]

# NOT (A OR B)
['!', '|', condA, condB]
```

### 3.8 ⚠️ ARMADILHAS COMUNS

#### Armadilha 1: Ordem de Avaliação

```python
# ❌ ERRADO: Esta regra SEMPRE bloqueia criação
domain = ['|', '&', ('user_id', '=', user.id), ('user_id', '=', False), ('stage_edit', '=', True)]
# Problema: Durante CREATE, stage_edit pode ser NULL/False

# ✅ CORRETO: Permitir criação com usuário
domain = ['|', '|', ('user_id', '=', user.id), ('user_id', '=', False), ('stage_edit', '=', True)]
```

#### Armadilha 2: Campos Nullable

```python
# ❌ ERRADO: Bloqueia registros onde user_id é NULL
domain = [('user_id', '=', user.id)]

# ✅ CORRETO: Permite registros sem responsável
domain = ['|', ('user_id', '=', user.id), ('user_id', '=', False)]
```

#### Armadilha 3: Múltiplos Grupos

```python
# Se usuário tem grupos A e B:
# - Regra do grupo A: [('team_id', '=', 1)]
# - Regra do grupo B: [('team_id', '=', 2)]
# Resultado: Vê registros com team_id = 1 OR team_id = 2 (OR lógico)
```

### 3.9 Queries de Verificação

```sql
-- Ver TODAS as regras de um modelo
SELECT
    r.id,
    r.name,
    r.domain_force,
    r.global,
    r.perm_read,
    r.perm_write,
    r.perm_create,
    r.perm_unlink,
    COALESCE(array_agg(g.name) FILTER (WHERE g.id IS NOT NULL), '{}') as grupos
FROM ir_rule r
JOIN ir_model m ON r.model_id = m.id
LEFT JOIN rule_group_rel rel ON r.id = rel.rule_group_id
LEFT JOIN res_groups g ON rel.group_id = g.id
WHERE m.model = 'crm.lead'
  AND r.active = true
GROUP BY r.id, r.name, r.domain_force, r.global, r.perm_read, r.perm_write, r.perm_create, r.perm_unlink
ORDER BY r.global DESC, r.id;

-- Ver regras aplicadas a um usuário específico
SELECT DISTINCT
    u.login,
    r.name as regra,
    r.domain_force,
    r.global,
    g.name as grupo
FROM res_users u
LEFT JOIN res_groups_users_rel ugrel ON u.id = ugrel.uid
LEFT JOIN rule_group_rel rgrel ON ugrel.gid = rgrel.group_id
LEFT JOIN ir_rule r ON rgrel.rule_group_id = r.id
LEFT JOIN res_groups g ON rgrel.group_id = g.id
JOIN ir_model m ON r.model_id = m.id
WHERE u.login = 'usuario@example.com'
  AND m.model = 'crm.lead'
  AND r.active = true
ORDER BY r.global DESC, r.name;
```

---

## 4. GROUPS (res.groups) {#4-groups}

### 4.1 Estrutura da Tabela `res_groups`

```sql
CREATE TABLE res_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,              -- Nome do grupo
    category_id INTEGER,                -- FK para ir_module_category
    comment TEXT,                       -- Descrição do grupo
    implied_ids INTEGER[],              -- Array de grupos implicados
    share BOOLEAN DEFAULT FALSE         -- Se TRUE, grupo de portal/público
);

-- Tabela de relacionamento usuários-grupos
CREATE TABLE res_groups_users_rel (
    gid INTEGER,                        -- FK para res_groups
    uid INTEGER,                        -- FK para res_users
    PRIMARY KEY (gid, uid)
);

-- Tabela de relacionamento grupos-grupos (implied)
CREATE TABLE res_groups_implied_rel (
    gid INTEGER,                        -- FK para res_groups (grupo pai)
    hid INTEGER,                        -- FK para res_groups (grupo filho)
    PRIMARY KEY (gid, hid)
);
```

### 4.2 Campos e Significado

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `name` | VARCHAR | ✅ SIM | Nome visível do grupo (ex: "Sales / User") |
| `category_id` | INTEGER | ❌ NÃO | Categoria para organização (ex: "Sales") |
| `comment` | TEXT | ❌ NÃO | Descrição/tooltip do grupo |
| `implied_ids` | M2M | ❌ NÃO | Grupos herdados automaticamente |
| `share` | BOOLEAN | ❌ NÃO | Se TRUE, é grupo de portal/público |

### 4.3 Categorias de Grupos (ir.module.category)

Grupos são organizados em categorias para facilitar navegação:

```sql
-- Ver categorias existentes
SELECT
    id,
    name,
    sequence,
    parent_id
FROM ir_module_category
WHERE visible = true
ORDER BY sequence, name;
```

**Categorias Comuns:**

| ID | Nome | Uso |
|----|------|-----|
| - | Sales | Grupos de vendas/CRM |
| - | Human Resources | Grupos de RH |
| - | Accounting | Grupos de contabilidade |
| - | Inventory | Grupos de estoque |
| - | Technical | Grupos técnicos |
| - | Extra Rights | Permissões especiais |

### 4.4 Grupos de Sistema

**Internal User (base.group_user):**
- ID normalmente: 1
- Grupo base para usuários internos
- Acesso ao backend do Odoo

**Portal (base.group_portal):**
- Usuários externos com acesso limitado
- Veem apenas seus próprios dados
- Não acessam backend

**Public (base.group_public):**
- Usuários não autenticados
- Acesso mínimo (website público)

### 4.5 Queries de Verificação

```sql
-- Ver TODOS os grupos de um usuário
SELECT
    u.id,
    u.login,
    g.id as group_id,
    g.name as grupo,
    cat.name as categoria
FROM res_users u
JOIN res_groups_users_rel rel ON u.id = rel.uid
JOIN res_groups g ON rel.gid = g.id
LEFT JOIN ir_module_category cat ON g.category_id = cat.id
WHERE u.login = 'usuario@example.com'
ORDER BY cat.name, g.name;

-- Ver todos os usuários de um grupo
SELECT
    g.name as grupo,
    u.id,
    u.login,
    u.active
FROM res_groups g
JOIN res_groups_users_rel rel ON g.id = rel.gid
JOIN res_users u ON rel.uid = u.id
WHERE g.id = 13  -- ID do grupo
ORDER BY u.login;

-- Ver grupos por categoria
SELECT
    cat.name as categoria,
    g.id,
    g.name as grupo,
    COUNT(DISTINCT rel.uid) as total_usuarios
FROM res_groups g
LEFT JOIN ir_module_category cat ON g.category_id = cat.id
LEFT JOIN res_groups_users_rel rel ON g.id = rel.gid
WHERE g.share = false
GROUP BY cat.name, g.id, g.name
ORDER BY cat.name, g.name;
```

---

## 5. HIERARQUIA E IMPLIED GROUPS {#5-hierarquia}

### 5.1 Conceito de Implied Groups

**Definição:** Quando um usuário é adicionado a um grupo A que tem `implied_ids` apontando para grupos B e C, o usuário **automaticamente** recebe B e C também.

**Diferença de Herança Real:**
- Herança real: Remover grupo pai remove grupos filhos
- Implied: É possível remover grupos implicados manualmente sem remover o implicador

### 5.2 Estrutura de Hierarquia

```
┌─────────────────────────────────────┐
│ Sales / Administrator (ID: 15)      │
│ implied_ids: [14, 13]               │
└────────────────┬────────────────────┘
                 │
                 ├────────────────────────────────┐
                 ↓                                ↓
┌──────────────────────────────────┐  ┌──────────────────────────────────┐
│ Sales / User: All Documents (14) │  │ Sales / User: Own Documents (13) │
│ implied_ids: [13]                │  │ implied_ids: []                  │
└──────────────────────────────────┘  └──────────────────────────────────┘
```

**Comportamento:**
- Adicionar usuário ao grupo 15 (Administrator) → Recebe automaticamente 14 e 13
- Adicionar usuário ao grupo 14 (All Documents) → Recebe automaticamente 13
- Adicionar usuário ao grupo 13 (Own Documents) → Recebe apenas 13

### 5.3 Exemplo Prático: Sales Groups

```sql
-- Ver hierarquia de grupos de Sales
WITH RECURSIVE group_hierarchy AS (
    -- Base: grupos sem implied
    SELECT
        g.id,
        g.name,
        g.category_id,
        0 as level,
        ARRAY[g.id] as path
    FROM res_groups g
    WHERE g.category_id = (SELECT id FROM ir_module_category WHERE name = 'Sales')
    AND NOT EXISTS (
        SELECT 1 FROM res_groups_implied_rel WHERE hid = g.id
    )

    UNION ALL

    -- Recursivo: grupos que implicam os anteriores
    SELECT
        g.id,
        g.name,
        g.category_id,
        gh.level + 1,
        gh.path || g.id
    FROM res_groups g
    JOIN res_groups_implied_rel rel ON g.id = rel.gid
    JOIN group_hierarchy gh ON rel.hid = gh.id
    WHERE NOT g.id = ANY(gh.path)  -- Evitar loops
)
SELECT
    level,
    id,
    name,
    path
FROM group_hierarchy
ORDER BY level, name;
```

### 5.4 Best Practices com Implied Groups

**✅ FAZER:**
1. Criar hierarquia lógica (Admin > Manager > User)
2. Grupos mais poderosos devem implicar grupos menos poderosos
3. Documentar hierarquia em comentários

**❌ NÃO FAZER:**
1. Criar loops de implicação (A implica B, B implica A)
2. Implicar grupos de categorias diferentes sem razão clara
3. Usar implied_ids para substituir record rules

### 5.5 Queries de Gerenciamento

```sql
-- Ver quais grupos um grupo implica
SELECT
    g1.name as grupo_principal,
    g2.name as grupo_implicado
FROM res_groups g1
JOIN res_groups_implied_rel rel ON g1.id = rel.gid
JOIN res_groups g2 ON rel.hid = g2.id
WHERE g1.id = 15
ORDER BY g2.name;

-- Ver quais grupos implicam um grupo específico
SELECT
    g1.name as grupo_principal,
    g2.name as grupo_implicado
FROM res_groups g1
JOIN res_groups_implied_rel rel ON g1.id = rel.gid
JOIN res_groups g2 ON rel.hid = g2.id
WHERE g2.id = 13
ORDER BY g1.name;

-- Adicionar implied group (grupo 15 implica grupo 14)
INSERT INTO res_groups_implied_rel (gid, hid)
VALUES (15, 14)
ON CONFLICT DO NOTHING;

-- Remover implied group
DELETE FROM res_groups_implied_rel
WHERE gid = 15 AND hid = 14;
```

---

### 5.6 🚨 ATENÇÃO: Comportamento REAL de Implied Groups {#5-6-real-implied}

**INCIDENT CRÍTICO DESCOBERTO: 17/11/2025**

#### ❌ MITO (PERIGOSO - CAUSOU INCIDENT CRÍTICO):

"Se grupo A implica grupo B, e usuário tem A, então B é automaticamente atribuído ao usuário na tabela `res_groups_users_rel`, tornando B redundante e podendo ser removido."

#### ✅ REALIDADE (COMPORTAMENTO REAL DO ODOO):

**Implied groups são verificados em RUNTIME durante a checagem de permissões, NÃO criam registros físicos na tabela `res_groups_users_rel`.**

---

#### Como Funciona REALMENTE:

**1. Estrutura de Dados:**

```sql
-- res_groups_implied_rel define RELAÇÃO entre grupos
-- Exemplo: Grupo 13 (Own Documents) implica grupo 1 (Internal User)
SELECT gid, hid FROM res_groups_implied_rel WHERE gid = 13;
-- Resultado: gid=13, hid=1

-- res_groups_users_rel define ATRIBUIÇÃO física ao usuário
-- O que ESTÁ na tabela:
SELECT uid, gid FROM res_groups_users_rel WHERE uid = 346;
-- Resultado: uid=346, gid=13  (usuário TEM grupo 13)
-- Resultado: uid=346, gid=1   (usuário TEM grupo 1 FISICAMENTE)

-- O que NÃO ESTÁ:
-- O Odoo NÃO cria automaticamente registro (uid=346, gid=1) quando atribui gid=13
```

**2. Verificação de Permissão em Runtime:**

```python
# Pseudocódigo de como Odoo verifica permissões

def user_has_group(user_id, group_id):
    # PASSO 1: Verifica se usuário tem grupo DIRETAMENTE
    has_directly = db.query("""
        SELECT 1 FROM res_groups_users_rel
        WHERE uid = %s AND gid = %s
    """, [user_id, group_id])

    if has_directly:
        return True

    # PASSO 2: Verifica se usuário tem algum grupo que IMPLICA o grupo procurado
    has_via_implied = db.query("""
        SELECT 1 FROM res_groups_users_rel rel
        JOIN res_groups_implied_rel impl ON rel.gid = impl.gid
        WHERE rel.uid = %s AND impl.hid = %s
    """, [user_id, group_id])

    return bool(has_via_implied)

# EXEMPLO PRÁTICO:
# Usuário 346 tem grupo 13 (Own Documents) fisicamente
# Grupo 13 implica grupo 1 (Internal User)

user_has_group(346, 13)  → True  (verificação direta: usuário TEM gid=13)
user_has_group(346, 1)   → True  (verificação implied: gid=13 implica gid=1)

# MAS ATENÇÃO: Se removermos grupo 1 fisicamente:
DELETE FROM res_groups_users_rel WHERE uid=346 AND gid=1;

# Alguns módulos CHECAM APENAS grupo 1 DIRETAMENTE:
SELECT id FROM dms_directory WHERE ...;  -- Requer grupo 1 DIRETO
# Resultado: ERRO "Você não tem permissão para acessar 'dms.directory'"
```

**3. Por Que Grupos Base DEVEM Estar Fisicamente Atribuídos:**

```sql
-- Alguns access rights requerem grupo ESPECÍFICO:
SELECT * FROM ir_model_access
WHERE model_id = (SELECT id FROM ir_model WHERE model = 'dms.directory');

-- Resultado:
-- id  | name                     | group_id | perm_read
-- 1168| dms_directory_base_user  |    1     | t

-- Este access right verifica APENAS grupo 1 (Internal User)
-- NÃO verifica implied groups!
-- Por isso, se usuário não tem gid=1 FISICAMENTE, acesso é negado
```

**4. Quando Implied Groups SÃO Verificados vs NÃO SÃO:**

✅ **Implied groups SÃO verificados:**
- Verificação via ORM do Odoo (`user.has_group()`)
- Record rules (ir.rule) - domínio avaliado em Python
- Menu visibility (verificação via XML)
- View visibility (atributo `groups`)

❌ **Implied groups NÃO SÃO verificados (ou podem falhar):**
- Access rights (ir.model.access) - alguns módulos verificam grupo direto
- Módulos de terceiros que checam `res_groups_users_rel` diretamente
- Funções SQL que não usam ORM
- Alguns controladores web que verificam grupo via SQL

---

#### 🔴 INCIDENT REAL - 17/11/2025

**O QUE ACONTECEU:**

Script de limpeza de grupos redundantes executado na Fase 3:

```sql
-- ❌ SCRIPT INCORRETO (CAUSOU INCIDENT CRÍTICO)
DELETE FROM res_groups_users_rel
WHERE (uid, gid) IN (
    SELECT DISTINCT rel.uid, rel.gid
    FROM res_groups_users_rel rel
    WHERE EXISTS (
        SELECT 1
        FROM res_groups_implied_rel gi
        JOIN res_groups_users_rel rel2 ON rel2.uid = rel.uid AND rel2.gid = gi.gid
        WHERE gi.hid = rel.gid  -- ← ERRO: Assumiu que implied = redundante
    )
);
```

**RESULTADO:**
- ❌ Removeu grupo 1 (Internal User) de 33 usuários
- ❌ Admin perdeu acesso ao DMS (dms.directory)
- ❌ Vendedores perderam acesso ao CRM e Chat
- ❌ Sistema COMPLETAMENTE INOPERANTE por 2 horas

**CAUSA RAIZ:**
- Script assumiu que grupo 1 era "redundante" porque grupo 13 implica 1
- MAS: Grupo 1 DEVE estar fisicamente atribuído para certos access rights

---

#### ✅ REGRA DE OURO: GRUPOS PROTEGIDOS

**NUNCA, EM HIPÓTESE ALGUMA, REMOVER ESTES GRUPOS:**

```sql
-- Tabela de grupos PROTEGIDOS (criar permanentemente no banco)
CREATE TABLE IF NOT EXISTS protected_groups (
    group_id INTEGER PRIMARY KEY,
    group_name VARCHAR(255),
    reason TEXT,
    created_date TIMESTAMP DEFAULT NOW()
);

INSERT INTO protected_groups (group_id, group_name, reason) VALUES
(1, 'Internal User', 'Grupo base essencial para TODOS usuários internos - NUNCA remover'),
(9, 'Portal', 'Grupo base para usuários portal - NUNCA remover'),
(10, 'Public', 'Grupo base para usuários públicos - NUNCA remover'),
(3, 'Settings', 'Grupo admin essencial - NUNCA remover');

-- QUALQUER script que remove grupos DEVE verificar:
DELETE FROM res_groups_users_rel
WHERE gid NOT IN (SELECT group_id FROM protected_groups)
  AND ...outras condições...;
```

---

#### ✅ SCRIPT CORRETO para Remover Grupos Redundantes

```sql
-- ✅ SCRIPT CORRIGIDO (COM PROTEÇÃO)
BEGIN;

-- 1. Criar lista de grupos protegidos (NUNCA remover)
CREATE TEMP TABLE protected_groups_temp AS
SELECT UNNEST(ARRAY[1, 9, 10, 3]) as gid;

-- 2. Identificar grupos REALMENTE redundantes (EXCLUINDO protegidos)
CREATE TEMP TABLE redundant_groups AS
SELECT DISTINCT rel.uid, rel.gid
FROM res_groups_users_rel rel
JOIN res_users u ON rel.uid = u.id
WHERE u.active = true
  AND rel.gid NOT IN (SELECT gid FROM protected_groups_temp)  -- ← PROTEÇÃO!
  AND EXISTS (
      SELECT 1
      FROM res_groups_implied_rel gi
      JOIN res_groups_users_rel rel2 ON rel2.uid = rel.uid AND rel2.gid = gi.gid
      WHERE gi.hid = rel.gid
        AND gi.gid != rel.gid
        AND gi.gid NOT IN (SELECT gid FROM protected_groups_temp)  -- ← PROTEÇÃO!
  );

-- 3. VALIDAR impacto ANTES de deletar
SELECT
    'ATENÇÃO: Serão removidos ' || COUNT(*) || ' grupos de ' ||
    COUNT(DISTINCT uid) || ' usuários' as alerta
FROM redundant_groups;

-- 4. Mostrar amostra do que será removido
SELECT
    u.login,
    g.name,
    CASE
        WHEN g.id IN (SELECT gid FROM protected_groups_temp)
        THEN 'PROTEGIDO - NÃO SERÁ REMOVIDO'
        ELSE 'Será removido'
    END as status
FROM redundant_groups rg
JOIN res_users u ON rg.uid = u.id
JOIN res_groups g ON rg.gid = g.id
LIMIT 20;

-- 5. SE VALIDADO, descomentar abaixo para executar:
-- DELETE FROM res_groups_users_rel
-- WHERE (uid, gid) IN (SELECT uid, gid FROM redundant_groups);

ROLLBACK;  -- Mudar para COMMIT após validação manual
```

---

#### 📊 Query de Validação (Executar DIARIAMENTE)

```sql
-- ALERTA CRÍTICO: Verificar se algum usuário ativo não tem Internal User
SELECT
    u.id,
    u.login,
    u.active,
    CASE
        WHEN EXISTS (
            SELECT 1 FROM res_groups_users_rel
            WHERE uid = u.id AND gid = 1
        ) THEN 'OK'
        ELSE '🚨 ERRO CRÍTICO: SEM INTERNAL USER!'
    END as status_internal_user
FROM res_users u
WHERE u.active = true
  AND u.share = false  -- Usuários internos (não Portal/Public)
  AND u.id != 1  -- Excluir OdooBot
HAVING status_internal_user != 'OK';

-- Se retornar algum registro → ALERTA CRÍTICO IMEDIATO!
-- Restaurar grupo Internal User imediatamente:

-- INSERT INTO res_groups_users_rel (uid, gid)
-- SELECT u.id, 1
-- FROM res_users u
-- WHERE u.active = true AND u.share = false AND u.id != 1
-- ON CONFLICT DO NOTHING;
```

---

#### 📚 RESUMO: O que Você DEVE Saber

✅ **FAZER:**
1. Sempre atribuir grupo Internal User (1) FISICAMENTE aos usuários
2. Usar implied_ids para criar hierarquia lógica
3. Proteger grupos base (1, 9, 10, 3) em TODOS os scripts
4. Validar impacto ANTES de qualquer DELETE em massa
5. Testar em dev ANTES de executar em produção

❌ **NUNCA FAZER:**
1. Assumir que implied groups criam registros físicos
2. Remover grupos base pensando que são "redundantes"
3. Executar DELETE em res_groups_users_rel sem WHERE clause protegendo grupos base
4. Confiar apenas em verificação via implied (alguns módulos não verificam)

---

## 6. FIELD-LEVEL SECURITY {#6-field-security}

### 6.1 Conceito

Field-level security permite restringir acesso a campos específicos de um modelo, independente de access rights.

**Implementação:** Atributo `groups` na definição do campo no modelo Python.

### 6.2 Exemplo de Código

```python
from odoo import models, fields

class SaleOrder(models.Model):
    _name = 'sale.order'

    # Campo visível para todos
    name = fields.Char('Order Reference', required=True)

    # Campo visível apenas para grupo "Sales / Manager"
    margin = fields.Float(
        'Margin',
        groups='sales_team.group_sale_manager'
    )

    # Campo visível para múltiplos grupos (OR lógico)
    cost = fields.Float(
        'Cost',
        groups='sales_team.group_sale_manager,account.group_account_manager'
    )
```

### 6.3 Comportamento

**Se usuário NÃO está no grupo:**
- Campo não aparece em views (form, tree, kanban)
- Campo não retornado em read()
- Tentativa de write() no campo é ignorada silenciosamente

**Se usuário ESTÁ no grupo:**
- Campo aparece normalmente
- Todas as operações permitidas

### 6.4 Verificação de Field Security

```sql
-- Verificar campos com restrição de grupo (via XML/código)
-- Não há tabela direta no banco, está no código Python

-- Alternativa: Buscar em ir.model.fields
SELECT
    m.model,
    f.name as campo,
    f.ttype as tipo,
    f.groups as grupos_restritos
FROM ir_model_fields f
JOIN ir_model m ON f.model_id = m.id
WHERE f.groups IS NOT NULL
ORDER BY m.model, f.name;
```

### 6.5 Best Practices

**✅ FAZER:**
1. Usar para campos sensíveis (salário, margem, custo)
2. Documentar claramente quais campos são restritos
3. Testar com usuários de diferentes grupos

**❌ NÃO FAZER:**
1. Usar para segurança crítica (preferir record rules)
2. Restringir campos obrigatórios sem garantir preenchimento
3. Misturar field security com lógica de negócio complexa

---

## 7. BEST PRACTICES {#7-best-practices}

### 7.1 Princípio do Menor Privilégio (Least Privilege)

**Definição:** Usuários devem ter APENAS as permissões necessárias para suas funções.

**Implementação:**
```sql
-- ❌ ERRADO: Dar grupo Administrator para todos
INSERT INTO res_groups_users_rel (gid, uid)
SELECT 15, u.id
FROM res_users u
WHERE u.active = true;

-- ✅ CORRETO: Dar grupos específicos por função
-- Vendedores: grupo "User: Own Documents Only"
INSERT INTO res_groups_users_rel (gid, uid)
SELECT 13, u.id
FROM res_users u
WHERE u.id IN (SELECT id FROM hr_employee WHERE department_id = <sales_dept>);

-- Gerentes: grupo "User: All Documents"
INSERT INTO res_groups_users_rel (gid, uid)
SELECT 14, u.id
FROM res_users u
WHERE u.id IN (SELECT id FROM hr_employee WHERE job_id = <manager_job>);
```

### 7.2 Segregação de Funções (Separation of Duties)

**Definição:** Evitar que uma pessoa tenha controle total sobre processo crítico.

**Exemplo:**
```sql
-- Criar grupos separados
-- Grupo 1: Pode criar pedidos de compra
-- Grupo 2: Pode aprovar pedidos de compra
-- Grupo 3: Pode fazer pagamentos

-- NUNCA dar os 3 grupos para mesma pessoa
```

### 7.3 Hierarquia Lógica de Grupos

**Estrutura recomendada:**
```
Administrator (tudo)
    ↓ implied
Manager (gerenciar equipe + próprio trabalho)
    ↓ implied
User (apenas próprio trabalho)
```

**Implementação:**
```sql
-- Criar grupos com hierarquia
BEGIN;

-- Grupo base: User
INSERT INTO res_groups (name, category_id, comment)
VALUES ('Meu Módulo / User', <cat_id>, 'Acesso básico ao módulo');

-- Grupo intermediário: Manager
INSERT INTO res_groups (name, category_id, comment)
VALUES ('Meu Módulo / Manager', <cat_id>, 'Gerencia equipe e dados');

-- Adicionar implied: Manager implica User
INSERT INTO res_groups_implied_rel (gid, hid)
VALUES (
    (SELECT id FROM res_groups WHERE name = 'Meu Módulo / Manager'),
    (SELECT id FROM res_groups WHERE name = 'Meu Módulo / User')
);

COMMIT;
```

### 7.4 Record Rules: Global vs Grupo

**Global Rules - Use para:**
- Multi-company (garantir isolamento)
- Restrições de segurança que NUNCA podem ser contornadas
- Compliance e regulamentação

**Group Rules - Use para:**
- Acesso por função (vendedor, gerente, etc.)
- Hierarquia organizacional
- Visibilidade por equipe

### 7.5 Evitar Sobrecarga de Permissões

**❌ PROBLEMA: Usuário com muitos grupos**
```sql
-- Usuário com 50+ grupos
SELECT u.login, COUNT(*) as total_grupos
FROM res_users u
JOIN res_groups_users_rel rel ON u.id = rel.uid
WHERE u.login = 'usuario@example.com'
GROUP BY u.login;
-- Resultado: 57 grupos
```

**Impacto:**
- Performance degradada (muitas regras para avaliar)
- Difícil troubleshooting
- Segurança comprometida (difícil auditar)

**✅ SOLUÇÃO: Consolidar em grupos bem definidos**
```sql
-- Criar grupo consolidado "Vendedor Completo"
-- Com implied_ids apontando para grupos necessários
-- Adicionar usuário apenas a este grupo
```

### 7.6 Naming Conventions

**Grupos:**
```
<Módulo> / <Nível>
Exemplos:
- Sales / User
- Sales / Manager
- Sales / Administrator
```

**Access Rights:**
```
<modelo>.<grupo_abreviado>
Exemplos:
- crm.lead.user
- crm.lead.manager
- crm.lead.admin
```

**Record Rules:**
```
<Descrição> <Tipo>
Exemplos:
- Personal Leads
- Team Leads
- Multi-Company Rule
```

### 7.7 Documentação Obrigatória

**Em cada grupo, documentar:**
1. Propósito do grupo
2. Quem deve ter (cargo/função)
3. Quais permissões concede
4. Implied groups (se houver)

**Exemplo:**
```sql
UPDATE res_groups
SET comment = 'PROPÓSITO: Vendedores que trabalham em equipe
QUEM: Vendedores plenos e seniores
PERMISSÕES:
- Ver todas as oportunidades da equipe
- Criar/editar oportunidades
- Não pode deletar
IMPLIED GROUPS:
- Sales / User: Own Documents Only
CRIADO: 2025-11-16
ÚLTIMA REVISÃO: 2025-11-16'
WHERE id = 14;
```

### 7.8 Auditoria e Revisão Periódica

**Mensal:**
```sql
-- Listar usuários sem atividade há 30+ dias com grupos sensíveis
SELECT
    u.login,
    u.login_date,
    array_agg(g.name) as grupos_sensiveis
FROM res_users u
JOIN res_groups_users_rel rel ON u.id = rel.uid
JOIN res_groups g ON rel.gid = g.id
WHERE u.active = true
  AND (u.login_date IS NULL OR u.login_date < CURRENT_DATE - INTERVAL '30 days')
  AND g.id IN (15, 14)  -- Grupos sensíveis
GROUP BY u.login, u.login_date
ORDER BY u.login_date NULLS FIRST;
```

**Trimestral:**
```sql
-- Revisar todos os usuários e seus grupos
-- Verificar se ainda precisam de cada grupo
SELECT
    u.login,
    array_agg(g.name ORDER BY g.name) as todos_grupos,
    COUNT(*) as total
FROM res_users u
JOIN res_groups_users_rel rel ON u.id = rel.uid
JOIN res_groups g ON rel.gid = g.id
WHERE u.active = true
GROUP BY u.login
HAVING COUNT(*) > 20  -- Alerta: muitos grupos
ORDER BY total DESC;
```

**Anual:**
```sql
-- Revisar todos os access rights e record rules
-- Verificar se ainda são necessários
SELECT
    'access_right' as tipo,
    a.name,
    m.model,
    g.name as grupo,
    a.create_date
FROM ir_model_access a
JOIN ir_model m ON a.model_id = m.id
LEFT JOIN res_groups g ON a.group_id = g.id
WHERE a.active = true

UNION ALL

SELECT
    'record_rule' as tipo,
    r.name,
    m.model,
    string_agg(g.name, ', ') as grupo,
    r.create_date
FROM ir_rule r
JOIN ir_model m ON r.model_id = m.id
LEFT JOIN rule_group_rel rel ON r.id = rel.rule_group_id
LEFT JOIN res_groups g ON rel.group_id = g.id
WHERE r.active = true
GROUP BY r.id, r.name, m.model, r.create_date
ORDER BY create_date DESC;
```

---

### 7.9 🚨 GRUPOS PROTEGIDOS - NUNCA REMOVER {#7-9-protected-groups}

**ADICIONADO APÓS INCIDENT 17/11/2025**

Alguns grupos são ESSENCIAIS para o funcionamento do Odoo e **NUNCA devem ser removidos** de usuários ativos, mesmo que pareçam "redundantes" devido a implied groups.

#### Lista de Grupos Protegidos

| ID | Nome | XML ID | Por Que é Protegido |
|----|------|--------|---------------------|
| 1 | Internal User | base.group_user | Grupo base para TODOS usuários internos. Alguns access rights verificam este grupo DIRETAMENTE sem considerar implied. |
| 9 | Portal | base.group_portal | Grupo base para usuários portal. Essencial para acesso externo. |
| 10 | Public | base.group_public | Grupo base para usuários não autenticados. Website público depende deste grupo. |
| 3 | Settings | base.group_system | Acesso a configurações do sistema. Crítico para administração. |

#### Criar Tabela de Proteção

```sql
-- Criar tabela permanente de grupos protegidos
CREATE TABLE IF NOT EXISTS protected_groups (
    group_id INTEGER PRIMARY KEY,
    group_name VARCHAR(255) NOT NULL,
    xml_id VARCHAR(255),
    reason TEXT NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    updated_date TIMESTAMP DEFAULT NOW()
);

-- Inserir grupos protegidos
INSERT INTO protected_groups (group_id, group_name, xml_id, reason) VALUES
(1, 'Internal User', 'base.group_user',
 'Grupo base essencial para TODOS usuários internos. Alguns módulos verificam este grupo DIRETAMENTE sem considerar implied groups. INCIDENT 17/11/2025: Remoção deste grupo causou falha completa de permissões em 33 usuários.'),

(9, 'Portal', 'base.group_portal',
 'Grupo base para usuários externos (portal). Essencial para acesso de clientes e parceiros.'),

(10, 'Public', 'base.group_public',
 'Grupo base para usuários não autenticados. Website público e eCommerce dependem deste grupo.'),

(3, 'Settings', 'base.group_system',
 'Acesso a configurações do sistema. Crítico para administração e manutenção.')
ON CONFLICT (group_id) DO UPDATE
SET updated_date = NOW();

-- Adicionar comentário à tabela
COMMENT ON TABLE protected_groups IS
'Grupos que NUNCA devem ser removidos de usuários. Criado após incident crítico de 17/11/2025.';
```

#### Função de Proteção em Scripts

```sql
-- Criar função helper para verificar se grupo é protegido
CREATE OR REPLACE FUNCTION is_protected_group(p_group_id INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM protected_groups WHERE group_id = p_group_id
    );
END;
$$ LANGUAGE plpgsql;

-- Exemplo de uso:
SELECT is_protected_group(1);  -- Retorna TRUE
SELECT is_protected_group(100);  -- Retorna FALSE
```

#### Template de Script Seguro

```sql
-- TEMPLATE: Qualquer script que modifica res_groups_users_rel
BEGIN;

-- 1. Verificar se tabela protected_groups existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'protected_groups') THEN
        RAISE EXCEPTION 'Tabela protected_groups não existe! Criar antes de executar scripts de permissão.';
    END IF;
END $$;

-- 2. Criar temp table com grupos protegidos
CREATE TEMP TABLE protected_groups_temp AS
SELECT group_id as gid FROM protected_groups;

-- 3. Seu script aqui - SEMPRE incluir WHERE clause protegendo grupos
-- Exemplo: Remover usuário de um grupo
DELETE FROM res_groups_users_rel
WHERE uid = <USER_ID>
  AND gid = <GROUP_ID>
  AND gid NOT IN (SELECT gid FROM protected_groups_temp);  -- ← PROTEÇÃO!

-- 4. Validar resultado
SELECT
    CASE
        WHEN COUNT(*) > 0 THEN
            '⚠️ ATENÇÃO: Tentativa de remover grupo protegido foi BLOQUEADA'
        ELSE
            '✅ OK: Nenhum grupo protegido foi afetado'
    END as status
FROM res_groups_users_rel
WHERE uid = <USER_ID>
  AND gid IN (SELECT gid FROM protected_groups_temp);

COMMIT;  -- ou ROLLBACK se houver problemas
```

---

### 7.10 🚨 Script de Validação Diária {#7-10-validation-script}

**ADICIONADO APÓS INCIDENT 17/11/2025**

Script para executar DIARIAMENTE via cron para detectar problemas de permissões antes que afetem usuários.

#### Script SQL Completo

```sql
-- ============================================================================
-- VALIDAÇÃO DIÁRIA DE PERMISSÕES - ODOO 15
-- Criado: 17/11/2025 após incident crítico
-- Executar: DIARIAMENTE via cron
-- ============================================================================

\set QUIET on
\set ON_ERROR_STOP on

-- ============================================================================
-- CHECK 1: Usuários ativos SEM grupo Internal User (CRÍTICO!)
-- ============================================================================
\echo '============================================================================'
\echo 'CHECK 1: Validando grupo Internal User...'
\echo '============================================================================'

WITH usuarios_sem_internal AS (
    SELECT
        u.id,
        u.login,
        u.active
    FROM res_users u
    WHERE u.active = true
      AND u.share = false  -- Usuários internos (não Portal/Public)
      AND u.id != 1  -- Excluir OdooBot
      AND NOT EXISTS (
          SELECT 1 FROM res_groups_users_rel
          WHERE uid = u.id AND gid = 1
      )
)
SELECT
    CASE
        WHEN COUNT(*) = 0 THEN '✅ OK: Todos os usuários têm grupo Internal User'
        ELSE '🚨 ALERTA CRÍTICO: ' || COUNT(*) || ' usuário(s) SEM grupo Internal User!'
    END as resultado,
    COALESCE(string_agg(login, ', '), 'Nenhum') as usuarios_afetados
FROM usuarios_sem_internal;

-- ============================================================================
-- CHECK 2: Usuários com número excessivo de grupos (>40)
-- ============================================================================
\echo ''
\echo '============================================================================'
\echo 'CHECK 2: Validando sobrecarga de grupos...'
\echo '============================================================================'

WITH usuarios_muitos_grupos AS (
    SELECT
        u.login,
        COUNT(*) as total_grupos
    FROM res_users u
    JOIN res_groups_users_rel rel ON u.id = rel.uid
    WHERE u.active = true
    GROUP BY u.login
    HAVING COUNT(*) > 40
)
SELECT
    CASE
        WHEN COUNT(*) = 0 THEN '✅ OK: Nenhum usuário com excesso de grupos'
        ELSE '⚠️ ATENÇÃO: ' || COUNT(*) || ' usuário(s) com mais de 40 grupos'
    END as resultado,
    COALESCE(string_agg(login || ' (' || total_grupos || ')', ', '), 'Nenhum') as usuarios
FROM usuarios_muitos_grupos;

-- ============================================================================
-- CHECK 3: Access rights duplicados
-- ============================================================================
\echo ''
\echo '============================================================================'
\echo 'CHECK 3: Validando access rights duplicados...'
\echo '============================================================================'

WITH duplicatas AS (
    SELECT
        model_id,
        group_id,
        COUNT(*) as total
    FROM ir_model_access
    WHERE active = true
    GROUP BY model_id, group_id
    HAVING COUNT(*) > 1
)
SELECT
    CASE
        WHEN COUNT(*) = 0 THEN '✅ OK: Nenhum access right duplicado'
        ELSE '⚠️ ATENÇÃO: ' || COUNT(*) || ' modelo(s) com access rights duplicados'
    END as resultado,
    COALESCE(COUNT(*)::TEXT, '0') as total_duplicatas
FROM duplicatas;

-- ============================================================================
-- CHECK 4: Access rights inúteis (todas permissões = FALSE)
-- ============================================================================
\echo ''
\echo '============================================================================'
\echo 'CHECK 4: Validando access rights inúteis...'
\echo '============================================================================'

WITH inuteis AS (
    SELECT id, name
    FROM ir_model_access
    WHERE active = true
      AND perm_read = false
      AND perm_write = false
      AND perm_create = false
      AND perm_unlink = false
)
SELECT
    CASE
        WHEN COUNT(*) = 0 THEN '✅ OK: Nenhum access right inútil'
        ELSE '⚠️ ATENÇÃO: ' || COUNT(*) || ' access right(s) com todas permissões = FALSE'
    END as resultado,
    COALESCE(COUNT(*)::TEXT, '0') as total_inuteis
FROM inuteis;

-- ============================================================================
-- CHECK 5: Usuários inativos com grupos (segurança)
-- ============================================================================
\echo ''
\echo '============================================================================'
\echo 'CHECK 5: Validando grupos de usuários inativos...'
\echo '============================================================================'

WITH grupos_inativos AS (
    SELECT COUNT(*) as total
    FROM res_groups_users_rel rel
    JOIN res_users u ON rel.uid = u.id
    WHERE u.active = false
)
SELECT
    CASE
        WHEN total = 0 THEN '✅ OK: Nenhum usuário inativo com grupos'
        ELSE '⚠️ ATENÇÃO: ' || total || ' grupo(s) atribuído(s) a usuários inativos'
    END as resultado,
    total
FROM grupos_inativos;

-- ============================================================================
-- CHECK 6: Grupos órfãos (sem usuários)
-- ============================================================================
\echo ''
\echo '============================================================================'
\echo 'CHECK 6: Validando grupos órfãos...'
\echo '============================================================================'

WITH grupos_orfaos AS (
    SELECT
        g.id,
        g.name
    FROM res_groups g
    WHERE NOT EXISTS (
        SELECT 1 FROM res_groups_users_rel WHERE gid = g.id
    )
    AND g.share = false  -- Excluir grupos de Portal/Public
    AND g.id NOT IN (1, 9, 10, 3)  -- Excluir grupos sistema
)
SELECT
    CASE
        WHEN COUNT(*) = 0 THEN '✅ OK: Nenhum grupo órfão'
        ELSE '⚠️ INFO: ' || COUNT(*) || ' grupo(s) sem usuários (pode ser normal)'
    END as resultado,
    COALESCE(COUNT(*)::TEXT, '0') as total_orfaos
FROM grupos_orfaos;

-- ============================================================================
-- CHECK 7: Tabela protected_groups existe?
-- ============================================================================
\echo ''
\echo '============================================================================'
\echo 'CHECK 7: Validando infraestrutura de proteção...'
\echo '============================================================================'

SELECT
    CASE
        WHEN EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'protected_groups'
        ) THEN '✅ OK: Tabela protected_groups existe'
        ELSE '🚨 ALERTA: Tabela protected_groups NÃO EXISTE! Criar imediatamente.'
    END as resultado;

-- ============================================================================
-- SUMÁRIO FINAL
-- ============================================================================
\echo ''
\echo '============================================================================'
\echo 'SUMÁRIO DA VALIDAÇÃO'
\echo '============================================================================'

SELECT
    NOW() as data_validacao,
    (SELECT COUNT(*) FROM res_users WHERE active = true) as total_usuarios_ativos,
    (SELECT COUNT(*) FROM res_groups WHERE share = false) as total_grupos,
    (SELECT COUNT(*) FROM ir_model_access WHERE active = true) as total_access_rights,
    (SELECT COUNT(*) FROM ir_rule WHERE active = true) as total_record_rules;

\echo ''
\echo 'Validação concluída!'
\echo 'Se houver alertas críticos (🚨), execute correções IMEDIATAMENTE.'
\echo '============================================================================'
```

#### Configurar Cron (Linux)

```bash
# Editar crontab
sudo crontab -e

# Adicionar linha (executar todos os dias às 6h)
0 6 * * * sudo -u postgres psql -d realcred -f /path/to/validacao_diaria.sql >> /var/log/odoo/permissoes_validation.log 2>&1
```

#### Alertas Automáticos

```bash
#!/bin/bash
# Script: /usr/local/bin/validate_odoo_permissions.sh

LOG_FILE="/var/log/odoo/permissoes_validation.log"
ALERT_EMAIL="ti@semprereal.com"

# Executar validação
sudo -u postgres psql -d realcred -f /path/to/validacao_diaria.sql > "$LOG_FILE" 2>&1

# Verificar se há alertas críticos
if grep -q "🚨 ALERTA CRÍTICO" "$LOG_FILE"; then
    # Enviar email
    mail -s "ODOO: ALERTA CRÍTICO DE PERMISSÕES!" "$ALERT_EMAIL" < "$LOG_FILE"

    # Log adicional
    echo "[$(date)] ALERTA CRÍTICO enviado para $ALERT_EMAIL" >> /var/log/odoo/alerts.log
fi

# Verificar se há atenções
if grep -q "⚠️ ATENÇÃO" "$LOG_FILE"; then
    echo "[$(date)] Atenções detectadas - revisar log" >> /var/log/odoo/alerts.log
fi
```

---

## 8. TROUBLESHOOTING {#8-troubleshooting}

### 8.1 Erro: "Você não tem permissão para acessar este registro"

**Diagnóstico:**

```sql
-- PASSO 1: Verificar access rights
SELECT
    a.name,
    g.name as grupo,
    a.perm_read,
    a.perm_write,
    a.perm_create,
    a.perm_unlink
FROM ir_model_access a
JOIN ir_model m ON a.model_id = m.id
LEFT JOIN res_groups g ON a.group_id = g.id
LEFT JOIN res_groups_users_rel rel ON g.id = rel.gid
WHERE m.model = '<MODELO>'
  AND (rel.uid = <USER_ID> OR a.group_id IS NULL)
  AND a.active = true;

-- PASSO 2: Verificar record rules
SELECT
    r.name,
    r.domain_force,
    r.global,
    string_agg(g.name, ', ') as grupos
FROM ir_rule r
JOIN ir_model m ON r.model_id = m.id
LEFT JOIN rule_group_rel rel ON r.id = rel.rule_group_id
LEFT JOIN res_groups g ON rel.group_id = g.id
WHERE m.model = '<MODELO>'
  AND r.active = true
GROUP BY r.id, r.name, r.domain_force, r.global;

-- PASSO 3: Verificar grupos do usuário
SELECT g.id, g.name
FROM res_groups g
JOIN res_groups_users_rel rel ON g.id = rel.gid
WHERE rel.uid = <USER_ID>
ORDER BY g.name;
```

**Soluções:**

1. **Falta access right:** Adicionar grupo apropriado ao usuário
2. **Record rule bloqueando:** Ajustar domínio ou adicionar grupo com regra menos restritiva
3. **Regra global bloqueando:** Revisar se usuário está na empresa certa

### 8.2 Erro: "Você não tem permissão para criar registros"

**Diagnóstico específico para CREATE:**

```sql
-- Verificar perm_create em access rights
SELECT
    a.name,
    a.perm_create,
    g.name as grupo
FROM ir_model_access a
JOIN ir_model m ON a.model_id = m.id
LEFT JOIN res_groups g ON a.group_id = g.id
LEFT JOIN res_groups_users_rel rel ON g.id = rel.gid
WHERE m.model = '<MODELO>'
  AND (rel.uid = <USER_ID> OR a.group_id IS NULL)
  AND a.active = true;

-- Verificar record rules com perm_create = true
SELECT
    r.name,
    r.domain_force,
    r.perm_create,
    r.global
FROM ir_rule r
JOIN ir_model m ON r.model_id = m.id
WHERE m.model = '<MODELO>'
  AND r.perm_create = true
  AND r.active = true;
```

**Problema comum:** Record rule com domínio que bloqueia em CREATE

```python
# ❌ PROBLEMA: Regra exige campo que é NULL durante criação
domain = ['&', ('user_id', '=', user.id), ('stage_edit', '=', True)]
# Durante CREATE, stage_edit pode ser NULL

# ✅ SOLUÇÃO: Tornar regra mais permissiva
domain = ['|', '|', ('user_id', '=', user.id), ('user_id', '=', False), ('stage_edit', '=', True)]
```

### 8.3 Usuário Vê Registros que Não Deveria Ver

**Diagnóstico:**

```sql
-- Verificar se há regra global faltando
SELECT
    r.name,
    r.domain_force,
    r.global
FROM ir_rule r
JOIN ir_model m ON r.model_id = m.id
WHERE m.model = '<MODELO>'
  AND r.active = true
ORDER BY r.global DESC;

-- Se não há regra global de multi-company, criar:
INSERT INTO ir_rule (name, model_id, domain_force, global, perm_read, perm_write, perm_create, perm_unlink)
SELECT
    'Multi-Company Rule',
    m.id,
    '[''|'', (''company_id'', ''='', False), (''company_id'', ''in'', company_ids)]',
    true,
    true, true, true, true
FROM ir_model m
WHERE m.model = '<MODELO>';
```

### 8.4 Performance Lenta em Listagens

**Causa comum:** Muitas record rules complexas

**Diagnóstico:**

```sql
-- Ver quantas regras se aplicam ao modelo
SELECT
    m.model,
    COUNT(*) as total_regras,
    SUM(CASE WHEN r.global THEN 1 ELSE 0 END) as regras_globais,
    SUM(CASE WHEN NOT r.global THEN 1 ELSE 0 END) as regras_grupo
FROM ir_rule r
JOIN ir_model m ON r.model_id = m.id
WHERE m.model = '<MODELO>'
  AND r.active = true
GROUP BY m.model;

-- Ver complexidade dos domínios
SELECT
    r.name,
    length(r.domain_force) as tamanho_dominio,
    r.domain_force
FROM ir_rule r
JOIN ir_model m ON r.model_id = m.id
WHERE m.model = '<MODELO>'
  AND r.active = true
ORDER BY tamanho_dominio DESC;
```

**Solução:**

1. Consolidar regras similares
2. Simplificar domínios complexos
3. Adicionar índices no banco de dados em campos usados em domínios

```sql
-- Exemplo: Criar índice para melhorar performance
CREATE INDEX idx_crm_lead_user_id ON crm_lead(user_id);
CREATE INDEX idx_crm_lead_team_id ON crm_lead(team_id);
CREATE INDEX idx_crm_lead_stage_edit ON crm_lead(stage_edit);
```

### 8.5 Usuário com Muitos Grupos

**Diagnóstico:**

```sql
-- Listar usuários com mais de 30 grupos
SELECT
    u.login,
    COUNT(*) as total_grupos,
    array_agg(g.name ORDER BY g.name) as grupos
FROM res_users u
JOIN res_groups_users_rel rel ON u.id = rel.uid
JOIN res_groups g ON rel.gid = g.id
WHERE u.active = true
GROUP BY u.login
HAVING COUNT(*) > 30
ORDER BY total_grupos DESC;
```

**Solução:**

1. Revisar grupos necessários
2. Remover grupos redundantes (implied já dá acesso)
3. Consolidar em grupo único com implied_ids

```sql
-- Remover grupo redundante
DELETE FROM res_groups_users_rel
WHERE uid = <USER_ID>
  AND gid = <GRUPO_REDUNDANTE>;
```

### 8.6 Debugging Avançado: Log de Acesso

**Habilitar log de acesso no Odoo:**

```python
# No arquivo de configuração odoo.conf
[options]
log_level = debug
log_handler = odoo.models.unlink:DEBUG,odoo.models.create:DEBUG
```

**Query para ver últimas operações:**

```sql
-- Requer módulo de auditoria instalado
SELECT
    l.create_date,
    l.user_id,
    u.login,
    l.model,
    l.method,
    l.res_id
FROM auditlog_log l
JOIN res_users u ON l.user_id = u.id
WHERE l.model = '<MODELO>'
ORDER BY l.create_date DESC
LIMIT 100;
```

---

### 8.7 🚨 Incident Report: Internal User Removido {#8-7-incident-internal-user}

**INCIDENT CRÍTICO - 17/11/2025**

#### Sumário do Incident

**Data:** 17/11/2025
**Descoberta:** 01:50 UTC
**Resolução:** 02:40 UTC
**Duração:** ~50 minutos (diagnóstico + correção)
**Downtime Total:** ~2h 10min (desde execução do script até resolução)
**Severidade:** 🔴 CRÍTICA
**Usuários Afetados:** 33 (100% dos usuários ativos)

#### O Que Aconteceu

Durante a Fase 3 do projeto de reorganização de permissões, foi executado um script SQL para remover grupos "redundantes" baseado na lógica de implied groups.

**Script Problemático:**

```sql
-- ❌ SCRIPT INCORRETO (CAUSOU INCIDENT)
DELETE FROM res_groups_users_rel
WHERE (uid, gid) IN (
    SELECT DISTINCT rel.uid, rel.gid
    FROM res_groups_users_rel rel
    WHERE EXISTS (
        SELECT 1
        FROM res_groups_implied_rel gi
        JOIN res_groups_users_rel rel2 ON rel2.uid = rel.uid AND rel2.gid = gi.gid
        WHERE gi.hid = rel.gid  -- ← ERRO FATAL
    )
);
```

**Premissa Incorreta:** "Se usuário tem grupo A que implica grupo B, então B é redundante e pode ser removido."

**Resultado:**
- ✅ Removeu 1.014 grupos "redundantes"
- ❌ Incluindo grupo 1 (Internal User) de 33 usuários
- ❌ Sistema completamente inoperante

#### Erros Reportados pelos Usuários

**1. Admin - Erro ao acessar DMS:**
```
AccessError: Você não tem permissão para acessar registros 'Diretório' (dms.directory).
Esta operação é permitida para os seguintes grupos:
- Documents/User
- User types/Internal User
- User types/Portal
- User types/Public
```

**2. Vendedores - Erro ao acessar Chat:**
```
AccessError: Você não tem permissão para acessar registros 'Ouvintes de um Canal' (mail.channel.partner).
Esta operação é permitida para os seguintes grupos:
- User types/Internal User
- User types/Portal
- User types/Public
```

**3. Vendedores - Erro ao acessar CRM:**
```
AccessError: Você não tem permissão para acessar registros 'Lead/Oportunidade' (crm.lead).
Esta operação é permitida para os seguintes grupos:
- Accounting/Accountant
- Sales/Administrator
- Sales/Operacional
- Sales/User: Own Documents Only
```

#### Diagnóstico

**Query de Investigação:**

```sql
-- Verificar se usuários têm grupo Internal User
SELECT COUNT(*) FROM res_groups_users_rel WHERE gid = 1;
-- Resultado: 0 ❌ CRÍTICO!

-- Verificar backup da Fase 3
SELECT COUNT(*) FROM res_groups_users_rel_backup_fase3_20251117 WHERE gid = 1;
-- Resultado: 33 ✅ (backup tem os registros!)
```

**Causa Raiz Identificada:**

Implied groups são verificados em **RUNTIME** via JOIN, **NÃO criam registros físicos** em `res_groups_users_rel`.

- Grupo 13 (Own Documents) implica grupo 1 (Internal User)
- Quando Odoo verifica permissão que requer grupo 1:
  1. Verifica se usuário tem grupo 1 DIRETAMENTE → NÃO
  2. Verifica se usuário tem grupo que implica 1 → SIM (grupo 13)
  3. Permite acesso

**MAS:** Alguns access rights verificam grupo 1 **DIRETAMENTE** sem considerar implied:

```sql
SELECT * FROM ir_model_access
WHERE model_id = (SELECT id FROM ir_model WHERE model = 'dms.directory')
  AND group_id = 1;
-- Estes access rights EXIGEM grupo 1 físico!
```

#### Correção Aplicada

**1. Restauração do Grupo Internal User:**

```sql
BEGIN;

-- Backup antes da correção
CREATE TABLE IF NOT EXISTS res_groups_users_rel_before_fix_internal_user AS
SELECT * FROM res_groups_users_rel;

-- Restaurar de backup
INSERT INTO res_groups_users_rel (uid, gid)
SELECT DISTINCT uid, 1
FROM res_groups_users_rel_backup_fase3_20251117
WHERE gid = 1
  AND uid IN (SELECT id FROM res_users WHERE active = true)
ON CONFLICT DO NOTHING;

SELECT COUNT(*) FROM res_groups_users_rel WHERE gid = 1;
-- Resultado: 33 ✅ RESTAURADO!

COMMIT;
```

**2. Adicionar Grupo Documents para Admin:**

```sql
INSERT INTO res_groups_users_rel (uid, gid)
VALUES (2, 88)  -- Admin, Documents/User
ON CONFLICT DO NOTHING;
```

**3. Remover Duplicata de Access Right:**

```sql
-- Havia 2 access rights para grupo 13 em crm.lead (IDs 290 e 1750)
DELETE FROM ir_model_access WHERE id = 1750;
```

**4. Reiniciar Odoo:**

```bash
sudo pkill -9 -f odoo-bin
sleep 5
sudo -u odoo /odoo/odoo-server/odoo-bin -c /etc/odoo-server.conf &
```

#### Lições Aprendidas

**❌ O QUE NÃO FAZER:**

1. **Assumir que implied groups criam registros físicos**
   - Implied é verificado em runtime, não cria registros

2. **Remover grupos base sem entender dependências**
   - Grupos 1, 9, 10, 3 são ESSENCIAIS

3. **Executar DELETE em massa sem validação**
   - Sempre validar impacto ANTES de executar

4. **Não testar em ambiente de dev**
   - Scripts críticos devem ser testados antes de produção

**✅ O QUE FAZER:**

1. **Criar lista de grupos protegidos**
   - Tabela `protected_groups` com grupos que NUNCA devem ser removidos

2. **Validar impacto antes de DELETE**
   - Query de preview mostrando exatamente o que será removido

3. **Usar BEGIN/ROLLBACK**
   - Permitir reversão imediata se algo der errado

4. **Manter backups recentes**
   - Backup salvou o dia! Restauração em minutos.

5. **Monitoramento proativo**
   - Script de validação diária (ver seção 7.10)

#### Script Corrigido

```sql
-- ✅ VERSÃO CORRETA (COM PROTEÇÃO)
BEGIN;

-- 1. Grupos protegidos (NUNCA remover)
CREATE TEMP TABLE protected_groups_temp AS
SELECT UNNEST(ARRAY[1, 9, 10, 3]) as gid;

-- 2. Identificar redundantes (EXCLUINDO protegidos)
CREATE TEMP TABLE redundant_groups AS
SELECT DISTINCT rel.uid, rel.gid
FROM res_groups_users_rel rel
WHERE rel.gid NOT IN (SELECT gid FROM protected_groups_temp)  -- ← PROTEÇÃO!
  AND EXISTS (
      SELECT 1
      FROM res_groups_implied_rel gi
      JOIN res_groups_users_rel rel2 ON rel2.uid = rel.uid AND rel2.gid = gi.gid
      WHERE gi.hid = rel.gid
        AND gi.gid NOT IN (SELECT gid FROM protected_groups_temp)  -- ← PROTEÇÃO!
  );

-- 3. Validar impacto
SELECT 'Serão removidos ' || COUNT(*) || ' grupos' FROM redundant_groups;

-- 4. Preview
SELECT u.login, g.name
FROM redundant_groups rg
JOIN res_users u ON rg.uid = u.id
JOIN res_groups g ON rg.gid = g.id
LIMIT 10;

-- 5. SE VALIDADO, descomentar:
-- DELETE FROM res_groups_users_rel
-- WHERE (uid, gid) IN (SELECT uid, gid FROM redundant_groups);

ROLLBACK;  -- Mudar para COMMIT após validação
```

#### Prevenção Futura

**Implementar IMEDIATAMENTE:**

1. Criar tabela `protected_groups` (ver seção 7.9)
2. Configurar script de validação diária (ver seção 7.10)
3. Atualizar todos os scripts existentes com proteções
4. Documentar procedimento de rollback

**Métricas de Sucesso:**

- Zero incidents relacionados a grupos base nos próximos 12 meses
- 100% dos scripts de permissão usando `protected_groups`
- Validação diária detectando anomalias em < 24h

#### Documentos Relacionados

- `INCIDENT_REPORT_INTERNAL_USER_20251117.md` - Relatório completo (13.000+ linhas)
- Seção 5.6 - Comportamento REAL de Implied Groups
- Seção 7.9 - Grupos Protegidos
- Seção 7.10 - Script de Validação Diária

---

### 8.8 🚨 Incident Report: Admin User Locked {#8-8-incident-admin-locked}

**INCIDENT CRÍTICO - 16/11/2025**

#### Sumário do Incident

**Data:** 16/11/2025
**Descoberta:** ~20:00 UTC
**Resolução:** ~20:20 UTC
**Duração:** ~20 minutos (diagnóstico + correção + restart)
**Severidade:** 🔴 CRÍTICA
**Usuários Afetados:** 1 (admin - usuário crítico)
**Impacto:** Sistema administrativo completamente inacessível

#### O Que Aconteceu

O usuário admin (uid=2) ficou completamente travado/locked, impossibilitando acesso à interface administrativa e causando erros JavaScript críticos.

**Sintomas Reportados:**

```javascript
// Console do navegador (F12)
TypeError: Cannot read properties of undefined (reading 'context')
    at ActionContainer.render (web.assets_backend.min.js:10604:389)

Tour Manager is ready
Some modules could not be started
Missing dependencies
```

**Interface:** Admin não conseguia acessar nenhum módulo, interface administrativa não carregava.

#### Diagnóstico

**Query de Investigação:**

```sql
-- 1. Verificar estado atual do admin
SELECT id, login, active, share, COUNT(rel.gid) as total_grupos
FROM res_users u
LEFT JOIN res_groups_users_rel rel ON u.id = rel.uid
WHERE u.id = 2
GROUP BY u.id, u.login, u.active, u.share;

-- Resultado:
--  id | login | active | share | total_grupos
-- ----+-------+--------+-------+--------------
--   2 | admin | t      | f     |           34

-- 2. Verificar grupos CRÍTICOS
SELECT
    g.id,
    g.name,
    CASE
        WHEN EXISTS(SELECT 1 FROM res_groups_users_rel WHERE uid = 2 AND gid = g.id)
        THEN '✅ TEM'
        ELSE '❌ FALTA - CRÍTICO!'
    END as status
FROM res_groups g
WHERE g.id IN (1, 2, 3)
ORDER BY g.id;

-- Resultado:
--  id |     name      |       status
-- ----+---------------+---------------------
--   1 | Internal User | ✅ TEM
--   2 | Access Rights | ❌ FALTA - CRÍTICO!
--   3 | Settings      | ✅ TEM
```

**PROBLEMA IDENTIFICADO:** Admin estava sem o grupo "Access Rights" (ID: 2)!

#### Causa Raiz

**DESCOBERTA CRÍTICA:** Confusão entre Admin User (uid=2) e Superuser (uid=1)

```
┌────────────────────────────────────────────────┐
│ SUPERUSER (OdooBot - UID=1)                    │
│ ✅ BYPASSA todas as regras de segurança       │
│ ✅ NÃO precisa de grupos                      │
│ ✅ Usado internamente pelo Odoo               │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ ADMIN USER (admin - UID=2)                     │
│ ❌ NÃO BYPASSA regras de segurança            │
│ ⚠️  PRECISA de grupos explícitos              │
│ ⚠️  Está sujeito a Access Rights              │
│ ⚠️  Está sujeito a Record Rules               │
└────────────────────────────────────────────────┘
```

**Segundo documentação oficial Odoo:**
> "The admin account is (by default) a member of **all application security groups**"

**Admin estava FALTANDO:**
- ❌ Access Rights (ID: 2) - CRÍTICO para interface administrativa
- ❌ Website Restricted Editor (ID: 126)
- ❌ Website Editor and Designer (ID: 127)
- ❌ Possivelmente outros grupos Administrator

#### Solução Aplicada

**1. Backup Preventivo:**

```bash
ssh odoo-rc "sudo -u postgres pg_dump realcred -F c -f /tmp/backup_antes_correcao_admin_20251116_201755.dump"
# Resultado: 557 MB backup criado ✅
```

**2. Script SQL de Correção:**

```sql
-- Script: CORRECAO_ADMIN_LOCKED_20251116.sql

BEGIN;

-- Criar tabela temporária com grupos a adicionar
CREATE TEMP TABLE admin_groups_to_add AS
SELECT DISTINCT g.id as gid
FROM res_groups g
LEFT JOIN ir_module_category c ON g.category_id = c.id
WHERE NOT EXISTS(SELECT 1 FROM res_groups_users_rel WHERE uid = 2 AND gid = g.id)
  AND (
    -- Grupos CRÍTICOS base (NUNCA devem faltar)
    g.id IN (1, 2, 3)
    OR
    -- Grupos Administrator de TODOS os módulos instalados
    g.name ILIKE '%administrator%'
    OR
    -- Grupos Manager de módulos principais
    (g.name ILIKE '%manager%' AND c.name IN (
        'Sales', 'Accounting', 'Inventory', 'Purchase',
        'Human Resources', 'Project', 'Website', 'CRM'
    ))
    OR
    -- Grupos essenciais adicionais
    g.id IN (88, 126, 127)  -- Documents/User, Website groups
  );

-- Adicionar grupos ao admin
INSERT INTO res_groups_users_rel (uid, gid)
SELECT 2, gid
FROM admin_groups_to_add
ON CONFLICT (uid, gid) DO NOTHING;

-- Validar
SELECT COUNT(*) as total_grupos FROM res_groups_users_rel WHERE uid = 2;
-- Resultado esperado: 37+ grupos

COMMIT;
```

**3. Resultado da Execução:**

```
Grupos adicionados ao admin (uid=2):
 gid |        name         |   categoria
-----+---------------------+----------------
   2 | Access Rights       | Administration  ← CRÍTICO
 127 | Editor and Designer | Website
 126 | Restricted Editor   | Website

Total de grupos ANTES:  34
Total de grupos DEPOIS: 37 ✅
```

**4. Reinício do Odoo:**

```bash
ssh odoo-rc "sudo systemctl restart odoo-server"
# Status: Active (running) ✅
```

**5. Validação Pós-Correção:**

```sql
-- Verificar grupos críticos
SELECT g.id, g.name,
    CASE WHEN EXISTS(SELECT 1 FROM res_groups_users_rel WHERE uid = 2 AND gid = g.id)
    THEN '✅ OK' ELSE '❌ PROBLEMA' END as status
FROM res_groups g
WHERE g.id IN (1, 2, 3, 88);

-- Resultado:
--  id |     name      | status
-- ----+---------------+--------
--   1 | Internal User | ✅ OK
--   2 | Access Rights | ✅ OK
--   3 | Settings      | ✅ OK
--  88 | User          | ✅ OK
```

#### Lições Aprendidas

**1. Admin ≠ Superuser (CRÍTICO)**

Esta é a lição mais importante deste incident:

- **SUPERUSER (uid=1)** bypassa TODAS as regras → Não precisa de grupos
- **ADMIN (uid=2)** é usuário NORMAL → PRECISA de grupos explícitos

**2. Grupos Essenciais do Admin**

Admin DEVE ter SEMPRE:

```sql
-- GRUPOS BASE (NUNCA podem faltar)
1  -- Internal User (base.group_user)
2  -- Access Rights (base.group_erp_manager)  ← CAUSOU O INCIDENT!
3  -- Settings (base.group_system)

-- GRUPOS ADICIONAIS (Todos Administrator de módulos instalados)
15  -- Sales / Administrator
21  -- Employees / Administrator
72  -- Purchase / Administrator
109 -- Inventory / Administrator
-- ... E TODOS OS OUTROS!
```

**3. Sintomas de Admin Locked**

Se admin está locked, você verá:

- ❌ JavaScript: `TypeError: Cannot read properties of undefined (reading 'context')`
- ❌ "Some modules could not be started"
- ❌ Interface administrativa não carrega
- ❌ Módulos aparecem mas não funcionam

**Solução:** Adicionar grupos faltantes + Restart

**4. Query de Validação Diária**

```sql
-- Verificar DIARIAMENTE que admin tem grupos críticos
SELECT
    'Admin Critical Groups Check' as validacao,
    CASE
        WHEN (SELECT COUNT(*) FROM res_groups_users_rel WHERE uid = 2 AND gid IN (1,2,3)) = 3
        THEN '✅ OK - Admin tem todos os grupos base'
        ELSE '❌ PROBLEMA - Admin sem grupos críticos!'
    END as status;
```

#### Referências Consultadas

**Documentação Oficial Odoo:**

1. **Odoo Tricks - Superuser vs Admin**
   - URL: https://odootricks.tips/about/building-blocks/security/superuser-admin/
   - Citação: "The admin account is (by default) a member of all application security groups"

2. **GitHub Odoo 15.0 - base_groups.xml**
   - URL: https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/security/base_groups.xml
   - Define grupos: group_erp_manager (Access Rights), group_system (Settings)

3. **GitHub Odoo 15.0 - res_users_data.xml**
   - URL: https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/res_users_data.xml
   - Admin user definition: `groups_id = Command.set([])`
   - Nota: Grupos são adicionados na inicialização do banco

4. **Documentação Oficial Users (Odoo 15)**
   - URL: https://www.odoo.com/documentation/15.0/applications/general/users.html
   - Recomendação: Usar admin apenas em circunstâncias excepcionais

#### Prevenção Futura

**Script de Validação (Executar SEMANALMENTE):**

```sql
-- Verificar configuração do admin
DO $$
DECLARE
    admin_groups_count INTEGER;
    missing_critical INTEGER;
BEGIN
    -- Contar grupos do admin
    SELECT COUNT(*) INTO admin_groups_count
    FROM res_groups_users_rel WHERE uid = 2;

    -- Verificar grupos críticos
    SELECT 3 - COUNT(*) INTO missing_critical
    FROM res_groups_users_rel
    WHERE uid = 2 AND gid IN (1, 2, 3);

    -- Alertar se problemas
    IF admin_groups_count < 30 THEN
        RAISE NOTICE '⚠️ ALERTA: Admin tem apenas % grupos (esperado: 35+)', admin_groups_count;
    END IF;

    IF missing_critical > 0 THEN
        RAISE EXCEPTION '🚨 CRÍTICO: Admin está faltando % grupos base!', missing_critical;
    END IF;

    RAISE NOTICE '✅ Admin configurado corretamente (% grupos)', admin_groups_count;
END $$;
```

**Checklist Admin:**

- [ ] Admin tem Internal User (ID: 1)
- [ ] Admin tem Access Rights (ID: 2)
- [ ] Admin tem Settings (ID: 3)
- [ ] Admin tem 35+ grupos total
- [ ] Admin consegue acessar todos os módulos
- [ ] Não há erros JavaScript no console

#### Documentos Relacionados

- `SOLUCAO_ADMIN_LOCKED_EXECUTAR_AGORA.md` - Documentação completa da solução
- `CORRECAO_ADMIN_LOCKED_20251116.sql` - Script SQL executado
- Seção 0.4 - Admin vs Superuser - DIFERENÇA CRÍTICA
- Seção 0.5 - Referências Oficiais Consultadas

#### Métricas do Incident

| Métrica | Valor |
|---------|-------|
| **Tempo de Detecção** | Imediato (usuário reportou) |
| **Tempo de Diagnóstico** | ~10 minutos |
| **Tempo de Correção** | ~5 minutos |
| **Tempo de Validação** | ~5 minutos |
| **Downtime Total** | 0 (outros usuários não afetados) |
| **Grupos Adicionados** | 3 |
| **Backup Criado** | 557 MB ✅ |
| **Rollback Necessário** | Não |
| **Sucesso** | ✅ 100% |

---

## 9. SQL QUERIES DE REFERÊNCIA {#9-sql-reference}

### 9.1 Gestão de Usuários e Grupos

#### Adicionar Usuário a Grupo

```sql
-- Adicionar usuário ao grupo (com verificação de duplicata)
INSERT INTO res_groups_users_rel (gid, uid)
SELECT <GROUP_ID>, <USER_ID>
WHERE NOT EXISTS (
    SELECT 1 FROM res_groups_users_rel
    WHERE gid = <GROUP_ID> AND uid = <USER_ID>
);

-- Adicionar múltiplos usuários a um grupo
INSERT INTO res_groups_users_rel (gid, uid)
SELECT <GROUP_ID>, u.id
FROM res_users u
WHERE u.login IN ('user1@example.com', 'user2@example.com', 'user3@example.com')
ON CONFLICT DO NOTHING;
```

#### Remover Usuário de Grupo

```sql
-- Remover usuário de um grupo específico
DELETE FROM res_groups_users_rel
WHERE gid = <GROUP_ID>
  AND uid = <USER_ID>;

-- Remover usuário de todos os grupos de uma categoria
DELETE FROM res_groups_users_rel
WHERE uid = <USER_ID>
  AND gid IN (
      SELECT id FROM res_groups
      WHERE category_id = <CATEGORY_ID>
  );
```

#### Copiar Grupos de um Usuário para Outro

```sql
-- Copiar TODOS os grupos
INSERT INTO res_groups_users_rel (gid, uid)
SELECT gid, <USER_DESTINO>
FROM res_groups_users_rel
WHERE uid = <USER_ORIGEM>
ON CONFLICT DO NOTHING;

-- Copiar apenas grupos de uma categoria
INSERT INTO res_groups_users_rel (gid, uid)
SELECT rel.gid, <USER_DESTINO>
FROM res_groups_users_rel rel
JOIN res_groups g ON rel.gid = g.id
WHERE rel.uid = <USER_ORIGEM>
  AND g.category_id = <CATEGORY_ID>
ON CONFLICT DO NOTHING;
```

### 9.2 Gestão de Access Rights

#### Criar Access Right

```sql
-- Criar access right completo (CRUD)
INSERT INTO ir_model_access (name, model_id, group_id, perm_read, perm_write, perm_create, perm_unlink, active)
SELECT
    '<nome_regra>',
    m.id,
    <GROUP_ID>,  -- NULL para todos
    true,        -- read
    true,        -- write
    true,        -- create
    true,        -- delete
    true         -- active
FROM ir_model m
WHERE m.model = '<modelo>';

-- Criar access right apenas leitura
INSERT INTO ir_model_access (name, model_id, group_id, perm_read, perm_write, perm_create, perm_unlink, active)
SELECT
    '<nome_regra>',
    m.id,
    <GROUP_ID>,
    true,   -- read
    false,  -- write
    false,  -- create
    false,  -- delete
    true
FROM ir_model m
WHERE m.model = '<modelo>';
```

#### Modificar Access Right

```sql
-- Adicionar permissão de criação
UPDATE ir_model_access
SET perm_create = true
WHERE id = <ACCESS_ID>;

-- Remover permissão de exclusão
UPDATE ir_model_access
SET perm_unlink = false
WHERE model_id = (SELECT id FROM ir_model WHERE model = '<modelo>')
  AND group_id = <GROUP_ID>;
```

#### Desabilitar Access Right

```sql
-- Desabilitar (melhor que deletar)
UPDATE ir_model_access
SET active = false
WHERE id = <ACCESS_ID>;

-- Reabilitar
UPDATE ir_model_access
SET active = true
WHERE id = <ACCESS_ID>;
```

### 9.3 Gestão de Record Rules

#### Criar Record Rule

```sql
-- Regra de grupo (permissiva)
INSERT INTO ir_rule (name, model_id, domain_force, global, perm_read, perm_write, perm_create, perm_unlink, active)
SELECT
    '<nome_regra>',
    m.id,
    '[''|'', (''user_id'', ''='', user.id), (''user_id'', ''='', False)]',
    false,  -- NÃO global
    true, true, true, true,  -- Aplicar em todas operações
    true
FROM ir_model m
WHERE m.model = '<modelo>';

-- Associar regra ao grupo
INSERT INTO rule_group_rel (rule_group_id, group_id)
VALUES (
    (SELECT id FROM ir_rule WHERE name = '<nome_regra>'),
    <GROUP_ID>
);

-- Regra global (restritiva)
INSERT INTO ir_rule (name, model_id, domain_force, global, perm_read, perm_write, perm_create, perm_unlink, active)
SELECT
    'Multi-Company Rule',
    m.id,
    '[''|'', (''company_id'', ''='', False), (''company_id'', ''in'', company_ids)]',
    true,  -- GLOBAL
    true, true, true, true,
    true
FROM ir_model m
WHERE m.model = '<modelo>';
```

#### Modificar Domain de Rule

```sql
-- Atualizar domínio
UPDATE ir_rule
SET domain_force = '[''|'', ''|'', (''user_id'', ''='', user.id), (''user_id'', ''='', False), (''stage_edit'', ''='', True)]'
WHERE id = <RULE_ID>;

-- Desabilitar aplicação em CREATE
UPDATE ir_rule
SET perm_create = false
WHERE id = <RULE_ID>;
```

#### Adicionar/Remover Grupos de Rule

```sql
-- Adicionar grupo a rule
INSERT INTO rule_group_rel (rule_group_id, group_id)
VALUES (<RULE_ID>, <GROUP_ID>)
ON CONFLICT DO NOTHING;

-- Remover grupo de rule
DELETE FROM rule_group_rel
WHERE rule_group_id = <RULE_ID>
  AND group_id = <GROUP_ID>;
```

### 9.4 Queries de Auditoria

#### Relatório Completo de Permissões por Usuário

```sql
SELECT
    u.login as usuario,
    m.model as modelo,
    -- Access Rights
    bool_or(a.perm_read) as acl_read,
    bool_or(a.perm_write) as acl_write,
    bool_or(a.perm_create) as acl_create,
    bool_or(a.perm_unlink) as acl_delete,
    -- Record Rules
    COUNT(DISTINCT r.id) FILTER (WHERE r.global = false) as regras_grupo,
    COUNT(DISTINCT rg.id) FILTER (WHERE rg.global = true) as regras_globais,
    -- Grupos
    string_agg(DISTINCT g.name, ', ' ORDER BY g.name) as grupos
FROM res_users u
CROSS JOIN ir_model m
LEFT JOIN res_groups_users_rel ugrel ON u.id = ugrel.uid
LEFT JOIN res_groups g ON ugrel.gid = g.id
LEFT JOIN ir_model_access a ON (a.group_id = g.id OR a.group_id IS NULL) AND a.model_id = m.id AND a.active = true
LEFT JOIN rule_group_rel rgrel ON g.id = rgrel.group_id
LEFT JOIN ir_rule r ON rgrel.rule_group_id = r.id AND r.model_id = m.id AND r.active = true
LEFT JOIN ir_rule rg ON rg.model_id = m.id AND rg.global = true AND rg.active = true
WHERE u.login = '<usuario@example.com>'
  AND m.model IN ('crm.lead', 'res.partner', 'sale.order')  -- Modelos de interesse
GROUP BY u.login, m.model
ORDER BY m.model;
```

#### Usuários com Acesso a Modelo Específico

```sql
SELECT DISTINCT
    u.login,
    u.active,
    string_agg(DISTINCT g.name, ', ') as grupos_com_acesso
FROM res_users u
JOIN res_groups_users_rel ugrel ON u.id = ugrel.uid
JOIN ir_model_access a ON (a.group_id = ugrel.gid OR a.group_id IS NULL)
JOIN ir_model m ON a.model_id = m.id
LEFT JOIN res_groups g ON ugrel.gid = g.id
WHERE m.model = '<modelo>'
  AND a.active = true
  AND (a.perm_read = true OR a.perm_write = true OR a.perm_create = true OR a.perm_unlink = true)
GROUP BY u.login, u.active
ORDER BY u.active DESC, u.login;
```

#### Modelos Sem Access Rights

```sql
-- PERIGOSO: Modelos sem nenhum access right
SELECT
    m.model,
    m.name
FROM ir_model m
WHERE NOT EXISTS (
    SELECT 1 FROM ir_model_access a
    WHERE a.model_id = m.id AND a.active = true
)
AND m.transient = false  -- Excluir modelos temporários
ORDER BY m.model;
```

### 9.5 Queries de Limpeza

#### Remover Access Rights Duplicados

```sql
-- Identificar duplicatas
SELECT
    model_id,
    group_id,
    COUNT(*) as total
FROM ir_model_access
WHERE active = true
GROUP BY model_id, group_id
HAVING COUNT(*) > 1;

-- Remover duplicatas (manter apenas o mais recente)
DELETE FROM ir_model_access
WHERE id IN (
    SELECT id
    FROM (
        SELECT
            id,
            ROW_NUMBER() OVER (PARTITION BY model_id, group_id ORDER BY id DESC) as rn
        FROM ir_model_access
        WHERE active = true
    ) sub
    WHERE rn > 1
);
```

#### Remover Grupos de Usuários Inativos

```sql
-- Remover todos os grupos de usuários inativos
DELETE FROM res_groups_users_rel
WHERE uid IN (
    SELECT id FROM res_users WHERE active = false
);
```

#### Limpar Record Rules Órfãs

```sql
-- Rules sem grupos e não globais (inúteis)
DELETE FROM ir_rule
WHERE global = false
  AND NOT EXISTS (
      SELECT 1 FROM rule_group_rel WHERE rule_group_id = ir_rule.id
  );
```

---

## 10. CASOS DE USO COMUNS {#10-casos-uso}

### 10.1 Caso: Vendedor Vê Apenas Próprios Leads

**Requisito:** Vendedores devem ver apenas leads atribuídos a eles ou sem responsável.

**Implementação:**

```sql
BEGIN;

-- 1. Criar grupo "Sales / User: Own Documents Only" (se não existir)
INSERT INTO res_groups (name, category_id, comment)
SELECT
    'User: Own Documents Only',
    (SELECT id FROM ir_module_category WHERE name = 'Sales'),
    'Vendedores veem apenas próprios leads'
WHERE NOT EXISTS (SELECT 1 FROM res_groups WHERE name = 'User: Own Documents Only');

-- 2. Criar access right
INSERT INTO ir_model_access (name, model_id, group_id, perm_read, perm_write, perm_create, perm_unlink)
SELECT
    'crm.lead.user.own',
    m.id,
    (SELECT id FROM res_groups WHERE name = 'User: Own Documents Only'),
    true, true, true, false  -- Sem permissão de deletar
FROM ir_model m
WHERE m.model = 'crm.lead';

-- 3. Criar record rule
INSERT INTO ir_rule (name, model_id, domain_force, global, perm_read, perm_write, perm_create, perm_unlink)
SELECT
    'Personal Leads Only',
    m.id,
    '[''|'', (''user_id'', ''='', user.id), (''user_id'', ''='', False)]',
    false,
    true, true, true, true
FROM ir_model m
WHERE m.model = 'crm.lead';

-- 4. Associar rule ao grupo
INSERT INTO rule_group_rel (rule_group_id, group_id)
VALUES (
    (SELECT id FROM ir_rule WHERE name = 'Personal Leads Only'),
    (SELECT id FROM res_groups WHERE name = 'User: Own Documents Only')
);

COMMIT;
```

### 10.2 Caso: Gerente Vê Todos os Leads da Equipe

**Requisito:** Gerentes devem ver todos os leads de sua equipe.

**Implementação:**

```sql
BEGIN;

-- 1. Criar grupo "Sales / Manager" (se não existir)
INSERT INTO res_groups (name, category_id, comment)
SELECT
    'Manager',
    (SELECT id FROM ir_module_category WHERE name = 'Sales'),
    'Gerentes veem todos leads da equipe'
WHERE NOT EXISTS (SELECT 1 FROM res_groups WHERE name = 'Manager');

-- 2. Adicionar implied: Manager implica User
INSERT INTO res_groups_implied_rel (gid, hid)
VALUES (
    (SELECT id FROM res_groups WHERE name = 'Manager'),
    (SELECT id FROM res_groups WHERE name = 'User: Own Documents Only')
);

-- 3. Criar access right (mesmo do User, herdado por implied)

-- 4. Criar record rule
INSERT INTO ir_rule (name, model_id, domain_force, global, perm_read, perm_write, perm_create, perm_unlink)
SELECT
    'Team Leads',
    m.id,
    '[''|'', (''team_id'', ''='', user.team_id.id), (''team_id.user_id'', ''='', user.id)]',
    false,
    true, true, true, true
FROM ir_model m
WHERE m.model = 'crm.lead';

-- 5. Associar rule ao grupo Manager
INSERT INTO rule_group_rel (rule_group_id, group_id)
VALUES (
    (SELECT id FROM ir_rule WHERE name = 'Team Leads'),
    (SELECT id FROM res_groups WHERE name = 'Manager')
);

COMMIT;
```

### 10.3 Caso: Multi-Company (Isolamento de Dados)

**Requisito:** Usuários de empresa A não podem ver dados de empresa B.

**Implementação:**

```sql
-- Criar regra GLOBAL (aplica a TODOS)
INSERT INTO ir_rule (name, model_id, domain_force, global, perm_read, perm_write, perm_create, perm_unlink)
SELECT
    'crm.lead multi-company',
    m.id,
    '[''|'', (''company_id'', ''='', False), (''company_id'', ''in'', company_ids)]',
    true,  -- GLOBAL
    true, true, true, true
FROM ir_model m
WHERE m.model = 'crm.lead';

-- Aplicar para TODOS os modelos relevantes
DO $$
DECLARE
    modelo TEXT;
BEGIN
    FOR modelo IN
        SELECT model FROM ir_model
        WHERE model IN ('sale.order', 'purchase.order', 'account.move', 'crm.lead')
    LOOP
        INSERT INTO ir_rule (name, model_id, domain_force, global, perm_read, perm_write, perm_create, perm_unlink)
        SELECT
            modelo || ' multi-company',
            m.id,
            '[''|'', (''company_id'', ''='', False), (''company_id'', ''in'', company_ids)]',
            true,
            true, true, true, true
        FROM ir_model m
        WHERE m.model = modelo;
    END LOOP;
END $$;
```

### 10.4 Caso: Campo Sensível (Salário)

**Requisito:** Apenas RH e gerentes podem ver salário de funcionários.

**Implementação:**

**Opção 1: Field-level security (requer código Python)**

```python
# Em hr_employee.py
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    wage = fields.Monetary(
        'Wage',
        groups='hr.group_hr_manager,hr.group_hr_user'
    )
```

**Opção 2: Record rule (limitar acesso ao modelo inteiro)**

```sql
-- Criar grupo "HR / Manager"
-- Criar record rule: apenas HR pode ver todos funcionários
INSERT INTO ir_rule (name, model_id, domain_force, global, perm_read, perm_write, perm_create, perm_unlink)
SELECT
    'All Employees',
    m.id,
    '[(1, ''='', 1)]',  -- Ver todos
    false,
    true, true, true, true
FROM ir_model m
WHERE m.model = 'hr.employee';

-- Associar ao grupo HR / Manager
INSERT INTO rule_group_rel (rule_group_id, group_id)
VALUES (
    (SELECT id FROM ir_rule WHERE name = 'All Employees'),
    (SELECT id FROM res_groups WHERE name LIKE '%HR%Manager%')
);

-- Outros usuários veem apenas próprio registro
INSERT INTO ir_rule (name, model_id, domain_force, global, perm_read, perm_write, perm_create, perm_unlink)
SELECT
    'Own Employee Only',
    m.id,
    '[''|'', (''user_id'', ''='', user.id), (''id'', ''='', user.employee_id.id)]',
    false,
    true, false, false, false  -- Apenas leitura
FROM ir_model m
WHERE m.model = 'hr.employee';

-- Associar ao grupo base (Internal User)
INSERT INTO rule_group_rel (rule_group_id, group_id)
VALUES (
    (SELECT id FROM ir_rule WHERE name = 'Own Employee Only'),
    (SELECT id FROM res_groups WHERE name = 'Internal User')
);
```

### 10.5 Caso: Workflow com Estágios

**Requisito:**
- Vendedores: veem leads em estágios "Novo" e "Qualificado"
- Gerentes: veem todos os estágios
- Administradores: veem tudo

**Implementação:**

```sql
BEGIN;

-- 1. Vendedores: apenas estágios iniciais
INSERT INTO ir_rule (name, model_id, domain_force, global, perm_read, perm_write, perm_create, perm_unlink)
SELECT
    'Leads - Early Stages',
    m.id,
    '[''&'', (''user_id'', ''='', user.id), (''stage_id.name'', ''in'', [''Novo'', ''Qualificado''])]',
    false,
    true, true, true, false
FROM ir_model m
WHERE m.model = 'crm.lead';

INSERT INTO rule_group_rel (rule_group_id, group_id)
VALUES (
    (SELECT id FROM ir_rule WHERE name = 'Leads - Early Stages'),
    (SELECT id FROM res_groups WHERE name LIKE '%Sales%User%Own%')
);

-- 2. Gerentes: todos os estágios da equipe
INSERT INTO ir_rule (name, model_id, domain_force, global, perm_read, perm_write, perm_create, perm_unlink)
SELECT
    'Leads - All Stages Team',
    m.id,
    '[''|'', (''team_id'', ''='', user.team_id.id), (''team_id.user_id'', ''='', user.id)]',
    false,
    true, true, true, true
FROM ir_model m
WHERE m.model = 'crm.lead';

INSERT INTO rule_group_rel (rule_group_id, group_id)
VALUES (
    (SELECT id FROM ir_rule WHERE name = 'Leads - All Stages Team'),
    (SELECT id FROM res_groups WHERE name LIKE '%Sales%Manager%')
);

-- 3. Administradores: tudo (regra sempre verdadeira)
INSERT INTO ir_rule (name, model_id, domain_force, global, perm_read, perm_write, perm_create, perm_unlink)
SELECT
    'Leads - All',
    m.id,
    '[(1, ''='', 1)]',
    false,
    true, true, true, true
FROM ir_model m
WHERE m.model = 'crm.lead';

INSERT INTO rule_group_rel (rule_group_id, group_id)
VALUES (
    (SELECT id FROM ir_rule WHERE name = 'Leads - All'),
    (SELECT id FROM res_groups WHERE name LIKE '%Sales%Admin%')
);

COMMIT;
```

### 10.6 Caso: Acesso Baseado em Data

**Requisito:** Usuários só podem editar registros criados nos últimos 7 dias.

**Implementação:**

```sql
-- Record rule com restrição temporal
INSERT INTO ir_rule (name, model_id, domain_force, global, perm_read, perm_write, perm_create, perm_unlink)
SELECT
    'Edit Recent Only',
    m.id,
    '[''&'', (''user_id'', ''='', user.id), (''create_date'', ''>'', (datetime.now() - timedelta(days=7)).strftime(''%Y-%m-%d''))]',
    false,
    false, true, false, false  -- Aplicar apenas em WRITE
FROM ir_model m
WHERE m.model = 'crm.lead';

INSERT INTO rule_group_rel (rule_group_id, group_id)
VALUES (
    (SELECT id FROM ir_rule WHERE name = 'Edit Recent Only'),
    (SELECT id FROM res_groups WHERE name LIKE '%Sales%User%')
);

-- Criar outra rule para READ (sem restrição temporal)
INSERT INTO ir_rule (name, model_id, domain_force, global, perm_read, perm_write, perm_create, perm_unlink)
SELECT
    'Read All Own',
    m.id,
    '[(''user_id'', ''='', user.id)]',
    false,
    true, false, false, false  -- Apenas READ
FROM ir_model m
WHERE m.model = 'crm.lead';

INSERT INTO rule_group_rel (rule_group_id, group_id)
VALUES (
    (SELECT id FROM ir_rule WHERE name = 'Read All Own'),
    (SELECT id FROM res_groups WHERE name LIKE '%Sales%User%')
);
```

---

## GLOSSÁRIO

**Access Rights (ACL):** Permissões CRUD por modelo e grupo (ir.model.access)

**Record Rules:** Filtros de domínio aplicados a registros específicos (ir.rule)

**Groups:** Conjuntos de permissões atribuídos a usuários (res.groups)

**Implied Groups:** Grupos herdados automaticamente quando usuário recebe outro grupo

**Global Rule:** Record rule sem grupo, restritiva, aplica-se a todos

**Group Rule:** Record rule com grupo, permissiva, aplica-se apenas aos membros

**Domain:** Expressão Python de filtro (ex: `[('field', '=', value)]`)

**CRUD:** Create, Read, Update, Delete

**ORM:** Object-Relational Mapping (camada de abstração do banco)

**Multi-tenancy:** Múltiplas empresas na mesma instância Odoo

**Portal User:** Usuário externo com acesso limitado

**Internal User:** Usuário interno com acesso ao backend

---

## REFERÊNCIAS

**Documentação Oficial Odoo 15:**
- Security: https://www.odoo.com/documentation/15.0/developer/reference/backend/security.html
- ORM API: https://www.odoo.com/documentation/15.0/developer/reference/backend/orm.html

**Odoo Development Documentation:**
- ir.model.access: https://odoo-development.readthedocs.io/en/latest/odoo/models/ir.model.access.html
- ir.rule: https://odoo-development.readthedocs.io/en/latest/odoo/models/ir.rule.html
- res.groups: https://odoo-development.readthedocs.io/en/latest/odoo/models/res.groups.html

**Best Practices:**
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Least Privilege Principle: https://en.wikipedia.org/wiki/Principle_of_least_privilege

---

## 11. 🚨 LESSONS LEARNED - INCIDENT 17/11/2025 {#11-lessons-learned}

Esta seção documenta as lições críticas aprendidas com o incident de remoção incorreta do grupo Internal User, ocorrido em 17/11/2025, que afetou 100% dos usuários ativos do sistema.

---

### 11.1 Sobre Implied Groups

#### ❌ MITO PERIGOSO (Causou o Incident)

"Implied groups criam registros automáticos em `res_groups_users_rel`, tornando a atribuição física redundante."

#### ✅ REALIDADE

**Implied groups são verificados em RUNTIME via JOIN**, **NÃO criam registros físicos**.

**Comportamento Real:**

```python
# Quando você atribui grupo A (que implica grupo B) ao usuário:

# 1. O que É criado fisicamente:
INSERT INTO res_groups_users_rel (uid, gid) VALUES (user_id, group_A_id);

# 2. O que NÃO É criado:
# INSERT INTO res_groups_users_rel (uid, gid) VALUES (user_id, group_B_id);  ← NÃO ACONTECE!

# 3. Como Odoo verifica se usuário tem grupo B:
SELECT 1
FROM res_groups_users_rel rel
LEFT JOIN res_groups_implied_rel impl ON rel.gid = impl.gid
WHERE rel.uid = user_id
  AND (rel.gid = group_B_id OR impl.hid = group_B_id);  ← JOIN em runtime!
```

**Implicação Prática:**

- ✅ ORM do Odoo (`user.has_group()`) verifica implied corretamente
- ❌ Alguns access rights verificam grupo DIRETAMENTE sem considerar implied
- ❌ Módulos de terceiros podem não verificar implied
- ❌ SQL direto não considera implied

**Conclusão:** Grupos base (especialmente ID 1 - Internal User) **DEVEM estar fisicamente atribuídos**.

---

### 11.2 Grupos que NUNCA Devem Ser Removidos

| ID | Nome | XML ID | Consequência se Removido |
|----|------|--------|--------------------------|
| 1 | Internal User | base.group_user | **CRÍTICA:** Perda total de permissões em múltiplos módulos |
| 9 | Portal | base.group_portal | **ALTA:** Usuários portal perdem acesso completamente |
| 10 | Public | base.group_public | **ALTA:** Website público para de funcionar |
| 3 | Settings | base.group_system | **ALTA:** Impossível configurar sistema |

**Como Proteger:**

```sql
-- Criar tabela permanente (executar UMA VEZ)
CREATE TABLE IF NOT EXISTS protected_groups (
    group_id INTEGER PRIMARY KEY,
    group_name VARCHAR(255),
    reason TEXT
);

INSERT INTO protected_groups VALUES
(1, 'Internal User', 'NUNCA REMOVER - Incident 17/11/2025'),
(9, 'Portal', 'NUNCA REMOVER - Grupo base portal'),
(10, 'Public', 'NUNCA REMOVER - Grupo base website'),
(3, 'Settings', 'NUNCA REMOVER - Grupo admin');

-- Usar em TODOS os scripts:
DELETE FROM res_groups_users_rel
WHERE gid NOT IN (SELECT group_id FROM protected_groups)
  AND ...outras condições...;
```

---

### 11.3 Checklist OBRIGATÓRIO para Scripts de Permissões

**ANTES de executar qualquer script que modifica permissões:**

- [ ] **1. Backup criado?**
  ```sql
  CREATE TABLE res_groups_users_rel_backup_YYYYMMDD AS
  SELECT * FROM res_groups_users_rel;
  ```

- [ ] **2. Grupos protegidos estão EXCLUÍDOS?**
  ```sql
  WHERE gid NOT IN (SELECT group_id FROM protected_groups)
  ```

- [ ] **3. Query de PREVIEW executada?**
  ```sql
  -- Mostrar EXATAMENTE o que será removido
  SELECT u.login, g.name FROM ...
  ```

- [ ] **4. Impacto é razoável?**
  - Se > 100 registros afetados → REVISAR COM 2 PESSOAS
  - Se afeta grupos base (1, 9, 10, 3) → **BLOQUEAR IMEDIATAMENTE**

- [ ] **5. Testado em ambiente de dev?**
  - Scripts críticos DEVEM ser testados antes de produção

- [ ] **6. Usa BEGIN/ROLLBACK?**
  ```sql
  BEGIN;
  -- ... seu script ...
  ROLLBACK;  -- Testar primeiro
  -- COMMIT;  -- Só após validação
  ```

- [ ] **7. Plano de rollback definido?**
  - Como reverter se algo der errado?
  - Backup acessível e testado?

- [ ] **8. Horário apropriado?**
  - Evitar horário comercial para mudanças críticas
  - Ter tempo para resolver problemas

---

### 11.4 Script Template SEGURO

```sql
-- ============================================================================
-- TEMPLATE SEGURO PARA SCRIPTS DE PERMISSÕES
-- Copiar este template para QUALQUER modificação em permissões
-- ============================================================================

BEGIN;

-- 1. VERIFICAR INFRAESTRUTURA
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'protected_groups') THEN
        RAISE EXCEPTION 'Tabela protected_groups não existe! Criar antes de continuar.';
    END IF;
END $$;

-- 2. CRIAR BACKUP
CREATE TABLE IF NOT EXISTS res_groups_users_rel_backup_$(date +%Y%m%d_%H%M%S) AS
SELECT * FROM res_groups_users_rel;

-- 3. CRIAR TEMP TABLE COM GRUPOS PROTEGIDOS
CREATE TEMP TABLE protected_groups_temp AS
SELECT group_id as gid FROM protected_groups;

-- 4. IDENTIFICAR REGISTROS AFETADOS
CREATE TEMP TABLE affected_records AS
SELECT uid, gid, 'Seu critério aqui' as reason
FROM res_groups_users_rel
WHERE gid NOT IN (SELECT gid FROM protected_groups_temp)  -- ← PROTEÇÃO!
  AND ...seus critérios...;

-- 5. VALIDAÇÃO 1: Quantos registros?
SELECT
    'TOTAL AFETADO: ' || COUNT(*) || ' registros de ' ||
    COUNT(DISTINCT uid) || ' usuários' as validacao
FROM affected_records;

-- 6. VALIDAÇÃO 2: Algum grupo protegido?
SELECT
    CASE
        WHEN COUNT(*) > 0 THEN
            '🚨 ERRO: Tentando afetar ' || COUNT(*) || ' grupo(s) protegido(s)!'
        ELSE
            '✅ OK: Nenhum grupo protegido será afetado'
    END as check_protecao,
    string_agg(DISTINCT g.name, ', ') as grupos_protegidos
FROM affected_records ar
JOIN res_groups g ON ar.gid = g.id
WHERE ar.gid IN (SELECT gid FROM protected_groups_temp);

-- 7. PREVIEW: Mostrar amostra do que será afetado
SELECT
    u.login as usuario,
    g.name as grupo,
    ar.reason as motivo
FROM affected_records ar
JOIN res_users u ON ar.uid = u.id
JOIN res_groups g ON ar.gid = g.id
ORDER BY u.login, g.name
LIMIT 20;

-- 8. SE TUDO VALIDADO, descomentar linha abaixo:
-- DELETE FROM res_groups_users_rel
-- WHERE (uid, gid) IN (SELECT uid, gid FROM affected_records);

-- 9. DECIDIR: COMMIT ou ROLLBACK
\echo ''
\echo 'Revisar resultados acima.'
\echo 'Se tudo OK, trocar ROLLBACK por COMMIT.'
\echo ''

ROLLBACK;  -- ← Mudar para COMMIT após validação manual
```

---

### 11.5 Monitoramento Proativo

**Script de Validação Diária (OBRIGATÓRIO):**

Ver seção 7.10 para script completo.

**Configurar Cron:**

```bash
# /etc/cron.d/odoo-permissions-check
0 6 * * * postgres psql -d realcred -f /path/to/validacao_diaria.sql >> /var/log/odoo/permissions_check.log 2>&1
```

**Alertas Automáticos:**

```bash
# Se detectar "🚨 ALERTA CRÍTICO" → enviar email imediatamente
if grep -q "🚨 ALERTA CRÍTICO" /var/log/odoo/permissions_check.log; then
    mail -s "ODOO: ALERTA CRÍTICO!" ti@semprereal.com < /var/log/odoo/permissions_check.log
fi
```

---

### 11.6 Métricas de Sucesso (Pós-Incident)

**Implementar e Medir:**

| Métrica | Baseline (Antes) | Meta (Após) | Status Atual |
|---------|------------------|-------------|--------------|
| Incidents críticos de permissões | 1 (nov/2025) | 0 nos próximos 12 meses | ⏳ Monitorar |
| Scripts usando `protected_groups` | 0% | 100% | ⏳ Implementar |
| Tempo de detecção de anomalias | Manual (horas) | Automático (< 24h) | ⏳ Configurar |
| Backups de permissões | Ad-hoc | Diário automático | ⏳ Configurar |
| Validação antes de executar scripts | 0% | 100% | ⏳ Treinar equipe |

---

### 11.7 Comunicação e Escalação

**Quando Comunicar Incidents:**

1. **Imediatamente (< 15 min):**
   - Perda de acesso para > 5 usuários
   - Admin sem acesso ao sistema
   - Módulos críticos (CRM, Vendas) inoperantes

2. **Dentro de 1 hora:**
   - Mudanças não planejadas em permissões
   - Detecção de anomalias pela validação diária

3. **Dentro de 24h:**
   - Mudanças planejadas mas com resultado inesperado
   - Descoberta de configurações incorretas

**Para Quem Escalar:**

- **Nível 1:** TI RealCred (ti@semprereal.com)
- **Nível 2:** Gerente de TI + Analista Sênior
- **Nível 3:** Fornecedor Odoo / Comunidade Odoo

**Template de Comunicação:**

```
Assunto: [ODOO] [CRÍTICO/ALTO/MÉDIO] <Descrição Breve>

INCIDENT ID: INC-YYYYMMDD-NNN
SEVERIDADE: [CRÍTICA/ALTA/MÉDIA/BAIXA]
DESCOBERTO: DD/MM/YYYY HH:MM
STATUS: [EM INVESTIGAÇÃO/EM CORREÇÃO/RESOLVIDO]

IMPACTO:
- Usuários afetados: <número>
- Módulos afetados: <lista>
- Funcionalidades bloqueadas: <lista>

CAUSA RAIZ:
<descrição técnica>

CORREÇÃO APLICADA:
<passos executados>

PREVENÇÃO FUTURA:
<ações para evitar recorrência>

RESPONSÁVEL: <nome>
PRÓXIMOS PASSOS: <ações pendentes>
```

---

### 11.8 Lições Finais - O Que Mudou

#### Antes do Incident (16/11/2025):

❌ Scripts executados diretamente em produção sem validação
❌ Nenhum grupo era considerado "protegido"
❌ Confiança excessiva na lógica de implied groups
❌ Sem monitoramento automático de permissões
❌ Sem checklist obrigatório para mudanças

#### Depois do Incident (17/11/2025 em diante):

✅ **Tabela `protected_groups` criada** - grupos base nunca mais serão removidos
✅ **Script de validação diária** - detecta anomalias em < 24h
✅ **Template seguro** - todo script usa proteções obrigatórias
✅ **Checklist obrigatório** - 8 pontos de verificação antes de executar
✅ **Documentação completa** - 300+ páginas sobre permissões Odoo

#### Mudança Cultural:

**Antes:** "Vamos executar esse script, parece correto."

**Depois:** "Vamos validar este script seguindo o checklist obrigatório, testar em dev, criar backup, executar preview, verificar grupos protegidos, e só então executar com BEGIN/ROLLBACK."

---

### 11.9 Referências Rápidas

**Para consulta rápida durante incidents:**

| Preciso de... | Ver Seção |
|---------------|-----------|
| Entender implied groups | [5.6](#5-6-real-implied) |
| Lista de grupos protegidos | [7.9](#7-9-protected-groups) |
| Script de validação diária | [7.10](#7-10-validation-script) |
| Incident report completo | [8.7](#8-7-incident-internal-user) |
| Template de script seguro | [11.4](#114-script-template-seguro) |
| Checklist obrigatório | [11.3](#113-checklist-obrigatório-para-scripts-de-permissões) |

**Comandos de Emergência:**

```sql
-- 🚨 EMERGÊNCIA: Restaurar grupo Internal User para TODOS
INSERT INTO res_groups_users_rel (uid, gid)
SELECT u.id, 1
FROM res_users u
WHERE u.active = true AND u.share = false AND u.id != 1
ON CONFLICT DO NOTHING;

-- 🚨 EMERGÊNCIA: Verificar quem NÃO tem Internal User
SELECT id, login FROM res_users u
WHERE active = true AND share = false AND id != 1
AND NOT EXISTS (SELECT 1 FROM res_groups_users_rel WHERE uid = u.id AND gid = 1);

-- 🚨 EMERGÊNCIA: Restaurar de backup
INSERT INTO res_groups_users_rel
SELECT * FROM res_groups_users_rel_backup_<DATA>
WHERE gid = 1
ON CONFLICT DO NOTHING;
```

---

### 11.10 Compromisso de Melhoria Contínua

**Este guia é um documento VIVO.**

- Atualizado após cada incident ou descoberta importante
- Versão documentada e datada
- Changelog mantido no início do documento
- Feedback da equipe incorporado trimestralmente

**Versão Atual:** 3.0 (17/11/2025)

**Próxima Revisão Programada:** 17/02/2026

**Responsável:** TI RealCred (ti@semprereal.com)

---

**FIM DO GUIA**

*Última atualização: 17/11/2025 02:20 UTC*
*Versão: 3.0 (Contexto Servidor + Incident Admin Locked)*
*Mantido por: Sistema AI-First + TI RealCred*
*Total de Linhas: 4.185+*

---

## 🎯 CHANGELOG

### Versão 3.0 (17/11/2025 - 02:20 UTC) 🆕

**GRANDE ATUALIZAÇÃO - Contexto Completo para LLMs**

- 🆕 **SEÇÃO 0:** Contexto do Servidor e Acesso (LLM Context)
  - 0.1: Informações do Servidor (IP, portas, configurações)
  - 0.2: Como Acessar (SSH, PostgreSQL, comandos essenciais)
  - 0.3: Estrutura de Arquivos (diretórios, módulos customizados)
  - 0.4: **Admin vs Superuser - DIFERENÇA CRÍTICA** 🚨
  - 0.5: Referências Oficiais Consultadas (14 fontes)

- 🚨 **INCIDENT 2:** Admin User Locked (16/11/2025)
  - Seção 8.8: Incident Report Completo
  - Causa: Confusão entre admin (uid=2) e superuser (uid=1)
  - Solução: Adicionar grupos Access Rights + Website
  - Backup: 557 MB criado preventivamente
  - Resultado: 34 → 37 grupos, admin funcionando 100%

- 📚 **REFERÊNCIAS OFICIAIS:**
  - Odoo Tricks (Security Guide)
  - GitHub Odoo 15.0 (base_groups.xml, res_users_data.xml)
  - Documentação Oficial Odoo 15
  - Forums Stack Overflow e Odoo Community

- 🔧 **COMANDOS PRÁTICOS:**
  - SSH ao servidor odoo-rc
  - Backup e restore de PostgreSQL
  - Upload/download de arquivos
  - Gestão do serviço Odoo
  - Validação de grupos do admin

- 📊 **MÉTRICAS:**
  - Linhas totais: 3.317 → **4.185** (+868 linhas)
  - Seções principais: 11 (0 a 11)
  - Incidents documentados: 2
  - Referências consultadas: 14+
  - Scripts de correção: 2

### Versão 2.0 (17/11/2025)
- 🚨 **CRÍTICO:** Adicionado aviso sobre incident de remoção do Internal User
- ➕ Seção 5.6: Comportamento REAL de Implied Groups
- ➕ Seção 7.9: Grupos Protegidos - NUNCA Remover
- ➕ Seção 7.10: Script de Validação Diária
- ➕ Seção 8.7: Incident Report Completo
- ➕ Seção 11: Lessons Learned (completa)
- 📝 Atualização de todas as referências com proteções
- 📝 Templates de scripts seguros adicionados
- 📊 Total: 3.317 linhas

### Versão 1.0 (16/11/2025)
- 📚 Versão inicial do guia completo
- 📚 10 capítulos cobrindo todos aspectos de segurança Odoo 15
- 📚 2.000+ linhas de documentação técnica
