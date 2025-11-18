#!/bin/bash
# Hook: enforce-protocol-completion.sh
# Trigger: Quando usuário digita "PROTOCOLO" no prompt
# Ação: FORÇA Claude a documentar, commitar, sincronizar
# Event: Stop (bloqueia fim de tarefa até protocolo completo)

# Cores
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Verificar se última mensagem do usuário contém "PROTOCOLO"
USER_MESSAGE="$1"

if echo "$USER_MESSAGE" | grep -qi "PROTOCOLO"; then
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  🚨 PALAVRA MÁGICA DETECTADA: 'PROTOCOLO'                 ║${NC}"
    echo -e "${RED}║  Claude DEVE executar checklist OBRIGATÓRIO!              ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}📋 CHECKLIST OBRIGATÓRIO (NÃO PODE PULAR):${NC}"
    echo ""
    echo -e "  ${BLUE}[ ]${NC} 1. Ativou Thinking Mode para aprendizados?"
    echo -e "  ${BLUE}[ ]${NC} 2. Documentou em ERRORS-SOLVED.md?"
    echo -e "  ${BLUE}[ ]${NC} 3. Documentou em COMMAND-HISTORY.md?"
    echo -e "  ${BLUE}[ ]${NC} 4. Documentou em PATTERNS.md?"
    echo -e "  ${BLUE}[ ]${NC} 5. Documentou em learnings/ (se aplicável)?"
    echo -e "  ${BLUE}[ ]${NC} 6. Criou/atualizou ADR (se decisão arquitetural)?"
    echo -e "  ${BLUE}[ ]${NC} 7. Verificou tool-inventory ANTES de criar scripts?"
    echo -e "  ${BLUE}[ ]${NC} 8. Commitou mudanças localmente (git)?"
    echo -e "  ${BLUE}[ ]${NC} 9. Sincronizou com Claude-especial (se genérico)?"
    echo -e "  ${BLUE}[ ]${NC} 10. Push para GitHub (ambos repos se aplicável)?"
    echo ""
    echo -e "${RED}⚠️  Claude NÃO PODE terminar sem completar TODOS os itens!${NC}"
    echo ""

    # Exit code 2 = bloqueia stoppage (Claude precisa continuar)
    exit 2
fi

# Se não tem "PROTOCOLO", deixa passar
exit 0
