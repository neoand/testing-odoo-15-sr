#!/bin/bash
# 🔄 Carrega variáveis de ambiente do arquivo .env
# Uso: source .claude/load-env.sh

ENV_FILE=".claude/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Arquivo $ENV_FILE não encontrado!"
    echo "   O arquivo deve ser criado automaticamente"
    return 1
fi

# Carregar variáveis (ignorar comentários e linhas vazias)
export $(cat "$ENV_FILE" | grep -v '^#' | grep -v '^$' | xargs)

# Garantir compatibilidade (sem duplicar ANTHROPIC_API_KEY para evitar conflito)
export ANTHROPIC_API_URL="${ANTHROPIC_API_URL:-$ANTHROPIC_BASE_URL}"

TOKEN_PREVIEW="${ANTHROPIC_AUTH_TOKEN:0:10}...${ANTHROPIC_AUTH_TOKEN: -4}"
echo "✅ Variáveis de ambiente carregadas de $ENV_FILE"
echo "   🔑 Token: $TOKEN_PREVIEW"
echo "   🌐 URL: $ANTHROPIC_API_URL"
echo "   🤖 Model: $ANTHROPIC_MODEL"

