#!/bin/bash
#
# Hook Pré-Tool Use - Validação e Otimização
#
# Executado antes de qualquer uso de ferramenta Claude
#

TOOL_NAME="$1"
TOOL_ARGS="$2"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
PROJECT_ROOT="/Users/andersongoliveira/testing_odoo_15_sr"

# Log de uso de ferramentas
echo "[$TIMESTAMP] TOOL_USE: $TOOL_NAME | ARGS_TRUNCATED: ${TOOL_ARGS:0:100}..." >> .claude/logs/tool-usage.log

# Verificar se já existe script similar (evitar duplicação)
if [[ "$TOOL_NAME" == "Write" && "$TOOL_ARGS" =~ \.(sh|py|js)$ ]]; then
    SCRIPT_NAME=$(basename "$TOOL_ARGS" | sed 's/\.[^.]*$//')

    # Verificar em scripts bash
    if [[ "$TOOL_ARGS" =~ \.sh$ ]] && ls .claude/scripts/bash/ | grep -q "$SCRIPT_NAME"; then
        echo "⚠️ Script bash similar já existe em .claude/scripts/bash/"
        echo "Scripts encontrados:"
        ls .claude/scripts/bash/ | grep "$SCRIPT_NAME" | sed 's/^/  - /'
        echo "Use 'skill tool-inventory' para verificar antes de duplicar."
    fi

    # Verificar em scripts python
    if [[ "$TOOL_ARGS" =~ \.py$ ]] && ls .claude/scripts/python/ | grep -q "$SCRIPT_NAME"; then
        echo "⚠️ Script Python similar já existe em .claude/scripts/python/"
        echo "Scripts encontrados:"
        ls .claude/scripts/python/ | grep "$SCRIPT_NAME" | sed 's/^/  - /'
        echo "Use 'skill tool-inventory' para verificar antes de duplicar."
    fi
fi

# Otimizações específicas para Odoo
if [[ "$TOOL_ARGS" =~ odoo ]]; then
    # Sugerir uso do MCP server para queries Odoo
    if [[ "$TOOL_ARGS" =~ (SELECT|FROM.*ir_) && "$TOOL_NAME" == "Bash" ]]; then
        echo "💡 Dica: Use 'odoo' MCP server para queries Odoo:"
        echo "   - odoo.list_models"
        echo "   - odoo.model_fields model='model.name'"
        echo "   - odoo.query query='SELECT ...'"
    fi

    # Sugerir skill odoo-ops para operações comuns
    if [[ "$TOOL_ARGS" =~ (systemctl|restart|odoo-bin) && "$TOOL_NAME" == "Bash" ]]; then
        echo "💡 Dica: Use 'skill odoo-ops' para operações Odoo automatizadas"
    fi
fi

# Verificar se está tentando acessar APIs externas sem tratamento de erro
if [[ "$TOOL_ARGS" =~ (curl|wget|requests) && "$TOOL_ARGS" =~ (api|endpoint) ]]; then
    if [[ ! "$TOOL_ARGS" =~ (try|catch|error|timeout) ]]; then
        echo "⚠️ Requisição de API detectada sem tratamento de erro"
        echo "Considere adicionar try/catch, timeout e retry logic"
    fi
fi

# Verificar se está criando arquivo grande sem gzip
if [[ "$TOOL_NAME" == "Bash" && "$TOOL_ARGS" =~ (pg_dump|mysqldump) && ! "$TOOL_ARGS" =~ (gz|compress) ]]; then
    echo "💡 Dica: Considere comprimir o backup com gzip:"
    echo "   pg_dump ... | gzip > backup.sql.gz"
fi

# Sugerir paralelização para múltiplas operações
if [[ "$TOOL_ARGS" =~ (&&|;) ]]; then
    COMMAND_COUNT=$(echo "$TOOL_ARGS" | grep -o -E "(&&|;)" | wc -l)
    if [[ $COMMAND_COUNT -gt 2 ]]; then
        echo "💡 Dica: Operações múltiplas detectadas. Considere paralelização:"
        echo "   Comandos independentes: use '&' e 'wait'"
        echo "   Multiple tool calls: executar em uma única mensagem"
    fi
fi

# Verificar se está editando arquivos de memória diretamente
if [[ "$TOOL_ARGS" =~ .claude/memory/ && "$TOOL_NAME" == "Edit" ]]; then
    echo "⚠️ Editando arquivos de memória diretamente"
    echo "Considere usar os protocolos de aprendizado automático:"
    echo "   - Erros: documente em ERRORS-SOLVED.md"
    echo "   - Comandos: adicione a COMMAND-HISTORY.md"
    echo "   - Padrões: registre em PATTERNS.md"
fi

# Sugestões de melhoria de performance
if [[ "$TOOL_ARGS" =~ (find|grep) && "$TOOL_ARGS" =~ -r ]]; then
    echo "💡 Dica: Para busca recursiva, considere:"
    echo "   - rg (ripgrep): mais rápido que find+grep"
    echo "   - glob patterns: mais eficiente que find"
fi

exit 0