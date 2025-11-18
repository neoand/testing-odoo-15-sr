# 🔧 Fix: Erro 404 - Modelo não encontrado

## 🐛 Problema Identificado

O erro `404 - model: glm-4.6` ocorria porque o Claude CLI não estava usando as variáveis de ambiente configuradas no script.

## ✅ Solução Aplicada

O Claude CLI lê configurações de **dois lugares**:

1. **Variáveis de ambiente** (temporárias, apenas na sessão atual)
2. **Arquivo `~/.claude/settings.json`** (permanente, usado pelo CLI)

### Configuração Aplicada

O arquivo `~/.claude/settings.json` foi atualizado com:

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "bb42e0b593324786be8fb989ce839b2c.eHkqUUIiaVj3K9IV",
    "ANTHROPIC_API_KEY": "bb42e0b593324786be8fb989ce839b2c.eHkqUUIiaVj3K9IV",
    "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
    "ANTHROPIC_API_URL": "https://api.z.ai/api/anthropic",
    "API_TIMEOUT_MS": "3000000",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4.5-air",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-4.6",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-4.6"
  }
}
```

## 🚀 Como Usar Agora

### Opção 1: Usar diretamente (recomendado)

Agora que o `settings.json` está configurado, você pode usar diretamente:

```bash
claude "Sua pergunta aqui"
```

Ou especificar modelo:

```bash
claude --model glm-4.5-air "pergunta rápida"
claude --model glm-4.6 "pergunta normal"
```

### Opção 2: Carregar variáveis também (opcional)

Se quiser garantir que as variáveis estão carregadas:

```bash
source .claude/setup-api-externa.sh
claude "Sua pergunta aqui"
```

## ✅ Teste

Execute para verificar:

```bash
claude -p "Diga apenas 'OK' se você está funcionando"
```

## 📝 Notas

- O arquivo `~/.claude/settings.json` é **global** (afeta todos os projetos)
- Se quiser configuração por projeto, crie `.claude/settings.json` no projeto
- As variáveis de ambiente têm precedência sobre o `settings.json`

## 🔄 Reverter (se necessário)

Se quiser voltar para a API oficial do Anthropic:

```bash
# Remover ou renomear o arquivo
mv ~/.claude/settings.json ~/.claude/settings.json.backup
```

---

**Status:** ✅ Corrigido  
**Data:** 2025-11-18

