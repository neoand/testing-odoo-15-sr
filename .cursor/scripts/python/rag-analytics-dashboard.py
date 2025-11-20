#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: rag-analytics-dashboard.py
Description: Dashboard analítico do RAG com métricas de uso e sugestões de melhoria
Usage: python3 rag-analytics-dashboard.py
Author: Claude + Anderson
Created: 2025-11-18
"""

import sys
from pathlib import Path

# Import logger
sys.path.insert(0, str(Path(__file__).parent))
from rag_query_logger import (
    generate_analytics,
    suggest_documentation,
    get_query_stats,
    get_feedback_stats
)

# Cores
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
CYAN = '\033[0;36m'
MAGENTA = '\033[0;35m'
RED = '\033[0;31m'
NC = '\033[0m'

def print_dashboard():
    """Imprime dashboard analytics completo"""

    print(f"{BLUE}{'='*70}{NC}")
    print(f"{BLUE}📊 RAG ANALYTICS DASHBOARD{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")

    # Gerar analytics
    analytics = generate_analytics()
    query_stats = analytics['query_stats']
    feedback_stats = analytics['feedback_stats']

    # ====== MÉTRICAS GERAIS ======
    print(f"{CYAN}📈 MÉTRICAS GERAIS{NC}")
    print(f"{'-'*70}")
    print(f"  Total de queries: {YELLOW}{query_stats['total_queries']}{NC}")
    print(f"  Média de resultados: {YELLOW}{query_stats['avg_results']:.2f}{NC}")
    print(f"  Queries sem resultado: {YELLOW}{len(query_stats['zero_results_queries'])}{NC}")

    if feedback_stats['total_feedback'] > 0:
        print(f"  Feedback total: {YELLOW}{feedback_stats['total_feedback']}{NC}")
        print(f"  Taxa de relevância: {GREEN}{feedback_stats['relevance_rate']:.1f}%{NC}")
    print()

    # ====== TOP QUERIES ======
    if query_stats['top_queries']:
        print(f"{CYAN}🔥 TOP QUERIES (Mais Frequentes){NC}")
        print(f"{'-'*70}")
        for i, (query, count) in enumerate(list(query_stats['top_queries'].items())[:10], 1):
            print(f"  {i}. {YELLOW}({count}x){NC} {query}")
        print()

    # ====== QUERIES SEM RESULTADO ======
    if query_stats['zero_results_queries']:
        print(f"{RED}⚠️  QUERIES SEM RESULTADO (Últimas 5){NC}")
        print(f"{'-'*70}")
        for i, q in enumerate(query_stats['zero_results_queries'][-5:], 1):
            print(f"  {i}. {q['query']}")
            print(f"     {CYAN}Timestamp:{NC} {q['timestamp']}")
        print()

    # ====== QUERIES POR DATA ======
    if query_stats['queries_by_date']:
        print(f"{CYAN}📅 QUERIES POR DATA{NC}")
        print(f"{'-'*70}")
        for date, count in sorted(query_stats['queries_by_date'].items(), reverse=True)[:7]:
            bar = '█' * min(count, 50)
            print(f"  {date}: {YELLOW}{bar}{NC} ({count})")
        print()

    # ====== SUGESTÕES DE DOCUMENTAÇÃO ======
    suggestions = suggest_documentation()
    if suggestions:
        print(f"{MAGENTA}💡 SUGESTÕES DE DOCUMENTAÇÃO{NC}")
        print(f"{'-'*70}")
        print(f"  {YELLOW}Encontramos {len(suggestions)} queries sem resultado!{NC}")
        print(f"  {CYAN}Considere documentar sobre:{NC}\n")
        for i, s in enumerate(suggestions[:5], 1):
            print(f"  {i}. \"{s['query']}\"")
            print(f"     {CYAN}→{NC} Sugerido: {s['file']}\n")

    # ====== INSIGHTS & RECOMENDAÇÕES ======
    print(f"{GREEN}🎯 INSIGHTS & RECOMENDAÇÕES{NC}")
    print(f"{'-'*70}")

    # Taxa de zero results
    zero_rate = len(query_stats['zero_results_queries']) / query_stats['total_queries'] * 100 if query_stats['total_queries'] > 0 else 0

    if zero_rate > 20:
        print(f"  {RED}⚠️{NC}  Taxa de queries sem resultado: {RED}{zero_rate:.1f}%{NC}")
        print(f"      {CYAN}→{NC} Considere expandir documentação!")
    elif zero_rate > 10:
        print(f"  {YELLOW}⚠️{NC}  Taxa de queries sem resultado: {YELLOW}{zero_rate:.1f}%{NC}")
        print(f"      {CYAN}→{NC} Algumas áreas precisam documentação")
    else:
        print(f"  {GREEN}✅{NC} Taxa de queries sem resultado: {GREEN}{zero_rate:.1f}%{NC}")
        print(f"      {CYAN}→{NC} Documentação está cobrindo bem as queries!")

    # Taxa de relevância
    if feedback_stats['total_feedback'] > 0:
        rel_rate = feedback_stats['relevance_rate']
        if rel_rate >= 90:
            print(f"  {GREEN}✅{NC} Taxa de relevância: {GREEN}{rel_rate:.1f}%{NC}")
            print(f"      {CYAN}→{NC} RAG está performando excelentemente!")
        elif rel_rate >= 75:
            print(f"  {YELLOW}⚠️{NC}  Taxa de relevância: {YELLOW}{rel_rate:.1f}%{NC}")
            print(f"      {CYAN}→{NC} Considere ajustar reranking ou embeddings")
        else:
            print(f"  {RED}⚠️{NC}  Taxa de relevância: {RED}{rel_rate:.1f}%{NC}")
            print(f"      {CYAN}→{NC} RAG precisa de ajustes urgentes!")

    # Queries mais frequentes
    if query_stats['top_queries']:
        top_query, top_count = list(query_stats['top_queries'].items())[0]
        if top_count >= 5:
            print(f"  {CYAN}💡{NC} Query mais frequente: \"{top_query}\" ({top_count}x)")
            print(f"      {CYAN}→{NC} Considere criar atalho ou documentação dedicada!")

    print()

    # ====== AÇÕES SUGERIDAS ======
    print(f"{YELLOW}🚀 AÇÕES SUGERIDAS{NC}")
    print(f"{'-'*70}")

    actions = []

    if suggestions:
        actions.append(f"Documentar {len(suggestions)} tópicos sem cobertura")

    if zero_rate > 15:
        actions.append("Expandir documentação em áreas com zero results")

    if feedback_stats['total_feedback'] > 0 and feedback_stats['relevance_rate'] < 80:
        actions.append("Revisar e melhorar embeddings ou reranking")

    if query_stats['top_queries'] and list(query_stats['top_queries'].values())[0] >= 5:
        actions.append("Criar documentação dedicada para queries frequentes")

    if actions:
        for i, action in enumerate(actions, 1):
            print(f"  {i}. {action}")
    else:
        print(f"  {GREEN}✅ Nenhuma ação urgente necessária!{NC}")

    print()
    print(f"{BLUE}{'='*70}{NC}\n")

    # ====== EXPORT INFO ======
    print(f"{CYAN}💾 Analytics salvo em:{NC} .claude/logs/rag-analytics.json")
    print(f"{CYAN}📝 Query log:{NC} .claude/logs/rag-queries.jsonl")
    print(f"{CYAN}📊 Feedback log:{NC} .claude/logs/rag-feedback.jsonl\n")

if __name__ == "__main__":
    print_dashboard()
