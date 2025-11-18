#!/bin/bash
# Script: pre-compact-save-context.sh
# Description: Salva snapshot do contexto crítico ANTES de auto-compact
# Usage: Executado automaticamente pelo PreCompact hook
# Author: Claude
# Created: 2025-11-17
# ADR: ADR-008 (Sistema Avançado de Gestão de Contexto)

set -e  # Exit on error

# ================================
# Configuration
# ================================

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SNAPSHOT_DIR="$PROJECT_ROOT/.claude/memory/context-snapshots"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SNAPSHOT_FILE="$SNAPSHOT_DIR/context-snapshot-$TIMESTAMP.md"

# ================================
# Create Snapshot Directory
# ================================

mkdir -p "$SNAPSHOT_DIR"

# ================================
# Save Context Snapshot
# ================================

cat > "$SNAPSHOT_FILE" << EOF
# 📸 Context Snapshot - Auto-Compact

**Criado em:** $(date '+%Y-%m-%d %H:%M:%S')
**Razão:** Auto-compact atingiu 95% da capacidade
**Objetivo:** Restaurar contexto crítico pós-compactação

---

## 📐 Últimos ADRs (Top 20)

$(tail -20 "$PROJECT_ROOT/.claude/memory/decisions/ADR-INDEX.md" 2>/dev/null || echo "Nenhum ADR encontrado")

---

## 📊 ADR-008: Recursos Revolucionários

**Status Sprint 1:**
- ✅ PreCompact Hook implementado (este script!)
- ✅ SessionStart Hook configurado
- ✅ UserPromptSubmit Hook configurado

**Próximos Sprints:**
- Sprint 2: Output Styles (odoo-expert, performance-guru, architect)
- Sprint 3: @imports para CLAUDE.md modular

---

## 🔄 Git Status e Commits Recentes

### Branch Atual
$(git branch --show-current 2>/dev/null || echo "Git não inicializado")

### Últimos 10 Commits
$(git log --oneline -10 2>/dev/null || echo "Nenhum commit encontrado")

### Status do Working Directory
$(git status --short 2>/dev/null || echo "Nenhuma mudança")

---

## 📝 TODOs Ativos

### Em .claude/memory/
$(grep -r "TODO\|FIXME\|XXX" "$PROJECT_ROOT/.claude/memory/" 2>/dev/null | head -20 || echo "Nenhum TODO encontrado")

### Em código Python (addons)
$(find "$PROJECT_ROOT/addons" -name "*.py" -type f -exec grep -l "TODO\|FIXME" {} \; 2>/dev/null | head -10 || echo "Nenhum TODO em código")

---

## 🔄 Última Sincronização Template

$(tail -30 "$PROJECT_ROOT/.claude/memory/learnings/sync-log.md" 2>/dev/null || echo "Nenhuma sincronização registrada")

---

## 🐍 Contexto Odoo (Específico do Projeto)

### Servidores Ativos
- odoo-sr-testing (porta 8073)
- odoo-rc (porta 8072)

### Últimos Módulos Modificados
$(git log --name-only --oneline -5 -- addons/ 2>/dev/null | grep "addons/" | sort | uniq | head -10 || echo "Nenhum módulo modificado recentemente")

---

## ⚡ Performance Settings (ADR-007)

**Lembrete:** Claude Max 20x - SEMPRE paralelizar!
- Tool calls independentes → UMA mensagem
- Bash commands independentes → & e wait
- Commits em múltiplos repos → paralelo

---

## 🎯 Regras Críticas

**ADR-006 (Sincronização Dual):**
- TUDO genérico → testing-odoo-15-sr + Claude-especial
- Específico Odoo → apenas testing-odoo-15-sr

**ADR-007 (Performance):**
- Checklist SEMPRE: posso paralelizar?

**ADR-008 (Este!):**
- Hooks garantem ZERO perda de contexto!

---

## 📍 Estado do Projeto

**Projeto:** testing-odoo-15-sr
**Template:** Claude-especial
**GitHub:** https://github.com/neoand/testing-odoo-15-sr
**Git Workflow:** Anti-rebase (merge sempre)

---

**Snapshot salvo em:** $SNAPSHOT_FILE
**Próximo passo:** SessionStart hook irá ler este arquivo automaticamente

EOF

# ================================
# Cleanup Old Snapshots
# ================================

# Manter apenas os últimos 10 snapshots
SNAPSHOT_COUNT=$(ls -1 "$SNAPSHOT_DIR"/context-snapshot-*.md 2>/dev/null | wc -l | tr -d ' ')

if [ "$SNAPSHOT_COUNT" -gt 10 ]; then
    # Remove os mais antigos
    ls -1t "$SNAPSHOT_DIR"/context-snapshot-*.md | tail -n +11 | xargs rm -f
    echo "🧹 Limpeza: Removidos $(($SNAPSHOT_COUNT - 10)) snapshots antigos"
fi

# ================================
# Output
# ================================

echo "✅ Context snapshot saved successfully!"
echo "📁 Location: $SNAPSHOT_FILE"
echo "📊 Snapshot size: $(wc -l < "$SNAPSHOT_FILE") lines"
echo "💾 Total snapshots: $(ls -1 "$SNAPSHOT_DIR"/context-snapshot-*.md 2>/dev/null | wc -l | tr -d ' ')"
echo ""
echo "🔄 Claude will auto-restore this context after compact via SessionStart hook!"
