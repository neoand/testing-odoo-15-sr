# 🧠 Sistema de Memória de Longo Prazo - Claude Code

> **Propósito:** Garantir que NADA seja esquecido entre sessões. Todo erro, decisão, pattern e aprendizado fica registrado para sempre.

---

## 🎯 Visão Geral

Este diretório contém a **memória persistente** do projeto, automaticamente carregada pelo Claude Code em **toda sessão**.

### Problema Resolvido
❌ **Antes:** Claude perdia contexto entre sessões
✅ **Agora:** Tudo fica registrado e é carregado automaticamente

---

## 📂 Estrutura

```
.claude/memory/
├── README.md              (este arquivo)
│
├── context/              📋 CONTEXTO PERMANENTE
│   ├── projeto.md        - Informações do projeto
│   └── odoo.md          - Conhecimento Odoo específico
│
├── decisions/            📐 DECISÕES ARQUITETURAIS
│   └── ADR-INDEX.md     - Architecture Decision Records
│
├── errors/               🐛 ERROS E SOLUÇÕES
│   └── ERRORS-SOLVED.md - Histórico de erros resolvidos
│
├── patterns/             🎨 PADRÕES E BOAS PRÁTICAS
│   └── PATTERNS.md      - Padrões de código descobertos
│
├── odoo/                 🎓 CONHECIMENTO ODOO
│   └── (específico)     - Truques, hacks, soluções Odoo
│
└── learnings/            📚 APRENDIZADOS
    └── README.md        - Descobertas de pesquisas online
```

---

## 🚀 Como Usar

### Para Você (Humano)

**Adicionar Memória Rápida:**
1. No chat, digite: `#`
2. Escreva a memória
3. Enter
4. Claude adiciona ao arquivo correto

**Editar Memórias:**
```
/memory
```
Abre editor com todos os arquivos de memória.

**Ver Memórias Carregadas:**
```
/memory
```
Lista todos os arquivos sendo usados.

### Para Claude (Automático)

Claude carrega automaticamente:
1. `CLAUDE.md` (raiz)
2. Todos os arquivos referenciados com `@import`
3. Recursivamente até profundidade 5

---

## 📋 Quando Adicionar o Quê

### context/ - Informações Permanentes
- Estrutura do projeto
- Módulos instalados
- Configurações importantes
- Integrações ativas

**Exemplo:** "Database é PostgreSQL 13 em localhost:5432"

### decisions/ - Decisões Técnicas
- Escolhas arquiteturais
- Trade-offs considerados
- Alternativas rejeitadas
- Quando reavaliar

**Exemplo:** "Escolhemos Redis para cache porque..."

### errors/ - Bugs Resolvidos
- Erro encontrado
- Causa raiz
- Solução aplicada
- Como prevenir

**Exemplo:** "Permissões quebradas por override incorreto de write()"

### patterns/ - Código Exemplar
- Padrões de código
- Soluções elegantes
- Anti-patterns (o que evitar)
- Templates

**Exemplo:** "Sempre usar @api.depends com campos relacionados completos"

### learnings/ - Descobertas
- Pesquisas online
- Stack Overflow
- Documentação estudada
- Experimentos bem-sucedidos

**Exemplo:** "Descobri que Session do requests reduz latência em 40%"

---

## 🎨 Templates

### Erro Resolvido
```markdown
### [YYYY-MM-DD] Título do Erro

**Contexto:**
**Sintoma:**
**Causa Raiz:**
**Solução:**
**Prevenção:**
**Tags:** #tag1 #tag2
```

### Decisão Arquitetural (ADR)
```markdown
## ADR-XXX: Título

**Data:** YYYY-MM-DD
**Status:** 🔄 Proposto / ✅ Aceito

### Contexto
### Decisão
### Alternativas
### Consequências
```

### Learning
```markdown
### Título

**Data:** YYYY-MM-DD
**Fonte:** URL

**O que é:**
**Descoberta:**
**Impacto:**
**Aplicado em:**
```

---

## 💡 Boas Práticas

### ✅ FAZER

1. **Adicionar SEMPRE que:**
   - Resolver um erro
   - Tomar decisão importante
   - Descobrir algo útil
   - Encontrar solução elegante

2. **Ser ESPECÍFICO:**
   - "Use timeout de 30s na Kolmeya API"
   - NÃO "Use timeout adequado"

3. **Incluir CÓDIGO:**
   - Exemplos práticos
   - Antes/depois
   - Snippets reutilizáveis

4. **CONTEXTUALIZAR:**
   - Por que isso importa?
   - Onde se aplica?
   - Quando reavaliar?

5. **REVISAR periodicamente:**
   - Remover obsoleto
   - Atualizar mudanças
   - Consolidar duplicatas

### ❌ EVITAR

1. **Informação óbvia:**
   - "Python usa indentação" (todo mundo sabe)

2. **Detalhes excessivos:**
   - Histórico completo de commits
   - Discussões internas extensas

3. **Duplicação:**
   - Checar se já existe antes de adicionar

4. **Informação mutável:**
   - Senhas, tokens (use .env!)
   - IPs temporários
   - Dados de teste

---

## 🔄 Manutenção

### Diariamente
- Adicionar erros resolvidos
- Adicionar learnings de pesquisas
- Adicionar decisões tomadas

### Semanalmente
- Revisar e consolidar
- Atualizar contexto se mudou
- Adicionar patterns descobertos

### Mensalmente
- Limpar obsoleto
- Reorganizar se necessário
- Atualizar índices

---

## 📊 Estatísticas

**Criado em:** 2025-11-17
**Arquivos de memória:** 7
**Total de erros documentados:** 5
**Total de ADRs:** 4
**Total de patterns:** 15+
**Total de learnings:** 5

---

## 🎯 Objetivos

### Curto Prazo
- [x] Sistema de memória funcionando
- [x] Templates criados
- [x] Documentação completa
- [ ] 10+ erros documentados
- [ ] 10+ ADRs
- [ ] 20+ patterns

### Longo Prazo
- [ ] Knowledge base completa do projeto
- [ ] Zero erros repetidos
- [ ] Onboarding < 1 dia
- [ ] Claude 100% autônomo em tarefas comuns

---

## 🚀 Benefícios Esperados

### Para Desenvolvimento
- ✅ Erros nunca se repetem
- ✅ Decisões rastreáveis
- ✅ Padrões consistentes
- ✅ Código de qualidade

### Para Colaboração
- ✅ Onboarding rápido
- ✅ Contexto compartilhado
- ✅ Conhecimento institucional
- ✅ Autonomia crescente

### Para Claude
- ✅ Contexto permanente
- ✅ Aprendizado cumulativo
- ✅ Respostas mais precisas
- ✅ Velocidade crescente

---

## 📝 Próximos Passos

1. **Hoje:** Começar a usar! Adicione o próximo erro/learning
2. **Esta semana:** Documente 5+ erros já resolvidos
3. **Este mês:** Criar knowledge base completa

---

**Dúvidas?** Pergunte para Claude! Ele sabe como usar. 😊

**Contribua:** Toda adição de conhecimento beneficia o projeto!

---

**Sistema criado com ❤️ por Claude + Anderson**
**Versão:** 1.0
**Última atualização:** 2025-11-17
