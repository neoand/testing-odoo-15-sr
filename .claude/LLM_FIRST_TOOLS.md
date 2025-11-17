# 🤖 LLM-First Tools System - Arquitetura Híbrida Completa

> **Criado:** 2025-11-17
> **Atualizado:** 2025-11-17 (Adicionados MCPs)
> **Versão:** 2.0 (Híbrida Skills + MCPs)
> **Objetivo:** Sistema de ferramentas reutilizáveis onde Claude descobre e usa automaticamente, eliminando duplicação de scripts

---

## 🎯 Problema Resolvido

### Antes (Problemático) ❌
- Claude criava scripts novos a cada sessão
- Duplicação massiva de arquivos
- HD cheio de scripts iguais
- Sem memória de ferramentas disponíveis
- Usuário precisava lembrar e dizer "use o script X"
- Sem integração nativa com GitHub, Git, etc.

### Agora (LLM-First Híbrido) ✅
- Claude **descobre automaticamente** ferramentas disponíveis (Skills + MCPs)
- **Zero duplicação** - verifica inventário antes de criar
- Scripts **centralizados** em `.claude/scripts/`
- **Skills auto-invocados** - Claude usa sem você pedir
- **MCPs nativos** - GitHub, Git, Filesystem integrados
- **Memória persistente** - sobrevive a todas as sessões
- **Performance superior** - MCPs mais rápidos que bash scripts

---

## 🏗️ Arquitetura do Sistema (4 Camadas)

### Camada 1: Skills (Auto-descoberta de Scripts Internos)
**Localização:** `.claude/skills/`

Skills são capabilities que Claude **automaticamente descobre e usa** baseado na descrição.

**Skills Disponíveis:**

#### 1. `tool-inventory/`
- **Quando usa:** Antes de criar qualquer script
- **O que faz:** Lista todos os scripts disponíveis para evitar duplicação
- **Auto-ativação:** Quando Claude vai criar bash/python/npm scripts

#### 2. `odoo-ops/`
- **Quando usa:** Operações com Odoo (restart, logs, status)
- **O que faz:** Gerencia serviços Odoo nos 2 servidores
- **Auto-ativação:** Quando mencionar Odoo, logs, restart, troubleshooting

### Camada 2: Scripts Reutilizáveis
**Localização:** `.claude/scripts/`

Scripts organizados por tipo:

```
.claude/scripts/
├── bash/           # Scripts bash para operações de servidor
│   ├── odoo-restart.sh
│   ├── odoo-logs.sh
│   └── odoo-health-check.sh
├── python/         # Scripts Python e MCP server
│   └── mcp_server.py
└── npm/            # Scripts npm (se houver package.json)
```

### Camada 3: MCPs Oficiais (IMPLEMENTADO!) ✨
**Localização:** `.mcp.json` (raiz do projeto)

MCPs (Model Context Protocol) são servers oficiais do Anthropic que expõem tools nativos para Claude.

**MCPs Instalados:**

#### 1. **GitHub MCP** (`@modelcontextprotocol/server-github`)
- **Capabilities:** Repos, PRs, issues, commits, branches
- **Quando Claude usa:** Automaticamente quando você menciona GitHub, PR, issues
- **Exemplos:**
  - "Crie um PR com essas mudanças"
  - "Liste issues abertas"
  - "Mostre commits recentes"

#### 2. **Filesystem MCP** (`@modelcontextprotocol/server-filesystem`)
- **Capabilities:** Navegação avançada, busca de arquivos, operações em batch
- **Escopo:** `/Users/andersongoliveira/testing_odoo_15_sr`
- **Quando Claude usa:** Automaticamente para operações de arquivo avançadas
- **Exemplos:**
  - "Encontre todos os modelos que herdam de res.partner"
  - "Liste arquivos modificados nas últimas 24h"

#### 3. **Git MCP** (`@modelcontextprotocol/server-git`)
- **Capabilities:** status, diff, log, commit, branch, stash
- **Repo:** `/Users/andersongoliveira/testing_odoo_15_sr`
- **Quando Claude usa:** Automaticamente para operações git
- **Exemplos:**
  - "Mostre o que mudou desde ontem"
  - "Crie commit com mudanças"
  - "Qual o histórico de commits?"

**Vantagens dos MCPs:**
- ✅ Tools nativos = mais rápidos
- ✅ Mantidos pela comunidade oficial
- ✅ Atualizações automáticas (npm)
- ✅ Claude descobre automaticamente
- ✅ Melhor performance que bash scripts

**Configuração:** Ver arquivo `.mcp.json` na raiz

---

### Camada 4: Slash Commands (Atalhos Explícitos)
**Localização:** `.claude/commands/`

Para quando você quer controle direto. Pode chamar Skills e MCPs internamente.

---

## 📚 Scripts Disponíveis

### 1. odoo-restart.sh
**Propósito:** Reiniciar Odoo em testing ou produção

**Uso:**
```bash
./.claude/scripts/bash/odoo-restart.sh [testing|production]
```

**Exemplos:**
```bash
# Produção (padrão)
./.claude/scripts/bash/odoo-restart.sh production

# Testing
./.claude/scripts/bash/odoo-restart.sh testing
```

**Claude usa automaticamente quando:**
- Você pede para reiniciar Odoo
- Após fazer deploy de módulos
- Durante troubleshooting

---

### 2. odoo-logs.sh
**Propósito:** Ver logs do Odoo

**Uso:**
```bash
./.claude/scripts/bash/odoo-logs.sh [server] [mode] [lines]
```

**Parâmetros:**
- `server`: testing ou production (padrão: production)
- `mode`: lines ou follow (padrão: lines)
- `lines`: número de linhas (padrão: 100)

**Exemplos:**
```bash
# Últimas 100 linhas da produção
./.claude/scripts/bash/odoo-logs.sh production lines 100

# Seguir logs em tempo real (testing)
./.claude/scripts/bash/odoo-logs.sh testing follow

# Últimas 500 linhas
./.claude/scripts/bash/odoo-logs.sh production lines 500
```

**Claude usa automaticamente quando:**
- Você pede para ver logs
- Troubleshooting de erros
- Análise de performance

---

### 3. odoo-health-check.sh
**Propósito:** Verificação completa de saúde do servidor

**Uso:**
```bash
./.claude/scripts/bash/odoo-health-check.sh [testing|production]
```

**Verifica:**
1. ✅ Recursos do sistema (RAM, disco, uptime)
2. ✅ Status dos serviços (Odoo, PostgreSQL, Nginx)
3. ✅ Workers ativos
4. ✅ Conexões com database
5. ✅ Erros recentes nos logs

**Claude usa automaticamente quando:**
- Você pede para verificar status do servidor
- Antes de fazer mudanças críticas
- Troubleshooting geral

---

## 🔄 Como Funciona (Workflow Automático)

### Cenário 1: Você pede "Reinicie o Odoo na produção"

1. **Claude ativa o skill `odoo-ops`** (baseado na descrição)
2. **Skill verifica se existe script** via `tool-inventory`
3. **Script encontrado:** `.claude/scripts/bash/odoo-restart.sh`
4. **Claude executa:** `./odoo-restart.sh production`
5. **✅ Pronto!** Sem criar script novo

### Cenário 2: Você pede "Crie um script para fazer backup"

1. **Claude ativa skill `tool-inventory`**
2. **Verifica:** `ls .claude/scripts/bash/backup*.sh`
3. **Não encontrado** → Claude cria novo script
4. **Salva em:** `.claude/scripts/bash/db-backup.sh`
5. **Documenta:** Header completo com usage
6. **Próxima vez:** Claude reutiliza esse script! ✅

### Cenário 3: Você pede "Faça deploy do módulo chatroom_sms_advanced" (HÍBRIDO!)

1. **Skill `tool-inventory`** → Verifica se existe script de deploy
2. **Script encontrado:** `.claude/scripts/bash/deploy-module.sh` (ou cria se não existir)
3. **Skill `odoo-ops`** → Executa deploy no servidor
4. **MCP Git** → Automaticamente verifica mudanças: `git status`, `git diff`
5. **MCP Git** → Cria commit: "Deploy módulo chatroom_sms_advanced"
6. **MCP GitHub** → Cria Pull Request automaticamente
7. **Skill `odoo-ops`** → Health check pós-deploy
8. **✅ Deploy completo + PR criado + Servidor verificado!**

**Resultado:** Workflow completo automatizado usando **Skills + MCPs juntos!**

### Cenário 4: Você pede "Mostre arquivos modificados hoje que herdam de res.partner"

1. **MCP Filesystem** → Busca arquivos `.py` modificados hoje
2. **MCP Filesystem** → Grep por `_inherit.*res.partner` nos arquivos
3. **MCP Git** → Mostra diff dos arquivos encontrados
4. **✅ Resultado completo** usando apenas MCPs!

---

## 🎨 Padrões e Convenções

### Nomenclatura de Scripts
```
verbo-substantivo.extensão

Exemplos:
✅ odoo-restart.sh
✅ db-backup.sh
✅ deploy-module.sh
❌ restart.sh (muito genérico)
❌ script1.sh (não descritivo)
```

### Header Obrigatório
Todo script deve ter:

```bash
#!/bin/bash
# Script: nome-do-script.sh
# Description: O que este script faz em uma linha
# Usage: ./nome-do-script.sh [param1] [param2]
# Author: Claude
# Created: YYYY-MM-DD

set -e  # Exit on error

# Script code here...
```

### Parâmetros
- Sempre com valores padrão: `SERVER=${1:-production}`
- Help message se argumentos inválidos
- Validação de inputs

---

## 📋 Checklist para Claude

Antes de criar qualquer script, Claude deve:

```markdown
[ ] 1. Ativar skill `tool-inventory` (automático)
[ ] 2. Listar scripts existentes
[ ] 3. Verificar se já existe script similar
[ ] 4. Se existe → REUTILIZAR
[ ] 5. Se não existe → CRIAR em .claude/scripts/[tipo]/
[ ] 6. Adicionar header completo
[ ] 7. Fazer chmod +x
[ ] 8. Documentar se resolver problema novo
```

---

## 🚀 Próximos Passos (Opcional)

### Configurar MCP Server
Para que scripts apareçam como tools nativos para Claude:

```bash
# Adicionar MCP server local (stdio transport)
claude mcp add --transport stdio odoo-tools -- python3 /Users/andersongoliveira/testing_odoo_15_sr/.claude/scripts/python/mcp_server.py

# Verificar
claude mcp list

# Usar
# Claude verá automaticamente:
# - odoo_restart
# - odoo_logs
# - odoo_health_check
```

**Vantagens:**
- Scripts aparecem como ferramentas nativas
- Claude os vê na lista de tools disponíveis
- Invocação ainda mais automática

**Desvantagens:**
- Configuração extra necessária
- Mais uma camada de abstração

**Recomendação:** Skills já resolvem 95% dos casos. MCP é opcional para cenários avançados.

---

## 📊 Inventário Atual

### Skills (2)
1. ✅ `tool-inventory` - Gerenciamento de inventário de scripts
2. ✅ `odoo-ops` - Operações Odoo automáticas

### Scripts Bash (3)
1. ✅ `odoo-restart.sh` - Reiniciar Odoo
2. ✅ `odoo-logs.sh` - Ver logs
3. ✅ `odoo-health-check.sh` - Health check completo

### Scripts Python (1)
1. ✅ `mcp_server.py` - MCP server (opcional)

### Scripts NPM (0)
- Nenhum ainda (adicionar se projeto tiver package.json)

---

## 🧠 Integração com Memória

### Como Claude Aprende

1. **Novo script criado** → Documentado automaticamente
2. **Problema resolvido** → Salvo em `.claude/memory/errors/ERRORS-SOLVED.md`
3. **Comando com sudo** → Salvo em `.claude/memory/commands/COMMAND-HISTORY.md`
4. **Padrão descoberto** → Adicionado a `.claude/memory/patterns/PATTERNS.md`

### Exemplo de Aprendizado

```markdown
# Situação: Script precisa de sudo

1. Claude tenta: ./odoo-restart.sh
2. Erro: Permission denied
3. Claude usa sudo: sudo ./odoo-restart.sh (ou comando SSH com sudo)
4. Sucesso! ✅
5. Claude SALVA em COMMAND-HISTORY.md:
   "odoo-restart.sh sempre precisa sudo quando executado remotamente"
6. Próxima sessão: Claude JÁ SABE usar sudo
```

---

## 🎓 Vantagens desta Arquitetura

### 1. Zero Duplicação
✅ Claude verifica inventário antes de criar
✅ Reutiliza scripts existentes
✅ HD limpo e organizado

### 2. Descoberta Automática
✅ Skills auto-invocados por Claude
✅ Não precisa pedir para usar script X
✅ Claude escolhe ferramenta certa sozinho

### 3. Memória Permanente
✅ Scripts sobrevivem a todas as sessões
✅ Conhecimento acumulado cresce
✅ Claude fica expert no seu projeto

### 4. Manutenção Simplificada
✅ Um lugar para todos os scripts
✅ Nomenclatura consistente
✅ Documentação obrigatória

### 5. Escalável
✅ Fácil adicionar novos scripts
✅ Fácil criar novos skills
✅ MCPs oficiais para integrações externas

### 6. Integrações Nativas (NOVO!)
✅ GitHub, Git, Filesystem via MCPs
✅ Performance superior a bash scripts
✅ Mantidos pela comunidade oficial
✅ Workflows híbridos (Skills + MCPs)

---

## 🔌 Gerenciamento de MCPs

### MCPs Instalados

Ver lista de MCPs:
```bash
claude mcp list
```

Ver configuração:
```bash
cat .mcp.json
```

### Adicionar Novos MCPs

**Sintaxe geral:**
```bash
claude mcp add --transport stdio --scope project <name> -- npx -y @modelcontextprotocol/server-<name> [args]
```

**Exemplos de MCPs úteis:**

#### PostgreSQL (Para queries diretas)
```bash
claude mcp add --transport stdio --scope project postgresql -- npx -y @modelcontextprotocol/server-postgres postgresql://user:pass@localhost/realcred
```

#### Memory (Conhecimento persistente)
```bash
claude mcp add --transport stdio --scope project memory -- npx -y @modelcontextprotocol/server-memory
```

#### Fetch (Web scraping)
```bash
claude mcp add --transport stdio --scope project fetch -- npx -y @modelcontextprotocol/server-fetch
```

#### Slack (Notificações)
```bash
claude mcp add --transport stdio --scope project slack --env SLACK_BOT_TOKEN=xoxb-your-token -- npx -y @modelcontextprotocol/server-slack
```

### Remover MCP

```bash
claude mcp remove <name>
```

**Exemplo:**
```bash
claude mcp remove github
```

### Atualizar MCPs

MCPs são instalados via npx com flag `-y`, então sempre puxam a versão mais recente. Para forçar atualização:

```bash
# Remover e reinstalar
claude mcp remove <name>
claude mcp add --transport stdio --scope project <name> -- npx -y @modelcontextprotocol/server-<name>
```

### Debugging MCPs

Se MCP não funcionar:

1. **Verificar logs:**
   - MCPs rodam via npx, erros aparecem no console do Claude Code

2. **Testar instalação:**
   ```bash
   npx -y @modelcontextprotocol/server-github
   # Deve executar sem erros
   ```

3. **Verificar permissões:**
   - Filesystem MCP precisa de acesso ao diretório
   - GitHub MCP pode precisar de autenticação (via `/mcp`)

4. **Recarregar Claude Code:**
   - Após adicionar MCP, pode precisar reiniciar sessão

### MCPs Recomendados por Caso de Uso

**Para desenvolvimento Odoo:**
- ✅ `git` - Operações git
- ✅ `github` - PRs e issues
- ✅ `filesystem` - Navegação de código
- ⚠️ `postgresql` - Queries no banco (se precisar)

**Para automação:**
- ✅ `fetch` - Web scraping
- ⚠️ `slack`/`discord` - Notificações

**Para memória avançada:**
- ⚠️ `memory` - Conhecimento em grafo (experimental)

**Legenda:**
- ✅ Instalado e recomendado
- ⚠️ Opcional conforme necessidade

---

## 🔍 Troubleshooting

### Claude não está usando os scripts

**Verificar:**
1. Skills estão em `.claude/skills/`?
2. Arquivo `SKILL.md` tem frontmatter correto?
3. Descrição do skill é clara?

**Solução:**
- Revisar descrição do skill
- Testar explicitamente: "Use o skill tool-inventory"

### Script não tem permissão

```bash
chmod +x .claude/scripts/bash/*.sh
chmod +x .claude/scripts/python/*.py
```

### MCPs não aparecem ou não funcionam

**Verificar:**
1. MCPs foram adicionados? `claude mcp list`
2. Arquivo `.mcp.json` existe na raiz?
3. Node.js/npm instalados? (MCPs usam npx)

**Solução:**
```bash
# Verificar configuração
cat .mcp.json

# Listar MCPs
claude mcp list

# Reinstalar MCP problemático
claude mcp remove <name>
claude mcp add --transport stdio --scope project <name> -- npx -y @modelcontextprotocol/server-<name>
```

### GitHub MCP precisa autenticação

Alguns MCPs (como GitHub) podem precisar de token:

```bash
# Via /mcp no chat
/mcp

# Ou via environment variable
claude mcp remove github
claude mcp add --transport stdio --scope project github --env GITHUB_TOKEN=ghp_your_token -- npx -y @modelcontextprotocol/server-github
```

---

## 📞 Referência Rápida

### Verificar Inventário
```bash
ls -lh .claude/scripts/bash/
ls -lh .claude/scripts/python/
```

### Testar Script Manualmente
```bash
./.claude/scripts/bash/odoo-health-check.sh production
```

### Ver Skills Disponíveis
```bash
ls -la .claude/skills/
```

### Ver MCPs Instalados
```bash
claude mcp list
cat .mcp.json
```

### Adicionar Novo Script
```bash
# 1. Criar script com header completo
# 2. Salvar em .claude/scripts/[tipo]/
# 3. chmod +x
# 4. Testar manualmente
# 5. Claude descobrirá automaticamente!
```

### Adicionar Novo MCP
```bash
claude mcp add --transport stdio --scope project <name> -- npx -y @modelcontextprotocol/server-<name>
```

---

## ✨ Conclusão

Este sistema **híbrido Skills + MCPs** transforma Claude em um **agente verdadeiramente autônomo** que:

**Skills (Internos):**
- 🧠 Lembra de todos os scripts locais
- 🔍 Descobre e reutiliza automaticamente
- ♻️ Zero duplicação de código

**MCPs (Externos):**
- ⚡ Integrações nativas (GitHub, Git, Filesystem)
- 🚀 Performance superior
- 🔄 Mantidos pela comunidade

**Resultado Combinado:**
- 🎯 Workflows completos automatizados
- 📚 Conhecimento acumulado cresce
- 🤖 Claude cada vez mais expert
- ✅ Você pede, Claude faz - sem overhead

**Exemplo Real:**
```
Você: "Faça deploy e crie PR"

Claude:
1. Skill tool-inventory → Encontra script deploy
2. Skill odoo-ops → Executa deploy
3. MCP Git → Cria commit
4. MCP GitHub → Cria PR
5. Skill odoo-ops → Health check
✅ Tudo automatizado!
```

---

**Última atualização:** 2025-11-17
**Versão:** 2.0 (Híbrida Skills + MCPs)
**Status:** ✅ Operacional com 3 MCPs instalados

**MCPs Ativos:**
- ✅ GitHub (repos, PRs, issues)
- ✅ Git (commits, diff, log)
- ✅ Filesystem (navegação avançada)

**Documentação completa:** Este arquivo + [ADR-005](.claude/memory/decisions/ADR-INDEX.md#adr-005)
