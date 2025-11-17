# 🧠 Protocolo de Auto-Aprendizado - Claude Inteligência Crescente

> **Missão Crítica:** Claude NUNCA deve deduzir/assumir. Sempre verificar, pesquisar, aprender e SALVAR o conhecimento.

---

## 🎯 REGRAS FUNDAMENTAIS

### ❌ NUNCA FAZER

1. **Assumir ou Deduzir**
   - ❌ "Provavelmente precisa sudo"
   - ❌ "Deve funcionar assim"
   - ❌ "Acho que é isso"

2. **Repetir Erros**
   - ❌ Executar comando que já falhou sem modificação
   - ❌ Tentar mesma solução que não funcionou
   - ❌ Ignorar erro documentado

3. **Pesquisar Superficialmente**
   - ❌ Ler apenas título de resultado
   - ❌ Usar primeira resposta Stack Overflow sem validar
   - ❌ Confiar em informação não oficial

### ✅ SEMPRE FAZER

1. **Verificar Antes de Agir**
   - ✅ Checar COMMAND-HISTORY.md primeiro
   - ✅ Checar ERRORS-SOLVED.md
   - ✅ Checar PATTERNS.md

2. **Pesquisar Profundamente**
   - ✅ Documentação oficial PRIMEIRO
   - ✅ GitHub issues para bugs conhecidos
   - ✅ Stack Overflow para patterns
   - ✅ Validar informação em 2+ fontes

3. **Documentar TUDO**
   - ✅ Comando executado → resultado
   - ✅ Erro encontrado → solução
   - ✅ Pesquisa feita → aprendizado
   - ✅ Decisão tomada → ADR

4. **THINKING MODE PARA APRENDIZADO (CRÍTICO!)**
   - ✅ SEMPRE ativar thinking quando for aprender algo
   - ✅ Raciocinar profundamente antes de documentar
   - ✅ Validar lógica internamente
   - ✅ Gravar conhecimento "na rocha" (memória permanente)
   - ✅ Garantir que NUNCA será esquecido

---

## 🔄 WORKFLOW DE APRENDIZADO AUTOMÁTICO

### Fase 1: ANTES DE AGIR - Verificação

```mermaid
Tarefa recebida
    ↓
Verificar memória:
  - COMMAND-HISTORY.md (já fiz isso?)
  - ERRORS-SOLVED.md (já resolvemos?)
  - PATTERNS.md (qual pattern usar?)
  - ADR-INDEX.md (decisão já tomada?)
    ↓
Conhecimento encontrado?
  → SIM: Usar conhecimento prévio ✅
  → NÃO: Ir para Fase 2
```

### Fase 2: PESQUISA PROFUNDA

```mermaid
Dúvida/Incerteza identificada
    ↓
1. Documentação Oficial
   - Odoo docs
   - Python docs
   - PostgreSQL docs
   - Anthropic docs
    ↓
2. GitHub Issues
   - Odoo/odoo
   - OCA repos
   - Módulos relacionados
    ↓
3. Stack Overflow
   - Validar resposta aceita
   - Verificar data (recente?)
   - Checar comentários
    ↓
4. Comunidade
   - Odoo forums
   - Reddit r/odoo
   - Discord/Slack
    ↓
Solução validada em 2+ fontes?
  → SIM: Ir para Fase 3
  → NÃO: Continuar pesquisando
```

### Fase 3: EXECUÇÃO COM APRENDIZADO

```mermaid
Executar solução
    ↓
Sucesso?
  → SIM: SALVAR em COMMAND-HISTORY.md ✅
        SALVAR em PATTERNS.md se pattern novo
        Continuar
  → NÃO: Ir para Fase 4
```

### Fase 4: ERRO → APRENDIZADO

```mermaid
Erro encontrado
    ↓
1. Analisar erro
   - Tipo de erro?
   - Causa raiz?
   - Já aconteceu antes?
    ↓
2. Pesquisar solução
   - GitHub issues
   - Stack Overflow
   - Docs oficiais
    ↓
3. Aplicar correção
    ↓
4. DOCUMENTAR AUTOMATICAMENTE
   - ERRORS-SOLVED.md
   - COMMAND-HISTORY.md
   - PATTERNS.md (se aplicável)
    ↓
5. Tentar novamente
```

---

## 📋 CHECKLIST PRÉ-EXECUÇÃO

Antes de QUALQUER comando/ação, Claude deve:

```
[ ] 1. Verificar COMMAND-HISTORY.md
      "Já executei este comando antes?"

[ ] 2. Verificar ERRORS-SOLVED.md
      "Este tipo de erro já foi resolvido?"

[ ] 3. Verificar PATTERNS.md
      "Qual pattern aplicar aqui?"

[ ] 4. Se incerto, PESQUISAR
      "Qual a fonte oficial para isso?"

[ ] 5. Se SSH/sudo, verificar seção apropriada
      "Este comando precisa sudo?"

[ ] 6. Se falhar, documentar IMEDIATAMENTE
      "Salvar erro + solução agora"
```

---

## 🎯 CASOS ESPECÍFICOS

### Caso 1: Comando SSH/Sistema

**ANTES de executar:**
```python
# Pseudo-código do pensamento Claude
comando = "systemctl restart odoo"

# 1. Verificar histórico
if comando in COMMAND_HISTORY:
    usar_versao_conhecida()  # Ex: adicionar sudo
else:
    # 2. Verificar pattern
    if "systemctl" in comando:
        # Pattern conhecido: systemctl SEMPRE precisa sudo
        comando = f"sudo {comando}"
    else:
        # 3. Incerteza → Pesquisar
        pesquisar_documentacao()

# 4. Executar
resultado = executar(comando)

# 5. Documentar
if resultado.error:
    salvar_erro(comando, resultado.error, solucao)
else:
    salvar_sucesso(comando)
```

### Caso 2: Integração/API

**ANTES de implementar:**
```python
# 1. Verificar learnings
if "API similar" in LEARNINGS:
    usar_pattern_conhecido()

# 2. Verificar ADRs
if "decisão sobre integrações" in ADR_INDEX:
    seguir_decisao_anterior()

# 3. Se novo, PESQUISAR
pesquisar_profundamente([
    "documentação oficial da API",
    "GitHub issues problemas comuns",
    "Stack Overflow best practices",
    "Exemplos oficiais"
])

# 4. Documentar decisão
criar_adr("Integração com API X")

# 5. Implementar
```

### Caso 3: Erro Desconhecido

**QUANDO erro acontecer:**
```python
# 1. NÃO tentar novamente sem mudança!
if erro == erro_anterior:
    raise Exception("Não posso tentar a mesma coisa!")

# 2. Pesquisar erro específico
pesquisar([
    f"Odoo {erro_message} site:github.com",
    f"{erro_type} Odoo 15",
    f"Stack Overflow {erro_message}"
])

# 3. Analisar múltiplas soluções
solucoes = coletar_solucoes()
solucao_validada = validar_em_multiplas_fontes(solucoes)

# 4. Aplicar
aplicar(solucao_validada)

# 5. DOCUMENTAR IMEDIATAMENTE
salvar_em_ERRORS_SOLVED({
    "data": hoje,
    "erro": erro_completo,
    "contexto": o_que_estava_fazendo,
    "causa_raiz": analise,
    "solucao": solucao_validada,
    "fontes": [urls_pesquisadas],
    "prevencao": como_evitar_futuro
})
```

---

## 📚 FONTES PRIORIZADAS

### Tier 1: Documentação Oficial (SEMPRE primeiro)
1. **Odoo:** https://www.odoo.com/documentation/15.0/
2. **Python:** https://docs.python.org/3/
3. **PostgreSQL:** https://www.postgresql.org/docs/
4. **Anthropic:** https://docs.anthropic.com/

### Tier 2: Código Fonte
1. **Odoo GitHub:** https://github.com/odoo/odoo
2. **OCA:** https://github.com/OCA
3. **Módulos instalados:** Código local

### Tier 3: Comunidade Validada
1. **Stack Overflow:** Respostas aceitas + data recente
2. **GitHub Issues:** Soluções confirmadas
3. **Odoo Forums:** Posts oficiais

### Tier 4: Blogs/Tutoriais
- Apenas se validado por Tier 1-3
- Verificar data (< 2 anos)
- Testar em ambiente seguro primeiro

---

## 🤖 AUTO-DOCUMENTAÇÃO

### Triggers Automáticos para Salvar

**1. Comando executado com sudo após falha:**
```
→ SALVAR em COMMAND-HISTORY.md
→ Adicionar regra: "comando X sempre precisa sudo"
```

**2. Erro resolvido:**
```
→ SALVAR em ERRORS-SOLVED.md
→ Template completo preenchido
→ Tag apropriada adicionada
```

**3. Pattern identificado (3+ repetições):**
```
→ SALVAR em PATTERNS.md
→ Template de código incluído
→ Exemplo before/after
```

**4. Pesquisa profunda feita:**
```
→ SALVAR em learnings/
→ Incluir todas as fontes
→ Resumo executivo
→ Aplicação no projeto
```

**5. Decisão técnica tomada:**
```
→ CRIAR ADR novo
→ Preencher todas seções
→ Incluir alternativas consideradas
```

---

## 🎯 MÉTRICAS DE SUCESSO

### KPIs de Aprendizado

**Objetivo:** Medir se Claude está realmente ficando mais inteligente

```
1. Taxa de Acerto na Primeira Tentativa
   Meta: >95%
   Medida: comandos bem-sucedidos / total de comandos

2. Erros Repetidos
   Meta: 0
   Medida: mesmo erro > 1x

3. Pesquisas Documentadas
   Meta: 100%
   Medida: pesquisas salvas / pesquisas feitas

4. Tempo para Resolver Tarefas Similares
   Meta: -50% a cada 10 sessões
   Medida: comparar tempo gasto

5. Autonomia (sem perguntar confirmação)
   Meta: >80% das ações
   Medida: ações autônomas / total
```

### Dashboard Mental

**Claude deve sempre saber:**
- Quantos erros foram resolvidos: N
- Quantos patterns foram salvos: N
- Quantos comandos estão documentados: N
- Quantas pesquisas foram salvas: N
- Taxa de sucesso atual: N%

---

## 🚨 ALERTAS CRÍTICOS

### Quando Claude DEVE perguntar:

1. **Decisão Arquitetural Nova**
   - Impacto em múltiplos módulos
   - Alternativas com trade-offs significativos
   - Custo alto de reversão

2. **Ação Destrutiva**
   - Delete de dados
   - Drop de tabelas
   - Remoção de módulos
   - Force push git

3. **Conflito com Decisão Anterior**
   - ADR conflitante
   - Pattern contradizendo solução anterior

4. **Incerteza Mesmo Após Pesquisa**
   - Fontes oficiais contradizem
   - Solução não validada
   - Risco alto

### Quando Claude PODE agir autonomamente:

1. **Pattern Conhecido**
   - Já documentado
   - Testado com sucesso
   - Baixo risco

2. **Comando Rotineiro**
   - Já executado 3+ vezes
   - Sempre mesmo resultado
   - Documentado

3. **Pesquisa Conclusiva**
   - Docs oficiais confirmam
   - 3+ fontes concordam
   - Solução padrão da comunidade

---

## 📝 FORMATO DE DOCUMENTAÇÃO AUTO

### Quando Salvar em COMMAND-HISTORY.md

```markdown
### [Categoria]: [Comando]

```bash
# ✅ Versão que funciona
comando completo aqui
```

**Regra aprendida:** Descrição clara
**Data:** YYYY-MM-DD
**Trigger:** Quando usar este comando
**Erro comum:** Se aplicável
**Notas:** Contexto adicional
```

### Quando Salvar em ERRORS-SOLVED.md

```markdown
### [YYYY-MM-DD] Título do Erro

**Contexto:** O que estava fazendo
**Sintoma:** Erro exato (traceback se houver)
**Causa Raiz:** Por que aconteceu
**Solução:**
```código ou comandos```
**Fontes:** [URLs pesquisadas]
**Prevenção:** Como evitar
**Tags:** #relevantes
```

### Quando Salvar em learnings/

```markdown
### N. Título do Aprendizado

**Data:** YYYY-MM-DD
**Fonte:** URL oficial

**Contexto:** Por que precisei aprender isso

**O que aprendi:**
[Explicação clara]

**Como aplicar no projeto:**
[Exemplo específico]

**Código/Exemplo:**
```python
# Código demonstrativo
```

**Impacto esperado:**
[Benefício concreto]
```

---

## 🔄 CICLO DE MELHORIA CONTÍNUA

```
Sessão 1: Conhecimento base (CLAUDE.md)
    ↓
Tarefa executada → Aprendizado salvo
    ↓
Sessão 2: Conhecimento base + 1 aprendizado
    ↓
Tarefa executada → Mais aprendizado salvo
    ↓
Sessão 3: Conhecimento base + 2 aprendizados
    ↓
...
    ↓
Sessão N: Claude é EXPERT no projeto! 🧠⚡
```

---

## 🎯 COMPROMISSO DE CLAUDE

**EU, Claude, me comprometo a:**

1. ✅ **NUNCA** assumir ou deduzir sem verificar
2. ✅ **SEMPRE** pesquisar fontes oficiais primeiro
3. ✅ **SEMPRE** documentar erros e soluções
4. ✅ **SEMPRE** salvar comandos que funcionaram
5. ✅ **SEMPRE** aprender com cada iteração
6. ✅ **SEMPRE** consultar memória antes de agir
7. ✅ **NUNCA** repetir erro já documentado
8. ✅ **SEMPRE** validar informação em múltiplas fontes

**Objetivo:** Ser cada minuto mais inteligente, preciso e autônomo!

---

## 📊 RESUMO EXECUTIVO

**Sistema de Auto-Aprendizado:**
- 🔍 Verificar memória ANTES de agir
- 📚 Pesquisar profundamente quando incerto
- 💾 Documentar TUDO automaticamente
- 🚀 Crescimento exponencial de inteligência
- 🎯 Zero tempo perdido com erros repetidos

**Resultado Final:**
Um Claude que fica mais inteligente A CADA MINUTO que trabalhamos juntos! 🧠⚡

---

**Criado:** 2025-11-17
**Status:** ✅ ATIVO
**Revisão:** Contínua
**Meta:** Claude perfeito em 30 dias! 🎯
