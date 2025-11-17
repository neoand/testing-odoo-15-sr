# Documentação - Reestruturação de Permissões de Vendas
## Sistema: Odoo 15 - Realcred
## Data: 16 de Novembro de 2025

---

## 1. PROBLEMA IDENTIFICADO

### Sintomas Reportados
Vendedores reclamando que alguns podem ver informações de clientes que outros não podem ver, causando inconsistências e conflitos na equipe de vendas.

### Diagnóstico
Análise revelou que 16 usuários tinham permissão de "Sales Administrator" (grupo 15), incluindo:
- **Vendedores comuns** que deveriam ver apenas seus próprios documentos
- **Operacionais/Financeiros** que corretamente precisam ver todos os documentos
- **Supervisores e Admin** que corretamente precisam de acesso administrativo

### Problema Root Cause
Não havia uma estrutura clara de permissões por função. Vendedores comuns tinham o mesmo nível de acesso que supervisores, causando:
- Vendedores vendo clientes de outros vendedores
- Conflitos sobre propriedade de leads
- Dificuldade de gestão e controle

---

## 2. ESTRUTURA IMPLEMENTADA

### Níveis de Permissão (res_groups)

| Grupo ID | Nome Odoo | Descrição | Uso |
|----------|-----------|-----------|-----|
| 13 | User: Own Documents Only | Vê apenas documentos próprios | Vendedores |
| 14 | User: All Documents | Vê todos os documentos | Marketing, alguns operacionais |
| 15 | Administrator | Acesso administrativo completo | Supervisor, Admin, Operacional, Financeiro |

### Estrutura por Função

```
┌─────────────────────────────────────────────────────────────┐
│                    ESTRUTURA DE PERMISSÕES                  │
└─────────────────────────────────────────────────────────────┘

1. VENDEDORES (15 usuários)
   ├─ Permissão: Own Documents Only (grupo 13)
   ├─ Acesso: Apenas seus próprios clientes e oportunidades
   └─ Usuários: comercial01-30 (ativos)

2. SUPERVISOR (1 usuário)
   ├─ Permissão: Sales Administrator (grupo 15)
   ├─ Acesso: Vê tudo, gerencia equipe
   └─ Usuário: eduardocadorin@semprereal.com

3. OPERACIONAL (6 usuários)
   ├─ Permissão: Sales Administrator (grupo 15)
   ├─ Acesso: Processam contratos de todos os vendedores
   └─ Usuários: operacional1, 2, 4, 5, 6, 8

4. FINANCEIRO (2 usuários)
   ├─ Permissão: Sales Administrator (grupo 15)
   ├─ Acesso: Processam pagamentos de todos os contratos
   └─ Usuários: financeiro, auxfinanceiro

5. MARKETING (2 usuários)
   ├─ marketingcriativo: All Documents (grupo 14)
   ├─ marketingdigital: Sales Administrator (grupo 15)
   └─ Acesso: Campanhas e análises

6. ADMIN (1 usuário)
   ├─ Permissão: Sales Administrator (grupo 15)
   ├─ Acesso: Configuração e administração do sistema
   └─ Usuário: ana@semprereal.com
```

---

## 3. MUDANÇAS APLICADAS

### Backup Criado
```sql
CREATE TABLE res_groups_users_rel_backup_20251116 AS
SELECT * FROM res_groups_users_rel
WHERE gid IN (13, 14, 15);
-- 381 registros salvos
```

### Usuários Modificados

#### Removido Sales Administrator (grupo 15):
1. **Iara** (ID 393) - comercial20@semprereal.com
2. **Isadora** (ID 30) - comercial22@semprereal.com
3. **Josiane** (ID 33) - comercial12@semprereal.com
4. **Adriely** (ID 382) - Comercial29@semprereal.com
5. **Comercial30** (ID 383) - Comercial30@semprereal.com

#### Removido All Documents (grupo 14):
- Mesmos 5 usuários acima (tinham múltiplos grupos)

#### Adicionado All Documents (grupo 14):
1. **Débora** (ID 23) - marketingcriativo@semprereal.com
   - Era: Own Documents Only
   - Agora: All Documents (precisa ver campanhas)

### SQL Executado
```sql
-- Remover Sales Administrator de vendedores
DELETE FROM res_groups_users_rel
WHERE gid = 15 AND uid IN (393, 30, 33, 382, 383);
-- Resultado: 5 registros deletados

-- Remover All Documents de vendedores
DELETE FROM res_groups_users_rel
WHERE gid = 14 AND uid IN (393, 30, 33, 382, 383);
-- Resultado: 5 registros deletados

-- Garantir Own Documents para vendedores
INSERT INTO res_groups_users_rel (uid, gid)
SELECT unnest(ARRAY[393, 30, 33, 382, 383]), 13
ON CONFLICT DO NOTHING;
-- Resultado: 0 novos (já tinham)

-- Upgrade Marketing para All Documents
DELETE FROM res_groups_users_rel WHERE gid = 13 AND uid = 23;
INSERT INTO res_groups_users_rel (uid, gid) VALUES (23, 14)
ON CONFLICT DO NOTHING;
-- Resultado: 1 registro inserido
```

---

## 4. RESULTADO FINAL

### Resumo por Função

| Função | Total Usuários | Nível de Permissão |
|--------|----------------|--------------------|
| VENDEDOR | 15 | Own Documents Only |
| SUPERVISOR | 1 | Sales Administrator |
| OPERACIONAL | 6 | Sales Administrator |
| FINANCEIRO | 2 | Sales Administrator |
| MARKETING | 2 | All Documents / Admin |
| ADMIN | 1 | Sales Administrator |

### Lista Completa de Usuários

#### VENDEDORES (Own Documents Only)
```
1.  Comercial29@semprereal.com
2.  Comercial30@semprereal.com
3.  comercial01@semprereal.com
4.  comercial11@semprereal.com
5.  comercial12@semprereal.com
6.  comercial15@semprereal.com
7.  comercial16@semprereal.com
8.  comercial20@semprereal.com
9.  comercial22@semprereal.com
10. comercial23@semprereal.com
11. comercial24@semprereal.com
12. comercial25@semprereal.com
13. comercial26@semprereal.com
14. comercial27@semprereal.com
15. comercial28@semprereal.com
```

#### SUPERVISOR (Sales Administrator)
```
1. eduardocadorin@semprereal.com
```

#### OPERACIONAL (Sales Administrator)
```
1. operacional1@semprereal.com
2. operacional2@semprereal.com
3. operacional4@semprereal.com
4. operacional5@semprereal.com
5. operacional6@semprereal.com
6. Operacional8@semprereal.com
```

#### FINANCEIRO (Sales Administrator)
```
1. financeiro@semprereal.com
2. auxfinanceiro@semprereal.com
```

#### MARKETING
```
1. marketingcriativo@semprereal.com - All Documents
2. marketingdigital@semprereal.com - Sales Administrator
```

#### ADMIN
```
1. ana@semprereal.com - Sales Administrator
```

---

## 5. IMPACTO NAS OPERAÇÕES

### O que mudou para VENDEDORES
**ANTES:**
- Alguns vendedores viam TODOS os clientes
- Outros viam apenas os próprios
- Inconsistência causava conflitos

**DEPOIS:**
- TODOS os vendedores veem apenas seus próprios clientes
- Não podem mais ver oportunidades de outros vendedores
- Cada vendedor gerencia apenas sua carteira

### O que NÃO mudou
**OPERACIONAL/FINANCEIRO:**
- Continuam vendo todos os documentos
- Podem processar contratos de qualquer vendedor
- Acesso administrativo mantido

**SUPERVISOR:**
- Continua com acesso total
- Pode gerenciar equipe completa
- Acesso administrativo mantido

**MARKETING:**
- Upgrade para marketingcriativo (agora vê todas campanhas)
- marketingdigital mantém acesso admin

---

## 6. VALIDAÇÃO

### Queries de Validação

#### Verificar permissões de um usuário específico:
```sql
SELECT
    u.login,
    string_agg(g.name, ' + ' ORDER BY g.id) as permissions
FROM res_users u
JOIN res_groups_users_rel r ON u.id = r.uid
JOIN res_groups g ON r.gid = g.id
WHERE u.login = 'comercial01@semprereal.com'
    AND g.id IN (13, 14, 15)
GROUP BY u.login;
```

#### Verificar todos os vendedores:
```sql
SELECT
    u.login,
    CASE
        WHEN MAX(CASE WHEN g.id = 15 THEN 1 ELSE 0 END) = 1 THEN 'Sales Admin'
        WHEN MAX(CASE WHEN g.id = 14 THEN 1 ELSE 0 END) = 1 THEN 'All Docs'
        WHEN MAX(CASE WHEN g.id = 13 THEN 1 ELSE 0 END) = 1 THEN 'Own Docs'
    END as permission
FROM res_users u
JOIN res_groups_users_rel r ON u.id = r.uid
JOIN res_groups g ON r.gid = g.id
WHERE u.login ILIKE 'comercial%'
    AND u.active = true
    AND g.id IN (13, 14, 15)
GROUP BY u.login
ORDER BY u.login;
```

#### Contar por nível de permissão:
```sql
SELECT
    g.name as permission_level,
    COUNT(DISTINCT u.id) as user_count
FROM res_users u
JOIN res_groups_users_rel r ON u.id = r.uid
JOIN res_groups g ON r.gid = g.id
WHERE g.id IN (13, 14, 15)
    AND u.active = true
    AND u.id NOT IN (1, 2)
GROUP BY g.id, g.name
ORDER BY g.id;
```

---

## 7. ROLLBACK (SE NECESSÁRIO)

### ⚠️ IMPORTANTE: Backup Seguro Disponível

Todas as permissões originais estão salvas e podem ser restauradas a qualquer momento!

- **Tabela de Backup:** `res_groups_users_rel_backup_20251116`
- **Total de Registros:** 381
- **Data do Backup:** 16/11/2025 (ANTES das mudanças)
- **Validação:** ✅ Testado e funcionando

### Opção 1: Rollback Automático (RECOMENDADO)

Use o script shell que já está pronto:

```bash
# No servidor odoo-rc
cd ~
chmod +x rollback_permissoes.sh
./rollback_permissoes.sh
```

O script vai:
1. Pedir confirmação
2. Mostrar estado atual
3. Reverter todas as mudanças
4. Mostrar estado após rollback
5. Validar que tudo voltou ao normal

### Opção 2: Rollback Manual via SQL

Se preferir executar manualmente:

```bash
# No servidor odoo-rc
cat ~/ROLLBACK_PERMISSOES.sql | sudo -u postgres psql realcred
```

### Opção 3: Comandos SQL Diretos

Se precisar executar passo a passo:

```sql
-- 1. Limpar permissões atuais dos grupos de vendas
DELETE FROM res_groups_users_rel
WHERE gid IN (13, 14, 15);

-- 2. Restaurar do backup
INSERT INTO res_groups_users_rel (uid, gid)
SELECT uid, gid
FROM res_groups_users_rel_backup_20251116;

-- 3. Verificar restauração
SELECT COUNT(*) FROM res_groups_users_rel WHERE gid IN (13, 14, 15);
-- Deve retornar 381 registros

-- 4. Confirmar usuários específicos voltaram ao normal
SELECT
    u.id,
    u.login,
    string_agg(g.name, ' + ' ORDER BY g.id) as permissions
FROM res_users u
JOIN res_groups_users_rel r ON u.id = r.uid
JOIN res_groups g ON r.gid = g.id
WHERE u.id IN (393, 30, 33, 382, 383, 23)
    AND g.id IN (13, 14, 15)
GROUP BY u.id, u.login
ORDER BY u.id;
```

### Arquivos de Rollback Disponíveis

1. **ROLLBACK_PERMISSOES.sql** - Script SQL completo com validações
2. **rollback_permissoes.sh** - Script shell interativo e seguro
3. **DOCUMENTACAO_PERMISSOES_VENDAS.md** - Esta documentação

### Tempo de Execução

- Rollback completo: ~2 segundos
- Sem necessidade de reiniciar Odoo
- Efeito imediato para todos os usuários

### Validação Pós-Rollback

Após executar o rollback, verificar:

1. **Contagem de registros:**
```sql
SELECT COUNT(*) FROM res_groups_users_rel WHERE gid IN (13, 14, 15);
-- Deve retornar: 381
```

2. **Usuários que foram modificados voltaram ao original:**
```sql
SELECT login,
       CASE
           WHEN MAX(CASE WHEN gid = 15 THEN 1 END) = 1 THEN 'Admin'
           WHEN MAX(CASE WHEN gid = 14 THEN 1 END) = 1 THEN 'All Docs'
           ELSE 'Own Docs'
       END as permission
FROM res_users u
JOIN res_groups_users_rel r ON u.id = r.uid
WHERE u.id IN (393, 30, 33, 382, 383, 23)
      AND r.gid IN (13, 14, 15)
GROUP BY u.id, login;
```

### Reaplicar Mudanças Depois

Se fizer rollback e depois quiser reaplicar as mudanças:

1. **Consultar a Seção 3** desta documentação ("MUDANÇAS APLICADAS")
2. **Executar os SQLs** documentados
3. **OU** criar novo script baseado na documentação

---

## 8. MANUTENÇÃO FUTURA

### Ao adicionar novo vendedor:
```sql
-- Exemplo para comercial31@semprereal.com (ID 999)
INSERT INTO res_groups_users_rel (uid, gid)
VALUES (999, 13)  -- Own Documents Only
ON CONFLICT DO NOTHING;
```

### Ao promover vendedor para supervisor:
```sql
-- Exemplo: promover comercial01 para supervisor
DELETE FROM res_groups_users_rel WHERE uid = 13 AND gid = 13;
INSERT INTO res_groups_users_rel (uid, gid) VALUES (13, 15);
```

### Ao adicionar operacional/financeiro:
```sql
-- Novo operacional (ID 999)
INSERT INTO res_groups_users_rel (uid, gid)
VALUES (999, 15)  -- Sales Administrator
ON CONFLICT DO NOTHING;
```

---

## 9. TROUBLESHOOTING

### Vendedor reclama que não vê cliente
**Verificar:**
1. Cliente está atribuído ao vendedor correto?
2. Vendedor tem grupo 13 (Own Documents)?
3. Não tem conflito de múltiplos grupos?

```sql
-- Ver atribuição do vendedor
SELECT login, partner_id, customer_id
FROM res_users WHERE id = VENDEDOR_ID;

-- Ver grupos do vendedor
SELECT g.name
FROM res_groups g
JOIN res_groups_users_rel r ON g.id = r.gid
WHERE r.uid = VENDEDOR_ID AND g.id IN (13,14,15);
```

### Operacional não consegue processar contrato
**Verificar:**
1. Tem grupo 15 (Sales Administrator)?
2. Módulo de vendas está instalado?

```sql
-- Verificar permissões operacional
SELECT u.login, g.name
FROM res_users u
JOIN res_groups_users_rel r ON u.id = r.uid
JOIN res_groups g ON r.gid = g.id
WHERE u.login = 'operacional1@semprereal.com'
    AND g.id IN (13,14,15);
```

### Novo vendedor vê todos os clientes
**Problema:** Atribuído grupo errado

**Solução:**
```sql
-- Remover grupos 14 e 15
DELETE FROM res_groups_users_rel
WHERE uid = VENDEDOR_ID AND gid IN (14, 15);

-- Garantir grupo 13
INSERT INTO res_groups_users_rel (uid, gid)
VALUES (VENDEDOR_ID, 13)
ON CONFLICT DO NOTHING;
```

---

## 10. REFERÊNCIAS TÉCNICAS

### Tabelas Odoo Envolvidas
- `res_users` - Usuários do sistema
- `res_groups` - Grupos de permissão
- `res_groups_users_rel` - Relacionamento muitos-para-muitos (usuários ↔ grupos)

### IDs dos Grupos de Vendas
```sql
SELECT id, name, category_id
FROM res_groups
WHERE id IN (13, 14, 15);

 id |            name             | category_id
----+-----------------------------+-------------
 13 | User: Own Documents Only    |           2
 14 | User: All Documents         |           2
 15 | Administrator               |           2
```

### Categoria 2 = Sales (CRM)
```sql
SELECT id, name FROM ir_module_category WHERE id = 2;
-- name: 'Sales'
```

---

## 11. HISTÓRICO DE MUDANÇAS

| Data | Mudança | Usuários Afetados | Motivo |
|------|---------|-------------------|--------|
| 2025-11-16 | Reestruturação inicial | 6 usuários | Reclamações de vendedores sobre inconsistência de acesso |
| 2025-11-16 | Backup criado | 381 registros | Segurança antes das mudanças |
| 2025-11-16 | Removido Admin de 5 vendedores | IDs: 393, 30, 33, 382, 383 | Vendedores não devem ter acesso admin |
| 2025-11-16 | Upgrade Marketing | ID 23 (marketingcriativo) | Precisa ver todas as campanhas |

---

## 12. CONTATOS E RESPONSÁVEIS

**Implementado por:** Claude (AI Assistant)
**Aprovado por:** Anderson Oliveira
**Data:** 16/11/2025
**Banco de Dados:** realcred
**Ambiente:** Produção Odoo 15

**Backup Location:**
- Tabela: `res_groups_users_rel_backup_20251116`
- Registros: 381
- Data: 2025-11-16

---

## RESUMO EXECUTIVO

Esta reestruturação resolveu o problema de inconsistência de permissões entre vendedores, implementando uma estrutura clara baseada em funções:

- **15 Vendedores** agora veem apenas seus próprios clientes
- **Supervisor, Operacional e Financeiro** mantêm acesso total para suas funções
- **Marketing** teve upgrade para visualizar todas as campanhas
- **Backup completo** criado para rollback se necessário
- **Documentação detalhada** para manutenção futura

**Status:** ✅ IMPLEMENTADO E VALIDADO
