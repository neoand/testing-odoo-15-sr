#!/bin/bash
# Script: model-switch.sh
# Description: Backend script for /model command to switch API providers
# Usage: ./model-switch.sh [provider] [model]
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
    local model="${1:-glm-4.6}"
    echo "🔄 Switching to z.ai API with model: $model"

    # Validate model for z.ai
    case "$model" in
        "glm-4.5-air"|"glm-4.6")
            ;;
        *)
            echo "⚠️  Unknown model for z.ai: $model, using glm-4.6"
            model="glm-4.6"
            ;;
    esac

    cat > "$ENV_FILE" << 'EOF'
# API Z.ai
ANTHROPIC_AUTH_TOKEN=bb42e0b593324786be8fb989ce839b2c.eHkqUUIiaVj3K9IV
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
ANTHROPIC_API_URL=https://api.z.ai/api/anthropic
API_TIMEOUT_MS=3000000
EOF

    # Add model-specific settings
    case "$model" in
        "glm-4.5-air")
            cat >> "$ENV_FILE" << 'EOF'
ANTHROPIC_DEFAULT_HAIKU_MODEL=glm-4.5-air
ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.5-air
ANTHROPIC_DEFAULT_OPUS_MODEL=glm-4.5-air
ANTHROPIC_MODEL=glm-4.5-air
EOF
            ;;
        *)
            cat >> "$ENV_FILE" << 'EOF'
ANTHROPIC_DEFAULT_HAIKU_MODEL=glm-4.6
ANTHROPIC_DEFAULT_SONNET_MODEL=glm-4.6
ANTHROPIC_DEFAULT_OPUS_MODEL=glm-4.6
ANTHROPIC_MODEL=glm-4.6
EOF
            ;;
    esac

    echo "✅ Switched to z.ai API with model: $model"
}

# Function to switch to MiniMax
switch_to_minimax() {
    local model="${1:-abab6.5-chat}"
    echo "🔄 Switching to MiniMax API with model: $model"

    # Load MiniMax API key from current .env if available
    MINIMAX_KEY=""
    if [ -f "$ENV_FILE" ]; then
        source "$ENV_FILE" 2>/dev/null
        MINIMAX_KEY="$MINIMAX_API_KEY"
    fi

    # If no key found, use default or ask
    if [ -z "$MINIMAX_KEY" ]; then
        echo "⚠️  MiniMax API key not found, using default key"
        MINIMAX_KEY="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJEaWVnbyBBbGNhbnRhcmEiLCJVc2VyTmFtZSI6ImZsb3ciLCJBY2NvdW50IjoiIiwiU3ViamVjdElEIjoiMTk4OTA2ODYyNDA1NjI5MTQzNCIsIlBob25lIjoiIiwiR3JvdXBJRCI6IjE5ODkwNjg2MjQwNTIxMDEyMjYiLCJQYWdlTmFtZSI6IiIsIk1haWwiOiJkaWVnby5jb2Zsb3dAZ21haWwuY29tIiwiQ3JlYXRlVGltZSI6IjIwMjUtMTEtMjAgMjI6NDU6MzQiLCJUb2tlblR5cGUiOjQsImlzcyI6Im1pbmltYXgifQ.cQHpOPg6QurDGgr4-W_tLCL7HjE7CcRyuS5TPU0-0hRId6H_88Uf1RwEzJKduLBT8DF_G9xJCSvh8Wld2RigLmML2lfOY_D76RrLZKicGlp3z1pENOf42Ml3qz6uRYfs5N8wkaoH_rJAeub6wYquTVAH5HvUmnDiYuIpwVa-wts-fJWB7pyC-I9HYIi78c1Y1n4gKXlisyIN4h4FdOqh6CgIn8XIgMQdBByxDhSY34RHOPNEX8OLc9Tz4mtiFt6_091NKeNCeuy6x9E4pvazft35EFrATRjykRyaCcAVIwHWYVEluj1mZwBhDcaGGyxXcpvnXBUjU0uGm1-ZfOt1mA"
    fi

    cat > "$ENV_FILE" << EOF
# API MiniMax
ANTHROPIC_AUTH_TOKEN=$MINIMAX_KEY
ANTHROPIC_BASE_URL=https://api.minimax.chat/v1
ANTHROPIC_API_URL=https://api.minimax.chat/v1
API_TIMEOUT_MS=3000000
ANTHROPIC_DEFAULT_HAIKU_MODEL=abab6.5-chat
ANTHROPIC_DEFAULT_SONNET_MODEL=abab6.5-chat
ANTHROPIC_DEFAULT_OPUS_MODEL=abab6.5-chat
ANTHROPIC_MODEL=$model

# Keep MiniMax variables for reference
MINIMAX_API_KEY=$MINIMAX_KEY
MINIMAX_BASE_URL=https://api.minimax.chat/v1
MINIMAX_MODEL=$model
EOF

    echo "✅ Switched to MiniMax API with model: $model"
}

# Function to switch to Direct Anthropic
switch_to_direct() {
    local model="${1:-claude-3-5-sonnet-20241022}"
    echo "🔄 Switching to Direct Anthropic API with model: $model"

    # Load direct API key if available
    ANTHROPIC_KEY=""
    if [ -f "$ENV_FILE" ]; then
        source "$ENV_FILE" 2>/dev/null
        ANTHROPIC_KEY="$ANTHROPIC_DIRECT_KEY"
    fi

    # If no key found, ask user
    if [ -z "$ANTHROPIC_KEY" ]; then
        echo "🔑 Enter Anthropic API Key:"
        read -s ANTHROPIC_KEY_INPUT
        ANTHROPIC_KEY="$ANTHROPIC_KEY_INPUT"
    fi

    # Validate model for Anthropic
    case "$model" in
        "claude-3-5-haiku-20241022"|"claude-3-5-sonnet-20241022")
            ;;
        *)
            echo "⚠️  Unknown model for Anthropic: $model, using claude-3-5-sonnet-20241022"
            model="claude-3-5-sonnet-20241022"
            ;;
    esac

    cat > "$ENV_FILE" << EOF
# Direct Anthropic API
ANTHROPIC_AUTH_TOKEN=$ANTHROPIC_KEY
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_API_URL=https://api.anthropic.com
API_TIMEOUT_MS=3000000
ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-3-5-haiku-20241022
ANTHROPIC_DEFAULT_SONNET_MODEL=$model
ANTHROPIC_DEFAULT_OPUS_MODEL=$model
ANTHROPIC_MODEL=$model
EOF

    echo "✅ Switched to Direct Anthropic API with model: $model"
}

# Function to show current provider and model
show_current() {
    echo "📊 Current API Provider:"
    if [ -f "$ENV_FILE" ]; then
        if grep -q "api.z.ai" "$ENV_FILE" 2>/dev/null; then
            echo "  Provider: z.ai (GLM)"
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
    else
        echo "  No .env file found"
    fi
}

# Function to show available options
show_help() {
    echo "📋 Model Switch Usage:"
    echo ""
    echo "  ./model-switch.sh [provider] [model]"
    echo ""
    echo "Providers:"
    echo "  z.ai | z    - z.ai API (GLM models)"
    echo "                Models: glm-4.5-air, glm-4.6"
    echo ""
    echo "  minimax | m - MiniMax API"
    echo "                Models: abab6.5-chat"
    echo ""
    echo "  direct | d  - Direct Anthropic API"
    echo "                Models: claude-3-5-haiku-20241022, claude-3-5-sonnet-20241022"
    echo ""
    echo "Examples:"
    echo "  ./model-switch.sh z.ai glm-4.6"
    echo "  ./model-switch.sh minimax"
    echo "  ./model-switch.sh d claude-3-5-sonnet-20241022"
    echo ""
    echo "Status:"
    echo "  ./model-switch.sh status"
}

# Main logic
PROVIDER="${1:-}"
MODEL="${2:-}"

# Handle provider aliases
case "$PROVIDER" in
    "z"|"z.ai")
        PROVIDER="z.ai"
        ;;
    "m"|"minimax")
        PROVIDER="minimax"
        ;;
    "d"|"direct"|"anthropic")
        PROVIDER="direct"
        ;;
esac

case "${PROVIDER:-}" in
    "z.ai")
        backup_env
        switch_to_zai "$MODEL"
        ;;
    "minimax")
        backup_env
        switch_to_minimax "$MODEL"
        ;;
    "direct")
        backup_env
        switch_to_direct "$MODEL"
        ;;
    "status"|"current"|"show")
        show_current
        ;;
    "help"|"-h"|"--help"|"")
        show_help
        ;;
    *)
        echo "❌ Unknown provider: ${PROVIDER}"
        show_help
        exit 1
        ;;
esac

# Reload environment for current session if switch was made
if [[ "$PROVIDER" != "status" && "$PROVIDER" != "help" && "$PROVIDER" != "" ]]; then
    echo "🔄 Reloading environment..."
    export $(grep -v '^#' "$ENV_FILE" | xargs)
    echo "✅ Environment reloaded"
fi