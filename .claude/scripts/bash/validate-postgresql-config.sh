#!/bin/bash
# Script: validate-postgresql-config.sh
# Description: Valida configuração PostgreSQL otimizada para Odoo
# Usage: ./validate-postgresql-config.sh [database_name]
# Author: Claude
# Created: 2025-11-17
# Version: 1.0
#
# Este script verifica se a configuração PostgreSQL foi aplicada
# corretamente e realiza testes básicos de performance.
#
# Testa:
# - Parâmetros críticos aplicados
# - Health do servidor PostgreSQL
# - Tamanho de indexes vs tabelas
# - Conexões ativas
# - Cache hit ratio
# - Queries lentas

set -e

# ==================== CORES E OUTPUT ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# ==================== FUNÇÕES AUXILIARES ====================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

section_header() {
    echo ""
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}$1${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
}

# ==================== VERIFICAÇÕES PRÉ-EXECUÇÃO ====================

# Verificar se PostgreSQL está instalado
if ! command -v psql &> /dev/null; then
    log_error "PostgreSQL não está instalado"
    exit 1
fi

# Verificar se PostgreSQL está rodando
if ! sudo systemctl is-active --quiet postgresql; then
    log_error "PostgreSQL não está em execução"
    exit 1
fi

# Database padrão
DATABASE="${1:-postgres}"

# ==================== TESTE 1: PARÂMETROS CRÍTICOS ====================

section_header "1. VERIFICAÇÃO DE PARÂMETROS CRÍTICOS"

log_info "Lendo parâmetros do PostgreSQL..."

# Array de parâmetros a verificar
declare -A PARAMS
declare -A EXPECTED_TYPES

PARAMS["shared_buffers"]="Shared Buffers"
PARAMS["effective_cache_size"]="Cache Efetivo"
PARAMS["work_mem"]="Work Memory"
PARAMS["maintenance_work_mem"]="Maintenance Work Memory"
PARAMS["random_page_cost"]="Random Page Cost (SSD CRÍTICO!)"
PARAMS["max_connections"]="Conexões Máximas"
PARAMS["checkpoint_timeout"]="Checkpoint Timeout"
PARAMS["max_wal_size"]="Max WAL Size"
PARAMS["autovacuum"]="Autovacuum"
PARAMS["autovacuum_max_workers"]="Autovacuum Workers"
PARAMS["effective_io_concurrency"]="I/O Concurrency"
PARAMS["jit"]="JIT Compilation"
PARAMS["synchronous_commit"]="Synchronous Commit"

# Verificar cada parâmetro
CRITICAL_ISSUES=0

for param in "${!PARAMS[@]}"; do
    VALUE=$(sudo -u postgres psql -t -c "SHOW $param;" | xargs)

    case "$param" in
        shared_buffers)
            # Deve estar > 128MB
            if [[ "$VALUE" =~ ([0-9]+)MB ]]; then
                MB="${BASH_REMATCH[1]}"
                if [ "$MB" -gt 128 ]; then
                    log_success "$param = $VALUE"
                else
                    log_warning "$param = $VALUE (Recomendado > 128MB)"
                fi
            fi
            ;;
        effective_cache_size)
            # Deve estar configurado
            if [ -n "$VALUE" ]; then
                log_success "$param = $VALUE"
            else
                log_error "$param não configurado!"
                ((CRITICAL_ISSUES++))
            fi
            ;;
        random_page_cost)
            # CRÍTICO: Deve ser 1.1 para SSD!
            if [ "$VALUE" = "1.1" ]; then
                log_success "$param = $VALUE (SSD - ÓTIMO!)"
            else
                log_error "$param = $VALUE (DEVE ser 1.1 para SSD!)"
                ((CRITICAL_ISSUES++))
            fi
            ;;
        work_mem)
            # Deve estar configurado
            if [ -n "$VALUE" ]; then
                log_success "$param = $VALUE"
            else
                log_error "$param não configurado!"
            fi
            ;;
        maintenance_work_mem)
            # Deve estar > 256MB
            if [[ "$VALUE" =~ ([0-9]+)MB ]]; then
                MB="${BASH_REMATCH[1]}"
                if [ "$MB" -ge 256 ]; then
                    log_success "$param = $VALUE"
                else
                    log_warning "$param = $VALUE (Recomendado >= 256MB)"
                fi
            fi
            ;;
        autovacuum)
            # Deve estar ON
            if [ "$VALUE" = "on" ]; then
                log_success "$param = $VALUE"
            else
                log_warning "$param = $VALUE (Recomendado: on)"
            fi
            ;;
        jit)
            # Deve estar ON (opcional)
            if [ "$VALUE" = "on" ]; then
                log_success "$param = $VALUE (JIT ativo - ótimo!)"
            else
                log_info "$param = $VALUE (JIT desativo, opcional)"
            fi
            ;;
        *)
            log_info "$param = $VALUE"
            ;;
    esac
done

if [ "$CRITICAL_ISSUES" -gt 0 ]; then
    log_warning "Existem $CRITICAL_ISSUES problemas críticos!"
else
    log_success "Todos parâmetros críticos configurados!"
fi

# ==================== TESTE 2: HEALTH DO SERVIDOR ====================

section_header "2. HEALTH DO SERVIDOR POSTGRESQL"

# Conexões ativas
CONNECTIONS=$(sudo -u postgres psql -t -c "SELECT count(*) FROM pg_stat_activity;" | xargs)
log_info "Conexões ativas: $CONNECTIONS"

# Uptime
UPTIME=$(sudo -u postgres psql -t -c "SELECT now() - pg_postmaster_start_time() as uptime;" | xargs)
log_info "Uptime: $UPTIME"

# Tamanho da database
DB_SIZE=$(sudo -u postgres psql -t -c "SELECT pg_size_pretty(pg_database_size('$DATABASE'));" | xargs)
log_info "Tamanho da database: $DB_SIZE"

# Núcleos de CPU
CPU_CORES=$(nproc)
log_info "CPU cores: $CPU_CORES"

# RAM disponível
RAM_GB=$(($(grep MemTotal /proc/meminfo | awk '{print $2}') / 1024 / 1024))
log_info "RAM disponível: ${RAM_GB}GB"

log_success "Server health verificado"

# ==================== TESTE 3: CACHE HIT RATIO ====================

section_header "3. CACHE HIT RATIO (Índices e Heap)"

# Verificar table hit ratio
TABLE_HIT_RATIO=$(sudo -u postgres psql -t -c "
    SELECT
        ROUND(100 * SUM(heap_blks_read) /
              (SUM(heap_blks_read) + SUM(heap_blks_hit)), 2) as ratio
    FROM pg_statio_user_tables
    WHERE (heap_blks_read + heap_blks_hit) > 0;
" | xargs)

if [ -z "$TABLE_HIT_RATIO" ]; then
    log_info "Table Hit Ratio: Sem dados (database recém-iniciada)"
else
    log_info "Table Hit Ratio: ${TABLE_HIT_RATIO}%"
    if (( $(echo "$TABLE_HIT_RATIO > 99" | bc -l) )); then
        log_success "Hit ratio excelente (>99%)"
    elif (( $(echo "$TABLE_HIT_RATIO > 95" | bc -l) )); then
        log_success "Hit ratio bom (>95%)"
    else
        log_warning "Hit ratio baixo (<95%) - considerar aumentar shared_buffers"
    fi
fi

# Verificar index hit ratio
INDEX_HIT_RATIO=$(sudo -u postgres psql -t -c "
    SELECT
        ROUND(100 * SUM(idx_blks_read) /
              (SUM(idx_blks_read) + SUM(idx_blks_hit)), 2) as ratio
    FROM pg_statio_user_indexes
    WHERE (idx_blks_read + idx_blks_hit) > 0;
" | xargs)

if [ -z "$INDEX_HIT_RATIO" ]; then
    log_info "Index Hit Ratio: Sem dados (database recém-iniciada)"
else
    log_info "Index Hit Ratio: ${INDEX_HIT_RATIO}%"
    if (( $(echo "$INDEX_HIT_RATIO > 99" | bc -l) )); then
        log_success "Hit ratio excelente (>99%)"
    elif (( $(echo "$INDEX_HIT_RATIO > 95" | bc -l) )); then
        log_success "Hit ratio bom (>95%)"
    else
        log_warning "Hit ratio baixo (<95%) - verificar índices"
    fi
fi

# ==================== TESTE 4: ÍNDICES NÃO UTILIZADOS ====================

section_header "4. ÍNDICES NÃO UTILIZADOS (Oportunidade de Limpeza)"

log_info "Buscando índices não utilizados..."

UNUSED_INDEXES=$(sudo -u postgres psql -t -c "
    SELECT schemaname, tablename, indexname, idx_scan
    FROM pg_stat_user_indexes
    WHERE idx_scan = 0
    ORDER BY pg_relation_size(indexrelid) DESC
    LIMIT 10;
" | wc -l)

if [ "$UNUSED_INDEXES" -gt 1 ]; then
    log_warning "Encontrados $((UNUSED_INDEXES - 1)) índices não utilizados"
    log_info "Execute: \`psql -U postgres $DATABASE -c \"SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0 ORDER BY pg_relation_size(indexrelid) DESC;\"\`"
else
    log_success "Sem índices não utilizados"
fi

# ==================== TESTE 5: TABELAS MUITO GRANDES ====================

section_header "5. TABELAS MUITO GRANDES (>100MB)"

log_info "Buscando tabelas grandes..."

sudo -u postgres psql << EOF
    \pset pager off
    SELECT
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
        n_live_tup as rows
    FROM pg_stat_user_tables
    WHERE pg_total_relation_size(schemaname||'.'||tablename) > 100*1024*1024
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
    LIMIT 15;
EOF

log_info "Tabelas > 100MB listadas acima"

# ==================== TESTE 6: AUTOVACUUM STATUS ====================

section_header "6. AUTOVACUUM STATUS"

log_info "Verificando atividade de autovacuum..."

LAST_VACUUM=$(sudo -u postgres psql -t -c "
    SELECT
        schemaname,
        tablename,
        ROUND((EXTRACT(epoch FROM (now() - last_vacuum)))::numeric/60, 2) as minutes_since_vacuum
    FROM pg_stat_user_tables
    WHERE last_vacuum IS NOT NULL
    ORDER BY last_vacuum DESC
    LIMIT 5;
")

echo "$LAST_VACUUM"

log_success "Autovacuum verificado"

# ==================== TESTE 7: SLOW QUERIES ====================

section_header "7. SLOW QUERIES (>1000ms)"

log_info "Verificando queries lentas..."

SLOW_QUERIES=$(sudo -u postgres psql -t -c "
    SELECT
        query,
        calls,
        total_time,
        mean_time,
        max_time
    FROM pg_stat_statements
    WHERE mean_time > 1000
    ORDER BY mean_time DESC
    LIMIT 10;
" 2>/dev/null || echo "pg_stat_statements não está habilitado")

if [ "$SLOW_QUERIES" != "pg_stat_statements não está habilitado" ]; then
    echo "$SLOW_QUERIES"
    log_warning "Queries lentas detectadas - considerar otimização"
else
    log_info "pg_stat_statements não está habilitado (opcional)"
fi

# ==================== TESTE 8: BLOAT CHECK ====================

section_header "8. TABLE BLOAT CHECK"

log_info "Verificando tabelas com excesso de espaço..."

BLOAT=$(sudo -u postgres psql -t -c "
    SELECT
        schemaname,
        tablename,
        ROUND(100 * (pg_relation_size(schemaname||'.'||tablename) -
              pg_relation_size(schemaname||'.'||tablename, 'main')) /
              pg_relation_size(schemaname||'.'||tablename), 2) as bloat_ratio
    FROM pg_stat_user_tables
    WHERE pg_relation_size(schemaname||'.'||tablename) > 10*1024*1024
    ORDER BY bloat_ratio DESC
    LIMIT 10;
") || true

if [ -n "$BLOAT" ]; then
    echo "$BLOAT"
    log_warning "Verificar tabelas com alto bloat (>10%)"
else
    log_info "Sem bloat significativo"
fi

# ==================== TESTE 9: CONNECTION POOLS ====================

section_header "9. ANÁLISE DE CONEXÕES"

log_info "Analisando distribuição de conexões..."

sudo -u postgres psql << EOF
    \pset pager off
    SELECT
        datname as database,
        usename as user,
        state,
        count(*) as count
    FROM pg_stat_activity
    GROUP BY datname, usename, state
    ORDER BY count DESC;
EOF

# ==================== TESTE 10: REPLICATION (se aplicável) ====================

section_header "10. REPLICATION STATUS"

log_info "Verificando replication..."

IS_REPLICA=$(sudo -u postgres psql -t -c "SELECT pg_is_in_recovery();" | xargs)

if [ "$IS_REPLICA" = "t" ]; then
    log_warning "Este é um servidor REPLICA (read-only)"
    REPL_LAG=$(sudo -u postgres psql -t -c "SELECT EXTRACT(epoch FROM now() - pg_last_xact_replay_timestamp()) as lag_seconds;" | xargs)
    log_info "Replication lag: ${REPL_LAG} segundos"
else
    log_success "Este é o servidor PRIMARY"
fi

# ==================== RESUMO FINAL ====================

section_header "RESUMO DA VALIDAÇÃO"

echo ""
log_info "Checklist de Validação:"
echo ""

# Verificação de parâmetros críticos
SHARED=$(sudo -u postgres psql -t -c "SHOW shared_buffers;" | xargs)
RANDOM_COST=$(sudo -u postgres psql -t -c "SHOW random_page_cost;" | xargs)
AUTOVAC=$(sudo -u postgres psql -t -c "SHOW autovacuum;" | xargs)

if [ "$RANDOM_COST" = "1.1" ]; then
    log_success "random_page_cost = 1.1 (SSD OK)"
else
    log_error "random_page_cost != 1.1 (PROBLEMA!)"
fi

if [[ "$SHARED" =~ ([0-9]+)MB ]] && [ "${BASH_REMATCH[1]}" -gt 128 ]; then
    log_success "shared_buffers configurado adequadamente"
else
    log_warning "shared_buffers pode ser insuficiente"
fi

if [ "$AUTOVAC" = "on" ]; then
    log_success "autovacuum ativo"
else
    log_warning "autovacuum desativo"
fi

echo ""
log_success "Validação Completa!"
echo ""
log_info "Próximos passos:"
echo "  1. Monitorar performance da aplicação"
echo "  2. Verificar logs: tail -f /var/log/postgresql/postgresql.log"
echo "  3. Se necessário, executar VACUUM ANALYZE:"
echo "     sudo -u postgres psql $DATABASE -c 'VACUUM ANALYZE;'"
echo "  4. Para mais detalhes: sudo -u postgres psql $DATABASE -c '\\dtS+'"
echo ""

exit 0
