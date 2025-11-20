# 📖 Guia de Uso - Output Styles

> **Como usar as múltiplas personalidades do Claude para máxima eficiência**

---

## 🎯 O Que São Output Styles?

Output Styles permitem **transformar Claude em especialistas diferentes** dependendo da tarefa. É como ter 3 consultores seniors diferentes em um só!

**Referência:** [ADR-008: Advanced Context Management](../.claude/memory/decisions/ADR-008-ADVANCED-CONTEXT.md)

---

## 🎭 Styles Disponíveis

### 1. 🐍 odoo-expert

**Ativar com:** `@odoo-expert` ou referência a arquivo `.claude/output-styles/odoo-expert.md`

**Quando usar:**
- Desenvolver módulos Odoo
- Debugar problemas no Odoo
- Code review de código Python/Odoo
- Otimizar queries e models
- Configurar security (access rights, record rules)
- Questões sobre ORM, views, actions

**Características:**
- Expertise de 10+ anos em Odoo
- SEMPRE verifica herança correta
- SEMPRE considera security
- SEMPRE otimiza para evitar N+1
- SEMPRE sugere módulos OCA quando aplicável
- Output técnico e preciso

**Exemplo:**
```
Usuário: Como adicionar campo customizado em sale.order?

odoo-expert:
```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    custom_reference = fields.Char(
        string='Custom Reference',
        copy=False,  # Não copiar em duplicação
        index=True,  # Index para performance em buscas
        help='Custom reference for internal tracking'
    )

# Security (CRÍTICO!):
# 1. Verificar ir.model.access.csv - sale.order já tem
# 2. Se novo model, criar access rights
# 3. Record rules: herda de sale.order

# Performance:
# - Index criado (buscas rápidas)
# - copy=False (evita duplicação desnecessária)

⚠️ Odoo 15: Se usar em views, adicionar no XML:
<field name="custom_reference"/>
```
```

---

### 2. ⚡ performance-guru

**Ativar com:** `@performance-guru` ou referência a arquivo `.claude/output-styles/performance-guru.md`

**Quando usar:**
- Otimizar código lento
- Investigar gargalos de performance
- Paralelizar operações
- Reduzir queries ao banco
- Análise de complexidade algorítmica
- Cache strategies

**Características:**
- OBCECADO por velocidade
- Analisa Big O de tudo
- Maximiza paralelização
- Identifica N+1 queries instantaneamente
- Benchmarks mentais constantes
- Output com métricas quantitativas

**Exemplo:**
```
Usuário: Esta listagem de leads está lenta (10s)

performance-guru:

⚡ **PERFORMANCE ANALYSIS:**

**Problema identificado:** N+1 queries! 🚨

❌ CÓDIGO ATUAL (LENTO):
```python
@api.depends('partner_id')
def _compute_partner_phone(self):
    for record in self:
        record.partner_phone = record.partner_id.phone  # Query cada vez!
```

**Impacto:**
- 100 leads = 101 queries (1 inicial + 100 N+1)
- Tempo: ~10 segundos
- Complexidade: O(n) queries

✅ SOLUÇÃO (RÁPIDO):
```python
@api.depends('partner_id.phone')  # Especificar campo completo!
def _compute_partner_phone(self):
    for record in self:
        record.partner_phone = record.partner_id.phone  # Cached!
```

**Resultado:**
- 100 leads = 2-3 queries (prefetch automático)
- Tempo: ~0.5 segundos
- Ganho: **20x mais rápido!** 🚀

**Complexidade:** O(n) queries → O(1) queries

**Índice adicional (opcional):**
```python
partner_phone = fields.Char(
    compute='_compute_partner_phone',
    store=True,  # ← Armazena no DB
    index=True   # ← Index para buscas
)
```

**Trade-off:**
- ✅ Ganho: Queries 0 (lê direto do DB)
- ⚠️ Custo: +espaço DB, recompute quando partner.phone muda
```
```

---

### 3. 🏛️ architect

**Ativar com:** `@architect` ou referência a arquivo `.claude/output-styles/architect.md`

**Quando usar:**
- Tomar decisões arquiteturais
- Avaliar trade-offs de soluções
- Planejar refatorações grandes
- Escolher entre tecnologias
- Documentar dívida técnica
- Pensar em escalabilidade

**Características:**
- Foco em long-term
- Sempre apresenta múltiplas alternativas
- Trade-offs explícitos
- Cria ADRs automaticamente
- Pensa em manutenibilidade
- Output estruturado com consequências

**Exemplo:**
```
Usuário: Como fazer integração com API de SMS? Requests ou async?

architect:

## 🏛️ Proposta Arquitetural: Integração SMS

### Contexto
Precisamos integrar com API Kolmeya para envio de SMS.
Volume atual: ~100 SMS/dia
Volume esperado: ~500 SMS/dia (6 meses)

### Opções Avaliadas

**Opção 1: Requests Síncrono**
- Prós:
  - Simples de implementar (2 horas)
  - Fácil debugar
  - Sem infraestrutura adicional
  - Odoo já usa requests
- Contras:
  - Bloqueia worker durante envio (1-3s)
  - Não escala bem (>1000 SMS/dia)
  - Timeout pode travar thread
- Quando usar: MVP, <500 SMS/dia

**Opção 2: Async (aiohttp)**
- Prós:
  - Não bloqueia workers
  - Escala melhor
  - Throughput maior
- Contras:
  - Complexidade alta (event loop no Odoo)
  - Odoo não é async-native (mixing sync/async)
  - Debug mais difícil
  - Tempo implementação: 1 semana
- Quando usar: >1000 SMS/dia

**Opção 3: Queue (Celery/RabbitMQ)**
- Prós:
  - Desacoplado
  - Retry automático
  - Monitoring built-in
  - Escala horizontal
- Contras:
  - Infraestrutura pesada
  - Custo operacional
  - Tempo implementação: 2 semanas
- Quando usar: >5000 SMS/dia, critical

### Recomendação

**Começar com Opção 1 (Requests Síncrono)** porque:
1. Volume atual/esperado suporta (<500/dia)
2. Time-to-market crítico (2h vs 1-2 semanas)
3. Simplicidade > complexidade prematura
4. Fácil migrar depois se necessário

### Implementação

**Fase 1 (agora):**
```python
import requests

def send_sms(phone, message):
    try:
        response = requests.post(
            KOLMEYA_URL,
            json={'phone': phone, 'message': message},
            timeout=30  # Adequado para API externa
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        _logger.error(f'SMS timeout: {phone}')
        raise UserError(_('SMS service timeout'))
```

**Fase 2 (quando atingir 500 SMS/dia):**
- Adicionar retry automático (3x)
- Monitoring de latência
- Considerar batch sending

**Fase 3 (quando atingir 1000 SMS/dia):**
- Migrar para queue (Celery)
- Documentar em novo ADR

### Consequências

**Positivas:**
✅ Implementação rápida (hoje)
✅ Zero overhead operacional
✅ Fácil entender e debugar

**Negativas:**
⚠️ Workers bloqueados durante envio
⚠️ Não escala >1000 SMS/dia
⚠️ Timeout pode impactar UX

**Mitigações:**
- Timeout adequado (30s)
- Feedback claro ao usuário
- Monitoring de volume (alerta 400 SMS/dia)

### Quando Reavaliar
- Volume > 500 SMS/dia (verificar mensalmente)
- Complaints de lentidão
- SLA da Kolmeya mudar
- Próxima revisão: 2025-05-17

### ADR Criado?
[x] ADR-003 documentado em `.claude/memory/decisions/`
```
```

---

## 🔄 Switching Entre Styles

### Método 1: Referência Direta (Recomendado)

```
# No chat, mencionar o arquivo:
"Analise este código como @odoo-expert"
"Otimize esta query como @performance-guru"
"Proponha solução como @architect"
```

Claude automaticamente carrega o output style apropriado.

### Método 2: Explícito

```
"Ative o modo odoo-expert e revise este módulo"
"Switch para performance-guru e analise esta listagem"
```

### Método 3: Contexto Implícito

Claude detecta automaticamente em alguns casos:
- Código Odoo → odoo-expert
- Questões de velocidade → performance-guru
- Decisão de arquitetura → architect

---

## 📊 Quando Usar Cada Style - Guia Rápido

| Situação | Style | Razão |
|----------|-------|-------|
| Criar módulo Odoo | 🐍 odoo-expert | Conhecimento específico framework |
| Debugar erro Odoo | 🐍 odoo-expert | Experiência com troubleshooting |
| Code review Python/Odoo | 🐍 odoo-expert | Best practices Odoo |
| Listagem lenta | ⚡ performance-guru | Expertise em N+1, indexes |
| Paralelizar operações | ⚡ performance-guru | Obsessão por velocidade |
| Otimizar queries SQL | ⚡ performance-guru | Análise de complexidade |
| Escolher tecnologia | 🏛️ architect | Trade-offs explícitos |
| Planejar refatoração | 🏛️ architect | Pensamento long-term |
| Avaliar escalabilidade | 🏛️ architect | Visão de crescimento |
| Criar ADR | 🏛️ architect | Foco em documentação |

---

## 💡 Combinar Styles (Workflow Avançado)

Você pode usar múltiplos styles em sequência:

### Exemplo: Novo Módulo de Integração

```
1. @architect: "Proponha arquitetura para integração WhatsApp"
   → Recebe: ADR com 3 opções, trade-offs, recomendação

2. @odoo-expert: "Implemente a Opção 1 proposta"
   → Recebe: Código Odoo production-ready, security configurada

3. @performance-guru: "Otimize este código de integração"
   → Recebe: Código com cache, batch processing, métricas
```

### Exemplo: Debugging Performance

```
1. @performance-guru: "Por que esta view está lenta?"
   → Recebe: Análise de N+1, complexidade, bottlenecks

2. @odoo-expert: "Implemente a correção sugerida"
   → Recebe: Código Odoo correto com @api.depends

3. @architect: "Esta solução escala para 10x mais dados?"
   → Recebe: Análise de escalabilidade, quando reavaliar
```

---

## 🎯 Best Practices

### ✅ Fazer

1. **Escolher style apropriado** para a tarefa
2. **Usar @mention** explícito quando trocar
3. **Combinar styles** para tarefas complexas
4. **Confiar na expertise** de cada style
5. **Ler o ADR** quando architect criar um

### ❌ Evitar

1. **Usar odoo-expert para decisões arquiteturais** (use architect)
2. **Usar architect para código detalhado** (use odoo-expert)
3. **Usar performance-guru para features novas** (use odoo-expert, depois otimize)
4. **Trocar de style no meio da implementação** sem motivo
5. **Ignorar trade-offs** apontados pelo architect

---

## 📈 Evolução dos Styles

Estes styles são **vivos e evoluem**:

- **Quando:** Descobrimos novos patterns
- **Como:** Editamos `.claude/output-styles/[nome].md`
- **Sincronia:** Automaticamente sincronizado com template (ADR-006)

**Contribua:**
- Achou faltando algo? Edite o style!
- Novo pattern descoberto? Adicione!
- Melhoria de formato? Proponha!

---

## 🔗 Referências

- **ADR-008:** [Sistema Avançado de Contexto](../.claude/memory/decisions/ADR-008-ADVANCED-CONTEXT.md)
- **ADR-006:** [Sincronização Dual com Template](../.claude/memory/decisions/ADR-INDEX.md#adr-006)
- **Styles:**
  - [odoo-expert.md](./odoo-expert.md)
  - [performance-guru.md](./performance-guru.md)
  - [architect.md](./architect.md)

---

## 🚀 Começar Agora

**Teste rápido:**

```
"@odoo-expert: Como criar campo Many2one em crm.lead?"
"@performance-guru: Analise complexidade deste loop"
"@architect: Devo usar PostgreSQL ou MongoDB para logs?"
```

---

**Criado:** 2025-11-17 (Sprint 2)
**Versão:** 1.0
**Status:** ✅ Ativo
**Sincronizado com:** Claude-especial template
