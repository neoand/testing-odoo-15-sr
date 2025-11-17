# 📞 PROPOSTA: Contact Center Unificado SMS + WhatsApp
## Análise de Viabilidade e Plano de Implementação

**Data**: 2025-11-16
**Status**: 🔍 **AGUARDANDO APROVAÇÃO** - NÃO IMPLEMENTADO
**Ambiente**: Produção - SempreReal
**Risco**: 🟡 Médio (Requer planejamento cuidadoso)

---

## 🎯 OBJETIVO

Criar um **Contact Center Unificado** que integre SMS (Kolmeya) e WhatsApp (AcruxLab ChatRoom) em uma única interface de atendimento, aproveitando a arquitetura enterprise-grade do ChatRoom já existente.

---

## 📊 ANÁLISE REALIZADA

### ✅ Descobertas Principais

**1. WhatsApp Connector (AcruxLab) - Já Instalado:**
- 26 módulos ativos com **4.968 conversas** registradas
- Arquitetura profissional: Conversation → Message → Agent → Stage
- Features avançadas: Kanban, Bot, IA, Templates, CRM integration
- **60% do código é reutilizável para SMS!**

**2. Arquitetura ChatRoom:**
```
┌─────────────────────────────────────────────────┐
│           CONTACT CENTER FRONTEND               │
│        (Real-time Kanban + Chat View)           │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────┐
│            CONVERSATION LAYER                    │
│   ┌──────────────┐    ┌──────────────┐         │
│   │ Conversation │    │   Message    │         │
│   │  (Thread)    │────│  (Content)   │         │
│   └──────────────┘    └──────────────┘         │
│          │                    │                  │
│   ┌──────┴──────┐      ┌─────┴─────┐          │
│   │ Agent       │      │ Template  │          │
│   │ (Assignment)│      │ (Replies) │          │
│   └─────────────┘      └───────────┘          │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────┐
│          CONNECTOR LAYER (API)                   │
│   WhatsApp     │    SMS (Kolmeya)               │
│   Instagram    │    (A CRIAR)                   │
│   Messenger    │                                 │
└──────────────────────────────────────────────────┘
```

**3. Features Reutilizáveis:**
- ✅ Sistema de Conversas (threading, status new/current/done)
- ✅ Atribuição de Agentes (online/offline, auto-assign)
- ✅ Kanban Stages (pipeline visual)
- ✅ Templates de Mensagens
- ✅ Integração CRM/Parceiros
- ✅ Bus Real-time (notificações instantâneas)
- ✅ Activity Tracking (tarefas, follow-ups)
- ✅ Envio em Massa
- ✅ Sistema de Fila (CRON auto-assign/close)

---

## 🏗️ ARQUITETURA PROPOSTA

### Opção 1: **ADAPTAÇÃO** (Recomendado)

Criar módulo SMS que **herda/estende** a arquitetura ChatRoom:

```
contact_center_unified/
├── models/
│   ├── conversation.py       # Herda acrux.chat.conversation
│   ├── message.py            # Herda acrux.chat.message
│   ├── connector_sms.py      # Novo: SMS Connector
│   └── provider_kolmeya.py   # Novo: Kolmeya API
├── views/
│   ├── conversation_views.xml # Adiciona filtro SMS/WhatsApp
│   └── connector_sms_views.xml
└── controllers/
    └── webhooks_sms.py       # SMS webhooks (já criado!)
```

**Vantagens:**
- ✅ Reutiliza 60% código existente
- ✅ Interface única para SMS + WhatsApp
- ✅ Mesmos agentes, mesma fila
- ✅ Histórico unificado no parceiro
- ✅ Menor esforço de desenvolvimento

**Desvantagens:**
- ⚠️ Dependência do módulo AcruxLab (licença proprietária OPL-1)
- ⚠️ Atualizações do AcruxLab podem quebrar

### Opção 2: **FORK COMPLETO** (Não Recomendado)

Copiar toda arquitetura ChatRoom para módulo independente.

**Vantagens:**
- ✅ Independente do AcruxLab
- ✅ Controle total do código

**Desvantagens:**
- ❌ 10-12 semanas de desenvolvimento
- ❌ Duplicação de código (20+ modelos)
- ❌ Perda de atualizações do AcruxLab
- ❌ Manutenção duplicada

---

## 📋 PLANO DE IMPLEMENTAÇÃO (Opção 1)

### FASE 1: Preparação (Semana 1) ⚠️ SEM RISCO

**Objetivo**: Estudar e mapear sem tocar produção

**Tarefas:**
1. ✅ Análise da arquitetura ChatRoom (CONCLUÍDO)
2. Criar módulo novo `contact_center_sms` (development)
3. Mapear extensões necessárias
4. Testar em ambiente de DEV (não produção)
5. Documentar todas mudanças

**Impacto Produção**: ❌ ZERO (apenas leitura)

---

### FASE 2: Módulo SMS Connector (Semana 2-3) ⚠️ RISCO BAIXO

**Objetivo**: Criar connector SMS independente

**Tarefas:**
1. Criar modelo `contact.center.connector` (herda `acrux.chat.connector`)
2. Adicionar campos SMS:
   ```python
   connector_type = 'sms_kolmeya'  # Novo tipo
   sms_api_token = fields.Char()
   sms_segment_id = fields.Integer()
   sms_balance = fields.Float()
   sms_cost_per_message = fields.Float()
   ```
3. Implementar métodos API:
   ```python
   def _sms_send_message()
   def _sms_get_balance()
   def _sms_check_delivery()
   ```
4. Aproveitar webhooks já criados (kolmeya_webhooks.py)

**Impacto Produção**: 🟡 BAIXO
- Novo módulo instalado
- Não afeta WhatsApp existente
- Rollback: desinstalar módulo

---

### FASE 3: Conversas SMS (Semana 4) ⚠️ RISCO MÉDIO

**Objetivo**: Integrar SMS às conversas

**Tarefas:**
1. Estender `acrux.chat.conversation`:
   ```python
   channel_type = fields.Selection([
       ('whatsapp', 'WhatsApp'),
       ('sms', 'SMS'),
       ('instagram', 'Instagram'),
   ])
   ```
2. Adicionar filtros na view Kanban:
   - Minhas Conversas SMS
   - Minhas Conversas WhatsApp
   - Todas Conversas
3. Adicionar ícones visuais (SMS vs WhatsApp)

**Impacto Produção**: 🟡 MÉDIO
- Modifica modelo existente (adiciona campo)
- Views alteradas
- **Requer teste em DEV primeiro!**

---

### FASE 4: Mensagens SMS (Semana 5) ⚠️ RISCO MÉDIO

**Objetivo**: Enviar/receber SMS via interface unificada

**Tarefas:**
1. Adaptar `acrux.chat.message` para SMS:
   ```python
   # Remover validações WhatsApp para SMS
   # Adicionar contador de segmentos
   # Calcular custo por mensagem
   ```
2. Criar método de envio SMS
3. Processar webhooks Kolmeya → criar messages
4. Link SMS replies ao thread original (parent_id)

**Impacto Produção**: 🟡 MÉDIO
- Alteração em modelo crítico
- **Backup obrigatório antes!**

---

### FASE 5: Interface Unificada (Semana 6) ⚠️ RISCO BAIXO

**Objetivo**: UX/UI do Contact Center

**Tarefas:**
1. Dashboard unificado:
   - Total conversas abertas (SMS + WhatsApp)
   - Conversas por agente
   - Tempo médio de resposta
2. Filtros rápidos:
   - Ver só SMS
   - Ver só WhatsApp
   - Ver todos canais
3. Cores/ícones por canal

**Impacto Produção**: 🟢 BAIXO
- Apenas views/UI
- Fácil rollback

---

### FASE 6: Features Avançadas (Semana 7-8) ⚠️ RISCO BAIXO

**Objetivo**: Recursos adicionais

**Tarefas:**
1. Templates SMS (aproveitar sms.template existente)
2. Envio em massa SMS (aproveitar whatsapp_connector_mass)
3. Relatórios unificados
4. Auto-resposta (bot) para SMS

**Impacto Produção**: 🟢 BAIXO
- Features opcionais
- Podem ser adicionadas gradualmente

---

## ⚠️ RISCOS E MITIGAÇÕES

### Risco 1: Quebrar WhatsApp Existente
**Probabilidade**: Média
**Impacto**: Alto (4.968 conversas afetadas)

**Mitigação:**
- ✅ Testar em ambiente de DEV primeiro
- ✅ Backup completo antes de cada fase
- ✅ Deploy em horário de baixo uso (madrugada)
- ✅ Ter plano de rollback testado
- ✅ Monitorar logs após cada deploy

### Risco 2: Licença AcruxLab (OPL-1)
**Probabilidade**: Baixa
**Impacto**: Médio

**Mitigação:**
- ✅ Não modificar código fonte do AcruxLab
- ✅ Apenas herdar/estender (permitido pela licença)
- ✅ Manter créditos e links do AcruxLab
- ✅ Documentar que estamos usando arquitetura deles

### Risco 3: Performance
**Probabilidade**: Baixa
**Impacto**: Médio

**Mitigação:**
- ✅ Índices no banco de dados
- ✅ Cache de conversas ativas
- ✅ Monitorar query time
- ✅ Otimizar bus notifications

### Risco 4: Conflito de Dados
**Probabilidade**: Média
**Impacto**: Alto

**Mitigação:**
- ✅ Unique constraint: (number, channel_type, connector_id)
- ✅ Validação antes de criar conversa
- ✅ Log de erros detalhado
- ✅ Retry mechanism

---

## 💰 ESTIMATIVA DE ESFORÇO

### Opção 1: Adaptação (Recomendado)
- **Tempo**: 6-8 semanas
- **Complexidade**: Média
- **Risco**: Médio
- **Reuso de Código**: 60%

### Opção 2: Fork Completo
- **Tempo**: 10-12 semanas
- **Complexidade**: Alta
- **Risco**: Alto
- **Reuso de Código**: 0%

---

## 🎁 BENEFÍCIOS ESPERADOS

### Para Agentes:
- ✅ Interface única para todos canais
- ✅ Histórico unificado do cliente
- ✅ Mesma fila de atendimento
- ✅ Templates compartilhados
- ✅ Menos sistemas para aprender

### Para Gestores:
- ✅ Dashboard consolidado
- ✅ Métricas unificadas (tempo resposta, SLA)
- ✅ Relatórios por canal/agente
- ✅ Melhor distribuição de carga

### Para Clientes:
- ✅ Resposta mais rápida (agente vê tudo)
- ✅ Contexto preservado entre canais
- ✅ Flexibilidade (pode escolher canal)

### Para TI:
- ✅ Menos duplicação de código
- ✅ Manutenção centralizada
- ✅ Aproveitamento de features já prontas

---

## 📊 COMPARAÇÃO COM SISTEMA ATUAL

### Sistema Atual (Separado):
```
SMS (nosso módulo)          WhatsApp (AcruxLab)
├── sms.message             ├── acrux.chat.conversation
├── sms.provider            ├── acrux.chat.message
└── sms.compose             ├── Kanban stages
                            ├── Agent assignment
                            ├── Real-time bus
                            └── Templates
```
**Problema**: Duplicação, interfaces separadas, sem visão unificada

### Sistema Proposto (Unificado):
```
Contact Center Unificado
├── Conversation (SMS + WhatsApp + Instagram)
├── Message (multi-canal)
├── Agent (atende todos canais)
├── Kanban (pipeline único)
├── Templates (compartilhados)
└── Dashboard (métricas consolidadas)
```
**Benefício**: Tudo em um só lugar, melhor UX, menos duplicação

---

## 🚦 DECISÃO NECESSÁRIA

### Preciso de sua aprovação para:

**1. Qual opção seguir?**
- [ ] Opção 1: Adaptação (herdar ChatRoom) - 6-8 semanas
- [ ] Opção 2: Fork completo (independente) - 10-12 semanas
- [ ] Opção 3: Manter separado (não integrar)

**2. Se aprovar Opção 1, quando começar?**
- [ ] Imediatamente (próxima semana)
- [ ] Após testes em DEV (2 semanas)
- [ ] Aguardar outro momento

**3. Prioridades:**
- [ ] Focar em funcionalidade básica primeiro
- [ ] Incluir features avançadas (bot, IA)
- [ ] Fazer incremental (fase por fase)

---

## 📝 CHECKLIST PRÉ-IMPLEMENTAÇÃO

Antes de começar qualquer desenvolvimento, preciso garantir:

### Ambiente:
- [ ] Criar backup completo do banco de dados
- [ ] Ter ambiente de DEV separado para testes
- [ ] Configurar Git/versionamento dos módulos custom
- [ ] Documentar estado atual (screenshot das views)

### Aprovações:
- [ ] Aprovação do usuário (você)
- [ ] Verificar licença AcruxLab (OPL-1) - ok para herança?
- [ ] Definir janela de manutenção (deploy)
- [ ] Notificar equipe sobre mudanças

### Técnico:
- [ ] Estudar código completo do ChatRoom
- [ ] Mapear todas dependências
- [ ] Criar plano de rollback testado
- [ ] Preparar scripts de migração

---

## 🎯 RECOMENDAÇÃO FINAL

**Recomendo fortemente a Opção 1 (Adaptação)** pelos seguintes motivos:

1. **Reutiliza arquitetura enterprise-grade** já testada em produção
2. **60% menos código** para escrever/manter
3. **Interface unificada** melhora muito a UX
4. **Menor risco** (herança vs fork completo)
5. **Aproveitamento de features** já prontas (Kanban, Bot, IA)
6. **Timeline realista** (6-8 semanas vs 12 semanas)

**MAS** preciso de sua aprovação antes de tocar em QUALQUER coisa em produção!

---

## ❓ PRÓXIMOS PASSOS

Se você aprovar, farei:

1. **Criar ambiente de DEV** (clone do prod)
2. **Implementar Fase 1** em DEV
3. **Mostrar protótipo** para validação
4. **Só depois** tocar em produção

---

## 📞 DÚVIDAS FREQUENTES

**P: Vai quebrar o WhatsApp atual?**
R: Não, se feito corretamente. Vamos apenas ADICIONAR campos/features, não remover. O WhatsApp continua funcionando normalmente.

**P: Precisa parar o sistema?**
R: Apenas restart do Odoo (5 minutos) em horário combinado.

**P: E se der errado?**
R: Rollback via backup. Por isso insisto em testar em DEV primeiro.

**P: Posso testar antes de aprovar?**
R: SIM! Posso criar protótipo em DEV para você ver funcionando.

**P: Vai afetar os 4.968 chats existentes?**
R: Não. Eles continuam intactos. Apenas ganham um campo extra (channel_type).

---

**🚨 IMPORTANTE: Este documento é apenas PROPOSTA. Nada foi implementado ainda. Aguardo sua decisão!**
