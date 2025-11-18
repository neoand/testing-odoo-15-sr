#!/bin/bash
# 🔧 Script de Configuração de API Externa para Claude CLI (GLM)
# Uso: source .claude/setup-api-externa.sh

# ✅ CONFIGURAÇÃO GLM API
# Provider: GLM (api.z.ai)
# Modelos disponíveis: glm-4.5-air, glm-4.6

# Configurações da API GLM
# Usar apenas ANTHROPIC_AUTH_TOKEN (removido ANTHROPIC_API_KEY para evitar conflito)
export ANTHROPIC_AUTH_TOKEN="bb42e0b593324786be8fb989ce839b2c.eHkqUUIiaVj3K9IV"
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_API_URL="https://api.z.ai/api/anthropic"  # URL completa sem /v1 (CLI adiciona)
export ANTHROPIC_API_BASE_URL="https://api.z.ai/api/anthropic"  # Alternativa
export API_TIMEOUT_MS="3000000"

# Modelos GLM disponíveis
export ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-4.5-air"
export ANTHROPIC_DEFAULT_SONNET_MODEL="glm-4.6"
export ANTHROPIC_DEFAULT_OPUS_MODEL="glm-4.6"

# Modelo padrão (usar Sonnet como padrão)
export ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-glm-4.6}"

# Mostrar configuração (sem mostrar o token completo)
TOKEN_PREVIEW="${ANTHROPIC_AUTH_TOKEN:0:10}...${ANTHROPIC_AUTH_TOKEN: -4}"
echo "✅ API GLM configurada para Claude CLI"
echo "   🔑 Token: $TOKEN_PREVIEW"
echo "   🌐 URL: $ANTHROPIC_BASE_URL"
echo "   🤖 Model padrão: $ANTHROPIC_MODEL"
echo "   ⏱️  Timeout: ${API_TIMEOUT_MS}ms"
echo ""
echo "📋 Modelos disponíveis:"
echo "   - Haiku: $ANTHROPIC_DEFAULT_HAIKU_MODEL"
echo "   - Sonnet: $ANTHROPIC_DEFAULT_SONNET_MODEL"
echo "   - Opus: $ANTHROPIC_DEFAULT_OPUS_MODEL"
echo ""
echo "💡 Use: claude 'sua pergunta aqui'"
echo "💡 Ou especifique modelo: claude --model glm-4.5-air 'pergunta'"

