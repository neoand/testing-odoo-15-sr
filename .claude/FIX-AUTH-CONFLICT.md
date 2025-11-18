# 🔧 Fix: Conflito de Autenticação

## 🐛 Problema

O CLI estava mostrando aviso:
```
⚠ Auth conflict: Both a token (ANTHROPIC_AUTH_TOKEN) and an API key 
(ANTHROPIC_API_KEY) are set. This may lead to unexpected behavior.
```

## ✅ Solução Aplicada

Removida a variável `ANTHROPIC_API_KEY` duplicada, mantendo apenas `ANTHROPIC_AUTH_TOKEN`.

### Arquivos Atualizados

1. **`~/.claude/settings.json`** - Removido `ANTHROPIC_API_KEY`
2. **`.claude/setup-api-externa.sh`** - Removido `export ANTHROPIC_API_KEY`
3. **`.claude/.env`** - Removido `ANTHROPIC_API_KEY`

### Configuração Correta

Agora usa apenas:
- `ANTHROPIC_AUTH_TOKEN` - Token de autenticação GLM
- `ANTHROPIC_BASE_URL` / `ANTHROPIC_API_URL` - URL da API
- Modelos configurados

## 🚀 Como Usar

Agora pode usar normalmente sem avisos:

```bash
claude "Sua pergunta aqui"
```

Ou:

```bash
claude --model glm-4.6 "pergunta"
```

## ✅ Verificação

O aviso de conflito não deve mais aparecer. Se ainda aparecer, verifique:

```bash
# Verificar variáveis carregadas
env | grep ANTHROPIC

# Se ANTHROPIC_API_KEY ainda estiver definida, remova:
unset ANTHROPIC_API_KEY
```

---

**Status:** ✅ Corrigido  
**Data:** 2025-11-18

