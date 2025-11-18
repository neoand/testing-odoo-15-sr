# 🧠 RAG Setup - Project Knowledge

## Método 1: RAG Nativo Claude Projects (RECOMENDADO)

### Como Funciona

O Claude Projects tem RAG **built-in** que ativa automaticamente quando:
- Project knowledge se aproxima do limite de contexto (200K tokens)
- Expande capacidade até **10x** (2 milhões de tokens efetivos)
- **Sem configuração** - totalmente automático

### Setup em 3 Passos

**1. Organizar Conhecimento do Projeto**

Estrutura atual (já otimizada):
```
.claude/memory/
├── context/           # Contexto permanente
├── decisions/         # ADRs
├── errors/            # Erros resolvidos
├── patterns/          # Padrões descobertos
├── commands/          # Comandos aprendidos
├── learnings/         # Aprendizados profundos
└── tech-deep-dive/    # Tecnologias (PostgreSQL, OWL, etc)
```

**2. Nomenclatura Descritiva (CRÍTICO para RAG)**

✅ **BOM (RAG encontra facilmente):**
```
postgresql-mastery.md
owl-frontend-mastery.md
python-orm-performance-mastery.md
ERRORS-SOLVED.md
COMMAND-HISTORY.md
```

❌ **RUIM (RAG falha em encontrar):**
```
doc1.md
notes.md
temp.md
```

**3. Referências Explícitas nas Perguntas**

✅ **CORRETO:**
```
"Como resolver erro de rede conforme ERRORS-SOLVED.md seção http_interface?"
"Qual comando para GCP firewall segundo COMMAND-HISTORY.md?"
"Aplicar pattern de troubleshooting de PATTERNS.md"
```

❌ **ERRADO:**
```
"Como resolver erro de rede?"  # RAG pode não encontrar seção correta
```

### Validação de RAG Ativo

**Indicador visual:** Você verá ícone/badge mostrando "RAG enabled"

**Como testar:**
1. Adicionar muitos arquivos .md em .claude/memory/
2. Ultrapassar ~150K tokens de contexto
3. RAG ativa automaticamente
4. Claude consegue consultar TUDO

### Otimizações para RAG

**1. Chunking Estratégico:**

Dividir documentos grandes em seções lógicas:
```markdown
# Documento Grande

## Seção 1: PostgreSQL Performance
[Conteúdo específico]

## Seção 2: PostgreSQL Backup
[Conteúdo específico]

## Seção 3: PostgreSQL Replication
[Conteúdo específico]
```

**RAG consegue recuperar APENAS seção relevante!**

**2. Metadata em Headers:**

```markdown
# [ERRO-2025-11-18] Odoo Não Acessível - http_interface

**Tags:** #odoo #network #firewall #gcp
**Componentes:** http_interface, GCP firewall
**Resolução:** Configuração + Firewall
```

**RAG usa metadata para melhor ranking de relevância!**

**3. Links Internos:**

```markdown
Ver também:
- [COMMAND-HISTORY.md - GCP Firewall](../commands/COMMAND-HISTORY.md#gcp-firewall)
- [PATTERNS.md - Troubleshooting Rede](../patterns/PATTERNS.md#troubleshooting-rede)
```

**RAG segue links para contexto adicional!**

---

## Método 2: MCP Server RAG (Avançado)

### Quando Usar

- ✅ Precisa de embeddings customizados
- ✅ Quer controle fino sobre retrieval
- ✅ Integração com vector database externa

### Ferramentas Disponíveis

**1. ragmcp (GitHub: mr-dojo/ragmcp)**
- MCP server dedicado para RAG
- Usa embeddings locais
- Integra com Claude Desktop

**Setup:**
```bash
# 1. Instalar ragmcp
npm install -g @mr-dojo/ragmcp

# 2. Configurar .mcp.json
{
  "mcpServers": {
    "rag": {
      "command": "npx",
      "args": ["-y", "@mr-dojo/ragmcp", "--documents", "/Users/andersongoliveira/testing_odoo_15_sr/.claude/memory"]
    }
  }
}

# 3. Restart Claude Code
# RAG server estará disponível como tool
```

**2. Contextual Retrieval (Anthropic)**

Técnica avançada (reduz falhas 67%):
```python
# Pseudocódigo do que Anthropic faz internamente
def contextualize_chunk(chunk, document_context):
    prompt = f"""
    <document>
    {document_context}
    </document>

    Aqui está o chunk:
    <chunk>
    {chunk}
    </chunk>

    Forneça contexto sucinto (50-100 tokens) para situar este chunk
    dentro do documento geral para retrieval.
    """

    context = call_claude(prompt)
    return f"{context}\n\n{chunk}"

# Resultado: chunks com contexto prepended
# RAG encontra MUITO mais precisamente!
```

---

## Método 3: Local Vector Database (Máximo Controle)

### Arquitetura

```
Documentos (.md)
    ↓
Chunking (sentence-level)
    ↓
Embeddings (local model)
    ↓
Vector DB (ChromaDB/FAISS)
    ↓
Claude consulta via MCP
```

### Setup Completo

**1. Instalar dependências:**
```bash
pip install chromadb sentence-transformers
```

**2. Script de indexação:**
```python
# .claude/scripts/python/index-knowledge.py
import chromadb
from sentence_transformers import SentenceTransformer
import os
import glob

# Inicializar
client = chromadb.PersistentClient(path="./.claude/vectordb")
collection = client.get_or_create_collection("project_knowledge")
model = SentenceTransformer('all-MiniLM-L6-v2')  # Modelo local

# Indexar todos .md
memory_path = "./.claude/memory/**/*.md"
for file_path in glob.glob(memory_path, recursive=True):
    with open(file_path, 'r') as f:
        content = f.read()

    # Chunking por seção (## headers)
    chunks = content.split('\n## ')

    for i, chunk in enumerate(chunks):
        # Gerar embedding
        embedding = model.encode(chunk).tolist()

        # Adicionar ao vector DB
        collection.add(
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{"source": file_path, "chunk_id": i}],
            ids=[f"{file_path}_{i}"]
        )

print(f"✅ Indexados {collection.count()} chunks!")
```

**3. MCP Server para consulta:**
```python
# .claude/scripts/python/mcp_rag_server.py
from mcp import Server
import chromadb

server = Server("project-rag")
client = chromadb.PersistentClient(path="./.claude/vectordb")
collection = client.get_collection("project_knowledge")

@server.tool()
def search_knowledge(query: str, n_results: int = 5):
    """Busca conhecimento do projeto via RAG"""
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return {
        "documents": results['documents'][0],
        "sources": [m['source'] for m in results['metadatas'][0]]
    }

if __name__ == "__main__":
    server.run()
```

**4. Configurar MCP:**
```json
// .mcp.json
{
  "mcpServers": {
    "project-rag": {
      "command": "python",
      "args": [".claude/scripts/python/mcp_rag_server.py"]
    }
  }
}
```

---

## 📊 Comparação das Opções

| Aspecto | RAG Nativo | MCP ragmcp | Vector DB Local |
|---------|------------|------------|-----------------|
| **Setup** | ✅ Zero config | 🟡 npm install | 🔴 Complexo |
| **Performance** | 🟢 Ótimo | 🟢 Ótimo | 🟢 Excelente |
| **Controle** | 🔴 Limitado | 🟡 Médio | 🟢 Total |
| **Custo** | ✅ Grátis | ✅ Grátis | ✅ Grátis |
| **Manutenção** | ✅ Automático | 🟡 Manual | 🔴 Manual |
| **Recomendado?** | ✅ SIM | 🟡 Avançado | 🔴 Expert |

---

## 🎯 RECOMENDAÇÃO FINAL

**Para este projeto, usar MÉTODO 1 (RAG Nativo):**

✅ **Já está 90% pronto!**
- Estrutura .claude/memory/ organizada
- Nomenclatura descritiva
- Conteúdo bem estruturado (3200+ linhas)

**Próximos passos:**
1. ✅ Continuar adicionando conhecimento em .claude/memory/
2. ✅ Manter nomenclatura descritiva
3. ✅ Referenciar docs específicos nas perguntas
4. ✅ RAG ativa automaticamente quando necessário

**Quando migrar para Método 2/3:**
- Projeto ultrapassar 10 milhões de tokens
- Precisar embeddings customizados
- Integração com sistemas externos

---

**Criado:** 2025-11-18
**Baseado em:** Anthropic Contextual Retrieval, Claude Projects RAG, MCP ragmcp
**Status:** Método 1 ATIVO (automático)
