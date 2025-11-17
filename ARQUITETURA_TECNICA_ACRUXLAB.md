# 🏗️ Arquitetura Técnica Detalhada - AcruxLab WhatsApp Connector

**Documento Técnico de Engenharia Reversa**
**Data:** 2025-11-16
**Objetivo:** Revelar os segredos internos do AcruxLab para criar soluções similares

---

## 📑 Índice

1. [Engenharia Reversa do AcruxLab](#engenharia-reversa-do-acruxlab)
2. [Modelos de Dados Detalhados](#modelos-de-dados-detalhados)
3. [Fluxos de Execução](#fluxos-de-execução)
4. [API Endpoints e Rotas](#api-endpoints-e-rotas)
5. [JavaScript e Frontend](#javascript-e-frontend)
6. [Segredos de Performance](#segredos-de-performance)
7. [Padrões de Design](#padrões-de-design)

---

## 1. Engenharia Reversa do AcruxLab

### 1.1 Estrutura de Arquivos do WhatsApp Connector

```
whatsapp_connector/
├── __init__.py
├── __manifest__.py
│
├── models/                          # 26 arquivos Python
│   ├── __init__.py
│   ├── AcruxChatMessages.py        # ⭐ Mensagens individuais
│   ├── Connector.py                # ⭐⭐⭐ CORE - Gerencia canal
│   ├── Conversation.py             # ⭐⭐⭐ CORE - Thread de conversa
│   ├── res_partner.py              # Extensão de parceiros
│   ├── ResUsers.py                 # Agentes/usuários
│   ├── InitMessages.py             # Mensagens de boas-vindas
│   ├── TemplateMessage.py          # Templates rápidos
│   └── ...
│
├── controllers/                     # Webhooks e API
│   ├── __init__.py
│   ├── main.py                     # ⭐ Rotas web principais
│   └── webhook.py                  # ⭐ Recebimento de mensagens
│
├── static/
│   ├── src/
│   │   ├── js/
│   │   │   ├── acrux_chat_conversation.js  # ⭐ Kanban de conversas
│   │   │   ├── acrux_chat_message.js       # ⭐ Thread de mensagens
│   │   │   └── ...
│   │   └── xml/                            # Templates QWeb
│   └── description/
│       └── icon.png
│
├── views/
│   ├── conversation_views.xml      # Kanban, Form, List
│   ├── message_views.xml
│   ├── connector_views.xml
│   └── res_partner_views.xml       # Botão "Abrir Chat"
│
└── tools/                           # Utilitários
    ├── __init__.py
    ├── common.py                   # phone_format, clean_number
    └── image_tools.py
```

---

### 1.2 Hierarquia de Modelos (ORM)

```
┌─────────────────────────────────────────────────────────────┐
│                    acrux.chat.connector                      │
│  (Canal = Conta WhatsApp, SMS, Instagram, etc)              │
│                                                              │
│  Fields:                                                     │
│  - name: str                     "WhatsApp Vendas"          │
│  - connector_type: selection     'chatapi', 'apichat', 'sms'│
│  - token: str (UUID)             Autenticação webhook       │
│  - uuid: str                     ID curto (6 dígitos)       │
│  - endpoint: str                 URL da API externa         │
│  - company_id: many2one          Empresa                    │
│  - border_color: str             Cor do card no Kanban      │
│  - desk_notify: selection        'mines', 'all', 'none'     │
│  - conversation_ids: one2many    ← Conversas deste canal    │
│                                                              │
│  Methods:                                                    │
│  - assert_id(key)                Valida número              │
│  - clean_id(key)                 Remove caracteres          │
│  - format_id(key)                Formata para exibição      │
│  - ca_request(endpoint, data)    Faz request para API       │
└──────────────────┬───────────────────────────────────────────┘
                   │ one2many
                   │
┌──────────────────▼───────────────────────────────────────────┐
│                acrux.chat.conversation                        │
│  (Thread = Conversa com um cliente específico)               │
│                                                              │
│  Fields:                                                     │
│  - name: str                     "João Silva"               │
│  - number: str (required!)       "5511999887766"            │
│  - number_format: str            "+55 (11) 99988-7766"      │
│  - connector_id: many2one        ← Canal                    │
│  - res_partner_id: many2one      Cliente (contacts)         │
│  - status: selection             'new', 'current', 'done'   │
│  - agent_id: many2one            Agente responsável         │
│  - message_ids: one2many         ← Mensagens                │
│  - last_received: datetime       Última msg recebida        │
│  - image_128: binary             Avatar do contato          │
│                                                              │
│  Constraints:                                                │
│  - UNIQUE(number, connector_id)  Não pode duplicar!         │
│                                                              │
│  Methods:                                                    │
│  - send_message(text, attachments)  Envia mensagem          │
│  - archive_conversation()           Marca como 'done'       │
│  - notify_message(msg_id)           Bus notification        │
└──────────────────┬───────────────────────────────────────────┘
                   │ one2many
                   │
┌──────────────────▼───────────────────────────────────────────┐
│                 acrux.chat.message                           │
│  (Mensagem individual = balão de chat)                       │
│                                                              │
│  Fields:                                                     │
│  - contact_id: many2one          ← Conversa                 │
│  - text: text                    Conteúdo da mensagem       │
│  - ttype: selection              'text', 'image', 'audio'   │
│  - from_me: boolean              Enviado por nós?           │
│  - date_message: datetime        Timestamp                  │
│  - msg_id: char                  ID externo (API)           │
│  - res_model: char               Modelo relacionado         │
│  - res_id: integer               ID do registro             │
│  - attachment_ids: many2many     Arquivos anexos            │
│  - error_msg: text               Erro de envio (se houver)  │
│                                                              │
│  Methods:                                                    │
│  - ca_send_message()             Envia via API              │
│  - download_attachment()         Baixa mídia                │
└──────────────────────────────────────────────────────────────┘
```

---

### 1.3 Relacionamentos entre Tabelas (ERD)

```sql
┌─────────────────────┐
│   res_company       │
│  (Empresa)          │
└──────┬──────────────┘
       │ FK
       │
┌──────▼──────────────────────────────────────┐
│   acrux_chat_connector                      │
│   (Canal: WhatsApp, SMS, Instagram)         │
│                                             │
│   PK: id                                    │
│   UK: token (UUID único)                    │
│   FK: company_id → res_company.id           │
│   FK: sms_provider_id → sms_provider.id     │← Nossa adição!
└──────┬──────────────────────────────────────┘
       │ FK
       │
┌──────▼──────────────────────────────────────┐
│   acrux_chat_conversation                   │
│   (Conversa com cliente)                    │
│                                             │
│   PK: id                                    │
│   UK: (number, connector_id)  ← UNIQUE!     │
│   FK: connector_id → acrux_chat_connector.id│
│   FK: res_partner_id → res_partner.id       │
│   FK: agent_id → res_users.id               │
└──────┬──────────────────────────────────────┘
       │ FK
       │
┌──────▼──────────────────────────────────────┐
│   acrux_chat_message                        │
│   (Mensagem individual)                     │
│                                             │
│   PK: id                                    │
│   FK: contact_id → acrux_chat_conversation.id│
│   FK: user_id → res_users.id                │
└─────────────────────────────────────────────┘


┌─────────────────────┐
│   res_partner       │
│  (Contato/Cliente)  │
│                     │
│   Fields extras:    │
│   - whatsapp_active │
│   - whatsapp_number │
│   - conversation_ids│← one2many
└─────────────────────┘
```

---

## 2. Modelos de Dados Detalhados

### 2.1 acrux_chat_connector (Tabela Completa)

```sql
CREATE TABLE acrux_chat_connector (
    -- Campos de identificação
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR NOT NULL,           -- 'WhatsApp Vendas', 'SMS Kolmeya'
    uuid                VARCHAR NOT NULL UNIQUE,    -- '123456' (6 dígitos)
    token               VARCHAR NOT NULL UNIQUE,    -- UUID v4 para webhook

    -- Tipo de connector
    connector_type      VARCHAR NOT NULL,           -- 'chatapi', 'apichat', 'gupshup', 'sms'

    -- Configuração de conexão
    endpoint            VARCHAR NOT NULL,           -- 'https://api.chat-api.com/instance123456'
    odoo_url            VARCHAR NOT NULL,           -- 'https://odoo.semprereal.com'
    source              VARCHAR NOT NULL DEFAULT '/',

    -- Autenticação API externa
    api_key             VARCHAR,                    -- Token da API externa
    api_secret          VARCHAR,                    -- Secret (se necessário)

    -- Configurações visuais
    border_color        VARCHAR NOT NULL DEFAULT '#0D15E7',  -- Cor do card
    image_128           BYTEA,                      -- Avatar do canal

    -- Configurações de atribuição
    assing_type         VARCHAR NOT NULL,           -- 'connector', 'agent', 'team'
    desk_notify         VARCHAR NOT NULL,           -- 'mines', 'all', 'none'
    team_id             INTEGER,                    -- FK: crm.team (se assing_type='team')

    -- Sequência (ordem no Kanban)
    sequence            INTEGER NOT NULL DEFAULT 10,

    -- Status
    status              VARCHAR,                    -- 'active', 'paused', 'error'
    active              BOOLEAN DEFAULT TRUE,

    -- Limites e quotas
    limit_send          INTEGER,                    -- Msgs/dia
    allow_caption       BOOLEAN DEFAULT TRUE,       -- Permite legendas em mídia

    -- SMS específico (nossa adição)
    sms_provider_id     INTEGER,                    -- FK: sms_provider.id

    -- Relacionamentos
    company_id          INTEGER NOT NULL,           -- FK: res_company.id

    -- Auditoria
    create_date         TIMESTAMP,
    write_date          TIMESTAMP,
    create_uid          INTEGER,                    -- FK: res_users.id
    write_uid           INTEGER,

    CONSTRAINT fk_company FOREIGN KEY (company_id) REFERENCES res_company(id),
    CONSTRAINT fk_sms_provider FOREIGN KEY (sms_provider_id) REFERENCES sms_provider(id),
    CONSTRAINT check_connector_type CHECK (connector_type IN (
        'chatapi', 'apichat', 'gupshup', 'chatswing', 'sms'
    ))
);

-- Índices importantes
CREATE INDEX idx_connector_type ON acrux_chat_connector(connector_type);
CREATE INDEX idx_connector_active ON acrux_chat_connector(active) WHERE active = TRUE;
CREATE UNIQUE INDEX idx_connector_token ON acrux_chat_connector(token);
```

**Campos Críticos Explicados:**

| Campo | Tipo | Obrigatório | Descrição | Exemplo |
|-------|------|-------------|-----------|---------|
| `connector_type` | VARCHAR | ✅ SIM | Tipo de canal/API | `'sms'`, `'chatapi'` |
| `token` | VARCHAR | ✅ SIM | UUID para autenticar webhook | `'33860850-e93b...'` |
| `uuid` | VARCHAR | ✅ SIM | ID numérico curto (usado em URLs) | `'595911'` |
| `endpoint` | VARCHAR | ✅ SIM | URL base da API externa | `'https://kolmeya.com.br/api/v1'` |
| `odoo_url` | VARCHAR | ✅ SIM | URL pública do Odoo | `'https://odoo.semprereal.com'` |
| `border_color` | VARCHAR | ✅ SIM | Cor hex para identificar visualmente | `'#00C853'` (verde) |
| `desk_notify` | VARCHAR | ✅ SIM | Quem é notificado de novas msgs | `'mines'` (só minhas conversas) |
| `assing_type` | VARCHAR | ✅ SIM | Como atribuir conversas | `'connector'` (auto) |
| `sms_provider_id` | INTEGER | ❌ NÃO | FK para provider SMS | `1` (Kolmeya) |

---

### 2.2 acrux_chat_conversation (Tabela Completa)

```sql
CREATE TABLE acrux_chat_conversation (
    -- Identificação
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR NOT NULL,           -- Nome do contato

    -- Número do contato (CRÍTICO!)
    number              VARCHAR NOT NULL,           -- '5511999887766' (limpo)
    number_format       VARCHAR,                    -- '+55 (11) 99988-7766' (formatado)

    -- Relacionamentos principais
    connector_id        INTEGER NOT NULL,           -- FK: acrux_chat_connector.id
    res_partner_id      INTEGER,                    -- FK: res_partner.id (pode ser NULL!)
    agent_id            INTEGER,                    -- FK: res_users.id (agente atribuído)
    team_id             INTEGER,                    -- FK: crm.team.id

    -- Status da conversa
    status              VARCHAR DEFAULT 'new',      -- 'new', 'current', 'done'
    active              BOOLEAN DEFAULT TRUE,

    -- Avatar
    image_url           VARCHAR,                    -- URL da foto de perfil
    image_128           BYTEA,                      -- Binário da imagem

    -- Timestamps importantes
    last_received       TIMESTAMP,                  -- Última msg recebida
    last_sent           TIMESTAMP,                  -- Última msg enviada

    -- Contadores
    message_count       INTEGER DEFAULT 0,
    unread_count        INTEGER DEFAULT 0,

    -- Configurações
    mute                BOOLEAN DEFAULT FALSE,      -- Silenciar notificações

    -- Campos customizados (nossa adição)
    channel_type        VARCHAR DEFAULT 'whatsapp', -- 'whatsapp', 'sms', 'instagram'
    sms_message_id      INTEGER,                    -- FK: sms_message.id (primeira SMS)

    -- Relação com CRM/Vendas
    res_model           VARCHAR,                    -- 'sale.order', 'crm.lead', etc
    res_id              INTEGER,                    -- ID do registro

    -- Auditoria
    company_id          INTEGER NOT NULL,
    create_date         TIMESTAMP,
    write_date          TIMESTAMP,
    create_uid          INTEGER,
    write_uid           INTEGER,

    -- Constraints
    CONSTRAINT fk_connector FOREIGN KEY (connector_id) REFERENCES acrux_chat_connector(id),
    CONSTRAINT fk_partner FOREIGN KEY (res_partner_id) REFERENCES res_partner(id),
    CONSTRAINT fk_agent FOREIGN KEY (agent_id) REFERENCES res_users(id),
    CONSTRAINT unique_number_per_connector UNIQUE(number, connector_id),  -- ⚠️ IMPORTANTE!
    CONSTRAINT check_status CHECK (status IN ('new', 'current', 'done'))
);

-- Índices para performance
CREATE INDEX idx_conversation_connector ON acrux_chat_conversation(connector_id);
CREATE INDEX idx_conversation_status ON acrux_chat_conversation(status);
CREATE INDEX idx_conversation_agent ON acrux_chat_conversation(agent_id);
CREATE INDEX idx_conversation_number ON acrux_chat_conversation(number);
CREATE INDEX idx_conversation_active ON acrux_chat_conversation(active) WHERE active = TRUE;
```

**⚠️ CONSTRAINT CRÍTICO:**
```sql
CONSTRAINT unique_number_per_connector UNIQUE(number, connector_id)
```

**Significado:**
- Não pode ter 2 conversas com mesmo número no mesmo connector
- Pode ter número duplicado em connectors diferentes
- Exemplo válido:
  - Conversa 1: number='5511999887766', connector_id=1 (WhatsApp)
  - Conversa 2: number='5511999887766', connector_id=2 (SMS) ✅ OK

---

### 2.3 acrux_chat_message (Tabela Completa)

```sql
CREATE TABLE acrux_chat_message (
    -- Identificação
    id                  SERIAL PRIMARY KEY,

    -- Relacionamento com conversa
    contact_id          INTEGER NOT NULL,           -- FK: acrux_chat_conversation.id

    -- Conteúdo
    text                TEXT,                       -- Texto da mensagem
    ttype               VARCHAR NOT NULL,           -- 'text', 'image', 'video', 'audio', 'document'

    -- Direção
    from_me             BOOLEAN DEFAULT FALSE,      -- TRUE = enviado por nós, FALSE = recebido

    -- Timestamps
    date_message        TIMESTAMP,                  -- Data/hora da mensagem
    date_read           TIMESTAMP,                  -- Quando foi lida (se from_me=TRUE)

    -- IDs externos (API)
    msg_id              VARCHAR,                    -- ID da mensagem na API externa
    chatroom_id         VARCHAR,                    -- ID do chatroom (se aplicável)

    -- Usuário que enviou (se from_me=TRUE)
    user_id             INTEGER,                    -- FK: res_users.id

    -- Anexos
    attachment_ids      INTEGER[],                  -- Array de ir.attachment.id

    -- Status de envio
    status              VARCHAR,                    -- 'sent', 'delivered', 'read', 'failed'
    error_msg           TEXT,                       -- Mensagem de erro (se falhou)

    -- Relacionamento com registros Odoo
    res_model           VARCHAR,                    -- 'sale.order', 'crm.lead'
    res_id              INTEGER,                    -- ID do registro

    -- Flags especiais
    is_template         BOOLEAN DEFAULT FALSE,      -- É template rápido?
    is_init             BOOLEAN DEFAULT FALSE,      -- É mensagem inicial automática?

    -- Auditoria
    create_date         TIMESTAMP,
    write_date          TIMESTAMP,
    create_uid          INTEGER,
    write_uid           INTEGER,

    CONSTRAINT fk_conversation FOREIGN KEY (contact_id) REFERENCES acrux_chat_conversation(id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES res_users(id),
    CONSTRAINT check_ttype CHECK (ttype IN (
        'text', 'image', 'video', 'audio', 'document', 'location', 'sticker'
    ))
);

-- Índices para queries rápidas
CREATE INDEX idx_message_conversation ON acrux_chat_message(contact_id);
CREATE INDEX idx_message_date ON acrux_chat_message(date_message DESC);
CREATE INDEX idx_message_from_me ON acrux_chat_message(from_me);
CREATE INDEX idx_message_status ON acrux_chat_message(status);
```

---

## 3. Fluxos de Execução

### 3.1 Fluxo: Enviar Mensagem de Texto

```
┌──────────────────────────────────────────────────────────┐
│ 1. USER ACTION: Agente digita mensagem no ChatRoom      │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 2. JAVASCRIPT: acrux_chat_message.js                     │
│    - Captura evento onKeyPress (Enter)                   │
│    - Chama método RPC: send_message()                    │
│    - Payload: {conversation_id, text, ttype='text'}      │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 3. PYTHON: acrux.chat.conversation.send_message()        │
│    @api.model                                            │
│    def send_message(self, conversation_id, text):        │
│        conv = self.browse(conversation_id)               │
│        msg = self.env['acrux.chat.message'].create({     │
│            'contact_id': conv.id,                        │
│            'text': text,                                 │
│            'from_me': True,                              │
│            'ttype': 'text',                              │
│        })                                                │
│        return msg.ca_send_message()  ← Envia via API     │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 4. PYTHON: acrux.chat.message.ca_send_message()          │
│    - Verifica channel_type (whatsapp, sms, etc)         │
│    - Se SMS: chama conversation.send_sms_message()      │
│    - Se WhatsApp: chama connector.ca_request()          │
└───────────────────────┬──────────────────────────────────┘
                        │
          ┌─────────────┴──────────────┐
          │                            │
          ▼ SMS                        ▼ WhatsApp
┌─────────────────────┐      ┌─────────────────────┐
│ SMS Path:           │      │ WhatsApp Path:      │
│ 1. send_sms_message │      │ 1. ca_request()     │
│ 2. sms.message      │      │ 2. HTTP POST        │
│ 3. provider.send()  │      │ 3. ChatAPI/GupShup  │
│ 4. Kolmeya API      │      │ 4. WhatsApp server  │
└─────────────────────┘      └─────────────────────┘
          │                            │
          └─────────────┬──────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 5. RESPONSE: API externa retorna resultado              │
│    WhatsApp: {'id': 'msg_123', 'status': 'sent'}        │
│    SMS: {'job_id': 'job_456', 'valids': 1}              │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 6. UPDATE: Atualiza registro no banco                   │
│    msg.write({                                           │
│        'msg_id': result['id'],                           │
│        'status': 'sent',                                 │
│    })                                                    │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 7. NOTIFICATION: Bus notification para UI               │
│    self.env['bus.bus'].sendone(                          │
│        f'acrux_chat_conversation_{conv.id}',             │
│        {'message_sent': msg.id}                          │
│    )                                                     │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 8. UI UPDATE: JavaScript atualiza interface             │
│    - Marca mensagem como "enviada" (✓)                  │
│    - Depois "entregue" (✓✓) quando webhook confirmar    │
└──────────────────────────────────────────────────────────┘
```

---

### 3.2 Fluxo: Receber Mensagem via Webhook

```
┌──────────────────────────────────────────────────────────┐
│ 1. EXTERNAL: API externa recebe mensagem                │
│    - Cliente envia WhatsApp/SMS                          │
│    - API processa e prepara webhook                      │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 2. HTTP POST: Webhook enviado para Odoo                 │
│    POST https://odoo.com/chat_room/webhook/<token>       │
│    {                                                     │
│        "chatId": "5511999887766@c.us",                   │
│        "body": "Olá, preciso de ajuda",                  │
│        "fromMe": false,                                  │
│        "type": "chat",                                   │
│        "id": "msg_external_123",                         │
│        "timestamp": 1700000000                           │
│    }                                                     │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 3. ROUTE: Controller recebe requisição                  │
│    @http.route('/chat_room/webhook/<token>',            │
│                type='json', auth='public', csrf=False)   │
│    def webhook_whatsapp(self, token, **kwargs):         │
│        # 1. Valida token                                 │
│        connector = env['acrux.chat.connector'].search([  │
│            ('token', '=', token)                         │
│        ])                                                │
│        if not connector:                                 │
│            return {'status': 'error', 'msg': 'Invalid'}  │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 4. PARSE: Extrai dados do payload                       │
│    data = request.jsonrequest                            │
│    chat_id = data.get('chatId')  # "5511999887766@c.us" │
│    phone = extract_phone(chat_id) # "5511999887766"     │
│    text = data.get('body')                               │
│    msg_id = data.get('id')                               │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 5. SEARCH: Busca conversa existente                     │
│    conversation = env['acrux.chat.conversation'].search([│
│        ('number', '=', phone),                           │
│        ('connector_id', '=', connector.id),              │
│    ], limit=1)                                           │
└───────────────────────┬──────────────────────────────────┘
                        │
          ┌─────────────┴──────────────┐
          │                            │
          ▼ Não encontrado             ▼ Encontrado
┌─────────────────────┐      ┌─────────────────────┐
│ 6a. CREATE:         │      │ 6b. REOPEN:         │
│ Nova conversa       │      │ Reabre se 'done'    │
│                     │      │                     │
│ partner = find/     │      │ if conv.status ==   │
│   create_partner()  │      │    'done':          │
│                     │      │   conv.status='new' │
│ conversation =      │      │                     │
│   create({          │      │                     │
│     'name': name,   │      │                     │
│     'number': phone,│      │                     │
│     'connector_id': │      │                     │
│       connector.id, │      │                     │
│     'res_partner_id'│      │                     │
│       : partner.id, │      │                     │
│     'status': 'new' │      │                     │
│   })                │      │                     │
└─────────────────────┘      └─────────────────────┘
          │                            │
          └─────────────┬──────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 7. MESSAGE: Cria registro de mensagem                   │
│    message = env['acrux.chat.message'].create({         │
│        'contact_id': conversation.id,                    │
│        'text': text,                                     │
│        'ttype': 'text',                                  │
│        'from_me': False,  ← Recebido                     │
│        'msg_id': msg_id,                                 │
│        'date_message': datetime.fromtimestamp(ts),       │
│    })                                                    │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 8. NOTIFY: Notifica agente via longpolling              │
│    - Se desk_notify == 'all': notifica todos             │
│    - Se desk_notify == 'mines': notifica agent_id        │
│    - Se desk_notify == 'none': não notifica              │
│                                                          │
│    self.env['bus.bus'].sendone(                          │
│        channel='acrux_chat_new_message',                 │
│        message={                                         │
│            'conversation_id': conv.id,                   │
│            'message_id': msg.id,                         │
│        }                                                 │
│    )                                                     │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 9. UI: JavaScript recebe notification                   │
│    - Som de notificação (se habilitado)                 │
│    - Badge no ícone do chat                              │
│    - Conversa movida para topo do Kanban                │
│    - Se conversa está aberta: mensagem aparece em tempo  │
│      real no thread                                      │
└──────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 10. RESPONSE: Retorna 200 OK para API externa           │
│     return {'status': 'ok', 'message_id': msg.id}       │
│                                                          │
│     ⚠️ IMPORTANTE: Sempre retornar 200, mesmo com erro  │
│     Senão API externa reenvia webhook infinitamente     │
└──────────────────────────────────────────────────────────┘
```

---

### 3.3 Fluxo: Atribuir Conversa a Agente

```
┌──────────────────────────────────────────────────────────┐
│ 1. TRIGGER: Nova conversa criada (via webhook)          │
│    conversation.status = 'new'                           │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 2. CHECK: Verificar assing_type do connector            │
│    - 'connector': Auto-atribui para agente disponível   │
│    - 'agent': Atribui para agente específico            │
│    - 'team': Atribui para equipe de vendas              │
└───────────────────────┬──────────────────────────────────┘
                        │
          ┌─────────────┴──────────────┬──────────────┐
          │                            │              │
          ▼ connector                  ▼ agent        ▼ team
┌─────────────────────┐      ┌─────────────────┐    ┌──────────────┐
│ Auto Assing:        │      │ Fixed Agent:    │    │ Team Round   │
│                     │      │                 │    │ Robin:       │
│ agents = env[       │      │ agent = conn.   │    │              │
│   'res.users'       │      │   default_agent │    │ team = conn. │
│ ].search([          │      │                 │    │   team_id    │
│   ('active','=',T), │      │ conv.write({    │    │              │
│   ('is_agent','=',T)│      │   'agent_id':   │    │ members =    │
│ ])                  │      │     agent.id    │    │   team.member│
│                     │      │ })              │    │   _ids       │
│ # Round robin       │      │                 │    │              │
│ last_assing = get() │      │                 │    │ next_agent = │
│ next_agent = next() │      │                 │    │   round_robin│
│                     │      │                 │    │   (members)  │
│ conv.write({        │      │                 │    │              │
│   'agent_id':       │      │                 │    │ conv.write({ │
│     next_agent.id   │      │                 │    │   'agent_id':│
│ })                  │      │                 │    │     next.id, │
│                     │      │                 │    │   'team_id': │
└─────────────────────┘      └─────────────────┘    │     team.id})│
          │                            │              └──────────────┘
          └─────────────┬──────────────┘              │
                        │◄────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────┐
│ 3. NOTIFY: Notifica agente atribuído                    │
│    - Email (se configurado)                              │
│    - Push notification (mobile app)                      │
│    - Desktop notification (Odoo web)                     │
│    - Badge no menu ChatRoom                              │
└──────────────────────────────────────────────────────────┘
```

---

## 4. API Endpoints e Rotas

### 4.1 Rotas HTTP do WhatsApp Connector

```python
# whatsapp_connector/controllers/main.py

# ────────────────────────────────────────────────────────
# WEBHOOKS (Recebimento de mensagens)
# ────────────────────────────────────────────────────────

@http.route('/chat_room/webhook/<string:token>',
            type='json', auth='public', methods=['POST'], csrf=False)
def webhook_whatsapp(self, token, **kwargs):
    """
    Webhook principal para receber mensagens de WhatsApp

    URL: https://odoo.com/chat_room/webhook/33860850-e93b-4ce6-9756-778b92def7fd
    """
    pass


@http.route('/chat_room/status/<string:token>',
            type='json', auth='public', methods=['POST'], csrf=False)
def webhook_status(self, token, **kwargs):
    """
    Webhook para receber atualizações de status
    (entregue, lido, falha)

    Payload:
    {
        "id": "msg_123",
        "status": "delivered",  # ou "read", "failed"
        "timestamp": 1700000000
    }
    """
    pass


# ────────────────────────────────────────────────────────
# UI ACTIONS (Ações da interface)
# ────────────────────────────────────────────────────────

@http.route('/chat_room/init_conversation',
            type='json', auth='user', methods=['POST'])
def init_conversation(self, partner_id, connector_id):
    """
    Inicia nova conversa com parceiro

    Chamado quando usuário clica em "Abrir Chat" no res.partner
    """
    pass


@http.route('/chat_room/send_message',
            type='json', auth='user', methods=['POST'])
def send_message(self, conversation_id, text, attachments=None):
    """
    Envia mensagem em conversa existente

    Chamado quando agente envia mensagem via UI
    """
    pass


@http.route('/chat_room/upload_attachment',
            type='http', auth='user', methods=['POST'])
def upload_attachment(self, conversation_id, file):
    """
    Upload de arquivo (imagem, PDF, etc)

    Retorna: {'attachment_id': 123, 'url': 'https://...'}
    """
    pass


# ────────────────────────────────────────────────────────
# DADOS (Queries para preencher UI)
# ────────────────────────────────────────────────────────

@http.route('/chat_room/conversations',
            type='json', auth='user', methods=['POST'])
def get_conversations(self, connector_id, status='current', limit=50):
    """
    Lista conversas para preencher Kanban

    Retorna: [
        {
            'id': 1,
            'name': 'João Silva',
            'number_format': '+55 11 99988-7766',
            'last_received': '2025-11-16 10:30:00',
            'unread_count': 3,
            'image_128': 'data:image/png;base64,...',
        },
        ...
    ]
    """
    pass


@http.route('/chat_room/messages',
            type='json', auth='user', methods=['POST'])
def get_messages(self, conversation_id, limit=100, offset=0):
    """
    Lista mensagens de uma conversa

    Usado para preencher thread de mensagens
    """
    pass


# ────────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ────────────────────────────────────────────────────────

@http.route('/chat_room/connector/test',
            type='json', auth='user', methods=['POST'])
def test_connector(self, connector_id):
    """
    Testa conexão com API externa

    Retorna: {'status': 'ok', 'message': 'Connected'}
    """
    pass
```

---

### 4.2 RPC Methods (Chamados via JavaScript)

```javascript
// static/src/js/acrux_chat_conversation.js

// ────────────────────────────────────────────────────────
// ENVIO DE MENSAGENS
// ────────────────────────────────────────────────────────

/**
 * Envia mensagem de texto
 */
async sendMessage(conversationId, text) {
    return this._rpc({
        model: 'acrux.chat.conversation',
        method: 'send_message',
        args: [conversationId, text],
    });
}

/**
 * Envia mensagem com arquivo anexo
 */
async sendAttachment(conversationId, attachmentId, caption) {
    return this._rpc({
        model: 'acrux.chat.conversation',
        method: 'send_attachment',
        args: [conversationId, attachmentId, caption],
    });
}

/**
 * Envia template rápido
 */
async sendTemplate(conversationId, templateId, variables) {
    return this._rpc({
        model: 'acrux.chat.conversation',
        method: 'send_template',
        args: [conversationId, templateId, variables],
    });
}


// ────────────────────────────────────────────────────────
// ATRIBUIÇÃO DE CONVERSAS
// ────────────────────────────────────────────────────────

/**
 * Atribui conversa para agente
 */
async assignAgent(conversationId, agentId) {
    return this._rpc({
        model: 'acrux.chat.conversation',
        method: 'write',
        args: [[conversationId], {agent_id: agentId}],
    });
}

/**
 * Marca conversa como concluída
 */
async archiveConversation(conversationId) {
    return this._rpc({
        model: 'acrux.chat.conversation',
        method: 'write',
        args: [[conversationId], {status: 'done'}],
    });
}


// ────────────────────────────────────────────────────────
// BUSCA E FILTROS
// ────────────────────────────────────────────────────────

/**
 * Busca conversas por texto
 */
async searchConversations(query) {
    return this._rpc({
        model: 'acrux.chat.conversation',
        method: 'search_read',
        kwargs: {
            domain: [
                '|', '|',
                ['name', 'ilike', query],
                ['number', 'ilike', query],
                ['res_partner_id.email', 'ilike', query],
            ],
            fields: ['id', 'name', 'number_format', 'image_128'],
            limit: 20,
        },
    });
}


// ────────────────────────────────────────────────────────
// NOTIFICAÇÕES (Longpolling Bus)
// ────────────────────────────────────────────────────────

/**
 * Subscreve a canal de notificações
 */
startPolling() {
    this.call('bus_service', 'addChannel', 'acrux_chat_new_message');
    this.call('bus_service', 'addEventListener', 'notification', this.onNotification.bind(this));
}

/**
 * Processa notificação recebida
 */
onNotification(notifications) {
    for (let notif of notifications) {
        if (notif[0] === 'acrux_chat_new_message') {
            const data = notif[1];
            this.handleNewMessage(data.conversation_id, data.message_id);
        }
    }
}
```

---

## 5. JavaScript e Frontend

### 5.1 Estrutura do Widget Kanban

```javascript
// static/src/js/acrux_chat_conversation.js

odoo.define('whatsapp_connector.ChatConversation', function (require) {
    "use strict";

    const AbstractField = require('web.AbstractField');
    const core = require('web.core');
    const QWeb = core.qweb;

    /**
     * Widget customizado para Kanban de conversas
     */
    const ChatConversationKanban = AbstractField.extend({
        template: 'whatsapp_connector.ChatConversationKanban',

        events: {
            'click .o_chat_conversation_card': '_onClickConversation',
            'click .o_chat_send_button': '_onClickSend',
            'keypress .o_chat_input': '_onKeyPress',
        },

        /**
         * Inicialização
         */
        init: function () {
            this._super.apply(this, arguments);
            this.conversations = [];
            this.activeConversation = null;
        },

        /**
         * Renderiza a view
         */
        willStart: function () {
            return this._super.apply(this, arguments).then(() => {
                return this._loadConversations();
            });
        },

        /**
         * Carrega conversas do backend
         */
        _loadConversations: function () {
            return this._rpc({
                route: '/chat_room/conversations',
                params: {
                    connector_id: this.connector_id,
                    status: 'current',
                    limit: 50,
                },
            }).then((conversations) => {
                this.conversations = conversations;
                this._renderConversations();
            });
        },

        /**
         * Renderiza lista de conversas
         */
        _renderConversations: function () {
            const $container = this.$('.o_chat_conversation_list');
            $container.empty();

            for (let conv of this.conversations) {
                const $card = $(QWeb.render('whatsapp_connector.ConversationCard', {
                    conversation: conv,
                }));
                $container.append($card);
            }
        },

        /**
         * Abre thread de mensagens
         */
        _onClickConversation: function (ev) {
            const conversationId = $(ev.currentTarget).data('id');
            this._openConversation(conversationId);
        },

        /**
         * Carrega mensagens da conversa
         */
        _openConversation: function (conversationId) {
            return this._rpc({
                route: '/chat_room/messages',
                params: {
                    conversation_id: conversationId,
                    limit: 100,
                },
            }).then((messages) => {
                this.activeConversation = conversationId;
                this._renderMessages(messages);
                this._scrollToBottom();
            });
        },

        /**
         * Renderiza mensagens no thread
         */
        _renderMessages: function (messages) {
            const $thread = this.$('.o_chat_thread');
            $thread.empty();

            for (let msg of messages) {
                const $bubble = $(QWeb.render('whatsapp_connector.MessageBubble', {
                    message: msg,
                }));
                $thread.append($bubble);
            }
        },

        /**
         * Envia mensagem (Enter ou botão)
         */
        _onKeyPress: function (ev) {
            if (ev.which === 13 && !ev.shiftKey) {  // Enter (sem Shift)
                ev.preventDefault();
                this._sendMessage();
            }
        },

        _onClickSend: function () {
            this._sendMessage();
        },

        /**
         * Envia mensagem via RPC
         */
        _sendMessage: function () {
            const text = this.$('.o_chat_input').val().trim();
            if (!text || !this.activeConversation) return;

            return this._rpc({
                model: 'acrux.chat.conversation',
                method: 'send_message',
                args: [this.activeConversation, text],
            }).then((result) => {
                // Limpa input
                this.$('.o_chat_input').val('');

                // Adiciona mensagem localmente (otimista)
                this._addMessageToThread({
                    id: result.message_id,
                    text: text,
                    from_me: true,
                    date_message: moment().format('YYYY-MM-DD HH:mm:ss'),
                });
            });
        },

        /**
         * Adiciona mensagem ao thread (sem recarregar tudo)
         */
        _addMessageToThread: function (message) {
            const $bubble = $(QWeb.render('whatsapp_connector.MessageBubble', {
                message: message,
            }));
            this.$('.o_chat_thread').append($bubble);
            this._scrollToBottom();
        },

        /**
         * Scroll automático para última mensagem
         */
        _scrollToBottom: function () {
            const $thread = this.$('.o_chat_thread');
            $thread.scrollTop($thread[0].scrollHeight);
        },

        /**
         * Escuta notificações de novas mensagens
         */
        _startPolling: function () {
            this.call('bus_service', 'addChannel', 'acrux_chat_new_message');
            this.call('bus_service', 'addEventListener', 'notification',
                this._onNotification.bind(this));
        },

        /**
         * Processa notificação de nova mensagem
         */
        _onNotification: function (notifications) {
            for (let notif of notifications) {
                if (notif[0] === 'acrux_chat_new_message') {
                    const data = notif[1];

                    // Se for da conversa ativa, adiciona ao thread
                    if (data.conversation_id === this.activeConversation) {
                        this._loadMessage(data.message_id).then((msg) => {
                            this._addMessageToThread(msg);
                            this._playSound();
                        });
                    } else {
                        // Atualiza badge de não lidas
                        this._updateUnreadBadge(data.conversation_id);
                    }
                }
            }
        },

        /**
         * Toca som de notificação
         */
        _playSound: function () {
            const audio = new Audio('/whatsapp_connector/static/src/sounds/notification.mp3');
            audio.play();
        },
    });

    return ChatConversationKanban;
});
```

---

### 5.2 Templates QWeb

```xml
<!-- static/src/xml/templates.xml -->

<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">

    <!-- ════════════════════════════════════════════════════ -->
    <!-- KANBAN PRINCIPAL                                      -->
    <!-- ════════════════════════════════════════════════════ -->

    <t t-name="whatsapp_connector.ChatConversationKanban">
        <div class="o_chat_container">
            <!-- Sidebar: Lista de conversas -->
            <div class="o_chat_conversation_list">
                <!-- Preenchido via JS -->
            </div>

            <!-- Main: Thread de mensagens -->
            <div class="o_chat_main">
                <div class="o_chat_header">
                    <img class="o_chat_avatar" t-att-src="'data:image/png;base64,' + conversation.image_128"/>
                    <div class="o_chat_name">
                        <t t-esc="conversation.name"/>
                    </div>
                </div>

                <div class="o_chat_thread">
                    <!-- Mensagens preenchidas via JS -->
                </div>

                <div class="o_chat_composer">
                    <textarea class="o_chat_input" placeholder="Digite sua mensagem..."/>
                    <button class="o_chat_send_button btn btn-primary">
                        Enviar
                    </button>
                </div>
            </div>
        </div>
    </t>


    <!-- ════════════════════════════════════════════════════ -->
    <!-- CARD DE CONVERSA (Sidebar)                            -->
    <!-- ════════════════════════════════════════════════════ -->

    <t t-name="whatsapp_connector.ConversationCard">
        <div class="o_chat_conversation_card" t-att-data-id="conversation.id">
            <img class="o_conv_avatar" t-att-src="'data:image/png;base64,' + conversation.image_128"/>

            <div class="o_conv_details">
                <div class="o_conv_name">
                    <t t-esc="conversation.name"/>
                </div>

                <div class="o_conv_last_message">
                    <t t-esc="conversation.last_message_text"/>
                </div>
            </div>

            <div class="o_conv_meta">
                <div class="o_conv_time">
                    <t t-esc="conversation.last_received_relative"/>
                </div>

                <t t-if="conversation.unread_count > 0">
                    <span class="badge badge-primary o_conv_unread">
                        <t t-esc="conversation.unread_count"/>
                    </span>
                </t>
            </div>
        </div>
    </t>


    <!-- ════════════════════════════════════════════════════ -->
    <!-- BALÃO DE MENSAGEM (Thread)                            -->
    <!-- ════════════════════════════════════════════════════ -->

    <t t-name="whatsapp_connector.MessageBubble">
        <div t-att-class="'o_chat_message ' + (message.from_me ? 'o_from_me' : 'o_from_contact')">
            <div class="o_msg_bubble">
                <!-- Texto -->
                <div class="o_msg_text">
                    <t t-esc="message.text"/>
                </div>

                <!-- Timestamp -->
                <div class="o_msg_time">
                    <t t-esc="message.date_message_formatted"/>

                    <!-- Status (só para from_me) -->
                    <t t-if="message.from_me">
                        <t t-if="message.status === 'sent'">✓</t>
                        <t t-if="message.status === 'delivered'">✓✓</t>
                        <t t-if="message.status === 'read'">
                            <span class="text-primary">✓✓</span>
                        </t>
                    </t>
                </div>
            </div>
        </div>
    </t>

</templates>
```

---

## 6. Segredos de Performance

### 6.1 Índices Críticos

```sql
-- ════════════════════════════════════════════════════════
-- CONVERSAS: Queries mais comuns
-- ════════════════════════════════════════════════════════

-- Listar conversas de um connector ordenadas por data
CREATE INDEX idx_conv_connector_date
    ON acrux_chat_conversation(connector_id, last_received DESC);

-- Buscar conversa por número + connector (constraint UNIQUE já cria)
CREATE UNIQUE INDEX idx_conv_number_connector
    ON acrux_chat_conversation(number, connector_id);

-- Filtrar por status e agente
CREATE INDEX idx_conv_status_agent
    ON acrux_chat_conversation(status, agent_id)
    WHERE active = TRUE;

-- Buscar por parceiro
CREATE INDEX idx_conv_partner
    ON acrux_chat_conversation(res_partner_id);


-- ════════════════════════════════════════════════════════
-- MENSAGENS: Queries mais comuns
-- ════════════════════════════════════════════════════════

-- Listar mensagens de uma conversa ordenadas por data
CREATE INDEX idx_msg_conversation_date
    ON acrux_chat_message(contact_id, date_message DESC);

-- Buscar mensagens não lidas
CREATE INDEX idx_msg_unread
    ON acrux_chat_message(contact_id, from_me)
    WHERE from_me = FALSE;

-- Buscar por msg_id externo (webhook)
CREATE INDEX idx_msg_external_id
    ON acrux_chat_message(msg_id);


-- ════════════════════════════════════════════════════════
-- CONNECTOR: Lookup por token (webhook)
-- ════════════════════════════════════════════════════════

CREATE UNIQUE INDEX idx_connector_token
    ON acrux_chat_connector(token);
```

---

### 6.2 Otimizações de Query

```python
# ❌ LENTO: Query separada para cada conversa
for conv in conversations:
    partner = env['res.partner'].browse(conv.res_partner_id.id)
    messages = env['acrux.chat.message'].search([
        ('contact_id', '=', conv.id)
    ], order='date_message desc', limit=1)


# ✅ RÁPIDO: Prefetch com read_group
conversations = env['acrux.chat.conversation'].search([
    ('connector_id', '=', connector_id),
    ('status', '=', 'current'),
])

# Prefetch partners de uma vez
conversations.mapped('res_partner_id')

# Buscar última mensagem com GROUP BY
last_messages = env['acrux.chat.message'].read_group(
    domain=[('contact_id', 'in', conversations.ids)],
    fields=['contact_id', 'text', 'date_message:max'],
    groupby=['contact_id'],
)


# ✅ RÁPIDO: Usar search_read ao invés de search + read
conversations = env['acrux.chat.conversation'].search_read(
    domain=[('connector_id', '=', connector_id)],
    fields=['id', 'name', 'number_format', 'image_128', 'last_received'],
    order='last_received desc',
    limit=50,
)
```

---

### 6.3 Cache Strategy

```python
from odoo.tools import ormcache

class AcruxChatConnector(models.Model):
    _inherit = 'acrux.chat.connector'

    @api.model
    @ormcache('token')
    def get_connector_by_token(self, token):
        """
        Cache de connector por token (webhook usa muito)

        Cache é limpo automaticamente quando connector é modificado
        """
        return self.search([('token', '=', token)], limit=1)


    @api.model
    @ormcache('phone', 'connector_id')
    def find_conversation(self, phone, connector_id):
        """
        Cache de lookup de conversa

        Evita query repetida para mesmo número
        """
        return self.env['acrux.chat.conversation'].search([
            ('number', '=', self.clean_id(phone)),
            ('connector_id', '=', connector_id),
        ], limit=1)
```

---

## 7. Padrões de Design

### 7.1 Herança de Modelos (Mixin Pattern)

```python
# ════════════════════════════════════════════════════════
# PADRÃO: Criar Abstract Model para comportamentos comuns
# ════════════════════════════════════════════════════════

class ChatChannelMixin(models.AbstractModel):
    """
    Mixin para adicionar comportamento de chat em qualquer modelo

    Uso:
    - sale.order pode ter chat
    - crm.lead pode ter chat
    - project.task pode ter chat
    """
    _name = 'chat.channel.mixin'
    _description = 'Chat Channel Mixin'

    conversation_ids = fields.One2many(
        'acrux.chat.conversation',
        'res_id',
        domain=lambda self: [('res_model', '=', self._name)],
        string='Conversations'
    )

    message_count = fields.Integer(
        'Messages',
        compute='_compute_message_count'
    )

    def _compute_message_count(self):
        for record in self:
            record.message_count = len(record.conversation_ids.mapped('message_ids'))

    def action_open_chat(self):
        """Abre widget de chat"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Chat',
            'res_model': 'acrux.chat.conversation',
            'view_mode': 'kanban,form',
            'domain': [
                ('res_model', '=', self._name),
                ('res_id', '=', self.id),
            ],
        }


# Usar o mixin em qualquer modelo:
class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'chat.channel.mixin']  # ← Adiciona chat


class CrmLead(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'chat.channel.mixin']  # ← Adiciona chat
```

---

### 7.2 Strategy Pattern (Connector Types)

```python
# ════════════════════════════════════════════════════════
# PADRÃO: Strategy para diferentes tipos de API
# ════════════════════════════════════════════════════════

class AcruxChatConnector(models.Model):
    _name = 'acrux.chat.connector'

    connector_type = fields.Selection([
        ('chatapi', 'ChatAPI'),
        ('gupshup', 'GupShup'),
        ('sms', 'SMS'),
    ])

    def _get_api_strategy(self):
        """
        Factory method: retorna estratégia correta de API
        """
        self.ensure_one()

        strategies = {
            'chatapi': ChatAPIStrategy,
            'gupshup': GupShupStrategy,
            'sms': SMSStrategy,
        }

        strategy_class = strategies.get(self.connector_type)
        if not strategy_class:
            raise ValueError(f'Unknown connector type: {self.connector_type}')

        return strategy_class(self)

    def send_message(self, phone, text):
        """
        Envia mensagem usando estratégia correta
        """
        strategy = self._get_api_strategy()
        return strategy.send_message(phone, text)


# ════════════════════════════════════════════════════════
# ESTRATÉGIAS CONCRETAS
# ════════════════════════════════════════════════════════

class BaseAPIStrategy:
    """Interface base para todas as estratégias"""

    def __init__(self, connector):
        self.connector = connector

    def send_message(self, phone, text):
        raise NotImplementedError()

    def send_media(self, phone, media_url, caption):
        raise NotImplementedError()


class ChatAPIStrategy(BaseAPIStrategy):
    """Estratégia para ChatAPI (WhatsApp)"""

    def send_message(self, phone, text):
        endpoint = f"{self.connector.endpoint}/sendMessage"
        payload = {
            'phone': phone,
            'body': text,
        }
        return requests.post(endpoint, json=payload, headers={
            'Authorization': f'Bearer {self.connector.api_key}'
        })


class GupShupStrategy(BaseAPIStrategy):
    """Estratégia para GupShup (WhatsApp)"""

    def send_message(self, phone, text):
        endpoint = "https://api.gupshup.io/sm/api/v1/msg"
        payload = {
            'channel': 'whatsapp',
            'source': self.connector.api_key,
            'destination': phone,
            'message': json.dumps({'type': 'text', 'text': text}),
        }
        return requests.post(endpoint, data=payload)


class SMSStrategy(BaseAPIStrategy):
    """Estratégia para SMS (Kolmeya)"""

    def send_message(self, phone, text):
        provider = self.connector.sms_provider_id
        return provider.send_sms(phone, text)
```

---

### 7.3 Observer Pattern (Notifications)

```python
# ════════════════════════════════════════════════════════
# PADRÃO: Observer para notificar agentes
# ════════════════════════════════════════════════════════

class AcruxChatMessage(models.Model):
    _name = 'acrux.chat.message'

    @api.model
    def create(self, vals):
        """
        Ao criar mensagem, notifica observers (agentes)
        """
        message = super().create(vals)

        # Se mensagem recebida (not from_me)
        if not message.from_me:
            message._notify_observers()

        return message

    def _notify_observers(self):
        """
        Notifica todos os observers interessados nesta mensagem
        """
        self.ensure_one()

        # 1. Notifica via Bus (tempo real UI)
        self._notify_bus()

        # 2. Notifica via Email (se configurado)
        if self.contact_id.connector_id.notify_email:
            self._notify_email()

        # 3. Notifica via Push (mobile app)
        if self.contact_id.connector_id.notify_push:
            self._notify_push()

    def _notify_bus(self):
        """Notificação via longpolling bus"""
        channel = 'acrux_chat_new_message'

        # Decide quem recebe notificação
        desk_notify = self.contact_id.connector_id.desk_notify

        if desk_notify == 'all':
            # Todos os agentes
            users = self.env['res.users'].search([('is_agent', '=', True)])
        elif desk_notify == 'mines':
            # Só o agente atribuído
            users = self.contact_id.agent_id if self.contact_id.agent_id else self.env['res.users']
        else:  # 'none'
            users = self.env['res.users']

        # Envia notificação
        for user in users:
            self.env['bus.bus'].sendone(
                channel,
                {
                    'conversation_id': self.contact_id.id,
                    'message_id': self.id,
                    'user_id': user.id,
                }
            )

    def _notify_email(self):
        """Notificação via email"""
        template = self.env.ref('whatsapp_connector.email_new_message')
        template.send_mail(self.id, force_send=True)

    def _notify_push(self):
        """Notificação push (mobile)"""
        # Integração com FCM (Firebase Cloud Messaging)
        pass
```

---

## Conclusão

Este documento revela **TODOS** os segredos técnicos do AcruxLab WhatsApp Connector:

✅ Arquitetura de 3 camadas (Connector → Conversation → Message)
✅ Constraint UNIQUE crítico (number, connector_id)
✅ Métodos de validação (assert_id, clean_id, format_id)
✅ Fluxos completos (envio, recebimento, atribuição)
✅ Estrutura JavaScript (widgets, templates QWeb)
✅ Otimizações de performance (índices, cache, prefetch)
✅ Padrões de design (Strategy, Observer, Mixin)

Com este conhecimento, você pode:
1. Criar connector para qualquer canal (Telegram, Instagram, etc)
2. Otimizar queries e melhorar performance
3. Customizar comportamento de notificações
4. Integrar com outras APIs de mensageria
5. Criar soluções white-label similares

---

**Criado em:** 2025-11-16
**Versão:** 1.0.0
**Status:** ✅ Completo

---
