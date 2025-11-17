# Análise Completa da Estrutura SMS Existente no Odoo 15

**Data:** 16/11/2025
**Autor:** Análise realizada via SSH no servidor odoo-rc
**Objetivo:** Mapear completamente a infraestrutura SMS existente para adaptar o módulo chatroom_sms_advanced

---

## 1. HIERARQUIA DE MÓDULOS

### Diagrama de Dependências

```
sms_base_sr (Base/Core)
    |
    +-- sms_kolmeya (Provider Integration)
            |
            +-- contact_center_sms (ChatRoom Integration)
                    |
                    +-- chatroom_sms_advanced (Advanced Features - NOVO)
```

### Descrição dos Módulos

#### 1.1. sms_base_sr
- **Tipo:** Módulo Base (application: True)
- **Versão:** 15.0.1.0.2
- **Dependências:** base, mail, contacts
- **Função:** Core do sistema SMS - modelos base, templates, wizard de envio
- **Caminho:** /odoo/custom/addons_custom/sms_base_sr/

#### 1.2. sms_kolmeya
- **Tipo:** Provider Integration
- **Versão:** 15.0.1.0.0
- **Dependências:** sms_base_sr, PyJWT (Python)
- **Função:** Implementação específica da API Kolmeya (gateway SMS)
- **Caminho:** /odoo/custom/addons_custom/sms_kolmeya/

#### 1.3. contact_center_sms
- **Tipo:** ChatRoom Integration (application: True)
- **Versão:** 15.0.1.0.2
- **Dependências:** whatsapp_connector, sms_base_sr, sms_kolmeya
- **Função:** Integra SMS ao WhatsApp ChatRoom para central unificada
- **Caminho:** /odoo/custom/addons_custom/contact_center_sms/

#### 1.4. chatroom_sms_advanced (NOSSO MÓDULO)
- **Tipo:** Advanced Features
- **Versão:** 15.0.1.0.0
- **Dependências:** base, web, mail, chatroom
- **STATUS:** Precisa ser COMPLETAMENTE ADAPTADO
- **Caminho:** /odoo/custom/addons_custom/chatroom_sms_advanced/

---

## 2. MODELOS EXISTENTES - DETALHAMENTO COMPLETO

### 2.1. sms.message (sms_base_sr)

**Nome Técnico:** `sms.message`
**Arquivo:** `/odoo/custom/addons_custom/sms_base_sr/models/sms_message.py`
**Inherit:** `mail.thread`, `mail.activity.mixin`
**Tabela BD:** `sms_message`

#### Campos Principais:

| Campo | Tipo | Descrição | Índice |
|-------|------|-----------|--------|
| partner_id | Many2one(res.partner) | Contato associado ao SMS | Sim |
| user_id | Many2one(res.users) | Usuário responsável | Não |
| provider_id | Many2one(sms.provider) | Provider SMS (Kolmeya) | Não |
| phone | Char | Número telefone internacional | Sim |
| body | Text | Conteúdo da mensagem | Não |
| direction | Selection | outgoing/incoming | Não |
| state | Selection | draft/outgoing/sent/delivered/error/rejected/expired/canceled | Sim |
| provider_message_id | Char | ID único do provider (Kolmeya) | Sim |
| provider_job_id | Char | ID do lote/job no provider | Não |
| parent_id | Many2one(sms.message) | Mensagem original (se for resposta) | Sim |
| provider_reference | Char | Referência customizada enviada ao provider | Não |
| sent_date | Datetime | Data/hora de envio | Não |
| delivered_date | Datetime | Data/hora de entrega | Não |
| error_message | Text | Mensagem de erro (se houver) | Não |
| retry_count | Integer | Contador de tentativas | Não |
| char_count | Integer | Total de caracteres | Não |
| sms_count | Integer | Quantidade de segmentos SMS | Não |
| cost | Float | Custo em R$ (padrão: 0.10) | Não |

#### Métodos Principais:

```python
# Envio
def action_send(self):
    """Envia SMS via provider"""
    # Valida estado (draft ou error)
    # Chama provider_id._send_sms(self)
    # Atualiza estado para 'outgoing'
    # Registra sent_date
    # Trata erros (retry_count)

# Gerenciamento
def action_cancel(self):
    """Cancela SMS (apenas draft/outgoing)"""

def action_reset_to_draft(self):
    """Reseta para draft"""

# Validações
@api.constrains('phone')
def _check_phone(self):
    """Valida formato do telefone (10-15 dígitos)"""

# Computados
@api.depends('body')
def _compute_char_count(self):
    """Conta caracteres da mensagem"""

@api.depends('char_count')
def _compute_sms_count(self):
    """Calcula segmentos SMS (160 chars ou 153 se > 160)"""

# Lifecycle Hooks
def create(self, vals):
    """Posta no chatter do partner quando criado"""

def write(self, vals):
    """Posta no chatter quando estado muda"""
```

#### Valores de State:

- `draft` - Rascunho
- `outgoing` - Em envio
- `sent` - Enviado ao provider
- `delivered` - Entregue ao destinatário
- `error` - Erro no envio
- `rejected` - Rejeitado pelo provider
- `expired` - Expirado
- `canceled` - Cancelado

---

### 2.2. sms.provider (sms_base_sr)

**Nome Técnico:** `sms.provider`
**Arquivo:** `/odoo/custom/addons_custom/sms_base_sr/models/sms_provider.py`
**Tabela BD:** `sms_provider`

#### Campos Principais:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| name | Char | Nome do provider |
| provider_type | Selection | mock/kolmeya |
| sequence | Integer | Ordem (padrão: 10) |
| active | Boolean | Ativo/Inativo |
| company_id | Many2one(res.company) | Empresa |
| message_count | Integer | Total de mensagens (computed) |
| delivered_count | Integer | Mensagens entregues (computed) |
| error_count | Integer | Mensagens com erro (computed) |

#### Métodos Principais:

```python
def _send_sms(self, sms_message):
    """Envia SMS individual
    - provider_type == 'mock': simula envio (testing)
    - Deve ser sobrescrito em módulos específicos (kolmeya)
    """

def _send_batch(self, messages_data):
    """Envia lote de SMS
    - messages_data: list of {'phone', 'message', 'reference'}
    - NotImplementedError - implementar no provider específico
    """

def action_view_messages(self):
    """Abre view com todas mensagens deste provider"""
```

---

### 2.3. sms.provider (sms_kolmeya - EXTENDS sms_base_sr)

**Nome Técnico:** `sms.provider` (inherit)
**Arquivo:** `/odoo/custom/addons_custom/sms_kolmeya/models/sms_provider_kolmeya.py`

#### Campos Adicionais Kolmeya:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| provider_type | Selection | Adiciona opção 'kolmeya' |
| kolmeya_api_token | Char | Bearer token API (secreto) |
| kolmeya_segment_id | Integer | ID do segmento (padrão: 109 - CORPORATIVO) |
| kolmeya_webhook_secret | Char | Secret JWT para validar webhooks |
| kolmeya_balance | Float | Saldo em R$ (readonly) |
| last_balance_check | Datetime | Última consulta de saldo |

#### Métodos Override:

```python
def _send_sms(self, sms_message):
    """Override - envia via Kolmeya API
    - Limpa número de telefone
    - Chama KolmeyaAPI.send_sms()
    - Processa resultado (valids/invalids/blacklist)
    - Atualiza provider_message_id, provider_job_id
    """

def _send_batch(self, messages_data):
    """Override - envia lote via Kolmeya
    - Suporta até 1000 mensagens por batch
    - Retorna job_id do Kolmeya
    """

def action_check_balance(self):
    """Consulta saldo Kolmeya"""

def action_check_job_status(self):
    """Abre wizard para consultar status de job"""
```

---

### 2.4. KolmeyaAPI (sms_kolmeya - Helper Class)

**Tipo:** Classe Python (não é Model Odoo)
**Arquivo:** `/odoo/custom/addons_custom/sms_kolmeya/models/kolmeya_api.py`

#### Configuração:

```python
BASE_URL = "https://kolmeya.com.br/api/v1"

def __init__(self, token, segment_id=109):
    """
    token: Bearer token (adiciona "Bearer " se necessário)
    segment_id: Centro de custo Kolmeya (padrão: 109)
    """
```

#### Métodos Disponíveis:

##### Envio de SMS:
```python
send_sms(phone, message, reference=None, webhook_url=None)
    # Retorna: {'id': job_id, 'valids': [...], 'invalids': [...], 'blacklist': [...]}

send_batch(messages_list, max_batch_size=1000)
    # messages_list: [{'phone': ..., 'message': ..., 'reference': ...}]
    # Retorna: lista de respostas (uma por batch)
```

##### Consultas de Status:
```python
check_job_status(job_id)
    # Retorna: {'id', 'status', 'status_code', 'messages': [...]}

check_message_status(message_id)
    # Retorna: status detalhado da mensagem
```

##### Saldo e Conta:
```python
get_balance()
    # Retorna: {'saldo': float, 'balance_str': 'R$9.396,84'}
    # Converte formato brasileiro para float
```

##### Templates:
```python
get_templates()
    # Retorna: templates configurados no Kolmeya
```

##### Blacklist:
```python
add_to_blacklist(phones_list)
remove_from_blacklist(phones_list)
get_blacklist()
```

##### Respostas:
```python
get_replies(page=1)
    # Retorna: respostas SMS dos últimos 7 dias
```

##### Relatórios:
```python
get_report(start_date, end_date, page=1)
    # start_date/end_date: formato 'YYYY-MM-DD'
    # Retorna: relatório do período
```

#### Tratamento de Erros:

- **Rate Limiting:** Verifica header `X-RateLimit-Remaining`
- **HTTP 429:** Levanta UserError com mensagem de rate limit
- **Timeouts:** 30 segundos padrão
- **Erros HTTP:** Extrai campo `errors` do JSON de resposta

---

### 2.5. sms.template (sms_base_sr)

**Nome Técnico:** `sms.template`
**Arquivo:** `/odoo/custom/addons_custom/sms_base_sr/models/sms_template.py`
**Tabela BD:** `sms_template`

#### Campos:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| name | Char | Nome do template |
| code | Char | Código único |
| message_template | Text | Template com placeholders Python ({name}, {cpf}, etc) |
| message_preview | Text | Preview com dados exemplo (computed) |
| applies_to | Selection | res_partner/contacts_realcred/crm_lead/all |
| active | Boolean | Ativo/Inativo |
| admin_only | Boolean | Apenas admin pode editar |
| use_count | Integer | Contador de uso |

#### Métodos:

```python
def render(self, data_dict):
    """Renderiza template com dados reais
    data_dict: {'name': 'João', 'cpf': '123...'}
    Retorna: string com placeholders substituídos
    Levanta: ValidationError se variável faltando
    """

def _track_usage(self):
    """Incrementa use_count"""

@api.constrains('message_template')
def _check_template_syntax(self):
    """Valida sintaxe do template"""
```

---

### 2.6. sms.compose (sms_base_sr - Wizard)

**Nome Técnico:** `sms.compose` (TransientModel)
**Arquivo:** `/odoo/custom/addons_custom/sms_base_sr/wizard/sms_compose.py`

#### Campos:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| template_id | Many2one(sms.template) | Template selecionado |
| partner_ids | Many2many(res.partner) | Destinatários |
| phone_numbers | Text | Preview dos telefones (computed) |
| body | Text | Corpo da mensagem |
| provider_id | Many2one(sms.provider) | Provider (default: Kolmeya) |
| char_count | Integer | Contador de caracteres (computed) |

#### Métodos:

```python
def action_send_sms(self):
    """Envia SMS para todos partners selecionados
    - Valida telefones
    - Renderiza template para cada partner
    - Cria sms.message para cada um
    - Chama action_send() em cada
    """

@api.onchange('template_id')
def _onchange_template_id(self):
    """Renderiza template quando selecionado
    - Usa primeiro partner para preview
    - Fallback para body padrão se erro
    """
```

---

### 2.7. res.partner (sms_base_sr - EXTENDS)

**Nome Técnico:** `res.partner` (inherit)
**Arquivo:** `/odoo/custom/addons_custom/sms_base_sr/models/res_partner.py`

#### Campos Adicionais:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| sms_message_ids | One2many(sms.message) | Todas mensagens SMS |
| sms_count | Integer | Total de SMS (computed) |
| sms_sent_count | Integer | SMS enviados (computed) |
| sms_received_count | Integer | SMS recebidos (computed) |
| last_sms_date | Datetime | Data do último SMS (computed) |

#### Métodos Adicionais:

```python
def action_view_sms_messages(self):
    """Abre view com todos SMS do partner"""

def action_send_sms(self):
    """Abre wizard sms.compose para enviar SMS"""
```

---

## 3. MODELOS CONTACT_CENTER_SMS (Integração ChatRoom)

### 3.1. acrux.chat.connector (contact_center_sms - EXTENDS)

**Arquivo:** `/odoo/custom/addons_custom/contact_center_sms/models/connector_sms.py`

#### Campos Adicionais:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| connector_type | Selection | Adiciona 'sms' (Kolmeya) |
| sms_provider_id | Many2one(sms.provider) | Referência ao provider Kolmeya |
| sms_api_token | Char | Related de sms_provider_id.kolmeya_api_token |
| sms_segment_id | Integer | Related de sms_provider_id.kolmeya_segment_id |
| sms_balance | Float | Related de sms_provider_id.kolmeya_balance |
| sms_sent_count | Integer | Total SMS enviados (computed) |
| sms_received_count | Integer | Total SMS recebidos (computed) |
| sms_total_cost | Float | Custo total (computed) |

#### Métodos Override:

```python
def action_test_connection(self):
    """Override - para SMS testa saldo Kolmeya"""

def ca_request(self, url, data, method):
    """Override - SMS não usa ca_request, levanta erro"""
```

---

### 3.2. acrux.chat.conversation (contact_center_sms - EXTENDS)

**Arquivo:** `/odoo/custom/addons_custom/contact_center_sms/models/conversation.py`

**ESTE É O MODELO MAIS IMPORTANTE PARA INTEGRAÇÃO**

#### Campos Adicionais:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| channel_type | Selection | whatsapp/sms/instagram/messenger |
| sms_message_id | Many2one(sms.message) | SMS original que iniciou conversa |

#### Métodos Principais:

```python
@api.model
def create_from_sms(self, sms_message):
    """Cria conversa ChatRoom a partir de SMS recebido

    Fluxo:
    1. Valida que sms_message tem partner_id
    2. Busca conversa existente (mesmo phone + channel_type='sms')
    3. Se existe: adiciona ao thread
    4. Se não: cria nova conversa
    5. Auto-assign agente disponível
    6. Notifica via bus

    Returns: acrux.chat.conversation
    """

def _add_sms_to_thread(self, sms_message):
    """Adiciona SMS ao thread da conversa

    - Cria acrux.chat.message vinculado ao SMS
    - Atualiza last_received/last_activity
    - Notifica via bus se incoming
    """

def send_sms_message(self, body):
    """Envia SMS através da conversa ChatRoom

    Fluxo:
    1. Valida channel_type == 'sms'
    2. Busca provider Kolmeya
    3. Cria sms.message (outgoing)
    4. Envia via action_send()
    5. Adiciona ao thread

    Returns: sms.message
    """

def _auto_assign_agent(self):
    """Auto-atribui agente online disponível"""

def _notify_new_message(self, message):
    """Notifica via Odoo bus (WebSocket real-time)"""
```

---

### 3.3. acrux.chat.message (contact_center_sms - EXTENDS)

**Arquivo:** `/odoo/custom/addons_custom/contact_center_sms/models/message.py`

#### Campos Adicionais:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| sms_message_id | Many2one(sms.message) | Referência ao SMS original |
| is_sms | Boolean | True se message é do canal SMS (computed) |
| sms_segment_count | Integer | Segmentos SMS (computed) |
| sms_cost | Float | Custo aproximado (computed) |

#### Métodos:

```python
@api.depends('contact_id.channel_type')
def _compute_is_sms(self):
    """Marca como SMS baseado no channel_type da conversa"""

@api.depends('text', 'is_sms')
def _compute_sms_info(self):
    """Calcula segmentos e custo
    - 160 chars ASCII / 70 chars Unicode
    - R$ 0.10 por segmento
    """
```

---

## 4. WEBHOOKS KOLMEYA

### 4.1. Webhooks Base (sms_kolmeya)

**Arquivo:** `/odoo/custom/addons_custom/sms_kolmeya/controllers/kolmeya_webhooks.py`

#### Endpoint: /kolmeya/webhook/reply

**Método:** POST (JSON)
**Auth:** public (sem CSRF)

**Payload Esperado:**
```json
{
    "phone": "5548999999999",
    "message": "Resposta do cliente",
    "reference": "message_id",
    "data": "2025-11-15 14:30:00"
}
```

**Fluxo:**
1. Busca sms.message original via `provider_reference` ou `phone`
2. Busca partner por telefone (phone/mobile)
3. Cria novo `sms.message` (direction='incoming', state='delivered')
4. Vincula ao original via `parent_id`
5. Posta no chatter do original
6. Cria Activity para o usuário responsável

---

#### Endpoint: /kolmeya/webhook/status

**Método:** POST (JSON)
**Auth:** public (sem CSRF)

**Payload Esperado:**
```json
{
    "id": "message_uuid",
    "reference": "our_reference",
    "status": "entregue",
    "status_code": 3,
    "phone": "5548999999999"
}
```

**Mapeamento de Status:**
```python
status_map = {
    1: 'outgoing',   # Tentando enviar
    2: 'sent',       # Enviado
    3: 'delivered',  # Entregue
    4: 'error',      # Não entregue
    5: 'rejected',   # Rejeitado
    6: 'expired',    # Expirado
}
```

**Fluxo:**
1. Busca `sms.message` via `provider_message_id` ou `provider_reference`
2. Atualiza `state` conforme mapeamento
3. Atualiza `delivered_date` se entregue
4. Posta no chatter

---

### 4.2. Webhooks ChatRoom (contact_center_sms)

**Arquivo:** `/odoo/custom/addons_custom/contact_center_sms/controllers/sms_webhook_integration.py`

**IMPORTANTE:** Estes webhooks SOBRESCREVEM os do sms_kolmeya!

#### Endpoint: /kolmeya/webhook/reply (ChatRoom Version)

**Diferenças da versão base:**
1. Cria/atualiza `acrux.chat.conversation`
2. Adiciona ao thread via `_add_sms_to_thread()`
3. Notifica via bus para atualização real-time
4. Posta no chatter da conversa

#### Endpoint: /kolmeya/webhook/status (ChatRoom Version)

**Diferenças da versão base:**
1. Atualiza também a conversa ChatRoom
2. Posta status no chatter da conversa

---

## 5. ESTRUTURA DE DADOS DO BANCO

### Tabelas Principais:

```sql
-- SMS Base
sms_message (core)
sms_provider (core)
sms_template (core)

-- ChatRoom SMS
acrux_chat_connector (extended with SMS fields)
acrux_chat_conversation (extended with channel_type, sms_message_id)
acrux_chat_message (extended with sms_message_id, is_sms)

-- Partner Extension
res_partner (extended with SMS stats)
```

### Relacionamentos:

```
sms.message
    |-- partner_id --> res.partner
    |-- user_id --> res.users
    |-- provider_id --> sms.provider
    |-- parent_id --> sms.message (self-reference)

sms.provider
    |-- company_id --> res.company

acrux.chat.conversation
    |-- connector_id --> acrux.chat.connector
    |-- res_partner_id --> res.partner
    |-- sms_message_id --> sms.message
    |-- agent_id --> res.users

acrux.chat.connector
    |-- sms_provider_id --> sms.provider

acrux.chat.message
    |-- contact_id --> acrux.chat.conversation
    |-- sms_message_id --> sms.message
```

---

## 6. FLUXOS PRINCIPAIS

### 6.1. Envio de SMS Simples (via sms_base_sr)

```
1. Usuário abre res.partner
2. Clica em "Send SMS"
3. Abre wizard sms.compose
4. Seleciona template (opcional)
5. Template é renderizado com dados do partner
6. Clica "Send"
7. Wizard cria sms.message (state='draft')
8. Chama action_send()
9. action_send() chama provider_id._send_sms()
10. _send_sms() chama KolmeyaAPI.send_sms()
11. Kolmeya retorna job_id e message_id
12. sms.message atualizado (state='sent', provider_message_id, sent_date)
13. Posta no chatter do partner
```

---

### 6.2. Recebimento de SMS (via webhook ChatRoom)

```
1. Kolmeya recebe SMS reply
2. POST /kolmeya/webhook/reply
3. Controller busca/cria partner por telefone
4. Cria sms.message (direction='incoming', state='delivered')
5. Busca acrux.chat.conversation existente (phone + channel_type='sms')
6. Se não existe: chama create_from_sms()
7. create_from_sms():
   - Busca connector SMS
   - Cria conversation (channel_type='sms')
   - Auto-assign agente
8. Adiciona ao thread: _add_sms_to_thread()
   - Cria acrux.chat.message
   - Vincula ao sms.message via sms_message_id
9. Notifica via bus (WebSocket)
10. Agente vê mensagem em tempo real no ChatRoom
```

---

### 6.3. Envio de SMS via ChatRoom

```
1. Agente abre conversa SMS no ChatRoom
2. Digita mensagem no chat
3. Clica enviar
4. Frontend chama método send_sms_message(body)
5. send_sms_message():
   - Valida channel_type='sms'
   - Busca provider Kolmeya
   - Cria sms.message (direction='outgoing')
   - Chama action_send()
   - Adiciona ao thread via _add_sms_to_thread()
6. KolmeyaAPI.send_sms() é chamado
7. Kolmeya envia SMS
8. Mensagem aparece no thread do ChatRoom
9. Webhook de status atualiza quando entregue
```

---

## 7. ADAPTAÇÃO DO CHATROOM_SMS_ADVANCED

### 7.1. PROBLEMAS ATUAIS

O módulo `chatroom_sms_advanced` foi criado ANTES de conhecer a estrutura real:

**Problemas Críticos:**
1. Criou modelos DUPLICADOS (chatroom.sms.log vs sms.message)
2. Não usa acrux.chat.conversation (criou sistema paralelo)
3. Não integra com sms_base_sr/sms_kolmeya
4. Dependências erradas (chatroom ao invés de whatsapp_connector)
5. Webhooks em endpoint diferente
6. Templates duplicados (chatroom.sms.template vs sms.template)

---

### 7.2. ESTRATÉGIA DE ADAPTAÇÃO

#### OPÇÃO 1: Refatoração Completa (RECOMENDADO)

**Ação:** Transformar chatroom_sms_advanced em módulo de features avançadas sobre a estrutura existente

**Mudanças no __manifest__.py:**
```python
'depends': [
    'sms_base_sr',           # Base SMS
    'sms_kolmeya',           # Provider Kolmeya
    'contact_center_sms',    # Integração ChatRoom
],
```

**Modelos a REMOVER (usar existentes):**
- `chatroom.sms.log` - USAR `sms.message`
- `chatroom.sms.template` - USAR `sms.template`
- `chatroom.sms.api` - USAR `KolmeyaAPI`

**Modelos a MANTER (funcionalidades novas):**
- `chatroom.sms.scheduled` - Agendamento (NOVO)
- `chatroom.sms.dashboard` - Dashboard (NOVO)
- `chatroom.sms.segment` - Centros de custo (NOVO)
- `chatroom.sms.report` - Relatórios avançados (NOVO)

**Modelos a CRIAR como _inherit:**
- `sms.message` (inherit) - Adicionar campos de agendamento
- `sms.provider` (inherit) - Adicionar configs avançadas
- `acrux.chat.conversation` (inherit) - Adicionar features SMS avançadas

---

#### OPÇÃO 2: Módulo Paralelo (NÃO RECOMENDADO)

Manter sistema paralelo causará:
- Duplicação de dados
- Inconsistências
- Confusão para usuários
- Dificuldade de manutenção

---

### 7.3. ARQUITETURA PROPOSTA

```
CAMADA 1 - BASE
sms_base_sr
    |-- sms.message (core)
    |-- sms.provider (abstração)
    |-- sms.template (templates)
    |-- res.partner (extensão)

CAMADA 2 - PROVIDER
sms_kolmeya
    |-- sms.provider (inherit - adiciona Kolmeya)
    |-- KolmeyaAPI (helper class)
    |-- Webhooks básicos

CAMADA 3 - CHATROOM
contact_center_sms
    |-- acrux.chat.connector (inherit - adiciona SMS)
    |-- acrux.chat.conversation (inherit - channel_type)
    |-- acrux.chat.message (inherit - link SMS)
    |-- Webhooks ChatRoom

CAMADA 4 - ADVANCED FEATURES (chatroom_sms_advanced)
    |-- sms.message (inherit)
        |-- scheduled_date
        |-- campaign_id
        |-- link_tracking_ids
    |
    |-- sms.provider (inherit)
        |-- auto_balance_check
        |-- balance_alert_threshold
        |-- webhook_url_custom
    |
    |-- chatroom.sms.scheduled (NEW)
        |-- Agendamento de envios
        |-- Recorrência
    |
    |-- chatroom.sms.campaign (NEW)
        |-- Campanhas SMS
        |-- Segmentação
    |
    |-- chatroom.sms.dashboard (NEW)
        |-- Estatísticas visuais
        |-- Gráficos
    |
    |-- chatroom.sms.blacklist (NEW)
        |-- Gestão de blacklist local
        |-- Sync com Kolmeya
    |
    |-- Wizards
        |-- Send Bulk SMS (usa sms.message)
        |-- Schedule SMS
```

---

### 7.4. MAPEAMENTO DE MODELOS

| Modelo Antigo (chatroom_sms_advanced) | Modelo Real (usar) | Ação |
|---------------------------------------|-------------------|------|
| chatroom.sms.log | sms.message | REMOVER - usar sms.message |
| chatroom.sms.api | KolmeyaAPI | REMOVER - usar KolmeyaAPI |
| chatroom.sms.template | sms.template | REMOVER - usar sms.template |
| chatroom.conversation | acrux.chat.conversation | USAR _inherit |
| chatroom.room | acrux.chat.conversation | REMOVER - conceito duplicado |
| chatroom.sms.segment | sms.provider (inherit) | ADAPTAR - adicionar campo segment_id |
| chatroom.sms.scheduled | (novo) | MANTER - feature nova |
| chatroom.sms.dashboard | (novo) | MANTER - feature nova |

---

### 7.5. CAMPOS A ADICIONAR VIA _inherit

#### 7.5.1. sms.message (inherit)

```python
class SMSMessage(models.Model):
    _inherit = 'sms.message'

    # Agendamento
    scheduled_date = fields.Datetime('Scheduled Date')
    is_scheduled = fields.Boolean('Is Scheduled', compute='_compute_is_scheduled')

    # Campanha
    campaign_id = fields.Many2one('chatroom.sms.campaign', 'Campaign')

    # Tracking
    link_tracking_ids = fields.One2many('chatroom.sms.link.tracking', 'sms_id')
    link_clicks = fields.Integer('Link Clicks', compute='_compute_link_clicks')

    # Blacklist
    blacklist_reason = fields.Selection([
        ('user_request', 'User Request'),
        ('auto_bounce', 'Auto Bounce'),
        ('manual', 'Manual'),
    ])

    @api.depends('scheduled_date')
    def _compute_is_scheduled(self):
        for rec in self:
            rec.is_scheduled = bool(rec.scheduled_date and rec.scheduled_date > fields.Datetime.now())
```

---

#### 7.5.2. sms.provider (inherit)

```python
class SMSProvider(models.Model):
    _inherit = 'sms.provider'

    # Auto-consulta saldo
    auto_balance_check = fields.Boolean('Auto Check Balance', default=True)
    balance_check_interval = fields.Integer('Check Interval (hours)', default=6)
    balance_alert_threshold = fields.Float('Alert Threshold (R$)', default=100.0)

    # Webhook customizado
    webhook_url_custom = fields.Char('Custom Webhook URL')

    # Notificações
    balance_alert_user_ids = fields.Many2many('res.users', string='Alert Users')

    # DND (Do Not Disturb)
    dnd_start_hour = fields.Integer('DND Start Hour', default=22)
    dnd_end_hour = fields.Integer('DND End Hour', default=8)
    dnd_enabled = fields.Boolean('Enable DND', default=True)
```

---

#### 7.5.3. acrux.chat.conversation (inherit)

```python
class AcruxChatConversation(models.Model):
    _inherit = 'acrux.chat.conversation'

    # SMS específicos
    sms_last_sent = fields.Datetime('Last SMS Sent')
    sms_last_received = fields.Datetime('Last SMS Received')
    sms_delivery_rate = fields.Float('Delivery Rate %', compute='_compute_sms_stats')

    # Tags SMS
    sms_tag_ids = fields.Many2many('chatroom.sms.tag', string='SMS Tags')

    # Priority
    is_priority = fields.Boolean('Priority Conversation')

    def action_schedule_sms(self):
        """Abre wizard para agendar SMS"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'chatroom.sms.schedule.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_conversation_id': self.id}
        }
```

---

### 7.6. MODELOS NOVOS A CRIAR

#### 7.6.1. chatroom.sms.scheduled

```python
class ChatroomSMSScheduled(models.Model):
    _name = 'chatroom.sms.scheduled'
    _description = 'Scheduled SMS Messages'
    _order = 'scheduled_date'

    name = fields.Char('Description', required=True)
    sms_message_id = fields.Many2one('sms.message', 'SMS Message', required=True)
    scheduled_date = fields.Datetime('Scheduled Date', required=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ], default='pending')

    # Recorrência
    is_recurring = fields.Boolean('Recurring')
    recurrence_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ])

    def cron_send_scheduled_sms(self):
        """Cron que roda a cada 5 minutos"""
        pending = self.search([
            ('state', '=', 'pending'),
            ('scheduled_date', '<=', fields.Datetime.now()),
        ])
        for scheduled in pending:
            try:
                scheduled.sms_message_id.action_send()
                scheduled.state = 'sent'
            except Exception as e:
                scheduled.state = 'failed'
                _logger.error(f"Failed to send scheduled SMS: {e}")
```

---

#### 7.6.2. chatroom.sms.campaign

```python
class ChatroomSMSCampaign(models.Model):
    _name = 'chatroom.sms.campaign'
    _description = 'SMS Campaigns'

    name = fields.Char('Campaign Name', required=True)
    description = fields.Text('Description')

    # Target
    partner_ids = fields.Many2many('res.partner', string='Recipients')
    domain_filter = fields.Char('Domain Filter')

    # Template
    template_id = fields.Many2one('sms.template', 'Template')

    # Stats
    sms_message_ids = fields.One2many('sms.message', 'campaign_id')
    total_sent = fields.Integer('Total Sent', compute='_compute_stats')
    total_delivered = fields.Integer('Total Delivered', compute='_compute_stats')
    total_failed = fields.Integer('Total Failed', compute='_compute_stats')
    delivery_rate = fields.Float('Delivery Rate %', compute='_compute_stats')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('canceled', 'Canceled'),
    ], default='draft')

    def action_start_campaign(self):
        """Inicia campanha - cria SMS para todos recipients"""
        self.ensure_one()
        for partner in self.partner_ids:
            if partner.mobile or partner.phone:
                sms = self.env['sms.message'].create({
                    'partner_id': partner.id,
                    'phone': partner.mobile or partner.phone,
                    'body': self.template_id.render({'name': partner.name}),
                    'campaign_id': self.id,
                    'provider_id': self.env['sms.provider'].search([('provider_type', '=', 'kolmeya')], limit=1).id,
                })
                sms.action_send()
        self.state = 'running'
```

---

#### 7.6.3. chatroom.sms.dashboard

```python
class ChatroomSMSDashboard(models.Model):
    _name = 'chatroom.sms.dashboard'
    _description = 'SMS Dashboard Statistics'
    _auto = False  # View SQL

    date = fields.Date('Date')
    total_sent = fields.Integer('Total Sent')
    total_delivered = fields.Integer('Total Delivered')
    total_failed = fields.Integer('Total Failed')
    delivery_rate = fields.Float('Delivery Rate %')
    total_cost = fields.Float('Total Cost')
    provider_id = fields.Many2one('sms.provider', 'Provider')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'chatroom_sms_dashboard')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW chatroom_sms_dashboard AS (
                SELECT
                    ROW_NUMBER() OVER() as id,
                    DATE(sent_date) as date,
                    COUNT(*) as total_sent,
                    SUM(CASE WHEN state = 'delivered' THEN 1 ELSE 0 END) as total_delivered,
                    SUM(CASE WHEN state IN ('error', 'rejected') THEN 1 ELSE 0 END) as total_failed,
                    AVG(CASE WHEN state = 'delivered' THEN 100.0 ELSE 0.0 END) as delivery_rate,
                    SUM(cost) as total_cost,
                    provider_id
                FROM sms_message
                WHERE sent_date IS NOT NULL
                GROUP BY DATE(sent_date), provider_id
            )
        """)
```

---

#### 7.6.4. chatroom.sms.blacklist

```python
class ChatroomSMSBlacklist(models.Model):
    _name = 'chatroom.sms.blacklist'
    _description = 'SMS Blacklist (Do Not Disturb)'

    phone = fields.Char('Phone Number', required=True, index=True)
    partner_id = fields.Many2one('res.partner', 'Partner')

    reason = fields.Selection([
        ('user_request', 'User Request'),
        ('auto_bounce', 'Auto Bounce'),
        ('manual', 'Manual'),
        ('legal', 'Legal Requirement'),
    ], required=True)

    added_date = fields.Datetime('Added Date', default=fields.Datetime.now)
    added_by = fields.Many2one('res.users', 'Added By', default=lambda self: self.env.user)

    synced_kolmeya = fields.Boolean('Synced with Kolmeya', default=False)

    _sql_constraints = [
        ('phone_unique', 'unique(phone)', 'Phone already in blacklist!')
    ]

    def sync_to_kolmeya(self):
        """Sincroniza blacklist local com Kolmeya"""
        provider = self.env['sms.provider'].search([('provider_type', '=', 'kolmeya')], limit=1)
        if not provider:
            return

        api = KolmeyaAPI(provider.kolmeya_api_token, provider.kolmeya_segment_id)

        phones_to_sync = self.filtered(lambda b: not b.synced_kolmeya)
        phone_list = [b.phone for b in phones_to_sync]

        if phone_list:
            api.add_to_blacklist(phone_list)
            phones_to_sync.write({'synced_kolmeya': True})
```

---

### 7.7. WIZARDS A ADAPTAR

#### 7.7.1. chatroom.send.bulk.sms (adaptar)

```python
class ChatroomSendBulkSMS(models.TransientModel):
    _name = 'chatroom.send.bulk.sms'
    _description = 'Send Bulk SMS Wizard'

    # Seleção de destinatários
    selection_type = fields.Selection([
        ('manual', 'Manual Selection'),
        ('domain', 'Domain Filter'),
        ('campaign', 'Existing Campaign'),
    ], default='manual')

    partner_ids = fields.Many2many('res.partner', string='Recipients')
    domain_filter = fields.Char('Domain Filter')
    campaign_id = fields.Many2one('chatroom.sms.campaign', 'Campaign')

    # Mensagem
    template_id = fields.Many2one('sms.template', 'Template')  # USAR sms.template
    body = fields.Text('Message')

    # Provider
    provider_id = fields.Many2one('sms.provider', 'Provider',
                                 default=lambda self: self.env['sms.provider'].search([('provider_type', '=', 'kolmeya')], limit=1))

    # Stats
    total_recipients = fields.Integer('Total Recipients', compute='_compute_stats')
    estimated_cost = fields.Float('Estimated Cost', compute='_compute_stats')

    def action_send_bulk(self):
        """Envia SMS em lote usando sms.message"""
        self.ensure_one()

        # Prepara lista de mensagens
        messages_data = []
        for partner in self.partner_ids:
            phone = partner.mobile or partner.phone
            if not phone:
                continue

            # Renderiza template para cada partner
            body = self.template_id.render({'name': partner.name}) if self.template_id else self.body

            # Cria sms.message
            sms = self.env['sms.message'].create({
                'partner_id': partner.id,
                'phone': phone,
                'body': body,
                'provider_id': self.provider_id.id,
                'campaign_id': self.campaign_id.id if self.campaign_id else False,
            })

            messages_data.append({
                'phone': phone,
                'message': body,
                'reference': str(sms.id),
            })

        # Envia batch via Kolmeya
        if messages_data:
            self.provider_id._send_batch(messages_data)

        return {'type': 'ir.actions.act_window_close'}
```

---

### 7.8. CRONS NECESSÁRIOS

#### 7.8.1. Consulta Automática de Saldo

```xml
<record id="cron_check_sms_balance" model="ir.cron">
    <field name="name">SMS: Check Kolmeya Balance</field>
    <field name="model_id" ref="sms_base_sr.model_sms_provider"/>
    <field name="state">code</field>
    <field name="code">model.search([('provider_type', '=', 'kolmeya'), ('auto_balance_check', '=', True)]).action_check_balance()</field>
    <field name="interval_number">6</field>
    <field name="interval_type">hours</field>
    <field name="numbercall">-1</field>
    <field name="active">True</field>
</record>
```

#### 7.8.2. Envio de SMS Agendados

```xml
<record id="cron_send_scheduled_sms" model="ir.cron">
    <field name="name">SMS: Send Scheduled Messages</field>
    <field name="model_id" ref="model_chatroom_sms_scheduled"/>
    <field name="state">code</field>
    <field name="code">model.cron_send_scheduled_sms()</field>
    <field name="interval_number">5</field>
    <field name="interval_type">minutes</field>
    <field name="numbercall">-1</field>
    <field name="active">True</field>
</record>
```

#### 7.8.3. Sync Blacklist com Kolmeya

```xml
<record id="cron_sync_blacklist_kolmeya" model="ir.cron">
    <field name="name">SMS: Sync Blacklist to Kolmeya</field>
    <field name="model_id" ref="model_chatroom_sms_blacklist"/>
    <field name="state">code</field>
    <field name="code">model.search([('synced_kolmeya', '=', False)]).sync_to_kolmeya()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">hours</field>
    <field name="numbercall">-1</field>
    <field name="active">True</field>
</record>
```

---

### 7.9. VIEWS A ADAPTAR

#### Principais Mudanças:

1. **sms_log_views.xml** → **sms_message_views.xml**
   - Usar modelo `sms.message` ao invés de `chatroom.sms.log`
   - Adicionar campos de agendamento, campanha
   - Adicionar filtros avançados

2. **sms_template_views.xml**
   - REMOVER - usar views de `sms.template` do sms_base_sr
   - Apenas adicionar campos extras via inherit se necessário

3. **conversation_views.xml**
   - Adicionar aba "SMS Advanced" em acrux.chat.conversation
   - Mostrar stats SMS, agendamentos, etc

4. **dashboard_views.xml**
   - Criar view Kanban/Graph para estatísticas
   - Usar modelo `chatroom.sms.dashboard` (SQL view)

---

### 7.10. SECURITY

#### ir.model.access.csv

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_chatroom_sms_scheduled_user,chatroom.sms.scheduled.user,model_chatroom_sms_scheduled,base.group_user,1,1,1,0
access_chatroom_sms_scheduled_manager,chatroom.sms.scheduled.manager,model_chatroom_sms_scheduled,base.group_system,1,1,1,1
access_chatroom_sms_campaign_user,chatroom.sms.campaign.user,model_chatroom_sms_campaign,base.group_user,1,1,1,0
access_chatroom_sms_campaign_manager,chatroom.sms.campaign.manager,model_chatroom_sms_campaign,base.group_system,1,1,1,1
access_chatroom_sms_dashboard_user,chatroom.sms.dashboard.user,model_chatroom_sms_dashboard,base.group_user,1,0,0,0
access_chatroom_sms_blacklist_user,chatroom.sms.blacklist.user,model_chatroom_sms_blacklist,base.group_user,1,0,0,0
access_chatroom_sms_blacklist_manager,chatroom.sms.blacklist.manager,model_chatroom_sms_blacklist,base.group_system,1,1,1,1
```

---

### 7.11. WEBHOOKS

**IMPORTANTE:** NÃO criar novos endpoints webhook!

**Usar os existentes:**
- `/kolmeya/webhook/reply` (contact_center_sms)
- `/kolmeya/webhook/status` (contact_center_sms)

**Se necessário features extras:**
- Adicionar lógica via _inherit nos controllers existentes
- Ou criar método helper que os webhooks existentes chamam

---

## 8. PLANO DE MIGRAÇÃO

### Fase 1: Preparação (1-2 dias)

1. **Backup completo do módulo atual**
2. **Criar branch Git para refatoração**
3. **Documentar todos os modelos/campos atuais**
4. **Mapear dependências e usos**

### Fase 2: Refatoração Core (3-5 dias)

1. **Atualizar __manifest__.py**
   - Mudar depends para sms_base_sr, sms_kolmeya, contact_center_sms
   - Remover data files de modelos duplicados

2. **Remover modelos duplicados**
   - chatroom.sms.log → substituir por sms.message
   - chatroom.sms.api → substituir por KolmeyaAPI
   - chatroom.sms.template → substituir por sms.template

3. **Criar _inherit dos modelos base**
   - sms.message (inherit) - adicionar campos agendamento/campanha
   - sms.provider (inherit) - adicionar configs avançadas
   - acrux.chat.conversation (inherit) - features SMS

4. **Criar modelos novos**
   - chatroom.sms.scheduled
   - chatroom.sms.campaign
   - chatroom.sms.dashboard
   - chatroom.sms.blacklist

### Fase 3: Views e Wizards (2-3 dias)

1. **Adaptar views existentes**
   - Substituir referências de modelo
   - Adicionar campos novos
   - Criar dashboard views

2. **Adaptar wizards**
   - Bulk send usando sms.message
   - Schedule wizard

3. **Criar menus**
   - Integrar com menu SMS existente
   - Adicionar submenus de features avançadas

### Fase 4: Testes (2-3 dias)

1. **Testes unitários**
   - Criação de SMS agendados
   - Envio em lote
   - Webhooks

2. **Testes integração**
   - ChatRoom + SMS
   - Kolmeya API
   - Blacklist sync

3. **Testes UI**
   - Dashboard
   - Wizards
   - Conversas SMS

### Fase 5: Deploy (1 dia)

1. **Deploy em ambiente staging**
2. **Testes com usuários**
3. **Ajustes finais**
4. **Deploy produção**

---

## 9. CHECKLIST FINAL

### Antes de Iniciar:

- [ ] Backup completo do servidor
- [ ] Backup do banco de dados
- [ ] Documentação atual salva
- [ ] Branch Git criado

### Durante Refatoração:

- [ ] __manifest__.py atualizado
- [ ] Todos os _inherit criados
- [ ] Modelos duplicados removidos
- [ ] Views adaptadas
- [ ] Wizards adaptados
- [ ] Security configurado
- [ ] Crons criados
- [ ] Menus atualizados

### Antes de Deploy:

- [ ] Testes unitários passando
- [ ] Testes integração OK
- [ ] Webhooks testados
- [ ] Dashboard funcional
- [ ] Documentação atualizada
- [ ] Migration script (se necessário)

---

## 10. RESUMO EXECUTIVO

### Estrutura Real Descoberta:

O sistema SMS do Odoo 15 possui uma arquitetura bem organizada em 3 camadas:

1. **sms_base_sr:** Core SMS com modelos base (sms.message, sms.provider, sms.template)
2. **sms_kolmeya:** Integração com API Kolmeya (provider específico)
3. **contact_center_sms:** Integração com ChatRoom WhatsApp (central unificada)

### Principais Descobertas:

1. **Modelo sms.message** já possui TUDO que precisamos:
   - Tracking completo (provider_message_id, job_id, reference)
   - Estados detalhados (draft → sent → delivered)
   - Integração com partner e chatter
   - Custos e segmentação

2. **KolmeyaAPI** é uma classe Python completa com:
   - Todos os endpoints da API Kolmeya
   - Tratamento de erros e rate limiting
   - Métodos para saldo, blacklist, relatórios

3. **contact_center_sms** já integra SMS ao ChatRoom:
   - acrux.chat.conversation com channel_type='sms'
   - Webhooks funcionais
   - Conversas unificadas SMS + WhatsApp

### Impacto no chatroom_sms_advanced:

**CRÍTICO:** 80% do código atual está DUPLICADO e deve ser removido!

**Manter apenas:**
- Features avançadas (agendamento, campanhas, dashboard)
- Reports customizados
- Blacklist management
- Bulk send wizard (adaptado)

**Remover/Substituir:**
- chatroom.sms.log → sms.message
- chatroom.sms.api → KolmeyaAPI
- chatroom.sms.template → sms.template
- Webhooks duplicados

### Próximos Passos:

1. **Atualizar depends no __manifest__.py**
2. **Criar _inherit de sms.message, sms.provider, acrux.chat.conversation**
3. **Remover modelos duplicados**
4. **Adaptar wizards para usar sms.message**
5. **Criar modelos novos (scheduled, campaign, dashboard, blacklist)**
6. **Testar integração completa**

### Tempo Estimado:

- **Refatoração:** 8-10 dias
- **Testes:** 3-5 dias
- **Deploy:** 1-2 dias

**TOTAL:** 12-17 dias de trabalho

---

## ANEXOS

### A. Exemplo de Envio SMS Completo

```python
# 1. Criar SMS
sms = env['sms.message'].create({
    'partner_id': partner.id,
    'phone': '5548991234567',
    'body': 'Olá {name}! Seu pedido está pronto.'.format(name=partner.name),
    'direction': 'outgoing',
    'provider_id': env['sms.provider'].search([('provider_type', '=', 'kolmeya')], limit=1).id,
})

# 2. Enviar
sms.action_send()

# 3. Provider chama KolmeyaAPI
provider = sms.provider_id
api = KolmeyaAPI(provider.kolmeya_api_token, provider.kolmeya_segment_id)
result = api.send_sms(
    phone='5548991234567',
    message=sms.body,
    reference=str(sms.id)
)

# 4. Atualiza SMS
sms.write({
    'state': 'sent',
    'provider_message_id': result['valids'][0]['id'],
    'provider_job_id': result['id'],
    'sent_date': fields.Datetime.now(),
})

# 5. Webhook de status atualiza para 'delivered'
# POST /kolmeya/webhook/status
# {
#   "id": "uuid",
#   "reference": "1234",
#   "status": "entregue",
#   "status_code": 3
# }

# 6. SMS atualizado
sms.write({
    'state': 'delivered',
    'delivered_date': fields.Datetime.now(),
})
```

---

### B. Exemplo de Conversa ChatRoom SMS

```python
# 1. Cliente responde SMS via Kolmeya
# Webhook: POST /kolmeya/webhook/reply
# {
#   "phone": "5548991234567",
#   "message": "Sim, quero comprar!",
#   "reference": "1234"
# }

# 2. Controller cria/atualiza conversa
partner = env['res.partner'].search([('mobile', '=', '5548991234567')], limit=1)

sms_incoming = env['sms.message'].create({
    'partner_id': partner.id,
    'phone': '5548991234567',
    'body': 'Sim, quero comprar!',
    'direction': 'incoming',
    'state': 'delivered',
})

conversation = env['acrux.chat.conversation'].search([
    ('number', '=', '5548991234567'),
    ('channel_type', '=', 'sms'),
], limit=1)

if not conversation:
    conversation = env['acrux.chat.conversation'].create_from_sms(sms_incoming)
else:
    conversation._add_sms_to_thread(sms_incoming)

# 3. Agente vê mensagem no ChatRoom em tempo real
# 4. Agente responde pelo ChatRoom
conversation.send_sms_message('Ótimo! Vou processar seu pedido.')

# 5. SMS enviado via Kolmeya
# 6. Mensagem aparece no thread do ChatRoom
```

---

### C. Endpoints da API Kolmeya

```
Base URL: https://kolmeya.com.br/api/v1

POST /sms/store
    - Enviar SMS (individual ou batch)
    - Body: {"messages": [{"phone": "...", "message": "..."}], "segment": 109}

POST /sms/status/request
    - Status de um job
    - Body: {"id": "job_id"}

POST /sms/status/message
    - Status de uma mensagem
    - Body: {"id": "message_id"}

GET /sms/balance
    - Consultar saldo
    - Response: {"balance": "R$9.396,84"}

GET /sms/modelos
    - Templates configurados

POST /sms/blacklist/adicionar
    - Adicionar à blacklist
    - Body: {"phones": [{"phone": "..."}]}

POST /sms/blacklist/remover
    - Remover da blacklist

GET /sms/blacklist
    - Listar blacklist

GET /sms/respostas?page=1
    - Respostas SMS (últimos 7 dias)

POST /sms/relatorio
    - Relatório por período
    - Body: {"data_inicio": "2025-01-01", "data_fim": "2025-01-31", "page": 1}
```

---

## FIM DA DOCUMENTAÇÃO

**Autor:** Claude AI + Análise SSH
**Data:** 16/11/2025
**Versão:** 1.0
**Status:** COMPLETO

Esta documentação deve ser usada como referência principal para adaptar o módulo chatroom_sms_advanced à estrutura real do sistema SMS existente no Odoo 15.
