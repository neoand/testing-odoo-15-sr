#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Auto-Learning System
Automatic knowledge extraction and RAG updates for Claude

Features:
- Extract knowledge from conversations
- Auto-update ChromaDB with learnings
- Session memory integration
- Automatic reindexing
- Error handling and validation
"""

import sys
import json
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add project root to path
script_path = Path(__file__).resolve()
PROJECT_ROOT = script_path.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "scripts" / "python"))

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    # Try to import session_memory, but make it optional for testing
    try:
        import session_memory
    except ImportError:
        print("⚠️ session_memory module not available, some features disabled")
        session_memory = None
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install: pip install chromadb sentence-transformers watchdog")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RAGAutoLearning:
    def __init__(self):
        """Initialize RAG Auto-Learning System"""
        # Paths
        self.PROJECT_ROOT = PROJECT_ROOT
        self.VECTORDB_PATH = self.PROJECT_ROOT / ".claude" / "vectordb"
        self.MEMORY_PATH = self.PROJECT_ROOT / ".claude" / "memory"

        # Models
        logger.info("🚀 Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # ChromaDB setup
        self.client = chromadb.PersistentClient(path=str(self.VECTORDB_PATH))
        self.knowledge_collection = self.client.get_or_create_collection(
            name="project_knowledge",
            metadata={
                "hnsw:space": "cosine",
                "hnsw:M": 32,
                "hnsw:construction_ef": 200,
                "hnsw:search_ef": 100,
                "hnsw:num_threads": 8,
                "hnsw:batch_size": 1000,
                "hnsw:sync_threshold": 500
            }
        )

        # Session memory (optional)
        if session_memory:
            self.session_memory = session_memory.SessionMemory()
        else:
            self.session_memory = None

        logger.info("✅ RAG Auto-Learning System initialized")

    def extract_knowledge_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract knowledge chunks from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract different types of knowledge
            knowledge_chunks = []

            # 1. Solutions from ERRORS-SOLVED.md
            if "ERRORS-SOLVED.md" in str(file_path):
                knowledge_chunks.extend(self._extract_error_solutions(content))

            # 2. Patterns from PATTERNS.md
            elif "PATTERNS.md" in str(file_path):
                knowledge_chunks.extend(self._extract_patterns(content))

            # 3. Commands from COMMAND-HISTORY.md
            elif "COMMAND-HISTORY.md" in str(file_path):
                knowledge_chunks.extend(self._extract_commands(content))

            # 4. General knowledge from other files
            else:
                knowledge_chunks.extend(self._extract_general_knowledge(content, file_path))

            return knowledge_chunks

        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {e}")
            return []

    def _extract_error_solutions(self, content: str) -> List[Dict[str, Any]]:
        """Extract solutions from ERRORS-SOLVED.md"""
        chunks = []
        lines = content.split('\n')
        current_error = {}

        for line in lines:
            if line.startswith('### [20'):
                if current_error:
                    chunks.append(current_error)
                current_error = {'type': 'error_solution', 'content': '', 'metadata': {}}
                # Extract date from header
                date_part = line.split(']')[0].strip('### [')
                current_error['metadata']['date'] = date_part
                current_error['content'] += line + '\n'
            elif current_error and line.strip():
                current_error['content'] += line + '\n'
                # Extract key sections
                if line.startswith('**Contexto:**'):
                    current_error['metadata']['context'] = line.replace('**Contexto:**', '').strip()
                elif line.startswith('**Solução:**'):
                    current_error['metadata']['solution'] = line.replace('**Solução:**', '').strip()
                elif line.startswith('**Tags:**'):
                    tags = line.replace('**Tags:**', '').strip()
                    current_error['metadata']['tags'] = [tag.strip('#') for tag in tags.split() if tag.startswith('#')]

        if current_error:
            chunks.append(current_error)

        return chunks

    def _extract_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Extract patterns from PATTERNS.md"""
        chunks = []
        lines = content.split('\n')
        current_pattern = {}

        for line in lines:
            if line.startswith('### ') and 'Pattern' in line:
                if current_pattern:
                    chunks.append(current_pattern)
                current_pattern = {'type': 'pattern', 'content': '', 'metadata': {}}
                current_pattern['metadata']['name'] = line.replace('### ', '').strip()
                current_pattern['content'] += line + '\n'
            elif current_pattern and line.strip():
                current_pattern['content'] += line + '\n'
                # Extract code examples
                if line.startswith('```'):
                    current_pattern['metadata']['has_code'] = True
                elif line.startswith('**Por que:**'):
                    current_pattern['metadata']['reasoning'] = line.replace('**Por que:**', '').strip()

        if current_pattern:
            chunks.append(current_pattern)

        return chunks

    def _extract_commands(self, content: str) -> List[Dict[str, Any]]:
        """Extract commands from COMMAND-HISTORY.md"""
        chunks = []
        lines = content.split('\n')
        current_command = {}

        for line in lines:
            if line.startswith('### [') and ('Command' in line or 'Erro' in line):
                if current_command:
                    chunks.append(current_command)
                current_command = {'type': 'command', 'content': '', 'metadata': {}}
                current_command['metadata']['title'] = line.replace('### ', '').strip()
                current_command['content'] += line + '\n'
            elif current_command and line.strip():
                current_command['content'] += line + '\n'
                # Extract command line
                if line.startswith('```bash'):
                    continue
                elif line.strip().startswith('#') or line.strip().startswith('sudo') or line.strip().startswith('git'):
                    current_command['metadata']['command'] = line.strip()
                elif line.startswith('**Regra aprendida:**'):
                    current_command['metadata']['rule'] = line.replace('**Regra aprendida:**', '').strip()

        if current_command:
            chunks.append(current_command)

        return chunks

    def _extract_general_knowledge(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract general knowledge from any file"""
        chunks = []

        # Split by sections (### headers)
        sections = content.split('\n### ')

        for i, section in enumerate(sections):
            if not section.strip():
                continue

            # Re-add the ### for the first section
            if i > 0:
                section = '### ' + section

            # Extract meaningful chunks
            lines = section.split('\n')

            # Skip if section is too short
            if len(lines) < 3:
                continue

            chunk_content = '\n'.join(lines)

            # Create knowledge chunk
            chunk = {
                'type': 'general_knowledge',
                'content': chunk_content,
                'metadata': {
                    'source_file': str(file_path.relative_to(self.PROJECT_ROOT)),
                    'section_count': len(lines),
                    'created_at': datetime.now().isoformat()
                }
            }

            # Extract title from first line
            first_line = lines[0].strip()
            if first_line.startswith('#'):
                chunk['metadata']['title'] = first_line.replace('#', '').strip()

            chunks.append(chunk)

        return chunks

    def add_knowledge_to_rag(self, knowledge_chunks: List[Dict[str, Any]]) -> int:
        """Add knowledge chunks to RAG"""
        added_count = 0

        for chunk in knowledge_chunks:
            try:
                # Generate ID from content hash
                content_hash = hashlib.md5(chunk['content'].encode()).hexdigest()[:12]

                # Generate embedding
                embedding = self.embedding_model.encode(chunk['content']).tolist()

                # Prepare metadata
                metadata = {
                    'type': chunk['type'],
                    'source': chunk['metadata'].get('source_file', 'unknown'),
                    'created_at': chunk['metadata'].get('created_at', datetime.now().isoformat()),
                    'content_preview': chunk['content'][:200] + '...' if len(chunk['content']) > 200 else chunk['content']
                }

                # Add all metadata
                metadata.update(chunk['metadata'])

                # Add to ChromaDB
                self.knowledge_collection.add(
                    ids=[f"auto_{content_hash}"],
                    embeddings=[embedding],
                    documents=[chunk['content']],
                    metadatas=[metadata]
                )

                added_count += 1
                logger.info(f"✅ Added {chunk['type']} chunk from {metadata.get('source', 'unknown')}")

            except Exception as e:
                logger.error(f"❌ Error adding chunk to RAG: {e}")

        return added_count

    def scan_and_update(self) -> Dict[str, int]:
        """Scan memory files and update RAG automatically"""
        logger.info("🔍 Starting automatic RAG update scan...")

        results = {
            'files_scanned': 0,
            'knowledge_chunks_extracted': 0,
            'chunks_added_to_rag': 0
        }

        # Scan all memory files
        memory_files = list(self.MEMORY_PATH.rglob("*.md"))
        memory_files.extend(list(self.MEMORY_PATH.rglob("*.txt")))

        for file_path in memory_files:
            try:
                logger.info(f"📖 Processing: {file_path.relative_to(self.PROJECT_ROOT)}")
                results['files_scanned'] += 1

                # Extract knowledge
                knowledge_chunks = self.extract_knowledge_from_file(file_path)
                results['knowledge_chunks_extracted'] += len(knowledge_chunks)

                # Add to RAG
                added = self.add_knowledge_to_rag(knowledge_chunks)
                results['chunks_added_to_rag'] += added

            except Exception as e:
                logger.error(f"❌ Error processing {file_path}: {e}")

        logger.info(f"✅ Scan complete: {results}")
        return results

    def save_session_to_rag(self, summary: str, tasks: List[str], learnings: List[str],
                           commands_used: List[str] = None, errors_solved: List[str] = None) -> str:
        """Save current session to RAG and session memory"""
        session_id = hashlib.md5(f"{datetime.now()}{summary}".encode()).hexdigest()[:12]

        try:
            # Create session content
            session_content = f"""Session Summary: {summary}
Tasks Completed: {len(tasks)} - {', '.join(tasks)}
Key Learnings: {len(learnings)} - {', '.join(learnings)}
Commands Used: {len(commands_used or [])} - {', '.join(commands_used or [])}
Errors Solved: {len(errors_solved or [])} - {', '.join(errors_solved or [])}
Session Date: {datetime.now().isoformat()}
"""

            # Generate embedding
            embedding = self.embedding_model.encode(session_content).tolist()

            # Add to RAG
            self.knowledge_collection.add(
                ids=[f"session_{session_id}"],
                embeddings=[embedding],
                documents=[session_content],
                metadatas=[{
                    'type': 'session',
                    'session_id': session_id,
                    'summary': summary,
                    'tasks_count': len(tasks),
                    'learnings_count': len(learnings),
                    'created_at': datetime.now().isoformat(),
                    'content_preview': session_content[:200] + '...'
                }]
            )

            # Also save to session memory (if available)
            if self.session_memory:
                self.session_memory.save_session(summary, tasks, learnings)

            logger.info(f"✅ Session saved to RAG: {session_id}")
            return session_id

        except Exception as e:
            logger.error(f"❌ Error saving session to RAG: {e}")
            return ""

    def search_knowledge(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge in RAG"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()

            # Search in ChromaDB
            results = self.knowledge_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )

            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })

            return formatted_results

        except Exception as e:
            logger.error(f"❌ Error searching RAG: {e}")
            return []

def main():
    """Main function for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description='RAG Auto-Learning System')
    parser.add_argument('--scan', action='store_true', help='Scan memory files and update RAG')
    parser.add_argument('--search', type=str, help='Search knowledge in RAG')
    parser.add_argument('--save-session', type=str, help='Save session to RAG')
    parser.add_argument('--stats', action='store_true', help='Show RAG statistics')

    args = parser.parse_args()

    rag = RAGAutoLearning()

    if args.scan:
        results = rag.scan_and_update()
        print(f"📊 Scan Results: {results}")

    elif args.search:
        results = rag.search_knowledge(args.search, n_results=3)
        print(f"🔍 Search Results for '{args.search}':")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['metadata'].get('title', result['metadata'].get('source', 'Unknown'))}")
            print(f"   Type: {result['metadata'].get('type', 'unknown')}")
            print(f"   Preview: {result['metadata'].get('content_preview', '')[:100]}...")

    elif args.save_session:
        session_id = rag.save_session_to_rag(
            summary=args.save_session,
            tasks=["Example task"],
            learnings=["Example learning"]
        )
        print(f"✅ Session saved: {session_id}")

    elif args.stats:
        count = rag.knowledge_collection.count()
        print(f"📊 RAG Statistics:")
        print(f"   Total knowledge chunks: {count}")
        print(f"   Collections: project_knowledge")

if __name__ == "__main__":
    main()