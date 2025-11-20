# 🤖 Sistema LLM-First Tools - Overview Rápido

> **Arquitetura Híbrida:** Skills + MCPs + Scripts

---

## 🎯 Skills Disponíveis (Auto-descoberta)

Claude descobre e usa automaticamente:

### 1. `tool-inventory`
- Lista scripts disponíveis antes de criar novos
- Evita duplicação
- **Uso:** Automático quando for criar bash/python/npm scripts

### 2. `odoo-ops` (se aplicável ao projeto)
- Operações específicas do framework
- **Uso:** Automático quando mencionar serviços

---

## ✨ MCPs Instalados (Integrações Nativas)

Claude usa automaticamente como tools nativos:

### 1. GitHub MCP (`github`)
- Repos, PRs, issues, commits, branches
- **Uso:** "Crie PR", "Liste issues", "Mostre commits"

### 2. Git MCP (`git`)
- status, diff, log, commit, branch
- **Uso:** "Mostre mudanças", "Crie commit", "Histórico"

### 3. Filesystem MCP (`filesystem`)
- Navegação avançada, busca, file operations
- **Uso:** "Encontre arquivos X", "Arquivos modificados hoje"

**Ver MCPs:** `claude mcp list` ou `cat .mcp.json`

---

## 📁 Scripts Reutilizáveis

**Localização:** `.claude/scripts/`

**Estrutura:**
- `bash/` - Shell scripts
- `python/` - Python scripts
- `npm/` - Node scripts

---

## 🔄 Workflow Híbrido (Exemplo)

1. Usuário: "Faça deploy do módulo X"
2. **Skill tool-inventory** → Encontra deploy script
3. **Skill específico** → Executa deploy
4. **MCP Git** → git status, git diff, commit
5. **MCP GitHub** → Cria Pull Request
6. **Skill** → Health check pós-deploy
7. ✅ **Deploy completo + PR criado!**

---

## 📖 Documentação Completa

- **Detalhes:** `.claude/LLM_FIRST_TOOLS.md`
- **ADR:** [ADR-005](../decisions/ADR-INDEX.md#adr-005)

---

**Última atualização:** 2025-11-17
**Status:** ✅ ATIVO
