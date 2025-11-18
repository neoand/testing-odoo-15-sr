#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server para RAG - Claude consulta conhecimento via tool
Inclui reranking para máxima precisão
Otimizado para Mac M3
"""

import sys
import json
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
import torch
from pathlib import Path

# ====== CONFIGURAÇÃO ======
VECTORDB_PATH = "./.claude/vectordb"
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
RERANKER_MODEL = 'cross-encoder/ms-marco-MiniLM-L-6-v2'

# ====== INICIALIZAÇÃO ======

# Detectar device (M3 optimization)
if torch.backends.mps.is_available():
    device = "mps"
elif torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

# Carregar modelos
client = chromadb.PersistentClient(path=VECTORDB_PATH)

try:
    collection = client.get_collection("project_knowledge")
except:
    print(json.dumps({"error": "Vector database não encontrada. Execute index-knowledge.py primeiro."}))
    sys.exit(1)

model = SentenceTransformer(EMBEDDING_MODEL, device=device)
reranker = CrossEncoder(RERANKER_MODEL)

# ====== MCP PROTOCOL ======

def handle_search_knowledge(query: str, n_results: int = 5, use_reranking: bool = True):
    """
    Busca conhecimento do projeto via RAG com reranking opcional

    Args:
        query: Pergunta ou termo de busca
        n_results: Quantos resultados retornar (padrão: 5)
        use_reranking: Usar reranking para melhor precisão (padrão: True)

    Returns:
        JSON com documentos relevantes
    """
    try:
        # Gerar embedding da query
        query_embedding = model.encode(query).tolist()

        # Buscar mais resultados se usar reranking (filtrar depois)
        search_n = n_results * 3 if use_reranking else n_results

        # Buscar no ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(search_n, 50)  # Max 50 para reranking
        )

        if not results['documents'][0]:
            return {
                "status": "success",
                "query": query,
                "results_count": 0,
                "documents": [],
                "reranking_used": False
            }

        # Preparar documentos
        documents = []
        for doc, metadata, distance in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0] if 'distances' in results else [0] * len(results['documents'][0])
        ):
            documents.append({
                'content': doc,
                'file_path': metadata.get('file_path', ''),
                'file_name': metadata.get('file_name', ''),
                'header': metadata.get('header', ''),
                'section_number': metadata.get('section_number', 0),
                'tags': metadata.get('tags', '').split(',') if metadata.get('tags') else [],
                'distance': float(distance),
                'indexed_at': metadata.get('indexed_at', '')
            })

        # Reranking (se habilitado)
        if use_reranking and len(documents) > n_results:
            # Criar pares (query, documento)
            pairs = [[query, doc['content']] for doc in documents]

            # Reranking scores
            scores = reranker.predict(pairs)

            # Adicionar scores e ordenar
            for doc, score in zip(documents, scores):
                doc['rerank_score'] = float(score)

            # Ordenar por rerank_score (maior = mais relevante)
            documents.sort(key=lambda x: x['rerank_score'], reverse=True)

            # Limitar a n_results
            documents = documents[:n_results]

            reranking_used = True
        else:
            reranking_used = False

        return {
            "status": "success",
            "query": query,
            "results_count": len(documents),
            "documents": documents,
            "reranking_used": reranking_used,
            "device": device
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "query": query
        }

def handle_list_sources():
    """Lista todos os arquivos indexados na base"""
    try:
        # Pegar todos documentos
        all_docs = collection.get()

        # Extrair arquivos únicos
        files = {}
        for metadata in all_docs['metadatas']:
            file_path = metadata.get('file_path', '')
            if file_path not in files:
                files[file_path] = {
                    'file_name': metadata.get('file_name', ''),
                    'indexed_at': metadata.get('indexed_at', ''),
                    'chunk_count': 0
                }
            files[file_path]['chunk_count'] += 1

        return {
            "status": "success",
            "total_files": len(files),
            "total_chunks": len(all_docs['ids']),
            "files": [
                {
                    "path": path,
                    "name": info['file_name'],
                    "chunks": info['chunk_count'],
                    "indexed_at": info['indexed_at']
                }
                for path, info in sorted(files.items())
            ]
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def handle_stats():
    """Estatísticas da vector database"""
    try:
        all_docs = collection.get()

        # Calcular estatísticas
        total_chunks = len(all_docs['ids'])

        # Tamanho da database
        db_size_mb = sum(
            f.stat().st_size for f in Path(VECTORDB_PATH).rglob('*') if f.is_file()
        ) / 1024 / 1024

        # Arquivos únicos
        unique_files = len(set(m.get('file_path', '') for m in all_docs['metadatas']))

        # Tags únicas
        all_tags = set()
        for metadata in all_docs['metadatas']:
            tags = metadata.get('tags', '').split(',')
            all_tags.update([t for t in tags if t])

        return {
            "status": "success",
            "total_chunks": total_chunks,
            "unique_files": unique_files,
            "unique_tags": len(all_tags),
            "database_size_mb": round(db_size_mb, 2),
            "embedding_model": EMBEDDING_MODEL,
            "reranker_model": RERANKER_MODEL,
            "device": device,
            "vectordb_path": VECTORDB_PATH
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# ====== MCP SERVER ======

def handle_request(request):
    """Processa requisições MCP"""
    method = request.get('method', '')
    params = request.get('params', {})

    if method == 'search_knowledge':
        return handle_search_knowledge(
            query=params.get('query', ''),
            n_results=params.get('n_results', 5),
            use_reranking=params.get('use_reranking', True)
        )

    elif method == 'list_sources':
        return handle_list_sources()

    elif method == 'stats':
        return handle_stats()

    else:
        return {
            "status": "error",
            "error": f"Método desconhecido: {method}"
        }

# ====== MAIN ======

if __name__ == "__main__":
    print("🚀 MCP RAG Server iniciado", file=sys.stderr)
    print(f"📦 Embedding model: {EMBEDDING_MODEL}", file=sys.stderr)
    print(f"🎯 Reranker model: {RERANKER_MODEL}", file=sys.stderr)
    print(f"⚡ Device: {device}", file=sys.stderr)
    print(f"📂 Database: {VECTORDB_PATH}", file=sys.stderr)
    print("✅ Aguardando requisições...\n", file=sys.stderr)

    # Loop MCP
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except json.JSONDecodeError:
            print(json.dumps({"status": "error", "error": "JSON inválido"}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"status": "error", "error": str(e)}))
            sys.stdout.flush()
