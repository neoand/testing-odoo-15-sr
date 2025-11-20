# PostgreSQL Tuning para Odoo 15

> **Data:** 2025-11-17
> **Versão:** 1.0
> **Compatibilidade:** PostgreSQL 12-15, Odoo 15
> **Ambientes:** Testing (4GB RAM) + Production (12GB RAM)

---

## Visão Geral

Estes scripts otimizam automaticamente a configuração PostgreSQL 12 para servidores com Odoo 15, detectando RAM disponível e aplicando parâmetros ideais.

### Scripts

1. **`postgresql-tuning.sh`** - Aplica configuração otimizada
2. **`validate-postgresql-config.sh`** - Valida e testa performance

### Parâmetros Principais

| Parâmetro | Valor | Motivo |
|-----------|-------|--------|
| `random_page_cost` | **1.1** | CRÍTICO para SSDs (não use 4.0!) |
| `shared_buffers` | 25% RAM | Cache de dados |
| `effective_cache_size` | 75% RAM | Para query planner |
| `work_mem` | 50MB | Sorts/Hash joins |
| `maintenance_work_mem` | 10% RAM | VACUUM/CREATE INDEX |
| `autovacuum_*` | Otimizado | Limpeza automática |

---

## Instalação e Execução

### Pré-requisitos

- PostgreSQL 12+ instalado
- Acesso `sudo` (necessário para modificar configs)
- PostgreSQL rodando (`systemctl status postgresql`)
- Disco SSD (scripts assumem `random_page_cost=1.1`)

### Permissões

```bash
# Tornar scripts executáveis
chmod +x postgresql-tuning.sh
chmod +x validate-postgresql-config.sh
```

### Execução

#### 1. Servidor Testing (4GB RAM)

```bash
# Backup local seguro primeiro
cp -r /etc/postgresql ~/postgresql-backup-testing-$(date +%Y%m%d)

# Executar tuning
sudo ./postgresql-tuning.sh testing

# Aguardar completar
# Verificar saída para backup path
```

**Saída esperada:**
```
[INFO] Ambiente: testing
[INFO] RAM disponível: 4GB
[INFO] Parâmetros calculados:
  shared_buffers = 1024MB
  effective_cache_size = 3072MB
  work_mem = 50MB
  maintenance_work_mem = 409MB
[SUCCESS] PostgreSQL Tuning Completo!
```

#### 2. Servidor Production (12GB RAM)

```bash
# Backup local seguro primeiro
cp -r /etc/postgresql ~/postgresql-backup-production-$(date +%Y%m%d)

# Executar tuning (precisa restart)
sudo ./postgresql-tuning.sh production

# Aguardar completar
```

**Saída esperada:**
```
[INFO] Ambiente: production
[INFO] RAM disponível: 12GB
[INFO] Parâmetros calculados:
  shared_buffers = 3072MB
  effective_cache_size = 9216MB
  work_mem = 50MB
  maintenance_work_mem = 1228MB
[SUCCESS] PostgreSQL Tuning Completo!
```

---

## Validação

### 1. Verificação Rápida

```bash
# Logo após aplicar tuning
./validate-postgresql-config.sh

# Ou com database específica
./validate-postgresql-config.sh realcred
```

**Checklist esperado:**
- ✅ `shared_buffers` > 128MB
- ✅ `effective_cache_size` configurado
- ✅ `random_page_cost = 1.1` (SSD)
- ✅ `autovacuum = on`
- ✅ Cache hit ratio > 95%

### 2. Verificação Manual de Parâmetros

```bash
# Via SQL diretamente
sudo -u postgres psql -c "SHOW shared_buffers;"
sudo -u postgres psql -c "SHOW random_page_cost;"
sudo -u postgres psql -c "SHOW effective_cache_size;"

# Ver todos parâmetros otimizados
sudo -u postgres psql -c "SELECT name, setting FROM pg_settings WHERE name IN ('shared_buffers', 'effective_cache_size', 'random_page_cost', 'work_mem', 'maintenance_work_mem');"
```

### 3. Health Check Completo

```bash
# Verificar status do servidor
sudo systemctl status postgresql

# Ver logs
sudo tail -f /var/log/postgresql/postgresql.log

# Tamanho das databases
sudo -u postgres psql -l

# Conexões ativas
sudo -u postgres psql -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

---

## Tabela de Configuração por Ambiente

### Testing (4GB RAM)

```
shared_buffers           = 1024MB
effective_cache_size     = 3072MB
work_mem                 = 50MB
maintenance_work_mem     = 409MB
max_connections          = 100
checkpoint_timeout       = 10min
max_wal_size             = 2GB
autovacuum_max_workers   = 2
random_page_cost         = 1.1
```

### Production (12GB RAM)

```
shared_buffers           = 3072MB
effective_cache_size     = 9216MB
work_mem                 = 50MB
maintenance_work_mem     = 1228MB
max_connections          = 200
checkpoint_timeout       = 15min
max_wal_size             = 4GB
autovacuum_max_workers   = 3
random_page_cost         = 1.1
```

---

## Troubleshooting

### Problema: "Permission denied"

```bash
# Solução: usar sudo
sudo ./postgresql-tuning.sh production
```

### Problema: "PostgreSQL não está em execução"

```bash
# Iniciar PostgreSQL
sudo systemctl start postgresql

# Verificar status
sudo systemctl status postgresql
```

### Problema: "PostgreSQL não recarregou corretamente"

```bash
# Verificar log
sudo tail -50 /var/log/postgresql/postgresql.log

# Tentar restart completo (se reload não funcionou)
sudo systemctl restart postgresql

# Se ainda não funcionar, restaurar backup (ver seção Rollback)
```

### Problema: "Cache hit ratio baixo (<95%)"

**Causas:**
- `shared_buffers` insuficiente
- Database ainda aquecendo (primeiras horas)
- Muitos scans de tabelas grandes

**Soluções:**
```bash
# 1. Aguardar aquecimento (12-24h)
# 2. Aumentar shared_buffers manualmente:
sudo -u postgres psql -c "ALTER SYSTEM SET shared_buffers = '4GB';"
sudo systemctl reload postgresql

# 3. Executar VACUUM ANALYZE
sudo -u postgres psql realcred -c "VACUUM ANALYZE;"

# 4. Verificar índices não utilizados
./validate-postgresql-config.sh
```

---

## Rollback / Restauração

### Método 1: Usar Backup do Script

O script automaticamente salva backup antes de aplicar mudanças:

```bash
# Encontrar backup (path foi exibido ao executar)
ls -la /tmp/postgresql-backup-*

# Restaurar
BACKUP_PATH="/tmp/postgresql-backup-20251117-143022"
sudo cp $BACKUP_PATH/postgresql.conf.bak /etc/postgresql/12/main/postgresql.conf
sudo systemctl restart postgresql

# Verificar
sudo -u postgres psql -c "SHOW shared_buffers;"
```

### Método 2: ALTER SYSTEM RESET

```bash
# Resetar um parâmetro específico
sudo -u postgres psql -c "ALTER SYSTEM RESET shared_buffers;"

# Resetar todos (volta para defaults)
sudo -u postgres psql -c "ALTER SYSTEM RESET ALL;"

# Recarregar
sudo systemctl reload postgresql
```

### Método 3: Backup Manual (Mais Seguro)

Sempre faça antes de executar o script:

```bash
# Backup completo
sudo cp -r /etc/postgresql ~/postgresql-backup-$(date +%Y%m%d-%H%M%S)

# Para restaurar:
sudo cp -r ~/postgresql-backup-20251117-120000/* /etc/postgresql/
sudo systemctl restart postgresql
```

---

## Monitoramento Pós-Aplicação

### 1. Performance Queries

```bash
# Ver queries mais lentas
sudo -u postgres psql realcred << EOF
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
WHERE mean_time > 500
ORDER BY mean_time DESC
LIMIT 10;
EOF
```

### 2. Cache Hit Ratio

```bash
# Table cache hit
sudo -u postgres psql realcred << EOF
SELECT
    ROUND(100 * SUM(heap_blks_read) / (SUM(heap_blks_read) + SUM(heap_blks_hit)), 2) as table_hit_ratio
FROM pg_statio_user_tables;
EOF

# Index cache hit
sudo -u postgres psql realcred << EOF
SELECT
    ROUND(100 * SUM(idx_blks_read) / (SUM(idx_blks_read) + SUM(idx_blks_hit)), 2) as index_hit_ratio
FROM pg_statio_user_indexes;
EOF
```

### 3. Autovacuum Activity

```bash
# Ver última atividade
sudo -u postgres psql realcred << EOF
SELECT
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
ORDER BY last_autovacuum DESC
LIMIT 10;
EOF
```

### 4. Índices Não Utilizados

```bash
# Encontrar índices não utilizados (possível remover)
sudo -u postgres psql realcred << EOF
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
EOF
```

---

## Recomendações Adicionais

### 1. Ativar pg_stat_statements

Para monitorar queries:

```bash
# Editar postgresql.conf
sudo nano /etc/postgresql/12/main/postgresql.conf

# Descomente e encontre:
# shared_preload_libraries = 'pg_stat_statements'

# Depois ativar:
sudo -u postgres psql -c "CREATE EXTENSION pg_stat_statements;"
sudo systemctl restart postgresql
```

### 2. Configurar Log de Slow Queries

Já configurado por padrão:

```bash
# Padrão: queries > 1000ms
ALTER SYSTEM SET log_min_duration_statement = 1000;

# Ver logs
sudo tail -f /var/log/postgresql/postgresql.log | grep "duration:"
```

### 3. Agendar VACUUM ANALYZE Periódico

```bash
# Criar cron job para maintenance
sudo crontab -e

# Adicionar:
# VACUUM ANALYZE diariamente às 2AM
0 2 * * * sudo -u postgres psql realcred -c "VACUUM ANALYZE;" >> /var/log/postgresql/vacuum.log 2>&1
```

### 4. Monitorar Replication (Produção)

Se houver replicação configurada:

```bash
# Ver status de replication
sudo -u postgres psql -c "SELECT * FROM pg_stat_replication;"

# Ver replication lag
sudo -u postgres psql -c "SELECT now() - pg_last_xact_replay_timestamp() as replication_lag;"
```

---

## Impacto Esperado

### Antes do Tuning

- Cache hit ratio: 50-70%
- Queries lentas: >3s
- Latência Odoo: 2-5s
- CPU: Intermitente

### Depois do Tuning

- Cache hit ratio: >99%
- Queries otimizadas: <500ms
- Latência Odoo: <1s
- CPU: Estável

**Melhoria esperada: 50-80% faster** ⚡

---

## Segurança

### Permissões Recomendadas

```bash
# Scripts
chmod 750 postgresql-tuning.sh
chmod 750 validate-postgresql-config.sh

# Backups
sudo chown root:root /tmp/postgresql-backup-*
sudo chmod 700 /tmp/postgresql-backup-*
```

### Requisitos sudo

Para executar sem pedir senha toda vez:

```bash
# Adicionar ao sudoers
sudo visudo

# Adicionar linhas:
# %odoo_admins ALL=(ALL) NOPASSWD: /path/to/postgresql-tuning.sh
# %odoo_admins ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart postgresql
```

---

## Referências

- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Odoo Database Configuration](https://www.odoo.com/documentation/15.0/administration/install/deploy.html)
- [PostgreSQL ALTER SYSTEM](https://www.postgresql.org/docs/12/sql-altersystem.html)
- [SSD vs HDD: random_page_cost](https://wiki.postgresql.org/wiki/Performance_Optimization#random_page_cost)

---

## Suporte

Se encontrar problemas:

1. Executar `validate-postgresql-config.sh` para diagnóstico
2. Verificar logs: `sudo tail -f /var/log/postgresql/postgresql.log`
3. Restaurar backup se necessário
4. Documentar erro em `.claude/memory/errors/ERRORS-SOLVED.md`

---

**Última atualização:** 2025-11-17
**Status:** ✅ Pronto para produção
