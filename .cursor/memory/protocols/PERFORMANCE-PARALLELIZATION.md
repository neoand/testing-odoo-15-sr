# ⚡ Protocolo de Performance e Paralelização

> **Missão:** Maximizar velocidade usando Claude Max 20x ao MÁXIMO!

---

## 🎯 Princípio Fundamental

**PARALELIZAR SEMPRE! Usuário tem Claude Max 20x - MAXIMIZAR VELOCIDADE!**

---

## ✅ Checklist Rápido (A CADA Operação)

```
[ ] Vou ler múltiplos arquivos? → UMA mensagem com todos Reads
[ ] Vou executar múltiplos bash? → Verificar independência → & e wait
[ ] Vou criar/editar múltiplos arquivos? → UMA mensagem com todos
[ ] Commits em múltiplos repos? → Bash paralelo com &
```

---

## 🔥 Regras de Ouro

### 1. Tool Calls Paralelos
- ✅ Read 5 arquivos → UMA mensagem (5x mais rápido)
- ✅ Write 3 arquivos → UMA mensagem (3x mais rápido)
- ❌ NUNCA fazer calls sequenciais se independentes!

### 2. Bash Paralelo
- ✅ `git status & git diff & git log & wait`
- ✅ `(cd repo1 && git push) & (cd repo2 && git push) & wait`
- ❌ NUNCA sequencial se independente!

### 3. Identificar Dependências
- Independentes → PARALELIZAR
- Dependentes → Sequencial (óbvio)

---

## 🎯 Objetivo

**Operações 5-10x mais rápidas!**

---

## 📖 Referência Completa

Ver [ADR-007-PERFORMANCE.md](../decisions/ADR-007-PERFORMANCE.md) para detalhes completos e exemplos.

---

**Última atualização:** 2025-11-17
**Status:** ✅ ATIVO
