# Estratégia de Limpeza de Dados Históricos - Odoo realcred

**Data:** 2025-11-15
**Objetivo:** Deletar dados criados até 31/12/2024
**Estimativa de Recuperação:** **20-60 GB**

---

## 🎯 ANÁLISE - DADOS ANTIGOS IDENTIFICADOS

### Resumo Executivo

| Tabela/Recurso | Total | Até 31/12/2024 | % Antigo | Espaço Estimado |
|----------------|-------|----------------|----------|-----------------|
| **ir_attachment** | 239,486 | **202,705** | **84.64%** | ~20 GB (DB) + ~60 GB (filestore) |
| **mail_message** | 2,798,843 | **2,402,245** | **85.83%** | ~1.5 GB |
| **crm_lead (inativos)** | 21,400 | 21,400 | **100%** | ~50 MB |
| **Filestore** | 74 GB | ~60 GB est. | ~80-85% | **60 GB** |

**Total Potencial:** **~80+ GB de recuperação!**

---

## ⚠️ AVISOS CRÍTICOS ANTES DE COMEÇAR

### 🔴 RISCOS

1. **Dados deletados não podem ser recuperados** (a menos que tenha backup)
2. **Foreign keys** - Deletar attachments pode quebrar referências
3. **Relatórios/Auditorias** - Dados históricos podem ser necessários legalmente
4. **Integridade Odoo** - Alguns attachments podem ser críticos (logos, templates)

### ✅ PROTEÇÕES OBRIGATÓRIAS

1. **BACKUP COMPLETO** antes de qualquer deleção
2. **Testar em PEQUENO LOTE** primeiro (100-1000 registros)
3. **Verificar integridade** após cada etapa
4. **Manter logs** de tudo que foi deletado
5. **Executar fora de horário de pico**

---

## 📋 ESTRATÉGIA SEGURA - 5 FASES

### FASE 0: PREPARAÇÃO (OBRIGATÓRIA)

#### 1. Backup Completo
```bash
# 1. Backup do database
sudo -u postgres pg_dump -Fc realcred > ~/backup_before_cleanup_$(date +%Y%m%d).dump

# 2. Backup do filestore
sudo tar -czf ~/filestore_backup_$(date +%Y%m%d).tar.gz /odoo/filestore/

# 3. Verificar backups
ls -lh ~/backup_before_cleanup_*
ls -lh ~/filestore_backup_*

# 4. Testar restauração (CRÍTICO!)
sudo -u postgres pg_restore -l ~/backup_before_cleanup_*.dump | head -20
```

**IMPORTANTE:** Não prossiga sem backup verificado!

#### 2. Criar Tabela de Log
```sql
-- Tabela para registrar o que foi deletado
CREATE TABLE IF NOT EXISTS deleted_records_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    record_id INTEGER,
    record_info JSONB,
    deleted_at TIMESTAMP DEFAULT NOW(),
    deleted_by VARCHAR(50) DEFAULT 'cleanup_script'
);
```

---

### FASE 1: LIMPEZA DE ATTACHMENTS (MAIOR IMPACTO)

**Recuperação Estimada:** 20 GB (DB) + 60 GB (filestore) = **80 GB total**

#### Estratégia Incremental Segura

##### 1.1. Identificar Attachments Seguros para Deletar

**SAFE TO DELETE:**
- ✅ Attachments de emails antigos
- ✅ Attachments de leads/oportunidades perdidas
- ✅ Logs e relatórios temporários
- ✅ Imagens antigas de chat
- ✅ Documentos de processos concluídos

**NUNCA DELETAR:**
- ❌ Attachments de res.company (logos, configs)
- ❌ Templates de email/relatório
- ❌ Documentos fiscais (NFe, boletos) - **OBRIGAÇÃO LEGAL!**
- ❌ Contratos ativos
- ❌ Documentos de RH (admissão, férias)

##### 1.2. Query para Identificar Attachments Seguros

```sql
-- Ver attachments antigos por modelo
SELECT
    res_model,
    COUNT(*) as total,
    pg_size_pretty(SUM(file_size::bigint)) as total_size
FROM ir_attachment
WHERE create_date <= '2024-12-31'
  AND res_model IS NOT NULL
GROUP BY res_model
ORDER BY COUNT(*) DESC
LIMIT 20;
```

##### 1.3. Teste em PEQUENO LOTE (100 registros)

```sql
-- TESTE: Deletar apenas 100 attachments de emails antigos
WITH old_mail_attachments AS (
    SELECT id, name, res_id, res_model, store_fname
    FROM ir_attachment
    WHERE create_date <= '2024-12-31'
      AND res_model = 'mail.message'
      AND create_date < '2024-01-01'  -- Só de 2023 ou antes
    LIMIT 100
)
-- Log antes de deletar
INSERT INTO deleted_records_log (table_name, record_id, record_info)
SELECT
    'ir_attachment',
    id,
    jsonb_build_object('name', name, 'model', res_model, 'res_id', res_id, 'file', store_fname)
FROM old_mail_attachments;

-- Deletar
DELETE FROM ir_attachment
WHERE id IN (SELECT id FROM old_mail_attachments);

-- Verificar
SELECT COUNT(*) FROM deleted_records_log WHERE table_name = 'ir_attachment';
```

**Após teste:** Verificar Odoo funciona normalmente por 24h!

##### 1.4. Limpeza em Lotes (APÓS TESTE BEM-SUCEDIDO)

```sql
-- Deletar attachments de emails antigos em lotes de 1000
DO $$
DECLARE
    deleted_count INTEGER;
    total_deleted INTEGER := 0;
    batch_size INTEGER := 1000;
BEGIN
    LOOP
        -- Log + Delete em lotes
        WITH to_delete AS (
            SELECT id, name, res_id, res_model, store_fname
            FROM ir_attachment
            WHERE create_date <= '2024-12-31'
              AND res_model = 'mail.message'
              AND id NOT IN (SELECT record_id FROM deleted_records_log WHERE table_name = 'ir_attachment')
            LIMIT batch_size
        )
        INSERT INTO deleted_records_log (table_name, record_id, record_info)
        SELECT
            'ir_attachment',
            id,
            jsonb_build_object('name', name, 'model', res_model, 'res_id', res_id, 'file', store_fname)
        FROM to_delete;

        GET DIAGNOSTICS deleted_count = ROW_COUNT;

        EXIT WHEN deleted_count = 0;

        DELETE FROM ir_attachment
        WHERE id IN (
            SELECT record_id::integer
            FROM deleted_records_log
            WHERE table_name = 'ir_attachment'
              AND id > (total_deleted)
            LIMIT batch_size
        );

        total_deleted := total_deleted + deleted_count;

        RAISE NOTICE 'Deleted % attachments, total: %', deleted_count, total_deleted;

        -- Pause entre lotes para não sobrecarregar
        PERFORM pg_sleep(2);
    END LOOP;

    RAISE NOTICE 'COMPLETED: Total deleted: %', total_deleted;
END $$;
```

##### 1.5. Limpar Filestore Órfãos

Depois de deletar do DB, limpar arquivos físicos:

```bash
#!/bin/bash
# Script: cleanup_orphan_files.sh

echo "Obtendo lista de arquivos válidos do database..."
sudo -u postgres psql realcred -t -c "
SELECT store_fname
FROM ir_attachment
WHERE store_fname IS NOT NULL
" > /tmp/valid_files.txt

echo "Encontrando arquivos órfãos no filestore..."
cd /odoo/filestore/realcred

# Criar lista de arquivos para deletar
find . -type f | while read file; do
    basename=$(basename "$file")
    if ! grep -q "$basename" /tmp/valid_files.txt; then
        echo "$file"
    fi
done > /tmp/orphan_files.txt

echo "Arquivos órfãos encontrados: $(wc -l < /tmp/orphan_files.txt)"
echo "Espaço a recuperar: $(du -ch $(cat /tmp/orphan_files.txt) | tail -1)"

# TESTAR PRIMEIRO: Mover para pasta temporária ao invés de deletar
mkdir -p /tmp/orphan_backup
cat /tmp/orphan_files.txt | xargs -I {} mv {} /tmp/orphan_backup/

# Após 1 semana sem problemas, deletar:
# rm -rf /tmp/orphan_backup
```

---

### FASE 2: LIMPEZA DE MENSAGENS (mail_message)

**Recuperação Estimada:** ~1.5 GB

#### 2.1. Identificar Mensagens Antigas Seguras

```sql
-- Análise de mensagens antigas por tipo
SELECT
    message_type,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE date <= '2024-12-31') as old_count
FROM mail_message
GROUP BY message_type
ORDER BY old_count DESC;
```

#### 2.2. Deletar Mensagens de Notificação Antigas

```sql
-- Teste: 1000 mensagens de notificação antigas
WITH old_notifications AS (
    SELECT id, subject, model, res_id
    FROM mail_message
    WHERE date <= '2024-12-31'
      AND message_type = 'notification'
      AND date < '2024-01-01'
    LIMIT 1000
)
-- Log
INSERT INTO deleted_records_log (table_name, record_id, record_info)
SELECT
    'mail_message',
    id,
    jsonb_build_object('subject', subject, 'model', model, 'res_id', res_id)
FROM old_notifications;

-- Deletar
DELETE FROM mail_message WHERE id IN (SELECT id FROM old_notifications);
```

#### 2.3. Limpeza em Lotes

```sql
-- Deletar em lotes de 5000 (mensagens de notificação antigas)
DO $$
DECLARE
    batch_size INTEGER := 5000;
    total_deleted INTEGER := 0;
    deleted_count INTEGER;
BEGIN
    LOOP
        DELETE FROM mail_message
        WHERE id IN (
            SELECT id
            FROM mail_message
            WHERE date <= '2024-12-31'
              AND message_type = 'notification'
            LIMIT batch_size
        );

        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        EXIT WHEN deleted_count = 0;

        total_deleted := total_deleted + deleted_count;
        RAISE NOTICE 'Deleted % messages, total: %', deleted_count, total_deleted;

        PERFORM pg_sleep(2);
    END LOOP;
END $$;
```

---

### FASE 3: ARQUIVAR LEADS ANTIGOS (ao invés de deletar)

**Melhor Prática:** Arquivar ao invés de deletar (dados de CRM são valiosos!)

#### 3.1. Desativar Leads Perdidos Antigos

```sql
-- Marcar como inativos ao invés de deletar
UPDATE crm_lead
SET active = false
WHERE create_date <= '2024-12-31'
  AND (probability = 0 OR stage_id IN (SELECT id FROM crm_stage WHERE is_won = false));

-- Resultado esperado: 21,400 leads arquivados
```

**IMPORTANTE:** Não deletar leads! Mantenha no banco mas inativos.

---

### FASE 4: OUTRAS TABELAS

#### 4.1. Logs Antigos

```sql
-- Deletar logs de requisições antigas
DELETE FROM json_request_log
WHERE create_date <= '2024-12-31';

-- Deletar tracking de website antigo
DELETE FROM website_track
WHERE visit_datetime <= '2024-12-31';

-- Deletar mensagens do bus antigas
DELETE FROM bus_bus
WHERE create_date <= '2024-12-31';
```

#### 4.2. Dados de Chat

```sql
-- Chat messages antigos (se não forem críticos)
DELETE FROM acrux_chat_message
WHERE date_message <= '2024-12-31'
  AND conversation_id IN (
      SELECT id FROM acrux_chat_conversation
      WHERE status = 'done' OR status = 'closed'
  );
```

---

### FASE 5: MANUTENÇÃO PÓS-LIMPEZA

#### 5.1. Vacuum Full (Recuperar Espaço)

```bash
# Agendar para fim de semana
sudo systemctl stop odoo-server
sudo -u postgres psql realcred -c "VACUUM FULL VERBOSE;"
sudo systemctl start odoo-server
```

#### 5.2. Reindex

```bash
sudo -u postgres psql realcred -c "REINDEX DATABASE realcred;"
```

#### 5.3. Atualizar Estatísticas

```bash
sudo -u postgres psql realcred -c "ANALYZE VERBOSE;"
```

---

## 📊 SCRIPT COMPLETO - EXECUÇÃO RECOMENDADA

### Script Mestre (Executar em Etapas!)

```bash
#!/bin/bash
# cleanup_old_data.sh - Executar SOMENTE após backup!

set -e  # Para em caso de erro

echo "========================================="
echo "LIMPEZA DE DADOS ANTIGOS - realcred"
echo "Data limite: 2024-12-31"
echo "========================================="

# Verificar backup
if [ ! -f ~/backup_before_cleanup_*.dump ]; then
    echo "❌ ERRO: Backup não encontrado! Execute backup primeiro!"
    exit 1
fi

echo "✅ Backup encontrado"

# FASE 1: Teste pequeno (100 attachments de emails)
echo ""
echo "FASE 1: Teste - Deletando 100 attachments de emails antigos..."
sudo -u postgres psql realcred << 'EOF'
WITH old_mail_attachments AS (
    SELECT id
    FROM ir_attachment
    WHERE create_date <= '2023-12-31'
      AND res_model = 'mail.message'
    LIMIT 100
)
DELETE FROM ir_attachment
WHERE id IN (SELECT id FROM old_mail_attachments);

SELECT 'Deletados: ' || COUNT(*) FROM old_mail_attachments;
EOF

echo "✅ Fase 1 completa. Verificar Odoo funciona normalmente."
echo "   Aguardar 24h antes de continuar!"

read -p "Continuar com Fase 2? (s/N): " continue
if [ "$continue" != "s" ]; then
    echo "Abortado pelo usuário"
    exit 0
fi

# FASE 2: Deletar mensagens de notificação antigas
echo ""
echo "FASE 2: Deletando mensagens de notificação antigas..."
sudo -u postgres psql realcred << 'EOF'
DELETE FROM mail_message
WHERE date <= '2024-12-31'
  AND message_type = 'notification';
EOF

echo "✅ Fase 2 completa"

# FASE 3: Arquivar leads
echo ""
echo "FASE 3: Arquivando leads perdidos antigos..."
sudo -u postgres psql realcred << 'EOF'
UPDATE crm_lead
SET active = false
WHERE create_date <= '2024-12-31'
  AND probability = 0;
EOF

echo "✅ Fase 3 completa"

# FASE 4: Vacuum e Reindex
echo ""
echo "FASE 4: Vacuum e Reindex (pode demorar!)..."
sudo systemctl stop odoo-server
sudo -u postgres psql realcred -c "VACUUM FULL VERBOSE;"
sudo -u postgres psql realcred -c "REINDEX DATABASE realcred;"
sudo -u postgres psql realcred -c "ANALYZE VERBOSE;"
sudo systemctl start odoo-server

echo "✅ LIMPEZA COMPLETA!"
echo ""
echo "Verificar tamanho final:"
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('realcred'));"
```

---

## 🔍 MONITORAMENTO E VALIDAÇÃO

### Antes da Limpeza
```sql
-- Capturar estatísticas iniciais
CREATE TABLE cleanup_stats_before AS
SELECT
    'ir_attachment' as table_name,
    COUNT(*) as records,
    pg_total_relation_size('ir_attachment') as size_bytes,
    pg_size_pretty(pg_total_relation_size('ir_attachment')) as size_pretty
UNION ALL
SELECT
    'mail_message',
    COUNT(*),
    pg_total_relation_size('mail_message'),
    pg_size_pretty(pg_total_relation_size('mail_message'))
FROM mail_message;

SELECT * FROM cleanup_stats_before;
```

### Após Limpeza
```sql
-- Comparar resultados
WITH after_stats AS (
    SELECT
        'ir_attachment' as table_name,
        COUNT(*) as records,
        pg_total_relation_size('ir_attachment') as size_bytes
    FROM ir_attachment
    UNION ALL
    SELECT
        'mail_message',
        COUNT(*),
        pg_total_relation_size('mail_message')
    FROM mail_message
)
SELECT
    b.table_name,
    b.records as records_before,
    a.records as records_after,
    b.records - a.records as records_deleted,
    b.size_pretty as size_before,
    pg_size_pretty(a.size_bytes) as size_after,
    pg_size_pretty(b.size_bytes - a.size_bytes) as space_freed
FROM cleanup_stats_before b
JOIN after_stats a ON b.table_name = a.table_name;
```

---

## ⚠️ CHECKLIST DE SEGURANÇA

### Antes de Executar
- [ ] Backup completo do database realizado
- [ ] Backup do filestore realizado
- [ ] Teste de restauração verificado
- [ ] Tabela de log criada
- [ ] Usuários notificados (manutenção programada)
- [ ] Janela de manutenção agendada (fim de semana)

### Durante Execução
- [ ] Executar em lotes pequenos
- [ ] Monitorar logs do Odoo
- [ ] Verificar espaço em disco
- [ ] Pause entre lotes (não sobrecarregar)

### Após Execução
- [ ] Verificar Odoo funciona normalmente
- [ ] Testar funcionalidades principais
- [ ] Verificar relatórios
- [ ] VACUUM FULL executado
- [ ] REINDEX executado
- [ ] Estatísticas comparadas
- [ ] Manter backup por 30 dias

---

## 📈 ESTIMATIVA DE RESULTADOS

### Recuperação Esperada

| Fase | Componente | Espaço Atual | Espaço Deletado | Espaço Final |
|------|------------|--------------|-----------------|--------------|
| 1 | ir_attachment (DB) | 3.6 GB | ~3 GB | ~600 MB |
| 1 | Filestore | 74 GB | ~60 GB | ~14 GB |
| 2 | mail_message | 1.7 GB | ~1.5 GB | ~200 MB |
| 3 | CRM leads | 78 MB | 0 (arquivados) | 78 MB |
| 4 | Outros | ~500 MB | ~300 MB | ~200 MB |
| **TOTAL** | **~80 GB** | **~65 GB** | **~15 GB** |

**Database:** 8.8 GB → ~2 GB (redução de 77%!)
**Filestore:** 74 GB → ~14 GB (redução de 81%!)

---

## 🚨 TROUBLESHOOTING

### Erro: Foreign Key Violation
```
ERROR: update or delete on table "X" violates foreign key constraint
```

**Solução:** Deletar tabelas dependentes primeiro:
```sql
-- Identificar dependências
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE confrelid = 'ir_attachment'::regclass;

-- Deletar mail_notification primeiro, depois ir_attachment
```

### Erro: Disk Space
```
ERROR: could not extend file: No space left on device
```

**Solução:**
1. Limpar /tmp/
2. Executar em lotes menores
3. Fazer VACUUM incremental

### Odoo Lento Após Limpeza
**Solução:**
```sql
VACUUM ANALYZE VERBOSE;
REINDEX DATABASE realcred;
```

---

## 📞 SUPORTE E ROLLBACK

### Se Algo Der Errado

**Restaurar Backup Completo:**
```bash
# 1. Parar Odoo
sudo systemctl stop odoo-server

# 2. Restaurar database
sudo -u postgres dropdb realcred
sudo -u postgres createdb -O odoo realcred
sudo -u postgres pg_restore -d realcred ~/backup_before_cleanup_*.dump

# 3. Restaurar filestore
sudo rm -rf /odoo/filestore/*
sudo tar -xzf ~/filestore_backup_*.tar.gz -C /

# 4. Corrigir permissões
sudo chown -R odoo:odoo /odoo/filestore

# 5. Reiniciar Odoo
sudo systemctl start odoo-server
```

---

## 🎯 RECOMENDAÇÃO FINAL

### Abordagem Conservadora (Recomendada)

1. **Semana 1:** Testar com 1000 registros
2. **Semana 2:** Deletar attachments de emails (50% dos dados)
3. **Semana 3:** Deletar mensagens antigas
4. **Semana 4:** Limpar filestore órfãos
5. **Semana 5:** VACUUM FULL (fim de semana)

### Abordagem Agressiva (Maior Risco)

Executar tudo em um fim de semana com backup completo.

**Minha Recomendação:** **Abordagem Conservadora** - Segurança > Velocidade!

---

**Criado:** 2025-11-15
**Status:** Pronto para execução (APÓS BACKUP!)
**Estimativa:** 65-80 GB de recuperação potencial
