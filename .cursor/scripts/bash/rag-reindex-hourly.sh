#!/bin/bash
# Script: rag-reindex-hourly.sh
# Description: Reindexação automática RAG a cada hora (incremental - apenas arquivos modificados)
# Usage: ./rag-reindex-hourly.sh
# Author: Claude + Anderson
# Created: 2025-11-18

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuração
PROJECT_ROOT="/Users/andersongoliveira/testing_odoo_15_sr"
PYTHON_SCRIPT="$PROJECT_ROOT/.claude/scripts/python/index-knowledge.py"
LOG_DIR="$PROJECT_ROOT/.claude/logs"
LOG_FILE="$LOG_DIR/rag-reindex.log"

# Criar diretório de logs se não existe
mkdir -p "$LOG_DIR"

# Header do log
echo -e "${BLUE}========================================${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}🔄 RAG Reindexação Incremental${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}📅 Data: $(date '+%Y-%m-%d %H:%M:%S')${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}========================================${NC}" | tee -a "$LOG_FILE"

# Ir para diretório do projeto
cd "$PROJECT_ROOT" || exit 1

# Executar reindexação incremental (sem --reindex = só arquivos modificados)
echo -e "${YELLOW}⚡ Executando reindexação incremental...${NC}" | tee -a "$LOG_FILE"
python3 "$PYTHON_SCRIPT" 2>&1 | tee -a "$LOG_FILE"

# Verificar sucesso
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Reindexação concluída com sucesso!${NC}" | tee -a "$LOG_FILE"
else
    echo -e "${YELLOW}⚠️  Reindexação falhou - ver log acima${NC}" | tee -a "$LOG_FILE"
fi

echo -e "${BLUE}========================================${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Limpar logs antigos (manter últimos 7 dias)
find "$LOG_DIR" -name "rag-reindex.log.*" -mtime +7 -delete 2>/dev/null

exit 0
