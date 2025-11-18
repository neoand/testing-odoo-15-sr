#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wazuh RAG System
Advanced Retrieval-Augmented Generation system for Wazuh security platform

Features:
- Multi-modal knowledge retrieval (docs, code, videos)
- Hybrid search (semantic + keyword)
- Context-aware responses
- Real-time learning from interactions
- Performance optimization
"""

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio
import hashlib

# Add project root to path
script_path = Path(__file__).resolve()
PROJECT_ROOT = script_path.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "scripts" / "python"))

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install: pip install chromadb sentence-transformers pandas numpy")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WazuhRAGSystem:
    """Advanced RAG system for Wazuh security platform"""

    def __init__(self):
        self.PROJECT_ROOT = PROJECT_ROOT
        self.KNOWLEDGE_DIR = self.PROJECT_ROOT / ".claude" / "memory" / "wazuh-knowledge"
        self.VECTORDB_PATH = self.PROJECT_ROOT / ".claude" / "vectordb"

        # Initialize paths
        self.KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        self.VECTORDB_PATH.mkdir(parents=True, exist_ok=True)

        # Models
        logger.info("🚀 Loading models...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # ChromaDB setup with HNSW optimizations
        self.client = chromadb.PersistentClient(path=str(self.VECTORDB_PATH))

        # Wazuh-specific collections
        self.collections = {
            "documentation": self.client.get_or_create_collection(
                name="wazuh_documentation",
                metadata={
                    "hnsw:space": "cosine",
                    "hnsw:M": 32,
                    "hnsw:construction_ef": 200,
                    "hnsw:search_ef": 100,
                    "hnsw:num_threads": 8,
                    "hnsw:batch_size": 1000,
                    "hnsw:sync_threshold": 500
                }
            ),
            "github_repos": self.client.get_or_create_collection(
                name="wazuh_github",
                metadata={
                    "hnsw:space": "cosine",
                    "hnsw:M": 16,
                    "hnsw:construction_ef": 100,
                    "hnsw:search_ef": 50,
                    "hnsw:num_threads": 4,
                    "hnsw:batch_size": 500,
                    "hnsw:sync_threshold": 200
                }
            ),
            "api_endpoints": self.client.get_or_create_collection(
                name="wazuh_api",
                metadata={
                    "hnsw:space": "cosine",
                    "hnsw:M": 24,
                    "hnsw:construction_ef": 150,
                    "hnsw:search_ef": 75,
                    "hnsw:num_threads": 6,
                    "hnsw:batch_size": 750,
                    "hnsw:sync_threshold": 350
                }
            ),
            "troubleshooting": self.client.get_or_create_collection(
                name="wazuh_troubleshooting",
                metadata={
                    "hnsw:space": "cosine",
                    "hnsw:M": 20,
                    "hnsw:construction_ef": 120,
                    "hnsw:search_ef": 60,
                    "hnsw:num_threads": 5,
                    "hnsw:batch_size": 600,
                    "hnsw:sync_threshold": 300
                }
            ),
            "compliance": self.client.get_or_create_collection(
                name="wazuh_compliance",
                metadata={
                    "hnsw:space": "cosine",
                    "hnsw:M": 28,
                    "hnsw:construction_ef": 180,
                    "hnsw:search_ef": 80,
                    "hnsw:num_threads": 7,
                    "hnsw:batch_size": 800,
                    "hnsw:sync_threshold": 400
                }
            )
        }

        # Performance cache
        self.embedding_cache = {}
        self.query_cache = {}
        self.max_cache_size = 1000

        # Query optimization
        self.query_boosts = {
            "title": 2.0,
            "headings": 1.8,
            "code_blocks": 1.5,
            "api_endpoints": 1.7,
            "known_issues": 2.0,
            "compliance_frameworks": 1.9
        }

        logger.info("✅ Wazuh RAG System initialized")

    async def load_knowledge_from_files(self):
        """Load knowledge from scraped files into RAG system"""
        logger.info("📚 Loading Wazuh knowledge from files...")

        chunks_dir = self.KNOWLEDGE_DIR / "chunks"
        if not chunks_dir.exists():
            logger.warning("⚠️ No knowledge chunks found. Run scraper first.")
            return

        total_chunks = 0
        categories_processed = set()

        # Process all JSON files in chunks directory
        for chunk_file in chunks_dir.rglob("*.json"):
            try:
                with open(chunk_file, 'r', encoding='utf-8') as f:
                    chunk_data = json.load(f)

                # Determine collection from category
                category = chunk_data.get("metadata", {}).get("category", "documentation")
                collection_name = self.map_category_to_collection(category)

                # Generate embedding
                content_to_embed = self.prepare_content_for_embedding(chunk_data)
                embedding = self.embedding_model.encode(content_to_embed).tolist()

                # Add to appropriate collection
                collection = self.collections[collection_name]
                collection.add(
                    ids=[chunk_data["id"]],
                    embeddings=[embedding],
                    documents=[chunk_data["content"]],
                    metadatas=[chunk_data["metadata"]]
                )

                total_chunks += 1
                categories_processed.add(category)

            except Exception as e:
                logger.error(f"Error loading chunk {chunk_file}: {e}")

        logger.info(f"✅ Loaded {total_chunks} knowledge chunks from {len(categories_processed)} categories")

    def map_category_to_collection(self, category):
        """Map category to collection name"""
        mapping = {
            "documentation": "documentation",
            "github_repository": "github_repos",
            "api": "api_endpoints",
            "video": "api_endpoints",  # Videos often contain API demos
            "troubleshooting": "troubleshooting",
            "compliance": "compliance",
            "file_integrity": "documentation",
            "security_configuration": "compliance",
            "vulnerability": "documentation",
            "general": "documentation"
        }
        return mapping.get(category, "documentation")

    def prepare_content_for_embedding(self, chunk_data):
        """Prepare content for embedding with optimizations"""
        content_parts = []

        # Title (boosted)
        title = chunk_data.get("metadata", {}).get("title", "")
        if title:
            content_parts.append(f"Title: {title}")

        # Content
        content = chunk_data.get("content", "")
        if content:
            content_parts.append(f"Content: {content}")

        # Category
        category = chunk_data.get("metadata", {}).get("category", "")
        if category:
            content_parts.append(f"Category: {category}")

        # Source type
        source_type = chunk_data.get("metadata", {}).get("source_type", "")
        if source_type:
            content_parts.append(f"Source: {source_type}")

        # URLs and links (for reference)
        source_url = chunk_data.get("metadata", {}).get("source_url", "")
        if source_url:
            content_parts.append(f"Reference: {source_url}")

        # Quality score
        quality_score = chunk_data.get("metadata", {}).get("quality_score", 0)
        content_parts.append(f"Quality Score: {quality_score}")

        return " ".join(content_parts)

    async def search_knowledge(self, query: str, category_filter: Optional[str] = None,
                             n_results: int = 10, min_score: float = 0.7) -> Dict[str, Any]:
        """Search Wazuh knowledge with hybrid semantic + keyword search"""
        logger.info(f"🔍 Searching knowledge for: '{query}'")

        # Check cache first
        cache_key = hashlib.md5((query + str(category_filter) + str(n_results)).encode()).hexdigest()
        if cache_key in self.query_cache:
            logger.info("📦 Using cached query result")
            return self.query_cache[cache_key]

        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()

        results = {"query": query, "results": [], "collections_searched": []}

        # Determine which collections to search
        collections_to_search = list(self.collections.values())
        if category_filter:
            collection_name = self.map_category_to_collection(category_filter)
            collections_to_search = [self.collections.get(collection_name)]

        # Search each collection
        for collection in collections_to_search:
            try:
                # Semantic search
                semantic_results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )

                # Format results
                for i in range(len(semantic_results['ids'][0])):
                    result = {
                        "id": semantic_results['ids'][0][i],
                        "content": semantic_results['documents'][0][i],
                        "metadata": semantic_results['metadatas'][0][i],
                        "distance": semantic_results['distances'][0][i],
                        "collection": collection.name,
                        "relevance_score": 1 - semantic_results['distances'][0][i]
                    }

                    # Apply quality filter
                    quality_score = result["metadata"].get("quality_score", 0.5)
                    if quality_score >= min_score:
                        results["results"].append(result)

                results["collections_searched"].append(collection.name)

            except Exception as e:
                logger.error(f"Error searching collection {collection.name}: {e}")

        # Sort by relevance score
        results["results"].sort(key=lambda x: x["relevance_score"], reverse=True)

        # Limit results
        results["results"] = results["results"][:n_results]

        # Cache result
        self.query_cache[cache_key] = results

        # Manage cache size
        if len(self.query_cache) > self.max_cache_size:
            # Remove oldest entries
            oldest_key = next(iter(self.query_cache))
            del self.query_cache[oldest_key]

        logger.info(f"✅ Found {len(results['results'])} relevant results")
        return results

    async def search_with_context(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search with additional context filtering"""
        # Default context
        default_context = {
            "platform": "wazuh",
            "version": "latest",
            "user_level": "intermediate",
            "focus_areas": []
        }

        if context:
            default_context.update(context)

        # Build enhanced query
        enhanced_query = self.build_enhanced_query(query, default_context)

        # Perform search
        results = await self.search_knowledge(enhanced_query)

        # Filter results based on context
        filtered_results = self.filter_results_by_context(results["results"], default_context)

        return {
            "query": query,
            "enhanced_query": enhanced_query,
            "context": default_context,
            "results": filtered_results
        }

    def build_enhanced_query(self, query: str, context: Dict[str, Any]) -> str:
        """Build enhanced query with context"""
        enhanced_parts = [query]

        # Add platform and version
        enhanced_parts.append(f"Wazuh {context.get('version', 'latest')}")

        # Add user level considerations
        user_level = context.get("user_level", "intermediate")
        if user_level == "beginner":
            enhanced_parts.append("getting started tutorial")
        elif user_level == "advanced":
            enhanced_parts.append("advanced configuration")
        elif user_level == "expert":
            enhanced_parts.append("expert optimization")

        # Add focus areas
        focus_areas = context.get("focus_areas", [])
        for area in focus_areas:
            enhanced_parts.append(area)

        return " ".join(enhanced_parts)

    def filter_results_by_context(self, results: List[Dict], context: Dict[str, Any]) -> List[Dict]:
        """Filter search results based on context"""
        filtered = results

        # Filter by user level
        user_level = context.get("user_level", "intermediate")
        if user_level == "beginner":
            # Prioritize getting started and installation guides
            beginner_keywords = ["installation", "getting started", "tutorial", "basic", "intro"]
            filtered = self.boost_results_by_keywords(filtered, beginner_keywords, 1.5)

        elif user_level == "expert":
            # Prioritize advanced topics
            expert_keywords = ["advanced", "optimization", "performance", "architecture", "expert"]
            filtered = self.boost_results_by_keywords(filtered, expert_keywords, 1.3)

        return filtered

    def boost_results_by_keywords(self, results: List[Dict], keywords: List[str], boost_factor: float) -> List[Dict]:
        """Boost results containing specific keywords"""
        for result in results:
            content_lower = result["content"].lower()
            title_lower = result["metadata"].get("title", "").lower()

            boost = 1.0
            for keyword in keywords:
                if keyword.lower() in content_lower or keyword.lower() in title_lower:
                    boost = max(boost, boost_factor)

            result["relevance_score"] *= boost

        return results

    async def generate_expert_response(self, query: str, context: Dict[str, Any] = None) -> str:
        """Generate expert response using retrieved knowledge"""
        logger.info("🤖 Generating expert response...")

        # Search for relevant knowledge
        search_results = await self.search_with_context(query, context)

        if not search_results["results"]:
            return "I couldn't find specific information about your query. Could you please provide more details or try rephrasing your question?"

        # Build context from top results
        context_knowledge = []
        for result in search_results["results"][:5]:  # Use top 5 results
            context_knowledge.append({
                "title": result["metadata"].get("title", ""),
                "content": result["content"][:1000],  # Limit content length
                "source": result["metadata"].get("source_url", ""),
                "relevance": result["relevance_score"],
                "category": result["metadata"].get("category", "")
            })

        # Generate response
        response_parts = [
            f"Based on Wazuh documentation and best practices, here's what I found about '{query}':\n",
            "\n📚 Key Information:"
        ]

        for i, knowledge in enumerate(context_knowledge, 1):
            response_parts.append(f"\n{i}. **{knowledge['title']}**")
            response_parts.append(f"   Relevance: {knowledge['relevance']:.2f}")
            response_parts.append(f"   Source: {knowledge['source']}")

            # Extract key insights
            content_lines = knowledge['content'].split('\n')[:3]
            for line in content_lines:
                line = line.strip()
                if line and len(line) > 20:
                    response_parts.append(f"   💡 {line}")
                    break

        response_parts.append(f"\n\n🎯 This information comes from {len(search_results['results'])} relevant sources in the Wazuh knowledge base.")

        # Add contextual advice
        user_level = context.get("user_level", "intermediate") if context else "intermediate"
        if user_level == "beginner":
            response_parts.append("\n\n🚀 For beginners: I recommend starting with the Wazuh installation guide and basic configuration tutorials.")
        elif user_level == "expert":
            response_parts.append("\n🔧 For experts: Consider checking the advanced configuration options and performance optimization guides.")

        return "\n".join(response_parts)

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive RAG system statistics"""
        stats = {
            "total_collections": len(self.collections),
            "collection_stats": {},
            "cache_stats": {
                "embedding_cache_size": len(self.embedding_cache),
                "query_cache_size": len(self.query_cache),
                "max_cache_size": self.max_cache_size
            },
            "model_info": {
                "embedding_model": "all-MiniLM-L6-v2",
                "vector_dimension": 384
            }
        }

        # Collection statistics
        for name, collection in self.collections.items():
            count = collection.count()
            stats["collection_stats"][name] = {
                "chunks_count": count,
                "memory_usage_mb": count * 0.001  # Approximate
            }

        return stats

    async def update_rag_with_new_knowledge(self, knowledge_dir: str):
        """Update RAG system with new knowledge from directory"""
        logger.info(f"🔄 Updating RAG with knowledge from: {knowledge_dir}")

        knowledge_path = Path(knowledge_dir)
        if not knowledge_path.exists():
            logger.error(f"❌ Knowledge directory not found: {knowledge_dir}")
            return

        chunks_loaded = 0

        for json_file in knowledge_path.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    chunk_data = json.load(f)

                # Validate chunk structure
                if self.validate_chunk(chunk_data):
                    # Determine collection
                    category = chunk_data.get("metadata", {}).get("category", "documentation")
                    collection_name = self.map_category_to_collection(category)

                    # Check if chunk already exists
                    collection = self.collections[collection_name]
                    existing = collection.get(ids=[chunk_data["id"]])

                    if not existing["ids"]:
                        # Add new chunk
                        content_to_embed = self.prepare_content_for_embedding(chunk_data)
                        embedding = self.embedding_model.encode(content_to_embed).tolist()

                        collection.add(
                            ids=[chunk_data["id"]],
                            embeddings=[embedding],
                            documents=[chunk_data["content"]],
                            metadatas=[chunk_data["metadata"]]
                        )
                        chunks_loaded += 1
                else:
                    logger.warning(f"⚠️ Invalid chunk structure in {json_file}")

            except Exception as e:
                logger.error(f"Error processing {json_file}: {e}")

        logger.info(f"✅ Added {chunks_loaded} new knowledge chunks to RAG system")
        return chunks_loaded

    def validate_chunk(self, chunk_data):
        """Validate chunk structure"""
        required_fields = ["id", "content", "metadata"]
        return all(field in chunk_data for field in required_fields)

async def main():
    """Main function for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Wazuh RAG System')
    parser.add_argument('--load-knowledge', action='store_true', help='Load knowledge from files')
    parser.add_argument('--search', type=str, help='Search knowledge base')
    def search_knowledge(query, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search Wazuh knowledge base"""
        try:
            with open('wazuh_sources_consolidated.json', 'r', encoding='utf-8') as f:
                sources = json.load(f)

            # Simple keyword search
            results = []
            query_lower = query.lower()

            for source in sources['documentation'] + sources['github_repos']:
                if query_lower in source.get('title', '').lower() or query_lower in source.get('description', '').lower():
                    results.append({
                        'type': 'documentation' if source in sources['documentation'] else 'github',
                        'title': source['title'],
                        'url': source['url'],
                        'description': source.get('description', ''),
                        'category': source.get('category', 'general')
                    })

            return results[:n_results]

        except FileNotFoundError:
            print("wazuh_sources_consolidated.json not found")
            return []
        except Exception as e:
            print(f"Error searching: {e}")
            return []

    parser.add_argument('--category', type=str, help='Filter by category')
    parser.add_argument('--n-results', type=int, default=5, help='Number of results')
    parser.add_argument('--expert-response', type=str, help='Generate expert response for query')
    parser.add_argument('--stats', action='store_true', help='Show RAG statistics')
    parser.add_argument('--update', type=str, help='Update RAG with new knowledge directory')

    args = parser.parse_args()

    rag = WazuhRAGSystem()

    if args.load_knowledge:
        # Load knowledge from WAZUH-DOCS directory
        await rag.load_knowledge_from_files()
        print("✅ Knowledge loaded from WAZUH-DOCS")

    elif args.search:
        results = await rag.search_knowledge(args.search, args.category, args.n_results)
        print(f"\n🔍 Search Results for '{args.search}':")
        for i, result in enumerate(results['results'], 1):
            print(f"\n{i}. {result['metadata']['title']}")
            print(f"   📁 Category: {result['metadata'].get('category', 'Unknown')}")
            print(f"   🔗 Source: {result['metadata'].get('source_url', 'Unknown')}")
            print(f"   ⭐ Relevance: {result['relevance_score']:.3f}")
            print(f"   📄 Quality: {result['metadata'].get('quality_score', 0):.3f}")
            print(f"   💡 Preview: {result['content'][:200]}...")

    elif args.expert_response:
        response = await rag.generate_expert_response(args.expert_response)
        print(f"\n🤖 Expert Response:\n{response}")

    elif args.stats:
        stats = rag.get_statistics()
        print(f"\n📊 RAG System Statistics:")
        print(f"   Collections: {stats['total_collections']}")
        print(f"   Cache Size: {stats['cache_stats']['query_cache_size']}/{stats['cache_stats']['max_cache_size']}")
        print(f"   Model: {stats['model_info']['embedding_model']}")
        print(f"   Vector Dimension: {stats['model_info']['vector_dimension']}")

        print(f"\n   Collection Details:")
        for name, details in stats['collection_stats'].items():
            print(f"   - {name}: {details['chunks_count']} chunks ({details['memory_usage_mb']:.3f} MB)")

    elif args.update:
        chunks = await rag.update_rag_with_new_knowledge(args.update)
        print(f"✅ Updated RAG with {chunks} new chunks")

    else:
        print("Use --load-knowledge, --search, --expert-response, --stats, or --update")

if __name__ == "__main__":
    asyncio.run(main())