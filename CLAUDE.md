# 🧠 Memória do Projeto - Odoo 15 Testing RealCred

> **IMPORTANTE**: Este arquivo é carregado AUTOMATICAMENTE em TODAS as sessões do Claude Code.
> Contém contexto permanente, decisões, padrões e conhecimento acumulado.

---

## 🎯 Contexto do Projeto

**Nome:** testing_odoo_15_sr
**Tipo:** Odoo 15 - Customizações RealCred
**Ambiente:** Testing/Development
**Linguagem:** Python, XML, JavaScript
**Framework:** Odoo 15.0

**Módulos Principais:**
- `chatroom_sms_advanced` - Contact Center SMS (módulo crítico)
- `crm` - CRM customizado
- `contacts` - Gestão de parceiros
- Integração API Kolmeya (SMS)

**Database:** PostgreSQL
**Servidor:** Em `servidor-testing-odoo/`

---

## 📋 Importações de Contexto

@.claude/memory/context/projeto.md
@.claude/memory/context/odoo.md
@.claude/memory/context/servidores.md
@.claude/memory/decisions/ADR-INDEX.md
@.claude/memory/errors/ERRORS-SOLVED.md
@.claude/memory/patterns/PATTERNS.md
@.claude/memory/commands/COMMAND-HISTORY.md
@.claude/memory/learnings/git-workflow.md
@.claude/memory/AUTO-LEARNING-PROTOCOL.md
@.claude/memory/THINKING-MODE-PROTOCOL.md

---

## 🧠 PROTOCOLO DE AUTO-APRENDIZADO (CRÍTICO!)

### Regras Fundamentais

**❌ NUNCA:**
- Assumir ou deduzir sem verificar
- Repetir comando que falhou sem modificação
- Executar sem checar histórico primeiro
- Esquecer de documentar erro resolvido
- Criar script novo sem verificar inventário (.claude/scripts/)

**✅ SEMPRE:**
1. **ANTES de executar comando:** Verificar COMMAND-HISTORY.md
2. **Se comando falhar:** Documentar IMEDIATAMENTE em ERRORS-SOLVED.md
3. **Se usar sudo:** Salvar regra em COMMAND-HISTORY.md
4. **Se pesquisar:** Salvar resultado em learnings/
5. **Se incerto:** Pesquisar docs oficiais, NUNCA assumir
6. **QUANDO APRENDER ALGO:** Ativar thinking mode, raciocinar profundamente, salvar "na rocha"
7. **ANTES de criar script:** Verificar `.claude/scripts/` via skill `tool-inventory`, reutilizar se existir
8. **QUANDO criar algo reutilizável:** Sincronizar com Claude-especial (ver ADR-006)
9. **ANTES de commitar:** Verificar se deve ir para template

### Checklist Pré-Execução

```
[ ] Verificar se já fiz isso antes (COMMAND-HISTORY.md)
[ ] Verificar se erro já foi resolvido (ERRORS-SOLVED.md)
[ ] Se SSH/sistema, confirmar se precisa sudo
[ ] Se incerto, pesquisar docs oficiais
[ ] Se falhar, documentar automaticamente
```

### Aprendizado Automático de Comandos

**Exemplo:** Se `systemctl restart odoo` falhar com "Permission denied":
1. ✅ Tentar com `sudo systemctl restart odoo`
2. ✅ SALVAR em COMMAND-HISTORY.md: "systemctl SEMPRE precisa sudo"
3. ✅ Próxima vez: usar sudo automaticamente

**Sistema de Memória Crescente:**
- Sessão 1: Conhecimento base
- Sessão 2: Base + aprendizados da sessão 1
- Sessão 3: Base + aprendizados sessões 1+2
- Sessão N: Claude é EXPERT! 🧠⚡

### Fontes Priorizadas (em ordem)

1. **Docs Oficiais:** Odoo, Python, PostgreSQL (SEMPRE primeiro)
2. **GitHub Issues:** Odoo/odoo, OCA (bugs conhecidos)
3. **Stack Overflow:** Respostas aceitas + recentes
4. **Memória Local:** COMMAND-HISTORY, ERRORS-SOLVED, PATTERNS

**NUNCA usar informação não validada!**

---

## 🎨 Padrões e Convenções

### Código Python/Odoo
- **Indentação:** 4 espaços (PEP 8)
- **Encoding:** UTF-8 com BOM `# -*- coding: utf-8 -*-`
- **Docstrings:** Google style em português
- **Imports:** Ordem: stdlib → odoo → local
- **Naming:** snake_case para funções/variáveis

### Views XML
- **Indentação:** 4 espaços
- **IDs:** `module_name.view_model_type_description`
- **Priority:** Múltiplos de 10 (10, 20, 30...)
- **Comentários:** Seções demarcadas com `<!-- ========== -->`

### Security
- **SEMPRE** criar ir.model.access.csv para novos models
- **SEMPRE** considerar record rules
- **TESTAR** com diferentes perfis de usuário
- **DOCUMENTAR** decisões de segurança

### Commits
- **Mensagens:** `tipo: descrição` (feat/fix/refactor/docs)
- **Idioma:** Português brasileiro
- **Co-authored:** Incluir Claude

---

## 🚨 Conhecimento Crítico

### Problemas Conhecidos
1. **Permissões CRM:** Vendedores precisam record rules para ver apenas suas oportunidades
2. **Módulo SMS:** Performance de queries precisa otimização
3. **Fotos perdidas:** Investigar causa raiz de perda de imagens de funcionários
4. **Admin locked:** Já resolvido (ver errors/)

### Decisões Arquiteturais
- Usar herança `_inherit` ao invés de `_inherits` para CRM
- API Kolmeya: timeout de 30s, retry 3x
- Cache de mensagens SMS: Redis (futuro)
- Logs estruturados em JSON
- **LLM-First Tools:** Skills + Scripts centralizados (ver ADR-005)

### Integrações Importantes
- **Kolmeya API:** SMS gateway principal
- **PostgreSQL:** Queries otimizadas, índices críticos
- **Mail:** Chatter customizado para SMS

---

## 🔄 PROTOCOLO DE SINCRONIZAÇÃO DUAL (CRÍTICO!)

### Regra de Ouro

**TUDO que for desenvolvido, criado, aprimorado ou descoberto tem DUPLO DESTINO:**

1. **Aplicado AQUI** (testing-odoo-15-sr)
2. **Sincronizado com Template** (Claude-especial)

### Checklist de Sincronização

Ao criar/modificar algo, perguntar:

```
[ ] É genérico ou específico de Odoo?
[ ] Útil para qualquer projeto ou só este?
[ ] Se GENÉRICO:
    [ ] Copiar para /Users/andersongoliveira/Claude-especial/
    [ ] Remover partes específicas de Odoo
    [ ] Commitar em Claude-especial
    [ ] Push para GitHub
    [ ] Documentar em sync-log.md
[ ] Se ESPECÍFICO:
    [ ] Apenas commitar aqui
```

### O Que Sincronizar

**✅ SINCRONIZAR:**
- Skills genéricos
- Scripts bash/python reutilizáveis
- Melhorias em protocolos
- ADRs de arquitetura geral
- Patterns universais
- Melhorias em LLM_FIRST_TOOLS.md
- Novos MCPs úteis

**❌ NÃO SINCRONIZAR:**
- Código Odoo específico
- Scripts de servidores (odoo-restart, etc)
- ADRs de negócio (Kolmeya, CRM)
- Contexto de servidores
- Erros específicos de Odoo

**Referência Completa:** Ver ADR-006

---

## 🤖 Sistema LLM-First Tools Híbrido (Skills + MCPs) v2.0

### Skills Disponíveis (Auto-descoberta Scripts Internos)
Claude descobre e usa automaticamente:

1. **`tool-inventory`**
   - Lista scripts disponíveis antes de criar novos
   - Evita duplicação
   - Uso: Automático quando for criar bash/python/npm scripts

2. **`odoo-ops`**
   - Operações Odoo (restart, logs, health-check)
   - Uso: Automático quando mencionar Odoo services
   - Funciona em ambos servidores (testing + production)

### MCPs Instalados (Integrações Nativas) ✨
Claude usa automaticamente como tools nativos:

1. **GitHub MCP** (`github`)
   - Repos, PRs, issues, commits, branches
   - Uso: "Crie PR", "Liste issues", "Mostre commits"

2. **Git MCP** (`git`)
   - status, diff, log, commit, branch
   - Uso: "Mostre mudanças", "Crie commit", "Histórico"

3. **Filesystem MCP** (`filesystem`)
   - Navegação avançada, busca, file operations
   - Uso: "Encontre modelos que herdam X", "Arquivos modificados hoje"

**Ver MCPs:** `claude mcp list` ou `cat .mcp.json`

### Scripts Reutilizáveis
Localização: `.claude/scripts/`

**Bash:**
- `odoo-restart.sh [testing|production]` - Reiniciar Odoo
- `odoo-logs.sh [server] [lines|follow] [N]` - Ver logs
- `odoo-health-check.sh [server]` - Health check completo

### Workflow Híbrido (Exemplo)
1. Você: "Faça deploy do chatroom_sms_advanced"
2. **Skill tool-inventory** → Encontra deploy script
3. **Skill odoo-ops** → Executa deploy
4. **MCP Git** → git status, git diff
5. **MCP Git** → Cria commit automaticamente
6. **MCP GitHub** → Cria Pull Request
7. **Skill odoo-ops** → Health check pós-deploy
8. ✅ **Deploy completo + PR criado + Servidor OK!**

**Documentação completa:** `.claude/LLM_FIRST_TOOLS.md` + [ADR-005](.claude/memory/decisions/ADR-INDEX.md#adr-005)

---

## 🎯 Prioridades Atuais

1. **Alta:** Estabilidade do módulo SMS
2. **Alta:** Segurança e permissões corretas
3. **Média:** Performance e otimizações
4. **Média:** Documentação técnica
5. **Baixa:** Features novas (após estabilização)

---

## 💡 Comandos Frequentes

```bash
# Restart Odoo
sudo systemctl restart odoo

# Update module
odoo-bin -c odoo.conf -d DATABASE -u MODULE

# Run tests
odoo-bin -c odoo.conf -d DATABASE -u MODULE --test-enable --stop-after-init

# PostgreSQL
sudo -u postgres psql DATABASE

# Logs
tail -f /var/log/odoo/odoo-server.log

# Git
git status
git add .
git commit -m "tipo: descrição"
```

---

## 📚 Referências Rápidas

**Documentação:**
- Odoo 15: https://www.odoo.com/documentation/15.0/
- PostgreSQL: https://www.postgresql.org/docs/
- Python 3: https://docs.python.org/3/

**Estrutura do Projeto:**
- Módulos custom: `./chatroom_sms_advanced`, `./temp_modules`
- Docs: `./server_documentation`
- Scripts: `./cleanup_scripts`
- Claude Config: `./.claude/`

---

## 🔄 Última Atualização

**Data:** 2025-11-17
**Por:** Claude + Anderson
**Versão:** 2.0 (com Auto-Aprendizado)
**Próxima revisão:** Automática a cada sessão

---

## 📝 Notas

- Este arquivo deve ser mantido ENXUTO (< 500 linhas)
- Detalhes profundos vão em arquivos específicos em `.claude/memory/`
- Use `#` no chat para adicionar memórias rapidamente
- Use `/memory` para editar este arquivo
- Revise mensalmente para remover informações obsoletas

**FIM DO CLAUDE.md**
