#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: session-memory.py
Description: Session memory com embeddings - Claude lembra de conversas anteriores
Usage: Automático via hooks ou manual
Author: Claude + Anderson
Created: 2025-11-18
"""

import json
import os
from datetime import datetime
from pathlib import Path
import hashlib
import chromadb
from sentence_transformers import SentenceTransformer
import torch

# ====== CONFIGURAÇÃO ======
# Determine project root
script_path = Path(__file__).resolve()
PROJECT_ROOT = script_path.parent.parent.parent.parent
SESSION_LOG_PATH = str(PROJECT_ROOT / ".claude" / "logs" / "sessions.jsonl")
VECTORDB_PATH = str(PROJECT_ROOT / ".claude" / "vectordb")
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

# Device detection
if torch.backends.mps.is_available():
    device = "mps"
elif torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

# ====== INICIALIZAÇÃO ======
model = SentenceTransformer(EMBEDDING_MODEL, device=device)
client = chromadb.PersistentClient(path=VECTORDB_PATH)

# Get or create session collection
try:
    session_collection = client.get_collection("session_memory")
except:
    session_collection = client.create_collection(
        name="session_memory",
        metadata={"description": "Session summaries with embeddings"}
    )

# ====== SESSION MEMORY ======

def save_session(summary, tasks_completed, key_learnings, files_modified, metadata=None):
    """
    Salva resumo de sessão com embedding para busca futura

    Args:
        summary: Resumo da sessão
        tasks_completed: Lista de tarefas completadas
        key_learnings: Aprendizados principais
        files_modified: Arquivos modificados
        metadata: Metadata adicional

    Returns:
        session_id: ID único da sessão
    """
    # Criar diretório se não existe
    os.makedirs(os.path.dirname(SESSION_LOG_PATH), exist_ok=True)

    # Gerar ID único
    session_id = hashlib.md5(
        f"{summary}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:12]

    # Preparar conteúdo completo para embedding
    full_content = f"""
    Summary: {summary}

    Tasks Completed:
    {chr(10).join('- ' + task for task in tasks_completed)}

    Key Learnings:
    {chr(10).join('- ' + learning for learning in key_learnings)}

    Files Modified:
    {chr(10).join('- ' + file for file in files_modified)}
    """

    # Gerar embedding
    embedding = model.encode(full_content).tolist()

    # Salvar em JSONL (log permanente)
    log_entry = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "tasks_completed": tasks_completed,
        "key_learnings": key_learnings,
        "files_modified": files_modified,
        "metadata": metadata or {}
    }

    with open(SESSION_LOG_PATH, 'a') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    # Salvar embedding em ChromaDB
    session_collection.add(
        ids=[session_id],
        embeddings=[embedding],
        documents=[full_content],
        metadatas=[{
            "timestamp": log_entry["timestamp"],
            "summary": summary,
            "tasks_count": len(tasks_completed),
            "learnings_count": len(key_learnings),
            "files_count": len(files_modified)
        }]
    )

    return session_id

def search_similar_sessions(query, n_results=3):
    """
    Busca sessões similares por similaridade semântica

    Args:
        query: Descrição da tarefa atual ou contexto
        n_results: Quantas sessões retornar

    Returns:
        List de sessões similares
    """
    # Gerar embedding da query
    query_embedding = model.encode(query).tolist()

    # Buscar sessões similares
    results = session_collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    if not results['documents'][0]:
        return []

    # Preparar resultados
    sessions = []
    for doc, metadata, distance in zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ):
        sessions.append({
            'summary': metadata.get('summary', ''),
            'timestamp': metadata.get('timestamp', ''),
            'tasks_count': metadata.get('tasks_count', 0),
            'learnings_count': metadata.get('learnings_count', 0),
            'files_count': metadata.get('files_count', 0),
            'relevance_score': 1 - distance,  # Converter distância em score
            'content': doc
        })

    return sessions

def get_session_context(current_task_description):
    """
    Retorna contexto relevante de sessões anteriores

    Args:
        current_task_description: Descrição da tarefa atual

    Returns:
        String com contexto formatado para injeção
    """
    similar = search_similar_sessions(current_task_description, n_results=3)

    if not similar:
        return ""

    context = "📚 CONTEXTO DE SESSÕES ANTERIORES SIMILARES:\n\n"

    for i, session in enumerate(similar, 1):
        relevance = session['relevance_score'] * 100
        if relevance < 50:  # Filtrar resultados pouco relevantes
            continue

        context += f"Sessão #{i} (Relevância: {relevance:.1f}%)\n"
        context += f"Data: {session['timestamp'][:10]}\n"
        context += f"Resumo: {session['summary']}\n"
        context += f"Tarefas completadas: {session['tasks_count']}\n"
        context += f"Aprendizados: {session['learnings_count']}\n"
        context += "---\n\n"

    return context

def get_recent_sessions(n=5):
    """Retorna as N sessões mais recentes"""
    if not os.path.exists(SESSION_LOG_PATH):
        return []

    sessions = []
    with open(SESSION_LOG_PATH, 'r') as f:
        for line in f:
            sessions.append(json.loads(line.strip()))

    # Retornar últimas N
    return sessions[-n:]

# ====== ANALYTICS ======

def get_session_stats():
    """Retorna estatísticas de sessões"""
    if not os.path.exists(SESSION_LOG_PATH):
        return {"total_sessions": 0}

    sessions = []
    with open(SESSION_LOG_PATH, 'r') as f:
        for line in f:
            sessions.append(json.loads(line.strip()))

    total_tasks = sum(len(s.get('tasks_completed', [])) for s in sessions)
    total_learnings = sum(len(s.get('key_learnings', [])) for s in sessions)
    total_files = sum(len(s.get('files_modified', [])) for s in sessions)

    # Sessions por dia
    sessions_by_date = {}
    for session in sessions:
        date = session['timestamp'][:10]
        sessions_by_date[date] = sessions_by_date.get(date, 0) + 1

    return {
        "total_sessions": len(sessions),
        "total_tasks_completed": total_tasks,
        "total_learnings": total_learnings,
        "total_files_modified": total_files,
        "avg_tasks_per_session": total_tasks / len(sessions) if sessions else 0,
        "avg_learnings_per_session": total_learnings / len(sessions) if sessions else 0,
        "sessions_by_date": sessions_by_date
    }

# ====== MAIN (para teste) ======

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Teste: salvar sessão de exemplo
        session_id = save_session(
            summary="Implementou RAG Feedback Loop com query logging e analytics",
            tasks_completed=[
                "Criar rag_query_logger.py",
                "Implementar analytics dashboard",
                "Integrar logging em test-rag.py",
                "Criar ADR-009"
            ],
            key_learnings=[
                "JSONL é ideal para append-only logs",
                "Python path calculation: 4x .parent necessário",
                "Query logging permite continuous learning"
            ],
            files_modified=[
                ".claude/scripts/python/rag_query_logger.py",
                ".claude/scripts/python/rag-analytics-dashboard.py",
                ".claude/memory/decisions/ADR-009-RAG-FEEDBACK-LOOP.md"
            ],
            metadata={"type": "implementation", "complexity": "high"}
        )
        print(f"✅ Session saved: {session_id}")

        # Teste: buscar sessões similares
        print("\n🔍 Searching similar sessions for 'RAG implementation'...")
        similar = search_similar_sessions("RAG implementation", n_results=3)
        for i, s in enumerate(similar, 1):
            print(f"\n{i}. {s['summary']}")
            print(f"   Relevance: {s['relevance_score']*100:.1f}%")
            print(f"   Date: {s['timestamp'][:10]}")

    elif len(sys.argv) > 1 and sys.argv[1] == "stats":
        # Mostrar estatísticas
        stats = get_session_stats()
        print("📊 SESSION MEMORY STATISTICS")
        print("=" * 60)
        print(f"Total sessions: {stats['total_sessions']}")
        print(f"Total tasks completed: {stats['total_tasks_completed']}")
        print(f"Total learnings: {stats['total_learnings']}")
        print(f"Total files modified: {stats['total_files_modified']}")
        print(f"Avg tasks/session: {stats['avg_tasks_per_session']:.1f}")
        print(f"Avg learnings/session: {stats['avg_learnings_per_session']:.1f}")

        if stats['sessions_by_date']:
            print("\nSessions by date:")
            for date, count in sorted(stats['sessions_by_date'].items(), reverse=True)[:7]:
                print(f"  {date}: {count}")

    else:
        print("Usage:")
        print("  python3.11 session-memory.py test   - Test save and search")
        print("  python3.11 session-memory.py stats  - Show statistics")
