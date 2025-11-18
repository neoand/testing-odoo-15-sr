#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: index-knowledge.py
Description: Indexa conhecimento em .claude/memory/ em ChromaDB com embeddings locais
             Otimizado para Mac M3 (Apple Silicon)
Usage: python3 index-knowledge.py [--reindex]
Author: Claude + Anderson
Created: 2025-11-18
"""

import chromadb
from sentence_transformers import SentenceTransformer
import os
import glob
import sys
from pathlib import Path
from datetime import datetime
import hashlib

# ====== CONFIGURAÇÃO ======
MEMORY_PATH = "./.claude/memory/**/*.md"
VECTORDB_PATH = "./.claude/vectordb"
MODEL_NAME = 'all-MiniLM-L6-v2'  # 384 dimensões, multilíngue

# Mac M3 optimizations
BATCH_SIZE = 64  # M3 tem memória rápida - processar mais de uma vez
NUM_THREADS = 8  # M3 tem 8 cores de performance

# ====== FUNÇÕES AUXILIARES ======

def get_file_hash(file_path):
    """Gera hash MD5 do arquivo para detectar mudanças"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def chunk_by_sections(content, file_path):
    """
    Divide markdown em seções (por ## headers)
    Estratégia: Cada seção = 1 chunk (melhor para RAG)
    """
    chunks = []
    lines = content.split('\n')

    current_section = ""
    current_header = "Introdução"
    section_number = 0

    for line in lines:
        if line.startswith('## '):  # Header nível 2
            # Salvar seção anterior
            if current_section.strip():
                chunks.append({
                    'content': current_section.strip(),
                    'header': current_header,
                    'section_number': section_number,
                    'file': file_path,
                    'char_count': len(current_section)
                })
                section_number += 1

            # Nova seção
            current_header = line.replace('## ', '').strip()
            current_section = line + '\n'

        elif line.startswith('### '):  # Subheader nível 3 (incluir no chunk)
            current_section += line + '\n'

        else:
            current_section += line + '\n'

    # Última seção
    if current_section.strip():
        chunks.append({
            'content': current_section.strip(),
            'header': current_header,
            'section_number': section_number,
            'file': file_path,
            'char_count': len(current_section)
        })

    return chunks

def extract_tags(content):
    """Extrai tags do formato #tag1 #tag2"""
    import re
    tags = re.findall(r'#(\w+)', content)
    return list(set(tags))  # Unique tags

# ====== INICIALIZAÇÃO ======

print("🚀 Iniciando indexação RAG - Otimizado para Mac M3")
print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Verificar se é reindexação
reindex = '--reindex' in sys.argv

if reindex:
    print("🔄 Modo REINDEXAÇÃO - apagando vector database anterior")
    import shutil
    if os.path.exists(VECTORDB_PATH):
        shutil.rmtree(VECTORDB_PATH)
    print("✅ Database anterior removida\n")

print("🔧 Inicializando ChromaDB e modelo de embeddings...")

# ChromaDB
client = chromadb.PersistentClient(path=VECTORDB_PATH)
collection = client.get_or_create_collection(
    name="project_knowledge",
    metadata={
        "description": "Conhecimento do projeto Odoo 15 - RAG Vector Database",
        "created": datetime.now().isoformat(),
        "model": MODEL_NAME
    }
)

# Modelo de embeddings (otimizado para M3)
print(f"📦 Carregando modelo: {MODEL_NAME}")
print("⚡ Detectando aceleração de hardware...")

# Mac M3 usa MPS (Metal Performance Shaders)
import torch
if torch.backends.mps.is_available():
    device = "mps"  # Apple Silicon GPU
    print("✅ GPU Apple M3 detectada - usando MPS (Metal)")
elif torch.cuda.is_available():
    device = "cuda"
    print("✅ CUDA detectada")
else:
    device = "cpu"
    print("⚠️  Usando CPU (sem aceleração)")

model = SentenceTransformer(MODEL_NAME, device=device)
print(f"✅ Modelo carregado em: {device}")
print(f"✅ ChromaDB em: {VECTORDB_PATH}\n")

# ====== INDEXAÇÃO ======

print("📚 Escaneando arquivos...")
files = sorted(glob.glob(MEMORY_PATH, recursive=True))
print(f"📊 Encontrados: {len(files)} arquivos\n")

total_chunks = 0
total_files = 0
total_chars = 0
skipped_files = 0

for file_path in files:
    try:
        file_name = Path(file_path).name

        # Ler arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Hash para detectar mudanças
        file_hash = get_file_hash(file_path)

        # Verificar se já indexado (skip se não mudou)
        existing_docs = collection.get(where={"file_path": file_path})
        if existing_docs['ids'] and not reindex:
            # Verificar hash
            old_hash = existing_docs['metadatas'][0].get('file_hash', '')
            if old_hash == file_hash:
                skipped_files += 1
                print(f"  ⏭️  {file_name}: não modificado, pulando")
                continue
            else:
                # Arquivo mudou - deletar chunks antigos
                collection.delete(where={"file_path": file_path})
                print(f"  🔄 {file_name}: arquivo modificado, reindexando")

        # Chunking
        chunks = chunk_by_sections(content, file_path)

        if not chunks:
            print(f"  ⚠️  {file_name}: sem conteúdo, pulando")
            continue

        # Gerar embeddings em batch (M3 optimization)
        print(f"  🔄 {file_name}: gerando embeddings para {len(chunks)} chunks...")
        texts = [chunk['content'] for chunk in chunks]

        # Batch encoding (mais rápido no M3)
        embeddings = model.encode(
            texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
            convert_to_numpy=True
        ).tolist()

        # Adicionar ao ChromaDB
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            doc_id = f"{Path(file_path).stem}_{i}_{file_hash[:8]}"

            # Extrair tags
            tags = extract_tags(chunk['content'])

            collection.add(
                embeddings=[embedding],
                documents=[chunk['content']],
                metadatas=[{
                    'file_path': file_path,
                    'file_name': file_name,
                    'header': chunk['header'],
                    'section_number': chunk['section_number'],
                    'char_count': chunk['char_count'],
                    'file_hash': file_hash,
                    'indexed_at': datetime.now().isoformat(),
                    'tags': ','.join(tags) if tags else ''
                }],
                ids=[doc_id]
            )

        total_chunks += len(chunks)
        total_chars += sum(c['char_count'] for c in chunks)
        total_files += 1
        print(f"  ✅ {file_name}: {len(chunks)} chunks indexados")

    except Exception as e:
        print(f"  ❌ Erro em {file_path}: {e}")

# ====== ESTATÍSTICAS ======

print(f"\n{'='*60}")
print("✅ INDEXAÇÃO COMPLETA!")
print(f"{'='*60}")
print(f"📊 Arquivos processados: {total_files}")
print(f"📊 Arquivos pulados (não modificados): {skipped_files}")
print(f"📊 Total de chunks: {total_chunks}")
print(f"📊 Total de caracteres: {total_chars:,}")
print(f"📊 Média chars/chunk: {total_chars//total_chunks if total_chunks > 0 else 0}")
print(f"📂 Vector database: {VECTORDB_PATH}")
print(f"💾 Tamanho database: {sum(f.stat().st_size for f in Path(VECTORDB_PATH).rglob('*') if f.is_file()) / 1024 / 1024:.2f} MB")
print(f"⚡ Device usado: {device.upper()}")

# ====== TESTE RÁPIDO ======

print(f"\n{'='*60}")
print("🧪 TESTE DE BUSCA")
print(f"{'='*60}")

test_queries = [
    "Como resolver erro de rede no Odoo?",
    "Comandos para reiniciar Odoo",
    "Patterns de performance Python"
]

for test_query in test_queries:
    print(f"\n📝 Pergunta: '{test_query}'")

    # Embedding da query
    query_embedding = model.encode(test_query).tolist()

    # Buscar
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    if results['documents'][0]:
        print("   Top 3 resultados:")
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
            print(f"   {i}. {metadata['file_name']} - {metadata['header']}")
            preview = doc[:80].replace('\n', ' ')
            print(f"      {preview}...")
    else:
        print("   ⚠️  Nenhum resultado encontrado")

print(f"\n{'='*60}")
print("🎉 RAG Vector Database pronto para uso!")
print(f"{'='*60}\n")
