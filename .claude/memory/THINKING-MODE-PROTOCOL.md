# 🧠 Protocolo de Thinking Mode para Aprendizado

> **Regra Crítica:** SEMPRE ativar thinking mode quando for aprender e documentar algo novo.

---

## 🎯 Quando Ativar Thinking Mode

### ✅ SEMPRE Ativar Quando:

1. **Aprender Algo Novo**
   - Resolver erro pela primeira vez
   - Descobrir pattern novo
   - Pesquisar documentação
   - Entender conceito complexo

2. **Documentar Conhecimento**
   - Salvar em ERRORS-SOLVED.md
   - Salvar em PATTERNS.md
   - Salvar em learnings/
   - Criar ADR novo

3. **Tomar Decisões Importantes**
   - Escolha arquitetural
   - Trade-offs significativos
   - Impacto em múltiplos módulos

4. **Validar Informação**
   - Antes de salvar em memória
   - Antes de aplicar solução
   - Quando múltiplas fontes contradizem

---

## 🔄 Workflow com Thinking Mode

### Processo Completo

```
1. Situação de Aprendizado Detectada
   ↓
2. ATIVAR THINKING MODE automaticamente
   ↓
3. Raciocinar profundamente:
   - O que estou aprendendo?
   - Por que isso é importante?
   - Como se relaciona com o projeto?
   - Quais as implicações?
   - Como validar isso?
   - Onde documentar?
   ↓
4. Validar Raciocínio:
   - Lógica faz sentido?
   - Informação está correta?
   - Fontes são confiáveis?
   - Há contradições?
   ↓
5. Documentar "na Rocha":
   - Arquivo apropriado (.claude/memory/)
   - Formato estruturado
   - Contexto completo
   - Fontes citadas
   - Exemplos práticos
   ↓
6. Confirmar Persistência:
   - ✅ Salvo em arquivo correto
   - ✅ Será carregado próxima sessão
   - ✅ NUNCA será esquecido
```

---

## 🧠 Exemplo de Thinking para Aprendizado

### Situação: Comando falhou com "Permission denied"

**COM Thinking Mode (CORRETO):**

```
<thinking>
Comando executou: systemctl restart odoo
Erro: Permission denied

Análise:
1. systemctl é comando de sistema
2. Controla serviços do systemd
3. Requer privilégios root
4. Solução: adicionar sudo

Validação:
- systemctl SEMPRE precisa sudo? SIM
  - Fonte: man systemctl
  - Fonte: experiência anterior em servidores
  - Confirmado em docs Linux

Generalização:
- systemctl [qualquer comando] → sempre sudo
- Não é específico de "restart"
- Aplica-se a: start, stop, status, enable, disable

Onde documentar:
- COMMAND-HISTORY.md (seção systemctl)
- Como regra geral, não caso específico

Prevenção:
- Próximas vezes: verificar COMMAND-HISTORY.md antes
- Se systemctl → adicionar sudo automaticamente

Impacto:
- Economiza tempo futuro
- Evita frustração
- Primeira tentativa correta sempre
</thinking>

Agora vou:
1. Executar com sudo
2. SALVAR regra em COMMAND-HISTORY.md
3. Garantir que NUNCA esquecerei
```

**SEM Thinking Mode (ERRADO):**

```
Ah, precisa sudo!
sudo systemctl restart odoo
[Funciona]
[Não documenta adequadamente]
[Esquece na próxima sessão]
```

---

## 📚 Categorias de Aprendizado

### 1. Comandos (COMMAND-HISTORY.md)

**Thinking deve incluir:**
- Por que o comando precisa sudo/usuário específico?
- É regra geral ou caso específico?
- Existem exceções?
- Como generalizar o aprendizado?

**Exemplo:**
```
systemctl → SEMPRE sudo (controle sistema)
psql → SEMPRE -u postgres (banco de dados)
chown → SEMPRE sudo (modificar propriedade)
```

---

### 2. Erros (ERRORS-SOLVED.md)

**Thinking deve incluir:**
- Qual a causa raiz REAL?
- Por que a solução funciona?
- Como prevenir no futuro?
- Padrão geral ou caso isolado?

**Exemplo:**
```
Erro: N+1 queries
Causa: Campo computed sem store
Solução: Adicionar store=True
Prevenção: SEMPRE usar store quando campo muito acessado
Pattern: Performance vs. Consistência trade-off
```

---

### 3. Patterns (PATTERNS.md)

**Thinking deve incluir:**
- Por que esse pattern é bom?
- Quando NÃO usar?
- Qual o contexto de aplicação?
- Alternativas consideradas?

**Exemplo:**
```
Pattern: @api.depends com campos relacionados completos
Por que: Garante cache correto do ORM
Quando usar: SEMPRE que compute depende de campo relacionado
Quando não: Campos não relacionais
```

---

### 4. Decisões (ADR-INDEX.md)

**Thinking deve incluir:**
- Contexto completo da decisão
- Todas alternativas consideradas
- Trade-offs de cada opção
- Por que escolhemos essa?
- Quando reavaliar?

**Exemplo:**
```
Decisão: Usar requests síncrono para Kolmeya
Alternativas: Async (aiohttp), Queue (Celery), Biblioteca própria
Trade-offs:
  - Síncrono: Simples, bloqueia thread
  - Async: Complexo, não bloqueia
  - Queue: Infraestrutura, mais robusto
Escolha: Síncrono (simplicidade > volume atual)
Reavaliar: Quando > 1000 SMS/dia
```

---

### 5. Learnings (learnings/)

**Thinking deve incluir:**
- O que aprendi exatamente?
- Por que isso é importante para o projeto?
- Como aplicar na prática?
- Qual o impacto esperado?

**Exemplo:**
```
Aprendizado: Odoo prefetch automático
Importância: Performance crítica
Aplicação: Evitar N+1 em iterações
Impacto: -90% queries em listagens
```

---

## 🎯 Qualidade do Aprendizado

### Aprendizado Superficial (EVITAR)

```
❌ "systemctl precisa sudo"
   - Sem entender por quê
   - Sem generalizar
   - Sem validar
```

### Aprendizado Profundo (FAZER)

```
✅ "systemctl é comando de controle do systemd
    que requer privilégios root porque manipula
    serviços do sistema. SEMPRE precisa sudo,
    independente da ação (start/stop/restart/etc).
    Validado em: man systemctl, docs Linux.
    Pattern: comandos de sistema = sudo"
```

---

## 🔒 Gravação "na Rocha"

### O Que Significa "Gravar na Rocha"

**Não é apenas salvar arquivo!**

É garantir que o conhecimento:
1. ✅ Foi validado profundamente
2. ✅ Está no contexto correto
3. ✅ Tem exemplos práticos
4. ✅ Tem fontes citadas
5. ✅ Está no arquivo correto
6. ✅ Será carregado automaticamente
7. ✅ NUNCA será perdido

### Checklist de "Gravação na Rocha"

```
[ ] Thinking mode foi ativado
[ ] Raciocínio profundo foi feito
[ ] Informação foi validada
[ ] Contexto está completo
[ ] Exemplos foram incluídos
[ ] Fontes foram citadas
[ ] Arquivo correto foi escolhido
[ ] Formato estruturado foi usado
[ ] Será carregado próxima sessão (via @import)
[ ] Verificação final: faz sentido?
```

---

## 📊 Métricas de Qualidade

### Aprendizado Bem Documentado

**Deve ter:**
- ✅ Contexto claro
- ✅ Causa raiz (não sintoma)
- ✅ Solução validada
- ✅ Fontes confiáveis
- ✅ Generalização aplicável
- ✅ Exemplos práticos
- ✅ Prevenção futura

### Aprendizado Mal Documentado

**Problemas:**
- ❌ Apenas sintoma, não causa
- ❌ Solução não validada
- ❌ Sem fontes
- ❌ Caso específico, não pattern
- ❌ Sem exemplos
- ❌ Não previne repetição

---

## 🎯 Compromisso de Claude

**Quando for aprender algo, EU me comprometo a:**

1. ✅ **ATIVAR thinking mode automaticamente**
2. ✅ **RACIOCINAR profundamente** (não superficialmente)
3. ✅ **VALIDAR informação** (múltiplas fontes)
4. ✅ **DOCUMENTAR completamente** (contexto + exemplos)
5. ✅ **GRAVAR "na rocha"** (memória permanente)
6. ✅ **GARANTIR persistência** (será carregado sempre)
7. ✅ **NUNCA esquecer** (conhecimento eterno)

---

## 💡 Exemplo Completo: Aprendizado End-to-End

### Situação: Descoberta de N+1 Query

**1. Detecção:**
```
Listagem de CRM lenta (>10s)
```

**2. Ativação de Thinking Mode:**
```
<thinking>
Problema: Lentidão em listagem
Hipótese: N+1 queries

Investigação:
- Verificar logs PostgreSQL
- Contar queries executadas
- Identificar padrão repetido

Descoberta: Campo computed partner_name fazendo query a cada record

Análise:
- Por que N+1? Campo computed sem cache
- O que é N+1? 1 query inicial + N queries (uma por record)
- Como resolver? @api.depends correto

Validação:
- Docs Odoo sobre @api.depends
- Como funciona prefetch do ORM
- Quando usar store=True

Solução validada:
@api.depends('partner_id.phone') ao invés de @api.depends('partner_id')

Pattern geral:
- Campos computados que acessam relacionados
- SEMPRE especificar campo completo no depends
- Considera store=True se campo muito acessado

Impacto:
- De 150 queries para 3 queries
- De 10s para <1s
- Aplicável a TODOS computed fields do projeto
</thinking>
```

**3. Documentação "na Rocha":**

```markdown
# Em ERRORS-SOLVED.md
### [2025-11-17] Performance CRM - N+1 Queries

**Contexto:** Listagem de leads levando >10s
**Causa Raiz:** Campo computed sem depends correto
**Solução:** @api.depends('partner_id.phone')
**Pattern:** SEMPRE especificar campo completo em depends
**Impacto:** -95% queries, -90% tempo

# Em PATTERNS.md
### @api.depends com Campos Relacionados

❌ ERRADO:
@api.depends('partner_id')
def _compute_phone(self):
    record.phone = record.partner_id.phone  # N+1!

✅ CORRETO:
@api.depends('partner_id.phone')
def _compute_phone(self):
    record.phone = record.partner_id.phone  # Cached!

# Em learnings/
### Odoo Prefetch e Depends

**Fontes:**
- Odoo docs: https://...
- OCA guidelines: https://...
- Debugging próprio: logs PostgreSQL

**Aplicação:** Todos os 12 campos computed do projeto auditados
```

**4. Verificação Final:**
```
✅ Thinking mode usado
✅ Raciocínio profundo feito
✅ Solução validada
✅ Documentado em 3 lugares
✅ Pattern generalizado
✅ Exemplos incluídos
✅ Fontes citadas
✅ GRAVADO NA ROCHA!
```

---

## 🚀 Resultado Esperado

### Com Este Protocolo:

**Aprendizado:**
- 🧠 Profundo (não superficial)
- ✅ Validado (não assumido)
- 📚 Documentado (não esquecido)
- 🎯 Aplicável (não teórico)
- 🔒 Permanente (gravado na rocha)

**Benefícios:**
- ⚡ Velocidade crescente
- 🎯 Precisão máxima
- 🧠 Inteligência exponencial
- 🔒 Conhecimento eterno
- 💪 Claude cada vez mais expert

---

## 📝 Resumo Executivo

**REGRA DE OURO:**

> "Toda vez que for aprender algo, ATIVAR thinking mode automaticamente,
> raciocinar profundamente, validar rigorosamente, e documentar COMPLETAMENTE
> para que o conhecimento seja gravado NA ROCHA e NUNCA seja esquecido!"

---

**Criado:** 2025-11-17
**Status:** ✅ ATIVO
**Prioridade:** 🔴 CRÍTICA
**Resultado:** Claude aprende de verdade, não superficialmente!
