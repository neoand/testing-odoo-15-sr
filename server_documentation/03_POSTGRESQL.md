# PostgreSQL - odoo-rc

**Data da documentação:** 2025-11-15
**Servidor:** odoo-rc (35.199.79.229)
**Versão:** PostgreSQL 12

---

## Clusters PostgreSQL

### Cluster 12/main (Principal)
- **Status:** Active (running) desde 24/Ago/2025
- **PID:** 645
- **Memória:** 6.3 GB
- **Data Directory:** `/var/lib/postgresql/12/main`
- **Config File:** `/etc/postgresql/12/main/postgresql.conf`
- **Porta:** 5432
- **Conexões ativas:** ~65 conexões do Odoo

### Cluster 12/test (Teste)
- **Status:** Active (running)
- **Data Directory:** `/var/lib/postgresql/12/test`
- **Conexões:** Mínimas (ambiente de teste)

---

## Databases

| Database  | Owner    | Size      | Encoding | Collation | Description                     |
|-----------|----------|-----------|----------|-----------|---------------------------------|
| postgres  | postgres | 8.1 MB    | UTF8     | C.UTF-8   | Administrative database         |
| realcred  | odoo     | **10 GB** | UTF8     | C.UTF-8   | Banco de produção Realcred      |
| template0 | postgres | 7.8 MB    | UTF8     | C.UTF-8   | Unmodifiable empty database     |
| template1 | postgres | 7.9 MB    | UTF8     | C.UTF-8   | Default template for new DBs    |

### Database realcred (Principal)
- **Tamanho:** 10.069 MB (~10 GB)
- **Total de tabelas:** 946 tabelas
- **Owner:** odoo
- **Encoding:** UTF8
- **Collation:** C.UTF-8

---

## Usuários PostgreSQL

| Role       | Atributos                                             | Membros |
|------------|-------------------------------------------------------|---------|
| postgres   | Superuser, Create role, Create DB, Replication, Bypass RLS | {}      |
| odoo       | Superuser, Create role, Create DB                     | {}      |
| replicador | Replication                                           | {}      |

**IMPORTANTE:** Usuário `odoo` tem privilégios de Superuser - necessário para operações do Odoo.

---

## Top 20 Tabelas Maiores (realcred)

| Tabela                                  | Tamanho  | Descrição                          |
|-----------------------------------------|----------|------------------------------------|
| ir_attachment                           | 3.6 GB   | Anexos (MAIOR TABELA!)             |
| mail_message                            | 2.3 GB   | Mensagens/comunicações             |
| contacts_realcred_batch                 | 1.2 GB   | Batch de contatos Realcred         |
| ir_model_data                           | 1.0 GB   | Metadados de modelos               |
| ir_translation                          | 309 MB   | Traduções                          |
| res_partner                             | 299 MB   | Parceiros/Contatos                 |
| acrux_chat_message                      | 298 MB   | Mensagens WhatsApp                 |
| mail_followers                          | 129 MB   | Seguidores de registros            |
| mail_tracking_value                     | 107 MB   | Tracking de mudanças               |
| crm_phonecall                           | 94 MB    | Ligações CRM                       |
| crm_lead                                | 78 MB    | Leads/Oportunidades                |
| mail_followers_mail_message_subtype_rel | 60 MB    | Relação followers                  |
| json_request_log                        | 31 MB    | Log de requisições JSON            |
| crm_phonecall_tag_rel                   | 23 MB    | Tags de ligações                   |
| bus_bus                                 | 22 MB    | Bus de mensagens                   |
| mail_notification                       | 21 MB    | Notificações                       |
| message_attachment_rel                  | 20 MB    | Relação mensagens-anexos           |
| mail_mail                               | 19 MB    | Emails enviados                    |
| website_track                           | 18 MB    | Tracking website                   |
| note_note                               | 18 MB    | Notas                              |

**Total das 20 maiores:** ~9.5 GB

---

## Configurações Importantes PostgreSQL

### Performance

```ini
# Memória
shared_buffers = 4GB                    # Buffer compartilhado
work_mem = 5242kB                       # Memória por operação
maintenance_work_mem = 1GB              # Memória para manutenção
effective_cache_size = 12GB             # Cache estimado do SO

# Conexões
max_connections = 200                   # Máximo de conexões

# Workers
max_worker_processes = 12
max_parallel_workers = 12
max_parallel_workers_per_gather = 4
max_parallel_maintenance_workers = 4

# Disco
effective_io_concurrency = 200          # SSD
random_page_cost = 1.1                  # Otimizado para SSD
```

### WAL (Write-Ahead Logging)

```ini
wal_level = logical                     # Permite replicação lógica
wal_buffers = 16MB
max_wal_size = 4GB
min_wal_size = 1GB
checkpoint_completion_target = 0.9

# Replicação
max_wal_senders = 10
max_replication_slots = 5
```

### Logging

```ini
log_line_prefix = '%m [%p] %q%u@%d '
log_timezone = 'Etc/UTC'
cluster_name = '12/main'
```

### Autovacuum

Configurações padrão ativas para limpeza automática.

---

## Autenticação (pg_hba.conf)

```
# Conexões locais
local   all             postgres                peer
local   all             all                     peer

# Conexões TCP/IP
host    realcred        odoo        127.0.0.1/32        md5
host    all             all         127.0.0.1/32        md5
host    all             all         ::1/128             md5

# Replicação
local   replication     all                             peer
host    replication     all         127.0.0.1/32        md5
host    replication     all         ::1/128             md5
host    replication     replicador  0.0.0.0/0           md5

# Acesso remoto específico
host    realcred        odoo        35.223.202.125/32   md5
host    postgres        odoo        35.223.202.125/32   md5
host    realcred        odoo        148.230.131.4/32    md5
```

**IPs Remotos:**
- `35.223.202.125` - Acesso externo autorizado
- `148.230.131.4` - Acesso externo autorizado

**ATENÇÃO:** Replicação aberta para `0.0.0.0/0` - RISCO DE SEGURANÇA! Considerar restringir.

---

## Conexões Ativas

### Estatísticas Atuais
- **Total de conexões:** ~65 conexões persistentes
- **Usuário:** odoo
- **Database:** realcred (principal) + postgres (admin)
- **Estado:** Maioria em idle (aguardando próxima query)

### Distribuição
- Conexões locais (127.0.0.1): ~64
- Conexões remotas (35.223.202.125): 1

---

## Módulos Odoo Instalados (Sample - Top 100)

Total de módulos instalados: **100+**

### Principais Categorias

**Core Odoo:**
- base, web, portal, auth_*
- mail, bus, http_routing

**CRM & Vendas:**
- crm, crm_phonecall, crm_products
- sale_management, sale_crm
- 3cxcrm (integração telefonia)

**Fiscal Brasil:**
- l10n_br_* (20+ módulos)
- account_*, contract

**RH:**
- hr, hr_attendance, hr_contract
- hr_holidays, hr_timesheet
- hr_attendance_face_recognition
- employee_documents_expiry

**Helpdesk:**
- helpdesk_mgmt, helpdesk_mgmt_project
- helpdesk_mgmt_rating, helpdesk_type

**WhatsApp:**
- Vários módulos whatsapp_connector_*

**Customizados:**
- contacts_realcred
- ks_dashboard_ninja
- auto_backup_odoo
- dms (Document Management)

(Ver lista completa via query ao banco)

---

## Backup e Restore

### Backup do Database realcred

```bash
# Backup completo
sudo -u postgres pg_dump realcred > realcred_backup_$(date +%Y%m%d_%H%M%S).sql

# Backup comprimido
sudo -u postgres pg_dump realcred | gzip > realcred_backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup custom format (recomendado - permite restore parcial)
sudo -u postgres pg_dump -Fc realcred > realcred_backup_$(date +%Y%m%d_%H%M%S).dump

# Backup apenas schema
sudo -u postgres pg_dump --schema-only realcred > realcred_schema_$(date +%Y%m%d_%H%M%S).sql

# Backup apenas dados
sudo -u postgres pg_dump --data-only realcred > realcred_data_$(date +%Y%m%d_%H%M%S).sql
```

### Restore

```bash
# Restore de SQL
sudo -u postgres psql realcred < realcred_backup.sql

# Restore de dump custom
sudo -u postgres pg_restore -d realcred realcred_backup.dump

# Restore em novo database
sudo -u postgres createdb realcred_new
sudo -u postgres pg_restore -d realcred_new realcred_backup.dump
```

### Backup de Roles/Users

```bash
sudo -u postgres pg_dumpall --roles-only > roles_backup.sql
```

---

## Monitoramento

### Verificar conexões ativas

```sql
SELECT
    datname,
    usename,
    client_addr,
    state,
    count(*)
FROM pg_stat_activity
GROUP BY datname, usename, client_addr, state;
```

### Verificar queries lentas

```sql
SELECT
    pid,
    now() - query_start AS duration,
    query,
    state
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;
```

### Verificar tamanho de tabelas

```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;
```

### Verificar uso de índices

```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

---

## Manutenção

### Vacuum manual

```bash
# Vacuum completo
sudo -u postgres psql realcred -c "VACUUM VERBOSE;"

# Vacuum analyze (atualiza estatísticas)
sudo -u postgres psql realcred -c "VACUUM ANALYZE;"

# Vacuum full (recupera espaço - LOCK completo!)
sudo -u postgres psql realcred -c "VACUUM FULL VERBOSE;"
```

### Reindex

```bash
# Reindex database completo (pode demorar!)
sudo -u postgres psql realcred -c "REINDEX DATABASE realcred;"

# Reindex tabela específica
sudo -u postgres psql realcred -c "REINDEX TABLE ir_attachment;"
```

---

## Troubleshooting

### PostgreSQL não inicia

```bash
# Verificar status
sudo systemctl status postgresql@12-main

# Ver logs
sudo tail -f /var/log/postgresql/postgresql-12-main.log

# Verificar config
sudo -u postgres /usr/lib/postgresql/12/bin/postgres -D /var/lib/postgresql/12/main --check
```

### Muitas conexões idle

```sql
-- Verificar
SELECT count(*) FROM pg_stat_activity WHERE state = 'idle';

-- Matar conexões idle antigas (cuidado!)
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < now() - interval '1 hour';
```

### Database muito grande

1. Verificar tabelas maiores (query acima)
2. Considerar:
   - Arquivar `ir_attachment` antigos
   - Limpar `mail_message` antigos
   - Vacuum full para recuperar espaço

### Performance lenta

1. Verificar queries lentas
2. Analisar plano de execução: `EXPLAIN ANALYZE`
3. Atualizar estatísticas: `VACUUM ANALYZE`
4. Verificar índices não utilizados

---

## Comandos Úteis

```bash
# Status do cluster
sudo systemctl status postgresql@12-main

# Restart
sudo systemctl restart postgresql@12-main

# Reload configuração
sudo systemctl reload postgresql@12-main

# Conectar ao database
sudo -u postgres psql realcred

# Listar databases
sudo -u postgres psql -l

# Listar conexões
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Tamanho do database
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('realcred'));"
```

---

## Atenção - Pontos Críticos

1. **ir_attachment com 3.6 GB** - Tabela muito grande! Considerar limpeza/arquivamento
2. **mail_message com 2.3 GB** - Considerar arquivamento de mensagens antigas
3. **contacts_realcred_batch com 1.2 GB** - Verificar se batches antigos podem ser removidos
4. **Replicação aberta (0.0.0.0/0)** - RISCO DE SEGURANÇA! Restringir IPs
5. **65+ conexões persistentes** - Monitorar para evitar esgotar max_connections (200)
6. **Database 10 GB** - Crescendo, planejar backups regulares e manutenção
7. **Shared_buffers 4GB** - OK para 12GB RAM, mas monitorar uso

---

## Recomendações

1. **Backup diário** do database realcred
2. **Limpar** ir_attachment e mail_message antigos periodicamente
3. **Restringir** acesso de replicação no pg_hba.conf
4. **Monitorar** crescimento do database (atualmente 10GB)
5. **Configurar** auto_backup_odoo para backups automatizados
6. **Vacuum** regular para manter performance
7. **Reindex** periódico (mensal) para manter índices otimizados
