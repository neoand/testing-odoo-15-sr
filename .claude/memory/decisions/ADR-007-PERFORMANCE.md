# ADR-007: Otimizações de Performance e Paralelização

**Data:** 2025-11-17
**Status:** ✅ Aceito e CRÍTICO
**Decisores:** Anderson + Claude
**Motivação:** Usuário possui Claude Max 20x - precisamos maximizar velocidade e eficiência

---

## Contexto

Claude estava ficando lento em operações sequenciais, especialmente ao:
- Ler múltiplos arquivos
- Executar comandos bash independentes
- Criar/atualizar vários documentos
- Sincronizar entre repositórios

**Problema:** Com Claude Max 20x, estamos sub-utilizando a capacidade de execução paralela.

**Objetivo:** MAXIMIZAR velocidade usando todas as capacidades nativas de paralelização do Claude Code.

---

## Decisão

**Implementar estratégia agressiva de paralelização em TODAS as operações possíveis.**

### Princípios de Execução

1. **Tool Calls Paralelos (CRÍTICO!)**
   - SEMPRE fazer múltiplas tool calls em UMA ÚNICA mensagem quando independentes
   - Nunca esperar resultado de tool se não há dependência
   - Usar batch de operações ao máximo

2. **Bash Commands em Paralelo**
   - Usar `&` e `wait` para comandos independentes
   - Executar git operations em batch
   - Combinar comandos com `&&` quando sequenciais

3. **Headless Mode para Automação**
   - Usar `claude -p` para scripts não-interativos
   - JSON output para parsing automatizado
   - Sessões com `--resume` para continuidade

4. **Git Worktrees para Multi-tasking Real**
   - Múltiplas instâncias Claude em paralelo
   - Cada worktree = tarefa independente
   - Sincronização via git no final

5. **Compactação Agressiva**
   - `/compact` frequentemente
   - Auto-compact ativado
   - `/clear` entre contextos diferentes

---

## Alternativas Consideradas

### 1. Execução Sequencial (ATUAL - LENTO)
- ✅ Simples de entender
- ❌ **MUITO LENTO** - sub-utiliza Claude Max
- ❌ Desperdício de recursos
- ❌ Frustrante para usuário

### 2. Subagents em Cadeia
- ✅ Delegação de tarefas
- ❌ **NÃO são paralelos** - são sequenciais
- ❌ Overhead de context gathering
- ❌ Latência adicional

### 3. Paralelização MÁXIMA ← **ESCOLHIDO**
- ✅ **Velocidade 5-10x maior**
- ✅ Utiliza Claude Max 20x
- ✅ Tool calls paralelos nativos
- ✅ Bash paralelo com & e wait
- ✅ Git worktrees para multi-tasking real
- ⚠️ Requer disciplina de identificar independências

### 4. CI/CD Automation
- ✅ Totalmente desatendido
- ❌ Overhead de setup
- ❌ Feedback loop mais lento
- ❌ Não adequado para desenvolvimento interativo

---

## Implementação

### Regra 1: Tool Calls Paralelos (SEMPRE QUE POSSÍVEL!)

**❌ ERRADO (Sequencial - LENTO):**
```
Read arquivo1 → espera
Read arquivo2 → espera
Read arquivo3 → espera
Total: 3x latência
```

**✅ CORRETO (Paralelo - RÁPIDO):**
```
Uma mensagem com:
- Read arquivo1
- Read arquivo2
- Read arquivo3
Todos executam juntos!
Total: 1x latência
```

**Exemplo Real:**
```python
# Ler múltiplos arquivos de uma vez
Enviar em UMA mensagem:
- Read(.claude/memory/context/projeto.md)
- Read(.claude/memory/context/odoo.md)
- Read(.claude/memory/context/servidores.md)
- Read(.claude/memory/decisions/ADR-INDEX.md)
```

### Regra 2: Bash Paralelo com & e wait

**❌ ERRADO (Sequencial):**
```bash
git status
git diff
git log --oneline -5
# 3 execuções sequenciais
```

**✅ CORRETO (Paralelo):**
```bash
git status & git diff & git log --oneline -5 & wait
# Todos executam em paralelo, wait aguarda conclusão
```

**Exemplo de Sync entre Repos:**
```bash
# Paralelo MÁXIMO
(cd /path/repo1 && git add . && git commit -m "msg" && git push) & \
(cd /path/repo2 && git add . && git commit -m "msg" && git push) & \
wait
# Ambos repos commitados e pushed simultaneamente!
```

### Regra 3: Identificar Dependências

**Independentes (PARALELIZAR):**
- ✅ Ler múltiplos arquivos diferentes
- ✅ Executar git status + git diff
- ✅ Criar múltiplos arquivos novos
- ✅ Bash commands em diretórios diferentes
- ✅ Commits em repos diferentes

**Dependentes (SEQUENCIAL):**
- ❌ Read arquivo → Edit mesmo arquivo
- ❌ git add → git commit (precisa add primeiro)
- ❌ Criar arquivo → Ler arquivo criado
- ❌ Executar script → Ler output do script

### Regra 4: Git Worktrees para Multi-tasking

**Quando usar:**
- Múltiplas features grandes simultâneas
- Trabalho longo que não bloqueia outras tarefas
- Testes em branches diferentes

**Setup:**
```bash
# Criar worktree para feature paralela
git worktree add ../projeto-feature-a -b feature-a

# Em outro terminal/Claude instance
cd ../projeto-feature-a
# Trabalhar independentemente

# Finalizar
cd ../projeto-main
git worktree remove ../projeto-feature-a
```

### Regra 5: Headless para Automação

**Quando usar:**
- Scripts repetitivos
- Batch operations
- CI/CD pipelines
- Cron jobs

**Exemplo:**
```bash
# Executar query sem interação
claude -p "Analyze errors in logs and create summary" \
  --allowedTools "Read,Grep" \
  --output-format json > summary.json

# Continuar conversação
claude --resume session-id -p "Fix top 3 errors"
```

---

## Checklist de Performance (Claude)

Antes de CADA operação, perguntar:

```
[ ] Preciso ler múltiplos arquivos?
    → SIM: Fazer todos Reads em UMA mensagem

[ ] Preciso executar múltiplos bash commands?
    → SIM: Verificar se são independentes
    → Independentes: Usar & e wait
    → Dependentes: Usar && ou sequencial

[ ] Vou criar/editar múltiplos arquivos?
    → SIM: Fazer todos Writes/Edits em UMA mensagem (se independentes)

[ ] Vou commitar em múltiplos repos?
    → SIM: Fazer commits em paralelo com & e wait

[ ] Operação é repetitiva/batch?
    → SIM: Considerar headless mode

[ ] Tarefa grande que pode rodar em paralelo?
    → SIM: Considerar git worktree + instância Claude separada
```

---

## Métricas de Sucesso

### Antes (Sequencial):
- 🔴 Ler 5 arquivos: ~5-10 segundos
- 🔴 Commits em 2 repos: ~10-15 segundos
- 🔴 Sync projeto → template: ~30-40 segundos
- 🔴 Satisfação do usuário: ⭐⭐ (lento demais)

### Depois (Paralelo):
- 🟢 Ler 5 arquivos: ~1-2 segundos (5x mais rápido)
- 🟢 Commits em 2 repos: ~3-5 segundos (3x mais rápido)
- 🟢 Sync projeto → template: ~8-10 segundos (4x mais rápido)
- 🟢 Satisfação do usuário: ⭐⭐⭐⭐⭐ (velocidade máxima!)

---

## Consequências

### Positivas
- ✅ **Velocidade 5-10x maior** em operações múltiplas
- ✅ **Melhor utilização do Claude Max 20x**
- ✅ **Usuário mais satisfeito** - respostas rápidas
- ✅ **Mais produtividade** - menos tempo de espera
- ✅ **Melhor experiência** - fluxo contínuo

### Negativas
- ⚠️ Claude precisa identificar dependências corretamente
- ⚠️ Erros em paralelo podem ser confusos
- ⚠️ Debug de operações paralelas é mais complexo

### Neutras
- 📝 Requer disciplina para aplicar sempre
- 📝 Checklist mental para cada operação
- 📝 Documentação de padrões paralelos

---

## Exemplos Práticos

### Exemplo 1: Sincronização Dual (Antes vs Depois)

**ANTES (LENTO - 40 segundos):**
```
1. Read ADR-INDEX.md projeto
2. Edit ADR-INDEX.md projeto
3. Commit projeto
4. Push projeto
5. Copy para template
6. Read ADR-INDEX.md template
7. Edit ADR-INDEX.md template
8. Commit template
9. Push template
10. Update sync-log projeto
11. Commit sync-log projeto
12. Copy sync-log para template
13. Commit sync-log template
```

**DEPOIS (RÁPIDO - 10 segundos):**
```
Mensagem 1: Read ADR-INDEX.md projeto + template (paralelo)
Mensagem 2: Edit ambos arquivos (paralelo)
Mensagem 3: Bash paralelo:
  (cd projeto && git add . && git commit && git push) &
  (cd template && git add . && git commit && git push) &
  wait
Mensagem 4: Update sync-logs (paralelo) + commits finais (paralelo)
```

### Exemplo 2: Deploy + Verificação

**ANTES (LENTO - 60 segundos):**
```
1. Deploy módulo
2. Espera deploy
3. git status
4. git diff
5. git log
6. Health check servidor
7. Verify logs
```

**DEPOIS (RÁPIDO - 20 segundos):**
```
Mensagem 1: Deploy módulo
Mensagem 2 (paralelo):
  - Bash: git status & git diff & git log & health-check & verify-logs & wait
  - Read logs (se necessário)
Tudo junto!
```

### Exemplo 3: Criação de Múltiplos Arquivos

**ANTES (LENTO):**
```
1. Write arquivo1.md
2. Write arquivo2.md
3. Write arquivo3.md
4. Write arquivo4.md
```

**DEPOIS (RÁPIDO):**
```
Uma mensagem com 4 Writes:
- Write arquivo1.md
- Write arquivo2.md
- Write arquivo3.md
- Write arquivo4.md
Todos criados simultaneamente!
```

---

## Referências

- **Documentação Oficial:** https://code.claude.com/docs/en/common-workflows.md
- **Tool Use Paralelo:** https://docs.claude.com/en/docs/build-with-claude/tool-use
- **Headless Mode:** https://code.claude.com/docs/en/headless.md
- **Git Worktrees:** https://code.claude.com/docs/en/common-workflows.md#git-worktrees

---

## Integração com CLAUDE.md

Adicionar ao CLAUDE.md:

```markdown
## ⚡ REGRAS DE PERFORMANCE (CRÍTICO!)

**SEMPRE paralelizar quando possível:**
1. Múltiplos Reads → UMA mensagem
2. Múltiplos Writes independentes → UMA mensagem
3. Bash commands independentes → & e wait
4. Git ops em repos diferentes → paralelo
5. NUNCA esperar se não há dependência!

**Checklist rápido:**
- [ ] Operação tem dependência? NÃO → PARALELIZAR!
- [ ] Múltiplos tools? SIM → UMA mensagem!
- [ ] Bash independente? SIM → & e wait!
```

---

**Última atualização:** 2025-11-17
**Próxima revisão:** Mensal (verificar se está sendo aplicado)
**Prioridade:** 🔥 CRÍTICA - Impacta satisfação do usuário diretamente
