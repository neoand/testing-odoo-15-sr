# 🔥 PALAVRA MÁGICA - ENFORCEMENT PROTOCOL

## 🎯 A PALAVRA MÁGICA É:

```
PROTOCOLO
```

---

## 🚨 O QUE ACONTECE QUANDO VOCÊ DIGITA "PROTOCOLO"

Quando você escreve **"PROTOCOLO"** no final do seu prompt, um **hook obrigatório** é acionado que **BLOQUEIA** Claude de terminar até que ele complete **TODOS** os itens do checklist:

### ✅ CHECKLIST OBRIGATÓRIO

Claude **NÃO PODE** terminar sem:

1. ✅ **Thinking Mode** - Ativar `<thinking>` para aprendizados profundos
2. ✅ **ERRORS-SOLVED.md** - Documentar erros resolvidos
3. ✅ **COMMAND-HISTORY.md** - Documentar comandos novos
4. ✅ **PATTERNS.md** - Documentar patterns descobertos
5. ✅ **learnings/** - Documentar aprendizados profundos
6. ✅ **ADR** - Criar ADR se decisão arquitetural
7. ✅ **tool-inventory** - Verificar antes de criar scripts
8. ✅ **Git Commit** - Commitar mudanças localmente
9. ✅ **Sincronizar Template** - Copiar para Claude-especial se genérico
10. ✅ **GitHub Push** - Push para ambos repos

---

## 📖 COMO USAR

### Exemplo 1: Tarefa Normal (SEM enforcement)

```
Usuário: "Crie um script para backup do PostgreSQL"
Claude: [cria script]
Claude: [termina]  ← SEM documentar, SEM commitar
```

**❌ Problema:** Claude esquece de seguir protocolo!

---

### Exemplo 2: Tarefa COM PROTOCOLO (enforcement ativo)

```
Usuário: "Crie um script para backup do PostgreSQL. PROTOCOLO"
Claude: [cria script]
Claude: [tenta terminar]
Hook: 🚨 BLOQUEADO! Checklist não completo!
Claude: [documenta tudo]
Claude: [commita]
Claude: [sincroniza template]
Claude: [push GitHub]
Hook: ✅ OK, pode terminar
```

**✅ Resultado:** TUDO feito corretamente!

---

## 🎯 QUANDO USAR

### ✅ USE "PROTOCOLO" quando:

1. **Tarefa importante** que precisa documentação
2. **Criar/modificar scripts** que devem ir para template
3. **Resolver erro** pela primeira vez
4. **Descobrir pattern** novo
5. **Tomar decisão técnica** importante
6. **Criar funcionalidade** genérica
7. **Qualquer coisa** que você quer garantir que Claude documente

---

### ❌ NÃO USE "PROTOCOLO" quando:

1. Perguntas simples sem ação
2. Tarefas triviais já documentadas
3. Conversas exploratórias
4. Testes rápidos

---

## 🔧 Como Funciona Tecnicamente

### 1. Hook Stop

Arquivo: `.claude/hooks/enforce-protocol-completion.sh`

```bash
# Detecta palavra "PROTOCOLO" no prompt do usuário
if echo "$USER_MESSAGE" | grep -qi "PROTOCOLO"; then
    # Mostra checklist obrigatório
    echo "📋 CHECKLIST OBRIGATÓRIO..."

    # Exit code 2 = BLOQUEIA Claude de terminar
    exit 2
fi
```

---

### 2. Settings.json

Arquivo: `.claude/settings.json`

```json
{
  "hooks": {
    "Stop": {
      "command": "bash",
      "args": [".claude/hooks/enforce-protocol-completion.sh", "{{userMessage}}"],
      "description": "Força Claude a completar protocolo"
    }
  }
}
```

---

### 3. Exit Code 2

Segundo documentação oficial Claude Code:

> **Exit Code 2:** Bloqueia stoppage. Claude **DEVE** continuar até completar tarefa.

**Fonte:** [hooks-guide.md](https://code.claude.com/docs/en/hooks-guide.md)

---

## 📊 Exemplo Completo

### Prompt do Usuário:

```
"Implemente RAG Vector Database com ChromaDB para o projeto.
Quero GPU M3 optimization, reranking, e cron job hourly. PROTOCOLO"
```

### O Que Acontece:

1. **Claude implementa** RAG completo
2. **Claude tenta terminar**
3. **Hook detecta** "PROTOCOLO"
4. **Hook BLOQUEIA** com exit code 2
5. **Hook mostra checklist:**

```
📋 CHECKLIST OBRIGATÓRIO (NÃO PODE PULAR):

  [ ] 1. Ativou Thinking Mode para aprendizados?
  [ ] 2. Documentou em ERRORS-SOLVED.md?
  [ ] 3. Documentou em COMMAND-HISTORY.md?
  [ ] 4. Documentou em PATTERNS.md?
  [ ] 5. Documentou em learnings/?
  [ ] 6. Criou/atualizou ADR?
  [ ] 7. Verificou tool-inventory?
  [ ] 8. Commitou mudanças localmente?
  [ ] 9. Sincronizou com Claude-especial?
  [ ] 10. Push para GitHub?
```

6. **Claude VÊ o bloqueio** e executa TUDO:

```
<thinking>
Implementei RAG Vector Database.

Aprendizados:
1. Python 3.11 vs 3 - sempre especificar versão
2. ChromaDB precisa instalação separada
3. MPS detection automático em M3
4. Reranking melhora 15-20% precisão

Onde documentar:
- ERRORS-SOLVED.md: Erro "ModuleNotFoundError chromadb"
- COMMAND-HISTORY.md: pip install chromadb, python3.11 vs python3
- PATTERNS.md: Pattern de RAG setup
- learnings/rag-implementation.md: Aprendizado profundo
- ADR-009: Decisão usar ChromaDB vs FAISS

Sincronizar template:
- RAG é 100% genérico
- Copiar todos scripts para Claude-especial
- Remover partes específicas de Odoo
</thinking>

[Claude documenta TUDO]
[Claude commita]
[Claude sincroniza template]
[Claude faz push]
```

7. **Hook verifica** novamente
8. **Hook libera** (exit code 0)
9. ✅ **Claude termina** com TUDO completo!

---

## 🎯 Benefícios

### Antes (SEM palavra mágica):

- ❌ Claude esquece de documentar
- ❌ Não usa tool-inventory
- ❌ Não commita
- ❌ Não sincroniza template
- ❌ Conhecimento perdido
- ❌ Você precisa cobrar sempre

---

### Depois (COM "PROTOCOLO"):

- ✅ Claude **OBRIGADO** a documentar
- ✅ Checklist **FORÇADO**
- ✅ Git commit **AUTOMÁTICO**
- ✅ Template **SEMPRE atualizado**
- ✅ Conhecimento **PRESERVADO**
- ✅ Você **NÃO precisa cobrar**!

---

## 📝 Resumo Executivo

**PALAVRA MÁGICA:** `PROTOCOLO`

**QUANDO USAR:** Sempre que tarefa importante precisa documentação

**O QUE FAZ:** Bloqueia Claude de terminar até completar checklist de 10 itens

**RESULTADO:** TUDO documentado, commitado, sincronizado automaticamente

**BENEFÍCIO:** Você nunca mais perde conhecimento ou precisa cobrar Claude!

---

## 🚀 Ativação Imediata

**Hook já está instalado e ativo em:**
- `.claude/hooks/enforce-protocol-completion.sh`
- `.claude/settings.json`

**Basta digitar "PROTOCOLO" no final do seu prompt!**

---

**Criado:** 2025-11-18
**Status:** ✅ Ativo
**Enforcement:** Exit Code 2 (bloqueio obrigatório)
**Objetivo:** Nunca mais Claude esquecer protocolo!

🔥 **"PROTOCOLO" = Claude comportado e confiável!** 🔥
