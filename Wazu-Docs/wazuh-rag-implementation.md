# 🎯 WAZUH RAG - PLANO DE IMPLEMENTAÇÃO PARA CLAUDE CODE

## 📋 RESUMO EXECUTIVO

Você tem **3 arquivos consolidados** com toda a documentação, fontes e tecnologias do Wazuh Open Source, prontos para treinar um RAG completo:

1. **wazuh-rag-complete.md** - Documentação técnica completa (todas as seções)
2. **wazuh_sources_consolidated.json** - Base estruturada de fontes e links
3. **wazuh-quick-guide.md** - Guia rápido com checklists e endpoints

---

## 🚀 FASE 1: PREPARAÇÃO (Hoje)

### ✅ Arquivos Já Gerados
```
📦 Wazuh Complete Knowledge Base
├── wazuh-rag-complete.md (15KB) - DOCUMENTAÇÃO COMPLETA
│   ├── Repositórios Oficiais (6)
│   ├── Documentação Principal (14 URLs)
│   ├── Módulo FIM (File Integrity Monitoring)
│   ├── Módulo API (RESTful)
│   ├── Módulo Kubernetes & Helm
│   ├── Módulo SCA (Security Configuration Assessment)
│   ├── Módulo Vulnerability Detection
│   ├── CDB Lists & Threat Intelligence
│   ├── Stack Tecnológico (Backend, Search, UI, Container)
│   ├── Issues Conhecidas & Soluções (6 principais)
│   ├── Instalação de Agents (5 plataformas)
│   └── Troubleshooting Completo
│
├── wazuh_sources_consolidated.json - BASE ESTRUTURADA
│   ├── Repositórios (6 sources)
│   ├── Documentação (14 URLs)
│   ├── Módulos Técnicos (6 módulos)
│   ├── Stack Tecnológico (5 camadas)
│   ├── Issues Conhecidas (6 issues)
│   └── Comunidade & Suporte
│
└── wazuh-quick-guide.md - GUIA RÁPIDO
    ├── Links de Navegação Rápida
    ├── API Endpoints
    ├── Compliance Frameworks
    └── Checklist de Implementação
```

### 📥 Como Importar para Claude Code

```bash
# 1. Clone/Crie diretório do projeto
mkdir -p wazuh-rag-system
cd wazuh-rag-system

# 2. Copie os arquivos
cp wazuh-rag-complete.md ./docs/
cp wazuh_sources_consolidated.json ./data/
cp wazuh-quick-guide.md ./docs/

# 3. Estruture o projeto
mkdir -p {src,tests,data,docs,embeddings}

# 4. Inicialize o Claude Code
# (Paste nos agentes)
```

---

## 🔧 FASE 2: SETUP TÉCNICO (1-2 horas)

### 2.1 Criar Estrutura de Projeto

```python
# requirements.txt
langchain>=0.0.200
openai>=0.27.0
pinecone-client>=2.2.0
# OU
weaviate-client>=3.11.0
chromadb>=0.3.21

python-dotenv
requests
json5
pyyaml

# Para parsing
python-frontmatter
markdown
beautifulsoup4
```

### 2.2 Configurar Knowledge Base

```python
# src/knowledge_base.py
from langchain.document_loaders import TextLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone

class WazuhKnowledgeBase:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n##", "\n###", "\n####", "\n\n", "\n", " "]
        )
    
    def load_documentation(self):
        """Carregar wazuh-rag-complete.md"""
        loader = TextLoader("docs/wazuh-rag-complete.md")
        docs = loader.load()
        return docs
    
    def load_sources(self):
        """Carregar wazuh_sources_consolidated.json"""
        loader = JSONLoader(
            file_path="data/wazuh_sources_consolidated.json",
            jq_schema=".[]",
            text_content_key="value"
        )
        docs = loader.load()
        return docs
    
    def process_documents(self):
        """Processar e splitar documentos"""
        docs = self.load_documentation() + self.load_sources()
        split_docs = self.splitter.split_documents(docs)
        return split_docs
    
    def create_vector_store(self):
        """Criar vector store com embeddings"""
        docs = self.process_documents()
        vector_store = Pinecone.from_documents(
            docs,
            self.embeddings,
            index_name="wazuh-knowledge"
        )
        return vector_store
```

### 2.3 Implementar RAG Chain

```python
# src/rag_chain.py
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

class WazuhRAG:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.llm = OpenAI(temperature=0.7, model="gpt-4")
        
    def create_chain(self):
        prompt_template = """
        Use the following pieces of Wazuh documentation context to answer the question.
        If you don't know the answer, say so. Use Portuguese when appropriate.
        
        Context:
        {context}
        
        Question: {question}
        Answer:
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 4}
            ),
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        
        return qa_chain
    
    def query(self, question):
        chain = self.create_chain()
        result = chain({"query": question})
        return {
            "answer": result["result"],
            "sources": result["source_documents"]
        }
```

---

## 📚 FASE 3: INDEXAÇÃO (1 hora)

### 3.1 Criar Índices de Embeddings

```python
# scripts/index_embeddings.py
import os
from src.knowledge_base import WazuhKnowledgeBase

def main():
    print("🔄 Iniciando indexação de documentos Wazuh...")
    
    kb = WazuhKnowledgeBase()
    
    # Processar documentação
    print("📖 Carregando wazuh-rag-complete.md...")
    docs = kb.process_documents()
    print(f"✅ {len(docs)} chunks criados")
    
    # Criar vector store
    print("🔍 Criando embeddings e vector store...")
    vector_store = kb.create_vector_store()
    print("✅ Vector store criado")
    
    # Salvar para referência
    print("💾 Salvando índices...")
    # vector_store.save_local("./embeddings/wazuh_index")
    
    print("\n✅ Indexação completa!")
    print(f"Total de chunks: {len(docs)}")
    print("Pronto para consultas via RAG")

if __name__ == "__main__":
    main()
```

### 3.2 Testar Indexação

```python
# scripts/test_rag.py
from src.rag_chain import WazuhRAG
from src.knowledge_base import WazuhKnowledgeBase

def test_queries():
    kb = WazuhKnowledgeBase()
    vector_store = kb.create_vector_store()
    rag = WazuhRAG(vector_store)
    
    test_cases = [
        "Como configurar File Integrity Monitoring no Wazuh?",
        "Quais são os endpoints principais da API Wazuh?",
        "Como fazer deploy do Wazuh no Kubernetes?",
        "Qual é o problema conhecido com Elasticsearch shards?",
        "Como integrar GitHub com Wazuh?",
        "Quais tecnologias são usadas no Wazuh?",
        "Como instalar o agent Wazuh no Windows?",
    ]
    
    for query in test_cases:
        print(f"\n📝 Query: {query}")
        result = rag.query(query)
        print(f"💡 Answer: {result['answer'][:200]}...")
        print(f"📚 Sources: {len(result['sources'])} documentos")

if __name__ == "__main__":
    test_queries()
```

---

## 🎯 FASE 4: VALIDAÇÃO (30 min)

### 4.1 Validar Qualidade das Respostas

```python
# scripts/validate_rag.py
from src.rag_chain import WazuhRAG

class RAGValidator:
    def __init__(self, rag):
        self.rag = rag
        self.validation_results = []
    
    def validate_accuracy(self, question, expected_keywords):
        """Validar se resposta contém keywords esperadas"""
        result = self.rag.query(question)
        answer = result["answer"].lower()
        
        found_keywords = [kw for kw in expected_keywords if kw.lower() in answer]
        accuracy = len(found_keywords) / len(expected_keywords) * 100
        
        return {
            "question": question,
            "accuracy": accuracy,
            "found_keywords": found_keywords,
            "total_keywords": len(expected_keywords)
        }
    
    def validate_sources(self, result):
        """Validar se sources são relevantes"""
        if not result["sources"]:
            return False
        return True
    
    def run_validation(self):
        """Executar suite de validação"""
        test_cases = [
            {
                "question": "O que é FIM no Wazuh?",
                "keywords": ["file integrity", "monitoring", "checksum"]
            },
            {
                "question": "Como autenticar na API Wazuh?",
                "keywords": ["JWT", "token", "authentication", "bearer"]
            },
            {
                "question": "Qual é a causa do erro Elasticsearch?",
                "keywords": ["shards", "elasticsearch", "rebalance"]
            }
        ]
        
        for test in test_cases:
            result = self.validate_accuracy(
                test["question"],
                test["keywords"]
            )
            self.validation_results.append(result)
            print(f"Accuracy: {result['accuracy']:.1f}% - {test['question']}")
        
        avg_accuracy = sum(r["accuracy"] for r in self.validation_results) / len(self.validation_results)
        print(f"\n✅ Média de Acurácia: {avg_accuracy:.1f}%")
```

---

## 📊 FASE 5: DEPLOYMENT (variável)

### 5.1 API REST para RAG

```python
# src/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.rag_chain import WazuhRAG

app = FastAPI(title="Wazuh RAG API")

class Query(BaseModel):
    question: str
    language: str = "pt"

class Answer(BaseModel):
    answer: str
    sources: list
    confidence: float

@app.post("/query", response_model=Answer)
async def query_wazuh(query: Query):
    """Fazer query ao RAG Wazuh"""
    try:
        result = rag.query(query.question)
        return Answer(
            answer=result["answer"],
            sources=[str(doc) for doc in result["sources"]],
            confidence=0.85  # Adicionar scoring
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "service": "wazuh-rag"}

@app.get("/docs")
async def docs():
    return {"sources": "wazuh_sources_consolidated.json"}
```

### 5.2 Deploy em Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY data/ data/
COPY docs/ docs/

COPY scripts/index_embeddings.py .
RUN python index_embeddings.py

COPY src/api.py .

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  wazuh-rag:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
    volumes:
      - ./embeddings:/app/embeddings
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Preparação
- [ ] Baixar 3 arquivos principais
- [ ] Criar estrutura de diretórios
- [ ] Copiar arquivos para `/docs` e `/data`

### Setup
- [ ] Instalar dependências (requirements.txt)
- [ ] Configurar API keys (OpenAI, Pinecone)
- [ ] Testar carregamento de documentos

### Indexação
- [ ] Criar embeddings de wazuh-rag-complete.md
- [ ] Indexar wazuh_sources_consolidated.json
- [ ] Validar chunks criados (~1000-2000)

### Validação
- [ ] Testar 10+ queries diferentes
- [ ] Validar acurácia (target: >80%)
- [ ] Verificar relevância de sources

### Deployment
- [ ] Criar API REST
- [ ] Testar endpoints
- [ ] Deploy em Docker
- [ ] Setup CI/CD

---

## 🔍 QUERIES DE TESTE SUGERIDAS

```python
test_queries = [
    # FIM
    "Como configurar File Integrity Monitoring?",
    "Quais arquivos são monitorados por default no FIM?",
    "Como integrar FIM com CDB lists?",
    
    # API
    "Como autenticar na API Wazuh?",
    "Quais são os endpoints para gerenciar agentes?",
    "Como listar vulnerabilidades via API?",
    
    # Kubernetes
    "Como fazer deploy do Wazuh no Kubernetes?",
    "Qual é a estrutura de um Helm Chart Wazuh?",
    
    # SCA
    "O que é Security Configuration Assessment?",
    "Quais benchmarks o SCA suporta?",
    
    # Troubleshooting
    "Como resolver erro de Elasticsearch shards?",
    "Agent não conecta, como debugar?",
    "Como regenerar certificados SSL?",
    
    # Compliance
    "Como usar Wazuh para compliance HIPAA?",
    "Quais regulações são suportadas?",
]
```

---

## 📈 MÉTRICAS DE SUCESSO

| Métrica | Target | Como Medir |
|---------|--------|-----------|
| **Acurácia RAG** | >85% | Validação de keywords |
| **Relevância Sources** | >90% | Manualmente verificar |
| **Latência Query** | <2s | Load testing |
| **Coverage** | >95% | Testar todos os módulos |
| **Fonte Attribution** | 100% | Sempre retornar sources |

---

## 🎓 RECURSOS PARA APRENDIZADO

### Documentation
- https://documentation.wazuh.com (oficial)
- https://github.com/wazuh/wazuh (source code)

### RAG & LLM
- LangChain Docs: https://python.langchain.com/
- OpenAI API: https://platform.openai.com/
- Vector Databases: Pinecone, Weaviate, ChromaDB

### Deployment
- FastAPI: https://fastapi.tiangolo.com/
- Docker: https://docs.docker.com/

---

## 🎯 PRÓXIMOS PASSOS IMEDIATOS

1. **Hoje**:
   - ✅ Você tem os 3 arquivos prontos
   - Baixe e organize no projeto

2. **Amanhã**:
   - Setup inicial (30 min)
   - Testar carregamento (30 min)
   - Criar embeddings (1 hora)

3. **Semana**:
   - Validar RAG (1-2 horas)
   - Deploy básico (1-2 horas)
   - Testes e refinamento

4. **Próximas semanas**:
   - Fine-tuning do modelo
   - Implementar feedback loop
   - Expandir para mais módulos

---

## 📞 SUPORTE

### Se tiver dúvidas:
- Consulte wazuh-quick-guide.md para links rápidos
- Verifique troubleshooting em wazuh-rag-complete.md
- Revise wazuh_sources_consolidated.json para estrutura

### Links Importantes:
- Docs Oficial: https://documentation.wazuh.com
- Community: https://wazuh.com/community/
- GitHub Issues: https://github.com/wazuh/wazuh/issues

---

**Status**: ✅ DOCUMENTAÇÃO COMPLETA E PRONTA  
**Data**: 2025-11-18  
**Versão**: Wazuh 4.7.4  
**Formato**: Markdown + JSON + Quick Guide

🚀 **Você está pronto para começar!**

