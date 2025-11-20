# 🐘 PostgreSQL Mastery - Conhecimento Profundo para Odoo

> **Última Pesquisa:** 2025-11-17
> **Fontes:** PostgreSQL Official Docs, EDB, Percona, Crunchy Data, MyDBOps
> **Nível:** Enterprise-Grade Production

---

## 📊 ÍNDICE

1. [Performance Tuning](#performance-tuning)
2. [Replicação](#replicação)
3. [Backup & Disaster Recovery](#backup--disaster-recovery)
4. [Indexes Optimization](#indexes-optimization)
5. [VACUUM & Bloat Management](#vacuum--bloat-management)
6. [Configuração para Odoo](#configuração-para-odoo)

---

## ⚡ PERFORMANCE TUNING

### Parâmetros Críticos de Memória

#### 1. shared_buffers

**O que é:**
Determina quanta memória é dedicada ao servidor para caching de dados.

**Recomendações 2025:**
```ini
# Conservative (Odoo Small - até 50 usuários)
shared_buffers = 2GB            # 25% de 8GB RAM

# Moderate (Odoo Medium - 50-200 usuários)
shared_buffers = 4GB            # 25% de 16GB RAM

# Aggressive (Odoo Large - 200+ usuários)
shared_buffers = 16GB           # 25% de 64GB RAM

# Maximum (não ultrapassar!)
shared_buffers = 40% da RAM     # Limite máximo recomendado
```

**Regra de Ouro:**
- **25-40% da RAM total**
- Nunca mais que 40% (performance degrada!)
- Em servidores dedicados: 25% é o sweet spot

**Por que não mais que 40%?**
- PostgreSQL usa cache do OS (page cache)
- Duplicar cache = desperdício
- OS precisa de memória para outros processos

---

#### 2. work_mem

**O que é:**
Memória usada para operações de sort e hash tables ANTES de gravar em disco temporário.

**Recomendações 2025:**
```ini
# Low concurrency (batch jobs, reports)
work_mem = 256MB                # Poucos queries complexos

# Medium concurrency (Odoo typical)
work_mem = 50MB                 # Default para Odoo

# High concurrency (muitos usuários simples)
work_mem = 16MB                 # Muitos queries simultâneos
```

**CUIDADO! 🚨**
- **Cada query pode usar work_mem MÚLTIPLAS VEZES!**
- Query com 3 sorts = 3 * work_mem
- 100 conexões * 50MB = 5GB potencial!

**Cálculo Seguro:**
```
work_mem = (RAM disponível) / (max_connections * avg_sorts_per_query)

Exemplo para Odoo:
- RAM: 16GB
- max_connections: 200
- avg_sorts: 2-3

work_mem = 16GB / (200 * 3) = ~27MB
Arredondar para: 50MB (com margem)
```

**Como saber se precisa aumentar:**
```sql
-- Queries usando temp files (BAD!)
SELECT datname, temp_files, temp_bytes
FROM pg_stat_database
WHERE temp_files > 0;

-- Se temp_files > 0 → Aumentar work_mem!
```

---

#### 3. effective_cache_size

**O que é:**
Estimativa de quanta memória está disponível para cache (PostgreSQL + OS).

**NÃO aloca memória!** Apenas ajuda o planner a decidir.

**Recomendações 2025:**
```ini
# Conservative
effective_cache_size = 8GB      # 50% de 16GB RAM

# Moderate
effective_cache_size = 12GB     # 75% de 16GB RAM

# Aggressive (servidor dedicado)
effective_cache_size = 48GB     # 75% de 64GB RAM
```

**Regra de Ouro:**
- **50-75% da RAM total**
- Servidores dedicados: 75%
- Servidores compartilhados: 50%

**Relação com shared_buffers:**
```
effective_cache_size INCLUI shared_buffers!

Exemplo:
- RAM total: 16GB
- shared_buffers: 4GB
- OS cache estimado: 8GB
- effective_cache_size = 4GB + 8GB = 12GB (75% RAM)
```

---

### Parâmetros de Conexões

#### max_connections

**Para Odoo:**
```ini
# Fórmula: (usuários * 2) + workers + 10
# Odoo usa 2 conexões por usuário (http + longpolling)

# Small (50 users)
max_connections = 120           # 50*2 + 10 workers + 10

# Medium (100 users)
max_connections = 220           # 100*2 + 10 + 10

# Large (200 users)
max_connections = 420           # 200*2 + 10 + 10
```

**Trade-off:**
- Mais connections = mais overhead
- Mas Odoo precisa de conexões suficientes
- Use connection pooling (pgBouncer) se > 300

---

### Parâmetros de Checkpoint

**O que são checkpoints:**
Pontos onde PostgreSQL grava todas as mudanças em memória para disco.

```ini
# Produção Odoo (transações moderadas)
checkpoint_timeout = 15min              # Default: 5min
checkpoint_completion_target = 0.9      # Spread I/O over 90% of timeout
max_wal_size = 4GB                      # Default: 1GB
min_wal_size = 1GB                      # Default: 80MB

# High-write Odoo (muitas transações)
checkpoint_timeout = 30min
max_wal_size = 8GB
min_wal_size = 2GB
```

**Por que isso importa:**
- Checkpoints frequentes = I/O spikes
- Checkpoints raros = recovery lento
- Sweet spot: 15-30min para Odoo

---

### Parâmetros de WAL (Write-Ahead Log)

```ini
# Produção
wal_buffers = 16MB                      # Default: -1 (auto = 1/32 shared_buffers)
wal_writer_delay = 200ms                # Default: 200ms

# High-write
wal_buffers = 32MB
wal_writer_delay = 10ms                 # Flush mais frequente
```

---

### Parâmetros de Query Planning

```ini
# SSD (não HDD!)
random_page_cost = 1.1                  # Default: 4.0 (para HDD!)
seq_page_cost = 1.0                     # Default: 1.0

# Planner agressivo (mais otimizações)
default_statistics_target = 100         # Default: 100
effective_io_concurrency = 200          # Para SSD
max_parallel_workers_per_gather = 4     # Parallel queries
```

**IMPORTANTE para Odoo:**
- **random_page_cost = 1.1** é CRÍTICO em SSD!
- Default 4.0 é para HDD (década de 2000!)
- Com 4.0, planner evita índices (acha que scan é mais rápido)

---

## 🔄 REPLICAÇÃO

### Tipos de Replicação (2025)

#### 1. Streaming Replication (Física)

**O que é:**
Replica TODA a instância PostgreSQL byte-a-byte.

**Tipos:**

##### Asynchronous (Padrão)
```ini
# Primary
wal_level = replica
max_wal_senders = 10
wal_keep_size = 1GB

# Standby
hot_standby = on
primary_conninfo = 'host=primary port=5432'
```

**Prós:**
- ✅ Baixo overhead (no wait)
- ✅ Simples de configurar
- ✅ Robusto para failover automático

**Contras:**
- ❌ Pode perder transações (lag)
- ❌ Standby pode ficar desatualizado

**Quando usar:**
- Alta disponibilidade (HA)
- Read replicas para reports
- Disaster recovery (DR)

---

##### Synchronous (Síncrona)
```ini
# Primary
synchronous_commit = on
synchronous_standby_names = 'standby1'

# Standby
(mesma config que async)
```

**Prós:**
- ✅ Zero data loss
- ✅ Standby SEMPRE atualizado

**Contras:**
- ❌ Latência alta (wait for ACK)
- ❌ Primary para se standby cair
- ❌ Performance impacto (~20-30%)

**Quando usar:**
- Dados críticos (financeiro, saúde)
- Compliance (zero perda)
- **NÃO para Odoo típico** (async é suficiente)

---

#### 2. Logical Replication

**O que é:**
Replica mudanças a nível de tabela (não byte-a-byte).

```sql
-- Publisher (Primary)
CREATE PUBLICATION my_pub FOR TABLE users, orders;

-- Subscriber (Standby)
CREATE SUBSCRIPTION my_sub
CONNECTION 'host=primary dbname=odoo'
PUBLICATION my_pub;
```

**Prós:**
- ✅ Replicar apenas tabelas específicas
- ✅ Subscribers podem receber de múltiplos publishers
- ✅ Diferentes versões PostgreSQL
- ✅ Filtros (WHERE clause)

**Contras:**
- ❌ Overhead maior
- ❌ Mais complexo
- ❌ DDL não replica (CREATE TABLE, etc)

**Quando usar para Odoo:**
- Replicar apenas `crm_lead`, `sale_order` para analytics
- Enviar dados para Data Warehouse
- Multi-tenant com segregação

---

### Configuração de Replicação para Odoo

**Cenário Típico: Primary + 1 Standby Async**

#### Primary (odoo-rc):
```ini
# postgresql.conf
wal_level = replica
max_wal_senders = 5                     # 1 standby + 3 reserve
wal_keep_size = 2GB                     # 2GB de WAL retido
hot_standby = on
archive_mode = on
archive_command = 'rsync -a %p standby:/var/lib/postgresql/archive/%f'
```

```
# pg_hba.conf
# Permitir replicação do standby
host    replication    replicator    10.158.0.6/32    scram-sha-256
```

#### Standby (odoo-standby):
```ini
# postgresql.conf
hot_standby = on
```

```
# standby.signal (arquivo vazio - marca como standby)
touch /var/lib/postgresql/15/main/standby.signal
```

```
# postgresql.auto.conf
primary_conninfo = 'host=10.158.0.5 port=5432 user=replicator password=XXX'
primary_slot_name = 'standby_slot'
```

**Setup:**
```bash
# No standby
pg_basebackup -h 10.158.0.5 -D /var/lib/postgresql/15/main -U replicator -P -R
```

---

### Monitoring Replication

```sql
-- No Primary: Ver standbys conectados
SELECT * FROM pg_stat_replication;

-- Ver lag (bytes)
SELECT
    client_addr,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn)) AS lag
FROM pg_stat_replication;

-- No Standby: Ver lag (tempo)
SELECT
    now() - pg_last_xact_replay_timestamp() AS replication_lag;
```

**Alertas:**
- Lag > 1GB → Investigar rede/disco standby
- Lag > 10 minutes → Crítico!

---

## 💾 BACKUP & DISASTER RECOVERY

### Estratégias de Backup (2025)

#### 1. pg_dump (Logical Backup)

**O que é:**
Backup lógico (SQL) de um database.

```bash
# Dump completo (formato custom - comprimido)
pg_dump -Fc -f backup_$(date +%Y%m%d).dump realcred

# Dump apenas schema
pg_dump -Fc -s -f schema.dump realcred

# Dump apenas data
pg_dump -Fc -a -f data.dump realcred

# Dump paralelo (4 jobs - 4x mais rápido!)
pg_dump -Fd -j 4 -f backup_dir/ realcred
```

**Restore:**
```bash
# Restore custom format
pg_restore -d realcred_new backup.dump

# Restore paralelo
pg_restore -d realcred_new -j 4 backup_dir/
```

**Prós:**
- ✅ Portável (qualquer PostgreSQL)
- ✅ Seletivo (tables específicas)
- ✅ Comprimido automaticamente

**Contras:**
- ❌ Lento para DBs grandes (>100GB)
- ❌ Locks tables durante dump
- ❌ Não permite PITR

**Quando usar:**
- Backup diário "snapshot"
- Migração entre versões PostgreSQL
- Odoo típico (<100GB)

---

#### 2. pg_basebackup (Physical Backup)

**O que é:**
Backup físico (cópia byte-a-byte) do cluster inteiro.

```bash
# Backup completo
pg_basebackup -h localhost -D /backup/base -Ft -z -P

# Backup incremental (PostgreSQL 17+)
pg_basebackup -h localhost -D /backup/incr --incremental=/backup/base/backup_manifest
```

**Prós:**
- ✅ Muito mais rápido que pg_dump
- ✅ Permite PITR (com WAL archiving)
- ✅ Backup do cluster inteiro

**Contras:**
- ❌ Mesma versão PostgreSQL
- ❌ Restaura tudo (não seletivo)
- ❌ Maior espaço (sem compressão SQL)

**Quando usar:**
- Databases grandes (>100GB)
- Disaster recovery com PITR
- Base para replicação

---

#### 3. PITR (Point-in-Time Recovery)

**O que é:**
Restaurar database para qualquer momento no tempo.

**Setup:**
```ini
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /mnt/archive/%f'
# Ou para S3:
# archive_command = 'aws s3 cp %p s3://bucket/wal/%f'
```

**Backup:**
```bash
# 1. Base backup
pg_basebackup -D /backup/base -Ft -z -X fetch

# 2. WAL files continuamente arquivados via archive_command
# (automático!)
```

**Restore para 2025-11-17 14:30:**
```bash
# 1. Restore base backup
tar -xzf /backup/base/base.tar.gz -C /var/lib/postgresql/15/main

# 2. Criar recovery.signal
touch /var/lib/postgresql/15/main/recovery.signal

# 3. Configurar recovery
cat > /var/lib/postgresql/15/main/postgresql.auto.conf <<EOF
restore_command = 'cp /mnt/archive/%f %p'
recovery_target_time = '2025-11-17 14:30:00'
recovery_target_action = 'promote'
EOF

# 4. Start PostgreSQL
systemctl start postgresql
# Vai restaurar até 14:30 e depois promover para primary
```

**Prós:**
- ✅ Recover para QUALQUER momento
- ✅ Proteção contra erro humano (DROP TABLE!)
- ✅ Compliance (audit trail)

**Contras:**
- ❌ Complexo de configurar
- ❌ Requer armazenamento para WALs (muitos GB/dia)
- ❌ Recovery pode ser demorado

**Quando usar para Odoo:**
- Produção crítica
- Compliance (LGPD, SOX)
- Proteção contra ransomware

---

### Ferramentas Enterprise (2025)

#### pgBackRest

```bash
# Instalação
sudo apt install pgbackrest

# Config
cat > /etc/pgbackrest/pgbackrest.conf <<EOF
[global]
repo1-path=/backup/pgbackrest
repo1-retention-full=7
process-max=4
log-level-console=info

[realcred]
pg1-path=/var/lib/postgresql/15/main
EOF

# Backup full
pgbackrest --stanza=realcred backup --type=full

# Backup incremental
pgbackrest --stanza=realcred backup --type=incr

# Backup diferencial
pgbackrest --stanza=realcred backup --type=diff

# Restore
pgbackrest --stanza=realcred restore
```

**Features:**
- ✅ Full + Incremental + Differential
- ✅ Parallel processing
- ✅ Encryption (AES-256)
- ✅ Compression (gzip, lz4, zstd)
- ✅ S3, Azure, GCS support
- ✅ PITR nativo
- ✅ Backup validation

**Recomendado para Odoo Produção!**

---

#### Barman (Backup and Recovery Manager)

```bash
# Instalação
sudo apt install barman

# Config
cat > /etc/barman.d/realcred.conf <<EOF
[realcred]
description = "Odoo Production"
conninfo = host=localhost user=barman dbname=realcred
backup_method = rsync
reuse_backup = link
backup_options = concurrent_backup
retention_policy = RECOVERY WINDOW OF 7 DAYS
EOF

# Backup
barman backup realcred

# List backups
barman list-backup realcred

# Restore
barman recover realcred latest /var/lib/postgresql/15/main
```

**Features:**
- ✅ Disaster recovery focused
- ✅ Remote backups
- ✅ PITR
- ✅ Parallel operations
- ✅ Compression
- ✅ Retention policies

---

### Estratégia Recomendada para Odoo (2025)

**Small/Medium (<100GB):**
```
Daily:    pg_dump -Fc (compressed custom format)
Archive:  7 daily + 4 weekly + 12 monthly
Storage:  Local + S3 (offsite)
```

**Large (>100GB):**
```
Daily:    pgBackRest full backup
Hourly:   pgBackRest incremental
WAL:      Continuous archiving to S3
PITR:     Enabled (recover to any point)
Retention: 7 days full + 30 days WAL
```

**Script Exemplo (pg_dump daily):**
```bash
#!/bin/bash
# /usr/local/bin/odoo-backup.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR=/backup/odoo
S3_BUCKET=s3://realcred-backups

# Dump
pg_dump -Fc -f $BACKUP_DIR/realcred_$DATE.dump realcred

# Compress (se não usar -Fc)
# gzip $BACKUP_DIR/realcred_$DATE.dump

# Upload S3
aws s3 cp $BACKUP_DIR/realcred_$DATE.dump $S3_BUCKET/

# Cleanup local (manter 7 dias)
find $BACKUP_DIR -name "*.dump" -mtime +7 -delete

# Cleanup S3 (lifecycle policy no bucket)
```

**Cron:**
```
0 2 * * * /usr/local/bin/odoo-backup.sh
```

---

## 🔍 INDEXES OPTIMIZATION

### Tipos de Índices (2025)

#### 1. B-tree (Padrão)

**Quando usar:**
- Igualdade (`=`)
- Comparação (`<`, `>`, `<=`, `>=`)
- Range (`BETWEEN`)
- Ordenação (`ORDER BY`)
- Pattern matching (`LIKE 'abc%'`)

**Odoo Típico:**
```sql
-- Busca por CPF
CREATE INDEX idx_partner_cpf ON res_partner(cpf);

-- Busca por nome (case-insensitive)
CREATE INDEX idx_partner_name_lower ON res_partner(LOWER(name));

-- Range de datas
CREATE INDEX idx_lead_create_date ON crm_lead(create_date);
```

**Características:**
- ✅ Versatile (90% dos casos)
- ✅ Suporta unique
- ✅ Boa performance geral
- ❌ Não eficiente para arrays, full-text

---

#### 2. GIN (Generalized Inverted Index)

**Quando usar:**
- Arrays (`ANY`, `ALL`, `@>`)
- JSONB
- Full-text search
- Trigram search (`pg_trgm`)

**Odoo Típico:**
```sql
-- Full-text search em descrição
CREATE INDEX idx_product_description_gin
ON product_template
USING GIN (to_tsvector('portuguese', description));

-- Busca em JSONB
CREATE INDEX idx_lead_metadata_gin
ON crm_lead
USING GIN (metadata jsonb_path_ops);

-- Trigram para busca fuzzy
CREATE EXTENSION pg_trgm;
CREATE INDEX idx_partner_name_trgm
ON res_partner
USING GIN (name gin_trgm_ops);
```

**Características:**
- ✅ Excelente para multi-value (arrays, JSONB)
- ✅ Full-text search
- ✅ Fuzzy search (trigram)
- ❌ Maior espaço em disco
- ❌ Slower inserts (precisa indexar todos valores)

---

#### 3. GiST (Generalized Search Tree)

**Quando usar:**
- Geometric types (point, box, circle)
- Range types
- Full-text search (alternativa ao GIN)
- Nearest neighbor (`<->`)

**Odoo Típico:**
```sql
-- Geolocalização (se usar PostGIS)
CREATE EXTENSION postgis;
CREATE INDEX idx_partner_location
ON res_partner
USING GIST (location);

-- Range types
CREATE INDEX idx_event_daterange
ON calendar_event
USING GIST (tstzrange(start_datetime, end_datetime));
```

**Características:**
- ✅ Bom para geometric/spatial
- ✅ Nearest neighbor queries
- ✅ Menor espaço que GIN
- ❌ Slower queries que GIN (para full-text)

---

#### 4. Partial Index

**Quando usar:**
Indexar apenas subset dos dados (WHERE clause).

**Odoo MUITO ÚTIL:**
```sql
-- Apenas leads ativos
CREATE INDEX idx_lead_active
ON crm_lead(user_id, stage_id)
WHERE active = true;

-- Apenas orders não cancelados
CREATE INDEX idx_order_not_cancelled
ON sale_order(partner_id, date_order)
WHERE state != 'cancel';

-- Apenas produtos vendáveis
CREATE INDEX idx_product_sale
ON product_template(name)
WHERE sale_ok = true;
```

**Benefícios:**
- ✅ Índice menor (menos disk I/O)
- ✅ Faster maintenance
- ✅ Queries mais rápidas (menos bloat)
- ✅ Economia de espaço (50-90%!)

**Exemplo Real:**
```sql
-- SEM partial index
CREATE INDEX idx_lead_user ON crm_lead(user_id);
-- Tamanho: 100MB (indexa 1M leads, incluindo 200k archived)

-- COM partial index
CREATE INDEX idx_lead_user_active ON crm_lead(user_id) WHERE active = true;
-- Tamanho: 80MB (indexa apenas 800k active)
-- 20% menor + queries mais rápidas!
```

---

### Identificando Índices Faltantes (Odoo)

```sql
-- Queries lentas sem índice
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
  AND tablename IN ('crm_lead', 'sale_order', 'account_move', 'res_partner')
  AND correlation < 0.1  -- Low correlation = needs index!
ORDER BY tablename, attname;

-- Tables sem índices em foreign keys
SELECT
    c.conrelid::regclass AS table_name,
    a.attname AS column_name,
    'CREATE INDEX idx_' || c.conrelid::regclass || '_' || a.attname ||
    ' ON ' || c.conrelid::regclass || '(' || a.attname || ');' AS create_index_sql
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
WHERE c.contype = 'f'  -- Foreign key
  AND NOT EXISTS (
      SELECT 1
      FROM pg_index i
      WHERE i.indrelid = c.conrelid
        AND a.attnum = ANY(i.indkey)
  );
```

---

### Monitoring de Índices

```sql
-- Índices não usados (considerar DROP)
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE 'pg_toast%'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Índices duplicados
SELECT
    pg_size_pretty(SUM(pg_relation_size(idx))::BIGINT) AS size,
    (array_agg(idx))[1] AS idx1,
    (array_agg(idx))[2] AS idx2,
    (array_agg(idx))[3] AS idx3
FROM (
    SELECT
        indexrelid::regclass AS idx,
        indrelid::text ||E'\n'|| indclass::text ||E'\n'|| indkey::text ||E'\n'||
        COALESCE(indexprs::text,'')||E'\n' || COALESCE(indpred::text,'') AS KEY
    FROM pg_index
) sub
GROUP BY KEY
HAVING COUNT(*) > 1
ORDER BY SUM(pg_relation_size(idx)) DESC;
```

---

### Reindex Strategy

```sql
-- Reindex concurrently (sem lock!)
REINDEX INDEX CONCURRENTLY idx_partner_name;

-- Reindex table (com lock - fazer fora de horário)
REINDEX TABLE res_partner;

-- Reindex database (CUIDADO!)
REINDEX DATABASE realcred;
```

**Quando fazer REINDEX:**
- Índice fragmentado (bloat > 30%)
- Performance degradou
- Após muitos UPDATEs/DELETEs
- **Frequência:** Mensal ou trimestral

---

## 🧹 VACUUM & BLOAT MANAGEMENT

### O que é VACUUM?

**Problema:**
PostgreSQL usa MVCC (Multi-Version Concurrency Control):
- UPDATE cria nova versão da row
- DELETE marca row como "dead" (não apaga!)
- Espaço fica ocupado = **BLOAT**

**Solução:**
VACUUM remove dead tuples e recupera espaço.

---

### Autovacuum (Recomendado!)

**Enable (default desde PG 8.3):**
```ini
# postgresql.conf
autovacuum = on                                 # Enabled by default
autovacuum_max_workers = 3                      # Default: 3
autovacuum_naptime = 1min                       # Default: 1min

# Thresholds (quando executar)
autovacuum_vacuum_threshold = 50                # Default: 50
autovacuum_vacuum_scale_factor = 0.2            # Default: 0.2

# Formula: vacuum quando dead_tuples > (threshold + scale_factor * reltuples)
# Exemplo: Table com 1M rows → vacuum quando > 50 + 0.2*1M = 200,050 dead tuples
```

**Para Odoo (High-write tables):**
```sql
-- Tabelas com muitos writes (crm_lead, mail_message, etc)
ALTER TABLE crm_lead SET (
    autovacuum_vacuum_scale_factor = 0.05,      -- 5% ao invés de 20%
    autovacuum_vacuum_threshold = 100,
    autovacuum_analyze_scale_factor = 0.02
);

-- Mail tracking (altíssimo write)
ALTER TABLE mail_tracking_event SET (
    autovacuum_vacuum_scale_factor = 0.01,      -- 1%!
    autovacuum_vacuum_threshold = 50
);
```

**Monitoring Autovacuum:**
```sql
-- Ver última vez que table foi vacuum/analyze
SELECT
    schemaname,
    relname,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze,
    vacuum_count,
    autovacuum_count
FROM pg_stat_user_tables
ORDER BY last_autovacuum NULLS FIRST;

-- Tables que precisam vacuum
SELECT
    schemaname,
    relname,
    n_dead_tup,
    n_live_tup,
    ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

---

### Manual VACUUM

**Quando fazer:**
- ❌ **NÃO** fazer rotineiramente (deixe autovacuum!)
- ✅ Após batch DELETE/UPDATE massivo
- ✅ Antes de REINDEX
- ✅ Troubleshooting de bloat

```sql
-- VACUUM simples (não bloqueia)
VACUUM res_partner;

-- VACUUM ANALYZE (recomendado)
VACUUM ANALYZE res_partner;

-- VACUUM VERBOSE (debug)
VACUUM VERBOSE res_partner;
```

---

### VACUUM FULL (CUIDADO!)

**O que faz:**
Reescreve table completamente, removendo TODO bloat.

```sql
-- Lock EXCLUSIVO! (downtime!)
VACUUM FULL res_partner;
```

**Quando usar:**
- ❌ **NUNCA** em produção (a não ser manutenção agendada)
- ✅ Bloat > 50% e queries sofrendo
- ✅ Fora de horário comercial
- ✅ Como último recurso

**Alternativa SEM LOCK:**
```bash
# pg_repack (extension)
sudo apt install postgresql-15-repack

# Repack table (online!)
pg_repack -t res_partner realcred
```

**pg_repack:**
- ✅ Sem lock exclusivo
- ✅ Pode rodar em produção
- ✅ Remove bloat como VACUUM FULL
- ⚠️ Requer 2x espaço temporário

---

### Bloat Monitoring

```sql
-- Bloat em tables
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    ROUND((CASE WHEN otta=0 THEN 0.0
           ELSE (pg_relation_size(schemaname||'.'||tablename) / otta::numeric - 1)*100
           END), 1) AS bloat_pct
FROM (
    SELECT
        schemaname, tablename, cc.reltuples, cc.relpages, bs,
        CEIL((cc.reltuples*((datahdr+ma-
          (CASE WHEN datahdr%ma=0 THEN ma ELSE datahdr%ma END))+nullhdr2+4))/(bs-20::float)) AS otta
    FROM (
        SELECT
            ma,bs,schemaname,tablename,
            (datawidth+(hdr+ma-(case when hdr%ma=0 THEN ma ELSE hdr%ma END)))::numeric AS datahdr,
            (maxfracsum*(nullhdr+ma-(case when nullhdr%ma=0 THEN ma ELSE nullhdr%ma END))) AS nullhdr2
        FROM (
            SELECT
                schemaname, tablename, hdr, ma, bs,
                SUM((1-null_frac)*avg_width) AS datawidth,
                MAX(null_frac) AS maxfracsum,
                hdr+(
                  SELECT 1+count(*)/8
                  FROM pg_stats s2
                  WHERE null_frac<>0 AND s2.schemaname = s.schemaname AND s2.tablename = s.tablename
                ) AS nullhdr
            FROM pg_stats s, (
                SELECT
                  (SELECT current_setting('block_size')::numeric) AS bs,
                  CASE WHEN substring(v,12,3) IN ('8.0','8.1','8.2') THEN 27 ELSE 23 END AS hdr,
                  CASE WHEN v ~ 'mingw32' THEN 8 ELSE 4 END AS ma
                FROM (SELECT version() AS v) AS foo
            ) AS constants
            GROUP BY 1,2,3,4,5
        ) AS foo
    ) AS rs
    JOIN pg_class cc ON cc.relname = rs.tablename
    JOIN pg_namespace nn ON cc.relnamespace = nn.oid AND nn.nspname = rs.schemaname AND nn.nspname <> 'information_schema'
) AS sml
WHERE schemaname = 'public'
ORDER BY bloat_pct DESC;
```

**Interpretar:**
- < 10%: ✅ OK
- 10-30%: 🟡 Monitor
- 30-50%: 🟠 Considerar VACUUM
- > 50%: 🔴 VACUUM FULL ou pg_repack urgente!

---

## ⚙️ CONFIGURAÇÃO PARA ODOO

### postgresql.conf Otimizado (Odoo Produção)

```ini
#------------------------------------------------------------------------------
# MEMORY
#------------------------------------------------------------------------------
shared_buffers = 4GB                            # 25% de 16GB RAM
effective_cache_size = 12GB                     # 75% de 16GB RAM
work_mem = 50MB                                 # 200 conexões * 3 sorts = ~30GB potencial
maintenance_work_mem = 1GB                      # Para VACUUM, CREATE INDEX

#------------------------------------------------------------------------------
# CONNECTIONS
#------------------------------------------------------------------------------
max_connections = 220                           # 100 users * 2 + workers + reserve
superuser_reserved_connections = 5

#------------------------------------------------------------------------------
# QUERY TUNING
#------------------------------------------------------------------------------
random_page_cost = 1.1                          # SSD (CRÍTICO!)
effective_io_concurrency = 200                  # SSD
default_statistics_target = 100
max_parallel_workers_per_gather = 4
max_parallel_workers = 8

#------------------------------------------------------------------------------
# WAL (Write-Ahead Logging)
#------------------------------------------------------------------------------
wal_level = replica
wal_buffers = 16MB
max_wal_size = 4GB
min_wal_size = 1GB
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9
wal_compression = on

#------------------------------------------------------------------------------
# REPLICATION
#------------------------------------------------------------------------------
max_wal_senders = 5
wal_keep_size = 2GB
hot_standby = on
hot_standby_feedback = on

#------------------------------------------------------------------------------
# AUTOVACUUM
#------------------------------------------------------------------------------
autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = 30s                        # Mais agressivo para Odoo
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_scale_factor = 0.1            # 10% ao invés de 20%
autovacuum_analyze_threshold = 50
autovacuum_analyze_scale_factor = 0.05
autovacuum_vacuum_cost_delay = 10ms
autovacuum_vacuum_cost_limit = 1000

#------------------------------------------------------------------------------
# LOGGING
#------------------------------------------------------------------------------
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000               # Log queries > 1s
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0                              # Log all temp file usage
log_autovacuum_min_duration = 0                 # Log all autovacuum

#------------------------------------------------------------------------------
# LOCALE
#------------------------------------------------------------------------------
lc_messages = 'pt_BR.UTF-8'
lc_monetary = 'pt_BR.UTF-8'
lc_numeric = 'pt_BR.UTF-8'
lc_time = 'pt_BR.UTF-8'
default_text_search_config = 'pg_catalog.portuguese'

#------------------------------------------------------------------------------
# SECURITY
#------------------------------------------------------------------------------
ssl = on
ssl_cert_file = '/etc/ssl/certs/ssl-cert-snakeoil.pem'
ssl_key_file = '/etc/ssl/private/ssl-cert-snakeoil.key'
password_encryption = scram-sha-256
```

---

### pg_hba.conf Seguro

```
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections (sem senha - apenas socket)
local   all             postgres                                peer

# Localhost (senha obrigatória)
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256

# Odoo application server
host    realcred        odoo            10.158.0.0/24           scram-sha-256

# Replication
host    replication     replicator      10.158.0.6/32           scram-sha-256

# Deny all others
host    all             all             0.0.0.0/0               reject
```

---

### Índices Essenciais para Odoo

```sql
-- res.partner (contatos)
CREATE INDEX CONCURRENTLY idx_partner_ref ON res_partner(ref) WHERE ref IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_partner_vat ON res_partner(vat) WHERE vat IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_partner_email_lower ON res_partner(LOWER(email)) WHERE email IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_partner_active ON res_partner(active, id);

-- crm.lead (oportunidades)
CREATE INDEX CONCURRENTLY idx_lead_user_stage ON crm_lead(user_id, stage_id) WHERE active = true;
CREATE INDEX CONCURRENTLY idx_lead_partner ON crm_lead(partner_id) WHERE partner_id IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_lead_team ON crm_lead(team_id) WHERE team_id IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_lead_date_deadline ON crm_lead(date_deadline) WHERE date_deadline IS NOT NULL AND active = true;

-- sale.order (vendas)
CREATE INDEX CONCURRENTLY idx_order_partner_date ON sale_order(partner_id, date_order);
CREATE INDEX CONCURRENTLY idx_order_state_date ON sale_order(state, date_order);
CREATE INDEX CONCURRENTLY idx_order_user ON sale_order(user_id) WHERE user_id IS NOT NULL;

-- account.move (faturas)
CREATE INDEX CONCURRENTLY idx_move_partner_date ON account_move(partner_id, invoice_date);
CREATE INDEX CONCURRENTLY idx_move_state_type ON account_move(state, move_type);
CREATE INDEX CONCURRENTLY idx_move_invoice_date ON account_move(invoice_date) WHERE move_type IN ('out_invoice', 'out_refund');

-- mail.message (mensagens - MUITO IMPORTANTE!)
CREATE INDEX CONCURRENTLY idx_message_model_res ON mail_message(model, res_id) WHERE model IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_message_date ON mail_message(date DESC);
CREATE INDEX CONCURRENTLY idx_message_author ON mail_message(author_id) WHERE author_id IS NOT NULL;

-- ir.attachment (arquivos)
CREATE INDEX CONCURRENTLY idx_attachment_res ON ir_attachment(res_model, res_id);
CREATE INDEX CONCURRENTLY idx_attachment_type ON ir_attachment(type);
```

---

## 📊 MONITORING QUERIES

### Slow Queries

```sql
-- Top 10 queries lentas (pg_stat_statements)
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time,
    stddev_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Locks

```sql
-- Queries bloqueadas
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

---

## ✅ CHECKLIST PRÉ-PRODUÇÃO

```
[ ] shared_buffers = 25% RAM
[ ] effective_cache_size = 75% RAM
[ ] work_mem calculado (não muito alto!)
[ ] random_page_cost = 1.1 (SSD)
[ ] max_connections adequado
[ ] Autovacuum habilitado e tuned
[ ] Logging configurado (slow queries)
[ ] pg_hba.conf seguro (apenas IPs necessários)
[ ] SSL habilitado
[ ] Backup automático configurado
[ ] Replicação configurada (se HA)
[ ] Monitoring (pg_stat_statements, logs)
[ ] Índices essenciais criados
[ ] VACUUM manual testado
[ ] Restore testado!
```

---

**Última atualização:** 2025-11-17
**Próxima revisão:** Quando PostgreSQL 18 for LTS
**Fontes:** PostgreSQL Official Docs, EDB, Percona, Crunchy Data, MyDBOps, CitusData
