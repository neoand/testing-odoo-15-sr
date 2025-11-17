# 📁 Diretório .claude/

Configuração Claude First para o projeto Odoo 15.

## 📂 Estrutura

```
.claude/
├── commands/           # Comandos slash personalizados
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
├── hooks/            # Hooks de automação (futuro)
│
├── PROJETO_CLAUDE_FIRST.md   # Documentação principal
├── GUIA_RAPIDO_CLAUDE.md     # Guia de uso rápido
└── README.md                  # Este arquivo
```

## 🎯 Como Usar

### Comandos Slash

Digite `/` seguido do comando na conversa com Claude:

- `/odoo-module` - Criar novo módulo
- `/odoo-model` - Criar modelo
- `/odoo-security` - Análise de segurança
- `/analyze` - Analisar código
- `/debug` - Debugar problemas
- `/refactor` - Refatorar código
- `/review` - Code review

### Templates

Use os templates em [templates/](templates/) como base para:
- Novos models Python
- Views XML
- Manifests de módulo

### Prompts

Prompts reutilizáveis em [prompts/](prompts/) para tarefas comuns.

## 📖 Documentação

- **[PROJETO_CLAUDE_FIRST.md](PROJETO_CLAUDE_FIRST.md)** - Filosofia e visão geral
- **[GUIA_RAPIDO_CLAUDE.md](GUIA_RAPIDO_CLAUDE.md)** - Guia prático de uso

## 🚀 Início Rápido

1. Leia: [GUIA_RAPIDO_CLAUDE.md](GUIA_RAPIDO_CLAUDE.md)
2. Experimente: `/analyze`
3. Desenvolva: "Adicione feature X"

## 🔧 Customização

Você pode adicionar seus próprios:
- Comandos em `commands/`
- Templates em `templates/`
- Prompts em `prompts/`
- Hooks em `hooks/`

## 📝 Notas

- Todos os arquivos em Markdown para fácil edição
- Comandos podem ter variáveis e lógica
- Templates seguem padrões Odoo 15
- Prompts são reutilizáveis

---

**Criado com Claude Code** 🤖
