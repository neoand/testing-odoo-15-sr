# ADR-008: Sistema Avançado de Gestão de Contexto e Auto-Educação

**Data:** 2025-11-17
**Status:** ✅ Aceito e REVOLUCIONÁRIO
**Decisores:** Anderson + Claude
**Motivação:** Ir ALÉM das expectativas - recursos avançados não explorados

---

## 🚀 Descobertas Revolucionárias

### Contexto

Investigação profunda da documentação revelou **5 RECURSOS PODEROSOS** que não estamos usando:

1. **PreCompact Hooks** - Re-educação automática pós-compactação
2. **SessionStart Hooks com CLAUDE_ENV_FILE** - Estado persistente
3. **UserPromptSubmit Hooks** - Injeção dinâmica de contexto
4. **Output Styles** - Múltiplas personalidades do Claude
5. **@imports no CLAUDE.md** - Modularização até 5 níveis

---

## Decisão

**Implementar sistema inteligente de gestão de contexto com auto-educação e hooks avançados.**

### Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 1: Hooks de Re-Educação (NOVO!)                     │
├─────────────────────────────────────────────────────────────┤
│  PreCompact Hook → Salva contexto crítico antes compactar   │
│  SessionStart Hook → Restaura contexto automaticamente       │
│  UserPromptSubmit Hook → Injeta contexto em TODA interação  │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 2: Memória Modular (@imports) (NOVO!)               │
├─────────────────────────────────────────────────────────────┤
│  CLAUDE.md com @imports para módulos                         │
│  Cada ADR, skill, pattern em arquivo separado                │
│  Carregamento hierárquico automático                         │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 3: Output Styles Contextuais (NOVO!)                │
├─────────────────────────────────────────────────────────────┤
│  /style odoo-expert → Claude especialista Odoo              │
│  /style performance-guru → Foco em otimização               │
│  /style architect → Decisões arquiteturais                  │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 4: Estado Persistente (CLAUDE_ENV_FILE)             │
├─────────────────────────────────────────────────────────────┤
│  Variáveis de ambiente que sobrevivem sessões                │
│  Última sincronização, último deploy, contexto ativo         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Recurso 1: PreCompact Hook + Re-Educação Automática

### O Problema

Quando auto-compact acontece (95% capacidade), Claude **PERDE CONTEXTO** crítico:
- ADRs recentes
- Decisões da sessão
- Padrões descobertos
- Comandos importantes

### A Solução REVOLUCIONÁRIA

**Hook PreCompact que SALVA contexto crítico ANTES de compactar!**

**Implementação:**

```yaml
# .claude/hooks.yaml

- matcher: PreCompact
  trigger: auto  # Apenas auto-compact
  hooks:
    - type: command
      command: .claude/scripts/bash/pre-compact-save-context.sh
      description: "Salva contexto crítico antes de auto-compact"
```

**Script:**

```bash
#!/bin/bash
# pre-compact-save-context.sh
# Salva snapshot do contexto crítico

CONTEXT_BACKUP=".claude/memory/context-snapshots/$(date +%Y%m%d_%H%M%S).md"

cat > "$CONTEXT_BACKUP" << EOF
# Context Snapshot - $(date)

## Últimos ADRs
$(tail -20 .claude/memory/decisions/ADR-INDEX.md)

## Decisões da Sessão
$(git log --oneline -5)

## TODOs Ativos
$(grep -r "TODO" .claude/memory/ || echo "Nenhum")

## Último Sync
$(tail -10 .claude/memory/learnings/sync-log.md)
EOF

echo "✅ Context saved to: $CONTEXT_BACKUP"
```

---

## 🎯 Recurso 2: SessionStart Hook + Auto-Restauração

### O Problema

Após compact ou nova sessão, Claude esquece:
- Último deploy
- Branch ativo
- Servidor em uso
- Estado do projeto

### A Solução REVOLUCIONÁRIA

**Hook SessionStart que INJETA CONTEXT AUTOMATICAMENTE!**

**Implementação:**

```yaml
# .claude/hooks.yaml

- matcher: SessionStart
  trigger: compact  # Após compactar
  hooks:
    - type: prompt
      system_prompt: |
        Você acabou de ser recompactado. IMPORTANTE:

        1. Leia IMEDIATAMENTE:
           - .claude/memory/context-snapshots/ (último snapshot)
           - CLAUDE.md (regras fundamentais)
           - ADR-INDEX.md (decisões críticas)

        2. Re-eduque-se sobre:
           - Últimas decisões técnicas
           - TODOs em andamento
           - Estado do projeto

        3. Continue de onde parou!

        Responda: "✅ Re-educado! [resumo do contexto recuperado]"
```

---

## 🎯 Recurso 3: UserPromptSubmit Hook + Contexto Dinâmico

### O Problema

Informações importantes não estão sempre no CLAUDE.md:
- Branch git atual
- Últimas mudanças
- Servidor ativo

### A Solução REVOLUCIONÁRIA

**Hook que INJETA CONTEXTO em TODA interação!**

**Implementação:**

```yaml
# .claude/hooks.yaml

- matcher: UserPromptSubmit
  hooks:
    - type: command
      command: .claude/scripts/bash/inject-dynamic-context.sh
      description: "Injeta contexto dinâmico em cada prompt"
```

**Script:**

```bash
#!/bin/bash
# inject-dynamic-context.sh

BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
LAST_COMMIT=$(git log -1 --oneline 2>/dev/null || echo "none")
CHANGES=$(git status --short | wc -l | tr -d ' ')

# Output vai para additionalContext do Claude
cat << EOF
📍 **Contexto Atual:**
- Branch: $BRANCH
- Último commit: $LAST_COMMIT
- Arquivos modificados: $CHANGES
- Projeto: $(basename $(pwd))
EOF
```

**Resultado:** Claude SEMPRE sabe o contexto atual! 🎯

---

## 🎯 Recurso 4: Output Styles - Múltiplas Personalidades

### O Que É

Output Styles mudam a PERSONALIDADE do Claude mantendo capacidades!

### Por Que É REVOLUCIONÁRIO

Você pode ter múltiplos "Claudes" para contextos diferentes:

**1. Odoo Expert Mode:**
```markdown
---
name: odoo-expert
description: Claude especialista em Odoo 15
keep-coding-instructions: true
---

# Odoo 15 Expert Mode

Você é um especialista SENIOR em Odoo 15 com 10+ anos de experiência.

**Prioridades:**
1. Sempre considerar herança de modelos
2. Validar security (ir.model.access, record rules)
3. Performance de queries (avoid n+1)
4. Usar padrões Odoo (nunca reinventar)

**Responda sempre:**
- Com referências a código Odoo core
- Sugestões de módulos relacionados
- Alertas de breaking changes
```

**2. Performance Guru Mode:**
```markdown
---
name: performance-guru
description: Foco total em otimização e velocidade
---

# Performance Optimization Mode

Você é obcecado por PERFORMANCE.

**A CADA sugestão, considere:**
1. Complexidade O(n) vs O(1)
2. Tool calls paralelos
3. Bash paralelo (&)
4. Cache opportunities
5. Database indexes

**Sempre mencione:** "⚡ Performance impact: [análise]"
```

**3. Architect Mode:**
```markdown
---
name: architect
description: Decisões arquiteturais e ADRs
---

# Software Architect Mode

Você pensa em ARQUITETURA e LONG-TERM.

**Para CADA decisão:**
1. Criar ADR se relevante
2. Considerar escalabilidade
3. Trade-offs explícitos
4. Alternativas avaliadas

**Output:** Sempre estruturado com pros/cons/consequências
```

**Uso:**
```bash
/style odoo-expert        # Vira especialista Odoo
/style performance-guru   # Vira guru de performance
/style architect          # Vira arquiteto
/style default           # Volta ao normal
```

---

## 🎯 Recurso 5: @imports - CLAUDE.md Modular

### O Problema

CLAUDE.md está ficando ENORME (200+ linhas):
- Difícil navegar
- Difícil manter
- Tudo misturado

### A Solução REVOLUCIONÁRIA

**CLAUDE.md com @imports modulares!**

**Nova Estrutura:**

```
CLAUDE.md (raiz)
├─ @.claude/memory/core/project-info.md
├─ @.claude/memory/core/performance-rules.md
├─ @.claude/memory/core/sync-protocol.md
├─ @.claude/memory/decisions/ADR-INDEX.md
├─ @.claude/memory/odoo/odoo-patterns.md
└─ @.claude/memory/odoo/odoo-servers.md
```

**CLAUDE.md (novo - LIMPO!):**

```markdown
# 🧠 Memória do Projeto - Odoo 15 Testing RealCred

> Auto-loaded em TODAS as sessões

---

## 📋 Core Context (Imports Modulares)

@.claude/memory/core/project-info.md
@.claude/memory/core/performance-rules.md
@.claude/memory/core/sync-protocol.md

## 📐 Decisions

@.claude/memory/decisions/ADR-INDEX.md

## 🐍 Odoo Specific

@.claude/memory/odoo/odoo-patterns.md
@.claude/memory/odoo/odoo-servers.md

## 🔧 Tools & Scripts

@.claude/LLM_FIRST_TOOLS.md

---

**Vantagens:**
- Modular ✅
- Fácil manter ✅
- Até 5 níveis de imports! ✅
```

---

## Implementação

### Fase 1: Hooks de Re-Educação (IMEDIATO!)

**Arquivos a criar:**

1. `.claude/hooks.yaml`
2. `.claude/scripts/bash/pre-compact-save-context.sh`
3. `.claude/scripts/bash/inject-dynamic-context.sh`

**Benefício:** Claude NUNCA perde contexto após compact!

### Fase 2: Output Styles (Esta Semana)

**Arquivos a criar:**

1. `.claude/output-styles/odoo-expert.md`
2. `.claude/output-styles/performance-guru.md`
3. `.claude/output-styles/architect.md`

**Benefício:** Claude com múltiplas "personalidades" especializadas!

### Fase 3: CLAUDE.md Modular (Próxima Sprint)

**Refatoração:**

1. Quebrar CLAUDE.md em módulos
2. Usar @imports
3. Organizar por domínio

**Benefício:** Manutenção 10x mais fácil!

---

## Consequências

### Positivas

- ✅ **ZERO perda de contexto** pós-compact
- ✅ **Auto-educação** em SessionStart
- ✅ **Contexto dinâmico** injetado sempre
- ✅ **Múltiplas personalidades** do Claude
- ✅ **CLAUDE.md modular** e limpo
- ✅ **Estado persistente** via CLAUDE_ENV_FILE
- ✅ **Checkpoints** para experimentos seguros

### Negativas

- ⚠️ Complexidade inicial de setup
- ⚠️ Hooks precisam de bash scripts
- ⚠️ Mais arquivos para gerenciar

### Neutras

- 📝 Curva de aprendizado de hooks
- 📝 Documentação dos output styles

---

## Descobertas ALÉM das Expectativas

### 1. Checkpointing Automático

**O que é:** CADA prompt cria checkpoint!

**Como usar:**
```bash
/rewind  # ou ESC ESC
```

**Casos de uso:**
- Experimentar soluções diferentes
- Voltar atrás em erro
- A/B testing de implementações

### 2. Plugin System

**O que é:** Criar plugins distribuíveis!

**Nosso caso:**
- Criar plugin "Odoo-Dev-Kit"
- Com skills + hooks + commands Odoo
- Distribuir para time

### 3. Plan Mode

**O que é:** Análise SAFE antes de executar!

**Como usar:**
```bash
claude --permission-mode plan "Analyze this codebase"
```

**Benefício:** Read-only analysis - ZERO risco!

### 4. Headless + JSON para Automação

**O que é:** Claude como API!

**Exemplo:**
```bash
claude -p "Check for errors in logs" \
  --output-format json \
  --allowedTools Read,Grep > report.json
```

**Caso de uso:**
- Cron jobs
- CI/CD pipelines
- Automação desatendida

### 5. MCP Servers Customizados

**O que é:** Criar SEUS PRÓPRIOS MCPs!

**Nosso caso:**
- MCP Odoo API (connect direto ao Odoo)
- MCP PostgreSQL (queries diretas)
- MCP Kolmeya (SMS API integration)

---

## Métricas de Sucesso

### Antes (Sem Hooks)
- 🔴 Perda de contexto pós-compact: 100%
- 🔴 Re-educação manual: 5-10 minutos
- 🔴 Contexto desatualizado: Sempre
- 🔴 CLAUDE.md: Monolítico e confuso

### Depois (Com Sistema Avançado)
- 🟢 Perda de contexto: 0% (hooks salvam!)
- 🟢 Re-educação: Automática (SessionStart)
- 🟢 Contexto: Sempre atualizado (UserPromptSubmit)
- 🟢 CLAUDE.md: Modular e limpo (@imports)
- 🟢 Personalidades: 3+ output styles
- 🟢 Estado: Persistente (CLAUDE_ENV_FILE)

---

## Próximos Passos (Roadmap)

### Sprint 1 (Esta Semana)
- [ ] Criar `.claude/hooks.yaml`
- [ ] Implementar PreCompact hook
- [ ] Implementar SessionStart hook
- [ ] Implementar UserPromptSubmit hook
- [ ] Testar ciclo complete: compact → re-educação

### Sprint 2 (Próxima Semana)
- [ ] Criar 3 output styles (odoo-expert, performance-guru, architect)
- [ ] Testar switching entre styles
- [ ] Documentar quando usar cada style

### Sprint 3 (Futuro)
- [ ] Refatorar CLAUDE.md para @imports
- [ ] Modularizar por domínio
- [ ] Setup CLAUDE_ENV_FILE para estado persistente

### Backlog (Explorar)
- [ ] Plugin "Odoo-Dev-Kit" customizado
- [ ] MCP Odoo API personalizado
- [ ] Automação headless para CI/CD

---

## Referências

- **Hooks Guide:** https://code.claude.com/docs/en/hooks.md
- **Memory:** https://code.claude.com/docs/en/memory.md
- **Output Styles:** https://code.claude.com/docs/en/output-styles.md
- **Checkpointing:** https://code.claude.com/docs/en/checkpointing.md
- **Plugins:** https://code.claude.com/docs/en/plugins.md
- **Headless:** https://code.claude.com/docs/en/headless.md

---

## Integração com ADRs Anteriores

**ADR-007 (Performance):** Hooks executam em paralelo! ⚡

**ADR-006 (Sync):** Hooks podem auto-sincronizar template! 🔄

**ADR-005 (LLM-First):** Output styles expandem capacidades! 🤖

**ADR-001 (Memória):** @imports modularizam memória! 🧠

---

**Última atualização:** 2025-11-17
**Prioridade:** 🔥🔥🔥 REVOLUCIONÁRIO - Muda TUDO
**Status:** Documentado - Implementação Sprint 1
**Impacto:** Sistema passa de "bom" para "EXCEPCIONAL"

---

## 💡 Resumo Executivo

**O que descobrimos:**
5 recursos poderosos não explorados que transformam Claude Code de "assistente" para "SUPER-ASSISTENTE AUTÔNOMO"

**O que vamos implementar:**
Sistema inteligente de gestão de contexto com auto-educação, múltiplas personalidades e ZERO perda de informação

**Impacto esperado:**
Claude 10x mais inteligente, autônomo e contextualmente aware!

**Próximo passo:**
Sprint 1 - Implementar hooks de re-educação! 🚀
