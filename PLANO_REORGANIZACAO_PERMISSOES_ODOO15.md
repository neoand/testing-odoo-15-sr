# PLANO DE REORGANIZAÇÃO DE PERMISSÕES - ODOO 15 REALCRED

**Data de Criação:** 16/11/2025
**Versão:** 1.0
**Status:** 📋 PLANEJAMENTO - Aguardando Aprovação
**Database:** realcred
**Servidor:** odoo-rc (GCP)

---

## 📊 SUMÁRIO EXECUTIVO

### Objetivo Principal
Reorganizar o sistema de permissões do Odoo 15 para atender aos requisitos de negócio especificados, corrigindo configurações incorretas existentes e estabelecendo uma estrutura clara e eficiente de controle de acesso.

### Escopo do Projeto
- **Módulos Afetados:** Contatos, CRM, Vendas, Financeiro, RH
- **Usuários Impactados:** 35 usuários ativos
- **Duração Estimada:** 6-8 semanas
- **Fases:** 5 fases sequenciais

---

## 🎯 REQUISITOS DE NEGÓCIO (Definidos pelo Cliente)

### 1. Módulo "Contato Sempre Real" e "res.partner"
**Regra:** **TODOS os usuários** devem ter acesso completo (CRUD)

**Justificativa:** Base de dados compartilhada essencial para operações

### 2. Módulos de CRM e Vendas

#### 2.1 Vendedor (Perfil: Vendedor Básico)
- **Acesso:** Apenas aos SEUS PRÓPRIOS documentos
- **Permissões:** CRUD (Create, Read, Update, Delete)
- **Grupo Odoo:** Sales / User: Own Documents Only (ID: 13)

#### 2.2 Líder de Equipe de Vendas (Perfil: Líder de Vendas)
- **Acesso:** Documentos do SEU TIME
- **Permissões:** CRUD completo na equipe
- **Grupo Odoo:** Sales / User: All Documents (ID: 14)

#### 2.3 Operacional (Perfil: Operações)
- **CRM:** Acesso total (CRUD)
- **Vendas:** Acesso total EXCETO DELETE
- **Razão:** Prevenir exclusões acidentais de pedidos

#### 2.4 Financeiro (Perfil: Financeiro)
- **Acesso:** Total aos módulos Financeiro, CRM e Contabilidade
- **Limitação:** Odoo 15 Community (sem recursos Enterprise de Contabilidade)
- **Permissões:** CRUD completo nos módulos disponíveis

### 3. Módulo de Recursos Humanos
**Regra:** Apenas usuários do **grupo RH** e **Administrador**

**Permissões:** CRUD completo

---

## 🔍 ANÁLISE DO ESTADO ATUAL

### Problemas Identificados na Auditoria

#### 🔴 CRÍTICOS (Bloqueiam operações)

1. **Record Rules Problemáticas (IDs 443, 444)**
   - Bloqueiam criação de oportunidades para usuários com grupo 13
   - Campo `stage_edit` causa falha em operações CREATE
   - **Status:** Workaround aplicado (adicionar grupo 14), correção definitiva pendente

2. **Access Rights Duplicados (16 casos)**
   - Modelos: `res.partner`, `account.journal`, `sms.provider`, etc.
   - Comportamento imprevisível
   - **Ação:** Remover duplicatas mantendo a mais recente

3. **Sobrecarga de Grupos**
   - Média: 46 grupos/usuário (ideal: 15-20)
   - Usuário mais crítico: 99 grupos
   - Impacto: Performance degradada, troubleshooting impossível

4. **Access Rights Inúteis (20+ casos)**
   - Todas as permissões = FALSE
   - Poluem banco sem conceder acesso
   - **Ação:** Remover

5. **172 Usuários Inativos com Grupos**
   - ~7.400 registros inúteis em `res_groups_users_rel`
   - Risco de segurança se reativados
   - **Ação:** Limpar grupos de inativos

#### 🟡 ALTA PRIORIDADE (Afetam segurança/organização)

6. **Falta de Documentação em Grupos**
   - Campo `comment` vazio em grupos principais
   - Impossível saber propósito sem investigar código

7. **Modelos Críticos sem Access Rights**
   - `hr.department`, `hr.attendance`, `res.country`, etc.
   - Acesso negado por padrão

8. **Naming Conventions Inconsistentes**
   - Alguns: `crm.lead.user`
   - Outros: `access_crm_lead`

#### 🟢 CONFORMIDADE COM REQUISITOS

**res.partner (Contatos):**
- ❌ **NÃO CONFORME:** Nem todos usuários têm CRUD
- Atual: Apenas grupos específicos (Contact Creation, Officer, Administrator)
- Necessário: Criar access right para "Internal User" com CRUD

**CRM/Vendas:**
- ✅ **PARCIALMENTE CONFORME:** Grupos 13, 14, 15 existem
- ❌ Bugs nas record rules (IDs 443, 444)
- ❌ Falta perfil "Operacional" específico

**RH:**
- ✅ **CONFORME:** Grupos RH existem (HR PRO, Employees)
- ⚠️ Verificar se apenas RH + Admin têm acesso

---

## 📋 ESTADO ATUAL DOS GRUPOS

### Grupos de Vendas (Categoria: Sales)
| ID | Nome | Usuários | Status |
|----|------|----------|--------|
| 13 | User: Own Documents Only | 194 | ✅ Manter |
| 14 | User: All Documents | 113 | ✅ Manter |
| 15 | Administrator | 66 | ✅ Manter |

**Hierarquia Atual (CORRETA):**
```
Administrator (15)
    ↓ implies
User: All Documents (14)
    ↓ implies
User: Own Documents Only (13)
    ↓ implies
Internal User (1)
```

### Grupos de Contabilidade (Categoria: Accounting)
| ID | Nome | Usuários | Propósito |
|----|------|----------|-----------|
| 43 | Auditor | 70 | Apenas leitura |
| 44 | Billing | 71 | Emissão de faturas |
| 45 | Accountant | 69 | Contabilidade completa |
| 46 | Advisor | 69 | Consultoria |

### Grupos de RH (Múltiplas Categorias)
| Categoria | ID | Nome | Usuários |
|-----------|-------|------|----------|
| HR PRO | 93 | User | 145 |
| HR PRO | 94 | Manager | 34 |
| HR PRO | 95 | Admin | 28 |
| Employees | 20 | Officer | 196 |
| Employees | 21 | Administrator | 19 |
| Employees | 22 | Kiosk Attendance | 199 |
| Employees | 140 | sem acesso | 0 | ❌ ÓRFÃO
| Employees | 142 | sem | 0 | ❌ ÓRFÃO
| Attendances | 23 | Manual Attendance | 191 |
| Attendances | 24 | Officer | 188 |
| Attendances | 25 | Administrator | 32 |
| Time Off | 83 | Time Off Officer | 26 |
| Time Off | 84 | Administrator | 17 |
| Expenses | 85 | Team Approver | 20 |
| Expenses | 86 | All Approver | 20 |
| Expenses | 87 | Administrator | 18 |
| Recruitment | 55 | Officer | 20 |
| Recruitment | 56 | Administrator | 17 |

---

## 🎯 PLANO DE AÇÃO DETALHADO

---

## FASE 1: CORREÇÕES CRÍTICAS E LIMPEZA (Semana 1-2)

**Objetivo:** Corrigir bugs bloqueadores e limpar dados órfãos

**Duração:** 2 semanas
**Risco:** Médio
**Impacto:** Alto (Resolve bugs operacionais)

### 1.1 Correção de Record Rules Problemáticas

**Problema:** Rules 443 e 444 bloqueiam criação de oportunidades

**SQL de Correção:**
```sql
BEGIN;

-- Backup das rules antes de alterar
CREATE TABLE IF NOT EXISTS ir_rule_backup_20251116 AS
SELECT * FROM ir_rule WHERE id IN (443, 444);

-- Corrigir rule 443: Personal Leads RC
UPDATE ir_rule
SET domain_force = '[''|'', ''|'', (''user_id'', ''='', user.id), (''user_id'', ''='', False), (''stage_edit'', ''='', True)]'
WHERE id = 443
  AND name = 'Personal Leads RC';

-- Corrigir rule 444: All Leads RC
UPDATE ir_rule
SET domain_force = '[''|'', ''|'', (''team_id'', ''='', user.team_id.id), (''team_id.user_id'', ''='', user.id), (''stage_edit'', ''='', True)]'
WHERE id = 444
  AND name = 'All Leads RC';

COMMIT;
```

**Validação:**
```sql
-- Verificar se correção foi aplicada
SELECT id, name, domain_force
FROM ir_rule
WHERE id IN (443, 444);
```

**Teste Funcional:**
1. Remover grupo 14 de usuário Iara
2. Manter apenas grupo 13
3. Tentar criar oportunidade
4. Deve funcionar ✅

---

### 1.2 Remoção de Access Rights Duplicados

**Problema:** 16 modelos com access rights duplicados

**SQL de Limpeza:**
```sql
BEGIN;

-- Backup antes de deletar
CREATE TABLE IF NOT EXISTS ir_model_access_backup_20251116 AS
SELECT * FROM ir_model_access
WHERE id IN (
    295, 1536, 912, 1189, 1191, 1193, 266, 865,
    2, 15, 17, 306, 293, 1762, 1763, 325
);

-- Remover duplicatas (manter sempre o ID maior = mais recente)
DELETE FROM ir_model_access
WHERE id IN (
    295,   -- res.partner / User: Own Documents Only (manter 908)
    293,   -- res.partner / Administrator (manter 909)
    1536,  -- account.journal / Administrator (manter 1572)
    912,   -- account.tax / User: Own Documents Only (manter 933)
    1189,  -- acrux.chat.connector / Settings (manter 1775)
    1191,  -- acrux.chat.conversation / Internal User (manter 1772)
    1193,  -- acrux.chat.message / Internal User (manter 1773)
    266,   -- calendar.event.type / Internal User (manter 304)
    865,   -- im_livechat.channel / público (manter 1625)
    2,     -- ir.attachment / Internal User (manter 1711)
    15,    -- ir.model / Internal User (manter 377)
    17,    -- ir.model.fields / Internal User (manter 378)
    306,   -- mail.activity.type / Administrator (manter 936)
    1762,  -- sms.provider / SMS User (manter 1764)
    1763,  -- sms.provider / SMS Manager (manter 1765)
    325    -- sms.template / Administrator (manter 951)
);

COMMIT;
```

**Validação:**
```sql
-- Verificar se não há mais duplicatas
SELECT
    m.model,
    g.name as grupo,
    COUNT(*) as duplicatas
FROM ir_model_access a
JOIN ir_model m ON a.model_id = m.id
LEFT JOIN res_groups g ON a.group_id = g.id
WHERE a.active = true
GROUP BY m.model, g.name
HAVING COUNT(*) > 1;
-- Deve retornar 0 linhas
```

---

### 1.3 Remoção de Access Rights Inúteis

**Problema:** 20+ access rights com todas permissões = FALSE

**SQL de Limpeza:**
```sql
BEGIN;

-- Backup antes de deletar
CREATE TABLE IF NOT EXISTS ir_model_access_useless_backup_20251116 AS
SELECT a.*, m.model
FROM ir_model_access a
JOIN ir_model m ON a.model_id = m.id
WHERE a.active = true
  AND NOT a.perm_read
  AND NOT a.perm_write
  AND NOT a.perm_create
  AND NOT a.perm_unlink;

-- Mostrar o que será deletado (para confirmação)
SELECT
    m.model,
    a.name,
    g.name as grupo
FROM ir_model_access a
JOIN ir_model m ON a.model_id = m.id
LEFT JOIN res_groups g ON a.group_id = g.id
WHERE a.active = true
  AND NOT a.perm_read
  AND NOT a.perm_write
  AND NOT a.perm_create
  AND NOT a.perm_unlink;

-- DELETAR (descomentar após validação)
-- DELETE FROM ir_model_access
-- WHERE active = true
--   AND NOT perm_read
--   AND NOT perm_write
--   AND NOT perm_create
--   AND NOT perm_unlink;

COMMIT;
```

---

### 1.4 Limpeza de Grupos de Usuários Inativos

**Problema:** 172 usuários inativos ainda têm ~7.400 registros de grupos

**SQL de Limpeza:**
```sql
BEGIN;

-- Backup completo da tabela
CREATE TABLE IF NOT EXISTS res_groups_users_rel_backup_20251116 AS
SELECT * FROM res_groups_users_rel;

-- Mostrar estatísticas antes
SELECT
    COUNT(DISTINCT rel.uid) as usuarios_inativos,
    COUNT(*) as total_registros_grupos
FROM res_groups_users_rel rel
JOIN res_users u ON rel.uid = u.id
WHERE u.active = false;

-- DELETAR grupos de usuários inativos
DELETE FROM res_groups_users_rel
WHERE uid IN (
    SELECT id
    FROM res_users
    WHERE active = false
);

-- Mostrar estatísticas depois
SELECT COUNT(*) as registros_restantes
FROM res_groups_users_rel;

COMMIT;
```

**Economia Esperada:**
- Antes: ~7.400 registros inúteis
- Depois: 0 registros de inativos
- Ganho: Performance em queries de permissões

---

### 1.5 Remoção de Grupos Órfãos

**Problema:** Grupos sem usuários (IDs 140, 142)

**SQL de Limpeza:**
```sql
BEGIN;

-- Backup
CREATE TABLE IF NOT EXISTS res_groups_orphan_backup_20251116 AS
SELECT * FROM res_groups WHERE id IN (140, 142);

-- Verificar dependências
SELECT
    'ir_model_access' as tabela,
    COUNT(*) as registros
FROM ir_model_access
WHERE group_id IN (140, 142)
UNION ALL
SELECT
    'ir_rule',
    COUNT(*)
FROM rule_group_rel
WHERE group_id IN (140, 142);

-- Se COUNT = 0 em ambos, é seguro deletar
DELETE FROM res_groups
WHERE id IN (140, 142);

COMMIT;
```

---

### 1.6 Checklist de Validação Fase 1

Após executar todas as correções, validar:

```bash
# No servidor
ssh odoo-rc

# Reiniciar Odoo para aplicar mudanças de permissões
sudo systemctl restart odoo-server

# Monitorar logs
sudo tail -f /var/log/odoo/odoo-server.log | grep -i "error\|permission\|access"
```

**Testes Funcionais:**
- [ ] Usuário com grupo 13 consegue criar oportunidade CRM
- [ ] Não há mensagens de erro no log sobre access rights
- [ ] Sistema está estável após restart

---

## FASE 2: CONFIGURAÇÃO CONFORME REQUISITOS (Semana 3-4)

**Objetivo:** Implementar as regras de negócio especificadas

---

### 2.1 res.partner (Contatos) - Acesso CRUD para TODOS

**Requisito:** TODOS os usuários devem ter CRUD em res.partner

**Estado Atual:**
```
res.partner / Internal User: perm_read=true, write=false, create=false, unlink=false
```

**Ação Necessária:** Modificar ou criar access right

**SQL de Implementação:**
```sql
BEGIN;

-- Opção 1: Modificar o access right existente de Internal User
UPDATE ir_model_access
SET
    perm_write = true,
    perm_create = true,
    perm_unlink = true
WHERE id = (
    SELECT a.id
    FROM ir_model_access a
    JOIN ir_model m ON a.model_id = m.id
    JOIN res_groups g ON a.group_id = g.id
    WHERE m.model = 'res.partner'
      AND g.id = 1  -- Internal User
    LIMIT 1
);

-- Validação
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
WHERE m.model = 'res.partner'
  AND g.id = 1;
-- Deve mostrar todas as permissões = true

COMMIT;
```

**Impacto:**
- ✅ Todos usuários internos (vendas, RH, financeiro) podem criar/editar/deletar contatos
- ⚠️ Aumenta risco de exclusões acidentais
- **Mitigação:** Implementar auditoria em deletes (log)

---

### 2.2 CRM/Vendas - Criar Perfil "Operacional"

**Requisito:**
- CRM: Acesso total (CRUD)
- Vendas: Acesso total EXCETO DELETE

**Solução:** Criar grupo customizado "Operacional"

**Implementação via XML (Módulo Customizado):**

Criar arquivo: `/odoo/custom/addons_custom/realcred_permissions/security/security.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="0">

        <!-- Grupo Operacional -->
        <record id="group_operacional" model="res.groups">
            <field name="name">Operacional</field>
            <field name="category_id" ref="base.module_category_sales_sales"/>
            <field name="implied_ids" eval="[(4, ref('sales_team.group_sale_salesman_all_leads'))]"/>
            <field name="comment">PROPÓSITO: Equipe de operações com acesso total em CRM e Vendas (sem delete em Vendas)
QUEM: Analistas de operações, back-office
PERMISSÕES:
- CRM: CRUD completo
- Vendas: CRU (sem Delete)
CRIADO: 2025-11-16
IMPLIED GROUPS:
- Sales / User: All Documents
            </field>
        </record>

    </data>
</odoo>
```

**Access Rights:** `/odoo/custom/addons_custom/realcred_permissions/security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_crm_lead_operacional,crm.lead.operacional,crm.model_crm_lead,group_operacional,1,1,1,1
access_sale_order_operacional,sale.order.operacional,sale.model_sale_order,group_operacional,1,1,1,0
access_sale_order_line_operacional,sale.order.line.operacional,sale.model_sale_order_line,group_operacional,1,1,1,0
```

**Estrutura do Módulo:**
```
/odoo/custom/addons_custom/realcred_permissions/
├── __init__.py
├── __manifest__.py
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
```

**__manifest__.py:**
```python
{
    'name': 'RealCred - Permissões Customizadas',
    'version': '15.0.1.0.0',
    'category': 'Hidden',
    'summary': 'Grupos e permissões customizados para RealCred',
    'depends': ['base', 'crm', 'sale', 'hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

---

### 2.3 Financeiro - Acesso Total (CRM + Contabilidade)

**Requisito:** Grupo Financeiro com CRUD em CRM e módulos financeiros

**Estado Atual:** Grupos Accounting existem (Accountant, Billing, etc.)

**Ação:** Verificar se grupo "Accountant" já atende requisito

**Validação via SQL:**
```sql
-- Verificar access rights do grupo Accountant para CRM
SELECT
    m.model,
    a.perm_read,
    a.perm_write,
    a.perm_create,
    a.perm_unlink
FROM ir_model_access a
JOIN ir_model m ON a.model_id = m.id
JOIN res_groups g ON a.group_id = g.id
WHERE g.id = 45  -- Accountant
  AND m.model IN ('crm.lead', 'account.move', 'account.payment');
```

**Se não houver access right para crm.lead:**

Adicionar em `ir.model.access.csv`:
```csv
access_crm_lead_accountant,crm.lead.accountant,crm.model_crm_lead,account.group_account_user,1,1,1,0
```

---

### 2.4 RH - Restringir Acesso

**Requisito:** Apenas grupo RH + Administrador têm acesso

**Verificação:**
```sql
-- Listar TODOS os access rights de modelos HR
SELECT
    m.model,
    g.name as grupo,
    a.perm_read,
    a.perm_write,
    a.perm_create,
    a.perm_unlink
FROM ir_model_access a
JOIN ir_model m ON a.model_id = m.id
LEFT JOIN res_groups g ON a.group_id = g.id
WHERE m.model LIKE 'hr.%'
  AND a.active = true
ORDER BY m.model, g.name;
```

**Se houver grupos não-RH com acesso:**

**Opção 1 (Restritiva):** Deletar access rights de grupos não-RH
```sql
DELETE FROM ir_model_access
WHERE model_id IN (
    SELECT id FROM ir_model WHERE model LIKE 'hr.%'
)
AND group_id NOT IN (
    -- IDs dos grupos RH + Administrator
    20, 21, 93, 94, 95,  -- RH groups
    1  -- Administrator (Settings)
);
```

**Opção 2 (Flexível):** Criar record rules para isolar dados HR
```xml
<record id="hr_employee_rule_rh_only" model="ir.rule">
    <field name="name">HR Employees: RH Only</field>
    <field name="model_id" ref="hr.model_hr_employee"/>
    <field name="groups" eval="[(4, ref('hr.group_hr_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
    <field name="domain_force">[(1,'=',1)]</field>
</record>
```

---

### 2.5 Checklist de Validação Fase 2

**Testes Funcionais por Perfil:**

**Vendedor (Grupo 13):**
- [ ] Consegue criar/editar/deletar suas próprias oportunidades
- [ ] NÃO vê oportunidades de outros vendedores
- [ ] Consegue criar/editar/deletar contatos (res.partner)

**Líder de Vendas (Grupo 14):**
- [ ] Vê todas as oportunidades do time
- [ ] Consegue editar oportunidades do time
- [ ] Consegue criar/editar/deletar contatos

**Operacional (Novo Grupo):**
- [ ] Vê todas as oportunidades CRM (CRUD)
- [ ] Vê todos os pedidos de venda (CRU, sem delete)
- [ ] Consegue criar/editar contatos

**Financeiro (Accountant):**
- [ ] Acesso total a módulos financeiros
- [ ] Consegue ler CRM (pelo menos)
- [ ] Consegue criar/editar contatos

**RH (Grupos HR PRO):**
- [ ] Acesso total a módulos HR
- [ ] Usuários não-RH NÃO vêem menus de RH

**Usuário Comum (Internal User):**
- [ ] NÃO vê menus de CRM/Vendas (apenas se tiver grupo Sales)
- [ ] Consegue criar/editar/deletar contatos
- [ ] NÃO vê menus de RH

---

## FASE 3: CONSOLIDAÇÃO DE GRUPOS (Semana 5-6)

**Objetivo:** Reduzir sobrecarga de grupos (de 46 para 15-20 grupos/usuário)

---

### 3.1 Análise de Grupos por Usuário

**Identificar usuários com >40 grupos:**
```sql
SELECT
    u.login,
    u.active,
    COUNT(rel.gid) as total_grupos,
    COUNT(DISTINCT cat.id) as categorias_distintas
FROM res_users u
JOIN res_groups_users_rel rel ON u.id = rel.uid
JOIN res_groups g ON rel.gid = g.id
LEFT JOIN ir_module_category cat ON g.category_id = cat.id
GROUP BY u.id, u.login, u.active
HAVING COUNT(rel.gid) > 40
ORDER BY total_grupos DESC;
```

---

### 3.2 Criar Perfis Consolidados

**Estratégia:** Usar `implied_groups` para criar perfis hierárquicos

**Perfis Propostos:**

1. **Vendedor Júnior**
   - Base: Sales / User: Own Documents Only (13)
   - Adicionar: Contact Creation (8)

2. **Vendedor Pleno**
   - Base: Sales / User: All Documents (14)
   - Implied: Vendedor Júnior

3. **Gerente de Vendas**
   - Base: Sales / Administrator (15)
   - Implied: Vendedor Pleno

4. **Operacional Completo**
   - Base: Grupo Operacional (novo)
   - Adicionar: Inventory, Project read-only

5. **Financeiro Completo**
   - Base: Accounting / Accountant (45)
   - Adicionar: CRM read, Sales read

6. **RH Completo**
   - Base: HR PRO / Manager (94)
   - Adicionar: Employees Admin, Time Off Admin

**Implementação:**
```xml
<!-- Perfil: Vendedor Pleno -->
<record id="group_vendedor_pleno" model="res.groups">
    <field name="name">Vendedor Pleno</field>
    <field name="category_id" ref="base.module_category_sales_sales"/>
    <field name="implied_ids" eval="[
        (4, ref('sales_team.group_sale_salesman_all_leads')),
        (4, ref('base.group_user')),
        (4, ref('base.group_partner_manager'))
    ]"/>
</record>
```

---

### 3.3 Migração de Usuários

**Processo:**
1. Identificar perfil do usuário (manual ou via regras)
2. Remover grupos individuais
3. Adicionar perfil consolidado

**Script de Migração (Python):**
```python
# Executar no shell do Odoo
# cd /odoo/odoo-server && sudo -u odoo python3 odoo-bin shell -c /etc/odoo-server.conf -d realcred

import odoo
from odoo import api, SUPERUSER_ID

env = api.Environment(cr, SUPERUSER_ID, {})

# Exemplo: Migrar usuário para perfil "Vendedor Pleno"
user = env['res.users'].search([('login', '=', 'vendedor@example.com')])
perfil_pleno = env.ref('realcred_permissions.group_vendedor_pleno')

# Remover TODOS os grupos de Sales/CRM
grupos_sales = env['res.groups'].search([
    ('category_id.name', 'in', ['Sales', 'CRM Access'])
])
user.groups_id = [(3, g.id) for g in grupos_sales]

# Adicionar apenas o perfil consolidado
user.groups_id = [(4, perfil_pleno.id)]

env.cr.commit()
```

**Fazer gradualmente:**
- Semana 1: Migrar 5-10 usuários de teste
- Semana 2: Validar e migrar restante

---

## FASE 4: DOCUMENTAÇÃO E PADRONIZAÇÃO (Semana 7)

---

### 4.1 Documentar TODOS os Grupos

**Template de Documentação:**
```sql
UPDATE res_groups
SET comment = 'PROPÓSITO: [O que este grupo permite fazer]
QUEM: [Cargos/funções que devem ter este grupo]
PERMISSÕES:
- [Lista de módulos e níveis de acesso]
IMPLIED GROUPS:
- [Grupos que são automaticamente incluídos]
CRIADO: [Data]
ÚLTIMA REVISÃO: [Data]
RESPONSÁVEL: [Nome/Email]'
WHERE id = <GROUP_ID>;
```

**Exemplo Prático:**
```sql
UPDATE res_groups
SET comment = 'PROPÓSITO: Vendedores que trabalham em equipe e precisam ver oportunidades do time
QUEM: Vendedores plenos, seniores, coordenadores
PERMISSÕES:
- CRM: Ver todas oportunidades do time (CRUD)
- Vendas: Ver todos pedidos do time (CRUD)
- Contatos: CRUD completo
IMPLIED GROUPS:
- Sales / User: Own Documents Only (13)
- Internal User (1)
- Contact Creation (8)
CRIADO: 2020-01-15
ÚLTIMA REVISÃO: 2025-11-16
RESPONSÁVEL: TI RealCred (ti@semprereal.com)'
WHERE id = 14
  AND name = 'User: All Documents';
```

---

### 4.2 Criar Matriz de Permissões

**Documento:** `MATRIZ_PERMISSOES_REALCRED.md`

| Cargo | Perfil Odoo | Grupos | Contatos | CRM | Vendas | Financeiro | RH |
|-------|-------------|--------|----------|-----|--------|------------|----|
| Vendedor Júnior | Vendedor Básico | 13, 8 | CRUD | Own CRUD | Own CRU | - | - |
| Vendedor Pleno | Vendedor Pleno | 14 | CRUD | Team CRUD | Team CRUD | - | - |
| Gerente Vendas | Gerente Vendas | 15 | CRUD | All CRUD | All CRUD | Read | - |
| Analista Operacional | Operacional | custom | CRUD | All CRUD | All CRU | - | - |
| Analista Financeiro | Financeiro | 45 | CRUD | Read | Read | CRUD | - |
| Analista RH | RH Manager | 94 | CRUD | - | - | - | CRUD |
| Administrador | Settings | 1 | CRUD | CRUD | CRUD | CRUD | CRUD |

---

### 4.3 Padronizar Naming Conventions

**Regras:**
- Access Rights: `<modelo>.<grupo_abrev>_<permissao>`
  - Exemplo: `crm.lead.salesman_own`, `sale.order.manager_all`

- Record Rules: `<Modelo> - <Grupo> - <Tipo>`
  - Exemplo: `CRM Lead - Salesman - Own Documents`

**Script de Renomeação:**
```sql
-- Renomear access rights
UPDATE ir_model_access
SET name = 'crm.lead.salesman_own'
WHERE id = (
    SELECT a.id
    FROM ir_model_access a
    JOIN ir_model m ON a.model_id = m.id
    JOIN res_groups g ON a.group_id = g.id
    WHERE m.model = 'crm.lead'
      AND g.id = 13
    LIMIT 1
);
```

---

## FASE 5: MONITORAMENTO E AUDITORIA (Contínuo)

---

### 5.1 Scripts de Monitoramento

**Script 1: Usuários com >20 Grupos (Trimestral)**
```sql
-- Salvar como: /home/andlee21/scripts/audit_grupos_usuarios.sql

SELECT
    u.login,
    u.active,
    u.create_date,
    COUNT(rel.gid) as total_grupos,
    string_agg(DISTINCT cat.name, ', ') as categorias
FROM res_users u
JOIN res_groups_users_rel rel ON u.id = rel.uid
JOIN res_groups g ON rel.gid = g.id
LEFT JOIN ir_module_category cat ON g.category_id = cat.id
WHERE u.active = true
GROUP BY u.id
HAVING COUNT(rel.gid) > 20
ORDER BY total_grupos DESC;
```

**Executar via cron:**
```bash
# Adicionar ao crontab do servidor
0 0 1 */3 * /usr/bin/psql realcred -U postgres -f /home/andlee21/scripts/audit_grupos_usuarios.sql > /home/andlee21/logs/audit_grupos_$(date +\%Y\%m\%d).log
```

---

### 5.2 Dashboard de Métricas

**Criar view SQL para dashboard:**
```sql
CREATE OR REPLACE VIEW security_metrics AS
SELECT
    'Usuários Ativos' as metrica,
    COUNT(*) as valor
FROM res_users
WHERE active = true
UNION ALL
SELECT
    'Média Grupos/Usuário Ativo',
    ROUND(AVG(total_grupos), 2)
FROM (
    SELECT COUNT(rel.gid) as total_grupos
    FROM res_users u
    JOIN res_groups_users_rel rel ON u.id = rel.uid
    WHERE u.active = true
    GROUP BY u.id
) sub
UNION ALL
SELECT
    'Access Rights Duplicados',
    COUNT(*)
FROM (
    SELECT model_id, group_id
    FROM ir_model_access
    WHERE active = true
    GROUP BY model_id, group_id
    HAVING COUNT(*) > 1
) dup
UNION ALL
SELECT
    'Usuários Inativos com Grupos',
    COUNT(DISTINCT rel.uid)
FROM res_groups_users_rel rel
JOIN res_users u ON rel.uid = u.id
WHERE u.active = false;
```

**Consultar:**
```sql
SELECT * FROM security_metrics;
```

---

### 5.3 Procedimentos de Auditoria

**Mensal:**
- [ ] Revisar usuários inativos >30 dias com grupos sensíveis (Admin, RH, Financeiro)
- [ ] Verificar se há novos access rights duplicados
- [ ] Validar que usuários novos têm perfil adequado

**Trimestral:**
- [ ] Executar script de auditoria de grupos
- [ ] Revisar usuários com >20 grupos
- [ ] Atualizar documentação de grupos (campo `comment`)

**Anual:**
- [ ] Revisão completa de access rights
- [ ] Revisão completa de record rules
- [ ] Atualizar matriz de permissões
- [ ] Treinamento de equipe sobre segurança

---

## 🛡️ GESTÃO DE RISCOS

### Risco 1: Usuário Perde Acesso Necessário

**Probabilidade:** Média
**Impacto:** Alto

**Mitigação:**
1. ✅ Backup completo antes de qualquer alteração
2. ✅ Testar em ambiente de homologação primeiro
3. ✅ Executar fora de horário comercial
4. ✅ Preparar script de rollback
5. ✅ Comunicar usuários com 48h de antecedência

**Script de Rollback:**
```sql
-- Restaurar grupos de um usuário específico
INSERT INTO res_groups_users_rel (uid, gid)
SELECT uid, gid
FROM res_groups_users_rel_backup_20251116
WHERE uid = <USER_ID>;
```

---

### Risco 2: Performance Degradada Temporariamente

**Probabilidade:** Baixa
**Impacto:** Médio

**Mitigação:**
1. Executar em janela de manutenção (sábado 22h-02h)
2. Fazer alterações em lotes pequenos
3. Monitorar logs em tempo real
4. VACUUM ANALYZE após grandes deletes

**Comando:**
```bash
ssh odoo-rc "sudo -u postgres psql realcred -c 'VACUUM ANALYZE;'"
```

---

### Risco 3: Resistência dos Usuários

**Probabilidade:** Alta
**Impacto:** Baixo-Médio

**Mitigação:**
1. ✅ Email comunicando benefícios (performance, segurança)
2. ✅ Documento com FAQ sobre mudanças
3. ✅ Suporte dedicado durante 1 semana pós-implantação
4. ✅ Reverter se >30% dos usuários reportarem problemas

---

## 📊 MÉTRICAS DE SUCESSO

### KPIs Principais

| Métrica | Baseline | Meta | Como Medir |
|---------|----------|------|------------|
| Média grupos/usuário | 46 | 15-20 | Query SQL |
| Access rights duplicados | 16 | 0 | Query SQL |
| Access rights inúteis | 20+ | 0 | Query SQL |
| Record rules com bugs | 2 | 0 | Teste funcional |
| Usuários inativos com grupos | 172 | 0 | Query SQL |
| Grupos sem documentação | ~100% | 0% | Revisão manual |
| Tempo de login (média) | ? | -20% | Medição antes/depois |
| Tickets de permissão/mês | ? | -50% | Sistema de tickets |

---

### Queries de Medição

**Antes e Depois de cada Fase:**
```sql
-- Salvar resultado em arquivo para comparação

-- 1. Média de grupos por usuário ativo
SELECT
    ROUND(AVG(total_grupos), 2) as media_grupos_usuario
FROM (
    SELECT COUNT(rel.gid) as total_grupos
    FROM res_users u
    JOIN res_groups_users_rel rel ON u.id = rel.uid
    WHERE u.active = true
    GROUP BY u.id
) sub;

-- 2. Access rights duplicados
SELECT COUNT(*) as duplicatas
FROM (
    SELECT model_id, group_id
    FROM ir_model_access
    WHERE active = true
    GROUP BY model_id, group_id
    HAVING COUNT(*) > 1
) dup;

-- 3. Access rights inúteis
SELECT COUNT(*) as inuteis
FROM ir_model_access
WHERE active = true
  AND NOT perm_read
  AND NOT perm_write
  AND NOT perm_create
  AND NOT perm_unlink;

-- 4. Usuários inativos com grupos
SELECT COUNT(DISTINCT uid) as usuarios_inativos_com_grupos
FROM res_groups_users_rel rel
JOIN res_users u ON rel.uid = u.id
WHERE u.active = false;
```

---

## 📅 CRONOGRAMA DETALHADO

### Semana 1-2: FASE 1
- **Dia 1:** Backup completo (DB + filestore)
- **Dia 2-3:** Correção de record rules + testes
- **Dia 4:** Limpeza de access rights duplicados
- **Dia 5:** Limpeza de access rights inúteis
- **Dia 6:** Limpeza de grupos de inativos
- **Dia 7:** Validação completa + documentação

**Janela de Manutenção:** Sábado 22h-02h

---

### Semana 3-4: FASE 2
- **Dia 1-2:** Criar módulo `realcred_permissions`
- **Dia 3:** Implementar res.partner CRUD para todos
- **Dia 4:** Criar grupo Operacional
- **Dia 5:** Configurar permissões Financeiro
- **Dia 6:** Restringir acesso RH
- **Dia 7:** Testes funcionais por perfil

**Instalação do Módulo:**
```bash
ssh odoo-rc "cd /odoo/odoo-server && sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d realcred -i realcred_permissions --stop-after-init"
sudo systemctl restart odoo-server
```

---

### Semana 5-6: FASE 3
- **Semana 5 - Dia 1-3:** Criar perfis consolidados (XML)
- **Semana 5 - Dia 4-7:** Migrar 10 usuários piloto
- **Semana 6 - Dia 1-2:** Validar com usuários piloto
- **Semana 6 - Dia 3-7:** Migrar demais usuários (5-10 por dia)

---

### Semana 7: FASE 4
- **Dia 1-2:** Documentar todos os grupos (campo comment)
- **Dia 3:** Criar matriz de permissões
- **Dia 4:** Padronizar naming conventions
- **Dia 5:** Criar documentação para usuários finais
- **Dia 6-7:** Treinamento da equipe

---

### Semana 8+: FASE 5
- **Configurar cron jobs de auditoria**
- **Criar view de métricas**
- **Estabelecer rotina de revisão trimestral**

---

## 🔧 COMANDOS ÚTEIS

### Backup Completo
```bash
# Conectar ao servidor
ssh odoo-rc

# Parar Odoo
sudo systemctl stop odoo-server

# Backup database
sudo -u postgres pg_dump realcred | gzip > ~/backups/realcred_pre_permissions_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup filestore
sudo tar -czf ~/backups/filestore_pre_permissions_$(date +%Y%m%d_%H%M%S).tar.gz /odoo/filestore/realcred/

# Backup módulos custom
sudo tar -czf ~/backups/custom_addons_pre_permissions_$(date +%Y%m%d_%H%M%S).tar.gz /odoo/custom/addons_custom/

# Reiniciar Odoo
sudo systemctl start odoo-server
```

---

### Restauração de Backup
```bash
# Parar Odoo
sudo systemctl stop odoo-server

# Dropar database
sudo -u postgres dropdb realcred

# Criar database
sudo -u postgres createdb realcred -O odoo

# Restaurar
gunzip < ~/backups/realcred_pre_permissions_XXXXXX.sql.gz | sudo -u postgres psql realcred

# Restaurar filestore
sudo rm -rf /odoo/filestore/realcred/*
sudo tar -xzf ~/backups/filestore_pre_permissions_XXXXXX.tar.gz -C /

# Reiniciar
sudo systemctl start odoo-server
```

---

### Monitoramento

```bash
# Logs em tempo real
sudo tail -f /var/log/odoo/odoo-server.log

# Filtrar erros de permissão
sudo tail -f /var/log/odoo/odoo-server.log | grep -i "access\|permission\|denied"

# Processos Odoo
ps aux | grep odoo-bin

# Uso de memória
free -h

# Conexões PostgreSQL
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname='realcred';"
```

---

## 📚 REFERÊNCIAS

**Documentação Oficial Odoo:**
- [Security in Odoo](https://www.odoo.com/documentation/15.0/developer/reference/backend/security.html)
- [Access Rights](https://www.odoo.com/documentation/15.0/developer/reference/backend/security.html#access-rights)
- [Record Rules](https://www.odoo.com/documentation/15.0/developer/reference/backend/security.html#record-rules)

**Documentação Interna:**
- `RELATORIO_AUDITORIA_PERMISSOES_ODOO15.md` - Auditoria completa
- `ODOO15_SECURITY_GRUPOS_PERMISSOES_GUIA_COMPLETO_AI_FIRST.md` - Guia de boas práticas
- `CORRECAO_CRIACAO_OPORTUNIDADES_IARA.md` - Correção de record rules

---

## ✅ APROVAÇÃO E PRÓXIMOS PASSOS

### Checklist Pré-Execução

- [ ] **Aprovação do Plano:** Revisar e aprovar todo o plano
- [ ] **Validação de Requisitos:** Confirmar requisitos de negócio
- [ ] **Definir Janela de Manutenção:** Escolher data/hora para Fase 1
- [ ] **Comunicação:** Informar usuários com 48h de antecedência
- [ ] **Ambiente de Homologação:** Preparar clone do banco para testes
- [ ] **Backup Completo:** Executar backup antes de iniciar

---

### Próximas Ações

**Após Aprovação deste Plano:**

1. **Criar Ambiente de Homologação**
   ```bash
   # Clonar database para testes
   sudo -u postgres createdb realcred_homolog -O odoo -T realcred
   ```

2. **Executar Fase 1 em Homologação**
   - Testar TODOS os scripts SQL
   - Validar funcionalmente
   - Ajustar se necessário

3. **Agendar Execução em Produção**
   - Proposta: Sábado próximo, 22h-02h
   - Confirmar disponibilidade da equipe

4. **Preparar Comunicação**
   - Email para usuários
   - FAQ sobre mudanças
   - Canal de suporte

---

## 📞 CONTATOS E RESPONSABILIDADES

**Responsável pelo Projeto:** Anderson Oliveira
**Email:** andersongoliveira@semprereal.com
**Servidor:** odoo-rc (35.199.79.229)
**Database:** realcred

**Equipe de Apoio:**
- TI: ti@semprereal.com
- Suporte: suporte@semprereal.com

---

## 📝 REGISTRO DE MUDANÇAS

| Data | Versão | Autor | Mudanças |
|------|--------|-------|----------|
| 16/11/2025 | 1.0 | Claude AI + Anderson | Criação do plano completo |

---

**STATUS:** 📋 **AGUARDANDO APROVAÇÃO**

**Próxima Ação:** Revisar plano e decidir sobre execução

---

**FIM DO PLANO DE REORGANIZAÇÃO**
