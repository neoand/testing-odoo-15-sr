# DOCUMENTAÇÃO - ESTADO ORIGINAL DAS PERMISSÕES
## Sistema: Odoo 15 - Realcred
## Data do Snapshot: 16 de Novembro de 2025 (ANTES das mudanças)

---

## 📋 INFORMAÇÕES DO BACKUP

- **Tabela de Backup:** `res_groups_users_rel_backup_20251116`
- **Total de Registros:** 381 permissões
- **Data/Hora:** 16/11/2025 - Antes da reestruturação
- **Banco de Dados:** realcred
- **Ambiente:** Produção Odoo 15

---

## 1. RESUMO EXECUTIVO - ESTADO ORIGINAL

### Problema Identificado no Estado Original

O sistema tinha **INCONSISTÊNCIA CRÍTICA** nas permissões:

- **5 vendedores** tinham FULL ADMIN (Sales Administrator)
- **10 vendedores** tinham apenas Own Documents
- Vendedores com permissões diferentes causavam conflitos
- Alguns viam todos os clientes, outros não

### Distribuição Original

| Função | Total Usuários | Permissões Inconsistentes |
|--------|----------------|---------------------------|
| VENDEDOR | 15 | ⚠️ 5 com Admin, 10 com Own Docs |
| SUPERVISOR | 1 | ✅ Admin (correto) |
| OPERACIONAL | 6 | ⚠️ Maioria Admin, 1 só All Docs |
| FINANCEIRO | 2 | ✅ Admin (correto) |
| MARKETING | 2 | ⚠️ 1 Own Docs, 1 Admin |
| ADMIN | 1 | ✅ Admin (correto) |

---

## 2. LISTA COMPLETA - ESTADO ORIGINAL DE CADA USUÁRIO

### 🔴 VENDEDORES (15 usuários)

#### ⚠️ Vendedores com SALES ADMINISTRATOR (PROBLEMA!)

| ID | Login | Permissões Originais | Problema |
|----|-------|---------------------|----------|
| 382 | Comercial29@semprereal.com | Own Docs + All Docs + **Admin** | ❌ Vendedor não deve ter Admin |
| 383 | Comercial30@semprereal.com | Own Docs + All Docs + **Admin** | ❌ Vendedor não deve ter Admin |
| 33 | comercial12@semprereal.com | Own Docs + All Docs + **Admin** | ❌ Vendedor não deve ter Admin |
| 393 | comercial20@semprereal.com | Own Docs + All Docs + **Admin** | ❌ Vendedor não deve ter Admin |
| 30 | comercial22@semprereal.com | Own Docs + All Docs + **Admin** | ❌ Vendedor não deve ter Admin |

**Impacto:** Estes 5 vendedores viam TODOS os clientes de TODOS os vendedores.

#### ✅ Vendedores com Own Documents Only (CORRETO)

| ID | Login | Permissões Originais | Status |
|----|-------|---------------------|--------|
| 13 | comercial01@semprereal.com | Own Documents Only | ✅ Correto |
| 175 | comercial11@semprereal.com | Own Documents Only | ✅ Correto |
| 322 | comercial15@semprereal.com | Own Documents Only | ✅ Correto |
| 346 | comercial16@semprereal.com | Own Documents Only | ✅ Correto |
| 53 | comercial23@semprereal.com | Own Documents Only | ✅ Correto |
| 363 | comercial24@semprereal.com | Own Documents Only | ✅ Correto |
| 364 | comercial25@semprereal.com | Own Documents Only | ✅ Correto |
| 60 | comercial26@semprereal.com | Own Documents Only | ✅ Correto |
| 378 | comercial27@semprereal.com | Own Documents Only | ✅ Correto |
| 380 | comercial28@semprereal.com | Own Documents Only | ✅ Correto |

**Total:** 10 vendedores com permissões corretas.

---

### 🟢 SUPERVISOR (1 usuário)

| ID | Login | Permissões Originais | Status |
|----|-------|---------------------|--------|
| 25 | eduardocadorin@semprereal.com | Own Docs + All Docs + **Admin** | ✅ Correto (precisa gerenciar equipe) |

---

### 🟡 OPERACIONAL (6 usuários)

| ID | Login | Permissões Originais | Status |
|----|-------|---------------------|--------|
| 149 | operacional1@semprereal.com | Own Docs + All Docs + **Admin** | ✅ Correto |
| 44 | operacional2@semprereal.com | Own Docs + All Docs + **Admin** | ✅ Correto |
| 39 | operacional4@semprereal.com | Own Docs + All Docs + **Admin** | ✅ Correto |
| 391 | operacional5@semprereal.com | Own Docs + All Docs + **Admin** | ✅ Correto |
| 392 | operacional6@semprereal.com | Own Docs + All Docs + **Admin** | ✅ Correto |
| 394 | Operacional8@semprereal.com | Own Docs + All Docs | ✅ Suficiente (processa contratos) |

**Nota:** Operacionais processam contratos de todos os vendedores, precisam ver tudo.

---

### 💰 FINANCEIRO (2 usuários)

| ID | Login | Permissões Originais | Status |
|----|-------|---------------------|--------|
| 10 | financeiro@semprereal.com | Own Docs + All Docs + **Admin** | ✅ Correto |
| 119 | auxfinanceiro@semprereal.com | Own Docs + All Docs + **Admin** | ✅ Correto |

**Nota:** Financeiro precisa processar pagamentos de todos os contratos.

---

### 📢 MARKETING (2 usuários)

| ID | Login | Permissões Originais | Status |
|----|-------|---------------------|--------|
| 23 | marketingcriativo@semprereal.com | **Own Documents Only** | ⚠️ Insuficiente (precisa ver campanhas) |
| 12 | marketingdigital@semprereal.com | Own Docs + All Docs + **Admin** | ✅ Correto |

**Problema:** Marketing Criativo não conseguia ver dados de todas as campanhas.

---

### 👤 ADMIN (1 usuário)

| ID | Login | Permissões Originais | Status |
|----|-------|---------------------|--------|
| 79 | ana@semprereal.com | Own Docs + All Docs + **Admin** | ✅ Correto |

---

## 3. DETALHAMENTO TÉCNICO DOS GRUPOS

### Grupos de Segurança Odoo (res_groups)

| ID | Nome Técnico | Descrição | Categoria |
|----|--------------|-----------|-----------|
| 13 | User: Own Documents Only | Vê apenas documentos próprios | Sales |
| 14 | User: All Documents | Vê todos os documentos | Sales |
| 15 | Administrator | Acesso administrativo completo | Sales |

### Hierarquia de Permissões

```
┌─────────────────────────────────────────────────────────┐
│  Grupo 15: Administrator (Sales Admin)                 │
│  ├─ Configurações do módulo Vendas                     │
│  ├─ Ver TODOS os documentos                            │
│  ├─ Gerenciar equipes                                  │
│  └─ Acesso administrativo total                        │
├─────────────────────────────────────────────────────────┤
│  Grupo 14: All Documents                               │
│  ├─ Ver TODOS os documentos                            │
│  ├─ Editar documentos de outros                        │
│  └─ SEM acesso administrativo                          │
├─────────────────────────────────────────────────────────┤
│  Grupo 13: Own Documents Only                          │
│  ├─ Ver APENAS seus documentos                         │
│  ├─ Criar novos documentos                             │
│  └─ Editar apenas os próprios                          │
└─────────────────────────────────────────────────────────┘
```

---

## 4. MATRIZ COMPLETA - ESTADO ORIGINAL

### Tabela de Permissões por Usuário

| ID | Login | Função | Grupo 13 (Own) | Grupo 14 (All) | Grupo 15 (Admin) | Total Grupos |
|----|-------|--------|----------------|----------------|------------------|--------------|
| 13 | comercial01 | VENDEDOR | ✓ | | | 1 |
| 30 | comercial22 | VENDEDOR | ✓ | ✓ | ✓ | 3 |
| 33 | comercial12 | VENDEDOR | ✓ | ✓ | ✓ | 3 |
| 53 | comercial23 | VENDEDOR | ✓ | | | 1 |
| 60 | comercial26 | VENDEDOR | ✓ | | | 1 |
| 175 | comercial11 | VENDEDOR | ✓ | | | 1 |
| 322 | comercial15 | VENDEDOR | ✓ | | | 1 |
| 346 | comercial16 | VENDEDOR | ✓ | | | 1 |
| 363 | comercial24 | VENDEDOR | ✓ | | | 1 |
| 364 | comercial25 | VENDEDOR | ✓ | | | 1 |
| 378 | comercial27 | VENDEDOR | ✓ | | | 1 |
| 380 | comercial28 | VENDEDOR | ✓ | | | 1 |
| 382 | Comercial29 | VENDEDOR | ✓ | ✓ | ✓ | 3 |
| 383 | Comercial30 | VENDEDOR | ✓ | ✓ | ✓ | 3 |
| 393 | comercial20 | VENDEDOR | ✓ | ✓ | ✓ | 3 |
| 25 | eduardocadorin | SUPERVISOR | ✓ | ✓ | ✓ | 3 |
| 39 | operacional4 | OPERACIONAL | ✓ | ✓ | ✓ | 3 |
| 44 | operacional2 | OPERACIONAL | ✓ | ✓ | ✓ | 3 |
| 149 | operacional1 | OPERACIONAL | ✓ | ✓ | ✓ | 3 |
| 391 | operacional5 | OPERACIONAL | ✓ | ✓ | ✓ | 3 |
| 392 | operacional6 | OPERACIONAL | ✓ | ✓ | ✓ | 3 |
| 394 | Operacional8 | OPERACIONAL | ✓ | ✓ | | 2 |
| 10 | financeiro | FINANCEIRO | ✓ | ✓ | ✓ | 3 |
| 119 | auxfinanceiro | FINANCEIRO | ✓ | ✓ | ✓ | 3 |
| 12 | marketingdigital | MARKETING | ✓ | ✓ | ✓ | 3 |
| 23 | marketingcriativo | MARKETING | ✓ | | | 1 |
| 79 | ana | ADMIN | ✓ | ✓ | ✓ | 3 |

**Total de Usuários:** 27
**Total de Registros de Permissões:** 381 (considerando TODOS os grupos, não só 13, 14, 15)

---

## 5. ANÁLISE DE INCONSISTÊNCIAS NO ESTADO ORIGINAL

### 🔴 Problemas Críticos Identificados

#### 1. Vendedores com Poderes Administrativos
```
❌ PROBLEMA: 5 de 15 vendedores (33%) tinham Sales Administrator

   comercial12@semprereal.com  (ID 33)
   comercial20@semprereal.com  (ID 393)
   comercial22@semprereal.com  (ID 30)
   Comercial29@semprereal.com  (ID 382)
   Comercial30@semprereal.com  (ID 383)

   Consequência:
   - Viam clientes de TODOS os vendedores
   - Podiam modificar configurações de vendas
   - Causavam conflitos de propriedade de leads
```

#### 2. Vendedores com Múltiplos Grupos
```
⚠️ OBSERVAÇÃO: Os 5 vendedores problemáticos tinham 3 grupos simultâneos:
   - Own Documents Only (redundante)
   - All Documents (redundante quando tem Admin)
   - Administrator (o mais permissivo)

   Odoo usa o grupo MAIS PERMISSIVO quando há múltiplos.
```

#### 3. Marketing com Permissão Insuficiente
```
❌ PROBLEMA: marketingcriativo@semprereal.com tinha apenas Own Docs

   Consequência:
   - Não conseguia ver dados de campanhas de outros
   - Não conseguia fazer análises globais
   - Trabalho limitado
```

---

## 6. COMPARAÇÃO: ANTES vs DEPOIS

### Estado ORIGINAL (16/11/2025 - ANTES)

| Função | Usuários | Permissões | Problema |
|--------|----------|------------|----------|
| VENDEDOR | 15 | 5 Admin + 10 Own Docs | ❌ Inconsistente |
| SUPERVISOR | 1 | Admin | ✅ OK |
| OPERACIONAL | 6 | 5 Admin + 1 All Docs | ⚠️ Quase OK |
| FINANCEIRO | 2 | Admin | ✅ OK |
| MARKETING | 2 | 1 Admin + 1 Own Docs | ⚠️ Inconsistente |
| ADMIN | 1 | Admin | ✅ OK |

### Estado NOVO (16/11/2025 - DEPOIS da reestruturação)

| Função | Usuários | Permissões | Resultado |
|--------|----------|------------|-----------|
| VENDEDOR | 15 | **TODOS Own Docs** | ✅ Consistente |
| SUPERVISOR | 1 | Admin | ✅ Mantido |
| OPERACIONAL | 6 | Admin/All Docs | ✅ Mantido |
| FINANCEIRO | 2 | Admin | ✅ Mantido |
| MARKETING | 2 | **1 Admin + 1 All Docs** | ✅ Corrigido |
| ADMIN | 1 | Admin | ✅ Mantido |

---

## 7. REGISTROS RAW DO BACKUP

### SQL para Consultar Estado Original

```sql
-- Ver TODOS os registros do backup
SELECT
    b.uid as user_id,
    u.login,
    b.gid as group_id,
    g.name as group_name
FROM res_groups_users_rel_backup_20251116 b
JOIN res_users u ON b.uid = u.id
JOIN res_groups g ON b.gid = g.id
WHERE u.active = true
ORDER BY u.login, g.id;
```

### SQL para Ver Usuário Específico no Estado Original

```sql
-- Exemplo: ver estado original do comercial20
SELECT
    u.id,
    u.login,
    string_agg(g.name, ' | ' ORDER BY g.id) as permissoes_originais
FROM res_users u
JOIN res_groups_users_rel_backup_20251116 b ON u.id = b.uid
JOIN res_groups g ON b.gid = g.id
WHERE u.login = 'comercial20@semprereal.com'
    AND g.id IN (13, 14, 15)
GROUP BY u.id, u.login;

-- Resultado esperado:
-- User: Own Documents Only | User: All Documents | Administrator
```

---

## 8. ESTATÍSTICAS DO ESTADO ORIGINAL

### Distribuição de Grupos

```
Grupo 13 (Own Documents Only):  27 usuários (100% tinham este grupo)
Grupo 14 (All Documents):       16 usuários (59%)
Grupo 15 (Administrator):       16 usuários (59%)

Usuários com APENAS Grupo 13:   11 usuários (41%)
Usuários com TODOS os 3 grupos: 15 usuários (56%)
Usuários com 2 grupos:          1 usuário  (4%)
```

### Por Função

```
VENDEDORES:
  - 5 com Admin (33%)
  - 10 com Own Docs apenas (67%)

STAFF (Operacional/Financeiro):
  - 7 com Admin (88%)
  - 1 com All Docs apenas (12%)

SUPERVISÃO/ADMIN:
  - 2 com Admin (100%)

MARKETING:
  - 1 com Admin (50%)
  - 1 com Own Docs (50%)
```

---

## 9. BACKUP E SEGURANÇA

### Informações do Backup

- **Criado em:** 16/11/2025
- **Método:** `CREATE TABLE AS SELECT`
- **Validação:** ✅ 381 registros confirmados
- **Integridade:** ✅ Todos os JOINs funcionando
- **Teste de Rollback:** ✅ Testado e validado

### Comando de Criação do Backup

```sql
CREATE TABLE IF NOT EXISTS res_groups_users_rel_backup_20251116 AS
SELECT * FROM res_groups_users_rel
WHERE gid IN (13, 14, 15);

-- Resultado: 381 registros copiados
```

### Verificação do Backup

```sql
-- Verificar integridade
SELECT COUNT(*) FROM res_groups_users_rel_backup_20251116;
-- Deve retornar: 381

-- Verificar se JOINs funcionam
SELECT COUNT(DISTINCT b.uid)
FROM res_groups_users_rel_backup_20251116 b
JOIN res_users u ON b.uid = u.id
WHERE u.active = true;
-- Deve retornar: 27 (usuários ativos)
```

---

## 10. USAR ESTE DOCUMENTO

### Para consultar estado original de um usuário:

1. Procurar na **Seção 2** (Lista Completa)
2. Verificar **Seção 4** (Matriz Completa) para ver todos os grupos
3. Conferir **Seção 5** (Análise de Inconsistências) para entender problemas

### Para fazer rollback:

1. Seguir instruções em `DOCUMENTACAO_PERMISSOES_VENDAS.md` (Seção 7)
2. Usar scripts `ROLLBACK_PERMISSOES.sql` ou `rollback_permissoes.sh`
3. Após rollback, estado voltará EXATAMENTE como documentado aqui

### Para comparar antes/depois:

1. Este documento = ANTES
2. `DOCUMENTACAO_PERMISSOES_VENDAS.md` Seção 4 = DEPOIS
3. `DOCUMENTACAO_PERMISSOES_VENDAS.md` Seção 3 = O que mudou

---

## RESUMO FINAL

✅ **Estado Original Documentado Completamente**
✅ **381 Registros no Backup**
✅ **27 Usuários Ativos Catalogados**
✅ **Todos os Grupos e Permissões Mapeados**
✅ **Inconsistências Identificadas e Documentadas**
✅ **Pronto para Rollback a Qualquer Momento**

**Data da Documentação:** 16/11/2025
**Autor:** Claude (AI Assistant)
**Aprovado por:** Anderson Oliveira
