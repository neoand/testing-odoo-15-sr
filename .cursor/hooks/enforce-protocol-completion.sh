#!/bin/bash
# Hook para forçar completar protocolo quando usuário digita "PROTOCOLO"
# Adaptado para Cursor AI

USER_MESSAGE="$1"

if [[ "$USER_MESSAGE" == *"protocolo"* ]] || [[ "$USER_MESSAGE" == *"PROTOCOLO"* ]]; then
    echo "🔒 PROTOCOLO DETECTADO - Executando Sistema Automático V3.0"
    echo "Verificando memória e contexto..."
    
    # Verificar arquivos de memória obrigatórios
    MEMORY_FILES=(
        ".cursor/memory/commands/COMMAND-HISTORY.md"
        ".cursor/memory/errors/ERRORS-SOLVED.md"
        ".cursor/memory/patterns/PATTERNS.md"
        ".cursor/memory/AUTO-LEARNING-PROTOCOL.md"
        ".cursor/memory/THINKING-MODE-PROTOCOL.md"
        ".cursor/memory/protocols/PROTOCOL-V3-AUTOMATICO.md"
    )
    
    for file in "${MEMORY_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo "✅ $file"
        else
            echo "⚠️  $file não encontrado"
        fi
    done
    
    echo ""
    echo "🚀 Sistema V3.0 ativado - Cursor AI deve seguir protocolo completo"
fi

exit 0

