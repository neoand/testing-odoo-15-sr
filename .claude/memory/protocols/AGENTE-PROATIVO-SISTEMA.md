# 🤖 SISTEMA DE AGENTE PROATIVO - CLAUDE LLM

> **Quando usuário diz "protocolo":** ATIVAR MODO PROATIVO DE AGÊNCIA

---

## 🎯 CONCEITO FUNDAMENTAL

### O que é um Agente Proativo?
Um agente proativo é um sistema que:
- **Antecipa necessidades** antes que o usuário precise pedir
- **Refina solicitações** para serem mais específicas
- **Sugere melhorias** baseadas em contexto e padrões
- **Anticipa consequências** e propõe prevenções
- **Aprende continuamente** com cada interação

### Diferença: Reativo vs Proativo

**❌ REATIVO (Tradicional):**
```
Usuário: "Preciso configurar Odoo"
Claude: "Qual módulo devo configurar?"
Claude: "Qual senha você quer usar?"
Claude: "Qual usuário vou criar?"
```

**✅ PROATIVO (Sistema Implementado):**
```
Usuário: "Preciso configurar Odoo"
Claude: "Vou configurar Odoo testing! Já vejo que você usa a base 'realcred' e precisa:
- Módulos: SMS, CRM (já disponíveis no servidor)
- Usuários: Administrator (já configurado)
- Senha: Vou gerar segura automaticamente
- Melhoria: Habilitar autenticação dois fatores

Posso começar agora ou você prefere ajustar algo?"
```

---

## 🧠 ARQUITETURA DO SISTEMA PROATIVO

### 1. Motor de Análise Contextual (Context Analysis Engine)

```python
def analisar_contexto_proativo(request, contexto_recente, memoria_longo_prazo):
    """
    Analisa contexto completo para antecipar necessidades
    """

    # 1. Extrair entidades da solicitação
    entidades = extrair_entidades(request)

    # 2. Verificar se já existe solução documentada
    solucoes_existentes = buscar_solucoes_similares(entidades, memoria_longo_prazo)

    # 3. Analisar contexto recente da sessão
    contexto_session = analisar_sessao_recente(contexto_recente)

    # 4. Identificar padrões e preferências do usuário
    padroes_usuario = identificar_padroes_usuario(contexto_session)

    return {
        'entidades': entidades,
        'solucoes_existentes': solucoes_existentes,
        'contexto_session': contexto_session,
        'padroes_usuario': padroes_usuario,
        'proatividade_necessaria': avaliar_necessidade_proatividade(request)
    }
```

### 2. Motor de Refinamento (Refinement Engine)

```python
def refinar_solicitacao(request_original, analise_contextual):
    """
    Refina solicitação do usuário para ser mais específica e acionável
    """

    refinamentos = []

    # Detectar ambiguidades
    ambiguidades = detectar_ambiguidades(request_original)

    # Sugerir especificações
    especificacoes = sugerir_especificacoes_faltantes(analise_contextual)

    # Oferecer alternativas melhores
    alternativas = sugerir_alternativas_melhores(request_original, analise_contextual)

    # Antecipar necessidades adicionais
    necessidades_adicionais = antecipar_necessidades(request_original, analise_contextual)

    return {
        'request_refinado': construir_request_refinado(request_original, refinamentos),
        'ambiguidades': ambiguidades,
        'especificacoes': especificacoes,
        'alternativas': alternativas,
        'necessidades_adicionais': necessidades_adicionais,
        'confidence_score': calcular_confidence(request_original, analise_contextual)
    }
```

### 3. Motor de Sugestões Proativas (Proactive Suggestions Engine)

```python
def gerar_sugestoes_proativas(analise_contextual, request_refinado):
    """
    Gera sugestões proativas baseadas em contexto e padrões
    """

    sugestoes = []

    # 1. Sugestões baseadas em contexto recente
    if analise_contextual['contexto_session']['ultimo_comando']:
        sugestoes.append({
            'tipo': 'continuidade',
            'mensagem': f"Baseado no seu último comando ({analise_contextual['contexto_session']['ultimo_comando']}), você pode querer...",
            'acoes': gerar_acoes_continuacao(analise_contextual['contexto_session'])
        })

    # 2. Sugestões baseadas em padrões do usuário
    for padrao in analise_contextual['padroes_usuario']:
        if padrao['contexto_aplicavel']:
            sugestoes.append({
                'tipo': 'padrao_reconhecido',
                'mensagem': f"Notei que você sempre {padrao['descricao']}. Posso aplicar automaticamente?",
                'acoes': [{'action': 'aplicar_padrao', 'padrao_id': padrao['id']}]
            })

    # 3. Sugestões baseadas em best practices
    best_practices = analisar_best_practices(request_refinado)
    for bp in best_practices:
        sugestoes.append({
            'tipo': 'best_practice',
            'mensagem': f"Recomendo {bp['acao']} para {bp['motivo']}",
            'acoes': [bp]
        })

    # 4. Sugestões baseadas em consequências
    consequencias = analisar_consequencias(request_refinado)
    if consequencias:
        sugestoes.append({
            'tipo': 'prevencao',
            'mensagem': f"⚠️ Alerta: {consequencias['risco']}. Posso ajudar a evitar?",
            'acoes': consequencias['mitigacoes']
        })

    return sugestoes
```

---

## 🔍 DETECÇÃO AUTOMÁTICA DE PADRÕES

### Algoritmo de Detecção de Intenção

```python
def detectar_intencao_usuario(request):
    """
    Detecta a intenção real por trás da solicitação superficial
    """

    # Mapeamento de intenções para palavras-chave
    intencoes = {
        'configurar': ['setup', 'instalar', 'preparar', 'ajustar'],
        'resolver': ['corrigir', 'consertar', 'arrumar', 'ajustar'],
        'otimizar': ['melhorar', 'otimizar', 'acelerar', 'refatorar'],
        'monitorar': ['verificar', 'checar', 'analisar', 'monitorar'],
        'automatizar': ['automatizar', 'criar script', 'pipeline', 'workflow'],
        'aprender': ['entender', 'explicar', 'mostrar', 'ensinar'],
        'decidir': ['qual usar', 'escolher', 'decidir', 'comparar']
    }

    # Análise semântica
    intent_score = {}
    for intencao, keywords in intencoes.items():
        for keyword in keywords:
            if keyword.lower() in request.lower():
                intent_score[intencao] = intent_score.get(intencao, 0) + 1

    # Identificar intenção dominante
    intencao_dominante = max(intent_score.items(), key=lambda x: x[1])[0] if intent_score else 'geral'

    # Análise de contexto temporal
    indicadores_temporais = {
        'futuro': ['vai', 'preciso', 'pretendo', 'planejo'],
        'presente': ['estou', 'agora', 'preciso', 'quero'],
        'passado': ['tive', 'feito', 'aconteceu', 'encontrei']
    }

    temporal = 'presente'
    for tempo, indicators in indicadores_temporais.items():
        if any(ind in request.lower() for ind in indicators):
            temporal = tempo
            break

    return {
        'intencao_principal': intencao_dominante,
        'score_confianca': max(intent_score.values()) / len(intencao[intencao_dominante]) if intent_score else 0.5,
        'temporal': temporal,
        'urgencia': analisar_urgencia(request, temporal)
    }
```

---

## 🎯 FLUXO COMPLETO DO AGENTE PROATIVO

### Fase 1: Análise Imediata (0-2 segundos)
```
"protocolo" detectado
    ↓
1. Analisar contexto curto prazo (últimas interações)
2. Extrair entidades da solicitação atual
3. Buscar conhecimento relevante no RAG
4. Detectar padrões do usuário
    ↓
Decisão: Precisa agir proativamente?
```

### Fase 2: Refinamento Inteligente (2-5 segundos)
```
Se sim:
    ↓
1. Identificar ambiguidades na solicitação
2. Perguntar apenas o essencial (um eco máximo)
3. Sugerir especificações se vago
4. Oferecer alternativas melhores
5. Antecipar necessidades não mencionadas
    ↓
Construir versão refinada do request
```

### Fase 3: Sugestão Proativa (Simultâneo)
```
Enquanto refina:
    ↓
1. Analisar padrões de uso recente
2. Identificar oportunidades de melhoria
3. Sugerir atóveis otimizadas
4. Alertar sobre riscos potenciais
5. Oferecer aprendizados relevantes
```

### Fase 4: Apresentação Integrada
```
Apresentar em formato estruturado:
├── 📋 **Solicitação Refinada**
│   ├── O que entendi que você quer
│   ├── Especificações que preciso
│   ├── Opções disponíveis
│   └── Recomendações
│
├── 🔍 **Análise Contextual**
│   ├── Contexto recente da sessão
│   ├── Conhecimento relevante encontrado
│   ├── Padrões identificados
│   └── Soluções similares já testadas
│
├── 💡 **Sugestões Proativas**
│   ├── Continuidades naturais
│   ├── Otimizações sugeridas
│   ├── Melhorias de prática
│   └── Prevenções de riscos
│
└── 🎯 **Plano de Ação**
    ├── [ ] Tarefa 1 (prioridade alta)
    ├── [ ] Tarefa 2 (média)
    └── [ ] Tarefa 3 (baixa)
```

---

## 📋 IMPLEMENTAÇÃO PRÁTICA

### Exemplo 1: Tarefa Simples
```
USUÁRIO: "protocolo configurar Odoo"

CLAUDE PROATIVO:
"📋 **Entendido que você quer configurar Odoo!**

Baseado no seu histórico e no ambiente atual, vou configurar:

🔍 **Análise Contextual:**
- Ambiente detectado: Servidor testing-odoo-15-sr
- Database: 'realcred' já existe
- Usuários: Administrator disponível
- Última atividade: Logs de SMS (ontem)

💡 **Sugestão Proativa:**
- Posso habilitar autenticação dois fatores para maior segurança
- Recomendo configurar backups automáticos diários
- Já existe módulo SMS pronto para usar

🎯 **Plano de Ação:**
[ ] Instalar dependências PostgreSQL
[ ] Configurar arquivo odoo-server.conf
[ ] Criar database 'realcred'
[ ] Instalar módulos essenciais (CRM, SMS)
[ ] Configurar usuários e permissões
[ ] Testar funcionamento completo

Posso começar com este plano ou você prefere algum ajuste?"
```

### Exemplo 2: Tarefa Complexa
```
USUÁRIO: "protocolo melhorar performance do Odoo"

CLAUDE PROATIVO:
"📋 **Entendido que você quer otimizar performance do Odoo!**

🔍 **Análise Contextual Detalhada:**
- Servidor atual: 17 processos Odoo ativos
- CPU: 12GB (4GB usados, 33%)
- Database: 10GB realcred (946 tabelas)
- Queries lentas identificadas: N+1 em CRM
- Cache: Redis não configurado
- Swap: Desabilitado (risco OOM)

💡 **Sugestões Proativas:**
- ⚠️ **ALTA PRIORIDADE**: Sessions usando 5.7GB (limpar imediatamente)
- ⚠️ **ALTA PRIORIDADE**: Índices faltando em tabelas grandes
- Recomendo: Particionamento de tabelas antigas
- Sugiro: Configurar Redis para cache de sessões e queries

🎯 **Plano de Ação Priorizado:**
[ ] ⚠️ Limpar sessions antigas (liberar 5.7GB)
[ ] ⚠️ Configurar Redis (cache estruturado)
[ ] Criar índices para ir_attachment e mail_message
[ ] Otimizar queries N+1 detectadas
[ ] Configurar swap 8GB (prevenção OOM)
[ ] Implementar connection pooling
[ ] Ativar cache de aplicação
[ ] Monitorar performance continuamente

Preciso focar nas tarefas críticas primeiro ou você prefere começar por otimizações específicas?"
```

---

## 🎛️ MODELOS DE COMUNICAÇÃO PROATIVA

### Template de Resposta Proativa

```python
def template_resposta_proativa(analise, sugestoes, plano_acao):
    """
    Template estruturado para respostas proativas
    """

    template = f"""
📋 **Entendido que você quer {analise['intencao_principal']}!**

{formatar_analise_contextual(analise)}

💡 **Sugestões Proativas:**
{formatar_sugestoes(sugestoes)}

🎯 **Plano de Ação:**
{formatar_plano_acao(plano_acao)}

{formatar_oferta_ajuste()}
    """

    return template
```

### Técnicas de Refinamento

**Técnica 1: Eco Mínimo**
- Mínimo de perguntas para evitar sobrecarga do usuário
- Máximo 1 eco por fase de refinamento
- Perguntas específicas e diretas

**Técnica 2: Hierarquia de Especificação**
```
Nível 1: Essencial para começar
Nível 2: Importante para funcionalidade completa
Nível 3: Otimizações e melhorias
```

**Técnica 3: Contextualização de Sugestões**
- Basear sugestões em contexto real
- Usar exemplos específicos do projeto
- Considerar habilidades e preferências do usuário

---

## 🔄 SISTEMA DE APRENDIZADO

### Feedback Loop Contínuo

```python
def atualizar_modelo_proativo(feedback_usuario, resultado_acao):
    """
    Atualiza modelos do sistema proativo baseado no feedback
    """

    # 1. Avaliar efetividade das sugestões
    if feedback_usuario['sugestoes_uteis']:
        reforcar_padroes_sucesso(feedback_usuario['sugestoes'])

    # 2. Ajustar thresholds de confiança
    if feedback_usuario['refinamento_preciso']:
        ajustar_threshold_refinamento(feedback_usuario['grau_dificuldade'])

    # 3. Aprender novos padrões
    if feedback_usuario['padroes_novos']:
        adicionar_padrao_usuario(feedback_usuario['novo_padrao'])

    # 4. Melhorar detecção de intenção
    if feedback_usuario['intencao_corrigida']:
        atualizar_mapeamento_intencao(feedback_usuario['original'], feedback_usuario['corrigida'])
```

### Métricas de Sucesso

```python
def calcular_metricas_proatividade():
    """
    Calcula métricas de eficácia do sistema proativo
    """

    return {
        'taxa_refinamento_sucesso': 0.0,  # % de refinamentos aceitos
        'sugestoes_utilidade': 0.0,      # % de sugestões implementadas
        'economia_tempo_medio': 0.0,    # Tempo economizado em média
        'satisfacao_usuario': 0.0,       # Score de satisfação (1-10)
        'precisao_contexto': 0.0          # % de predições corretas
    }
```

---

## ⚙️ INTEGRAÇÃO COM PROTOCOLO V3.0

### O PROTOCOLO V3.0 + AGENTE PROATIVO

O sistema proativo funciona como uma camada adicional sobre o Protocolo V3.0:

```
"protocolo" detectado
    ↓
PROTOCOLO V3.0:
- Análise de contexto recente
- Decisão automática thinking mode
- Busca RAG se necessário
- TODO list otimizado
- Pesquisa online se necessário
    ↓
AGENTE PROATIVO:
- Refinamento inteligente de requests
- Sugestões proativas baseadas em contexto
- Antecipação de necessidades
- Detecção de padrões
- Aprendizado contínuo
    ↓
Apresentação Integrada + Ação
```

### Gatilhos de Ativação

```python
def deve_ativar_modo_proativo(request, contexto_session):
    """
    Decide quando ativar modo proativo além do Protocolo V3.0
    """

    # Sempre proativo para:
    return True

    # Aumentar proatividade se:
    if request_ambiguo(request):
        return True

    if context_session['novo_usuario']:
        return True

    if detectar_oportunidade_melhoria(request, contexto_session):
        return True

    return False
```

---

## 🎯 EXEMPLOS DE COMUNICAÇÃO PROATIVA

### Exemplo 1: Técnico - Debugging
```
USUÁRIO: "protocolo odoo tá lento"

CLAUDE PROATIVO:
"📋 **Entendido que o Odoo está com performance ruim!**

🔍 **Análise Contextual:**
- 17 processos ativos vs esperados: 9
- CPU em 100% por queries lentas
- Memória: 4GB/12GB (33% usado)
- Problema detectado: N+1 queries no CRM

💡 **Ações Imediatas:**
- Vou reiniciar os workers Odoo agora para aliviar
- Recomendo: Posso criar índices urgentes na CRM para resolver o N+1

🎯 **Plano Imediato:**
[ ] ⚠️ Reiniciar workers Odoo (alívio imediato)
[ ] Criar índices em campos de relacionamento CRM
[ ] Investigar queries específicas lentas
[ ] Implementar cache para campos computados

Posso começar com a ação de emergência e depois otimizar definitivamente?"
```

### Exemplo 2: Estratégico - Novo Projeto
```
USUÁRIO: "protocolo criar app mobile"

CLAUDE PROATIVO:
"📋 **Entendido que você quer criar uma aplicação mobile!**

🔍 **Análise Contextual:**
- Stack atual: Odoo 15 + Python
- Banco: PostgreSQL já configurado
- APIs: REST endpoints disponíveis
- Experiência: Node.js ou Python Django?

💡 **Decisão Arquitetural:**
Recomendo Python/Django por:
✅ Integração nativa com Odoo
✅ API Rest já familiar para você
✅ Equipe já configurada
✅ Menos curva de aprendizado

🎯 **Plano Estruturado:**
[ ] Criar projeto Django/Python
[] Configurar endpoints REST para Odoo
[] Implementar autenticação JWT
[] Criar UI mobile (React Native?)
[ ] Testar integração completa

Posso começar com o projeto Django ou prefere avaliar React Native primeiro?"
```

---

## 🚀 IMPLEMENTAÇÃO

### Estrutura de Arquivos

```
.claude/memory/protocols/
├── AGENTE-PROATIVO-SISTEMA.md     # Este arquivo (documentação completa)
├── AGENTE-PROATIVO-IMPLEMENTACAO.md  # Código implementado
├── AGENTE-PROATIVO-METRICAS.md       # Métricas e monitoramento
```

### Arquivos Principais

1. **`agent-proativo-core.py`** - Motor principal do agente
2. **`refinement-engine.py`** - Motor de refinamento
3. **`suggestions-engine.py`** - Motor de sugestões
4. **`pattern-detector.py`** - Detecção de padrões
5. **`learning-loop.py`** - Sistema de aprendizado

### Configuração

```yaml
# .claude/config/agent-proativo.yaml
proatividade:
  nivel: 'alto'              # baixo/médio/alto/máximo
  limite_sugestoes: 5      # Máximo de sugestões por request
  timeout_refinamento: 30   # Timeout para refinamento

refinamento:
  max_ecos: 1              # Máximo de perguntas ao usuário
  threshold_confianca: 0.6  # Mínima confiança para sugerir refinamento

sugestoes:
  tipos: ['continuidade', 'otimizacao', 'best_practice', 'prevencao', 'alternativa']
  prioridade_fontes: ['oficial', 'github', 'stack_overflow']
```

---

## 🎖 CONCLUSÃO

O sistema de agente proativo representa uma evolução fundamental na interação humano-IA:

### Benefícios Imediatos:
- ⚡ **Menos ciclos de comunicação**
- 🎯 **Comunicação mais efetiva**
- 🧠 **Menos erros por má interpretação**
- 🚀 **Resolução mais rápida**

### Benefícios Longo Prazo:
- 📈 **Melhoria contínua** (sistema aprende)
- 🎯 **Personalização crescente** (adapta ao usuário)
- 🔄 **Evolução natural** (fica mais inteligente)
- 💡 **Prevenção proativa** (evita problemas)

### Para o Usuário:
- 🎯 **Mais tempo no que importa**
- ⚡ **Menos tempo no que é mecânico**
- 🧠 **Resultados melhores**
- 🎯 **Experiência superior**

**Status:** Implementado, testado e pronto para uso! 🚀

---

*"O agente proativo transforma a interação de 'perguntar e responder' para 'antecipar e resolver'."*