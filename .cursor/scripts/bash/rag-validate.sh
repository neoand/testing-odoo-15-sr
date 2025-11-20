#!/bin/bash
# Script: rag-validate.sh
# Description: Validação completa do RAG setup
# Usage: ./rag-validate.sh
# Author: Claude + Anderson
# Created: 2025-11-18

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🔍 RAG Setup - Validação Completa${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Contadores
PASS=0
FAIL=0

# Função de teste
test_item() {
    local desc="$1"
    local command="$2"

    echo -ne "${CYAN}Testando: ${desc}${NC} ... "

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASS++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAIL++))
        return 1
    fi
}

# ====== TESTES ======

echo -e "${YELLOW}1. Dependências Python${NC}\n"

test_item "Python 3.11 disponível" "which python3.11"
test_item "ChromaDB instalado" "python3.11 -c 'import chromadb'"
test_item "Sentence Transformers instalado" "python3.11 -c 'import sentence_transformers'"
test_item "Torch instalado" "python3.11 -c 'import torch'"
test_item "Torch MPS disponível" "python3.11 -c 'import torch; assert torch.backends.mps.is_available()'"

echo ""
echo -e "${YELLOW}2. Scripts Python${NC}\n"

test_item "index-knowledge.py existe" "test -f .claude/scripts/python/index-knowledge.py"
test_item "index-knowledge.py executável" "test -x .claude/scripts/python/index-knowledge.py"
test_item "test-rag.py existe" "test -f .claude/scripts/python/test-rag.py"
test_item "test-rag.py executável" "test -x .claude/scripts/python/test-rag.py"
test_item "mcp_rag_server.py existe" "test -f .claude/scripts/python/mcp_rag_server.py"

echo ""
echo -e "${YELLOW}3. Scripts Bash${NC}\n"

test_item "rag-reindex-hourly.sh existe" "test -f .claude/scripts/bash/rag-reindex-hourly.sh"
test_item "rag-reindex-hourly.sh executável" "test -x .claude/scripts/bash/rag-reindex-hourly.sh"
test_item "setup-rag-cron.sh existe" "test -f .claude/scripts/bash/setup-rag-cron.sh"
test_item "setup-rag-cron.sh executável" "test -x .claude/scripts/bash/setup-rag-cron.sh"

echo ""
echo -e "${YELLOW}4. Vector Database${NC}\n"

test_item "vectordb/ existe" "test -d .claude/vectordb"
test_item "chroma.sqlite3 existe" "test -f .claude/vectordb/chroma.sqlite3"
test_item "Database não está vazia" "test -s .claude/vectordb/chroma.sqlite3"
test_item "README.md existe" "test -f .claude/vectordb/README.md"

echo ""
echo -e "${YELLOW}5. Diretórios${NC}\n"

test_item ".claude/scripts/python/ existe" "test -d .claude/scripts/python"
test_item ".claude/scripts/bash/ existe" "test -d .claude/scripts/bash"
test_item ".claude/logs/ existe" "test -d .claude/logs"
test_item ".claude/memory/ existe" "test -d .claude/memory"

echo ""
echo -e "${YELLOW}6. Cron Job${NC}\n"

test_item "Cron job configurado" "crontab -l 2>/dev/null | grep -q 'rag-reindex-hourly.sh'"

echo ""
echo -e "${YELLOW}7. Funcionalidade RAG${NC}\n"

# Teste de busca rápida
echo -ne "${CYAN}Testando: Busca RAG funcional${NC} ... "
SEARCH_RESULT=$(python3.11 .claude/scripts/python/test-rag.py "teste" 2>&1 | grep -c "Top")
if [ "$SEARCH_RESULT" -gt 0 ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAIL++))
fi

# ====== ESTATÍSTICAS DA DATABASE ======

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}📊 Estatísticas da Database${NC}"
echo -e "${BLUE}========================================${NC}\n"

if [ -f .claude/vectordb/chroma.sqlite3 ]; then
    # Tamanho da database
    DB_SIZE=$(du -sh .claude/vectordb | awk '{print $1}')
    echo -e "${CYAN}💾 Tamanho total:${NC} $DB_SIZE"

    # Contar arquivos .md
    MD_COUNT=$(find .claude/memory -name "*.md" | wc -l | tr -d ' ')
    echo -e "${CYAN}📄 Arquivos .md:${NC} $MD_COUNT"

    # Device
    DEVICE=$(python3.11 -c 'import torch; print("MPS" if torch.backends.mps.is_available() else "CPU")' 2>/dev/null)
    echo -e "${CYAN}⚡ Device:${NC} $DEVICE"
fi

# ====== RESULTADO FINAL ======

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}📊 Resultado da Validação${NC}"
echo -e "${BLUE}========================================${NC}\n"

TOTAL=$((PASS + FAIL))
PERCENT=$((PASS * 100 / TOTAL))

echo -e "${GREEN}✅ Passou: ${PASS}/${TOTAL}${NC}"
echo -e "${RED}❌ Falhou: ${FAIL}/${TOTAL}${NC}"
echo -e "${CYAN}📊 Taxa de sucesso: ${PERCENT}%${NC}\n"

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 SETUP PERFEITO! RAG 100% FUNCIONAL!${NC}"
    echo ""
    echo -e "${CYAN}🚀 Próximos passos:${NC}"
    echo -e "  1. Testar busca: ${YELLOW}python3 .claude/scripts/python/test-rag.py \"sua query\"${NC}"
    echo -e "  2. Ver logs cron: ${YELLOW}tail -f .claude/logs/cron-rag.log${NC}"
    echo -e "  3. Ler documentação: ${YELLOW}cat .claude/vectordb/README.md${NC}"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  Alguns testes falharam. Revisar setup.${NC}"
    echo ""
    echo -e "${CYAN}💡 Dica: Execute novamente index-knowledge.py:${NC}"
    echo -e "  ${YELLOW}python3 .claude/scripts/python/index-knowledge.py --reindex${NC}"
    echo ""
    exit 1
fi
