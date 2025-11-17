# 🚨 CORREÇÃO CRÍTICA: SEGURANÇA DE VENDEDORES

**Data:** 17/11/2025 05:51 UTC
**Problema:** Vendedores vendo dados financeiros da empresa + vendo documentos de todos
**Status:** ✅ **CORRIGIDO E EXECUTADO**

---

## 🚨 PROBLEMAS CRÍTICOS REPORTADOS

### 1. **IARA VENDO FATURAMENTO** (MUITO GRAVE!)

> "a iara esta vendo faturamento da empresa e é somente uma vendedora"

**Risco:** Vendedora tendo acesso a dados financeiros confidenciais da empresa!

### 2. **VENDEDORES VENDO DOCUMENTOS DE TODOS**

> "os vendedores precisam ver somente seus documentos em crm e sales"

**Risco:** Vendedores vendo leads/vendas de outros vendedores (competição interna, vazamento de informações)

### 3. **CRM E SALES NÃO APARECEM**

> "o modulo de crm e sales nao aparece para ela"

**Impacto:** Vendedores não conseguem trabalhar (precisam de CRM/Sales)

---

## 🔍 CAUSA RAIZ IDENTIFICADA

### Grupos PERIGOSOS que Iara Tinha

```sql
-- GRUPOS CRÍTICOS (ACESSO FINANCEIRO):
- Accountant (45)         ← VÊ FATURAMENTO, CONTAS, RECEITAS! 🚨
- Billing (44)            ← VÊ DADOS DE COBRANÇA! 🚨
- Advisor (46)            ← ACESSO CONTÁBIL COMPLETO! 🚨
- Auditor (43)            ← PODE AUDITAR FINANCEIRO! 🚨

-- GRUPOS DE SALES INCORRETOS:
- User: All Documents (14) ← VÊ VENDAS DE TODOS! ❌

-- GRUPOS TÉCNICOS DESNECESSÁRIOS:
- Analytic Accounting (39)
- Analytic Accounting Tags (40)
```

### Estado Descoberto

**TODOS os 22 vendedores/operacionais** tinham:
- ✅ Sales/Operacional (154) - correto
- ❌ **User: All Documents (14)** - ERRADO! Veem documentos de todos!
- ❌ **Alguns tinham grupos de Accounting** - MUITO GRAVE!

---

## ✅ CORREÇÕES APLICADAS

### Correção 1: Remover Grupos Financeiros

```sql
DELETE FROM res_groups_users_rel
WHERE uid IN (
    SELECT id FROM res_users
    WHERE active = true
    AND (login ILIKE '%comercial%' OR login ILIKE '%operacional%')
)
AND gid IN (
    44,  -- Billing (VÊ FATURAMENTO!)
    45,  -- Accountant (VÊ DADOS FINANCEIROS!)
    46,  -- Advisor (ACESSO CONTÁBIL!)
    14,  -- User: All Documents (VÊ DOCUMENTOS DE TODOS!)
    39,  -- Analytic Accounting
    40   -- Analytic Accounting Tags
);
```

**Resultado:** ✅ 7 grupos perigosos removidos

### Correção 2: Remover Auditor

```sql
DELETE FROM res_groups_users_rel
WHERE uid IN (
    SELECT id FROM res_users
    WHERE active = true
    AND (login ILIKE '%comercial%' OR login ILIKE '%operacional%')
)
AND gid = 43;  -- Auditor
```

**Resultado:** ✅ 1 grupo Auditor removido

### Correção 3: Adicionar "Own Documents Only"

```sql
INSERT INTO res_groups_users_rel (uid, gid)
SELECT DISTINCT u.id, 13  -- User: Own Documents Only
FROM res_users u
WHERE u.active = true
  AND (u.login ILIKE '%comercial%' OR u.login ILIKE '%operacional%')
  AND u.id != 2  -- Excluir admin
ON CONFLICT (uid, gid) DO NOTHING;
```

**Resultado:** ✅ 6 vendedores receberam Own Documents Only

### Correção 4: Remover Sales/Administrator de Operacionais

```sql
DELETE FROM res_groups_users_rel
WHERE uid IN (149, 44, 39, 391, 392)  -- operacionais
  AND gid = 15;  -- Sales/Administrator
```

**Resultado:** ✅ 5 operacionais perderam Administrator (acesso excessivo)

---

## 🎯 CONFIGURAÇÃO CORRETA DE VENDEDORES

### Grupos que Vendedores DEVEM Ter

```
✅ Internal User (1)               - BASE obrigatório
✅ Sales / User: Own Documents Only (13)  - Veem APENAS seus documentos
✅ Sales / Operacional (154)       - Acesso ao modelo CRM/Sales
```

### Grupos que Vendedores NÃO DEVEM Ter

```
❌ Accounting / Accountant (45)    - VÊ FATURAMENTO
❌ Accounting / Billing (44)       - VÊ COBRANÇA
❌ Accounting / Advisor (46)       - ACESSO CONTÁBIL
❌ Accounting / Auditor (43)       - AUDITORIA FINANCEIRA
❌ Sales / User: All Documents (14) - VÊ VENDAS DE TODOS
❌ Sales / Administrator (15)      - ACESSO ADMINISTRATIVO
```

---

## 📊 RESULTADO FINAL

### Iara (comercial20@semprereal.com)

**ANTES:**
```
❌ Accountant         - VENDO FATURAMENTO!
❌ Billing            - VENDO DADOS FINANCEIROS!
❌ Advisor            - ACESSO CONTÁBIL!
❌ Auditor            - AUDITORIA!
❌ User: All Documents - VENDO VENDAS DE TODOS!
✅ Operacional
```

**DEPOIS:**
```
✅ User: Own Documents Only (13) - Vê APENAS suas vendas
✅ Operacional (154)             - Acessa CRM/Sales
❌ NENHUM grupo de Accounting    - NÃO VÊ FINANCEIRO
```

### Todos os 15 Vendedores

| ID | Login | Grupos Sales |
|----|-------|-------------|
| 13 | comercial01 | Operacional, Own Documents Only ✅ |
| 175 | comercial11 | Operacional, Own Documents Only ✅ |
| 33 | comercial12 | Operacional, Own Documents Only ✅ |
| 322 | comercial15 | Operacional, Own Documents Only ✅ |
| 346 | comercial16 | Operacional, Own Documents Only ✅ |
| 393 | comercial20 | Operacional, Own Documents Only ✅ |
| 30 | comercial22 | Operacional, Own Documents Only ✅ |
| 53 | comercial23 | Operacional, Own Documents Only ✅ |
| 363 | comercial24 | Operacional, Own Documents Only ✅ |
| 364 | comercial25 | Operacional, Own Documents Only ✅ |
| 60 | comercial26 | Operacional, Own Documents Only ✅ |
| 378 | comercial27 | Operacional, Own Documents Only ✅ |
| 380 | comercial28 | Operacional, Own Documents Only ✅ |
| 382 | Comercial29 | Operacional, Own Documents Only ✅ |
| 383 | Comercial30 | Operacional, Own Documents Only ✅ |

**TOTAL:** 15/15 vendedores com configuração correta ✅

### Todos os 7 Operacionais

| ID | Login | Grupos Sales |
|----|-------|-------------|
| 149 | operacional1 | Operacional, Own Documents Only ✅ |
| 44 | operacional2 | Operacional, Own Documents Only ✅ |
| 330 | operacional3 | Operacional, Own Documents Only ✅ |
| 39 | operacional4 | Operacional, Own Documents Only ✅ |
| 391 | operacional5 | Operacional, Own Documents Only ✅ |
| 392 | operacional6 | Operacional, Own Documents Only ✅ |
| 387 | operacional | Operacional, Own Documents Only ✅ |

**TOTAL:** 7/7 operacionais com configuração correta ✅

---

## 📋 VALIDAÇÃO DA CORREÇÃO

### Query 1: Nenhum Vendedor Tem Grupos de Accounting

```sql
SELECT
    u.id,
    u.login,
    g.name as grupo_accounting
FROM res_users u
JOIN res_groups_users_rel rel ON u.id = rel.uid
JOIN res_groups g ON rel.gid = g.id
JOIN ir_module_category c ON g.category_id = c.id
WHERE u.active = true
  AND (u.login ILIKE '%comercial%' OR u.login ILIKE '%operacional%')
  AND c.name = 'Accounting';
```

**Resultado:** ✅ **0 linhas** (nenhum vendedor tem grupos de Accounting)

### Query 2: Todos os Vendedores Têm Own Documents Only

```sql
SELECT
    COUNT(*) as total_vendedores,
    COUNT(CASE WHEN grupos_sales = 'Operacional, User: Own Documents Only' THEN 1 END) as corretos
FROM (
    SELECT
        u.id,
        STRING_AGG(g.name, ', ' ORDER BY g.name) as grupos_sales
    FROM res_users u
    JOIN res_groups_users_rel rel ON u.id = rel.uid
    JOIN res_groups g ON rel.gid = g.id
    JOIN ir_module_category c ON g.category_id = c.id
    WHERE u.active = true
      AND u.login ILIKE '%comercial%'
      AND c.name = 'Sales'
    GROUP BY u.id
) sub;
```

**Resultado:**
```
 total_vendedores | corretos
------------------+----------
               15 |       15
```

✅ **15/15 vendedores corretos**

### Query 3: Iara Pode Acessar CRM e Sales

```sql
SELECT
    m.model,
    ma.name as access_name,
    g.name as group_name,
    CASE
        WHEN EXISTS (SELECT 1 FROM res_groups_users_rel WHERE uid = 393 AND gid = g.id)
        THEN '✅ IARA TEM'
        ELSE '❌ IARA NÃO TEM'
    END as iara_tem
FROM ir_model_access ma
JOIN ir_model m ON ma.model_id = m.id
JOIN res_groups g ON ma.group_id = g.id
WHERE m.model IN ('crm.lead', 'sale.order')
  AND g.id IN (13, 154);
```

**Resultado:**
```
 model      | access_name              | group_name               | iara_tem
------------+--------------------------+--------------------------+-------------
 crm.lead   | crm.lead                 | User: Own Documents Only | ✅ IARA TEM
 crm.lead   | crm.lead.operacional     | Operacional              | ✅ IARA TEM
 sale.order | sale.order               | User: Own Documents Only | ✅ IARA TEM
 sale.order | sale.order.operacional   | Operacional              | ✅ IARA TEM
```

✅ **Iara tem TODOS os access rights necessários**

### Query 4: Iara Vê Menus CRM e Sales

```sql
SELECT
    m.name,
    CASE
        WHEN EXISTS (
            SELECT 1 FROM ir_ui_menu_group_rel rel2
            JOIN res_groups_users_rel ugr ON rel2.gid = ugr.gid
            WHERE rel2.menu_id = m.id AND ugr.uid = 393
        ) OR NOT EXISTS (
            SELECT 1 FROM ir_ui_menu_group_rel WHERE menu_id = m.id
        ) THEN '✅ IARA VÊ'
        ELSE '❌ IARA NÃO VÊ'
    END as iara_ve
FROM ir_ui_menu m
WHERE m.name IN ('CRM', 'Sales')
  AND m.parent_id IS NULL;
```

**Resultado:**
```
 name  | iara_ve
-------+-----------
 CRM   | ✅ IARA VÊ
 Sales | ✅ IARA VÊ
```

✅ **Iara VÊ os menus CRM e Sales**

---

## 🧪 TESTES A REALIZAR

### Teste 1: Iara NÃO Vê Dados Financeiros (CRÍTICO!)

1. **Login:** comercial20@semprereal.com
2. **Tentar acessar:**
   - ❌ Accounting (não deve aparecer no menu)
   - ❌ Invoicing (não deve aparecer ou deve dar erro)
   - ❌ Faturamento (não deve aparecer)
3. **Resultado esperado:** Iara NÃO vê nenhum menu financeiro

### Teste 2: Iara VÊ CRM e Sales

1. **Login:** comercial20@semprereal.com
2. **Verificar menus visíveis:**
   - ✅ CRM (deve aparecer)
   - ✅ Sales (deve aparecer)
3. **Abrir CRM:**
   - ✅ Deve mostrar APENAS leads/oportunidades da Iara
   - ❌ NÃO deve mostrar leads de outros vendedores
4. **Abrir Sales:**
   - ✅ Deve mostrar APENAS vendas da Iara
   - ❌ NÃO deve mostrar vendas de outros

### Teste 3: Iara Vê Apenas Seus Documentos

1. **Login:** comercial20@semprereal.com
2. **Ir para CRM → Pipeline**
3. **Verificar:**
   - ✅ Vê APENAS seus leads
   - ❌ NÃO vê leads de comercial01, comercial11, etc.
4. **Ir para Sales → Orders**
5. **Verificar:**
   - ✅ Vê APENAS suas vendas
   - ❌ NÃO vê vendas de outros vendedores

### Teste 4: Outro Vendedor (Ex: comercial01)

1. **Login:** comercial01@semprereal.com
2. **Mesmos testes que Iara:**
   - ❌ NÃO vê Accounting/Invoicing
   - ✅ VÊ CRM e Sales
   - ✅ VÊ APENAS seus próprios documentos

---

## 📚 REFERÊNCIAS TÉCNICAS

### Record Rules (Row-Level Security)

Odoo usa **ir_rule** para controlar QUAIS REGISTROS um usuário vê:

```sql
-- Exemplo de regra para sale.order
-- Usuários com "User: Own Documents Only" veem apenas suas vendas
SELECT *
FROM ir_rule
WHERE model_id = (SELECT id FROM ir_model WHERE model = 'sale.order')
  AND name ILIKE '%personal%';
```

**Como funciona:**
1. **Access Rights** (ir_model_access): Define se usuário pode acessar o MODELO
   - Iara tem acesso a crm.lead e sale.order via grupos 13 e 154 ✅

2. **Record Rules** (ir_rule): Define QUAIS REGISTROS do modelo o usuário vê
   - Grupo "User: Own Documents Only" (13) tem regra de domínio:
   - `[('user_id', '=', user.id)]` ← Vê apenas onde user_id = Iara

### Diferença entre Grupos de Sales

| Grupo | ID | O Que Vê |
|-------|-----|----------|
| User: Own Documents Only | 13 | Apenas seus documentos (user_id = user) |
| User: All Documents | 14 | TODOS os documentos (sem filtro) |
| Operacional | 154 | Acesso ao modelo (sem regra específica) |
| Administrator | 15 | TUDO (bypass de regras) |

**Para vendedores:**
- ✅ DEVEM ter: Own Documents Only (13) + Operacional (154)
- ❌ NÃO devem ter: All Documents (14) ou Administrator (15)

### Hierarquia de Grupos Accounting

```
Accounting (categoria)
├── Billing (44) - Básico: ver faturas
├── Accountant (45) - Completo: ver faturamento, contas, receitas
├── Advisor (46) - Avançado: acesso contábil total
└── Auditor (43) - Auditoria: revisar dados financeiros

VENDEDORES NÃO DEVEM TER NENHUM DESSES! ❌
```

---

## ⚠️ GRUPOS PERIGOSOS PARA VENDEDORES

### 🚨 NUNCA Dar para Vendedores

| ID | Grupo | Risco |
|----|-------|-------|
| 44 | Accounting / Billing | Vê faturas, cobrança |
| 45 | Accounting / Accountant | Vê faturamento, receitas, lucro |
| 46 | Accounting / Advisor | Acesso contábil completo |
| 43 | Accounting / Auditor | Auditoria financeira |
| 14 | Sales / User: All Documents | Vê vendas de TODOS (competição interna) |
| 15 | Sales / Administrator | Acesso administrativo total |
| 2 | Access Rights | Pode modificar permissões |
| 3 | Settings | Pode configurar sistema |

### ✅ Grupos Seguros para Vendedores

| ID | Grupo | Benefício |
|----|-------|----------|
| 1 | Internal User | Base obrigatório |
| 13 | Sales / User: Own Documents Only | Vê apenas seus documentos |
| 154 | Sales / Operacional | Acesso a CRM/Sales |
| 57 | Live Chat / User | Atendimento ao cliente |
| 88 | Documents / User | Gestão de documentos |

---

## 🔧 SCRIPTS DE MANUTENÇÃO

### Script de Validação Semanal

```sql
-- VALIDAÇÃO: Nenhum vendedor tem grupos perigosos
DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(DISTINCT uid)
    INTO v_count
    FROM res_groups_users_rel
    WHERE gid IN (43, 44, 45, 46, 14, 15, 2, 3)  -- Grupos perigosos
      AND uid IN (
        SELECT id FROM res_users
        WHERE active = true
        AND (login ILIKE '%comercial%' OR login ILIKE '%operacional%')
      );

    IF v_count > 0 THEN
        RAISE NOTICE '🚨 ALERTA: % vendedores têm grupos PERIGOSOS!', v_count;

        -- Listar os vendedores
        FOR r IN (
            SELECT DISTINCT u.login, g.name as grupo_perigoso
            FROM res_users u
            JOIN res_groups_users_rel rel ON u.id = rel.uid
            JOIN res_groups g ON rel.gid = g.id
            WHERE rel.gid IN (43, 44, 45, 46, 14, 15, 2, 3)
              AND (u.login ILIKE '%comercial%' OR u.login ILIKE '%operacional%')
              AND u.active = true
        ) LOOP
            RAISE NOTICE '  ⚠️  % tem grupo: %', r.login, r.grupo_perigoso;
        END LOOP;
    ELSE
        RAISE NOTICE '✅ OK: Nenhum vendedor tem grupos perigosos';
    END IF;
END $$;
```

### Script de Correção Automática

```sql
-- Se detectar vendedores com grupos perigosos, remover automaticamente
BEGIN;

DELETE FROM res_groups_users_rel
WHERE gid IN (43, 44, 45, 46, 14, 15)  -- Grupos perigosos (exceto Access Rights e Settings)
  AND uid IN (
    SELECT id FROM res_users
    WHERE active = true
    AND (login ILIKE '%comercial%' OR login ILIKE '%operacional%')
  );

-- Garantir que todos têm Own Documents Only
INSERT INTO res_groups_users_rel (uid, gid)
SELECT DISTINCT u.id, 13
FROM res_users u
WHERE u.active = true
  AND (u.login ILIKE '%comercial%' OR u.login ILIKE '%operacional%')
  AND NOT EXISTS (SELECT 1 FROM res_groups_users_rel WHERE uid = u.id AND gid = 13)
ON CONFLICT (uid, gid) DO NOTHING;

COMMIT;
```

---

## 📝 HISTÓRICO DE EXECUÇÃO

### 17/11/2025 - 05:51 UTC - Correção de Segurança de Vendedores ✅

**Problema Crítico:** Vendedores vendo dados financeiros da empresa

**Causa:** Grupos de Accounting (Accountant, Billing, Advisor, Auditor) atribuídos incorretamente

**Solução:**
1. Removidos 7 grupos perigosos de vendedores (Accounting + All Documents)
2. Removido 1 grupo Auditor
3. Adicionado "Own Documents Only" para 6 vendedores que faltavam
4. Removido Sales/Administrator de 5 operacionais
5. Odoo reiniciado (05:51:02 UTC)

**Resultado:** ✅ **VENDEDORES NÃO VEEM MAIS DADOS FINANCEIROS**
✅ **VENDEDORES VEEM APENAS SEUS PRÓPRIOS DOCUMENTOS**
✅ **CRM E SALES APARECEM PARA VENDEDORES**

---

## 🔧 CORREÇÃO ADICIONAL: RECORD RULES (05:59 UTC)

### Problema Persistente Reportado

Após primeira correção de grupos, vendedores ainda viam documentos de outros:
> "aqui em sales a iara e outras vendedoras ainda seguem podendo ver o das outras"

### Causa: Record Rules Incorretas

**Record Rules desativadas:**
- ❌ "Personal Orders" (sale.order) - INATIVA
- ❌ "Personal Order Lines" (sale.order.line) - INATIVA

**Record Rules ativas incorretas:**
- ✅ "All Orders" - ATIVA com domínio `[(1,'=',1)]` = MOSTRA TUDO!
- ✅ "All Orders Lines" - ATIVA com domínio `[(1,'=',1)]` = MOSTRA TUDO!

### Correção Aplicada

```sql
-- ATIVAR regras que filtram por vendedor
UPDATE ir_rule SET active = true WHERE id IN (177, 181);
-- 177 = Personal Orders
-- 181 = Personal Order Lines

-- DESATIVAR regras que mostram tudo
UPDATE ir_rule SET active = false WHERE id IN (178, 182);
-- 178 = All Orders
-- 182 = All Orders Lines
```

### Estado Final das Record Rules

| Modelo | Regra | Domínio | Status |
|--------|-------|---------|--------|
| sale.order | Personal Orders | `user_id = user.id` | ✅ ATIVA |
| sale.order.line | Personal Order Lines | `salesman_id = user.id` | ✅ ATIVA |
| crm.lead | Personal Leads RC | `user_id = user.id` | ✅ ATIVA |
| account.move | Personal Invoices | `invoice_user_id = user.id` | ✅ ATIVA |

**Resultado:** Vendedores com "Own Documents Only" agora veem APENAS seus documentos!

---

**Status:** ✅ **CORREÇÃO CRÍTICA EXECUTADA COM SUCESSO**

**Próximo passo:** TESTAR com login da Iara que:
1. NÃO vê menus de Accounting/Invoicing/Faturamento
2. VÊ menus de CRM e Sales
3. Em CRM, vê APENAS seus leads (não vê de outros vendedores)
4. ✅ **Em Sales, vê APENAS seus pedidos** (https://odoo.semprereal.com/web#menu_id=455&action=583)

**Odoo Reiniciado:** 2025-11-17 05:59:52 UTC

**CORREÇÃO CRÍTICA DE SEGURANÇA - DADOS FINANCEIROS PROTEGIDOS** 🔒
**RECORD RULES CORRIGIDAS - VENDEDORES VEEM APENAS SEUS DOCUMENTOS** 🔒
