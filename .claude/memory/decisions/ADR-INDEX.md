# 📐 Architecture Decision Records (ADRs) - Índice

> **Propósito:** Documentar TODAS as decisões arquiteturais e técnicas importantes do projeto.

---

## O Que São ADRs?

**Architecture Decision Records** documentam decisões técnicas importantes:
- **Contexto:** Por que precisamos decidir?
- **Decisão:** O que escolhemos?
- **Alternativas:** O que consideramos?
- **Consequências:** Impactos da decisão

**Benefícios:**
- 🧠 Memória institucional
- 🤔 Raciocínio documentado
- 🔄 Facilita onboarding
- ✅ Evita refazer decisões

---

## 📋 ADRs Registrados

| # | Data | Título | Status | Tags |
|---|------|--------|--------|------|
| 001 | 2025-11-17 | [Sistema de Memória Claude](#adr-001) | ✅ Aceito | #infra #claude |
| 002 | 2025-11-16 | [Herança vs Delegate no CRM](#adr-002) | ✅ Aceito | #odoo #crm |
| 003 | 2025-11-16 | [Integração Kolmeya API](#adr-003) | ✅ Aceito | #integration #sms |
| 004 | 2025-11-15 | [Estratégia de Cache](#adr-004) | 🔄 Proposto | #performance |
| 005 | 2025-11-17 | [Arquitetura LLM-First Tools](#adr-005) | ✅ Aceito | #infra #claude #automation |

---

## ADR-001: Sistema de Memória Claude

**Data:** 2025-11-17
**Status:** ✅ Aceito
**Decisores:** Anderson + Claude

### Contexto
Claude Code perdia contexto entre sessões, causando:
- Reexplicação constante de decisões
- Repetição de erros já resolvidos
- Perda de conhecimento acumulado
- Frustração e perda de tempo

### Decisão
Implementar sistema hierárquico de memória usando CLAUDE.md oficial:

```
CLAUDE.md (raiz)
.claude/memory/
  ├── context/      - Contexto permanente
  ├── decisions/    - ADRs
  ├── errors/       - Erros resolvidos
  ├── patterns/     - Padrões descobertos
  ├── odoo/        - Conhecimento Odoo
  └── learnings/   - Aprendizados
```

### Alternativas Consideradas

1. **claude-mem (MCP + ChromaDB)**
   - ✅ Busca semântica
   - ✅ Escalável
   - ❌ Complexidade alta
   - ❌ Dependência externa
   - ❌ Setup não trivial

2. **Memory MCP (SQLite)**
   - ✅ Persistente
   - ✅ Estruturado
   - ❌ Requer MCP server
   - ❌ Configuração adicional

3. **CLAUDE.md nativo** ← **ESCOLHIDO**
   - ✅ Oficial Anthropic
   - ✅ Zero config
   - ✅ Simples e eficaz
   - ✅ Markdown legível
   - ✅ Git-friendly
   - ⚠️ Manual para atualizar

### Consequências

**Positivas:**
- ✅ Contexto persiste entre sessões
- ✅ Conhecimento acumulativo
- ✅ Erros documentados = não repetidos
- ✅ Onboarding mais rápido
- ✅ Decisões rastreáveis
- ✅ Zero overhead de setup

**Negativas:**
- ⚠️ Arquivos precisam ser mantidos
- ⚠️ Pode crescer muito (mitigation: modularizar)
- ⚠️ Busca é textual, não semântica

**Neutral:**
- 📝 Disciplina para documentar

### Implementação
- CLAUDE.md na raiz com @imports
- Estrutura em .claude/memory/
- Templates para ADRs e erros
- Docs em português

---

## ADR-002: Herança vs Delegate no CRM

**Data:** 2025-11-16
**Status:** ✅ Aceito

### Contexto
Precisávamos estender `crm.lead` com campos customizados para SMS integration.

Duas opções:
- `_inherit = 'crm.lead'` (herança)
- `_inherits = {'crm.lead': 'lead_id'}` (delegate)

### Decisão
Usar `_inherit` para extensão direta do modelo.

### Razão
- Simplicidade
- Sem overhead de joins extras
- Padrão Odoo para customizações
- Melhor performance

### Consequências
- ✅ Código mais simples
- ✅ Performance melhor
- ⚠️ Módulo precisa estar instalado com CRM

---

## ADR-003: Integração Kolmeya API

**Data:** 2025-11-16
**Status:** ✅ Aceito

### Contexto
Precisávamos integrar envio de SMS via gateway Kolmeya.

Opções:
1. Requests direto
2. Biblioteca específica Kolmeya (se houver)
3. Queue async (Celery/RabbitMQ)

### Decisão
Usar `requests` síncrono com timeout de 30s e retry de 3x.

### Razão
- Simplicidade > complexidade prematura
- Volume de SMS ainda baixo
- Kolmeya API é REST simples
- Retry nativo do Odoo suficiente

### Consequências
- ✅ Implementação rápida
- ✅ Fácil debug
- ✅ Sem infraestrutura adicional
- ⚠️ Bloqueia thread durante envio
- ⚠️ Pode precisar async no futuro (>1000 SMS/dia)

### Quando Reavaliar
- Volume > 1000 SMS/dia
- Latência > 5s no Kolmeya
- Complaints de performance

---

## ADR-004: Estratégia de Cache

**Data:** 2025-11-15
**Status:** 🔄 Proposto (não implementado ainda)

### Contexto
Queries repetidas em `crm.lead` para buscar dados de `res.partner`.

### Proposta
Implementar cache Redis para:
- Partner data (phone, email, name)
- SMS status
- Configurações frequentes

### Alternativas
1. Redis
2. Memcached
3. Cache nativo Odoo (ormcache)
4. Compute fields com store=True

### Análise Necessária
- Overhead vs benefício
- Infraestrutura adicional
- Complexidade de invalidação

**Status:** Aguardando medições de performance real

---

## ADR-005: Arquitetura LLM-First Tools (Híbrida Skills + MCPs)

**Data:** 2025-11-17
**Última atualização:** 2025-11-17 (Adicionados MCPs)
**Status:** ✅ Aceito e Evoluído
**Decisores:** Anderson + Claude

### Contexto

Claude estava criando scripts duplicados a cada sessão porque:
- Sem memória de ferramentas disponíveis
- Sem inventário de scripts existentes
- HD ficando cheio de scripts iguais
- Usuário precisava manualmente dizer "use o script X"
- Cada sessão = novos scripts para mesmas tarefas

**Problema crítico:** Falta de sistema de descoberta automática de ferramentas.

### Decisão

Implementar arquitetura LLM-First em 4 camadas:

**Camada 1: Skills (Auto-descoberta)**
- Local: `.claude/skills/`
- Claude descobre e usa automaticamente
- Baseado em descrições (model-driven)
- Skills criados:
  - `tool-inventory/` - Lista ferramentas disponíveis
  - `odoo-ops/` - Operações Odoo automáticas

**Camada 2: Scripts Centralizados**
- Local: `.claude/scripts/`
- Organização por tipo: `bash/`, `python/`, `npm/`
- Nomenclatura padronizada: `verbo-substantivo.ext`
- Header obrigatório com documentação
- Scripts base criados:
  - `odoo-restart.sh`
  - `odoo-logs.sh`
  - `odoo-health-check.sh`

**Camada 3: MCPs Oficiais (IMPLEMENTADO!)** ✨
- MCPs do Anthropic para integrações externas
- Tools nativos que Claude descobre automaticamente
- Mantidos pela comunidade oficial
- MCPs instalados:
  - `github` - GitHub API (repos, PRs, issues, commits)
  - `filesystem` - Operações de arquivo avançadas
  - `git` - Operações git (log, diff, status, commit)

**Camada 4: Slash Commands (Existente)**
- Para operações que usuário quer controle direto
- Pode chamar Skills, MCPs ou scripts internamente

### Alternativas Consideradas

1. **Apenas Slash Commands**
   - ✅ Controle explícito
   - ❌ Usuário precisa lembrar de chamar
   - ❌ Não é LLM-first
   - ❌ Não resolve duplicação

2. **Apenas MCP Server**
   - ✅ Tools nativos para Claude
   - ❌ Requer configuração complexa
   - ❌ Overhead desnecessário para casos simples
   - ❌ Mais uma camada de abstração

3. **Skills + Scripts Centralizados** ← **ESCOLHIDO**
   - ✅ Descoberta automática
   - ✅ Zero duplicação
   - ✅ Simples de manter
   - ✅ Escalável
   - ✅ Git-friendly
   - ✅ LLM-first na essência

4. **Plugin System**
   - ✅ Distribuível
   - ❌ Complexidade muito alta
   - ❌ Overkill para uso interno
   - ❌ Harder to customize

### Consequências

**Positivas:**
- ✅ **Zero duplicação** - Claude verifica inventário antes de criar
- ✅ **Descoberta automática** - Skills auto-invocados + MCPs nativos
- ✅ **Memória persistente** - Scripts sobrevivem sessões
- ✅ **Centralização** - Um lugar para todos scripts
- ✅ **Escalável** - Fácil adicionar novos tools e MCPs
- ✅ **Manutenção** - Nomenclatura e docs padronizados
- ✅ **LLM-first** - Claude usa sem usuário pedir
- ✅ **HD limpo** - Sem acumulação de arquivos
- ✅ **Integrações nativas** - GitHub, Git, Filesystem via MCPs oficiais
- ✅ **Performance superior** - MCPs mais rápidos que bash scripts
- ✅ **Mantidos pela comunidade** - Atualizações automáticas via npm

**Negativas:**
- ⚠️ Skills precisam de descrições claras
- ⚠️ Scripts precisam de headers documentados
- ⚠️ Disciplina para seguir convenções

**Neutras:**
- 📝 MCP server opcional (95% dos casos não precisa)
- 📝 Skills complementam, não substituem slash commands

### Implementação

**Estrutura criada:**
```
.claude/
├── skills/
│   ├── tool-inventory/SKILL.md
│   └── odoo-ops/SKILL.md
├── scripts/
│   ├── bash/
│   │   ├── odoo-restart.sh
│   │   ├── odoo-logs.sh
│   │   └── odoo-health-check.sh
│   ├── python/
│   │   └── mcp_server.py
│   └── npm/
├── LLM_FIRST_TOOLS.md (documentação completa)
└── (raiz)
    └── .mcp.json (MCPs configurados)
```

**MCPs Instalados (.mcp.json):**
```json
{
  "mcpServers": {
    "github": "@modelcontextprotocol/server-github",
    "filesystem": "@modelcontextprotocol/server-filesystem",
    "git": "@modelcontextprotocol/server-git"
  }
}
```

**Workflow automático (Exemplo 1 - Operação Odoo):**
1. Usuário: "Reinicie o Odoo"
2. Claude ativa skill `odoo-ops` (automático)
3. Skill verifica inventário via `tool-inventory`
4. Script encontrado: `.claude/scripts/bash/odoo-restart.sh`
5. Claude executa sem criar duplicata
6. ✅ Pronto!

**Workflow automático (Exemplo 2 - Deploy + GitHub):**
1. Usuário: "Faça deploy do módulo chatroom_sms_advanced"
2. Claude ativa skill `tool-inventory` → encontra deploy script
3. Executa deploy usando script bash
4. **MCP Git** → Verifica mudanças: `git status`, `git diff`
5. **MCP Git** → Cria commit com mudanças
6. **MCP GitHub** → Cria Pull Request automaticamente
7. **Skill odoo-ops** → Verifica health do servidor
8. ✅ Deploy completo com PR criado!

**Checklist para novos scripts:**
- [ ] Verificar inventário primeiro
- [ ] Se existe, reutilizar
- [ ] Se não, criar em `.claude/scripts/[tipo]/`
- [ ] Header completo
- [ ] chmod +x
- [ ] Testar manualmente
- [ ] Documentar se resolver problema novo

### Padrões Estabelecidos

**Nomenclatura:**
```
verbo-substantivo.extensão
✅ odoo-restart.sh
✅ db-backup.sh
❌ restart.sh (genérico)
❌ script1.sh (não descritivo)
```

**Header obrigatório:**
```bash
#!/bin/bash
# Script: nome.sh
# Description: O que faz
# Usage: ./nome.sh [params]
# Author: Claude
# Created: YYYY-MM-DD
```

**Parameters:**
- Valores padrão: `VAR=${1:-default}`
- Validação de inputs
- Help message

### Quando Reavaliar

**Configurar MCP server se:**
- Volume de scripts > 20
- Necessidade de tools verdadeiramente nativos
- Integração com outras ferramentas MCP

**Criar novo Skill se:**
- Padrão de uso repetitivo identificado
- 3+ scripts relacionados a mesma área
- Oportunidade de automação clara

**Migrar para Plugin se:**
- Ferramentas úteis para comunidade
- Distribuição necessária
- Time > 5 pessoas

### Integração com Memória

Scripts documentados em:
- `.claude/memory/commands/COMMAND-HISTORY.md` - Se usar sudo
- `.claude/memory/errors/ERRORS-SOLVED.md` - Se resolver problema
- `.claude/memory/learnings/` - Descobertas importantes

### Métricas de Sucesso

**Antes:**
- 🔴 Scripts duplicados: ~10-20 por semana
- 🔴 HD uso: Crescimento descontrolado
- 🔴 Reuso: 0%
- 🔴 Claude awareness: Nenhuma

**Depois:**
- 🟢 Scripts duplicados: 0
- 🟢 HD uso: Controlado e organizado
- 🟢 Reuso: 100%
- 🟢 Claude awareness: Total

### Referência

Documentação completa: `.claude/LLM_FIRST_TOOLS.md`

---

## 📝 Template para Nova ADR

Copie quando fazer nova decisão arquitetural:

```markdown
## ADR-XXX: Título da Decisão

**Data:** YYYY-MM-DD
**Status:** 🔄 Proposto / ✅ Aceito / ❌ Rejeitado / 🗑️ Obsoleto

### Contexto
Por que precisamos decidir?

### Decisão
O que escolhemos?

### Alternativas Consideradas
1. Opção A
   - Prós
   - Contras
2. Opção B
   - Prós
   - Contras

### Consequências
**Positivas:**
- Item

**Negativas:**
- Item

**Neutras:**
- Item

### Implementação
Como será implementado?

### Quando Reavaliar
Em que condições revisitar esta decisão?
```

---

## 📊 Estatísticas

**Total de ADRs:** 5
**Aceitos:** 4
**Propostos:** 1
**Rejeitados:** 0
**Obsoletos:** 0

---

**Última atualização:** 2025-11-17
**Próxima revisão:** Sempre que nova decisão arquitetural for tomada
