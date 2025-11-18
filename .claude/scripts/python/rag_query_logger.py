#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: rag-query-logger.py
Description: Logger de queries RAG com feedback loop para aprendizado contínuo
Usage: Usado automaticamente por search_knowledge()
Author: Claude + Anderson
Created: 2025-11-18
"""

import json
import os
from datetime import datetime
from pathlib import Path
import hashlib

# ====== CONFIGURAÇÃO ======
# Determine project root
# This script is at: PROJECT_ROOT/.claude/scripts/python/rag_query_logger.py
script_path = Path(__file__).resolve()
PROJECT_ROOT = script_path.parent.parent.parent.parent  # .claude/scripts/python/rag_query_logger.py -> PROJECT_ROOT
QUERY_LOG_PATH = str(PROJECT_ROOT / ".claude" / "logs" / "rag-queries.jsonl")  # JSONL = JSON Lines
FEEDBACK_LOG_PATH = str(PROJECT_ROOT / ".claude" / "logs" / "rag-feedback.jsonl")
ANALYTICS_PATH = str(PROJECT_ROOT / ".claude" / "logs" / "rag-analytics.json")

# ====== LOGGER ======

def log_query(query, results, metadata=None):
    """
    Registra query RAG com resultados

    Args:
        query: Query do usuário
        results: Resultados retornados
        metadata: Metadata adicional (device, timing, etc)

    Returns:
        query_id: ID único da query
    """
    # Criar diretório se não existe
    os.makedirs(os.path.dirname(QUERY_LOG_PATH), exist_ok=True)

    # Gerar ID único
    query_id = hashlib.md5(
        f"{query}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:12]

    # Preparar log entry
    log_entry = {
        "query_id": query_id,
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "results_count": len(results) if results else 0,
        "top_result": results[0] if results else None,
        "metadata": metadata or {}
    }

    # Append to JSONL file (cada linha = 1 JSON)
    with open(QUERY_LOG_PATH, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

    return query_id

def log_feedback(query_id, relevant=True, notes=""):
    """
    Registra feedback sobre relevância dos resultados

    Args:
        query_id: ID da query
        relevant: True se resultados foram relevantes
        notes: Notas adicionais
    """
    os.makedirs(os.path.dirname(FEEDBACK_LOG_PATH), exist_ok=True)

    feedback_entry = {
        "query_id": query_id,
        "timestamp": datetime.now().isoformat(),
        "relevant": relevant,
        "notes": notes
    }

    with open(FEEDBACK_LOG_PATH, 'a') as f:
        f.write(json.dumps(feedback_entry) + '\n')

def get_query_stats():
    """Retorna estatísticas agregadas de queries"""

    if not os.path.exists(QUERY_LOG_PATH):
        return {"total_queries": 0}

    stats = {
        "total_queries": 0,
        "queries_by_date": {},
        "top_queries": {},
        "avg_results": 0,
        "zero_results_queries": []
    }

    total_results = 0

    with open(QUERY_LOG_PATH, 'r') as f:
        for line in f:
            entry = json.loads(line.strip())
            stats["total_queries"] += 1

            # Queries por data
            date = entry["timestamp"][:10]
            stats["queries_by_date"][date] = stats["queries_by_date"].get(date, 0) + 1

            # Top queries (frequência)
            query = entry["query"].lower()
            stats["top_queries"][query] = stats["top_queries"].get(query, 0) + 1

            # Avg results
            total_results += entry.get("results_count", 0)

            # Zero results
            if entry.get("results_count", 0) == 0:
                stats["zero_results_queries"].append({
                    "query": entry["query"],
                    "timestamp": entry["timestamp"]
                })

    stats["avg_results"] = total_results / stats["total_queries"] if stats["total_queries"] > 0 else 0

    # Top 10 queries mais frequentes
    stats["top_queries"] = dict(
        sorted(stats["top_queries"].items(), key=lambda x: x[1], reverse=True)[:10]
    )

    return stats

def get_feedback_stats():
    """Retorna estatísticas de feedback"""

    if not os.path.exists(FEEDBACK_LOG_PATH):
        return {"total_feedback": 0}

    stats = {
        "total_feedback": 0,
        "relevant_count": 0,
        "irrelevant_count": 0,
        "relevance_rate": 0.0
    }

    with open(FEEDBACK_LOG_PATH, 'r') as f:
        for line in f:
            entry = json.loads(line.strip())
            stats["total_feedback"] += 1

            if entry.get("relevant", True):
                stats["relevant_count"] += 1
            else:
                stats["irrelevant_count"] += 1

    if stats["total_feedback"] > 0:
        stats["relevance_rate"] = stats["relevant_count"] / stats["total_feedback"] * 100

    return stats

def generate_analytics():
    """Gera analytics completo e salva em JSON"""

    analytics = {
        "generated_at": datetime.now().isoformat(),
        "query_stats": get_query_stats(),
        "feedback_stats": get_feedback_stats()
    }

    # Salvar analytics
    os.makedirs(os.path.dirname(ANALYTICS_PATH), exist_ok=True)
    with open(ANALYTICS_PATH, 'w') as f:
        json.dump(analytics, f, indent=2)

    return analytics

def suggest_documentation():
    """
    Analisa queries sem resultados e sugere documentação

    Returns:
        List de sugestões de documentação
    """
    stats = get_query_stats()
    suggestions = []

    for zero_result in stats.get("zero_results_queries", []):
        suggestions.append({
            "query": zero_result["query"],
            "timestamp": zero_result["timestamp"],
            "suggestion": f"Considere documentar sobre: {zero_result['query']}",
            "file": "PATTERNS.md ou learnings/ apropriado"
        })

    return suggestions

# ====== MAIN (para teste) ======

if __name__ == "__main__":
    # Gerar analytics
    analytics = generate_analytics()

    print("📊 RAG Analytics")
    print("=" * 60)
    print(f"Total de queries: {analytics['query_stats']['total_queries']}")
    print(f"Média de resultados: {analytics['query_stats']['avg_results']:.2f}")
    print(f"Queries sem resultado: {len(analytics['query_stats']['zero_results_queries'])}")

    if analytics['feedback_stats']['total_feedback'] > 0:
        print(f"\nFeedback total: {analytics['feedback_stats']['total_feedback']}")
        print(f"Taxa de relevância: {analytics['feedback_stats']['relevance_rate']:.1f}%")

    # Top queries
    if analytics['query_stats']['top_queries']:
        print("\nTop Queries:")
        for query, count in list(analytics['query_stats']['top_queries'].items())[:5]:
            print(f"  {count}x: {query}")

    # Sugestões de documentação
    suggestions = suggest_documentation()
    if suggestions:
        print(f"\n💡 Sugestões de documentação ({len(suggestions)}):")
        for s in suggestions[:3]:
            print(f"  • {s['query']}")
