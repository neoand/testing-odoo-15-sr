# ROLLBACK COMPLETO - OTIMIZAÇÕES DE STAGES CRM
## Sistema: Odoo 15 - Realcred
## Data do Backup: 16/11/2025
## Data de Aplicação: 16/11/2025

---

## 📋 SUMÁRIO

Este documento contém TODOS os procedimentos para reverter as otimizações aplicadas ao sistema de stages do CRM, voltando ao estado EXATO anterior.

---

## 1. BACKUPS CRIADOS

### 1.1. Backups no Banco de Dados PostgreSQL

| Tabela Backup | Registros | Descrição |
|---------------|-----------|-----------|
| `crm_stage_crm_team_rel_backup_20251116` | 56 | Relação stage ↔ teams (ANTES unificação) |
| `crm_team_member_backup_20251116` | 139 | Membros dos times (ANTES unificação) |
| `crm_team_backup_20251116` | 21 | Times do CRM (ANTES mudanças) |
| `crm_stage_backup_20251116` | 26 | Stages do CRM |
| `crm_lead_backup_20251116` | 25,763 | Leads (stage_id, user_id, team_id) |

### 1.2. Backups de Arquivos Python

| Arquivo | Localização |
|---------|-------------|
| crm_stage.py.backup_20251116 | `/odoo/custom/addons_custom/crm_products/models/` |

---

## 2. MUDANÇAS APLICADAS

### 2.1. Banco de Dados

#### Mudança 1: Unificação de Times
**O que foi feito:**
- TIME JULIENE (ID 28) desativado
- 3 membros movidos para TIME JULIENE (ID 6)
- 6 leads movidos do time 28 para time 6
- 1 usuário com team padrão atualizado

**SQL Executado:**
```sql
UPDATE crm_team_member SET crm_team_id = 6 WHERE crm_team_id = 28;
UPDATE crm_lead SET team_id = 6 WHERE team_id = 28;
UPDATE res_users SET sale_team_id = 6 WHERE sale_team_id = 28;
UPDATE crm_stage_crm_team_rel SET crm_team_id = 6 WHERE crm_team_id = 28;
UPDATE crm_team SET active = false, name = 'TIME JULIENE (UNIFICADO NO ID 6)' WHERE id = 28;
```

#### Mudança 2: Padronização de Nomenclatura
**O que foi feito:**
- "EQUIPE FINANCENIRO" → "EQUIPE FINANCEIRO"
- "Administrativo" → "TIME ADMINISTRATIVO"

**SQL Executado:**
```sql
UPDATE crm_team SET name = 'EQUIPE FINANCEIRO' WHERE name = 'EQUIPE FINANCENIRO';
UPDATE crm_team SET name = 'TIME ADMINISTRATIVO' WHERE name = 'Administrativo';
```

#### Mudança 3: Configuração de Stages Bloqueados
**O que foi feito:**
- Adicionados 22 relacionamentos stage ↔ team
- 11 stages bloqueados agora permitem OPERACIONAL + FINANCEIRO

**Stages afetados (IDs):** 95, 96, 87, 93, 88, 82, 89, 91, 45, 90, 94

**SQL Executado:**
```sql
INSERT INTO crm_stage_crm_team_rel (crm_stage_id, crm_team_id)
VALUES (95, 9), (95, 14), (96, 9), (96, 14), (87, 9), (87, 14),
       (93, 9), (93, 14), (88, 9), (88, 14), (82, 9), (82, 14),
       (89, 9), (89, 14), (91, 9), (91, 14), (45, 9), (45, 14),
       (90, 9), (90, 14), (94, 9), (94, 14)
ON CONFLICT DO NOTHING;
```

### 2.2. Código Python

#### Mudança 4: Otimização do Campo stage_edit
**O que foi feito:**
- Adicionado `store=True` ao campo `stage_edit`
- Melhorada lógica: admin sempre pode editar
- Adicionado `tracking=True` ao campo `stage_id`
- Otimizado `@api.depends`
- Documentação completa adicionada

**Arquivo:** `/odoo/custom/addons_custom/crm_products/models/crm_stage.py`

---

## 3. PROCEDIMENTOS DE ROLLBACK

### 🔴 OPÇÃO A: Rollback Completo (Banco + Código)

Execute este procedimento se quiser voltar 100% ao estado anterior:

```bash
#!/bin/bash
# ROLLBACK COMPLETO - Banco de Dados + Código Python

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  ROLLBACK COMPLETO - OTIMIZAÇÕES CRM                               ║"
echo "╚════════════════════════════════════════════════════════════════════╝"

# 1. Parar Odoo
echo "⏸️  Parando Odoo..."
ssh odoo-rc "sudo systemctl stop odoo-server"
sleep 3

# 2. Restaurar arquivo Python original
echo "📄 Restaurando arquivo Python..."
ssh odoo-rc "sudo cp /odoo/custom/addons_custom/crm_products/models/crm_stage.py.backup_20251116 /odoo/custom/addons_custom/crm_products/models/crm_stage.py"
ssh odoo-rc "sudo chown odoo:odoo /odoo/custom/addons_custom/crm_products/models/crm_stage.py"

# 3. Rollback do banco de dados
echo "💾 Restaurando banco de dados..."
ssh odoo-rc "sudo -u postgres psql realcred" << 'EOF'
BEGIN;

-- Restaurar relação stage <-> teams
DELETE FROM crm_stage_crm_team_rel;
INSERT INTO crm_stage_crm_team_rel
SELECT * FROM crm_stage_crm_team_rel_backup_20251116;

-- Restaurar membros dos times
DELETE FROM crm_team_member;
INSERT INTO crm_team_member
SELECT * FROM crm_team_member_backup_20251116;

-- Restaurar times
UPDATE crm_team SET
    name = b.name,
    active = b.active
FROM crm_team_backup_20251116 b
WHERE crm_team.id = b.id;

-- Restaurar team_id nos leads
UPDATE crm_lead l SET
    team_id = b.team_id
FROM crm_lead_backup_20251116 b
WHERE l.id = b.id;

-- Restaurar sale_team_id nos usuários que foram alterados
UPDATE res_users
SET sale_team_id = 28
WHERE login = 'TESTES@semprereal.com';  -- Era o único alterado

COMMIT;

-- Verificar
SELECT 'Rollback concluído! Contagens:' as info;
SELECT 'crm_stage_crm_team_rel' as tabela, COUNT(*) as registros FROM crm_stage_crm_team_rel
UNION ALL
SELECT 'crm_team_member', COUNT(*) FROM crm_team_member
UNION ALL
SELECT 'crm_team ativos', COUNT(*) FROM crm_team WHERE active = true;
EOF

# 4. Limpar cache Python
echo "🧹 Limpando cache..."
ssh odoo-rc "sudo find /odoo/custom/addons_custom/crm_products -name '*.pyc' -delete 2>/dev/null || true"
ssh odoo-rc "sudo find /odoo/custom/addons_custom/crm_products -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true"

# 5. Atualizar módulo
echo "⚙️  Atualizando módulo..."
ssh odoo-rc "cd /odoo/odoo-server && sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d realcred --stop-after-init -u crm_products"

# 6. Reiniciar Odoo
echo "▶️  Reiniciando Odoo..."
ssh odoo-rc "sudo systemctl start odoo-server"

echo "✅ ROLLBACK COMPLETO FINALIZADO!"
```

### 🟡 OPÇÃO B: Rollback Apenas do Banco

Se quiser manter o código otimizado mas reverter as mudanças de configuração:

```sql
-- Executar no PostgreSQL
BEGIN;

-- 1. Reverter stages bloqueados (remover permissões adicionadas)
DELETE FROM crm_stage_crm_team_rel
WHERE crm_stage_id IN (95, 96, 87, 93, 88, 82, 89, 91, 45, 90, 94)
    AND crm_team_id IN (9, 14);  -- OPERACIONAL e FINANCEIRO

-- 2. Reverter nomenclatura
UPDATE crm_team SET name = 'EQUIPE FINANCENIRO' WHERE name = 'EQUIPE FINANCEIRO';
UPDATE crm_team SET name = 'Administrativo' WHERE name = 'TIME ADMINISTRATIVO';

-- 3. Reverter unificação de times
-- Restaurar membros
UPDATE crm_team_member SET crm_team_id = 28
WHERE user_id IN (
    SELECT uid FROM res_users
    WHERE login IN ('TESTES@semprereal.com', 'comercial20@semprereal.com', 'comercial22@semprereal.com')
);

-- Restaurar leads
UPDATE crm_lead l
SET team_id = b.team_id
FROM crm_lead_backup_20251116 b
WHERE l.id = b.id AND b.team_id = 28;

-- Reativar time 28
UPDATE crm_team
SET active = true, name = 'TIME JULIENE'
WHERE id = 28;

COMMIT;
```

### 🟢 OPÇÃO C: Rollback Apenas do Código Python

Se quiser manter as configurações do banco mas reverter o código:

```bash
# Restaurar arquivo original
sudo cp /odoo/custom/addons_custom/crm_products/models/crm_stage.py.backup_20251116 \
        /odoo/custom/addons_custom/crm_products/models/crm_stage.py

# Reiniciar
sudo systemctl restart odoo-server
```

---

## 4. VALIDAÇÃO PÓS-ROLLBACK

### 4.1. Verificar Contagens no Banco

```sql
-- Devem retornar aos valores originais
SELECT 'crm_stage_crm_team_rel' as tabela, COUNT(*) as atual, 56 as esperado
FROM crm_stage_crm_team_rel
UNION ALL
SELECT 'crm_team_member', COUNT(*), 139
FROM crm_team_member
UNION ALL
SELECT 'crm_team ativos', COUNT(*), 7  -- Incluindo o time 28 reativado
FROM crm_team WHERE active = true;
```

### 4.2. Verificar Times

```sql
-- Deve mostrar TIME JULIENE duplicado novamente
SELECT id, name, active,
       (SELECT COUNT(*) FROM crm_team_member WHERE crm_team_id = crm_team.id) as members
FROM crm_team
WHERE name LIKE '%JULIENE%'
ORDER BY id;

-- Resultado esperado:
--  id |     name     | active | members
-- ----+--------------+--------+---------
--   6 | TIME JULIENE | t      |      33
--  28 | TIME JULIENE | t      |       3
```

### 4.3. Verificar Stages Bloqueados

```sql
-- Devem mostrar 0 times permitidos novamente
SELECT id, name,
       (SELECT COUNT(*) FROM crm_stage_crm_team_rel WHERE crm_stage_id = crm_stage.id) as teams_count
FROM crm_stage
WHERE id IN (95, 96, 87, 93, 88, 82, 89, 91, 45, 90, 94);

-- Todos devem ter teams_count = 0
```

### 4.4. Verificar Código Python

```bash
# Ver primeira linha do arquivo
head -n 30 /odoo/custom/addons_custom/crm_products/models/crm_stage.py

# Deve mostrar código ORIGINAL (sem store=True, sem tracking, etc)
```

---

## 5. TROUBLESHOOTING

### Problema: Rollback não restaurou contagens corretas

**Causa:** Pode ter havido mudanças entre o backup e agora

**Solução:**
```sql
-- Comparar com backup
SELECT 'Atual' as fonte, COUNT(*) FROM crm_stage_crm_team_rel
UNION ALL
SELECT 'Backup', COUNT(*) FROM crm_stage_crm_team_rel_backup_20251116;
```

### Problema: Odoo não inicia após rollback

**Causa:** Erro no código Python ou cache corrupto

**Solução:**
```bash
# 1. Ver logs
sudo tail -100 /var/log/odoo/odoo-server.log

# 2. Limpar TODO o cache Python
sudo find /odoo -name '*.pyc' -delete
sudo find /odoo -type d -name '__pycache__' -exec rm -rf {} +

# 3. Reiniciar
sudo systemctl restart odoo-server
```

### Problema: Usuários reclamam de permissões após rollback

**Causa:** Campo stage_edit pode estar desatualizado

**Solução:**
```sql
-- Forçar recomputação (se código original não tem store=True, não precisa)
-- Apenas reiniciar Odoo deve resolver
```

---

## 6. CONTATO E SUPORTE

**Backups Criados Por:** Claude (AI Assistant)
**Data:** 16/11/2025
**Localização dos Backups:**
- Banco: Tabelas `*_backup_20251116` no PostgreSQL
- Código: `/odoo/custom/addons_custom/crm_products/models/crm_stage.py.backup_20251116`

**Em caso de problemas:**
1. Consultar esta documentação
2. Verificar logs: `/var/log/odoo/odoo-server.log`
3. Executar queries de validação (Seção 4)

---

## 7. RESUMO DE COMANDOS RÁPIDOS

### Rollback Total (Um comando)
```bash
curl -o /tmp/rollback.sh https://SEU_SERVIDOR/rollback.sh && bash /tmp/rollback.sh
```

### Verificação Rápida
```sql
-- Está no estado APÓS otimizações?
SELECT COUNT(*) FROM crm_team WHERE name = 'TIME JULIENE' AND active = true;
-- Se retorna 1 = estado NOVO (otimizado)
-- Se retorna 2 = estado ANTIGO (original)
```

---

**Status:** ✅ DOCUMENTAÇÃO COMPLETA DE ROLLBACK
**Testado:** ❌ Aguardando necessidade
**Pronto para Uso:** ✅ SIM
