#!/bin/bash
# Script: switch-api-provider.sh
# Description: Switch between API providers (z.ai, minimax, direct)
# Usage: ./switch-api-provider.sh [z.ai|minimax|direct]
# Author: Claude
# Created: 2025-11-20

ENV_FILE="$(pwd)/.claude/.env"
BACKUP_FILE="$(pwd)/.claude/.env.backup"

# Function to backup current .env
backup_env() {
    if [ -f "$ENV_FILE" ]; then
        cp "$ENV_FILE" "$BACKUP_FILE"
        echo "✅ Backup criado: $BACKUP_FILE"
    fi
}

# Function to switch to z.ai
switch_to_zai() {
    echo "🔄 Switching to z.ai API..."

    cat > "$ENV_FILE" << 'EOF'
# API Z.ai
ANTHROPIC_AUTH_TOKEN=bb42e0b593324786be8fb989ce839b2c.eHkqUUIiaVj3K9IV
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
ANTHROPIC_API_URL=https://api.z.ai/api/anthropic
API_TIMEOUT_MS=3000000
ANTHROPIC_DEFAULT_HAIKU_MODEL=glm-4.5-air
ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.6
ANTHROPIC_DEFAULT_OPUS_MODEL=glm-4.6
ANTHROPIC_MODEL=glm-4.6
EOF

    echo "✅ Switched to z.ai API"
}

# Function to switch to MiniMax
switch_to_minimax() {
    echo "🔄 Switching to MiniMax API..."

    # Load MiniMax API key from current .env
    if [ -f "$ENV_FILE" ]; then
        source "$ENV_FILE"
    fi

    # Use configured MiniMax key or ask for it
    if [ -z "$MINIMAX_API_KEY" ]; then
        echo "🔑 Enter MiniMax API Key:"
        read -s MINIMAX_KEY_INPUT
        MINIMAX_API_KEY="$MINIMAX_KEY_INPUT"
    fi

    cat > "$ENV_FILE" << EOF
# API MiniMax
ANTHROPIC_AUTH_TOKEN=$MINIMAX_API_KEY
ANTHROPIC_BASE_URL=https://api.minimax.chat/v1
ANTHROPIC_API_URL=https://api.minimax.chat/v1
API_TIMEOUT_MS=3000000
ANTHROPIC_DEFAULT_HAIKU_MODEL=abab6.5-chat
ANTHROPIC_DEFAULT_SONNET_MODEL=abab6.5-chat
ANTHROPIC_DEFAULT_OPUS_MODEL=abab6.5-chat
ANTHROPIC_MODEL=abab6.5-chat

# Keep MiniMax variables for reference
MINIMAX_API_KEY=$MINIMAX_API_KEY
MINIMAX_BASE_URL=https://api.minimax.chat/v1
MINIMAX_MODEL=abab6.5-chat
EOF

    echo "✅ Switched to MiniMax API"
}

# Function to switch to Direct Anthropic
switch_to_direct() {
    echo "🔄 Switching to Direct Anthropic API..."

    # Read direct API key if not set
    if [ -z "$ANTHROPIC_DIRECT_KEY" ]; then
        echo "🔑 Enter Anthropic API Key:"
        read -s ANTHROPIC_KEY_INPUT
        ANTHROPIC_DIRECT_KEY="$ANTHROPIC_KEY_INPUT"
    fi

    cat > "$ENV_FILE" << EOF
# Direct Anthropic API
ANTHROPIC_AUTH_TOKEN=$ANTHROPIC_DIRECT_KEY
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_API_URL=https://api.anthropic.com
API_TIMEOUT_MS=3000000
ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-3-5-haiku-20241022
ANTHROPIC_DEFAULT_SONNET_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_DEFAULT_OPUS_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
EOF

    echo "✅ Switched to Direct Anthropic API"
}

# Function to show current provider
show_current() {
    echo "📊 Current API Provider:"
    if grep -q "api.z.ai" "$ENV_FILE" 2>/dev/null; then
        echo "  Provider: z.ai"
        echo "  Model: $(grep 'ANTHROPIC_MODEL=' "$ENV_FILE" | cut -d'=' -f2)"
    elif grep -q "minimax.chat" "$ENV_FILE" 2>/dev/null; then
        echo "  Provider: MiniMax"
        echo "  Model: $(grep 'ANTHROPIC_MODEL=' "$ENV_FILE" | cut -d'=' -f2)"
    elif grep -q "api.anthropic.com" "$ENV_FILE" 2>/dev/null; then
        echo "  Provider: Direct Anthropic"
        echo "  Model: $(grep 'ANTHROPIC_MODEL=' "$ENV_FILE" | cut -d'=' -f2)"
    else
        echo "  Unknown or not configured"
    fi
}

# Main logic
case "${1:-}" in
    "z.ai"|"zai")
        backup_env
        switch_to_zai
        ;;
    "minimax"|"mini")
        backup_env
        switch_to_minimax
        ;;
    "direct"|"anthropic")
        backup_env
        switch_to_direct
        ;;
    "status"|"current"|"show")
        show_current
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [z.ai|minimax|direct|status|help]"
        echo ""
        echo "Providers:"
        echo "  z.ai     - Use z.ai API (current)"
        echo "  minimax  - Use MiniMax API"
        echo "  direct   - Use direct Anthropic API"
        echo "  status   - Show current provider"
        echo "  help     - Show this help"
        ;;
    *)
        echo "❌ Unknown provider: ${1:-}"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

# Reload environment for current session
echo "🔄 Reloading environment..."
export $(grep -v '^#' "$ENV_FILE" | xargs)
echo "✅ Environment reloaded"