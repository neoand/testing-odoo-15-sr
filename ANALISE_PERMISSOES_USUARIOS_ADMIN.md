# ANÁLISE DE PERMISSÕES ADMINISTRATIVAS - USUÁRIOS
## Sistema: Odoo 15 - Realcred
## Data: 16/11/2025

---

## 🎯 PROBLEMA IDENTIFICADO

**Situação Atual:** Múltiplos usuários têm privilégios administrativos COMPLETOS, causando:
- "Bagunça" no sistema (modificações não autorizadas)
- Falta de controle centralizado
- Risco de segurança e compliance
- Dificuldade de rastreamento de mudanças

---

## 👥 USUÁRIOS COM PRIVILÉGIOS ADMINISTRATIVOS

### Administrador Principal (OK)
| ID | Login | Nome | Grupos Admin | Status |
|----|-------|------|--------------|--------|
| 2 | admin | ADMINISTRADOR | 88 grupos totais | ✅ CORRETO |

### Usuários Problemáticos (AÇÃO NECESSÁRIA)

#### 1. Wanessa de Oliveira (ID: 10)
- **Login:** financeiro@semprereal.com
- **Nome:** WANESSA DE OLIVEIRA - C75 S74
- **Total de Grupos:** 83 grupos
- **Grupos Críticos:** 20 grupos administrativos

**Grupos Administrativos:**
- ❌ **Settings** (Administração Central) - GRUPO MAIS PODEROSO
- ❌ Administrator - Sales
- ❌ Administrator - Employees
- ❌ Administrator - Attendances
- ❌ Administrator - Recruitment
- ❌ Administrator - Live Chat
- ❌ Administrator - Project
- ❌ Administrator - Purchase
- ❌ Administrator - Surveys
- ❌ Administrator - Lunch
- ❌ Administrator - Contracts
- ❌ Administrator - Time Off
- ❌ Administrator - Expenses
- ❌ Administrator - Inventory
- ❌ Manager - HR PRO
- ❌ Manager - Documents
- ❌ Manager - eLearning
- ❌ Manager - Contatos RC
- ❌ Helpdesk Manager
- ❌ Admin - HR PRO

#### 2. Gustavo Almeida de Oliveira (ID: 12)
- **Login:** marketingdigital@semprereal.com
- **Nome:** GUSTAVO ALMEIDA DE OLIVEIRA – C68 D51
- **Total de Grupos:** 84 grupos
- **Grupos Críticos:** 19 grupos administrativos

**Grupos Administrativos:**
- ❌ **Settings** (Administração Central)
- ❌ Administrator - Sales
- ❌ Administrator - Inventory
- ❌ Administrator - Employees
- ❌ Administrator - Attendances
- ❌ Administrator - Recruitment
- ❌ Administrator - Live Chat
- ❌ Administrator - Project
- ❌ Administrator - Purchase
- ❌ Administrator - Surveys
- ❌ Administrator - Contracts
- ❌ Administrator - Time Off
- ❌ Administrator - Expenses
- ❌ Administrator - Timesheets
- ❌ Manager - HR PRO
- ❌ Manager - Documents
- ❌ Manager - eLearning
- ❌ Manager - Contatos RC
- ❌ Helpdesk Manager

#### 3. Ana Carla Almeida de Oliveira (ID: 79)
- **Login:** ana@semprereal.com
- **Nome:** ANA CARLA ALMEIDA DE OLIVEIRA – D88 I62
- **Total de Grupos:** 82 grupos
- **Grupos Críticos:** 20 grupos administrativos

**Grupos Administrativos:**
- ❌ Settings NÃO tem (melhor que os outros)
- ❌ Administrator - Sales
- ❌ Administrator - Employees
- ❌ Administrator - Attendances
- ❌ Administrator - Recruitment
- ❌ Administrator - Live Chat
- ❌ Administrator - Project
- ❌ Administrator - Purchase
- ❌ Administrator - Surveys
- ❌ Administrator - Lunch
- ❌ Administrator - Contracts
- ❌ Administrator - Time Off
- ❌ Administrator - Expenses
- ❌ Administrator - Inventory
- ❌ Manager - HR PRO
- ❌ Manager - Documents
- ❌ Manager - eLearning
- ❌ Manager - Contatos RC
- ❌ Helpdesk Manager
- ❌ Admin - HR PRO
- ❌ Admin User - Send Messages

**OBSERVAÇÃO:** Ana Carla NÃO tem grupo Settings, mas tem todos os outros administrators!

#### 4. Thiago Mendes Rodrigues (ID: 119)
- **Login:** auxfinanceiro@semprereal.com
- **Nome:** THIAGO MENDES RODRIGUES – C75
- **Total de Grupos:** 82 grupos
- **Grupos Críticos:** 20 grupos administrativos

**Grupos Administrativos:**
- ❌ **Settings** (Administração Central)
- ❌ Administrator - Sales
- ❌ Administrator - Employees
- ❌ Administrator - Attendances
- ❌ Administrator - Live Chat
- ❌ Administrator - Project
- ❌ Administrator - Purchase
- ❌ Administrator - Surveys
- ❌ Administrator - Lunch
- ❌ Administrator - Contracts
- ❌ Administrator - Time Off
- ❌ Administrator - Expenses
- ❌ Administrator - Timesheets
- ❌ Administrator - Inventory
- ❌ Manager - HR PRO
- ❌ Manager - Documents
- ❌ Manager - eLearning
- ❌ Manager - Contatos RC
- ❌ Helpdesk Manager
- ❌ Admin User - Send Messages

---

## 🚨 GRAVIDADE DO PROBLEMA

### Grupo "Settings" (ID: 3)
**O MAIS CRÍTICO** - Permite:
- ✏️ Modificar configurações do sistema
- ✏️ Instalar/desinstalar módulos
- ✏️ Modificar regras de segurança
- ✏️ Alterar grupos de usuários
- ✏️ Acessar modo desenvolvedor
- ✏️ Modificar views/menus/ações

**56 usuários** têm este grupo! (Deveria ser apenas 1 ou 2)

**Usuários problemáticos com Settings:**
- ❌ Wanessa (ID 10)
- ❌ Gustavo (ID 12)
- ❌ Thiago (ID 119)
- ✅ Ana Carla (ID 79) - NÃO TEM (menos grave)

### Grupos "Administrator" de Módulos
Permitem controle total sobre cada módulo:
- Sales, Inventory, Purchase, HR, etc.
- Podem modificar configurações
- Podem deletar registros importantes
- Podem alterar workflows

**TODOS os 4 usuários problemáticos** têm múltiplos grupos Administrator!

---

## 📊 COMPARAÇÃO DE PERMISSÕES

| Usuário | Total Grupos | Settings | Administrators | Managers | Risco |
|---------|--------------|----------|----------------|----------|-------|
| admin (ID 2) | 88 | ✅ Sim | 15 | 5 | ✅ CORRETO |
| Wanessa (ID 10) | 83 | ❌ Sim | 14 | 4 | 🔴 ALTO |
| Gustavo (ID 12) | 84 | ❌ Sim | 14 | 4 | 🔴 ALTO |
| Ana Carla (ID 79) | 82 | ⚠️ Não | 14 | 4 | 🟡 MÉDIO |
| Thiago (ID 119) | 82 | ❌ Sim | 14 | 4 | 🔴 ALTO |

---

## 💡 PROPOSTA DE SOLUÇÃO

### OPÇÃO 1: Restrição Total (RECOMENDADO)
**Remover TODOS os privilégios administrativos** dos 4 usuários e criar perfis adequados à função.

**Para Wanessa e Thiago (Financeiro):**
- ✅ User - Sales (vendas básicas)
- ✅ Billing - Invoicing & Payments (apenas)
- ✅ User - Accounting (sem administração)
- ❌ Remover: Settings, Administrators, Managers

**Para Gustavo (Marketing Digital):**
- ✅ User - Marketing Automation
- ✅ User - Email Marketing
- ✅ User - Social Marketing
- ✅ User - CRM (apenas visualização)
- ❌ Remover: Settings, Administrators, Managers

**Para Ana Carla:**
- ✅ Definir função específica primeiro
- ❌ Remover: Administrators, Managers

**Benefícios:**
- 🔒 Controle total centralizado
- 🔒 Menor risco de "bagunça"
- 🔒 Auditoria clara
- 🔒 Compliance melhorado

**Riscos:**
- ⚠️ Usuários podem reclamar de falta de acesso
- ⚠️ Pode precisar liberar acessos específicos depois

### OPÇÃO 2: Restrição Parcial (INTERMEDIÁRIO)
**Remover apenas grupo Settings** e alguns administrators.

**Remover de TODOS:**
- ❌ Settings (ID 3)
- ❌ Administrator - Inventory
- ❌ Administrator - Purchase
- ❌ Administrator - Project
- ❌ Administrator - Timesheets

**Manter:**
- ✅ User/Officer dos módulos necessários
- ✅ Managers específicos da função

**Benefícios:**
- 🔒 Remove o acesso mais crítico (Settings)
- ✅ Mantém funcionalidade do dia-a-dia
- ✅ Menos resistência dos usuários

**Riscos:**
- ⚠️ Ainda podem fazer mudanças indesejadas
- ⚠️ Controle não é total

### OPÇÃO 3: Criar Novos Grupos Personalizados (IDEAL, MAS MAIS COMPLEXO)
Criar perfis específicos por função:
- "Financeiro Senior"
- "Marketing Digital"
- "Operacional Senior"

**Benefícios:**
- ✅ Granularidade perfeita
- ✅ Fácil de gerenciar no futuro
- ✅ Escalável

**Riscos:**
- ⏱️ Mais trabalhoso para implementar
- ⏱️ Requer análise detalhada de cada função

---

## 🔄 CAPACIDADE DE ROLLBACK

### Backup Necessário ANTES de Aplicar
```sql
-- Backup da tabela res_groups_users_rel
CREATE TABLE res_groups_users_rel_backup_permissoes_20251116 AS
SELECT * FROM res_groups_users_rel;

-- Backup específico dos 4 usuários
CREATE TABLE backup_grupos_usuarios_problematicos_20251116 AS
SELECT r.*, g.name as grupo_name, p.name as usuario_name
FROM res_groups_users_rel r
JOIN res_groups g ON g.id = r.gid
JOIN res_users u ON u.id = r.uid
JOIN res_partner p ON p.id = u.partner_id
WHERE r.uid IN (10, 12, 79, 119);
```

### Rollback Total
```sql
-- Restaurar permissões originais
DELETE FROM res_groups_users_rel WHERE uid IN (10, 12, 79, 119);
INSERT INTO res_groups_users_rel
SELECT uid, gid, create_uid, create_date, write_uid, write_date
FROM backup_grupos_usuarios_problematicos_20251116;
```

---

## 📋 PRÓXIMOS PASSOS

### 1. Decisão (VOCÊ DECIDE)
Escolher qual opção aplicar:
- [ ] OPÇÃO 1: Restrição Total (recomendado)
- [ ] OPÇÃO 2: Restrição Parcial
- [ ] OPÇÃO 3: Criar Grupos Personalizados

### 2. Confirmar Funções
Antes de aplicar, precisamos confirmar:
- Qual é a função específica de cada um?
- O que eles REALMENTE precisam fazer no sistema?
- Existem outros usuários que também têm privilégios demais?

### 3. Criar Backup
- ✅ Backup da tabela res_groups_users_rel
- ✅ Backup específico dos 4 usuários

### 4. Aplicar Mudanças
- Remover grupos conforme opção escolhida
- Testar acesso dos usuários
- Documentar mudanças

### 5. Comunicar Usuários
- Informar que permissões foram ajustadas
- Explicar motivo (segurança/controle)
- Solicitar que reportem acessos necessários

---

## ❓ PERGUNTAS PARA VOCÊ

1. **Qual opção você prefere?** (1, 2 ou 3)

2. **Funções reais:**
   - Wanessa: É do financeiro, mas o que ela faz exatamente?
   - Thiago: Auxiliar financeiro - quais tarefas específicas?
   - Gustavo: Marketing - precisa acessar CRM? Campanhas? E-mail marketing?
   - Ana Carla: Qual a função dela? (pelo código D88 I62 parece vendas)

3. **Há outros usuários** com privilégios demais que você conhece?

4. **Urgência:** Isso é urgente ou podemos analisar com calma?

5. **Comunicação:** Você quer que eu prepare um e-mail/mensagem para enviar aos usuários explicando as mudanças?

---

## 📊 ESTATÍSTICAS ADICIONAIS

**Total de usuários com grupo Settings:** 56 usuários
- 👤 admin (correto)
- 👤 55 outros usuários (MUITO ALTO!)

**Recomendação:** Analisar TODOS os 56 usuários com Settings, não apenas os 4 mencionados.

Quer que eu liste todos os 56 usuários com grupo Settings?

---

**Status:** ANÁLISE COMPLETA - AGUARDANDO DECISÃO
**Próxima Ação:** Você escolher a opção e confirmar as funções dos usuários
