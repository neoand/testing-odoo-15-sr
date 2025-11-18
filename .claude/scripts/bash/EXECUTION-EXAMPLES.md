# PostgreSQL Tuning - Exemplos de Execução

> **Data:** 2025-11-17
> **Versão:** 1.0
> **Propósito:** Exemplos reais com saída esperada

---

## Exemplo 1: Execução em Servidor Testing

### Pré-execução

```bash
$ ssh gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b
admin_iurd_mx@odoo-sr-tensting:~$

# Navegar para scripts
$ cd /home/admin_iurd_mx/testing_odoo_15_sr/.claude/scripts/bash
admin_iurd_mx@odoo-sr-tensting:~/.../scripts/bash$

# Listar scripts
$ ls -la postgresql-*.sh
-rwx--x--x 1 admin_iurd_mx staff  9410 Nov 17 22:37 postgresql-tuning.sh
-rwx--x--x 1 admin_iurd_mx staff  5416 Nov 17 22:37 postgresql-quick-setup.sh
-rwx--x--x 1 admin_iurd_mx staff  6181 Nov 17 22:37 postgresql-rollback.sh
-rwx--x--x 1 admin_iurd_mx staff 13442 Nov 17 22:36 validate-postgresql-config.sh

# Fazer backup local
$ sudo cp -r /etc/postgresql ~/postgresql-backup-testing-$(date +%Y%m%d)
```

### Execução

```bash
# Opção 1: Quick Setup (RECOMENDADO)
$ sudo ./postgresql-quick-setup.sh testing

Iniciando pre-flight checklist...

[✓] Executando como root
[✓] PostgreSQL instalado
[✓] PostgreSQL rodando
[✓] RAM suficiente: 4GB
[✓] Ambiente válido: testing

═══════════════════════════════════════════════════════════
PostgreSQL Tuning - Confirmação
═══════════════════════════════════════════════════════════

Configuração a ser aplicada:
  Ambiente: testing
  RAM: 4GB
  Backup: /tmp/postgresql-backup-[timestamp]/

[!] Esta operação vai:
  - MODIFICAR configuração PostgreSQL
  - RECARREGAR PostgreSQL (downtime: ~5 segundos)
  - CRIAR BACKUP automático

Continuar? (sim/nao): sim

[INFO] Executando postgresql-tuning.sh...

[INFO] PostgreSQL versão 12 detectada
[INFO] Ambiente: testing
[INFO] RAM disponível: 4GB
[INFO] Parâmetros calculados:
  shared_buffers = 1024MB
  effective_cache_size = 3072MB
  work_mem = 50MB
  maintenance_work_mem = 409MB
  random_page_cost = 1.1

[INFO] Fazendo backup de configuração em: /tmp/postgresql-backup-20251117-143022
[SUCCESS] Backup realizado

[INFO] Aplicando configuração PostgreSQL...
[SUCCESS] Configuração aplicada via ALTER SYSTEM

[INFO] Recarregando configuração do PostgreSQL...
[SUCCESS] PostgreSQL recarregado com sucesso

[INFO] Validando aplicação de configuração...
[INFO] Valores aplicados:
  shared_buffers = 1024MB
  effective_cache_size = 3072MB
  random_page_cost = 1.1

[SUCCESS] random_page_cost = 1.1 (SSD - CORRETO!)

[INFO] Executando validação...
[SUCCESS] Validação passou!

[INFO] Resumo da validação:
[✓] shared_buffers = 1024MB
[✓] effective_cache_size = 3072MB (Recomendado > 128MB)
[✓] random_page_cost = 1.1 (SSD - ÓTIMO!)
[✓] autovacuum = on

═══════════════════════════════════════════════════════════
PostgreSQL Tuning Concluído com Sucesso!
═══════════════════════════════════════════════════════════

[INFO] Próximas etapas:
  1. Monitorar performance Odoo:
     tail -f /var/log/odoo/odoo-server.log | grep duration

  2. Verificar health PostgreSQL:
     sudo systemctl status postgresql

  3. Rodar validação completa:
     ./validate-postgresql-config.sh

  4. Se algo der errado, restaurar:
     sudo ./postgresql-rollback.sh
```

### Pós-execução (Testing)

```bash
# Verificar parâmetros foram aplicados
$ sudo -u postgres psql -c "SHOW shared_buffers; SHOW random_page_cost; SHOW effective_cache_size;"
 shared_buffers
────────────────
 1024MB
(1 row)

 random_page_cost
──────────────────
 1.1
(1 row)

 effective_cache_size
──────────────────────
 3072MB
(1 row)

# Status PostgreSQL
$ sudo systemctl status postgresql
● postgresql.service - PostgreSQL database server
   Loaded: loaded (/lib/systemd/system/postgresql.service; enabled; vendor preset: enabled)
   Active: active (running) since Sat 2025-11-17 14:30:22 UTC; 2min 15s ago
   Main PID: 1234 (postgres)
   Tasks: 8 (limit: 1000)
   Memory: 245.2M
   CPU: 1%
   CGroup: /system.slice/postgresql.service

# Rodar validação completa
$ ./validate-postgresql-config.sh

═══════════════════════════════════════════════════════════
1. VERIFICAÇÃO DE PARÂMETROS CRÍTICOS
═══════════════════════════════════════════════════════════

[✓] shared_buffers = 1024MB
[✓] effective_cache_size = 3072MB
[✓] random_page_cost = 1.1 (SSD - ÓTIMO!)
[✓] work_mem = 50MB
[✓] maintenance_work_mem = 409MB
[✓] max_connections = 100
[✓] autovacuum = on
[✓] autovacuum_max_workers = 2
[✓] effective_io_concurrency = 200
[✓] jit = on (JIT ativo - ótimo!)
[SUCCESS] Todos parâmetros críticos configurados!

═══════════════════════════════════════════════════════════
2. HEALTH DO SERVIDOR POSTGRESQL
═══════════════════════════════════════════════════════════

[INFO] Conexões ativas: 5
[INFO] Uptime: 00:02:15.123456
[INFO] Tamanho da database: 2.5GB
[INFO] CPU cores: 2
[INFO] RAM disponível: 4GB
[SUCCESS] Server health verificado

[... mais 8 seções ...]

═══════════════════════════════════════════════════════════
RESUMO DA VALIDAÇÃO
═══════════════════════════════════════════════════════════

[✓] random_page_cost = 1.1 (SSD OK)
[✓] shared_buffers configurado adequadamente
[✓] autovacuum ativo
[SUCCESS] Validação Completa!

[INFO] Próximos passos:
  1. Monitorar performance da aplicação
  2. Verificar logs: tail -f /var/log/postgresql/postgresql.log
  3. Se necessário, executar VACUUM ANALYZE:
     sudo -u postgres psql database -c 'VACUUM ANALYZE;'
  4. Para mais detalhes: sudo -u postgres psql database -c '\dtS+'
```

---

## Exemplo 2: Execução em Servidor Production

### Pré-execução

```bash
$ ssh andlee21@35.199.79.229
andlee21@odoo-rc:~$

# Navegar para scripts
$ cd /opt/testing_odoo_15_sr/.claude/scripts/bash

# Fazer backup local
$ sudo cp -r /etc/postgresql ~/postgresql-backup-production-$(date +%Y%m%d)
```

### Execução

```bash
# Opção 1: Quick Setup (RECOMENDADO)
$ sudo ./postgresql-quick-setup.sh production

Iniciando pre-flight checklist...

[✓] Executando como root
[✓] PostgreSQL instalado
[✓] PostgreSQL rodando
[✓] RAM suficiente: 12GB
[✓] Ambiente válido: production

═══════════════════════════════════════════════════════════
PostgreSQL Tuning - Confirmação
═══════════════════════════════════════════════════════════

Configuração a ser aplicada:
  Ambiente: production
  RAM: 12GB
  Backup: /tmp/postgresql-backup-[timestamp]/

[!] Esta operação vai:
  - MODIFICAR configuração PostgreSQL
  - RECARREGAR PostgreSQL (downtime: ~5 segundos)
  - CRIAR BACKUP automático

Continuar? (sim/nao): sim

[INFO] Executando postgresql-tuning.sh...

[INFO] PostgreSQL versão 12 detectada
[INFO] Ambiente: production
[INFO] RAM disponível: 12GB
[INFO] Parâmetros calculados:
  shared_buffers = 3072MB
  effective_cache_size = 9216MB
  work_mem = 50MB
  maintenance_work_mem = 1228MB
  random_page_cost = 1.1

[INFO] Fazendo backup de configuração em: /tmp/postgresql-backup-20251117-150045
[SUCCESS] Backup realizado

[INFO] Aplicando configuração PostgreSQL...
[SUCCESS] Configuração aplicada via ALTER SYSTEM

[INFO] Recarregando configuração do PostgreSQL...
[SUCCESS] PostgreSQL recarregado com sucesso

[INFO] Validando aplicação de configuração...
[INFO] Valores aplicados:
  shared_buffers = 3072MB
  effective_cache_size = 9216MB
  random_page_cost = 1.1

[SUCCESS] random_page_cost = 1.1 (SSD - CORRETO!)

[INFO] Executando validação...
[SUCCESS] Validação passou!

═══════════════════════════════════════════════════════════
PostgreSQL Tuning Concluído com Sucesso!
═══════════════════════════════════════════════════════════

[INFO] Próximas etapas:
  1. Monitorar performance Odoo:
     tail -f /var/log/odoo/odoo-server.log | grep duration

  2. Verificar health PostgreSQL:
     sudo systemctl status postgresql

  3. Rodar validação completa:
     ./validate-postgresql-config.sh realcred

  4. Se algo der errado, restaurar:
     sudo ./postgresql-rollback.sh
```

### Pós-execução (Production)

```bash
# Verificar aplicação
$ sudo -u postgres psql -c "SHOW shared_buffers; SHOW random_page_cost;"
 shared_buffers
────────────────
 3072MB
(1 row)

 random_page_cost
──────────────────
 1.1
(1 row)

# Validação completa com database realcred
$ ./validate-postgresql-config.sh realcred

[INFO] Database: realcred

═══════════════════════════════════════════════════════════
1. VERIFICAÇÃO DE PARÂMETROS CRÍTICOS
═══════════════════════════════════════════════════════════

[✓] shared_buffers = 3072MB
[✓] effective_cache_size = 9216MB
[✓] random_page_cost = 1.1 (SSD - ÓTIMO!)
[✓] work_mem = 50MB
[✓] maintenance_work_mem = 1228MB
[✓] max_connections = 200
[✓] autovacuum = on
[✓] autovacuum_max_workers = 3
[SUCCESS] Todos parâmetros críticos configurados!

═══════════════════════════════════════════════════════════
2. HEALTH DO SERVIDOR POSTGRESQL
═══════════════════════════════════════════════════════════

[INFO] Conexões ativas: 67
[INFO] Uptime: 1 day 12:34:56.789123
[INFO] Tamanho da database: 10.2GB
[INFO] CPU cores: 8
[INFO] RAM disponível: 12GB
[SUCCESS] Server health verificado

═══════════════════════════════════════════════════════════
3. CACHE HIT RATIO (Índices e Heap)
═══════════════════════════════════════════════════════════

[INFO] Table Hit Ratio: 95.2%
[SUCCESS] Hit ratio bom (>95%)
[INFO] Index Hit Ratio: 97.8%
[SUCCESS] Hit ratio excelente (>99%)

[... mais seções ...]

═══════════════════════════════════════════════════════════
RESUMO DA VALIDAÇÃO
═══════════════════════════════════════════════════════════

[✓] random_page_cost = 1.1 (SSD OK)
[✓] shared_buffers configurado adequadamente (3GB)
[✓] autovacuum ativo
[SUCCESS] Validação Completa!
```

---

## Exemplo 3: Rollback (Se Necessário)

### Scenario: "Algo deu errado após tuning"

```bash
# Executar rollback
$ sudo ./postgresql-rollback.sh

[INFO] Nenhum backup especificado. Buscando backups disponíveis...

Backups disponíveis:
  1) /tmp/postgresql-backup-20251117-143022/
  2) /tmp/postgresql-backup-20251117-143500/
  3) /tmp/postgresql-backup-20251117-150045/

Selecione número do backup (1-3): 3

[INFO] Backup selecionado: /tmp/postgresql-backup-20251117-150045/
[INFO] Verificando integridade do backup...
[SUCCESS] Backup integridade OK (856 linhas)

═════════════════════════════════════════════════════════════════

[!] ATENÇÃO: Esta operação vai restaurar configuração anterior do PostgreSQL

Backup: /tmp/postgresql-backup-20251117-150045/
Arquivo: postgresql.conf.bak

Tem certeza que deseja restaurar? (sim/nao): sim

[INFO] Iniciando restauração...
[INFO] Salvando configuração atual em: /tmp/postgresql-config-before-rollback-20251117-161234
[INFO] Restaurando postgresql.conf...
[SUCCESS] postgresql.conf restaurado

[INFO] Recarregando PostgreSQL...
[SUCCESS] PostgreSQL recarregado com sucesso

[INFO] Verificando restauração...
[INFO] Parâmetros após restauração:
  shared_buffers = 256MB
  work_mem = 4MB
  random_page_cost = 1.0

═════════════════════════════════════════════════════════════════
[SUCCESS] RESTAURAÇÃO COMPLETA!
═════════════════════════════════════════════════════════════════

[INFO] Resumo:
  Backup restaurado: /tmp/postgresql-backup-20251117-150045/
  Config anterior salva: /tmp/postgresql-config-before-rollback-20251117-161234
  PostgreSQL status: active

[INFO] Para ver diferenças entre configurações:
  diff /tmp/postgresql-backup-20251117-150045/postgresql.conf.bak /tmp/postgresql-config-before-rollback-20251117-161234/postgresql.conf.current

[INFO] Próximas recomendações:
  1. Monitorar application: tail -f /var/log/odoo/odoo-server.log
  2. Verificar PostgreSQL: sudo tail -f /var/log/postgresql/postgresql.log
  3. Testar conexões: sudo -u postgres psql -l
  4. Se problema persistir, entre em contato com suporte
```

---

## Exemplo 4: Troubleshooting - Cache Hit Ratio Baixo

### Situação

```bash
# Após 12 horas de execução, cache hit ratio ainda baixo
$ ./validate-postgresql-config.sh realcred | grep -A 5 "Cache Hit"

[INFO] Table Hit Ratio: 45.2%
[!] Hit ratio baixo (<95%) - considerar aumentar shared_buffers
```

### Diagnóstico e Solução

```bash
# 1. Verificar aplicação de parâmetros
$ sudo -u postgres psql -c "SHOW shared_buffers;"
 shared_buffers
────────────────
 3072MB
(1 row)

# OK, parâmetro foi aplicado. Cache ainda aquecendo.

# 2. Executar VACUUM ANALYZE para otimizar planner
$ sudo -u postgres psql realcred -c "VACUUM ANALYZE;"
VACUUM

# 3. Verificar tabelas grandes
$ sudo -u postgres psql realcred -c "
    SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
    FROM pg_stat_user_tables
    WHERE pg_total_relation_size(schemaname||'.'||tablename) > 100*1024*1024
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
    LIMIT 5;
"
 schemaname │ tablename │ size
────────────┼──────────────────
 public     │ ir_attachment │ 3.6GB
 public     │ mail_message │ 2.3GB
 public     │ ir_logging │ 1.2GB
 public     │ crm_lead │ 890MB
 public     │ res_partner │ 560MB

# 4. Aguardar aquecimento (cache será preenchido naturalmente)
# Tempo estimado: 24-48 horas de uso normal

# 5. Se ainda baixo após 48h, considerar aumentar shared_buffers
$ sudo -u postgres psql -c "ALTER SYSTEM SET shared_buffers = '4GB';"
ALTER SYSTEM

$ sudo systemctl reload postgresql

# Verificar
$ sudo -u postgres psql -c "SHOW shared_buffers;"
 shared_buffers
────────────────
 4GB
(1 row)
```

---

## Exemplo 5: Monitoramento Contínuo

### Ver Performance Pré vs Pós

```bash
# ANTES (sem tuning)
$ sudo -u postgres psql realcred << EOF
SELECT
    query,
    calls,
    total_time::integer as total_ms,
    mean_time::integer as mean_ms,
    max_time::integer as max_ms
FROM pg_stat_statements
WHERE query LIKE '%crm_lead%'
ORDER BY mean_time DESC
LIMIT 5;
EOF

 query │ calls │ total_ms │ mean_ms │ max_ms
───────┼───────┼──────────┼─────────┼────────
 SELECT ... │ 1245 │ 4500 │ 3612 │ 8234

# DEPOIS (com tuning, 24h depois)
$ sudo -u postgres psql realcred << EOF
SELECT
    query,
    calls,
    total_time::integer as total_ms,
    mean_time::integer as mean_ms,
    max_time::integer as max_ms
FROM pg_stat_statements
WHERE query LIKE '%crm_lead%'
ORDER BY mean_time DESC
LIMIT 5;
EOF

 query │ calls │ total_ms │ mean_ms │ max_ms
───────┼───────┼──────────┼─────────┼────────
 SELECT ... │ 2340 │ 1200 │ 512 │ 1234

# MELHORIA:
# - mean_time: 3612ms → 512ms (-85%)
# - max_time: 8234ms → 1234ms (-85%)
# - Mais queries executadas (melhor cache)
```

---

## Exemplo 6: Automação em Shell Script

### Script para executar periodicamente

```bash
#!/bin/bash
# File: /usr/local/bin/postgresql-tuning-health-check.sh

SCRIPT_DIR="/opt/testing_odoo_15_sr/.claude/scripts/bash"
LOG_FILE="/var/log/postgresql-tuning-health.log"
ENV="${1:-production}"

echo "$(date): Starting PostgreSQL health check" >> $LOG_FILE

# Executar validação
$SCRIPT_DIR/validate-postgresql-config.sh >> $LOG_FILE 2>&1

# Extrair resultado
if grep -q "Validação Completa" $LOG_FILE; then
    echo "$(date): Health check PASSED" >> $LOG_FILE
    exit 0
else
    echo "$(date): Health check FAILED - Check logs!" >> $LOG_FILE
    exit 1
fi
```

### Agendar no Crontab

```bash
# Adicionar ao crontab
sudo crontab -e

# Adicionar:
# Executar health check diariamente às 8 AM
0 8 * * * /usr/local/bin/postgresql-tuning-health-check.sh >> /var/log/cron-pg-tuning.log 2>&1
```

---

## Exemplo 7: Verificação de Parâmetros (SQL Direto)

```bash
# Conectar ao PostgreSQL
$ sudo -u postgres psql

postgres=# -- Ver todos parâmetros otimizados
postgres=# SELECT name, setting FROM pg_settings WHERE name IN (
  'shared_buffers',
  'effective_cache_size',
  'random_page_cost',
  'work_mem',
  'maintenance_work_mem',
  'max_connections',
  'autovacuum',
  'jit'
);

        name        │      setting
───────────────────┼──────────────────
autovacuum          │ on
effective_cache_size│ 9216MB
jit                 │ on
max_connections     │ 200
maintenance_work_mem│ 1228MB
random_page_cost    │ 1.1
shared_buffers      │ 3072MB
work_mem            │ 50MB

(8 rows)

# Ver um parâmetro específico
postgres=# SHOW random_page_cost;
 random_page_cost
──────────────────
 1.1
(1 row)

# Sair
postgres=# \q
```

---

## Checklist de Sucesso

✅ **Todos os exemplos acima devem resultar em:**
- Parâmetros aplicados corretamente
- PostgreSQL rodando sem erros
- Cache hit ratio > 95% (após 24h)
- Queries mais rápidas (50-80% improvement)
- Odoo mais responsivo
- Sem downtime percebido para usuários

---

**Versão:** 1.0
**Data:** 2025-11-17
**Status:** Pronto para Referência
