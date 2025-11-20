#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: file-watcher.py
Description: File watcher para reindexação instantânea quando arquivos .md mudam
Usage: python3.11 file-watcher.py (roda em background)
Author: Claude + Anderson
Created: 2025-11-18
"""

import time
import os
import hashlib
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ====== CONFIGURAÇÃO ======
script_path = Path(__file__).resolve()
PROJECT_ROOT = script_path.parent.parent.parent.parent
WATCH_DIR = str(PROJECT_ROOT / ".claude" / "memory")
INDEX_SCRIPT = str(PROJECT_ROOT / ".claude" / "scripts" / "python" / "index-knowledge.py")
DEBOUNCE_SECONDS = 5  # Esperar 5s após mudança antes de reindexar

# ====== FILE WATCHER ======

class MarkdownFileHandler(FileSystemEventHandler):
    """Handler para mudanças em arquivos .md"""

    def __init__(self):
        self.last_reindex = {}
        self.pending_reindex = set()

    def on_modified(self, event):
        if event.is_directory:
            return

        # Apenas arquivos .md
        if not event.src_path.endswith('.md'):
            return

        file_path = event.src_path
        current_time = time.time()

        # Debounce: evitar múltiplos reindex do mesmo arquivo
        last_time = self.last_reindex.get(file_path, 0)
        if current_time - last_time < DEBOUNCE_SECONDS:
            return

        print(f"📝 Arquivo modificado: {os.path.basename(file_path)}")
        self.pending_reindex.add(file_path)
        self.last_reindex[file_path] = current_time

        # Agendar reindex após debounce
        self.schedule_reindex(file_path)

    def on_created(self, event):
        if event.is_directory:
            return

        if not event.src_path.endswith('.md'):
            return

        print(f"➕ Novo arquivo: {os.path.basename(event.src_path)}")
        self.pending_reindex.add(event.src_path)
        self.schedule_reindex(event.src_path)

    def on_deleted(self, event):
        if event.is_directory:
            return

        if not event.src_path.endswith('.md'):
            return

        print(f"🗑️  Arquivo removido: {os.path.basename(event.src_path)}")
        # Reindexar tudo para remover chunks do arquivo deletado
        self.trigger_full_reindex()

    def schedule_reindex(self, file_path):
        """Agenda reindex após debounce"""
        # Esperar debounce period
        time.sleep(DEBOUNCE_SECONDS)

        if file_path in self.pending_reindex:
            self.trigger_incremental_reindex(file_path)
            self.pending_reindex.discard(file_path)

    def trigger_incremental_reindex(self, file_path):
        """Reindexar apenas arquivo específico (incremental)"""
        print(f"🔄 Reindexando: {os.path.basename(file_path)}...")

        try:
            # Rodar index-knowledge.py para reindexar
            result = subprocess.run(
                ['python3.11', INDEX_SCRIPT],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print(f"✅ Reindexação completa!")
            else:
                print(f"❌ Erro na reindexação: {result.stderr[:200]}")

        except subprocess.TimeoutExpired:
            print("⏱️  Timeout na reindexação (>60s)")
        except Exception as e:
            print(f"❌ Erro: {e}")

    def trigger_full_reindex(self):
        """Reindexar tudo (quando arquivo é deletado)"""
        print("🔄 Reindexação completa (arquivo deletado)...")

        try:
            result = subprocess.run(
                ['python3.11', INDEX_SCRIPT, '--reindex'],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                print("✅ Reindexação completa!")
            else:
                print(f"❌ Erro: {result.stderr[:200]}")

        except subprocess.TimeoutExpired:
            print("⏱️  Timeout (>120s)")
        except Exception as e:
            print(f"❌ Erro: {e}")

# ====== MAIN ======

if __name__ == "__main__":
    print("🔍 File Watcher - RAG Instant Reindexing")
    print("=" * 60)
    print(f"📂 Watching: {WATCH_DIR}")
    print(f"📄 Pattern: *.md files")
    print(f"⏱️  Debounce: {DEBOUNCE_SECONDS}s")
    print(f"🔄 Index script: {os.path.basename(INDEX_SCRIPT)}")
    print("✅ Ready! Press Ctrl+C to stop\n")

    event_handler = MarkdownFileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping file watcher...")
        observer.stop()

    observer.join()
    print("✅ File watcher stopped")
