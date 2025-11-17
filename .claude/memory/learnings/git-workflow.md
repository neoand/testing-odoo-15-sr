# 🔀 Git Workflow - Anti-Rebase Configuration

**Data:** 2025-11-17
**Autor:** Claude + Anderson
**Status:** ✅ Implementado e Testado

---

## 🎯 Objetivo

Workflow Git **simples, seguro e sem rebases** para evitar travamentos e complexidade.

**Princípio:** MERGE > REBASE (sempre!)

---

## ⚙️ Configuração Aplicada

### Anti-Rebase Settings

```bash
# NUNCA fazer rebase ao fazer pull
git config pull.rebase false

# SEMPRE criar merge commit (nunca fast-forward)
git config merge.ff false

# Push apenas branch atual
git config push.default simple

# Line endings normalizados (LF no repo)
git config core.autocrlf input
```

### Performance Optimizations

```bash
git config core.preloadindex true  # Carrega índice em paralelo
git config core.fscache true       # Cache de filesystem
git config gc.auto 256             # Garbage collection automático
git config pack.threads 0          # Usa todos CPUs para pack
```

---

## 📋 Comandos Comuns

### Workflow Diário

```bash
# 1. Ver status atual
git status

# 2. Adicionar mudanças
git add .                    # Todos os arquivos
git add arquivo.py           # Arquivo específico
git add *.py                 # Pattern

# 3. Commit com mensagem
git commit -m "feat: descrição da mudança"

# 4. Puxar mudanças do remoto (com merge, SEM rebase)
git pull origin main

# 5. Resolver conflitos se houver
# Editar arquivos conflitantes
git add arquivo-resolvido.py
git commit -m "merge: resolve conflicts"

# 6. Push para remoto
git push origin main
```

### Verificação de Configuração

```bash
# Ver todas as configs
git config --list

# Ver configs anti-rebase
git config pull.rebase        # Deve ser: false
git config merge.ff           # Deve ser: false
git config push.default       # Deve ser: simple

# Ver histórico
git log --oneline --graph --all -10
```

### Branches

```bash
# Criar nova branch
git checkout -b feature/nova-funcionalidade

# Mudar de branch
git checkout main

# Listar branches
git branch -a

# Merge de branch (SEM REBASE!)
git checkout main
git merge feature/nova-funcionalidade   # Cria merge commit
git push origin main
```

### Remoto

```bash
# Ver remotos configurados
git remote -v

# Adicionar remoto
git remote add origin https://github.com/neoand/testing-odoo-15-sr.git

# Mudar URL do remoto
git remote set-url origin https://github.com/neoand/testing-odoo-15-sr.git

# Push com upstream tracking
git push -u origin main
```

---

## ✅ Verificação de Saúde

Execute regularmente para garantir que está tudo OK:

```bash
#!/bin/bash
# git-health-check.sh

echo "🔍 Git Health Check"
echo "==================="
echo ""

echo "1. Configuração Anti-Rebase:"
echo "  pull.rebase: $(git config pull.rebase)"
echo "  merge.ff: $(git config merge.ff)"
echo "  push.default: $(git config push.default)"
echo ""

echo "2. Status do Repositório:"
git status --short
echo ""

echo "3. Branches:"
git branch -a
echo ""

echo "4. Remotos:"
git remote -v
echo ""

echo "5. Últimos 5 Commits:"
git log --oneline --graph -5
echo ""

echo "✅ Health check completo!"
```

---

## 🚨 Troubleshooting

### Problema: "Pull com divergências"

```bash
# NÃO fazer rebase!
# Sempre usar merge:

git pull origin main
# Se houver conflitos:
# 1. Editar arquivos marcados
# 2. git add arquivo-resolvido.py
# 3. git commit -m "merge: resolve conflicts"
# 4. git push origin main
```

### Problema: "Push rejeitado"

```bash
# Alguém fez push antes de você
# Solução: Pull com merge, depois push

git pull origin main   # Faz merge automaticamente
git push origin main
```

### Problema: "Mudanças não commitadas"

```bash
# Salvar mudanças temporariamente
git stash

# Fazer pull
git pull origin main

# Restaurar mudanças
git stash pop
```

### Problema: "Arquivo muito grande"

```bash
# Git não gosta de arquivos > 100MB
# Solução: Adicionar ao .gitignore

echo "arquivo-grande.dump" >> .gitignore
git add .gitignore
git commit -m "chore: ignore large file"
```

---

## 📖 Convenções de Commit

Seguir padrão [Conventional Commits](https://www.conventionalcommits.org/):

```
tipo(escopo): descrição curta

Descrição detalhada (opcional)

BREAKING CHANGE: se houver mudança que quebra compatibilidade
```

**Tipos:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação, ponto e vírgula
- `refactor`: Refatoração de código
- `test`: Adicionar testes
- `chore`: Manutenção, configs

**Exemplos:**
```bash
git commit -m "feat(crm): add SMS integration with Kolmeya API"
git commit -m "fix(chatroom): resolve message duplication bug"
git commit -m "docs(readme): update installation instructions"
git commit -m "chore(deps): upgrade Odoo to 15.0-20231201"
```

---

## 🔐 .gitignore Configurado

Principais exclusões para Odoo:

```gitignore
# Odoo Específico
filestore/
sessions/
*.log
backups/
addons/*/

# Credenciais
.env
.env.*
*.pem
*.key
credentials.json
odoo.conf
odoo-server.conf

# IDE
.vscode/
.idea/

# Python
__pycache__/
*.pyc

# OS
.DS_Store
Thumbs.db
```

**Exceções importantes:**
```gitignore
# INCLUIR sempre:
!.gitignore
!.clauderc
!.mcp.json
!CLAUDE.md
```

---

## 📊 Estatísticas Iniciais

**Primeiro Commit:**
- **Commit Hash:** `2480b07`
- **Data:** 2025-11-17
- **Arquivos:** 5734
- **Mensagem:** "Initial commit: Odoo 15 Testing + LLM-First Tools v2.0"

**Remoto Configurado:**
- **GitHub:** https://github.com/neoand/testing-odoo-15-sr.git
- **Branch Principal:** `main`
- **Upstream:** `origin/main`

---

## 🎓 Lições Aprendidas

1. **NUNCA usar rebase** - Merge é mais simples e rastreável
2. **Sempre criar merge commits** (`merge.ff=false`) - Histórico claro
3. **Git config é seu amigo** - Configure uma vez, use sempre
4. **Commits atômicos** - Um commit = uma mudança lógica
5. **Mensagens descritivas** - Facilita code review
6. **Pull antes de push** - Evita conflitos
7. **.gitignore robusto** - Protege credenciais e mantém repo limpo

---

## 🔗 Integração com MCPs

Com MCP Git instalado, Claude pode:

```bash
# Automático via MCP
- Verificar status: git status
- Ver mudanças: git diff
- Criar commits: git commit -m "..."
- Criar branches: git checkout -b feature/x
- Merge automático: git merge --no-ff
```

Com MCP GitHub instalado, Claude pode:

```bash
# Automático via MCP
- Criar Pull Requests
- Listar PRs e Issues
- Comentar em PRs
- Merge de PRs
- Ver status de CI/CD
```

**Workflow Completo Automatizado:**
1. Claude faz mudanças no código
2. MCP Git: verifica diff e cria commit
3. MCP Git: push para origin
4. MCP GitHub: cria Pull Request
5. MCP GitHub: adiciona reviewers
6. ✅ Pronto para review!

---

## 🚀 Próximos Passos

- [ ] Push inicial para GitHub: `git push -u origin main`
- [ ] Verificar se MCP GitHub precisa autenticação
- [ ] Criar primeiro PR via MCP
- [ ] Configurar branch protection rules no GitHub
- [ ] Configurar GitHub Actions para CI/CD (opcional)

---

**Última atualização:** 2025-11-17
**Localização:** `.claude/memory/learnings/git-workflow.md`
**Referências:**
- [ADR-005: Arquitetura LLM-First Tools](../.claude/memory/decisions/ADR-INDEX.md#adr-005)
- [Git Documentation](https://git-scm.com/doc)
- [Conventional Commits](https://www.conventionalcommits.org/)
