#!/usr/bin/env python3
"""
Hierarchical RAG System - Organização avançada de conhecimento

Implementa RAG hierárquico com múltiplas coleções especializadas:
- code_knowledge: Código fonte e implementações
- errors_solved: Erros resolvidos e soluções
- patterns: Padrões e boas práticas
- documentation: Documentação oficial e guias
- odoo_specific: Conhecimento específico do Odoo
- api_integrations: APIs e integrações externas

Usa cross-encoder para reranking avançado e cache LRU.
"""

import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from functools import lru_cache
import logging

# Configuração
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Resultado da busca RAG com metadados enriquecidos"""
    content: str
    metadata: Dict[str, Any]
    score: float
    collection_type: str
    file_path: Optional[str] = None
    relevance_boost: float = 1.0

class HierarchicalRAG:
    """Sistema RAG Hierárquico para Claude Code"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.vector_db_path = self.project_root / ".claude" / "vectordb"

        # Modelos
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

        # Cache
        self.query_cache = {}
        self.cache_ttl = 3600  # 1 hora

        # Inicializar coleções
        self._init_collections()

        # Mapeamento de coleções
        self.collections_config = {
            'code_knowledge': {
                'description': 'Código fonte, implementações e exemplos',
                'weight': 1.2,
                'boost_keywords': ['function', 'class', 'def', 'import', 'implementação']
            },
            'errors_solved': {
                'description': 'Erros resolvidos e soluções aplicadas',
                'weight': 1.5,
                'boost_keywords': ['erro', 'solução', 'fix', 'problema', 'resolvido']
            },
            'patterns': {
                'description': 'Padrões, boas práticas e convenções',
                'weight': 1.3,
                'boost_keywords': ['padrão', 'prática', 'convenção', 'melhoria', 'otimização']
            },
            'documentation': {
                'description': 'Documentação oficial e guias',
                'weight': 1.0,
                'boost_keywords': ['documentação', 'guia', 'manual', 'referência']
            },
            'odoo_specific': {
                'description': 'Conhecimento específico do Odoo',
                'weight': 1.4,
                'boost_keywords': ['odoo', 'módulo', 'campo', 'modelo', 'view']
            },
            'api_integrations': {
                'description': 'APIs e integrações externas',
                'weight': 1.3,
                'boost_keywords': ['api', 'endpoint', 'integration', 'webhook', 'kolmeya']
            }
        }

    def _init_collections(self):
        """Inicializa ou obtém coleções ChromaDB"""
        self.client = chromadb.PersistentClient(str(self.vector_db_path))
        self.collections = {}

        for collection_name in self.collections_config.keys():
            try:
                self.collections[collection_name] = self.client.get_collection(collection_name)
                logger.info(f"Coleção '{collection_name}' carregada")
            except:
                self.collections[collection_name] = self.client.create_collection(
                    name=collection_name,
                    metadata=self.collections_config[collection_name]
                )
                logger.info(f"Coleção '{collection_name}' criada")

    def _get_cache_key(self, query: str, collection_type: str, k: int) -> str:
        """Gera chave de cache para query"""
        return hashlib.md5(f"{query}:{collection_type}:{k}".encode()).hexdigest()

    @lru_cache(maxsize=256)
    def get_query_embedding(self, query: str) -> List[float]:
        """Cache de embeddings para queries repetidas"""
        return self.embedding_model.encode(query, convert_to_tensor=False).tolist()

    def _boost_relevance(self, result: SearchResult, query: str) -> SearchResult:
        """Aplica boost de relevância baseado em keywords e collection type"""
        query_lower = query.lower()
        content_lower = result.content.lower()

        # Boost por keywords da coleção
        collection_config = self.collections_config.get(result.collection_type, {})
        boost_keywords = collection_config.get('boost_keywords', [])

        for keyword in boost_keywords:
            if keyword in query_lower and keyword in content_lower:
                result.relevance_boost *= 1.2

        # Boost por correspondência exata
        if query_lower in content_lower:
            result.relevance_boost *= 1.3

        # Boost por tamanho apropriado
        content_length = len(result.content)
        if 100 <= content_length <= 1000:  # Tamanho ideal
            result.relevance_boost *= 1.1
        elif content_length > 2000:  # Muito longo
            result.relevance_boost *= 0.9

        return result

    def search(self, query: str, collection_type: str = 'all', k: int = 10,
               use_reranking: bool = True) -> List[SearchResult]:
        """
        Busca hierárquica avançada

        Args:
            query: Query de busca
            collection_type: 'all' ou nome específico da coleção
            k: Número máximo de resultados
            use_reranking: Se deve usar cross-encoder para reranking

        Returns:
            Lista de SearchResult ordenados por relevância
        """
        cache_key = self._get_cache_key(query, collection_type, k)

        # Verificar cache
        if cache_key in self.query_cache:
            cached_result = self.query_cache[cache_key]
            if time.time() - cached_result['timestamp'] < self.cache_ttl:
                logger.info(f"Cache HIT para query: {query[:50]}...")
                return cached_result['results']

        # Busca nas coleções
        if collection_type == 'all':
            results = self._search_all_collections(query, k)
        else:
            results = self._search_single_collection(query, collection_type, k)

        # Aplicar boosts de relevância
        results = [self._boost_relevance(r, query) for r in results]

        # Reranking com cross-encoder
        if use_reranking and len(results) > 1:
            results = self._rerank_results(query, results)

        # Ordenar por score final
        results.sort(key=lambda x: x.score * x.relevance_boost, reverse=True)

        # Limitar resultados
        results = results[:k]

        # Cache do resultado
        self.query_cache[cache_key] = {
            'results': results,
            'timestamp': time.time()
        }

        logger.info(f"Busca concluída: {len(results)} resultados para '{query[:50]}...'")
        return results

    def _search_all_collections(self, query: str, k: int) -> List[SearchResult]:
        """Busca em todas as coleções"""
        all_results = []
        k_per_collection = max(k // len(self.collections), 2)

        for collection_name, collection in self.collections.items():
            try:
                results = self._search_single_collection(query, collection_name, k_per_collection)
                all_results.extend(results)
            except Exception as e:
                logger.warning(f"Erro buscando na coleção {collection_name}: {e}")

        return all_results

    def _search_single_collection(self, query: str, collection_name: str, k: int) -> List[SearchResult]:
        """Busca em uma coleção específica"""
        collection = self.collections[collection_name]

        # Embedding da query
        query_embedding = self.get_query_embedding(query)

        # Busca na coleção
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )

        # Converter para SearchResult
        search_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                distance = results['distances'][0][i] if results['distances'] and results['distances'][0] else 1.0

                # Converter distância para score (quanto menor a distância, maior o score)
                score = 1.0 - min(distance, 1.0)

                # Aplicar weight da coleção
                collection_weight = self.collections_config.get(collection_name, {}).get('weight', 1.0)
                score *= collection_weight

                search_result = SearchResult(
                    content=doc,
                    metadata=metadata,
                    score=score,
                    collection_type=collection_name,
                    file_path=metadata.get('file_path'),
                    relevance_boost=1.0
                )
                search_results.append(search_result)

        return search_results

    def _rerank_results(self, query: str, results: List[SearchResult]) -> List[SearchResult]:
        """Reranking avançado usando cross-encoder"""
        if len(results) <= 1:
            return results

        # Preparar pares (query, document) para o cross-encoder
        doc_texts = [result.content for result in results]
        query_doc_pairs = [(query, doc) for doc in doc_texts]

        # Calcular scores do cross-encoder
        cross_scores = self.cross_encoder.predict(query_doc_pairs)

        # Aplicar scores aos resultados
        for i, result in enumerate(results):
            # Combinar score original com cross-encoder score
            combined_score = (result.score * 0.3) + (cross_scores[i] * 0.7)
            result.score = max(0, min(1, combined_score))  # Normalizar entre 0 e 1

        logger.info(f"Reranking aplicado a {len(results)} resultados")
        return results

    def add_document(self, content: str, collection_type: str, metadata: Dict[str, Any] = None):
        """Adiciona documento a uma coleção específica"""
        if collection_type not in self.collections:
            raise ValueError(f"Coleção '{collection_type}' não existe")

        if metadata is None:
            metadata = {}

        # Metadata obrigatória
        metadata.update({
            'added_at': time.time(),
            'content_length': len(content),
            'file_path': metadata.get('file_path', ''),
            'source': metadata.get('source', 'manual')
        })

        # Embedding do conteúdo
        embedding = self.embedding_model.encode(content, convert_to_tensor=False).tolist()

        # Adicionar à coleção
        collection = self.collections[collection_type]
        collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata],
            ids=[hashlib.md5(f"{content[:100]}{time.time()}".encode()).hexdigest()]
        )

        logger.info(f"Documento adicionado à coleção '{collection_type}'")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas das coleções"""
        stats = {}
        total_documents = 0

        for collection_name, collection in self.collections.items():
            try:
                count = collection.count()
                stats[collection_name] = {
                    'count': count,
                    'description': self.collections_config[collection_name]['description'],
                    'weight': self.collections_config[collection_name]['weight']
                }
                total_documents += count
            except Exception as e:
                stats[collection_name] = {'error': str(e)}

        stats['total_documents'] = total_documents
        stats['total_collections'] = len(self.collections)
        stats['cache_size'] = len(self.query_cache)

        return stats

    def clear_cache(self):
        """Limpa cache de queries"""
        self.query_cache.clear()
        logger.info("Cache de queries limpo")

def main():
    """Teste do sistema RAG hierárquico"""
    rag = HierarchicalRAG()

    print("=== Hierarchical RAG System ===")
    print("\nEstatísticas das coleções:")
    stats = rag.get_collection_stats()
    for collection, info in stats.items():
        if collection not in ['total_documents', 'total_collections', 'cache_size']:
            print(f"  {collection}: {info.get('count', 0)} documentos")

    print(f"\nTotal: {stats.get('total_documents', 0)} documentos")
    print(f"Cache: {stats.get('cache_size', 0)} queries")

    # Teste de busca
    test_queries = [
        "odoo sms integration error",
        "python performance optimization",
        "api authentication patterns"
    ]

    print("\n=== Testes de Busca ===")
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = rag.search(query, k=3)

        for i, result in enumerate(results, 1):
            print(f"  {i}. [{result.collection_type}] Score: {result.score:.3f}")
            print(f"     {result.content[:100]}...")

if __name__ == "__main__":
    main()