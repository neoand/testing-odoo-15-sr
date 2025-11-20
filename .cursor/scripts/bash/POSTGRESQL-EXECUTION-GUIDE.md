# PostgreSQL Tuning - Guia de Execução Passo-a-Passo

> **Data:** 2025-11-17
> **Versão:** 1.0
> **Status:** Pronto para execução em produção

---

## Scripts Disponíveis

| Script | Finalidade | Quando Usar |
|--------|-----------|-------------|
| `postgresql-tuning.sh` | Aplica otimização automática | Primeira execução |
| `validate-postgresql-config.sh` | Valida e testa performance | Após tuning ou diagnosticar |
| `postgresql-quick-setup.sh` | Setup simplificado com confirmação | Para uso em CI/CD ou automação |
| `postgresql-rollback.sh` | Restaura configuração anterior | Se algo der errado |

---

## Opção 1: Execução Rápida (Recomendado para Produção)

### Servidor Testing (4GB RAM)

```bash
# 1. SSH para servidor
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b

# 2. Navegar para scripts
cd /path/to/testing_odoo_15_sr/.claude/scripts/bash

# 3. Executar setup rápido
sudo ./postgresql-quick-setup.sh testing

# 4. Responder "sim" na confirmação
# 5. Aguardar completo (~30 segundos)

# Saída esperada:
# [✓] PostgreSQL Tuning Concluído com Sucesso!
# [INFO] Próximas etapas:
#   1. Monitorar performance Odoo:
#      tail -f /var/log/odoo/odoo-server.log | grep duration
```

### Servidor Produção (12GB RAM)

```bash
# 1. SSH para servidor
ssh andlee21@35.199.79.229
# ou
ssh odoo-rc

# 2. Navegar para scripts
cd /path/to/testing_odoo_15_sr/.claude/scripts/bash

# 3. Executar setup rápido
sudo ./postgresql-quick-setup.sh production

# 4. Responder "sim" na confirmação
# 5. Aguardar completo (~30 segundos)

# Saída esperada: [✓] PostgreSQL Tuning Concluído com Sucesso!
```

---

## Opção 2: Execução Detalhada (Controle Total)

### Pré-Voo Manual

```bash
# 1. Conectar ao servidor
ssh odoo-rc

# 2. Verificar PostgreSQL
sudo systemctl status postgresql

# 3. Backup de segurança
sudo cp -r /etc/postgresql ~/postgresql-backup-$(date +%Y%m%d-%H%M%S)

# 4. Verificar RAM
free -h
# Esperado: >10GB para produção, >3GB para testing

# 5. Verificar storage
df -h /var/lib/postgresql
# Esperado: >20% espaço livre

# 6. Verificar conexões PostgreSQL
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
# Esperado: <50 conexões (se >100, há algo anormal)
```

### Executar Tuning Detalhado

```bash
# Navegar para scripts
cd /path/to/testing_odoo_15_sr/.claude/scripts/bash

# Executar direto (com argumentos)
sudo ./postgresql-tuning.sh production

# Monitorar saída:
# [INFO] Ambiente: production
# [INFO] RAM disponível: 12GB
# [INFO] Parâmetros calculados:
#   shared_buffers = 3072MB
#   effective_cache_size = 9216MB
# ...
# [SUCCESS] PostgreSQL Tuning Completo!

# Anotar backup path se quiser restaurar depois
# [INFO] Fazendo backup de configuração em: /tmp/postgresql-backup-20251117-143022
```

### Validação Detalhada

```bash
# Executar validação completa
./validate-postgresql-config.sh realcred

# Verificar saída:
# ═══════════════════════════════════════════════════════════
# 1. VERIFICAÇÃO DE PARÂMETROS CRÍTICOS
# ═══════════════════════════════════════════════════════════
# [✓] shared_buffers = 3072MB
# [✓] effective_cache_size = 9216MB
# [✓] random_page_cost = 1.1 (SSD - ÓTIMO!)
# [✓] autovacuum = on
# ...
# [✓] Todos parâmetros críticos configurados!

# Se houver problemas:
# [!] Existem 2 problemas críticos!
```

---

## Validação Manual Pós-Execução

### Verificar Aplicação de Parâmetros

```bash
# Conectar ao PostgreSQL
sudo -u postgres psql

# Executar queries:
postgres=# SHOW shared_buffers;
 shared_buffers
────────────────
 3072MB
(1 row)

postgres=# SHOW random_page_cost;
 random_page_cost
──────────────────
 1.1
(1 row)

postgres=# SHOW effective_cache_size;
 effective_cache_size
──────────────────────
 9216MB
(1 row)

postgres=# SHOW autovacuum_max_workers;
 autovacuum_max_workers
────────────────────────
 3
(1 row)

# Sair
postgres=# \q
```

### Verificar Health

```bash
# Status geral
sudo systemctl status postgresql

# Atividade do servidor
sudo -u postgres psql -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"

# Tamanho da database
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('realcred'));"

# Índices
sudo -u postgres psql realcred -c "SELECT count(*) FROM pg_indexes;"
```

### Monitorar Logs

```bash
# Verificar logs do PostgreSQL
sudo tail -50 /var/log/postgresql/postgresql.log | grep -i "error\|warning"

# Monitorar em tempo real
sudo tail -f /var/log/postgresql/postgresql.log

# Ver arquivo de changelog (post-tuning)
sudo grep -A 20 "ALTER SYSTEM" /var/log/postgresql/postgresql.log | tail -30
```

---

## Troubleshooting Rápido

### Problema 1: "Permission denied"

```bash
❌ Erro:
$ ./postgresql-tuning.sh production
bash: ./postgresql-tuning.sh: Permission denied

✅ Solução:
$ chmod +x postgresql-tuning.sh
$ sudo ./postgresql-tuning.sh production
```

### Problema 2: "PostgreSQL não está em execução"

```bash
❌ Erro:
[ERROR] PostgreSQL não está em execução

✅ Solução:
$ sudo systemctl start postgresql
$ sleep 2
$ sudo ./postgresql-tuning.sh production
```

### Problema 3: PostgreSQL falhou em recarregar

```bash
❌ Erro:
[ERROR] Falha ao recarregar PostgreSQL!
[INFO] Tentando restaurar backup...

✅ Solução (automática):
# Script já tentou restaurar. Se ainda falhar:
$ sudo systemctl restart postgresql
$ sleep 3
$ sudo systemctl status postgresql

# Se continuar falhando:
$ sudo ./postgresql-rollback.sh
# Selecionar backup mais recente
```

### Problema 4: Cache hit ratio baixo

```bash
❌ Sintoma:
Cache Hit Ratio: 45%

✅ Solução:
# 1. Aguardar aquecimento (12-24h)
# 2. Executar VACUUM ANALYZE
$ sudo -u postgres psql realcred -c "VACUUM ANALYZE;"

# 3. Se problema persistir:
$ sudo -u postgres psql -c "ALTER SYSTEM SET shared_buffers = '4GB';"
$ sudo systemctl reload postgresql
```

---

## Rollback (Se Necessário)

### Opção 1: Restauração Automática (Recomendado)

```bash
# Ver backups disponíveis
ls -la /tmp/postgresql-backup-*/

# Restaurar (script vai pedir confirmação)
sudo ./postgresql-rollback.sh

# Selecionar backup desejado da lista
# Confirmar com "sim"

# Verificar resultado
sudo systemctl status postgresql
```

### Opção 2: Restauração Manual

```bash
# Encontrar backup
BACKUP="/tmp/postgresql-backup-20251117-143022"

# Restaurar configuração
sudo cp "$BACKUP/postgresql.conf.bak" /etc/postgresql/12/main/postgresql.conf

# Reiniciar PostgreSQL
sudo systemctl restart postgresql

# Verificar
sudo systemctl status postgresql
```

### Opção 3: Reset Completo

```bash
# Reset via PostgreSQL (volta para defaults)
sudo -u postgres psql -c "ALTER SYSTEM RESET ALL;"

# Recarregar
sudo systemctl reload postgresql

# Verificar
sudo -u postgres psql -c "SHOW shared_buffers;"
```

---

## Monitoramento Contínuo

### Script de Monitoramento Diário

```bash
#!/bin/bash
# save como: /usr/local/bin/pg-monitor-daily.sh

echo "=== PostgreSQL Daily Monitor ==="
echo "Data: $(date)"
echo ""

echo "1. Status:"
sudo systemctl status postgresql | head -5
echo ""

echo "2. Cache Hit Ratio:"
sudo -u postgres psql realcred -c "
    SELECT
        ROUND(100 * SUM(heap_blks_read) / (SUM(heap_blks_read) + SUM(heap_blks_hit)), 2) as table_hit_ratio
    FROM pg_statio_user_tables
    WHERE (heap_blks_read + heap_blks_hit) > 0;
"
echo ""

echo "3. Autovacuum Activity:"
sudo -u postgres psql realcred -c "
    SELECT
        tablename,
        last_autovacuum,
        last_autoanalyze
    FROM pg_stat_user_tables
    WHERE last_autovacuum IS NOT NULL
    ORDER BY last_autovacuum DESC
    LIMIT 5;
"
echo ""

echo "4. Slow Queries (>1s):"
sudo -u postgres psql realcred -c "
    SELECT
        LEFT(query, 80),
        mean_time::integer
    FROM pg_stat_statements
    WHERE mean_time > 1000
    ORDER BY mean_time DESC
    LIMIT 5;
" 2>/dev/null || echo "pg_stat_statements não configurado"
```

### Agendar Monitor Diário

```bash
# Adicionar ao crontab
sudo crontab -e

# Adicionar linha:
0 8 * * * /usr/local/bin/pg-monitor-daily.sh >> /var/log/postgresql-monitor.log 2>&1
```

---

## Timeline de Impacto Esperado

### Imediatamente Após Execução
- ✅ PostgreSQL continua rodando (downtime: <5s)
- ✅ Odoo roda normalmente
- ✅ Configuração aplicada

### Primeiras Horas (1-4h)
- 📊 Cache começando a aquencer
- 📊 Hit ratio ainda < 95%
- 📊 Performance gradualmente melhorando

### Primeiro Dia (4-24h)
- 🚀 Cache hit ratio > 95%
- 🚀 Queries mais rápidas (50% em média)
- 🚀 Odoo mais responsivo

### Estabilização (1-7 dias)
- ⚡ Cache hit ratio > 99%
- ⚡ Queries otimizadas (70-80% faster)
- ⚡ Performance máxima

---

## Checklist de Execução

### Antes da Execução

- [ ] Backup local de /etc/postgresql feito
- [ ] RAM suficiente verificada (free -h)
- [ ] Disco com espaço livre (df -h)
- [ ] PostgreSQL rodando (systemctl status postgresql)
- [ ] Aplicação Odoo funcionando
- [ ] Ninguém usando o sistema pesadamente

### Durante a Execução

- [ ] Script executado corretamente
- [ ] Sem erros no output
- [ ] PostgreSQL recarregou com sucesso
- [ ] Backup foi criado em /tmp/postgresql-backup-*/

### Após a Execução

- [ ] PostgreSQL ainda está rodando
- [ ] Odoo ainda está rodando
- [ ] Validação passou (./validate-postgresql-config.sh)
- [ ] Parâmetros aplicados (SHOW random_page_cost, etc)
- [ ] Logs sem erros críticos
- [ ] Performance melhorou (pode levar 24h)

---

## Suporte e Documentação

### Documentação Disponível

- **README Principal:** `POSTGRESQL-TUNING-README.md`
- **Scripts:** `postgresql-*.sh`
- **Este Guia:** `POSTGRESQL-EXECUTION-GUIDE.md`

### Referências Rápidas

```bash
# Ver configuração atual
sudo -u postgres psql -c "SELECT name, setting FROM pg_settings WHERE name IN ('shared_buffers', 'random_page_cost', 'effective_cache_size');"

# Health check Odoo + PG
sudo systemctl status odoo postgresql

# Performance check
./validate-postgresql-config.sh

# Ver últimos erros
sudo journalctl -u postgresql -n 50
```

---

## Pontos Críticos

🔴 **CRÍTICO: random_page_cost**

Este parâmetro DEVE ser 1.1 para SSDs. Se estiver diferente:
- Queries podem não ser otimizadas corretamente
- Índices podem não ser usados
- Performance pode ser 10x pior

✅ Verificar:
```bash
sudo -u postgres psql -c "SHOW random_page_cost;"
# Deve retornar: 1.1
```

🔴 **CRÍTICO: Backup**

Sempre manter backup antes de aplicar:
```bash
sudo cp -r /etc/postgresql ~/postgresql-backup-$(date +%Y%m%d)
```

🔴 **CRÍTICO: Downtime**

A aplicação de configuração requer downtime mínimo (<5s):
- Executar em janela de manutenção se possível
- Configurar clientes para retry automático
- Monitorar Odoo após execução

---

**Versão:** 1.0
**Última atualização:** 2025-11-17
**Status:** Pronto para Produção
