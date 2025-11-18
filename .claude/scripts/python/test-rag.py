#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: test-rag.py
Description: Testa RAG com queries interativas e mostra resultados detalhados
Usage: python3 test-rag.py ["query opcional"]
Author: Claude + Anderson
Created: 2025-11-18
"""

import sys
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
import torch
from pathlib import Path

# Import query logger
script_dir = Path(__file__).parent.absolute()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from rag_query_logger import log_query, log_feedback
    RAG_LOGGING_ENABLED = True
except ImportError:
    print("⚠️  Query logging disabled (rag_query_logger not found)")
    RAG_LOGGING_ENABLED = False
    log_query = lambda *args, **kwargs: None
    log_feedback = lambda *args, **kwargs: None

# ====== CONFIGURAÇÃO ======
# Determine project root
# This script is at: PROJECT_ROOT/.claude/scripts/python/test-rag.py
# So we need parent.parent.parent.parent to get to PROJECT_ROOT
script_path = Path(__file__).resolve()
PROJECT_ROOT = script_path.parent.parent.parent.parent  # .claude/scripts/python/test-rag.py -> PROJECT_ROOT
VECTORDB_PATH = str(PROJECT_ROOT / ".claude" / "vectordb")
MODEL_NAME = 'all-MiniLM-L6-v2'
RERANKER_MODEL = 'cross-encoder/ms-marco-MiniLM-L-6-v2'

# ====== CORES ======
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
CYAN = '\033[0;36m'
MAGENTA = '\033[0;35m'
NC = '\033[0m'  # No Color

# ====== INICIALIZAÇÃO ======

print(f"{BLUE}{'='*70}{NC}")
print(f"{BLUE}🧪 RAG Vector Database - Teste Interativo{NC}")
print(f"{BLUE}{'='*70}{NC}\n")

# Detectar device
if torch.backends.mps.is_available():
    device = "mps"
    device_name = "Apple M3 GPU (MPS)"
elif torch.cuda.is_available():
    device = "cuda"
    device_name = "NVIDIA GPU (CUDA)"
else:
    device = "cpu"
    device_name = "CPU"

print(f"{CYAN}⚡ Hardware: {device_name}{NC}")

# Carregar modelos
print(f"{CYAN}📦 Carregando modelos...{NC}")
client = chromadb.PersistentClient(path=VECTORDB_PATH)

try:
    collection = client.get_collection("project_knowledge")
    total_chunks = collection.count()
    print(f"{GREEN}✅ Vector database carregada: {total_chunks} chunks{NC}")
except:
    print(f"{YELLOW}❌ Vector database não encontrada em {VECTORDB_PATH}{NC}")
    print(f"{YELLOW}💡 Execute: python3 .claude/scripts/python/index-knowledge.py --reindex{NC}")
    sys.exit(1)

model = SentenceTransformer(MODEL_NAME, device=device)
print(f"{GREEN}✅ Embedding model carregado{NC}")

print(f"{CYAN}📦 Carregando reranker (pode demorar primeira vez)...{NC}")
reranker = CrossEncoder(RERANKER_MODEL)
print(f"{GREEN}✅ Reranker carregado{NC}\n")

print(f"{BLUE}{'='*70}{NC}\n")

# ====== FUNÇÃO DE BUSCA ======

def search_with_reranking(query, n_results=5):
    """Busca com reranking"""

    print(f"{YELLOW}🔍 Buscando: '{query}'{NC}\n")

    # Embedding da query
    query_embedding = model.encode(query).tolist()

    # Buscar mais para reranking
    search_n = n_results * 3

    # Buscar
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(search_n, 50)
    )

    if not results['documents'][0]:
        print(f"{YELLOW}❌ Nenhum resultado encontrado{NC}\n")
        return

    # Preparar documentos
    documents = []
    for doc, metadata, distance in zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ):
        documents.append({
            'content': doc,
            'file': metadata.get('file_name', ''),
            'header': metadata.get('header', ''),
            'tags': metadata.get('tags', '').split(',') if metadata.get('tags') else [],
            'distance': float(distance)
        })

    # Reranking
    print(f"{CYAN}⚡ Aplicando reranking...{NC}")
    pairs = [[query, doc['content']] for doc in documents]
    scores = reranker.predict(pairs)

    for doc, score in zip(documents, scores):
        doc['rerank_score'] = float(score)

    # Ordenar por rerank_score
    documents.sort(key=lambda x: x['rerank_score'], reverse=True)
    documents = documents[:n_results]

    # LOG QUERY (Feedback Loop)
    if RAG_LOGGING_ENABLED:
        try:
            query_id = log_query(
                query=query,
                results=[{
                    'file': d['file'],
                    'header': d['header'],
                    'rerank_score': d['rerank_score'],
                    'distance': d['distance']
                } for d in documents],
                metadata={'device': device, 'n_results': n_results}
            )
            print(f"{CYAN}📊 Query logged (ID: {query_id}){NC}")
        except Exception as e:
            print(f"{YELLOW}⚠️  Logging failed: {e}{NC}")

    # Mostrar resultados
    print(f"\n{GREEN}{'='*70}{NC}")
    print(f"{GREEN}📊 Top {len(documents)} Resultados (com reranking):{NC}")
    print(f"{GREEN}{'='*70}{NC}\n")

    for i, doc in enumerate(documents, 1):
        print(f"{MAGENTA}━━━ Resultado #{i} ━━━{NC}")
        print(f"{CYAN}📄 Arquivo:{NC} {doc['file']}")
        print(f"{CYAN}📍 Seção:{NC} {doc['header']}")
        print(f"{CYAN}🎯 Rerank Score:{NC} {doc['rerank_score']:.4f} (quanto maior, mais relevante)")
        print(f"{CYAN}📏 Distance:{NC} {doc['distance']:.4f}")

        if doc['tags']:
            print(f"{CYAN}🏷️  Tags:{NC} {', '.join(doc['tags'])}")

        # Preview do conteúdo
        preview = doc['content'][:300].replace('\n', ' ')
        print(f"\n{YELLOW}📝 Preview:{NC}")
        print(f"   {preview}...\n")

    print(f"{GREEN}{'='*70}{NC}\n")

# ====== QUERIES DE TESTE ======

default_queries = [
    "Como resolver erro de rede no Odoo?",
    "Comandos SSH para reiniciar serviços",
    "Patterns de performance ORM Python",
    "Configuração http_interface Odoo",
    "GCP firewall rules criar"
]

# ====== MAIN ======

# Query via argumento
if len(sys.argv) > 1:
    query = ' '.join(sys.argv[1:])
    search_with_reranking(query)
else:
    # Modo interativo
    print(f"{BLUE}🎯 Queries de Teste Sugeridas:{NC}\n")
    for i, q in enumerate(default_queries, 1):
        print(f"   {i}. {q}")

    print(f"\n{YELLOW}💡 Digite sua query (ou número 1-5, ou Enter para testar todas):{NC} ", end='')

    user_input = input().strip()

    if not user_input:
        # Testar todas
        print(f"\n{BLUE}🚀 Executando todas queries de teste...{NC}\n")
        for query in default_queries:
            search_with_reranking(query, n_results=3)
            print(f"\n{BLUE}{'─'*70}{NC}\n")

    elif user_input.isdigit() and 1 <= int(user_input) <= 5:
        # Query pré-definida
        query = default_queries[int(user_input) - 1]
        search_with_reranking(query)

    else:
        # Query customizada
        search_with_reranking(user_input)

print(f"\n{GREEN}✅ Teste completo!{NC}\n")
