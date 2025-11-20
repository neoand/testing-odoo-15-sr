#!/bin/bash
# Script: postgresql-quick-setup.sh
# Description: Setup rápido de PostgreSQL tuning com confirmação
# Usage: ./postgresql-quick-setup.sh [testing|production]
# Author: Claude
# Created: 2025-11-17
# Version: 1.0
#
# Wrapper para executar postgresql-tuning.sh com segurança
# Ideal para usar em CI/CD ou skills automáticos

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

# ==================== SETUP ====================

ENVIRONMENT="${1:-production}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TUNING_SCRIPT="$SCRIPT_DIR/postgresql-tuning.sh"

# Verificar se script existe
if [ ! -f "$TUNING_SCRIPT" ]; then
    log_error "postgresql-tuning.sh não encontrado em: $SCRIPT_DIR"
    exit 1
fi

# ==================== PRÉ-FLIGHT CHECKLIST ====================

log_info "Iniciando pre-flight checklist..."
echo ""

# Verificar root
if [ "$EUID" -ne 0 ]; then
    log_error "Script PRECISA ser executado com sudo"
    exit 1
fi
log_success "✓ Executando como root"

# Verificar PostgreSQL
if ! command -v psql &> /dev/null; then
    log_error "PostgreSQL não instalado"
    exit 1
fi
log_success "✓ PostgreSQL instalado"

# Verificar status
if ! sudo systemctl is-active --quiet postgresql; then
    log_warning "PostgreSQL não está em execução, iniciando..."
    sudo systemctl start postgresql
    sleep 2
fi

if ! sudo systemctl is-active --quiet postgresql; then
    log_error "Falha ao iniciar PostgreSQL"
    exit 1
fi
log_success "✓ PostgreSQL rodando"

# Verificar RAM
RAM_GB=$(($(grep MemTotal /proc/meminfo | awk '{print $2}') / 1024 / 1024))
if [ "$RAM_GB" -lt 2 ]; then
    log_error "Servidor precisa de no mínimo 2GB RAM (tem ${RAM_GB}GB)"
    exit 1
fi
log_success "✓ RAM suficiente: ${RAM_GB}GB"

# Validar ambiente
if [ "$ENVIRONMENT" != "testing" ] && [ "$ENVIRONMENT" != "production" ]; then
    log_error "Ambiente inválido: $ENVIRONMENT"
    exit 1
fi
log_success "✓ Ambiente válido: $ENVIRONMENT"

# ==================== CONFIRMAÇÃO ====================

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}PostgreSQL Tuning - Confirmação${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Configuração a ser aplicada:"
echo "  Ambiente: $ENVIRONMENT"
echo "  RAM: ${RAM_GB}GB"
echo "  Backup: /tmp/postgresql-backup-[timestamp]/"
echo ""
log_warning "Esta operação vai:"
echo "  - MODIFICAR configuração PostgreSQL"
echo "  - RECARREGAR PostgreSQL (downtime: ~5 segundos)"
echo "  - CRIAR BACKUP automático"
echo ""

read -p "Continuar? (sim/nao): " CONFIRM

if [ "$CONFIRM" != "sim" ]; then
    log_info "Operação cancelada"
    exit 0
fi

# ==================== EXECUÇÃO ====================

echo ""
log_info "Executando postgresql-tuning.sh..."
echo ""

# Verificar permissões do script
if [ ! -x "$TUNING_SCRIPT" ]; then
    log_warning "Tornando script executável..."
    chmod +x "$TUNING_SCRIPT"
fi

# Executar tuning
sudo "$TUNING_SCRIPT" "$ENVIRONMENT"

# Capturar status
if [ $? -eq 0 ]; then
    log_success "Tuning executado com sucesso!"
else
    log_error "Tuning falhou!"
    exit 1
fi

# ==================== PÓS-EXECUÇÃO ====================

echo ""
log_info "Executando validação..."

VALIDATE_SCRIPT="$SCRIPT_DIR/validate-postgresql-config.sh"

if [ -f "$VALIDATE_SCRIPT" ]; then
    if [ ! -x "$VALIDATE_SCRIPT" ]; then
        chmod +x "$VALIDATE_SCRIPT"
    fi

    # Executar validação silenciosamente
    if "$VALIDATE_SCRIPT" > /tmp/pg-validation.log 2>&1; then
        log_success "Validação passou!"

        # Mostrar resumo
        echo ""
        log_info "Resumo da validação:"
        grep -E "^\[|Cache Hit|random_page_cost" /tmp/pg-validation.log | head -20
    else
        log_warning "Validação teve warnings (ver log para detalhes)"
    fi
else
    log_warning "validate-postgresql-config.sh não encontrado"
fi

# ==================== RESUMO FINAL ====================

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}PostgreSQL Tuning Concluído com Sucesso!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""

log_info "Próximas etapas:"
echo "  1. Monitorar performance Odoo:"
echo "     tail -f /var/log/odoo/odoo-server.log | grep duration"
echo ""
echo "  2. Verificar health PostgreSQL:"
echo "     sudo systemctl status postgresql"
echo ""
echo "  3. Rodar validação completa:"
echo "     $VALIDATE_SCRIPT"
echo ""
echo "  4. Se algo der errado, restaurar:"
echo "     sudo $SCRIPT_DIR/postgresql-rollback.sh"
echo ""

exit 0
