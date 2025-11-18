# 🔧 Configuração de API Externa no Claude CLI

## 📋 Situação

Você tem um plano no Claude Code e quer usar o CLI (`claude`) com APIs de outras empresas que oferecem acesso ao Claude, já que seu limite na API oficial acabou.

## ✅ Verificação Realizada

- ✅ Claude CLI instalado: `/usr/local/bin/claude` (versão 2.0.42)
- ❌ Nenhum arquivo de configuração encontrado no projeto atual
- ❌ Nenhuma variável de ambiente `ANTHROPIC_*` configurada

## 🎯 Como Configurar API Externa no Claude CLI

O Claude CLI usa **variáveis de ambiente** para configurar a API. Existem duas formas:

### Método 1: Variáveis de Ambiente (Temporário)

Configure as variáveis antes de usar o CLI:

```bash
export ANTHROPIC_API_KEY="sua-api-key-da-empresa-externa"
export ANTHROPIC_API_URL="https://api.empresa-externa.com/v1"
export ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"  # Opcional
```

Depois use normalmente:
```bash
claude "Olá, Claude!"
```

### Método 2: Arquivo de Configuração Permanente (Recomendado)

#### Opção A: Adicionar ao `.zshrc` (Mac/Linux)

Edite seu arquivo `~/.zshrc`:

```bash
# Claude CLI - API Externa
export ANTHROPIC_API_KEY="sua-api-key-da-empresa-externa"
export ANTHROPIC_API_URL="https://api.empresa-externa.com/v1"
export ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"  # Opcional
```

Depois recarregue:
```bash
source ~/.zshrc
```

#### Opção B: Criar arquivo `.env` no projeto

Crie um arquivo `.env` na raiz do projeto:

```bash
# .env
ANTHROPIC_API_KEY=sua-api-key-da-empresa-externa
ANTHROPIC_API_URL=https://api.empresa-externa.com/v1
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

E carregue antes de usar:
```bash
export $(cat .env | xargs)
claude "teste"
```

**⚠️ IMPORTANTE:** Adicione `.env` ao `.gitignore` para não commitar a API key!

#### Opção C: Script de inicialização

Crie um script `.claude/setup-api.sh`:

```bash
#!/bin/bash
# .claude/setup-api.sh

export ANTHROPIC_API_KEY="sua-api-key-da-empresa-externa"
export ANTHROPIC_API_URL="https://api.empresa-externa.com/v1"
export ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"

echo "✅ API externa configurada para Claude CLI"
echo "   URL: $ANTHROPIC_API_URL"
echo "   Model: $ANTHROPIC_MODEL"
```

Torne executável:
```bash
chmod +x .claude/setup-api.sh
```

Use antes de executar o CLI:
```bash
source .claude/setup-api.sh
claude "teste"
```

## 📝 Variáveis de Ambiente Suportadas

O Claude CLI reconhece as seguintes variáveis:

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `ANTHROPIC_API_KEY` | Chave de API da empresa externa | ✅ Sim |
| `ANTHROPIC_API_URL` | URL base da API (se diferente da padrão) | ⚠️ Depende |
| `ANTHROPIC_MODEL` | Modelo a usar (opcional, pode ser passado via `--model`) | ❌ Não |

## 🔍 Verificar Configuração

### Teste 1: Verificar variáveis
```bash
echo $ANTHROPIC_API_KEY
echo $ANTHROPIC_API_URL
```

### Teste 2: Testar CLI
```bash
claude -p "Diga apenas 'OK' se você está funcionando"
```

### Teste 3: Modo debug (ver requisições)
```bash
claude --debug api -p "teste"
```

## 🚨 Problemas Comuns

### 1. CLI ainda usa API oficial

**Causa:** Variáveis não estão carregadas na sessão atual.

**Solução:**
```bash
# Verificar se estão definidas
env | grep ANTHROPIC

# Se não estiverem, carregar novamente
source ~/.zshrc  # ou source .claude/setup-api.sh
```

### 2. Erro de autenticação

**Verificar:**
- API Key está correta?
- URL da API está acessível?
- Formato de autenticação está correto?

**Testar API manualmente:**
```bash
curl -X POST "$ANTHROPIC_API_URL/messages" \
  -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "messages": [{"role": "user", "content": "teste"}]
  }'
```

### 3. Modelo não encontrado

**Solução:** Especifique o modelo correto:
```bash
export ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"
# ou
claude --model claude-3-5-sonnet-20241022 "teste"
```

## 📋 Checklist de Configuração

- [ ] Obter API Key da empresa externa
- [ ] Obter URL base da API
- [ ] Verificar modelo disponível
- [ ] Configurar variáveis de ambiente
- [ ] Testar conexão com `curl`
- [ ] Testar CLI com `claude -p "teste"`
- [ ] Adicionar `.env` ao `.gitignore` (se usar .env)
- [ ] Documentar no projeto (este arquivo)

## 🔗 Informações Necessárias da Empresa Externa

Para configurar, você precisa:

1. **API Key:** Chave de autenticação
2. **Base URL:** URL base (ex: `https://api.exemplo.com/v1`)
3. **Modelo:** Nome do modelo (ex: `claude-3-5-sonnet-20241022`)
4. **Formato de Auth:** Geralmente `Authorization: Bearer <key>`
5. **Endpoints:** Verificar se usa `/messages` ou outro endpoint

## 🛠️ Exemplo Completo

### 1. Criar script de setup

```bash
# .claude/setup-api.sh
#!/bin/bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
export ANTHROPIC_API_URL="https://api.exemplo.com/v1"
export ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"
```

### 2. Usar no terminal

```bash
source .claude/setup-api.sh
claude "Explique o que é Odoo"
```

### 3. Ou criar alias no `.zshrc`

```bash
# Adicionar ao ~/.zshrc
alias claude-external='source ~/path/to/project/.claude/setup-api.sh && claude'
```

Depois:
```bash
claude-external "teste"
```

## 📚 Referências

- [Claude CLI Documentation](https://docs.claude.com/pt/docs/claude-code/setup)
- [Anthropic API Reference](https://docs.anthropic.com/claude/reference)
- [Environment Variables](https://docs.anthropic.com/claude/reference/environment-variables)

## 🔒 Segurança

⚠️ **NUNCA** commite API keys no Git!

- Adicione `.env` ao `.gitignore`
- Use variáveis de ambiente locais
- Não compartilhe keys em mensagens ou logs
- Revogue keys comprometidas imediatamente

---

**Última atualização:** 2025-11-18  
**Status:** Aguardando informações da API externa para configuração completa

