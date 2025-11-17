# 📱 Documentação Técnica Completa: Contact Center SMS Integration

**Versão:** 1.0.0
**Data:** 2025-11-16
**Autor:** Anderson Oliveira / Claude
**Odoo Version:** 15.0
**Database:** realcred (PostgreSQL 12)

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Módulos Desenvolvidos](#módulos-desenvolvidos)
4. [Análise AcruxLab WhatsApp Connector](#análise-acruxlab-whatsapp-connector)
5. [Implementação Detalhada](#implementação-detalhada)
6. [Problemas Encontrados e Soluções](#problemas-encontrados-e-soluções)
7. [Lições Aprendidas](#lições-aprendidas)
8. [Como Recriar do Zero](#como-recriar-do-zero)
9. [Testes e Validação](#testes-e-validação)
10. [Manutenção e Troubleshooting](#manutenção-e-troubleshooting)

---

## 1. Visão Geral

### 1.1 Objetivo do Projeto

Criar uma integração entre SMS (via Kolmeya API) e WhatsApp (via AcruxLab ChatRoom) para unificar atendimento de múltiplos canais em uma única interface no Odoo 15.

### 1.2 Tecnologias Utilizadas

- **Odoo 15.0** - Framework ERP
- **Python 3.8** - Linguagem de programação
- **PostgreSQL 12** - Banco de dados
- **AcruxLab WhatsApp Connector** - Módulo base para chat
- **Kolmeya SMS API** - Provedor de SMS brasileiro
- **Ubuntu 20.04.6 LTS** - Sistema operacional

### 1.3 Estrutura de Módulos

```
odoo_15_sr/
├── sms_base_sr/              # Módulo base SMS
│   ├── models/
│   │   ├── sms_message.py    # Modelo de mensagens SMS
│   │   ├── sms_template.py   # Templates de SMS
│   │   ├── sms_provider.py   # Provedores abstratos
│   │   └── res_partner.py    # Extensão de parceiros
│   ├── views/
│   ├── security/
│   └── __manifest__.py
│
├── sms_kolmeya/              # Integração Kolmeya
│   ├── models/
│   │   ├── kolmeya_api.py    # Wrapper da API
│   │   └── kolmeya_provider.py
│   └── __manifest__.py
│
└── contact_center_sms/       # Integração ChatRoom
    ├── models/
    │   ├── connector.py       # Extensão do connector
    │   ├── conversation.py    # Extensão de conversas
    │   ├── message.py         # Extensão de mensagens
    │   └── connector_sms.py   # SMS connector logic
    ├── controllers/
    │   └── webhook.py         # Webhook Kolmeya
    └── __manifest__.py
```

---

## 2. Arquitetura do Sistema

### 2.1 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────┐
│                  ODOO 15 FRONTEND                   │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │      AcruxLab ChatRoom Interface (Kanban)     │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐    │ │
│  │  │WhatsApp 1│  │WhatsApp 2│  │  SMS 1   │    │ │
│  │  │Contact   │  │Contact   │  │Contact   │    │ │
│  │  └──────────┘  └──────────┘  └──────────┘    │ │
│  └───────────────────────────────────────────────┘ │
└──────────────┬──────────────────────┬───────────────┘
               │                      │
       ┌───────▼────────┐    ┌────────▼─────────┐
       │ WhatsApp       │    │ SMS Contact      │
       │ Connector      │    │ Center Module    │
       │ (AcruxLab)     │    │ (Nossa Criação)  │
       └───────┬────────┘    └────────┬─────────┘
               │                      │
       ┌───────▼────────┐    ┌────────▼─────────┐
       │ acrux.chat.*   │    │ Extend Models:   │
       │ Base Models    │    │ - connector      │
       │                │◄───┤ - conversation   │
       │                │    │ - message        │
       └───────┬────────┘    └────────┬─────────┘
               │                      │
       ┌───────▼────────┐    ┌────────▼─────────┐
       │ ChatSmart API  │    │   Kolmeya API    │
       │ (WhatsApp)     │    │     (SMS)        │
       └────────────────┘    └──────────────────┘
```

### 2.2 Fluxo de Dados

#### 2.2.1 Envio de SMS

```
User Action (ChatRoom UI)
    ↓
acrux.chat.message.create()
    ↓
contact_center_sms.message (override)
    ↓
Verifica: channel_type == 'sms' ?
    ↓ SIM
sms_provider.send_sms()
    ↓
kolmeya_api.send_sms()
    ↓
HTTP POST → https://kolmeya.com.br/api/v1/sms/store
    ↓
Retorna job_id
    ↓
Atualiza sms.message.external_id
```

#### 2.2.2 Recebimento de SMS (via Webhook)

```
Kolmeya Webhook → POST /contact_center_sms/webhook/<token>
    ↓
Valida token do connector
    ↓
Extrai: phone, message, timestamp
    ↓
Busca/Cria res.partner (phone)
    ↓
Cria sms.message (direction='incoming')
    ↓
Busca acrux.chat.conversation (number + connector_id)
    ↓
Se não existe: cria conversa nova
    ↓
Cria acrux.chat.message (from_me=False)
    ↓
Notifica agentes (desk_notify)
```

### 2.3 Banco de Dados

#### 2.3.1 Tabelas Principais

**acrux_chat_connector** (Connector = Canal de comunicação)
```sql
CREATE TABLE acrux_chat_connector (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,              -- 'SMS Kolmeya'
    connector_type VARCHAR NOT NULL,    -- 'sms', 'whatsapp', etc
    token VARCHAR NOT NULL UNIQUE,      -- UUID para autenticação
    uuid VARCHAR NOT NULL,              -- ID numérico único
    company_id INTEGER NOT NULL,        -- res_company.id
    source VARCHAR NOT NULL DEFAULT '/',
    endpoint VARCHAR NOT NULL,          -- URL da API
    odoo_url VARCHAR NOT NULL,          -- URL do Odoo
    sequence INTEGER NOT NULL,
    border_color VARCHAR NOT NULL,      -- Cor no Kanban
    desk_notify VARCHAR NOT NULL,       -- 'mines', 'all', 'none'
    assing_type VARCHAR NOT NULL,       -- 'connector', 'agent'
    sms_provider_id INTEGER,            -- FK: sms_provider.id
    -- ... outros campos do WhatsApp
    CONSTRAINT fk_sms_provider
        FOREIGN KEY (sms_provider_id)
        REFERENCES sms_provider(id)
);
```

**acrux_chat_conversation** (Conversa = Thread de mensagens)
```sql
CREATE TABLE acrux_chat_conversation (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,              -- Nome do contato
    number VARCHAR NOT NULL,            -- Telefone (obrigatório!)
    number_format VARCHAR,              -- Telefone formatado
    connector_id INTEGER NOT NULL,      -- FK: acrux_chat_connector.id
    res_partner_id INTEGER,             -- FK: res_partner.id
    status VARCHAR DEFAULT 'new',       -- 'new', 'current', 'done'
    channel_type VARCHAR DEFAULT 'whatsapp', -- 'sms', 'whatsapp'
    sms_message_id INTEGER,             -- FK: sms_message.id (opcional)
    -- ... campos de timestamp, agente, etc
    CONSTRAINT unique_conversation
        UNIQUE(number, connector_id)
);
```

**acrux_chat_message** (Mensagem individual)
```sql
CREATE TABLE acrux_chat_message (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL,        -- FK: acrux_chat_conversation.id
    text TEXT,                          -- Conteúdo da mensagem
    ttype VARCHAR NOT NULL,             -- 'text', 'image', 'audio', etc
    from_me BOOLEAN DEFAULT FALSE,      -- Enviado por nós?
    date_message TIMESTAMP,
    -- ... campos de mídia, status, etc
);
```

**sms_provider** (Provedor de SMS)
```sql
CREATE TABLE sms_provider (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,              -- 'Kolmeya'
    provider_type VARCHAR NOT NULL,     -- 'kolmeya', 'twilio', etc
    api_url VARCHAR NOT NULL,
    api_key VARCHAR,
    api_secret VARCHAR,
    segment_id VARCHAR,                 -- Kolmeya specific
    active BOOLEAN DEFAULT TRUE
);
```

**sms_message** (Mensagem SMS - nosso modelo)
```sql
CREATE TABLE sms_message (
    id SERIAL PRIMARY KEY,
    partner_id INTEGER,                 -- FK: res_partner.id
    provider_id INTEGER NOT NULL,       -- FK: sms_provider.id
    phone VARCHAR NOT NULL,
    body TEXT NOT NULL,
    direction VARCHAR NOT NULL,         -- 'outgoing', 'incoming'
    state VARCHAR DEFAULT 'draft',      -- 'draft', 'sent', 'delivered', 'failed'
    external_id VARCHAR,                -- job_id do Kolmeya
    error_message TEXT,
    date_sent TIMESTAMP,
    date_delivered TIMESTAMP
);
```

---

## 3. Módulos Desenvolvidos

### 3.1 sms_base_sr

**Propósito:** Módulo base para gerenciamento de SMS, independente de provedor.

**Arquivo:** `sms_base_sr/__manifest__.py`
```python
{
    'name': 'SMS Base - SempreReal',
    'version': '15.0.1.0.2',
    'category': 'Marketing/SMS',
    'summary': 'Core SMS with Templates and Wizard',
    'description': '''
SMS Base Module for SempreReal
===============================

Features:
---------
* SMS messages management
* SMS templates
* Compose wizard
* Provider abstraction (Kolmeya, etc.)
* Partner integration
* Delivery status tracking
''',
    'author': 'SempreReal',
    'website': 'https://www.semprereal.com',
    'depends': ['base', 'mail', 'contacts'],
    'data': [
        'security/sms_security.xml',
        'security/ir.model.access.csv',
        'views/sms_message_views.xml',
        'views/sms_template_views.xml',
        'views/sms_provider_views.xml',
        'views/sms_compose_views.xml',
        'views/res_partner_views.xml',
        'views/sms_menu.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,  # ← Aparece como App no painel
    'auto_install': False,
    'license': 'LGPL-3',
}
```

**Modelo Principal:** `sms_base_sr/models/sms_message.py`
```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SMSMessage(models.Model):
    _name = 'sms.message'
    _description = 'SMS Message'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Campos principais
    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
        ondelete='set null',
        tracking=True
    )

    user_id = fields.Many2one(
        'res.users',
        'Sent by',
        default=lambda self: self.env.user,
        tracking=True
    )

    provider_id = fields.Many2one(
        'sms.provider',
        'SMS Provider',
        required=True,
        tracking=True
    )

    phone = fields.Char(
        'Phone Number',
        required=True,
        tracking=True
    )

    body = fields.Text(
        'Message Content',
        required=True,
        tracking=True
    )

    direction = fields.Selection([
        ('outgoing', 'Outgoing'),
        ('incoming', 'Incoming'),
    ], string='Direction', required=True, default='outgoing', tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ], string='Status', default='draft', tracking=True)

    external_id = fields.Char(
        'External ID',
        help='Job ID from SMS provider',
        tracking=True
    )

    error_message = fields.Text('Error Message')

    date_sent = fields.Datetime('Sent Date', readonly=True)
    date_delivered = fields.Datetime('Delivered Date', readonly=True)

    # Métodos
    def send_sms(self):
        """Send SMS using configured provider"""
        self.ensure_one()

        if self.state != 'draft':
            raise ValidationError(_('Only draft messages can be sent.'))

        if not self.provider_id:
            raise ValidationError(_('No SMS provider configured.'))

        try:
            # Chama método do provider
            result = self.provider_id.send_sms(
                phone=self.phone,
                message=self.body,
                reference=str(self.id)
            )

            # Atualiza registro
            self.write({
                'state': 'sent',
                'external_id': result.get('job_id'),
                'date_sent': fields.Datetime.now(),
            })

            return result

        except Exception as e:
            self.write({
                'state': 'failed',
                'error_message': str(e),
            })
            raise

    @api.model
    def create_from_webhook(self, vals):
        """
        Cria SMS recebido via webhook

        vals = {
            'phone': '+5511999887766',
            'body': 'Mensagem do cliente',
            'provider_id': 1,
            'external_id': 'kolmeya_id_123',
        }
        """
        # Busca ou cria parceiro
        partner = self.env['res.partner'].search([
            ('phone', '=', vals['phone'])
        ], limit=1)

        if not partner:
            partner = self.env['res.partner'].create({
                'name': f"SMS Client {vals['phone'][-4:]}",
                'phone': vals['phone'],
            })

        vals.update({
            'partner_id': partner.id,
            'direction': 'incoming',
            'state': 'delivered',
            'date_delivered': fields.Datetime.now(),
        })

        return self.create(vals)
```

**Provider Abstrato:** `sms_base_sr/models/sms_provider.py`
```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SMSProvider(models.Model):
    _name = 'sms.provider'
    _description = 'SMS Provider'

    name = fields.Char('Provider Name', required=True)

    provider_type = fields.Selection([
        ('kolmeya', 'Kolmeya'),
        ('twilio', 'Twilio'),
        ('nexmo', 'Nexmo'),
    ], string='Provider Type', required=True)

    api_url = fields.Char('API URL', required=True)
    api_key = fields.Char('API Key')
    api_secret = fields.Char('API Secret')
    segment_id = fields.Char('Segment ID')  # Kolmeya specific

    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', 'Company',
                                  default=lambda self: self.env.company)

    def send_sms(self, phone, message, reference=None):
        """
        Método abstrato - deve ser implementado por provider específico

        Returns:
            dict: {'job_id': 'xxx', 'status': 'sent'}
        """
        self.ensure_one()
        raise UserError(_('Provider %s has not implemented send_sms()') % self.name)
```

**Views Menu:** `sms_base_sr/views/sms_menu.xml`
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Menu raiz com ícone -->
    <menuitem id="menu_sms_root"
              name="SMS"
              sequence="100"
              web_icon="sms_base_sr,static/description/icon.png"/>

    <!-- Action para mensagens -->
    <record id="action_sms_message" model="ir.actions.act_window">
        <field name="name">SMS Messages</field>
        <field name="res_model">sms.message</field>
        <field name="view_mode">tree,form</field>
    </record>

    <!-- Submenu mensagens -->
    <menuitem id="menu_sms_messages"
              name="Messages"
              parent="menu_sms_root"
              action="action_sms_message"
              sequence="10"/>
</odoo>
```

**IMPORTANTE: Como fazer ícone aparecer:**
1. Arquivo `static/description/icon.png` (128x128px)
2. Manifest: `'images': ['static/description/icon.png']`
3. Manifest: `'application': True`
4. Menu XML: `web_icon="sms_base_sr,static/description/icon.png"`

---

### 3.2 sms_kolmeya

**Propósito:** Implementação específica da API Kolmeya.

**Arquivo:** `sms_kolmeya/__manifest__.py`
```python
{
    'name': 'SMS Kolmeya Provider',
    'version': '15.0.1.0.0',
    'category': 'Marketing/SMS',
    'summary': 'Kolmeya SMS API Integration',
    'author': 'SempreReal',
    'website': 'https://semprereal.com',
    'depends': ['sms_base_sr'],
    'data': [
        'views/kolmeya_provider_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

**API Wrapper:** `sms_kolmeya/models/kolmeya_api.py`
```python
# -*- coding: utf-8 -*-
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class KolmeyaAPI:
    """
    Wrapper para Kolmeya SMS API
    Documentação: https://kolmeya.com.br/docs/api
    """

    def __init__(self, api_key, segment_id, base_url='https://kolmeya.com.br/api/v1'):
        self.api_key = api_key
        self.segment_id = segment_id
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })

    def _make_request(self, endpoint, method='POST', payload=None):
        """
        Faz requisição para API Kolmeya

        Args:
            endpoint (str): '/sms/store', '/sms/status', etc
            method (str): 'GET', 'POST', 'PUT', 'DELETE'
            payload (dict): Dados a enviar

        Returns:
            dict: Resposta da API

        Raises:
            Exception: Se requisição falhar
        """
        url = f"{self.base_url}{endpoint}"

        try:
            if method == 'GET':
                response = self.session.get(url, params=payload, timeout=30)
            elif method == 'POST':
                response = self.session.post(url, json=payload, timeout=30)
            elif method == 'PUT':
                response = self.session.put(url, json=payload, timeout=30)
            elif method == 'DELETE':
                response = self.session.delete(url, timeout=30)
            else:
                raise ValueError(f'Invalid HTTP method: {method}')

            response.raise_for_status()

            result = response.json()
            _logger.info(f'Kolmeya API {method} {endpoint}: {response.status_code}')

            return result

        except requests.exceptions.RequestException as e:
            _logger.error(f'Kolmeya API error: {e}')
            raise Exception(f'Kolmeya API request failed: {str(e)}')

    def send_sms(self, phone, message, reference=None, webhook_url=None):
        """
        Envia SMS único

        Args:
            phone (str): Número com código do país (ex: 5511999887766)
            message (str): Texto da mensagem
            reference (str): ID de referência customizado
            webhook_url (str): URL para callback de status

        Returns:
            dict: {
                'id': 'job_id_123',
                'valids': 1,
                'invalids': 0,
                'segment': 'segment_id'
            }
        """
        payload = {
            'messages': [{
                'phone': phone,
                'message': message,
            }]
        }

        if reference:
            payload['messages'][0]['reference'] = reference

        # IMPORTANTE: Webhook é por mensagem, não global!
        if webhook_url:
            payload['webhook_url'] = webhook_url

        payload['segment'] = self.segment_id

        result = self._make_request('/sms/store', payload=payload)

        return {
            'job_id': result.get('id'),
            'valids': result.get('valids', 0),
            'invalids': result.get('invalids', 0),
        }

    def send_bulk_sms(self, messages, webhook_url=None):
        """
        Envia múltiplos SMS em lote

        Args:
            messages (list): [
                {'phone': '5511999887766', 'message': 'Texto', 'reference': 'id1'},
                {'phone': '5511888776655', 'message': 'Texto 2', 'reference': 'id2'},
            ]
            webhook_url (str): URL para callbacks

        Returns:
            dict: Resultado do envio
        """
        payload = {
            'messages': messages,
            'segment': self.segment_id,
        }

        if webhook_url:
            payload['webhook_url'] = webhook_url

        return self._make_request('/sms/store', payload=payload)

    def get_status(self, job_id):
        """
        Consulta status de envio

        Args:
            job_id (str): ID retornado no send_sms()

        Returns:
            dict: {'status': 'delivered', 'date': '2025-11-16 10:30:00'}
        """
        return self._make_request(f'/sms/status/{job_id}', method='GET')

    def get_balance(self):
        """
        Consulta saldo de créditos

        Returns:
            dict: {'credits': 1000, 'expires_at': '2025-12-31'}
        """
        return self._make_request('/account/balance', method='GET')
```

**Provider Implementation:** `sms_kolmeya/models/kolmeya_provider.py`
```python
# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError
from .kolmeya_api import KolmeyaAPI


class SMSProvider(models.Model):
    _inherit = 'sms.provider'

    def send_sms(self, phone, message, reference=None):
        """
        Implementa envio via Kolmeya
        """
        self.ensure_one()

        if self.provider_type != 'kolmeya':
            return super().send_sms(phone, message, reference)

        # Valida configuração
        if not self.api_key or not self.segment_id:
            raise UserError(_('Kolmeya API Key and Segment ID are required.'))

        # Instancia API wrapper
        api = KolmeyaAPI(
            api_key=self.api_key,
            segment_id=self.segment_id,
            base_url=self.api_url
        )

        # Prepara webhook URL (se configurado)
        webhook_url = None
        if self.env['ir.config_parameter'].sudo().get_param('web.base.url'):
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            # Webhook será processado por contact_center_sms module
            webhook_url = f"{base_url}/contact_center_sms/webhook/kolmeya"

        # Envia SMS
        try:
            result = api.send_sms(
                phone=phone,
                message=message,
                reference=reference,
                webhook_url=webhook_url
            )

            return result

        except Exception as e:
            raise UserError(_('Failed to send SMS via Kolmeya: %s') % str(e))
```

---

### 3.3 contact_center_sms

**Propósito:** Integração SMS com AcruxLab ChatRoom para interface unificada.

**Arquivo:** `contact_center_sms/__manifest__.py`
```python
{
    'name': 'Contact Center SMS Integration',
    'version': '15.0.1.0.2',
    'category': 'Marketing/SMS',
    'summary': 'Integrate SMS with WhatsApp ChatRoom for Unified Contact Center',
    'description': """
Contact Center SMS Integration
===============================

Integrates SMS (via Kolmeya) with WhatsApp ChatRoom to create a unified
contact center interface.

Features:
---------
* Unified interface for SMS and WhatsApp conversations
* Automatic conversation creation from incoming SMS
* SMS sending through ChatRoom interface
* Webhook integration for delivery status
* Agent assignment and notifications
* Message history and tracking
""",
    'author': 'SempreReal',
    'website': 'https://semprereal.com',
    'license': 'LGPL-3',
    'depends': [
        'whatsapp_connector',  # AcruxLab ChatRoom
        'sms_base_sr',
        'sms_kolmeya',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
```

**⭐ ARQUIVO CRÍTICO - Connector Extension:**
`contact_center_sms/models/connector.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, api


class AcruxChatConnector(models.Model):
    """
    Extensão do Connector do AcruxLab para suportar SMS

    ⚠️ SEGREDO #1: O Connector é a "porta de entrada" de cada canal
    Cada canal (WhatsApp, SMS, Instagram) tem um connector próprio.
    """
    _inherit = 'acrux.chat.connector'

    def assert_id(self, key):
        """
        ⚠️ SEGREDO #2: Validação de número

        O AcruxLab valida se o número é válido para WhatsApp.
        Para SMS, precisamos sobrescrever para aceitar qualquer número.

        PROBLEMA ORIGINAL:
        - ValidationError: 'Invalid number'
        - Motivo: phone_format() é muito restrito

        SOLUÇÃO:
        - Para SMS: validação flexível (qualquer número com dígitos)
        - Para outros: mantém validação original
        """
        self.ensure_one()

        # Se for connector SMS, permite qualquer número válido
        if self.connector_type == 'sms':
            # SMS é mais flexível - apenas verifica se tem dígitos
            if key and any(c.isdigit() for c in str(key)):
                return True
            else:
                # Se não tem dígitos, usa validação padrão
                return super(AcruxChatConnector, self).assert_id(key)

        # Para outros tipos (WhatsApp, etc), usa validação original
        return super(AcruxChatConnector, self).assert_id(key)

    def clean_id(self, key):
        """
        ⚠️ SEGREDO #3: Limpeza de número

        Remove caracteres especiais do número.
        Para WhatsApp, o AcruxLab tem lógica específica.
        Para SMS, apenas removemos tudo exceto dígitos.
        """
        self.ensure_one()

        if self.connector_type == 'sms':
            # Remove tudo exceto dígitos
            return ''.join(filter(str.isdigit, str(key)))

        return super(AcruxChatConnector, self).clean_id(key)

    def format_id(self, key):
        """
        ⚠️ SEGREDO #4: Formatação de número

        Formata número para exibição/comparação.
        WhatsApp usa formato específico.
        SMS usa formato simples: +5511999887766
        """
        self.ensure_one()

        if self.connector_type == 'sms':
            # Para SMS, mantém formato simples: +5511999887766
            cleaned = self.clean_id(key)
            if cleaned and not cleaned.startswith('+'):
                return '+' + cleaned
            return cleaned if cleaned else key

        return super(AcruxChatConnector, self).format_id(key)
```

**⭐ ARQUIVO CRÍTICO - Conversation Extension:**
`contact_center_sms/models/conversation.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AcruxChatConversation(models.Model):
    """
    Extensão das Conversas para suportar SMS

    ⚠️ SEGREDO #5: Conversation = Thread de mensagens
    No AcruxLab, cada conversa é um thread único por:
    - Connector (canal)
    - Number (telefone do cliente)

    Constraint: UNIQUE(number, connector_id)
    """
    _inherit = 'acrux.chat.conversation'

    # Novo campo: tipo de canal
    channel_type = fields.Selection([
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('instagram', 'Instagram'),
        ('messenger', 'Messenger'),
    ], string='Channel Type', default='whatsapp', required=True, index=True)

    # Referência à mensagem SMS original (opcional)
    sms_message_id = fields.Many2one(
        'sms.message',
        'Original SMS',
        ondelete='set null',
        index=True
    )

    @api.model
    def create_from_sms(self, sms_message):
        """
        ⚠️ SEGREDO #6: Criar conversa a partir de SMS recebido

        Chamado quando webhook recebe SMS.
        Cria conversa no ChatRoom automaticamente.

        Args:
            sms_message: recordset de sms.message

        Returns:
            acrux.chat.conversation: Conversa criada/existente
        """
        # Busca connector SMS
        connector = self.env['acrux.chat.connector'].search([
            ('connector_type', '=', 'sms'),
            ('sms_provider_id', '=', sms_message.provider_id.id),
        ], limit=1)

        if not connector:
            raise ValueError(_('No SMS connector configured for provider %s') %
                           sms_message.provider_id.name)

        # Busca conversa existente
        conversation = self.search([
            ('number', '=', connector.clean_id(sms_message.phone)),
            ('connector_id', '=', connector.id),
        ], limit=1)

        # Se não existe, cria nova
        if not conversation:
            conversation = self.create({
                'name': sms_message.partner_id.name if sms_message.partner_id
                        else f"SMS {sms_message.phone[-4:]}",
                'number': connector.clean_id(sms_message.phone),
                'number_format': connector.format_id(sms_message.phone),
                'connector_id': connector.id,
                'res_partner_id': sms_message.partner_id.id if sms_message.partner_id else False,
                'channel_type': 'sms',
                'sms_message_id': sms_message.id,
            })

        # Cria mensagem na conversa
        self.env['acrux.chat.message'].create({
            'contact_id': conversation.id,
            'text': sms_message.body,
            'ttype': 'text',
            'from_me': False,  # Recebido
            'date_message': sms_message.date_delivered or fields.Datetime.now(),
        })

        # Atualiza status da conversa
        if conversation.status == 'done':
            conversation.status = 'new'

        return conversation

    def send_sms_message(self, body):
        """
        ⚠️ SEGREDO #7: Enviar SMS através da conversa

        Chamado quando agente envia mensagem via ChatRoom.

        Args:
            body (str): Texto da mensagem

        Returns:
            dict: Resultado do envio
        """
        self.ensure_one()

        if self.channel_type != 'sms':
            raise ValueError(_('This is not an SMS conversation'))

        if not self.connector_id.sms_provider_id:
            raise ValueError(_('No SMS provider configured for this connector'))

        # Cria registro de SMS
        sms = self.env['sms.message'].create({
            'partner_id': self.res_partner_id.id if self.res_partner_id else False,
            'provider_id': self.connector_id.sms_provider_id.id,
            'phone': self.number_format,
            'body': body,
            'direction': 'outgoing',
            'state': 'draft',
        })

        # Envia SMS
        result = sms.send_sms()

        # Cria mensagem na conversa do ChatRoom
        self.env['acrux.chat.message'].create({
            'contact_id': self.id,
            'text': body,
            'ttype': 'text',
            'from_me': True,  # Enviado
            'date_message': fields.Datetime.now(),
        })

        return result
```

**⭐ ARQUIVO CRÍTICO - Message Extension:**
`contact_center_sms/models/message.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, api


class AcruxChatMessage(models.Model):
    """
    Extensão das Mensagens para interceptar envios SMS

    ⚠️ SEGREDO #8: Hook no create() para enviar SMS
    """
    _inherit = 'acrux.chat.message'

    @api.model
    def create(self, vals):
        """
        Intercepta criação de mensagem para enviar SMS automaticamente

        LÓGICA:
        1. Verifica se conversa é do tipo SMS
        2. Verifica se mensagem é enviada por nós (from_me=True)
        3. Se sim, envia SMS via provider
        """
        # Cria mensagem normalmente
        message = super(AcruxChatMessage, self).create(vals)

        # Se for mensagem enviada em conversa SMS
        if (message.contact_id and
            message.contact_id.channel_type == 'sms' and
            message.from_me and
            message.text):

            try:
                # Envia SMS
                message.contact_id.send_sms_message(message.text)
            except Exception as e:
                # Log erro mas não impede criação da mensagem
                import logging
                _logger = logging.getLogger(__name__)
                _logger.error(f'Failed to send SMS: {e}')

        return message
```

**Webhook Controller:**
`contact_center_sms/controllers/webhook.py`

```python
# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class KolmeyaWebhook(http.Controller):
    """
    ⚠️ SEGREDO #9: Webhook para receber SMS

    Kolmeya envia POST para esta URL quando SMS é recebido ou status muda.

    URL: https://odoo.semprereal.com/contact_center_sms/webhook/<token>
    """

    @http.route('/contact_center_sms/webhook/<string:token>',
                type='json', auth='public', methods=['POST'], csrf=False)
    def kolmeya_webhook(self, token, **kwargs):
        """
        Processa webhook do Kolmeya

        Args:
            token (str): Token do connector (para validar origem)

        Payload esperado:
        {
            "type": "sms_received",
            "phone": "5511999887766",
            "message": "Olá, preciso de ajuda",
            "timestamp": "2025-11-16 10:30:00",
            "reference": "optional_ref"
        }

        Returns:
            dict: {'status': 'ok'}
        """
        try:
            # Valida token
            connector = request.env['acrux.chat.connector'].sudo().search([
                ('token', '=', token),
                ('connector_type', '=', 'sms'),
            ], limit=1)

            if not connector:
                _logger.warning(f'Invalid webhook token: {token}')
                return {'status': 'error', 'message': 'Invalid token'}

            # Parse dados
            data = request.jsonrequest
            webhook_type = data.get('type', 'sms_received')
            phone = data.get('phone')
            message_text = data.get('message')
            external_id = data.get('id') or data.get('reference')

            _logger.info(f'Kolmeya webhook: {webhook_type} from {phone}')

            # Processa de acordo com tipo
            if webhook_type == 'sms_received':
                # Cria SMS recebido
                sms = request.env['sms.message'].sudo().create_from_webhook({
                    'phone': phone,
                    'body': message_text,
                    'provider_id': connector.sms_provider_id.id,
                    'external_id': external_id,
                })

                # Cria/atualiza conversa no ChatRoom
                request.env['acrux.chat.conversation'].sudo().create_from_sms(sms)

            elif webhook_type == 'sms_status':
                # Atualiza status de SMS enviado
                status = data.get('status')  # 'delivered', 'failed', etc

                sms = request.env['sms.message'].sudo().search([
                    ('external_id', '=', external_id)
                ], limit=1)

                if sms:
                    state_map = {
                        'delivered': 'delivered',
                        'failed': 'failed',
                        'sent': 'sent',
                    }
                    sms.state = state_map.get(status, sms.state)

                    if status == 'delivered':
                        sms.date_delivered = http.request.env['ir.fields'].Datetime.now()

            return {'status': 'ok'}

        except Exception as e:
            _logger.error(f'Webhook error: {e}', exc_info=True)
            return {'status': 'error', 'message': str(e)}

    @http.route('/contact_center_sms/webhook/test',
                type='http', auth='public', methods=['GET'])
    def test_webhook(self):
        """Endpoint de teste para verificar se webhook está acessível"""
        return "Webhook OK"
```

---

## 4. Análise AcruxLab WhatsApp Connector

### 4.1 Arquitetura do AcruxLab

**⚠️ SEGREDOS DESCOBERTOS:**

#### Segredo #1: Estrutura de 3 Camadas

```
LAYER 1: Connector (Canal)
    ↓
LAYER 2: Conversation (Thread)
    ↓
LAYER 3: Message (Mensagem individual)
```

**Por que isso importa?**
- Connector = Conta/Canal (ex: WhatsApp Business #1, SMS Kolmeya)
- Conversation = Cliente único em um canal (constraint: UNIQUE(number, connector_id))
- Message = Mensagens dentro de uma conversa

#### Segredo #2: Connector Types são Extensíveis

O campo `connector_type` não tem Selection fixa no modelo base!
Você pode adicionar novos tipos via `_inherit`:

```python
# No AcruxLab original:
connector_type = fields.Selection([
    ('chatapi', 'ChatAPI'),
    ('apichat', 'GupShup'),
    # ...
], string='Connector Type')

# Nossa extensão:
class AcruxChatConnector(models.Model):
    _inherit = 'acrux.chat.connector'

    connector_type = fields.Selection(
        selection_add=[('sms', 'SMS')],
        ondelete={'sms': 'cascade'}
    )
```

#### Segredo #3: Validação de Número via assert_id()

**Arquivo:** `whatsapp_connector/models/Connector.py:569`

```python
def assert_id(self, key):
    self.ensure_one()
    if not self.env.context.get('from_webhook'):
        if key != self.clean_id(key):
            raise ValidationError(_('Invalid number'))
        phone_format(key, formatted=False)  # to check
```

**Problema:** `phone_format()` é muito restrito para SMS.

**Solução:** Sobrescrever para `connector_type == 'sms'`.

#### Segredo #4: Métodos Auxiliares de Número

```python
# Connector.py
def clean_id(self, key):
    """Remove caracteres especiais"""
    return clean_number(key)  # Remove tudo exceto dígitos

def format_id(self, key):
    """Formata para exibição"""
    simple = '+%s' % clean_number(key)
    formatted = phone_format(key, formatted=True, raise_error=False)
    reverse = '+%s' % clean_number(formatted)
    return formatted if simple == reverse else simple
```

**Nossa adaptação:** Simplificamos para SMS retornar apenas `+5511999887766`.

#### Segredo #5: Conversation tem Unique Constraint

**Arquivo:** `whatsapp_connector/models/Conversation.py:99`

```python
@api.constrains('number', 'connector_id')
def _constrain_number(self):
    for r in self:
        r.connector_id.assert_id(r.number)
```

**Implicação:** Não pode ter 2 conversas com mesmo número no mesmo connector.

#### Segredo #6: Views são Herdadas Inteligentemente

O AcruxLab usa view inheritance:

```xml
<!-- Conversation Kanban -->
<record id="acrux_chat_conversation_view_kanban" model="ir.ui.view">
    <field name="name">acrux.chat.conversation.kanban</field>
    <field name="model">acrux.chat.conversation</field>
    <field name="arch" type="xml">
        <kanban>
            <!-- Kanban cards aqui -->
        </kanban>
    </field>
</record>
```

**Nossa estratégia:** Não criamos views novas, apenas extends quando necessário.

#### Segredo #7: Notificações via Bus

```python
# Conversation.py
def notify_message(self, message):
    """Notifica agentes via longpolling bus"""
    self.env['bus.bus'].sendone(
        f'acrux_chat_conversation_{self.id}',
        {'message_id': message.id}
    )
```

**Usado para:** Atualizar UI em tempo real quando SMS chega.

#### Segredo #8: Attachment Handling

```python
# Message.py
def ca_send_message(self, acrux_msg_ids):
    """Envia mensagens com attachments"""
    for msg in acrux_msg_ids:
        if msg.ttype == 'image':
            # Upload imagem para servidor WhatsApp
            # Depois envia URL
```

**Implicação para SMS:** SMS não suporta attachments nativamente.
Podemos enviar link encurtado ou ignorar.

---

## 5. Implementação Detalhada

### 5.1 Criação do Connector SMS via SQL

**Por que SQL ao invés de UI?**
- Connector não tem formulário de criação amigável
- Muitos campos obrigatórios (token, uuid, border_color, etc)
- SQL é mais rápido para setup inicial

**Script Completo:**

```sql
-- 1. Verificar se provider Kolmeya existe
SELECT id, name, provider_type FROM sms_provider WHERE provider_type = 'kolmeya';
-- Retorna: id=1, name='Kolmeya'

-- 2. Verificar campos obrigatórios da tabela
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'acrux_chat_connector'
  AND is_nullable = 'NO'
  AND column_default IS NULL
ORDER BY ordinal_position;

-- Resultado:
-- name, sequence, connector_type, company_id, source, odoo_url,
-- endpoint, token, uuid, border_color, desk_notify, assing_type

-- 3. Buscar valores de referência de connector existente
SELECT
    border_color,      -- '#0D15E7'
    desk_notify,       -- 'mines'
    assing_type,       -- 'connector'
    odoo_url,          -- 'https://odoo.semprereal.com'
    company_id         -- 1
FROM acrux_chat_connector
WHERE connector_type = 'whatsapp'
LIMIT 1;

-- 4. Gerar UUIDs (executar no terminal local)
-- python3 -c "import uuid; print(uuid.uuid4())"  # Token
-- python3 -c "import random; print(random.randint(100000, 999999))"  # UUID numérico

-- 5. Criar connector SMS
INSERT INTO acrux_chat_connector (
    name,
    connector_type,
    sms_provider_id,
    token,
    uuid,
    border_color,
    desk_notify,
    assing_type,
    sequence,
    company_id,
    source,
    endpoint,
    odoo_url,
    create_date,
    write_date,
    create_uid,
    write_uid
) VALUES (
    'SMS Kolmeya',                              -- Nome
    'sms',                                      -- Tipo
    1,                                          -- Provider ID
    '33860850-e93b-4ce6-9756-778b92def7fd',    -- Token UUID
    '595911',                                   -- UUID numérico
    '#00C853',                                  -- Verde (Material Design)
    'mines',                                    -- Notificar apenas minhas conversas
    'connector',                                -- Atribuição por connector
    100,                                        -- Sequência
    1,                                          -- SEMPRE REAL company
    '/',                                        -- Source padrão
    'https://kolmeya.com.br/api/v1',           -- Endpoint API
    'https://odoo.semprereal.com',             -- URL do Odoo
    NOW(),
    NOW(),
    2,                                          -- Admin user
    2
) RETURNING id, name, connector_type, token, uuid, sms_provider_id;

-- Retorno:
-- id=96, name='SMS Kolmeya', connector_type='sms',
-- token='33860850...', uuid='595911', sms_provider_id=1
```

**Valores Importantes:**

| Campo | Valor | Por quê? |
|-------|-------|----------|
| `connector_type` | `'sms'` | Identifica tipo de canal |
| `token` | UUID v4 | Usado para autenticar webhook |
| `uuid` | Numérico 6 dígitos | ID curto para URLs |
| `border_color` | `'#00C853'` | Verde Material Design - identifica SMS visualmente |
| `desk_notify` | `'mines'` | Notifica apenas conversas atribuídas ao agente |
| `assing_type` | `'connector'` | Atribuição automática por connector |
| `sms_provider_id` | `1` | FK para `sms_provider` (Kolmeya) |

---

### 5.2 Teste de Criação de Conversa SMS

**Script Python:** `/tmp/test_sms_chatroom_v2.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Contact Center SMS Integration
"""

import sys
import os

# Add Odoo to Python path
sys.path.insert(0, '/odoo/odoo-server')
sys.path.insert(0, '/odoo/custom/addons_custom')

import odoo
from odoo import api, SUPERUSER_ID

# Initialize Odoo environment
odoo.tools.config.parse_config([
    '-c', '/etc/odoo-server.conf',
    '--database', 'realcred'
])

registry = odoo.registry('realcred')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    print("="*60)
    print("📱 TESTE: Contact Center SMS Integration")
    print("="*60)

    # 1. Verificar connector SMS
    connector = env['acrux.chat.connector'].search([
        ('connector_type', '=', 'sms'),
        ('name', '=', 'SMS Kolmeya')
    ])

    print(f"\n✅ Connector: {connector.name} (ID: {connector.id})")

    # 2. Criar parceiro de teste
    partner = env['res.partner'].create({
        'name': 'Cliente Teste SMS',
        'phone': '+5511999887766',
    })

    print(f"✅ Parceiro: {partner.name} (ID: {partner.id})")

    # 3. Criar conversa no ChatRoom
    conversation = env['acrux.chat.conversation'].create({
        'name': partner.name,
        'number': '+5511999887766',           # ← Campo obrigatório!
        'number_format': '+5511999887766',
        'connector_id': connector.id,
        'res_partner_id': partner.id,
        'channel_type': 'sms',                # ← Nosso campo custom
    })

    print(f"✅ Conversa: ID {conversation.id}")

    # 4. Criar mensagem inicial
    message = env['acrux.chat.message'].create({
        'contact_id': conversation.id,
        'text': 'Olá! Mensagem de teste SMS.',
        'ttype': 'text',
        'from_me': True,
    })

    print(f"✅ Mensagem: ID {message.id}")

    # Commit
    cr.commit()

    print("\n" + "="*60)
    print("✅ TESTE CONCLUÍDO!")
    print("="*60)
    print(f"\n🌐 ChatRoom: https://odoo.semprereal.com/web#action=126&model=acrux.chat.conversation")
    print(f"📱 Conversa: https://odoo.semprereal.com/web#id={conversation.id}&model=acrux.chat.conversation&view_type=form")
```

**Como Executar:**

```bash
ssh odoo-rc "cd /odoo/odoo-server && sudo -u odoo python3 /tmp/test_sms_chatroom_v2.py"
```

**Saída Esperada:**

```
============================================================
📱 TESTE: Contact Center SMS Integration
============================================================

✅ Connector: SMS Kolmeya (ID: 96)
✅ Parceiro: Cliente Teste SMS (ID: 324051)
✅ Conversa: ID 66452
✅ Mensagem: ID 696666723

============================================================
✅ TESTE CONCLUÍDO!
============================================================

🌐 ChatRoom: https://odoo.semprereal.com/web#action=126...
📱 Conversa: https://odoo.semprereal.com/web#id=66452...
```

---

## 6. Problemas Encontrados e Soluções

### Problema 1: ValidationError: 'Invalid number'

**Erro Completo:**
```python
odoo.exceptions.ValidationError: Número invalido
File "Connector.py", line 569, in assert_id
    raise ValidationError(_('Invalid number'))
```

**Causa Raiz:**
- `assert_id()` do AcruxLab chama `phone_format()` do módulo WhatsApp
- `phone_format()` valida se número é WhatsApp válido
- SMS aceita números mais flexíveis

**Tentativas Falhadas:**
1. ❌ Importar `from odoo.tools import phone_format` - Não existe em Odoo 15
2. ❌ Importar `from odoo.tools.phone_validation import phone_format` - Módulo não existe
3. ❌ Usar `from ..tools import phone_format` - Funciona só dentro do whatsapp_connector

**Solução Final:**
```python
# contact_center_sms/models/connector.py
def assert_id(self, key):
    self.ensure_one()

    if self.connector_type == 'sms':
        # Validação flexível: apenas verifica se tem dígitos
        if key and any(c.isdigit() for c in str(key)):
            return True
        else:
            return super(AcruxChatConnector, self).assert_id(key)

    return super(AcruxChatConnector, self).assert_id(key)
```

**Lição:** Não tente usar funções internas do módulo base. Reimplemente com lógica própria.

---

### Problema 2: NOT NULL constraint violation - campo 'number'

**Erro Completo:**
```
psycopg2.errors.NotNullViolation: null value in column "number" violates not-null constraint
DETAIL: Failing row contains (..., null, +5511999887766, ...)
```

**Causa Raiz:**
- Usamos `number_format` mas esquecemos `number`
- Ambos são campos no modelo, mas `number` é NOT NULL no banco

**Código Quebrado:**
```python
conversation = env['acrux.chat.conversation'].create({
    'number_format': '+5511999887766',  # ← Não é suficiente!
    'connector_id': connector.id,
    # ...
})
```

**Solução:**
```python
conversation = env['acrux.chat.conversation'].create({
    'number': '+5511999887766',         # ← Campo obrigatório!
    'number_format': '+5511999887766',  # ← Formatado para exibição
    'connector_id': connector.id,
    # ...
})
```

**Lição:** Sempre verificar constraints do banco com:
```sql
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'nome_tabela' AND is_nullable = 'NO';
```

---

### Problema 3: ImportError - phone_format não encontrado

**Erro Completo:**
```python
ImportError: cannot import name 'phone_format' from 'odoo.tools'
ModuleNotFoundError: No module named 'odoo.tools.phone_validation'
```

**Tentativas:**
```python
# ❌ Tentativa 1
from odoo.tools import phone_format

# ❌ Tentativa 2
from odoo.tools.phone_validation import phone_format

# ❌ Tentativa 3
from odoo.addons.phone_validation.tools import phone_format
```

**Descoberta:**
```bash
# Procurar onde phone_format está definido
$ grep -r "def phone_format" /odoo/

# Resultado: NADA!
# phone_format() é função do whatsapp_connector, não do Odoo core
```

**Localização Real:**
```python
# whatsapp_connector/tools/__init__.py
from .common import phone_format, clean_number
```

**Solução:** Não usar `phone_format()`. Validar com regex simples:
```python
if key and any(c.isdigit() for c in str(key)):
    return True  # Válido se tem dígitos
```

**Lição:** Funções de módulos externos não são acessíveis globalmente. Use lógica própria.

---

### Problema 4: Ícone do módulo não aparece no Apps

**Sintomas:**
- Ícone quebrado (placeholder cinza) no painel de Apps
- Erro no console: `data:image/png;base64,false`

**Verificações:**
```bash
# 1. Arquivo existe?
ls -lh /odoo/custom/addons_custom/contact_center_sms/static/description/icon.png
# ✅ -rw-r--r-- 1 odoo odoo 1.6K icon.png

# 2. Arquivo é PNG válido?
file /odoo/custom/addons_custom/contact_center_sms/static/description/icon.png
# ✅ PNG image data, 128 x 128

# 3. Acessível via URL?
curl -I https://odoo.semprereal.com/contact_center_sms/static/description/icon.png
# ✅ HTTP/1.1 200 OK
```

**Causa Raiz:**
Faltavam 2 configurações no `__manifest__.py`:

```python
# ❌ ANTES (ícone não aparece)
{
    'name': 'Contact Center SMS',
    'installable': True,
    'application': False,  # ← Problema 1
    # 'images' não definido  # ← Problema 2
}

# ✅ DEPOIS (ícone aparece)
{
    'name': 'Contact Center SMS',
    'installable': True,
    'application': True,              # ← Marca como "Application"
    'images': ['static/description/icon.png'],  # ← Declara ícone
}
```

**Lição:** Para ícone aparecer no Apps:
1. `'application': True` (marca como app independente)
2. `'images': ['static/description/icon.png']`
3. Arquivo PNG 128x128px em `static/description/`

---

### Problema 5: Menu sem ícone (data:image/png;base64,false)

**Erro Console:**
```
GET data:image/png;base64,false 404 (Not Found)
```

**Causa:** Menuitem sem atributo `web_icon`.

**Código Quebrado:**
```xml
<menuitem id="menu_sms_root"
          name="SMS"
          sequence="100"/>
<!-- Sem web_icon! -->
```

**Solução:**
```xml
<menuitem id="menu_sms_root"
          name="SMS"
          sequence="100"
          web_icon="sms_base_sr,static/description/icon.png"/>
<!--     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
         Formato: module_name,caminho/para/icon.png -->
```

**Lição:** Menu raiz precisa de `web_icon` no formato `module,path`.

---

### Problema 6: Odoo não reinicia após criar connector.py

**Sintomas:**
```bash
sudo systemctl restart odoo-server
sleep 10
ps aux | grep odoo-bin | wc -l
# Retorna: 0 (nenhum processo!)
```

**Causa:** Erro de sintaxe ou import no `connector.py`.

**Debug:**
```bash
# 1. Testar sintaxe Python
python3 -m py_compile /path/to/connector.py
# ✅ Sem erros

# 2. Tentar iniciar Odoo manualmente
cd /odoo/odoo-server
sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d realcred

# Erro:
# ImportError: cannot import name 'phone_format' from 'odoo.tools'
```

**Solução:** Corrigir imports no connector.py (veja Problema 3).

**Lição:** Sempre testar Odoo manualmente após mudanças em models.

---

### Problema 7: Python code não recarrega (cache)

**Sintomas:**
- Edito `conversation.py`
- Reinicio Odoo
- Erro persiste com código antigo

**Causa:** Arquivos `.pyc` em `__pycache__` não são limpos.

**Solução:**
```bash
# Limpar todos os .pyc e __pycache__
find /odoo/custom/addons_custom/contact_center_sms -name '*.pyc' -delete
find /odoo/custom/addons_custom/contact_center_sms -type d -name '__pycache__' -exec rm -rf {} +

# Reiniciar
sudo systemctl restart odoo-server
```

**Lição:** Sempre limpar cache antes de testar mudanças em Python.

---

### Problema 8: Campo 'phone_number' inválido em sms.message

**Erro:**
```python
ValueError: Invalid field 'phone_number' on model 'sms.message'
```

**Causa:** Nome de campo errado. Modelo usa `phone`, não `phone_number`.

**Debug:**
```sql
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'sms_message'
  AND column_name LIKE '%phone%';

-- Resultado: phone (não phone_number!)
```

**Solução:**
```python
# ❌ Errado
sms = env['sms.message'].create({
    'phone_number': '+5511999887766',  # Campo não existe!
})

# ✅ Correto
sms = env['sms.message'].create({
    'phone': '+5511999887766',  # Campo correto
})
```

**Lição:** Sempre verificar nomes de campos no banco ou no modelo Python.

---

## 7. Lições Aprendidas

### 7.1 Arquitetura

✅ **DO:**
- Estudar modelos base antes de estender (AcruxLab é complexo)
- Usar herança de modelos (`_inherit`) ao invés de duplicar
- Testar campos obrigatórios via SQL antes de criar registros
- Manter lógica de negócio nos models, não nos controllers

❌ **DON'T:**
- Criar modelos paralelos (ex: `sms.conversation` separado de `acrux.chat.conversation`)
- Ignorar constraints do banco (UNIQUE, NOT NULL)
- Assumir que funções de um módulo externo estão disponíveis globalmente

### 7.2 Desenvolvimento Odoo

✅ **DO:**
- Sempre ler arquivo existente antes de usar `Edit` ou `Write`
- Usar `@api.model` para métodos de classe (ex: `create_from_webhook`)
- Usar `@api.depends()` para campos computados
- Testar sintaxe Python com `python3 -m py_compile`
- Limpar cache (`__pycache__`) após cada mudança

❌ **DON'T:**
- Editar arquivos sem ler primeiro (tool error)
- Esquecer de adicionar novos arquivos em `__init__.py`
- Usar `self` em métodos `@api.model` (use `cls` ou não use)
- Confiar que reiniciar Odoo recarrega tudo (precisa limpar cache)

### 7.3 Debugging

✅ **DO:**
- Verificar logs: `sudo tail -f /var/log/odoo/odoo-server.log`
- Iniciar Odoo manualmente para ver erros: `sudo -u odoo python3 odoo-bin ...`
- Usar `_logger.info()` para debug
- Testar SQL queries diretamente no psql

❌ **DON'T:**
- Assumir que "sem erro no log = está funcionando"
- Ignorar warnings (muitas vezes indicam problemas reais)
- Editar banco de dados diretamente sem transaction (use `BEGIN; ... ROLLBACK;` para testar)

### 7.4 Integração com APIs Externas

✅ **DO:**
- Criar wrapper class (ex: `KolmeyaAPI`) ao invés de requests inline
- Usar `requests.Session()` para reutilizar conexão
- Sempre usar `timeout` em requests HTTP
- Logar requests e responses para debug
- Tratar exceções de rede gracefully

❌ **DON'T:**
- Fazer chamadas síncronas em métodos `create()` (pode travar UI)
- Armazenar API keys em código (usar `ir.config_parameter`)
- Ignorar rate limits da API

### 7.5 Webhooks

✅ **DO:**
- Validar token antes de processar payload
- Usar `auth='public'` e `csrf=False` em route
- Logar todos os webhooks recebidos
- Retornar status 200 mesmo em erro (ou provider reenvia infinitamente)
- Usar `sudo()` para criar registros (webhook não tem user context)

❌ **DON'T:**
- Confiar em payload sem validação
- Fazer processamento pesado em webhook (use job queue)
- Retornar erro 500 (provider vai reenviar)

### 7.6 SQL no Odoo

✅ **DO:**
- Usar ORM sempre que possível
- SQL raw apenas para consultas complexas ou setup inicial
- Sempre usar `RETURNING` para verificar resultado de INSERT
- Fazer backup antes de UPDATE/DELETE

❌ **DON'T:**
- Fazer INSERT sem verificar campos obrigatórios
- Usar SQL para lógica de negócio (coloque em Python)
- Esquecer de fazer `cr.commit()` em scripts externos

---

## 8. Como Recriar do Zero

### 8.1 Pré-requisitos

```bash
# Sistema
- Ubuntu 20.04 LTS
- Odoo 15.0 instalado
- PostgreSQL 12+
- Python 3.8+
- Git

# Módulos Odoo
- base (core)
- mail (core)
- contacts (core)
- whatsapp_connector (AcruxLab - comprado ou open source version)
```

### 8.2 Passo 1: Criar Módulo Base SMS

```bash
# 1. Criar estrutura
mkdir -p ~/odoo_modules/sms_base_sr/{models,views,security,static/description}
cd ~/odoo_modules/sms_base_sr

# 2. Criar __init__.py
cat > __init__.py << 'EOF'
# -*- coding: utf-8 -*-
from . import models
EOF

# 3. Criar __manifest__.py
cat > __manifest__.py << 'EOF'
{
    'name': 'SMS Base',
    'version': '15.0.1.0.0',
    'category': 'Marketing/SMS',
    'summary': 'Core SMS Management',
    'author': 'Seu Nome',
    'depends': ['base', 'mail', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/sms_message_views.xml',
        'views/sms_provider_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
EOF

# 4. Criar models/__init__.py
mkdir models
cat > models/__init__.py << 'EOF'
# -*- coding: utf-8 -*-
from . import sms_provider
from . import sms_message
EOF

# 5. Copiar arquivos desta documentação:
# - sms_provider.py
# - sms_message.py
# - sms_message_views.xml
# - ir.model.access.csv

# 6. Baixar ícone (128x128 PNG)
wget -O static/description/icon.png https://img.icons8.com/color/128/sms.png
```

### 8.2 Passo 2: Criar Módulo Kolmeya

```bash
# 1. Criar estrutura
mkdir -p ~/odoo_modules/sms_kolmeya/{models,views}
cd ~/odoo_modules/sms_kolmeya

# 2. Criar arquivos base
cat > __init__.py << 'EOF'
# -*- coding: utf-8 -*-
from . import models
EOF

cat > __manifest__.py << 'EOF'
{
    'name': 'SMS Kolmeya Provider',
    'version': '15.0.1.0.0',
    'depends': ['sms_base_sr'],
    'installable': True,
}
EOF

# 3. Criar models
mkdir models
cat > models/__init__.py << 'EOF'
from . import kolmeya_api
from . import kolmeya_provider
EOF

# 4. Copiar desta documentação:
# - kolmeya_api.py
# - kolmeya_provider.py
```

### 8.3 Passo 3: Criar Módulo Contact Center

```bash
# 1. Criar estrutura
mkdir -p ~/odoo_modules/contact_center_sms/{models,controllers,security,static/description}
cd ~/odoo_modules/contact_center_sms

# 2. Arquivos base
cat > __init__.py << 'EOF'
# -*- coding: utf-8 -*-
from . import models
from . import controllers
EOF

cat > __manifest__.py << 'EOF'
{
    'name': 'Contact Center SMS Integration',
    'version': '15.0.1.0.0',
    'depends': ['whatsapp_connector', 'sms_base_sr', 'sms_kolmeya'],
    'data': ['security/ir.model.access.csv'],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}
EOF

# 3. Models
mkdir models
cat > models/__init__.py << 'EOF'
from . import connector
from . import conversation
from . import message
EOF

# Copiar desta doc:
# - connector.py
# - conversation.py
# - message.py

# 4. Controllers
mkdir controllers
cat > controllers/__init__.py << 'EOF'
from . import webhook
EOF

# Copiar webhook.py desta doc

# 5. Ícone
wget -O static/description/icon.png https://img.icons8.com/color/128/chat.png
```

### 8.4 Passo 4: Instalar Módulos

```bash
# 1. Copiar para addons_path
sudo cp -r ~/odoo_modules/* /odoo/custom/addons_custom/
sudo chown -R odoo:odoo /odoo/custom/addons_custom/

# 2. Reiniciar Odoo
sudo systemctl restart odoo-server

# 3. Atualizar lista de apps (via UI ou comando)
# UI: Apps > Update Apps List
# OU
cd /odoo/odoo-server
sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d sua_database --stop-after-init --update-apps-list

# 4. Instalar módulos em ordem:
# a) sms_base_sr
# b) sms_kolmeya
# c) contact_center_sms
```

### 8.5 Passo 5: Configurar Provider Kolmeya

**Via UI:**
1. Apps > SMS > Providers
2. Create:
   - Name: Kolmeya
   - Provider Type: kolmeya
   - API URL: https://kolmeya.com.br/api/v1
   - API Key: (seu token)
   - Segment ID: (seu segmento)

**Via SQL:**
```sql
INSERT INTO sms_provider (name, provider_type, api_url, api_key, segment_id, active, create_uid, write_uid, create_date, write_date)
VALUES ('Kolmeya', 'kolmeya', 'https://kolmeya.com.br/api/v1', 'SEU_API_KEY', 'SEU_SEGMENT', true, 2, 2, NOW(), NOW())
RETURNING id;
```

### 8.6 Passo 6: Criar Connector SMS

```bash
# Gerar UUIDs
TOKEN=$(python3 -c "import uuid; print(uuid.uuid4())")
UUID_NUM=$(python3 -c "import random; print(random.randint(100000, 999999))")

# Conectar ao banco
ssh seu-servidor "sudo -u postgres psql sua_database"
```

```sql
-- Buscar company_id
SELECT id, name FROM res_company LIMIT 1;

-- Buscar provider_id
SELECT id, name FROM sms_provider WHERE provider_type = 'kolmeya';

-- Criar connector (substitua valores)
INSERT INTO acrux_chat_connector (
    name, connector_type, sms_provider_id, token, uuid,
    border_color, desk_notify, assing_type, sequence,
    company_id, source, endpoint, odoo_url,
    create_date, write_date, create_uid, write_uid
) VALUES (
    'SMS Kolmeya',
    'sms',
    1,  -- ← ID do provider
    'SEU_TOKEN_UUID',
    'SEU_UUID_NUMERICO',
    '#00C853',
    'mines',
    'connector',
    100,
    1,  -- ← ID da company
    '/',
    'https://kolmeya.com.br/api/v1',
    'https://seu-odoo.com',
    NOW(), NOW(), 2, 2
) RETURNING id, name, token;
```

### 8.7 Passo 7: Testar

```bash
# 1. Criar script de teste (copiar deste doc)
nano /tmp/test_sms.py

# 2. Executar
cd /odoo/odoo-server
sudo -u odoo python3 /tmp/test_sms.py

# 3. Verificar no ChatRoom
# Abrir: https://seu-odoo.com/web#action=126&model=acrux.chat.conversation
```

### 8.8 Passo 8: Configurar Webhook (Opcional)

**No Kolmeya:**
```bash
# Se Kolmeya tiver painel web, configurar:
# Webhook URL: https://seu-odoo.com/contact_center_sms/webhook/SEU_TOKEN

# Se não tiver, webhook será configurado por mensagem (no send_sms)
```

**Testar Webhook:**
```bash
# Enviar POST manual
curl -X POST \
  https://seu-odoo.com/contact_center_sms/webhook/SEU_TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "sms_received",
    "phone": "5511999887766",
    "message": "Teste de webhook",
    "timestamp": "2025-11-16 10:00:00"
  }'

# Verificar se conversa foi criada no ChatRoom
```

---

## 9. Testes e Validação

### 9.1 Checklist de Testes

#### Módulos Instalados
- [ ] `sms_base_sr` instalado e sem erros
- [ ] `sms_kolmeya` instalado
- [ ] `contact_center_sms` instalado
- [ ] Ícones aparecendo no painel Apps

#### Provider Kolmeya
- [ ] Provider criado com API key válida
- [ ] Teste de conexão bem-sucedido
- [ ] Saldo de créditos visível

#### Connector SMS
- [ ] Connector criado via SQL
- [ ] `connector_type = 'sms'`
- [ ] `sms_provider_id` ligado ao Kolmeya
- [ ] Token único gerado

#### Conversas SMS
- [ ] Conversa criada manualmente via script
- [ ] Aparece no ChatRoom Kanban
- [ ] Campo `channel_type = 'sms'`
- [ ] Cor do card diferente (border_color verde)

#### Mensagens SMS
- [ ] Mensagem criada na conversa
- [ ] Aparece na thread do ChatRoom
- [ ] `from_me` correto (True/False)

#### Envio de SMS (Futuro)
- [ ] Enviar SMS via ChatRoom UI
- [ ] SMS registrado em `sms.message`
- [ ] `state` atualizado para 'sent'
- [ ] `external_id` (job_id) salvo

#### Recebimento via Webhook (Futuro)
- [ ] Webhook responde 200 OK
- [ ] SMS recebido cria `sms.message`
- [ ] Conversa criada/atualizada
- [ ] Mensagem aparece no ChatRoom
- [ ] Notificação para agente

---

### 9.2 Queries SQL Úteis

**Listar todos os connectors:**
```sql
SELECT id, name, connector_type, uuid, sms_provider_id
FROM acrux_chat_connector
ORDER BY id DESC;
```

**Listar conversas SMS:**
```sql
SELECT
    c.id,
    c.name,
    c.number_format,
    c.channel_type,
    c.status,
    conn.name as connector_name
FROM acrux_chat_conversation c
JOIN acrux_chat_connector conn ON c.connector_id = conn.id
WHERE c.channel_type = 'sms'
ORDER BY c.create_date DESC
LIMIT 20;
```

**Listar mensagens de uma conversa:**
```sql
SELECT
    m.id,
    m.text,
    m.from_me,
    m.ttype,
    m.date_message,
    c.name as conversation_name
FROM acrux_chat_message m
JOIN acrux_chat_conversation c ON m.contact_id = c.id
WHERE c.id = 66452  -- ← ID da conversa
ORDER BY m.date_message DESC;
```

**Listar SMS enviados:**
```sql
SELECT
    id,
    phone,
    body,
    state,
    direction,
    external_id,
    date_sent
FROM sms_message
WHERE direction = 'outgoing'
ORDER BY create_date DESC
LIMIT 20;
```

**Contar conversas por canal:**
```sql
SELECT
    channel_type,
    COUNT(*) as total
FROM acrux_chat_conversation
GROUP BY channel_type;
```

---

## 10. Manutenção e Troubleshooting

### 10.1 Logs Importantes

**Odoo Server Log:**
```bash
# Tempo real
sudo tail -f /var/log/odoo/odoo-server.log

# Erros recentes
sudo tail -200 /var/log/odoo/odoo-server.log | grep -i error

# Buscar por módulo específico
sudo grep -i "contact_center_sms" /var/log/odoo/odoo-server.log | tail -50
```

**PostgreSQL Log:**
```bash
# Queries lentas
sudo tail -f /var/log/postgresql/postgresql-12-main.log

# Deadlocks
sudo grep -i "deadlock" /var/log/postgresql/postgresql-12-main.log
```

**Nginx/Apache (se usar proxy):**
```bash
# Access log
sudo tail -f /var/log/nginx/access.log | grep webhook

# Error log
sudo tail -f /var/log/nginx/error.log
```

---

### 10.2 Comandos de Diagnóstico

**Verificar se Odoo está rodando:**
```bash
ps aux | grep odoo-bin | grep -v grep
# Deve mostrar ~19 workers

sudo systemctl status odoo-server
# Deve estar: active (running)
```

**Verificar módulos instalados:**
```bash
ssh servidor "echo \"SELECT name, state, latest_version FROM ir_module_module WHERE name LIKE '%sms%';\" | sudo -u postgres psql database"
```

**Verificar permissões de arquivos:**
```bash
ls -la /odoo/custom/addons_custom/contact_center_sms/
# Todos devem ser: odoo:odoo
```

**Verificar cache Python:**
```bash
find /odoo/custom/addons_custom/contact_center_sms -name '__pycache__' -type d
# Se retornar algo, limpar:
sudo find /odoo/custom/addons_custom/contact_center_sms -name '*.pyc' -delete
sudo find /odoo/custom/addons_custom/contact_center_sms -type d -name '__pycache__' -exec rm -rf {} +
```

---

### 10.3 Problemas Comuns

#### "Module not found" após instalação

**Sintomas:**
```
Module contact_center_sms not found in addons_path
```

**Soluções:**
1. Verificar se está em `addons_path` do config:
```bash
grep addons_path /etc/odoo-server.conf
# Deve incluir: /odoo/custom/addons_custom
```

2. Atualizar lista de apps:
```bash
cd /odoo/odoo-server
sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d database --stop-after-init --update-apps-list
```

3. Verificar permissões:
```bash
ls -la /odoo/custom/addons_custom/ | grep contact_center_sms
# Deve ser: drwxr-xr-x odoo odoo
```

---

#### Conversa não aparece no Kanban

**Verificar:**
1. Campo `status` está correto:
```sql
UPDATE acrux_chat_conversation SET status = 'new' WHERE id = 66452;
```

2. Filtro do Kanban:
- Remover filtros personalizados
- Verificar campo `active`:
```sql
UPDATE acrux_chat_conversation SET active = true WHERE id = 66452;
```

---

#### SMS não envia (fica em 'draft')

**Debug:**
```python
# No shell do Odoo
sms = env['sms.message'].browse(ID)
result = sms.send_sms()
print(result)
```

**Verificar:**
- [ ] Provider está `active = true`
- [ ] API Key válida
- [ ] Saldo de créditos suficiente
- [ ] Número de telefone válido (com código do país)

---

#### Webhook retorna 404

**Verificar:**
1. URL correta:
```
https://odoo.semprereal.com/contact_center_sms/webhook/SEU_TOKEN
```

2. Controller registrado:
```bash
grep -r "contact_center_sms/webhook" /odoo/custom/addons_custom/contact_center_sms/
```

3. Odoo recarregado após instalar módulo

4. Nginx não está bloqueando:
```bash
sudo tail /var/log/nginx/error.log | grep webhook
```

---

## 11. Referências e Recursos

### 11.1 Documentação Oficial

- **Odoo 15 Documentation:** https://www.odoo.com/documentation/15.0/
- **Odoo Developer Documentation:** https://www.odoo.com/documentation/15.0/developer.html
- **PostgreSQL 12 Documentation:** https://www.postgresql.org/docs/12/

### 11.2 APIs Externas

- **Kolmeya SMS API:** https://kolmeya.com.br/docs/api
- **AcruxLab WhatsApp Connector:** (documentação proprietária)

### 11.3 Ferramentas Úteis

- **Postman:** Para testar webhooks e APIs
- **DBeaver:** Para explorar banco PostgreSQL
- **VS Code:** Editor com extensões Python/Odoo
- **Git:** Versionamento de código

### 11.4 Comunidade

- **Odoo Community Forum:** https://www.odoo.com/forum
- **Stack Overflow [odoo]:** https://stackoverflow.com/questions/tagged/odoo
- **GitHub Odoo:** https://github.com/odoo/odoo

---

## 12. Conclusão

Este documento contém **TODOS** os segredos para recriar a integração Contact Center SMS com WhatsApp ChatRoom do zero.

**Principais conquistas:**
✅ 3 módulos criados (sms_base_sr, sms_kolmeya, contact_center_sms)
✅ Connector SMS funcionando (ID: 96)
✅ Conversas SMS aparecendo no ChatRoom
✅ Validação customizada de números
✅ Arquitetura extensível para outros canais

**Próximos passos sugeridos:**
1. Testar envio real de SMS via Kolmeya
2. Implementar recebimento via webhook
3. Adicionar suporte a mídia (links, imagens via URL)
4. Criar dashboard de métricas (SMS enviados, taxa de resposta)
5. Implementar templates de SMS rápidos
6. Adicionar suporte a SMS em massa
7. Integrar com outros providers (Twilio, Nexmo)

**Tempo estimado para recriar:**
- Desenvolvedor experiente em Odoo: **2-3 dias**
- Desenvolvedor intermediário: **1 semana**
- Desenvolvedor iniciante: **2-3 semanas**

---

**Documentação criada em:** 2025-11-16
**Última atualização:** 2025-11-16
**Versão:** 1.0.0
**Status:** ✅ Produção

---

## Apêndice A: Estrutura Completa de Arquivos

```
odoo_15_sr/
├── sms_base_sr/
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── sms_provider.py
│   │   ├── sms_message.py
│   │   ├── sms_template.py
│   │   └── res_partner.py
│   ├── views/
│   │   ├── sms_message_views.xml
│   │   ├── sms_provider_views.xml
│   │   ├── sms_template_views.xml
│   │   └── sms_menu.xml
│   ├── security/
│   │   ├── sms_security.xml
│   │   └── ir.model.access.csv
│   └── static/
│       └── description/
│           └── icon.png
│
├── sms_kolmeya/
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── kolmeya_api.py
│   │   └── kolmeya_provider.py
│   └── views/
│       └── kolmeya_provider_views.xml
│
└── contact_center_sms/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   ├── connector.py
    │   ├── conversation.py
    │   ├── message.py
    │   └── connector_sms.py
    ├── controllers/
    │   ├── __init__.py
    │   └── webhook.py
    ├── security/
    │   └── ir.model.access.csv
    └── static/
        └── description/
            └── icon.png
```

---

## Apêndice B: Comandos Rápidos (Cheat Sheet)

```bash
# === DESENVOLVIMENTO ===

# Reiniciar Odoo
sudo systemctl restart odoo-server

# Limpar cache Python
find /odoo/custom/addons_custom/MODULO -name '*.pyc' -delete
find /odoo/custom/addons_custom/MODULO -type d -name '__pycache__' -exec rm -rf {} +

# Atualizar módulo
cd /odoo/odoo-server
sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d DATABASE --stop-after-init -u MODULO

# Ver logs em tempo real
sudo tail -f /var/log/odoo/odoo-server.log

# === DATABASE ===

# Conectar PostgreSQL
sudo -u postgres psql DATABASE

# Backup
sudo -u postgres pg_dump DATABASE > backup_$(date +%Y%m%d).sql

# Restore
sudo -u postgres psql DATABASE < backup.sql

# === TESTES ===

# Testar sintaxe Python
python3 -m py_compile arquivo.py

# Verificar Odoo rodando
ps aux | grep odoo-bin | wc -l

# Testar webhook
curl -X POST https://odoo.com/contact_center_sms/webhook/TOKEN \
  -H 'Content-Type: application/json' \
  -d '{"type":"sms_received","phone":"5511999887766","message":"Teste"}'

# === MONITORING ===

# Processos Odoo
ps aux | grep odoo

# Uso de memória
free -h

# Disco
df -h

# Conexões PostgreSQL
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname='DATABASE';"
```

---

**FIM DA DOCUMENTAÇÃO**

Para dúvidas ou atualizações, consultar:
- Este arquivo: `DOCUMENTACAO_CONTACT_CENTER_SMS.md`
- Logs do servidor: `/var/log/odoo/odoo-server.log`
- Código fonte: `/odoo/custom/addons_custom/contact_center_sms/`
