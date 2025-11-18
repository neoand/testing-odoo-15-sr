#!/bin/bash
# Hook: enforce-protocol-completion.sh
# Versão: 2.0 - Intelligent Multi-Agent Parallel Execution
# Description: Detecta "PROTOCOLO" (case-insensitive) e força execução inteligente
# Author: Claude + Anderson
# Created: 2025-11-18

USER_MESSAGE="$1"

# Detectar "PROTOCOLO" ou "protocolo" (case-insensitive)
if echo "$USER_MESSAGE" | grep -qi "protocolo"; then

    echo "🔥 ========================================" >&2
    echo "🔥 PROTOCOLO V2.0 ATIVADO" >&2
    echo "🔥 Intelligent Multi-Agent Execution" >&2
    echo "🔥 ========================================" >&2
    echo "" >&2

    echo "📋 FASE 1: ANÁLISE INTELIGENTE (Obrigatória)" >&2
    echo "  [ ] 1. Ativar <thinking> mode para análise profunda" >&2
    echo "  [ ] 2. Analisar request: o que foi pedido exatamente?" >&2
    echo "  [ ] 3. Identificar sub-tarefas e dependências" >&2
    echo "  [ ] 4. Determinar paralelização possível" >&2
    echo "" >&2

    echo "📋 FASE 2: CONSULTA DE CONTEXTO AUTOMÁTICA (RAG + Session Memory)" >&2
    echo "  [ ] 5. 🧠 RAG AUTO-LEARNING: Buscar conhecimento pertinente" >&2
    echo "      python3.11 .claude/scripts/python/rag_auto_learning.py --search 'KEYWORDS_DA_TAREFA'" >&2
    echo "  [ ] 6. 🧠 SESSION MEMORY: Verificar sessões anteriores similares" >&2
    echo "      python3.11 .claude/scripts/python/session-memory.py test" >&2
    echo "  [ ] 7. 🌐 Se necessário: Web Search para conhecimento atualizado" >&2
    echo "  [ ] 8. 🎯 Reranking e síntese do contexto obtido" >&2
    echo "" >&2

    echo "📋 FASE 3: EXECUÇÃO MULTI-AGENTE (Paralela)" >&2
    echo "  [ ] 9. Lançar múltiplos agentes/skills em PARALELO" >&2
    echo "  [ ] 10. Usar Task tool para tarefas complexas" >&2
    echo "  [ ] 11. Maximizar uso de multi-tool calls em UMA mensagem" >&2
    echo "  [ ] 12. Bash paralelo (&& wait) para comandos independentes" >&2
    echo "" >&2

    echo "📋 FASE 4: DOCUMENTAÇÃO COMPLETA (Obrigatória)" >&2
    echo "  [ ] 13. ERRORS-SOLVED.md (se erros resolvidos)" >&2
    echo "  [ ] 14. COMMAND-HISTORY.md (comandos novos)" >&2
    echo "  [ ] 15. PATTERNS.md (patterns descobertos)" >&2
    echo "  [ ] 16. learnings/ (aprendizados profundos)" >&2
    echo "  [ ] 17. ADR (se decisão arquitetural)" >&2
    echo "  [ ] 18. Atualizar RAG (reindexar se necessário)" >&2
    echo "" >&2

    echo "📋 FASE 5: PERSISTÊNCIA (Obrigatória)" >&2
    echo "  [ ] 19. Verificar tool-inventory antes de criar scripts" >&2
    echo "  [ ] 20. Git commit local (mensagem detalhada)" >&2
    echo "  [ ] 21. Sincronizar com Claude-especial (se genérico)" >&2
    echo "  [ ] 22. Push para GitHub (ambos repos)" >&2
    echo "" >&2

    echo "📋 FASE 6: VALIDAÇÃO FINAL + AUTO-LEARNING (Obrigatória)" >&2
    echo "  [ ] 23. Revisar: TODAS as tarefas completadas?" >&2
    echo "  [ ] 24. Testar: Funciona corretamente?" >&2
    echo "  [ ] 25. Documentar: Tudo está salvo?" >&2
    echo "  [ ] 26. 🧠 RAG UPDATE: Extrair conhecimento e atualizar automaticamente" >&2
    echo "      python3.11 .claude/scripts/python/rag_auto_learning.py --scan" >&2
    echo "  [ ] 27. 🧠 SESSION SAVE: Salvar sessão completa com aprendizados" >&2
    echo "      python3.11 .claude/scripts/python/rag_auto_learning.py --save-session 'RESUMO_DA_SESSAO'" >&2
    echo "  [ ] 28. 📊 RAG STATS: Verificar crescimento do conhecimento" >&2
    echo "      python3.11 .claude/scripts/python/rag_auto_learning.py --stats" >&2
    echo "" >&2

    echo "⚡ REGRAS DE PARALELIZAÇÃO:" >&2
    echo "  1. Tool calls independentes → UMA mensagem" >&2
    echo "  2. Bash commands independentes → & wait" >&2
    echo "  3. Agentes complexos → Task tool paralelo" >&2
    echo "  4. RAG + Web Search → Paralelo sempre que possível" >&2
    echo "" >&2

    echo "🧠 RAG AUTO-LEARNING INTEGRADO:" >&2
    echo "  • Claude DEVE consultar RAG no início (FASE 2)" >&2
    echo "  • Claude DEVE atualizar RAG no final (FASE 6)" >&2
    echo "  • Conhecimento é extraído e indexado automaticamente" >&2
    echo "  • Session memory integra com RAG para continuidade" >&2
    echo "  • Claude fica mais inteligente a CADA PROTOCOLO!" >&2
    echo "  • Comandos, erros, patterns e soluções são aprendidos automaticamente" >&2
    echo "" >&2

    echo "🔴 BLOQUEIO ATIVO: Exit Code 2" >&2
    echo "Claude NÃO PODE terminar até completar TODAS as fases!" >&2
    echo "" >&2

    # Exit code 2 = BLOQUEIA stoppage
    exit 2
fi

# Se não detectou PROTOCOLO, libera normalmente
exit 0
