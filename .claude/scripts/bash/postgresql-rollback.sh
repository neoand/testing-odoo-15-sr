#!/bin/bash
# Script: postgresql-rollback.sh
# Description: Restaura configuração PostgreSQL anterior
# Usage: sudo ./postgresql-rollback.sh [backup_path]
# Author: Claude
# Created: 2025-11-17
# Version: 1.0
#
# Script para restaurar backup de configuração PostgreSQL
# criado pelo postgresql-tuning.sh

set -e

# ==================== CORES E OUTPUT ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# ==================== VERIFICAÇÕES ====================

if [ "$EUID" -ne 0 ]; then
    log_error "Este script DEVE ser executado com sudo"
    exit 1
fi

if ! command -v psql &> /dev/null; then
    log_error "PostgreSQL não está instalado"
    exit 1
fi

# ==================== BUSCAR BACKUPS ====================

if [ -z "$1" ]; then
    log_info "Nenhum backup especificado. Buscando backups disponíveis..."
    echo ""

    BACKUPS=($(ls -td /tmp/postgresql-backup-*/ 2>/dev/null | head -10))

    if [ ${#BACKUPS[@]} -eq 0 ]; then
        log_error "Nenhum backup encontrado em /tmp/postgresql-backup-*/"
        log_info "Verificar em outros locais ou fazer restauração manual"
        exit 1
    fi

    echo "Backups disponíveis:"
    for i in "${!BACKUPS[@]}"; do
        echo "  $((i+1))) ${BACKUPS[$i]}"
    done
    echo ""

    read -p "Selecione número do backup (1-${#BACKUPS[@]}): " SELECTION

    if ! [[ "$SELECTION" =~ ^[0-9]+$ ]] || [ "$SELECTION" -lt 1 ] || [ "$SELECTION" -gt ${#BACKUPS[@]} ]; then
        log_error "Seleção inválida"
        exit 1
    fi

    BACKUP_PATH="${BACKUPS[$((SELECTION-1))]}"
else
    BACKUP_PATH="$1"
fi

# Verificar se backup existe
if [ ! -d "$BACKUP_PATH" ]; then
    log_error "Backup não encontrado: $BACKUP_PATH"
    exit 1
fi

if [ ! -f "$BACKUP_PATH/postgresql.conf.bak" ]; then
    log_error "Arquivo postgresql.conf.bak não encontrado no backup"
    exit 1
fi

log_info "Backup selecionado: $BACKUP_PATH"

# ==================== VERIFICAR CONTEÚDO ====================

log_info "Verificando integridade do backup..."

# Contar linhas (arquivo válido deve ter 200+)
LINES=$(wc -l < "$BACKUP_PATH/postgresql.conf.bak")
if [ "$LINES" -lt 100 ]; then
    log_error "Arquivo de backup parece corrompido (apenas $LINES linhas)"
    exit 1
fi

log_success "Backup integridade OK ($LINES linhas)"

# ==================== CONFIRMAÇÃO ====================

echo ""
log_warning "ATENÇÃO: Esta operação vai restaurar configuração anterior do PostgreSQL"
echo ""
echo "Backup: $BACKUP_PATH"
echo "Arquivo: postgresql.conf.bak"
echo ""

read -p "Tem certeza que deseja restaurar? (sim/nao): " CONFIRM
if [ "$CONFIRM" != "sim" ]; then
    log_info "Operação cancelada"
    exit 0
fi

# ==================== RESTAURAÇÃO ====================

log_info "Iniciando restauração..."

# Encontrar diretório de configuração
PG_CONFIG_DIR=$(sudo -u postgres psql -t -c "SHOW config_file" | xargs dirname)
PG_CONFIG_FILE="$PG_CONFIG_DIR/postgresql.conf"

# Criar backup do backup (meta-backup)
META_BACKUP="/tmp/postgresql-config-before-rollback-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$META_BACKUP"
log_info "Salvando configuração atual em: $META_BACKUP"
sudo cp "$PG_CONFIG_FILE" "$META_BACKUP/postgresql.conf.current"

# Restaurar
log_info "Restaurando postgresql.conf..."
sudo cp "$BACKUP_PATH/postgresql.conf.bak" "$PG_CONFIG_FILE"
log_success "postgresql.conf restaurado"

# Restaurar pg_hba.conf se existir
if [ -f "$BACKUP_PATH/pg_hba.conf.bak" ]; then
    PG_HBA_FILE="$PG_CONFIG_DIR/pg_hba.conf"
    log_info "Restaurando pg_hba.conf..."
    sudo cp "$BACKUP_PATH/pg_hba.conf.bak" "$PG_HBA_FILE"
    log_success "pg_hba.conf restaurado"
fi

# ==================== RELOAD ====================

log_info "Recarregando PostgreSQL..."

if sudo systemctl is-active --quiet postgresql; then
    log_info "PostgreSQL já está rodando, recarregando..."
    sudo systemctl reload postgresql
    sleep 2
else
    log_info "Iniciando PostgreSQL..."
    sudo systemctl start postgresql
    sleep 2
fi

# Verificar se recarregou corretamente
if ! sudo systemctl is-active --quiet postgresql; then
    log_error "PostgreSQL falhou ao recarregar!"
    log_warning "Tentando restart completo..."
    sudo systemctl restart postgresql
    sleep 2

    if ! sudo systemctl is-active --quiet postgresql; then
        log_error "PostgreSQL ainda não está rodando!"
        log_info "Tentar restaurar manualmente:"
        log_info "  sudo systemctl start postgresql"
        exit 1
    fi
fi

log_success "PostgreSQL recarregado com sucesso"

# ==================== VERIFICAÇÃO ====================

log_info "Verificando restauração..."

# Verificar alguns parâmetros
SHARED_BUFFERS=$(sudo -u postgres psql -t -c "SHOW shared_buffers;" | xargs)
WORK_MEM=$(sudo -u postgres psql -t -c "SHOW work_mem;" | xargs)
RANDOM_PAGE_COST=$(sudo -u postgres psql -t -c "SHOW random_page_cost;" | xargs)

log_info "Parâmetros após restauração:"
log_info "  shared_buffers = $SHARED_BUFFERS"
log_info "  work_mem = $WORK_MEM"
log_info "  random_page_cost = $RANDOM_PAGE_COST"

# ==================== RESUMO ====================

echo ""
log_success "RESTAURAÇÃO COMPLETA!"
echo ""
log_info "Resumo:"
log_info "  Backup restaurado: $BACKUP_PATH"
log_info "  Config anterior salva: $META_BACKUP"
log_info "  PostgreSQL status: $(sudo systemctl is-active postgresql)"
echo ""

# Se desejado, mostrar diff
log_info "Para ver diferenças entre configurações:"
log_info "  diff $BACKUP_PATH/postgresql.conf.bak $META_BACKUP/postgresql.conf.current"
echo ""

# ==================== PRÓXIMOS PASSOS ====================

log_info "Próximas recomendações:"
echo "  1. Monitorar application: tail -f /var/log/odoo/odoo-server.log"
echo "  2. Verificar PostgreSQL: sudo tail -f /var/log/postgresql/postgresql.log"
echo "  3. Testar conexões: sudo -u postgres psql -l"
echo "  4. Se problema persistir, entre em contato com suporte"
echo ""

exit 0
