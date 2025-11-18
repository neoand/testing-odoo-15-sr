#!/bin/bash
# Script: setup-rag-cron.sh
# Description: Configura cron job para reindexação automática RAG a cada hora
# Usage: ./setup-rag-cron.sh
# Author: Claude + Anderson
# Created: 2025-11-18

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}⚙️  Setup RAG Cron Job${NC}"
echo -e "${BLUE}========================================${NC}"

# Configuração
PROJECT_ROOT="/Users/andersongoliveira/testing_odoo_15_sr"
REINDEX_SCRIPT="$PROJECT_ROOT/.claude/scripts/bash/rag-reindex-hourly.sh"

# Verificar se script existe
if [ ! -f "$REINDEX_SCRIPT" ]; then
    echo -e "${RED}❌ Script não encontrado: $REINDEX_SCRIPT${NC}"
    exit 1
fi

# Verificar permissões
if [ ! -x "$REINDEX_SCRIPT" ]; then
    echo -e "${YELLOW}⚠️  Script não executável, corrigindo...${NC}"
    chmod +x "$REINDEX_SCRIPT"
    echo -e "${GREEN}✅ Permissões corrigidas${NC}"
fi

# Criar entrada cron
CRON_ENTRY="0 * * * * $REINDEX_SCRIPT >> $PROJECT_ROOT/.claude/logs/cron-rag.log 2>&1"

# Verificar se cron já existe
if crontab -l 2>/dev/null | grep -q "$REINDEX_SCRIPT"; then
    echo -e "${YELLOW}⚠️  Cron job já existe!${NC}"
    echo ""
    echo -e "${BLUE}Cron atual:${NC}"
    crontab -l | grep "$REINDEX_SCRIPT"
    echo ""
    read -p "Deseja substituir? (s/n): " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo -e "${YELLOW}❌ Operação cancelada${NC}"
        exit 0
    fi

    # Remover cron antigo
    crontab -l 2>/dev/null | grep -v "$REINDEX_SCRIPT" | crontab -
    echo -e "${GREEN}✅ Cron antigo removido${NC}"
fi

# Adicionar novo cron
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Cron job configurado com sucesso!${NC}"
    echo ""
    echo -e "${BLUE}Detalhes:${NC}"
    echo -e "  • Frequência: ${YELLOW}A cada hora${NC} (minuto 0)"
    echo -e "  • Script: ${YELLOW}$REINDEX_SCRIPT${NC}"
    echo -e "  • Log: ${YELLOW}$PROJECT_ROOT/.claude/logs/cron-rag.log${NC}"
    echo ""
    echo -e "${BLUE}Próximas execuções:${NC}"
    current_hour=$(date +%H)
    for i in {1..3}; do
        next_hour=$(( (current_hour + i) % 24 ))
        echo -e "  • $(date -v +${i}H +"%Y-%m-%d ${next_hour}:00")"
    done
    echo ""
    echo -e "${GREEN}🎉 Setup completo!${NC}"
    echo ""
    echo -e "${YELLOW}Dica:${NC} Para ver cron jobs atuais: ${BLUE}crontab -l${NC}"
    echo -e "${YELLOW}Dica:${NC} Para remover: ${BLUE}crontab -l | grep -v rag-reindex | crontab -${NC}"
else
    echo -e "${RED}❌ Erro ao configurar cron job${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
