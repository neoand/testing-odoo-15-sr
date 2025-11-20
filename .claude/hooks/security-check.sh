#!/bin/bash
#
# Hook de Segurança Claude Code - Validação de Comandos Perigosos
#
# Uso: chamado automaticamente antes de executar ferramentas
#

TOOL_NAME="$1"
TOOL_ARGS="$2"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE=".claude/logs/security-checks.log"

# Criar diretório de logs se não existir
mkdir -p "$(dirname "$LOG_FILE")"

# Log da verificação
echo "[$TIMESTAMP] TOOL: $TOOL_NAME | ARGS: $TOOL_ARGS" >> "$LOG_FILE"

# Lista de comandos perigosos
DANGEROUS_COMMANDS=(
    "rm -rf /"
    "dd if="
    "mkfs"
    "fdisk"
    "format"
    "DELETE FROM"
    "DROP TABLE"
    "TRUNCATE TABLE"
    "UPDATE.*SET.*WHERE.*1=1"
    "sudo rm"
    "chmod 777"
    "chown root"
)

# Paths sensíveis
SENSITIVE_PATHS=(
    "/etc/passwd"
    "/etc/shadow"
    "/boot"
    "/usr/bin"
    "/bin"
    "/sbin"
    "/System"
    "node_modules"
    ".git/refs/heads/main"
)

# Verificar comandos perigosos
for cmd in "${DANGEROUS_COMMANDS[@]}"; do
    if [[ "$TOOL_ARGS" =~ $cmd ]]; then
        echo "🚨 COMANDO PERIGOSO DETECTADO: $cmd"
        echo "⚠️ Requer confirmação explícita do usuário."
        echo "[$TIMESTAMP] BLOCKED: Dangerous command detected - $cmd" >> "$LOG_FILE"
        exit 1
    fi
done

# Verificar paths sensíveis com operações de escrita/deleção
if [[ "$TOOL_ARGS" =~ (rm|delete|truncate|drop|chmod|chown) ]]; then
    for path in "${SENSITIVE_PATHS[@]}"; do
        if [[ "$TOOL_ARGS" =~ $path ]]; then
            echo "🚨 TENTATIVA DE ALTERAR SISTEMA: $path"
            echo "⚠️ Operação bloqueada por segurança."
            echo "[$TIMESTAMP] BLOCKED: Sensitive path access - $path" >> "$LOG_FILE"
            exit 1
        fi
    done
fi

# Verificação específica para Bash com comandos de rede suspeitos
if [[ "$TOOL_NAME" == "Bash" ]]; then
    # Bloquear downloads de fontes não confiáveis
    if [[ "$TOOL_ARGS" =~ (curl|wget|nc) && "$TOOL_ARGS" =~ (http://|ftp://) ]]; then
        echo "⚠️ Download de fonte HTTP não segura detectado"
        echo "Recomendado usar HTTPS ou fonte confiável."
        echo "[$TIMESTAMP] WARNING: Insecure download detected" >> "$LOG_FILE"
    fi

    # Alertar sobre comandos que podem expor credenciais
    if [[ "$TOOL_ARGS" =~ (cat|grep|find) && "$TOOL_ARGS" =~ (password|secret|key|token) ]]; then
        echo "⚠️ Operação envolvendo credenciais detectada"
        echo "Verifique se não está expondo informações sensíveis."
        echo "[$TIMESTAMP] WARNING: Credential operation detected" >> "$LOG_FILE"
    fi
fi

# Verificação específica para Write operations
if [[ "$TOOL_NAME" == "Write" ]]; then
    # Não permitir escrever arquivos executáveis em paths públicos
    if [[ "$TOOL_ARGS" =~ \.(sh|py|js|rb|pl)$ && "$TOOL_ARGS" =~ (/tmp|/var/tmp|/public) ]]; then
        echo "🚨 Tentativa de criar script executável em path público"
        echo "[$TIMESTAMP] BLOCKED: Executable creation in public path" >> "$LOG_FILE"
        exit 1
    fi

    # Alertar sobre arquivos de configuração
    if [[ "$TOOL_ARGS" =~ (\.conf|\.config|\.env|password|secret) ]]; then
        echo "⚠️ Arquivo de configuração/senha detectado"
        echo "Verifique se não está expondo credenciais."
        echo "[$TIMESTAMP] WARNING: Config file creation detected" >> "$LOG_FILE"
    fi
fi

# Log de sucesso
echo "[$TIMESTAMP] PASSED: Security check passed" >> "$LOG_FILE"

# Saída com sucesso
exit 0