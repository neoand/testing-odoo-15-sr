#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Auto-Index System
Automatic file watching and reindexing for RAG knowledge base

Features:
- File watching for .claude/memory/**/*.md changes
- Auto-reindexing when files change
- Background daemon mode
- Batch processing optimizations
"""

import sys
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from concurrent.futures import ThreadPoolExecutor
import threading

# Add project root to path
script_path = Path(__file__).resolve()
PROJECT_ROOT = script_path.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "scripts" / "python"))

try:
    from rag_auto_learning import RAGAutoLearning
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RAGFileWatcher(FileSystemEventHandler):
    """Watch for file changes in .claude/memory and trigger RAG updates"""

    def __init__(self, rag_system):
        self.rag_system = rag_system
        self.last_index_time = 0
        self.batch_updates = []
        self.batch_timer = None
        self.executor = ThreadPoolExecutor(max_workers=4)

    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return

        # Only process .md and .txt files
        file_path = Path(event.src_path)
        if not file_path.suffix in ['.md', '.txt']:
            return

        # Only process files in .claude/memory or .claude/
        if not any(parent in file_path.parts for parent in ['.claude/memory', '.claude/']):
            return

        logger.info(f"📝 File changed: {file_path.relative_to(PROJECT_ROOT)}")
        self.schedule_update(file_path)

    def on_created(self, event):
        """Handle file creation events"""
        self.on_modified(event)

    def schedule_update(self, file_path):
        """Schedule batch update with debouncing"""
        self.batch_updates.append(file_path)

        # Cancel existing timer
        if self.batch_timer:
            self.batch_timer.cancel()

        # Schedule new timer (2 seconds delay for batching)
        self.batch_timer = threading.Timer(2.0, self.process_batch)
        self.batch_timer.start()

    def process_batch(self):
        """Process batch of file updates"""
        if not self.batch_updates:
            return

        logger.info(f"🔄 Processing batch update for {len(self.batch_updates)} files")

        # Get unique files
        unique_files = list(set(self.batch_updates))
        self.batch_updates = []

        # Process in background thread
        self.executor.submit(self.update_rag_for_files, unique_files)

    def update_rag_for_files(self, files):
        """Update RAG for specific files"""
        try:
            total_chunks = 0
            added_chunks = 0

            for file_path in files:
                logger.info(f"🔍 Processing: {file_path.relative_to(PROJECT_ROOT)}")

                # Extract knowledge
                knowledge_chunks = self.rag_system.extract_knowledge_from_file(file_path)
                total_chunks += len(knowledge_chunks)

                # Add to RAG
                added = self.rag_system.add_knowledge_to_rag(knowledge_chunks)
                added_chunks += added

            logger.info(f"✅ Batch update complete: {added_chunks}/{total_chunks} chunks added")

        except Exception as e:
            logger.error(f"❌ Error in batch update: {e}")

class RAGAutoIndexer:
    """Main RAG Auto-Indexer class"""

    def __init__(self):
        self.rag_system = RAGAutoLearning()
        self.observer = None
        self.event_handler = None

    def start_watching(self):
        """Start file watching daemon"""
        try:
            # Setup paths to watch
            memory_path = PROJECT_ROOT / ".claude" / "memory"
            claude_path = PROJECT_ROOT / ".claude"

            # Create event handler
            self.event_handler = RAGFileWatcher(self.rag_system)

            # Setup observer
            self.observer = Observer()

            # Watch .claude/memory directory
            if memory_path.exists():
                self.observer.schedule(self.event_handler, str(memory_path), recursive=True)
                logger.info(f"👀 Watching: {memory_path}")

            # Watch .claude directory (for new files)
            self.observer.schedule(self.event_handler, str(claude_path), recursive=False)
            logger.info(f"👀 Watching: {claude_path}")

            # Start observer
            self.observer.start()
            logger.info("🚀 RAG Auto-Indexer started successfully")

            return True

        except Exception as e:
            logger.error(f"❌ Error starting file watcher: {e}")
            return False

    def stop_watching(self):
        """Stop file watching daemon"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("🛑 RAG Auto-Indexer stopped")

    def initial_index(self):
        """Perform initial indexing of all existing files"""
        logger.info("🔍 Performing initial indexing...")

        results = self.rag_system.scan_and_update()
        logger.info(f"✅ Initial indexing complete: {results}")

        return results

    def run_daemon(self):
        """Run as daemon process"""
        logger.info("👻 Starting RAG Auto-Indexer daemon...")

        try:
            # Perform initial indexing
            self.initial_index()

            # Start file watching
            if self.start_watching():
                logger.info("✅ Daemon is watching for file changes...")

                # Keep running
                try:
                    while True:
                        time.sleep(60)  # Check every minute
                except KeyboardInterrupt:
                    logger.info("👋 Received interrupt signal")
                    self.stop_watching()
            else:
                logger.error("❌ Failed to start file watcher")

        except Exception as e:
            logger.error(f"❌ Daemon error: {e}")
        finally:
            self.stop_watching()

def main():
    """Main function for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description='RAG Auto-Indexer')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--index', action='store_true', help='Perform initial indexing')
    parser.add_argument('--stop', action='store_true', help='Stop running daemon')

    args = parser.parse_args()

    indexer = RAGAutoIndexer()

    if args.daemon:
        indexer.run_daemon()
    elif args.index:
        indexer.initial_index()
    elif args.stop:
        indexer.stop_watching()
    else:
        # Default: daemon mode
        indexer.run_daemon()

if __name__ == "__main__":
    main()