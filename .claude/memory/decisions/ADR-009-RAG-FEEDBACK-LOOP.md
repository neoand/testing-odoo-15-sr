# ADR-009: RAG Feedback Loop Architecture

**Data:** 2025-11-18
**Status:** ✅ Aceito e Implementado
**Decisores:** Anderson + Claude

---

## 🎯 Contexto

Após implementar RAG Vector Database (ADR anterior), identificamos que o RAG era apenas **consultivo** - ele buscava informação mas não aprendia com o uso.

**Problema:** Como tornar o RAG mais inteligente a cada consulta?

**Necessidade:** Sistema de feedback loop que:
- Registre todas as queries
- Identifique gaps de documentação (queries sem resultado)
- Sugira melhorias baseadas em uso real
- Aprenda continuamente

---

## 🤔 Decisão

Implementar **RAG Feedback Loop completo** com 4 componentes:

### 1. Query Logger
- Registra TODAS as queries em `.claude/logs/rag-queries.jsonl`
- Formato JSONL (JSON Lines) - cada linha = 1 query
- Metadados: query_id, timestamp, query, results_count, top_result, metadata

### 2. Relevance Tracker
- Registra feedback de usuários em `.claude/logs/rag-feedback.jsonl`
- Permite marcar resultados como relevant/irrelevant
- Taxa de relevância calculada

### 3. Analytics Dashboard
- Script `rag-analytics-dashboard.py`
- Métricas: total queries, avg results, zero-result rate, top queries
- Queries por data (histograma)
- Sugestões automáticas de documentação

### 4. Auto-Documentation Suggester
- Analisa queries com zero results
- Sugere arquivos para documentar
- Lista prioritária de gaps

---

## 🔀 Alternativas Consideradas

### Alternativa 1: Embeddings Fine-tuning Automático
**Descrição:** Ajustar embeddings baseado em feedback

**Prós:**
- Melhoria contínua de precisão
- RAG "aprende" semanticamente

**Contras:**
- Complexidade MUITO alta
- Requires ML pipeline
- Overhead computacional
- Pode piorar embeddings se poucos dados

**Decisão:** ❌ Não implementar agora. Futuro se volume > 10k queries

### Alternativa 2: Simple Counter (Apenas Contar Queries)
**Descrição:** Apenas contar queries, sem estrutura

**Prós:**
- Simples
- Baixo overhead

**Contras:**
- Não identifica gaps
- Sem feedback loop real
- Sem aprendizado

**Decisão:** ❌ Insuficiente

### Alternativa 3: Feedback Loop Completo (ESCOLHIDO)
**Descrição:** Query logger + Relevance tracker + Analytics + Auto-suggestions

**Prós:**
- ✅ Identifica gaps automaticamente
- ✅ Métricas acionáveis
- ✅ Sugestões concretas
- ✅ Baixa complexidade
- ✅ Escalável (JSONL append-only)
- ✅ Zero overhead em runtime
- ✅ Analytics on-demand

**Contras:**
- Requer discipline para agir nas sugestões
- Logs crescem indefinidamente (mitigation: cleanup policy)

**Decisão:** ✅ **ESCOLHIDO**

---

## 📊 Arquitetura Implementada

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG FEEDBACK LOOP                        │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   User       │────▶│  test-rag.py │────▶│  ChromaDB        │
│   Query      │     │              │     │  Vector Search   │
└──────────────┘     └───────┬──────┘     └─────────┬────────┘
                             │                      │
                             │                      ▼
                             │                   Results
                             │                      │
                             ▼                      ▼
                   ┌──────────────────────────────────────┐
                   │  rag_query_logger.py                 │
                   │  log_query(query, results, metadata) │
                   └──────────────┬───────────────────────┘
                                  │
                        ┌─────────┴────────┐
                        │                  │
                        ▼                  ▼
              ┌──────────────────┐  ┌──────────────────┐
              │ rag-queries.jsonl │  │ rag-feedback.jsonl│
              │ (All queries)     │  │ (User ratings)    │
              └────────┬───────────┘  └───────┬──────────┘
                       │                      │
                       └──────────┬───────────┘
                                  │
                                  ▼
                   ┌────────────────────────────────┐
                   │  rag-analytics-dashboard.py    │
                   │  - Query stats                 │
                   │  - Zero-result detection       │
                   │  - Documentation suggestions   │
                   │  - Actionable insights         │
                   └────────────────────────────────┘
```

---

## 💡 Decisões Técnicas Detalhadas

### 1. Formato de Log: JSONL

**Por que JSONL e não JSON array ou CSV?**

✅ **JSONL (escolhido):**
```jsonl
{"query_id": "abc123", "query": "test", "results_count": 5}
{"query_id": "def456", "query": "another", "results_count": 3}
```
- Append-only (O(1) write)
- Cada linha independente (não corrompe arquivo se falhar)
- Fácil processar line-by-line
- Standard para logs estruturados

❌ **JSON Array:**
```json
[
  {"query_id": "abc123", ...},
  {"query_id": "def456", ...}
]
```
- Precisa reescrever arquivo inteiro para adicionar
- Arquivo corrompe se falhar no meio
- Não escalável

❌ **CSV:**
```csv
query_id,query,results_count
abc123,test,5
def456,another,3
```
- Difícil com nested data (metadata, top_result)
- Escape complexo (queries com vírgulas)
- Sem tipagem

### 2. Localização dos Logs

**Decisão:** `.claude/logs/`

**Por quê:**
- Separado de vectordb (concerns diferentes)
- Gitignore (logs não vão para repo)
- Fácil limpar periodicamente
- Padrão de projetos

### 3. Query ID: Hash MD5 (12 chars)

**Por quê:**
- Único (colisão ~impossível para volume)
- Curto (12 chars suficiente)
- Rastreável
- Link query ↔ feedback

```python
query_id = hashlib.md5(
    f"{query}{datetime.now().isoformat()}".encode()
).hexdigest()[:12]
```

### 4. Metadata Flexível

**Decisão:** Campo `metadata` dict livre

**Por quê:**
- Extensível sem breaking changes
- Device info (MPS, CUDA, CPU)
- Timing info (futuro)
- User context (futuro)

### 5. Analytics On-Demand (Não Real-Time)

**Decisão:** `generate_analytics()` manual

**Por quê:**
- Zero overhead em queries
- Analytics quando necessário
- Pode rodar em cron (futuro: diário)

**Alternativa rejeitada:** Real-time dashboard
- Overhead em cada query
- Complexidade alta
- Desnecessário para uso atual

---

## 🚀 Implementação

### Arquivos Criados

1. **`rag_query_logger.py`** (core module)
   - `log_query()` - Registra query
   - `log_feedback()` - Registra feedback
   - `get_query_stats()` - Estatísticas de queries
   - `get_feedback_stats()` - Estatísticas de feedback
   - `generate_analytics()` - Gera JSON completo
   - `suggest_documentation()` - Sugere docs para gaps

2. **`rag-analytics-dashboard.py`** (visualization)
   - Dashboard colorido no terminal
   - Métricas gerais
   - Top queries
   - Zero-result queries
   - Queries por data (histogram)
   - Insights automáticos
   - Ações sugeridas

3. **`test-rag.py`** (modificado)
   - Importa rag_query_logger
   - Chama `log_query()` após cada busca
   - Feedback visual: "📊 Query logged (ID: xxx)"

### Estrutura de Dados

**rag-queries.jsonl:**
```json
{
  "query_id": "a9baf4e1a6d4",
  "timestamp": "2025-11-18T00:45:23.123456",
  "query": "RAG feedback loop",
  "results_count": 5,
  "top_result": {
    "file": "TECHNOLOGY-360-INDEX.md",
    "header": "📚 CONHECIMENTO ADQUIRIDO",
    "rerank_score": -10.7268,
    "distance": 1.6788
  },
  "metadata": {
    "device": "mps",
    "n_results": 5
  }
}
```

**rag-feedback.jsonl:**
```json
{
  "query_id": "a9baf4e1a6d4",
  "timestamp": "2025-11-18T00:46:00.000000",
  "relevant": true,
  "notes": "Encontrou exatamente o que procurava"
}
```

**rag-analytics.json:**
```json
{
  "generated_at": "2025-11-18T00:50:00.000000",
  "query_stats": {
    "total_queries": 42,
    "avg_results": 4.2,
    "zero_results_queries": [
      {"query": "odoo 18 features", "timestamp": "..."}
    ],
    "top_queries": {
      "rag setup": 5,
      "performance tuning": 3
    },
    "queries_by_date": {
      "2025-11-18": 42
    }
  },
  "feedback_stats": {
    "total_feedback": 10,
    "relevant_count": 8,
    "irrelevant_count": 2,
    "relevance_rate": 80.0
  }
}
```

---

## 📈 Métricas de Sucesso

### Objetivos

1. **Taxa de Zero Results < 10%**
   - Se > 10%: Expandir documentação
   - Se > 20%: Gap crítico

2. **Taxa de Relevância > 80%**
   - Se < 80%: Ajustar reranking ou embeddings
   - Se < 60%: Problema crítico no RAG

3. **Top Queries Identificadas**
   - Queries frequentes (>5x) = criar docs dedicadas
   - Tópicos emergentes = priorizar documentação

4. **Feedback Loop Ativo**
   - Sugestões automaticamente geradas
   - Action items claros

### Dashboard de Exemplo

```
======================================================================
📊 RAG ANALYTICS DASHBOARD
======================================================================

📈 MÉTRICAS GERAIS
----------------------------------------------------------------------
  Total de queries: 42
  Média de resultados: 4.20
  Queries sem resultado: 3
  Feedback total: 10
  Taxa de relevância: 80.0%

🔥 TOP QUERIES (Mais Frequentes)
----------------------------------------------------------------------
  1. (5x) rag setup
  2. (3x) performance tuning
  3. (2x) postgresql optimization

⚠️  QUERIES SEM RESULTADO (Últimas 5)
----------------------------------------------------------------------
  1. odoo 18 features
     Timestamp: 2025-11-18T00:45:00

💡 SUGESTÕES DE DOCUMENTAÇÃO
----------------------------------------------------------------------
  Encontramos 3 queries sem resultado!
  Considere documentar sobre:

  1. "odoo 18 features"
     → Sugerido: PATTERNS.md ou learnings/ apropriado

🎯 INSIGHTS & RECOMENDAÇÕES
----------------------------------------------------------------------
  ✅ Taxa de queries sem resultado: 7.1%
      → Documentação está cobrindo bem as queries!
  ✅ Taxa de relevância: 80.0%
      → RAG está performando bem!

🚀 AÇÕES SUGERIDAS
----------------------------------------------------------------------
  1. Documentar 3 tópicos sem cobertura
  2. Criar documentação dedicada para "rag setup" (query frequente)

💾 Analytics salvo em: .claude/logs/rag-analytics.json
📝 Query log: .claude/logs/rag-queries.jsonl
📊 Feedback log: .claude/logs/rag-feedback.jsonl
```

---

## ✅ Consequências

### Positivas

- ✅ **RAG aprende automaticamente** - identifica gaps sem intervenção
- ✅ **Métricas acionáveis** - sabe exatamente onde melhorar
- ✅ **Zero overhead** - logging assíncrono, analytics on-demand
- ✅ **Escalável** - JSONL append-only, fácil processar milhões de linhas
- ✅ **Insights automáticos** - dashboard mostra problemas e soluções
- ✅ **Feedback visual** - usuário vê query ID ao buscar
- ✅ **Histórico completo** - todas queries salvas para análise futura

### Negativas

- ⚠️ **Logs crescem indefinidamente** - precisa cleanup policy (futuro)
  - Mitigation: Rotate logs mensalmente, arquivar old logs
- ⚠️ **Requer discipline** - sugestões precisam ser implementadas
  - Mitigation: Revisar analytics semanalmente, priorizar top suggestions

### Neutras

- 📝 Feedback manual (usuário precisa chamar `log_feedback()`)
  - Futuro: Prompt ao final de cada busca "Resultado foi relevante?"
- 📝 Analytics não é real-time
  - Suficiente para uso atual, pode adicionar real-time dashboard se necessário

---

## 🔄 Quando Reavaliar

### Triggers para Revisão

1. **Volume > 1000 queries/dia**
   - Considerar analytics real-time
   - Considerar embeddings fine-tuning

2. **Taxa zero results > 15% consistente**
   - Problema estrutural de documentação
   - Reavaliar chunking strategy

3. **Taxa relevância < 70% consistente**
   - Problema com reranking ou embeddings
   - Considerar modelo diferente

4. **Logs > 1GB**
   - Implementar rotation e archival
   - Considerar database (SQLite/PostgreSQL) ao invés de JSONL

---

## 🔗 Integrações

### Com Outros Componentes

- **ADR-005 (LLM-First Tools):** Analytics dashboard é script reutilizável
- **ADR-007 (Performance):** Logging assíncrono, zero impacto
- **RAG Vector Database:** Query logger integrado em `test-rag.py`

### Futuras Integrações

- **MCP RAG Server:** Logging automático de queries via MCP
- **Cron Job:** Analytics diário automático
- **Slack/Email Notifications:** Alertas se métricas degradam

---

## 📚 Referências

- [JSONL Specification](http://jsonlines.org/)
- [Feedback Loops in ML Systems](https://developers.google.com/machine-learning/crash-course/production-ml-systems)
- RAG Best Practices 2025

---

## 📊 Comparação: Antes vs Depois

| Aspecto | Antes (RAG Simples) | Depois (Feedback Loop) |
|---------|---------------------|------------------------|
| **Aprendizado** | ❌ Nenhum | ✅ Contínuo |
| **Gaps visíveis** | ❌ Não | ✅ Sim (zero-result queries) |
| **Métricas** | ❌ Nenhuma | ✅ Completas |
| **Ações** | ❌ Manual guess | ✅ Data-driven |
| **Histórico** | ❌ Perdido | ✅ Completo (JSONL) |
| **Melhoria** | ❌ Ad-hoc | ✅ Sistemática |

---

**Status Final:** ✅ Implementado e Testado
**Próxima Revisão:** Quando atingir 1000 queries
**Responsável:** Claude (analytics) + Anderson (ações)

**Criado:** 2025-11-18
**Última Atualização:** 2025-11-18
