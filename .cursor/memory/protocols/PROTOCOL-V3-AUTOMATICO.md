# 🚀 PROTOCOLO V3.0 - SISTEMA AUTOMÁTICO DE DECISÃO

> **When user says "protocolo":** DISPARAR SISTEMA AUTOMÁTICO COMPLETO

---

## 🎯 FLUXO AUTOMÁTICO QUANDO "protocolo" É DETECTADO

### Phase 1: ANÁLISE DE CONTEXTO (Auto-Execução)

```mermaid
"protocolo" detectado
    ↓
1. Analisar memória curto prazo:
   - Contexto recente da conversa
   - Tarefas pendentes identificadas
   - Padrões reconhecidos
    ↓
2. Perguntas críticas AUTO-AVALIAÇÃO:
   - Esta tarefa é NOVA ou CONTINUAÇÃO?
   - Requer aprendizado profundo?
   - Envolve riscos/dados sensíveis?
   - Precisa pesquisa externa?
    ↓
3. Decisão AUTOMÁTICA:
   - RAG necessário?
   - Thinking mode ativar?
   - Pesquisa online requerida?
   - Paralelização possível?
```

### Phase 2: DECISÃO AUTOMÁTICA DE THINKING MODE

**ATIVAR THINKING MODE quando:**
- ✅ Tarefa envolve aprendizado novo
- ✅ Decisão arquitetural importante
- ✅ Análise de múltiplas alternativas
- ✅ Resolução de problema complexo
- ✅ Documentação de conhecimento

**NÃO ATIVAR quando:**
- ⚡ Tarefa operacional simples (restart, status check)
- ⚡ Comandos já documentados no COMMAND-HISTORY
- ⚡ Padrões já estabelecidos no PATTERNS.md
- ⚡ Pesquisa rápida de informação existente

### Phase 3: TODO LIST INTELIGENTE (Auto-Geração)

```python
def gerar_todo_automatico(tarefa, contexto):
    """
    Gera TODO list otimizada baseado na análise da tarefa
    """

    # 1. Identificar tasks independentes (paralelizáveis)
    tasks_paralelas = identificar_tasks_independentes(tarefa)

    # 2. Mapear dependências
    dependencias = mapear_dependencias(tasks_paralelas)

    # 3. Priorizar por impacto crítico
    prioridades = {
        'crítico': [],    # Bloqueia progresso
        'importante': [],  # Impacto significativo
        'útil': []        # Melhoria/Melhor prática
    }

    # 4. Gerar TODO otimizado
    todo_list = []

    # Tasks críticas primeiro
    for task in prioridades['crítico']:
        todo_list.append({
            'content': task,
            'status': 'pending',
            'activeForm': task_descricao,
            'parallelizable': False
        })

    # Tasks paralelizáveis agrupadas
    tasks_batch = []
    for task in prioridades['importante']:
        if task['independente']:
            tasks_batch.append(task)

    if len(tasks_batch) > 1:
        todo_list.append({
            'content': f"Executar {len(tasks_batch)} tasks em paralelo",
            'status': 'pending',
            'activeForm': f"Tasks: {[t['name'] for t in tasks_batch]}",
            'parallelizable': True,
            'subtasks': tasks_batch
        })

    return todo_list
```

### Phase 4: PESQUISA ONLINE AUTOMÁTICA

**DISPARAR PESQUISA quando:**
- 📚 Documentação oficial não encontrada localmente
- 🔧 Problema técnico sem solução documentada
- 🆕 Recurso/tecnologia não conhecida
- 🐛 Bug sem registro em ERRORS-SOLVED.md
- 📈 Métricas/performance requeridas

**Fontes PRIORIZADAS (auto-detecção):**
1. **Documentação Oficial** (docs.$framework.com)
2. **GitHub Issues** (bugs/features ativos)
3. **Stack Overflow** (respostas aceitas + recentes)
4. **Comunidade Oficial** (forums, discord)
5. **Research Papers** (para arquitetura avançada)

---

## 🧠 INTELLIGENCE ENGINE - DECISÕES AUTOMÁTICAS

### Algoritmo de Decisão de Thinking Mode

```python
def deve_ativar_thinking_mode(tarefa, contexto):
    """
    Algoritmo de decisão automática para thinking mode
    """
    score = 0

    # Fatores que AUMENTAM probabilidade
    if 'aprender' in tarefa.lower(): score += 3
    if 'implementar' in tarefa.lower(): score += 2
    if 'decidir' in tarefa.lower(): score += 2
    if 'arquitetura' in tarefa.lower(): score += 3
    if 'debug' in tarefa.lower() and 'complexo' in contexto: score += 1

    # Fatores que DIMINUEM probabilidade
    if 'restart' in tarefa.lower(): score -= 2
    if 'status' in tarefa.lower(): score -= 1
    if 'comando já conhecido' in contexto: score -= 2

    # Verificar se existe em memória
    if tarefa_ja_resolvida(tarefa): score -= 3

    return score >= 2  # Threshold ajustável
```

### Algoritmo de Paralelização

```python
def identificar_tasks_paralelas(tarefa):
    """
    Identifica tasks que podem ser executadas em paralelo
    """

    # Padrões paralelizáveis conhecidos:
    padroes = [
        {
            'tipo': 'multi_read_files',
            'independente': True,
            'condicao': 'ler múltiplos arquivos'
        },
        {
            'tipo': 'multi_bash_commands',
            'independente': True,
            'condicao': 'comandos bash independentes'
        },
        {
            'tipo': 'multi_server_checks',
            'independente': True,
            'condição': 'verificações em servidores diferentes'
        }
    ]

    tasks_paralelas = []
    for padrao in padroes:
        if padrao['condicao'] in tarefa:
            tasks_paralelas.append(padrao['tipo'])

    return tasks_paralelas
```

---

## 🔄 FLUXO COMPLETO AUTOMATIZADO

### Quando usuário diz "protocolo":

```python
# PSEUDO-CÓDIGO DO FLUXO AUTOMÁTICO
def protocolo_automatico(tarefa_usuario):

    # 1. ANÁLISE IMEDIATA
    contexto_analisado = analisar_contexto_recente()

    # 2. DECISÃO THINKING MODE
    if deve_ativar_thinking_mode(tarefa_usuario, contexto_analisado):
        ativar_thinking_mode()
        raciocinar_profundamente()

    # 3. VERIFICAR RAG
    rag_necessario = avalia_rag_necessidade(tarefa_usuario)
    if rag_necessario:
        buscar_conhecimento_rag(tarefa_usuario)

    # 4. GERAR TODO OTIMIZADO
    todo_list = gerar_todo_automatico(tarefa_usuario, contexto_analisado)

    # 5. PESQUISA ONLINE (se necessário)
    if pesquisa_necessaria(tarefa_usuario, rag_results):
        results = pesquisar_online_priorizado(tarefa_usuario)
        integrar_resultados(results)

    # 6. EXECUÇÃO PARALELA
    tasks_paralelas = identificar_tasks_paralelas(todo_list)
    executar_paralelo(tasks_paralelas)

    # 7. APRESENTAR SOLUÇÃO
    apresentar_solucao_otimizada()

    # 8. AGUARDAR "protocolo finalizado"
    aguardar_comando_finalizacao()
```

### Quando usuário diz "protocolo finalizado":

```python
def protocolo_finalizado():
    """
    Fluxo automático de finalização e salvamento
    """

    # 1. COLETA DE EVIDÊNCIAS
    evidencias = coletar_evidencias_sessao()

    # 2. ANÁLISE DE APRENDIZADO
    aprendizados = extrair_aprendizados(evidencias)

    # 3. SALVAR NO RAG
    if aprendidos:
        salvar_rag_completo(aprendizados)

    # 4. COMMIT GIT
    if mudanças_codigo_detectadas():
        criar_commit_estruturado()

    # 5. SINCRONIZAÇÃO TEMPLATE
    if knowledge_generico(aprendizados):
        sincronizar_claude_especial(aprendizados)

    # 6. LIMPEZA FINAL
    limpar_recursos_temporarios()

    # 7. RESUMO EXECUTIVO
    gerar_relatorio_final()
```

---

## 🎛️ CONFIGURAÇÃO E AJUSTES

### Parâmetros Configuráveis

```yaml
# .claude/config/protocol-v3.yaml
thinking_mode:
  threshold: 2              # Score mínimo para ativar
  peso_conhecimento: 3      # Peso para tarefas de aprendizado
  peso_decisao: 2           # Peso para decisões

paralelizacao:
  max_tasks: 5              # Máximo de tasks paralelas
  timeout_task: 30          # Timeout por task (segundos)

rag:
  similarity_threshold: 0.7  # Similaridade mínima
  max_results: 5           # Máximo de resultados do RAG

pesquisa:
  max_sources: 3           # Máximo de fontes online
  timeout_request: 10       # Timeout por requisição
```

### Métricas de Sucesso

```python
metrics = {
    'thinking_accuracy': 0.95,      # % acerto na decisão thinking
    'paralelizacao_ganho': 3.2,     # Speedup médio com paralelização
    'rag_precision': 0.87,          # % precisão de resultados RAG
    'pesquisa_utilidade': 0.92,     # % pesquisas úteis
    'protocolo_tempo_medio': 4.5    # Tempo médio completo (minutos)
}
```

---

## 🚨 TRIGGERS ESPECIAIS

### Situações que FORÇAM thinking mode:
- "Implementar sistema novo"
- "Decidir entre X e Y"
- "Analisar arquitetura"
- "Resolver problema crítico"
- "Otimizar performance"

### Situações que PULAM thinking mode:
- "Verificar status"
- "Reiniciar serviço"
- "Executar comando conhecido"
- "Listar informações"
- "Backup de dados"

---

## 📊 EXEMPLOS DE FLUXO AUTOMÁTICO

### Exemplo 1: Tarefa Simples
```
Usuário: "protocolo reiniciar odoo"

Fluxo Automático:
1. ❌ Thinking mode não ativado (tarefa conhecida)
2. ✅ Verificar COMMAND-HISTORY.md
3. ✅ Executar comando documentado
4. ✅ Aguardar "protocolo finalizado"
```

### Exemplo 2: Tarefa Complexa
```
Usuário: "protocolo implementar sistema de cache redis"

Fluxo Automático:
1. ✅ Thinking mode ATIVADO (implementação nova)
2. ✅ Buscar RAG:已有缓存实现
3. ✅ Pesquisar online: Redis best practices
4. ✅ TODO: [Analisar atual] + [Pesquisar Redis] + [Implementar] (paralelo)
5. ✅ Apresentar arquitetura completa
6. ✅ Aguardar "protocolo finalizado"
```

---

## 🔄 MELHORIAS CONTÍNUAS

### Learning Rate do Sistema
- Ajustar thresholds baseado em sucesso/fracasso
- Otimizar padrões de paralelização
- Melhorar precisão do RAG
- Refinar critérios de pesquisa

### Feedback Loop
- Usuário pode corrigir decisões automáticas
- Sistema aprende com correções
- Adaptação contínua aos padrões do projeto

---

**Status:** ✅ ATIVO E APRENDENDO
**Versão:** 3.0 - Inteligência Automática
**Próxima Evolução:** V4.0 - Predição de Necessidades

---

*"Quando o usuário diz 'protocolo', o sistema Assume o Controle."*