# 📁 Diretório .cursor/  

Configuração Cursor AI para o projeto Odoo 15.

> **Adaptado de:** `.claude/` para uso com Cursor IDE
> **Versão:** 1.0
> **Data:** 2025-11-19

## 📂 Estrutura

```
.cursor/
├── commands/           # Comandos personalizados para Cursor
│   ├── analyze.md
│   ├── debug.md
│   ├── odoo-module.md
│   ├── odoo-model.md
│   ├── odoo-security.md
│   ├── odoo-test.md
│   ├── refactor.md
│   └── review.md
│
├── prompts/           # Prompts reutilizáveis
│   └── code_review.md
│
├── templates/         # Templates de código
│   ├── manifest.py
│   ├── odoo_model.py
│   └── odoo_view.xml
│
├── hooks/            # Hooks de automação
│
├── memory/           # Memória persistente do projeto
│   ├── context/      # Contexto permanente
│   ├── decisions/    # Decisões arquiteturais (ADRs)
│   ├── errors/       # Erros resolvidos
│   ├── patterns/     # Padrões de código
│   ├── learnings/    # Aprendizados
│   ├── odoo/         # Conhecimento Odoo específico
│   └── protocols/    # Protocolos de trabalho
│
├── scripts/          # Scripts utilitários
│   ├── bash/         # Scripts bash
│   ├── python/       # Scripts Python
│   └── npm/          # Scripts npm
│
├── output-styles/    # Estilos de saída
├── skills/           # Skills especializadas
├── logs/             # Logs do sistema
└── vectordb/         # Vector database para RAG
```

## 🎯 Como Usar no Cursor

### Comandos no Chat

No chat do Cursor, você pode referenciar comandos:

- `@analyze` - Analisar código
- `@debug` - Debugar problemas
- `@odoo-module` - Criar novo módulo Odoo
- `@odoo-model` - Criar modelo Odoo
- `@odoo-security` - Análise de segurança
- `@refactor` - Refatorar código
- `@review` - Code review

### Templates

Use os templates em [templates/](templates/) como base para:
- Novos models Python
- Views XML
- Manifests de módulo

### Prompts

Prompts reutilizáveis em [prompts/](prompts/) para tarefas comuns.

### Memória Persistente

A pasta `memory/` contém conhecimento permanente:
- **context/**: Informações do projeto, Odoo, servidores
- **decisions/**: Decisões arquiteturais (ADRs)
- **errors/**: Histórico de erros resolvidos
- **patterns/**: Padrões de código descobertos
- **learnings/**: Aprendizados de pesquisas e experimentos
- **odoo/**: Conhecimento específico do Odoo 15
- **protocols/**: Protocolos de trabalho e automação

## 📖 Documentação

- **[CURSOR.md](../CURSOR.md)** - Configuração principal do Cursor
- **[memory/README.md](memory/README.md)** - Sistema de memória
- **[MANDATORY-PROTOCOL.md](MANDATORY-PROTOCOL.md)** - Protocolo obrigatório

## 🚀 Início Rápido

1. Leia: [CURSOR.md](../CURSOR.md)
2. Experimente: `@analyze` no chat
3. Desenvolva: "Adicione feature X"

## 🔧 Customização

Você pode adicionar seus próprios:
- Comandos em `commands/`
- Templates em `templates/`
- Prompts em `prompts/`
- Hooks em `hooks/`

## 🔄 Sincronização com .claude

Este diretório é uma adaptação do `.claude/` para uso com Cursor.

**Principais diferenças:**
- Comandos adaptados para sintaxe do Cursor
- Referências a "Claude" substituídas por "Cursor AI"
- Mantida compatibilidade com estrutura original

## 📝 Notas

- Todos os arquivos em Markdown para fácil edição
- Comandos podem ter variáveis e lógica
- Templates seguem padrões Odoo 15
- Prompts são reutilizáveis
- Memória é carregada automaticamente

---

**Criado com Cursor AI** 🤖  
**Adaptado de Claude Code** 🧠

