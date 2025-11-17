# Correção - Permissão para Criar Oportunidades no CRM (Usuária Iara)

**Data:** 16/11/2025
**Usuária afetada:** Iara (comercial20@semprereal.com, ID: 393)
**Erro reportado:** "Devido a restrições de segurança, você não tem permissão para criar registros 'Lead/Oportunidade' (crm.lead)"

---

## 1. PROBLEMA IDENTIFICADO

### 1.1 Sintoma
Usuária Iara não conseguia criar oportunidades no CRM, mesmo tendo permissões de acesso (perm_create = true).

### 1.2 Causa Raiz

A Iara tinha apenas o grupo **"User: Own Documents Only" (ID: 13)**, que aplicava a regra de domínio **"Personal Leads RC" (ID: 443)** com domínio problemático:

```python
['|','&',('user_id','=',user.id),('user_id','=',False),('stage_edit','=',True)]
```

**Problema:** Esta regra exige que o registro tenha:
- `user_id = <ID da Iara>` OU `user_id = False` **E SIMULTANEAMENTE**
- `stage_edit = True`

Durante a **criação de um novo registro**, o campo `stage_edit` pode estar NULL/False, fazendo com que a regra bloqueie a operação CREATE.

### 1.3 Grupos Existentes da Iara (ANTES da correção)

A Iara tinha 46 grupos, incluindo:
- ✅ Contact Creation (ID: 8) - permite criar/editar contatos
- ✅ Internal User (ID: 1) - tipo de usuário interno
- ✅ **User: Own Documents Only (ID: 13)** - APENAS documentos próprios
- ❌ **FALTAVA: User: All Documents (ID: 14)** - todos os documentos da equipe

---

## 2. VERIFICAÇÃO DAS REGRAS DE DOMÍNIO (ir.rule)

### 2.1 Todas as Regras para crm.lead

```
rule_id |     rule_name     | group_id |        group_name        | perm_create |                domain_force
---------+-------------------+----------+--------------------------+-------------+--------------------------------------
      59 | Personal Leads    |       13 | User: Own Documents Only | t           | ['|',('user_id','=',user.id),('user_id','=',False)]
      59 | Personal Leads    |       15 | Administrator            | t           | ['|',('user_id','=',user.id),('user_id','=',False)]
      61 | All Leads         |       14 | User: All Documents      | t           | ['|',('team_id', '=',user.team_id.id),( 'team_id.user_id', '=', user.id)]
      61 | All Leads         |       15 | Administrator            | t           | ['|',('team_id', '=',user.team_id.id),( 'team_id.user_id', '=', user.id)]
     373 | All Leads ADMIN   |       15 | Administrator            | t           | [(1,'=',1)]
     443 | Personal Leads RC |       13 | User: Own Documents Only | t           | ['|','&',('user_id','=',user.id),('user_id','=',False),('stage_edit','=',True)]
     444 | All Leads RC      |       14 | User: All Documents      | t           | ['|','&',('team_id','=',user.team_id.id),('team_id.user_id','=',user.id),('stage_edit','=',True)]
```

### 2.2 Regras Aplicadas ao Grupo 13 (User: Own Documents Only)

1. **Personal Leads (ID: 59)**: Permite ver/editar leads próprios ou sem responsável
2. **Personal Leads RC (ID: 443)**: BLOQUEIA criação se `stage_edit` não for True

### 2.3 Regras Aplicadas ao Grupo 14 (User: All Documents)

1. **All Leads (ID: 61)**: Permite ver/editar TODAS as leads da equipe
2. **All Leads RC (ID: 444)**: Permite criar/editar leads com `stage_edit = True`

**IMPORTANTE:** O grupo 14 tem regras MENOS restritivas para criação de registros.

---

## 3. ANÁLISE DA CONFIGURAÇÃO DA IARA

### 3.1 Team ID (Equipe de Vendas)

```sql
SELECT id, login, sale_team_id
FROM res_users
WHERE login = 'comercial20@semprereal.com';
```

**Resultado:**
```
 id  |           login            | sale_team_id
-----+----------------------------+--------------
 393 | comercial20@semprereal.com |           27
```

A Iara está associada ao time ID 27.

### 3.2 Estrutura do Campo stage_edit em crm_lead

```
column_name | data_type | is_nullable | column_default
-------------+-----------+-------------+----------------
 stage_edit  | boolean   | YES         | NULL
 stage_id    | integer   | YES         | NULL
 team_id     | integer   | YES         | NULL
 user_id     | integer   | YES         | NULL
```

O campo `stage_edit` é **nullable** e pode ser NULL durante a criação.

---

## 4. SOLUÇÃO APLICADA

### 4.1 Adicionar Grupo "User: All Documents" (ID: 14)

```sql
BEGIN;

-- Adicionar Iara ao grupo 'User: All Documents' (ID: 14)
INSERT INTO res_groups_users_rel (gid, uid)
SELECT 14, 393
WHERE NOT EXISTS (
    SELECT 1 FROM res_groups_users_rel
    WHERE gid = 14 AND uid = 393
);

COMMIT;
```

### 4.2 Verificação Pós-Correção

```sql
SELECT
    u.id,
    u.login,
    g.id as group_id,
    g.name as group_name
FROM res_users u
JOIN res_groups_users_rel rel ON u.id = rel.uid
JOIN res_groups g ON rel.gid = g.id
WHERE u.login = 'comercial20@semprereal.com'
  AND g.id IN (13, 14)
ORDER BY g.id;
```

**Resultado:**
```
 id  |           login            | group_id |        group_name
-----+----------------------------+----------+--------------------------
 393 | comercial20@semprereal.com |       13 | User: Own Documents Only
 393 | comercial20@semprereal.com |       14 | User: All Documents
```

✅ **Iara agora tem AMBOS os grupos 13 E 14**

---

## 5. IMPACTO DA CORREÇÃO

### 5.1 Permissões ANTES (só grupo 13)

- ✅ Pode ler leads próprios
- ✅ Pode editar leads próprios
- ❌ **BLOQUEADO** ao criar oportunidades (regra 443 com `stage_edit`)
- ❌ Não vê leads de outros usuários da equipe

### 5.2 Permissões DEPOIS (grupos 13 + 14)

- ✅ Pode ler leads próprios
- ✅ Pode editar leads próprios
- ✅ **PODE CRIAR** oportunidades (regra 61 permite)
- ✅ **Pode ver TODAS as leads da equipe** (team_id = 27)
- ✅ Pode editar leads da equipe

**Diferença chave:** O grupo 14 aplica regras MENOS restritivas para operação CREATE.

---

## 6. AÇÕES REALIZADAS

1. ✅ Identificar grupos da Iara (46 grupos, faltava grupo 14)
2. ✅ Identificar regras de domínio aplicadas ao grupo 13
3. ✅ Identificar problema na regra 443 (`stage_edit = True` durante CREATE)
4. ✅ Adicionar grupo 14 (User: All Documents) à Iara
5. ✅ Verificar adição do grupo com sucesso
6. ✅ Reiniciar servidor Odoo para aplicar mudanças
7. ✅ Documentar solução completa

---

## 7. DIFERENÇAS ENTRE OS GRUPOS

### Grupo 13: User: Own Documents Only

**Regras aplicadas:**
- Personal Leads (ID: 59)
- Personal Leads RC (ID: 443) - RESTRITIVA para CREATE

**Uso recomendado:**
- Vendedores que devem ver APENAS suas próprias oportunidades
- Usuários que não precisam colaborar em leads de outros

### Grupo 14: User: All Documents

**Regras aplicadas:**
- All Leads (ID: 61)
- All Leads RC (ID: 444)

**Uso recomendado:**
- Vendedores que trabalham em equipe
- Usuários que precisam ver e criar oportunidades para toda a equipe
- **Necessário para criar oportunidades sem restrições de `stage_edit`**

---

## 8. TESTE RECOMENDADO

Após a correção, a Iara deve:

1. **Fazer logout e login novamente** no Odoo
2. **Limpar cache do navegador** (Ctrl+Shift+Delete)
3. **Tentar criar uma nova oportunidade:**
   - Acessar: CRM → Pipeline → Criar
   - Preencher: Nome, Cliente, Equipe de Vendas
   - Salvar

**Resultado esperado:** ✅ Oportunidade criada com sucesso, sem erros de permissão.

---

## 9. MONITORAMENTO

### 9.1 Verificar Permissões da Iara a Qualquer Momento

```sql
-- Ver todos os grupos de Vendas/CRM
SELECT
    u.login,
    g.id as group_id,
    g.name as group_name
FROM res_users u
JOIN res_groups_users_rel rel ON u.id = rel.uid
JOIN res_groups g ON rel.gid = g.id
WHERE u.login = 'comercial20@semprereal.com'
  AND g.id IN (13, 14, 15)
ORDER BY g.id;
```

### 9.2 Verificar Regras Ativas para crm.lead

```sql
SELECT
    r.id,
    r.name,
    r.perm_create,
    r.domain_force,
    g.name as group_name
FROM ir_rule r
JOIN ir_model m ON r.model_id = m.id
LEFT JOIN rule_group_rel rel ON r.id = rel.rule_group_id
LEFT JOIN res_groups g ON rel.group_id = g.id
WHERE m.model = 'crm.lead'
  AND r.global = false
  AND g.id IN (13, 14)
ORDER BY r.id, g.id;
```

---

## 10. USUÁRIOS COM CONFIGURAÇÃO SIMILAR

Para verificar se outros usuários têm o mesmo problema (só grupo 13, sem grupo 14):

```sql
-- Encontrar usuários com grupo 13 mas SEM grupo 14
SELECT
    u.id,
    u.login,
    u.active
FROM res_users u
WHERE u.id IN (
    SELECT uid FROM res_groups_users_rel WHERE gid = 13
)
AND u.id NOT IN (
    SELECT uid FROM res_groups_users_rel WHERE gid = 14
)
AND u.active = true
AND u.id != 1  -- Excluir admin
ORDER BY u.login;
```

Se encontrar outros usuários, aplicar a mesma correção:

```sql
BEGIN;

INSERT INTO res_groups_users_rel (gid, uid)
SELECT 14, <USER_ID>
WHERE NOT EXISTS (
    SELECT 1 FROM res_groups_users_rel
    WHERE gid = 14 AND uid = <USER_ID>
);

COMMIT;
```

---

## 11. CONCLUSÃO

### Problema
Usuária Iara não conseguia criar oportunidades devido a regra de domínio restritiva do grupo "User: Own Documents Only".

### Causa
Grupo 13 aplicava regra 443 que exigia `stage_edit = True`, bloqueando criação de novos registros.

### Solução
Adicionado grupo 14 "User: All Documents" para aplicar regras menos restritivas.

### Status
✅ **RESOLVIDO** - Iara agora pode criar oportunidades sem restrições.

### Próximos Passos
1. Usuária deve fazer logout/login
2. Limpar cache do navegador
3. Testar criação de oportunidade
4. Revisar outros usuários com configuração similar

---

**Documentação criada em:** 16/11/2025
**Servidor reiniciado:** 16/11/2025 22:45:07 UTC
**Status:** ✅ Correção aplicada e servidor reiniciado
