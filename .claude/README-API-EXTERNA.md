# 🚀 Guia Rápido: API Externa no Claude CLI (GLM)

## ✅ CONFIGURAÇÃO COMPLETA!

A API GLM já está configurada e pronta para uso!

**✅ Fixes aplicados:**
- Arquivo `~/.claude/settings.json` configurado (resolve erro 404)
- Conflito de autenticação corrigido (removido `ANTHROPIC_API_KEY` duplicado)

## ⚡ Como Usar (direto, sem carregar script)

Agora você pode usar diretamente:

```bash
claude "Sua pergunta aqui"
```

Ou especificar modelo:

```bash
claude --model glm-4.5-air "pergunta rápida"
claude --model glm-4.6 "pergunta normal"
```

### Opcional: Carregar variáveis também

Se quiser garantir que as variáveis estão carregadas:

```bash
source .claude/setup-api-externa.sh
claude "Sua pergunta aqui"
```

### Ou use modelos específicos:

```bash
source .claude/setup-api-externa.sh

# Haiku (rápido)
claude --model glm-4.5-air "pergunta rápida"

# Sonnet (padrão)
claude --model glm-4.6 "pergunta normal"
```

## 📚 Documentação Completa

- **Guia detalhado:** `.claude/CLI-API-EXTERNA-CONFIG.md`
- **Script de setup:** `.claude/setup-api-externa.sh`
- **Carregar .env:** `.claude/load-env.sh`

## 🔍 Verificar se está funcionando

```bash
# Verificar variáveis
echo $ANTHROPIC_API_KEY
echo $ANTHROPIC_API_URL

# Testar CLI
claude -p "Diga apenas 'OK'"
```

## ⚠️ Importante

- ✅ `.claude/.env` já está no `.gitignore`
- ❌ **NUNCA** commite API keys no Git
- 🔒 Mantenha suas credenciais seguras

---

**Precisa de ajuda?** Veja `.claude/CLI-API-EXTERNA-CONFIG.md` para troubleshooting.

