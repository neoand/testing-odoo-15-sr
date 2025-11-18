#!/bin/bash
# Script: postgresql-tuning.sh
# Description: Tuning automático de PostgreSQL 12 para Odoo 15
# Usage: sudo ./postgresql-tuning.sh [testing|production]
# Author: Claude
# Created: 2025-11-17
# Version: 1.0
#
# Este script detecta a RAM disponível e configura PostgreSQL
# de forma otimizada para Odoo 15 em servidores com SSD.
#
# Parâmetros críticos:
# - random_page_cost = 1.1 (DEVE ser 1.1 para SSD!)
# - shared_buffers = 25% RAM
# - effective_cache_size = 75% RAM
# - work_mem = 50MB
# - maintenance_work_mem = 1GB
#
# BACKUP AUTOMÁTICO: pg_hba.conf e postgresql.conf são salvos em /tmp/

set -e

# ==================== CORES E OUTPUT ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==================== FUNÇÕES AUXILIARES ====================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ==================== VERIFICAÇÕES PRÉ-EXECUÇÃO ====================

# Verificar se é root
if [ "$EUID" -ne 0 ]; then
    log_error "Este script DEVE ser executado com sudo"
    exit 1
fi

# Verificar se PostgreSQL está instalado
if ! command -v psql &> /dev/null; then
    log_error "PostgreSQL não está instalado"
    exit 1
fi

# Verificar se PostgreSQL está rodando
if ! sudo systemctl is-active --quiet postgresql; then
    log_error "PostgreSQL não está em execução"
    log_info "Iniciando PostgreSQL..."
    sudo systemctl start postgresql
fi

# Detectar versão do PostgreSQL
PG_VERSION=$(sudo -u postgres psql --version | grep -oP '\d+' | head -1)
if [ "$PG_VERSION" != "12" ] && [ "$PG_VERSION" != "13" ] && [ "$PG_VERSION" != "14" ] && [ "$PG_VERSION" != "15" ]; then
    log_warning "PostgreSQL versão $PG_VERSION detectada. Script foi testado em 12-15"
fi

log_info "PostgreSQL versão $PG_VERSION detectada"

# ==================== DETECÇÃO DE CONFIGURAÇÃO ====================

# Determinar ambiente
ENVIRONMENT="${1:-production}"
if [ "$ENVIRONMENT" != "testing" ] && [ "$ENVIRONMENT" != "production" ]; then
    log_error "Ambiente inválido. Use: testing ou production"
    exit 1
fi

log_info "Ambiente: $ENVIRONMENT"

# Detectar RAM disponível
TOTAL_RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
TOTAL_RAM_GB=$((TOTAL_RAM_KB / 1024 / 1024))

log_info "RAM disponível: ${TOTAL_RAM_GB}GB"

# Validar RAM mínima
if [ "$TOTAL_RAM_GB" -lt 2 ]; then
    log_error "Servidor precisa de no mínimo 2GB de RAM"
    exit 1
fi

# ==================== CÁLCULO DE PARÂMETROS ====================

# shared_buffers = 25% da RAM (padrão para Odoo)
SHARED_BUFFERS_MB=$((TOTAL_RAM_GB * 1024 / 4))
if [ "$SHARED_BUFFERS_MB" -gt 40960 ]; then
    SHARED_BUFFERS_MB=40960  # Máximo recomendado
fi

# effective_cache_size = 75% da RAM (para planner)
EFFECTIVE_CACHE_MB=$((TOTAL_RAM_GB * 1024 * 3 / 4))

# work_mem = RAM / (max_connections * 2)
# Padrão: 50MB para Odoo com workers
WORK_MEM_MB=50

# maintenance_work_mem = 10% da RAM
MAINTENANCE_WORK_MB=$((TOTAL_RAM_GB * 1024 / 10))
if [ "$MAINTENANCE_WORK_MB" -lt 256 ]; then
    MAINTENANCE_WORK_MB=256
fi
if [ "$MAINTENANCE_WORK_MB" -gt 2048 ]; then
    MAINTENANCE_WORK_MB=2048  # Máximo recomendado
fi

# Detectar tipo de storage (SSD vs HDD)
# random_page_cost: 1.1 para SSD, 4.0 para HDD
RANDOM_PAGE_COST=1.1  # CRÍTICO: SSDs usam 1.1!

log_info "Parâmetros calculados:"
log_info "  shared_buffers = ${SHARED_BUFFERS_MB}MB"
log_info "  effective_cache_size = ${EFFECTIVE_CACHE_MB}MB"
log_info "  work_mem = ${WORK_MEM_MB}MB"
log_info "  maintenance_work_mem = ${MAINTENANCE_WORK_MB}MB"
log_info "  random_page_cost = ${RANDOM_PAGE_COST}"

# ==================== BACKUP DE CONFIGURAÇÃO ====================

PG_CONFIG_DIR=$(sudo -u postgres psql -t -c "SHOW config_file" | xargs dirname)
PG_CONFIG_FILE="$PG_CONFIG_DIR/postgresql.conf"
PG_HBA_FILE="$PG_CONFIG_DIR/pg_hba.conf"

BACKUP_DIR="/tmp/postgresql-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

log_info "Fazendo backup de configuração em: $BACKUP_DIR"
sudo cp "$PG_CONFIG_FILE" "$BACKUP_DIR/postgresql.conf.bak"
sudo cp "$PG_HBA_FILE" "$BACKUP_DIR/pg_hba.conf.bak"
log_success "Backup realizado"

# ==================== PARÂMETROS ESPECÍFICOS POR AMBIENTE ====================

if [ "$ENVIRONMENT" = "production" ]; then
    MAX_CONNECTIONS=200
    CHECKPOINT_TIMEOUT=15  # 15 minutos
    MAX_WAL_SIZE=4         # 4GB
    AUTOVACUUM_MAX_WORKERS=3
    AUTOVACUUM_NAPTIME=10
    AUTOVACUUM_VACUUM_SCALE_FACTOR=0.05
    AUTOVACUUM_ANALYZE_SCALE_FACTOR=0.02
else
    # testing
    MAX_CONNECTIONS=100
    CHECKPOINT_TIMEOUT=10
    MAX_WAL_SIZE=2
    AUTOVACUUM_MAX_WORKERS=2
    AUTOVACUUM_NAPTIME=30
    AUTOVACUUM_VACUUM_SCALE_FACTOR=0.1
    AUTOVACUUM_ANALYZE_SCALE_FACTOR=0.05
fi

# ==================== APLICAÇÃO DE CONFIGURAÇÃO ====================

log_info "Aplicando configuração PostgreSQL..."

# Usar ALTER SYSTEM para aplicar de forma persistente
sudo -u postgres psql << EOF

-- ========== SHARED_BUFFERS E CACHE ==========
ALTER SYSTEM SET shared_buffers = '${SHARED_BUFFERS_MB}MB';
ALTER SYSTEM SET effective_cache_size = '${EFFECTIVE_CACHE_MB}MB';

-- ========== RANDOM PAGE COST (CRÍTICO PARA SSD!) ==========
ALTER SYSTEM SET random_page_cost = ${RANDOM_PAGE_COST};

-- ========== MEMORY ALLOCATION ==========
ALTER SYSTEM SET work_mem = '${WORK_MEM_MB}MB';
ALTER SYSTEM SET maintenance_work_mem = '${MAINTENANCE_WORK_MB}MB';

-- ========== CONNECTIONS ==========
ALTER SYSTEM SET max_connections = ${MAX_CONNECTIONS};
ALTER SYSTEM SET superuser_reserved_connections = 5;

-- ========== CHECKPOINT E WAL ==========
ALTER SYSTEM SET checkpoint_timeout = '${CHECKPOINT_TIMEOUT}min';
ALTER SYSTEM SET max_wal_size = '${MAX_WAL_SIZE}GB';
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET min_wal_size = '1GB';

-- ========== LOGGING ==========
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_duration = off;
ALTER SYSTEM SET log_statement = 'ddl';
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;

-- ========== QUERY PLANNING ==========
ALTER SYSTEM SET seq_page_cost = 1.0;
ALTER SYSTEM SET cpu_tuple_cost = 0.01;
ALTER SYSTEM SET cpu_index_tuple_cost = 0.005;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- ========== AUTOVACUUM OTIMIZADO ==========
ALTER SYSTEM SET autovacuum = on;
ALTER SYSTEM SET autovacuum_max_workers = ${AUTOVACUUM_MAX_WORKERS};
ALTER SYSTEM SET autovacuum_naptime = '${AUTOVACUUM_NAPTIME}s';
ALTER SYSTEM SET autovacuum_vacuum_scale_factor = ${AUTOVACUUM_VACUUM_SCALE_FACTOR};
ALTER SYSTEM SET autovacuum_analyze_scale_factor = ${AUTOVACUUM_ANALYZE_SCALE_FACTOR};
ALTER SYSTEM SET autovacuum_vacuum_cost_delay = '10ms';
ALTER SYSTEM SET autovacuum_vacuum_cost_limit = 1000;

-- ========== LOCK MANAGEMENT ==========
ALTER SYSTEM SET deadlock_timeout = '1s';

-- ========== OUTROS OTIMIZAÇÕES ==========
ALTER SYSTEM SET fsync = on;
ALTER SYSTEM SET synchronous_commit = 'local';
ALTER SYSTEM SET full_page_writes = on;
ALTER SYSTEM SET jit = on;
ALTER SYSTEM SET jit_above_cost = 100000;
ALTER SYSTEM SET jit_inline_above_cost = 500000;
ALTER SYSTEM SET jit_optimize_above_cost = 500000;

EOF

log_success "Configuração aplicada via ALTER SYSTEM"

# ==================== RELOAD DE CONFIGURAÇÃO ====================

log_info "Recarregando configuração do PostgreSQL..."
sudo systemctl reload postgresql

# Aguardar reload completar
sleep 2

# Verificar se reload foi bem-sucedido
if sudo systemctl is-active --quiet postgresql; then
    log_success "PostgreSQL recarregado com sucesso"
else
    log_error "Falha ao recarregar PostgreSQL!"
    log_info "Tentando restaurar backup..."
    sudo cp "$BACKUP_DIR/postgresql.conf.bak" "$PG_CONFIG_FILE"
    sudo systemctl restart postgresql
    exit 1
fi

# ==================== VALIDAÇÃO ====================

log_info "Validando aplicação de configuração..."

SHARED_BUFFERS_APPLIED=$(sudo -u postgres psql -t -c "SHOW shared_buffers;")
EFFECTIVE_CACHE_APPLIED=$(sudo -u postgres psql -t -c "SHOW effective_cache_size;")
RANDOM_PAGE_COST_APPLIED=$(sudo -u postgres psql -t -c "SHOW random_page_cost;")

log_info "Valores aplicados:"
log_info "  shared_buffers = $SHARED_BUFFERS_APPLIED"
log_info "  effective_cache_size = $EFFECTIVE_CACHE_APPLIED"
log_info "  random_page_cost = $RANDOM_PAGE_COST_APPLIED"

# Validar random_page_cost (CRÍTICO!)
if [ "$RANDOM_PAGE_COST_APPLIED" = "1.1" ]; then
    log_success "random_page_cost = 1.1 (SSD - CORRETO!)"
else
    log_warning "random_page_cost != 1.1 (Verificar se é SSD!)"
fi

# ==================== RESUMO ====================

log_info ""
log_success "PostgreSQL Tuning Completo!"
log_info ""
log_info "Resumo:"
log_info "  Ambiente: $ENVIRONMENT"
log_info "  RAM detectada: ${TOTAL_RAM_GB}GB"
log_info "  Backup: $BACKUP_DIR"
log_info ""
log_info "Próximos passos:"
log_info "  1. Executar: ./validate-postgresql-config.sh"
log_info "  2. Monitorar logs: tail -f /var/log/postgresql/postgresql.log"
log_info "  3. Em caso de problemas, usar restore abaixo"
log_info ""
log_info "ROLLBACK (se necessário):"
log_info "  sudo cp $BACKUP_DIR/postgresql.conf.bak $PG_CONFIG_FILE"
log_info "  sudo systemctl restart postgresql"
log_info ""

exit 0
