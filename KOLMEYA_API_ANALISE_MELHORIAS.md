# 📚 DOCUMENTAÇÃO COMPLETA API KOLMEYA + MELHORIAS PROPOSTAS
## Sistema: Odoo 15 - Realcred - Integração SMS
## Data: 16/11/2025

---

## 🎯 OBJETIVO

Documentar TODAS as funcionalidades da API Kolmeya disponíveis e propor melhorias para nossa integração SMS no Odoo 15.

---

# PARTE 1: DOCUMENTAÇÃO COMPLETA DA API KOLMEYA

## 📡 1. WEBHOOKS

### 1.1. Webhook para Requisições via API

**Configuração:** Passar parâmetro `webhook_url` no envio do SMS (`/v1/sms/store`)

#### Tipos de Eventos Enviados ao Webhook:

##### A. Atualizações de Status
```json
{
  "id": "uuid-string",
  "reference": "string | null",
  "messages": [
    {
      "id": "message-uuid",
      "reference": "string | null",
      "status_code": 3,
      "status": "entregue"
    }
  ]
}
```

**Status Codes:**
- `3` = entregue (delivered)
- `4` = não entregue (not delivered)
- `5` = rejeitado no broker (rejected by broker)
- `6` = expirada (expired)

##### B. Respostas de Clientes
```json
{
  "reply": {
    "id": "reply-uuid",
    "reply": "texto da resposta do cliente",
    "received_at": "16/11/2025 14:30:00",
    "message": {
      "id": "message-uuid",
      "reference": "ref-123",
      "phone": "5511999999999",
      "content": "mensagem original enviada"
    }
  }
}
```

##### C. Rejeições por Homologação
```json
{
  "id": "request-uuid",
  "reference": "string | null",
  "status": "rejected",
  "status_message": "Request rejected due to validation failure"
}
```

### 1.2. Webhook para Campanhas

**Status:** Documentação RESTRITA - requer autenticação na plataforma Kolmeya

---

## 📨 2. OPERAÇÕES DE ENVIO DE SMS

### 2.1. Envio Padrão - `/v1/sms/store`

**Método:** POST
**Autenticação:** Bearer Token

#### Parâmetros Obrigatórios:
```json
{
  "sms_api_id": 123,
  "messages": [
    {
      "phone": 5511999999999,
      "message": "Texto da mensagem",
      "reference": "opcional-ref-123"
    }
  ]
}
```

#### Parâmetros Opcionais:
```json
{
  "webhook_url": "https://seu-servidor.com/webhook",
  "tenant_segment_id": 456,
  "reference": "lote-2025-001"
}
```

**Limites:**
- Mínimo: 1 mensagem
- Máximo: 1.000 mensagens por requisição

**Validações Automáticas:**
- ✅ Verificação de "Não Perturbe" (São Paulo)
- ✅ Validação de números em blacklist
- ✅ Validação de formato de telefone

#### Resposta:
```json
{
  "id": "request-uuid",
  "reference": "lote-2025-001",
  "valids": [
    {
      "id": "msg-uuid-1",
      "phone": 5511999999999,
      "reference": "ref-123"
    }
  ],
  "invalids": [
    {
      "phone": 5511888888888,
      "message": "mensagem",
      "reference": "ref-124",
      "error": "número inválido"
    }
  ],
  "blacklist": [
    { "phone": 5511777777777 }
  ],
  "not_disturb": [
    { "phone": 5511666666666 }
  ]
}
```

### 2.2. Envio de Token de Autenticação - `/v1/sms/store-token`

**Método:** POST
**Autenticação:** Bearer Token

**Restrições ESPECÍFICAS:**
- ✅ Exatamente 1 mensagem por requisição
- ❌ PROIBIDO números 0800
- ❌ PROIBIDO links/URLs na mensagem
- ✅ BYPASS da verificação "Não Perturbe"

#### Exemplo:
```json
{
  "sms_api_id": 123,
  "messages": [
    {
      "phone": 5511999999999,
      "message": "Seu código de verificação: 123456"
    }
  ],
  "webhook_url": "https://opcional.com/webhook"
}
```

**Use Cases:**
- Autenticação 2FA
- Códigos de verificação
- OTPs (One-Time Passwords)
- Tokens de segurança

---

## 📊 3. RELATÓRIOS E CONSULTAS

### 3.1. Consulta de Saldo - `/v1/sms/balance`

**Método:** POST

**Resposta:**
```json
{
  "balance": "1500.50"
}
```

### 3.2. Status de Requisição - `/v1/sms/status/request`

**Método:** POST

**Parâmetros (usar APENAS UM):**
```json
{
  "id": "request-uuid"
}
// OU
{
  "reference": "minha-referencia-123"
}
```

**Resposta:**
```json
{
  "id": "request-uuid",
  "reference": "minha-referencia-123",
  "status": "delivered",
  "status_code": 3,
  "messages": [
    {
      "id": "msg-uuid",
      "reference": "ref-msg-1",
      "status": "entregue",
      "status_code": 3
    }
  ]
}
```

### 3.3. Status de Mensagem Individual - `/v1/sms/status/message`

Similar ao `/status/request` mas para mensagens específicas.

### 3.4. Relatório de Status (Período) - `/v1/sms/reports/statuses`

**Método:** POST

**Parâmetros:**
```json
{
  "start_at": "2025-11-01 00:00",
  "end_at": "2025-11-07 23:59",
  "limit": 30000
}
```

**Limites:**
- Período máximo: 7 dias
- Registros por consulta: até 30.000

**Resposta:**
```json
{
  "messages": [
    {
      "telefone": "5511999999999",
      "nome": "João Silva",
      "cpf": "12345678900",
      "mensagem": "Texto enviado",
      "status": "entregue",
      "enviada_em": "16/11/2025 14:30",
      "parametros": [],
      "lote": 123,
      "job": 456,
      "centro_custo": "Marketing",
      "api": "API Principal",
      "broker": "Broker 1",
      "produto": "SMS"
    }
  ]
}
```

### 3.5. Relatório de Jobs (últimos 7 dias) - `/v1/sms/reports/jobs`

**Método:** POST

**Resposta:**
```json
{
  "jobs": "string com informações dos jobs"
}
```

### 3.6. Status por Job - `/v1/sms/reports/statuses-by-job`

Consulta status de todas as mensagens de um job específico.

### 3.7. Resumo Mensal de Jobs - `/v1/sms/reports/quantity-jobs`

**Método:** POST

**Parâmetros:**
```json
{
  "period": "2025-11"
}
```

**Resposta inclui:**
- Produto, centro de custo, broker, API, canal
- Totais: arquivo, validações, entregas, respostas, acessos
- Timestamps de processamento

### 3.8. Registros Inválidos - `/v1/sms/reports/invalid-records`

Lista números rejeitados/inválidos de envios anteriores.

---

## 💬 4. RESPOSTAS DE CLIENTES

### 4.1. Respostas via API - `/v1/sms/replys`

**Método:** POST

**Parâmetros:**
```json
{
  "period": 48
}
```

**Limites:**
- Período máximo: 168 horas (7 dias)
- Período padrão: 24 horas

**Resposta (paginada):**
```json
{
  "current_page": 1,
  "data": [
    {
      "id": "reply-uuid",
      "reply": "Texto da resposta do cliente",
      "received_at": "16/11/2025 14:30:00",
      "message": {
        "id": "msg-uuid",
        "reference": "ref-123",
        "phone": 5511999999999
      },
      "request": {
        "id": "request-uuid",
        "reference": "lote-001"
      }
    }
  ],
  "first_page_url": "...",
  "last_page": 5,
  "total": 100,
  "per_page": 20,
  "from": 1,
  "to": 20,
  "prev_page_url": null,
  "next_page_url": "..."
}
```

### 4.2. Respostas via Web - `/v1/sms/replys-web`

Similar ao endpoint API, mas para campanhas criadas na interface web.

**Campos adicionais:**
```json
{
  "id": "reply-id",
  "job": 123,
  "phone": 5511999999999,
  "message": "mensagem original",
  "parameters": {},
  "send_at": "16/11/2025 10:00:00",
  "reply": "resposta do cliente",
  "received_at": "16/11/2025 14:30:00"
}
```

---

## 🚫 5. BLACKLIST

### 5.1. Adicionar à Blacklist - `/v1/blacklist/store`

**Método:** POST

**Parâmetros:**
```json
{
  "tenant_id": 123,
  "phones": [
    {
      "phone": 5511999999999,
      "document": "12345678900"
    },
    {
      "phone": 5511888888888
    }
  ]
}
```

**Limites:**
- Mínimo: 1 telefone
- Máximo: 1.000 telefones por requisição

**Campo `document` (opcional):**
- Se informado: bloqueia número APENAS para aquele CPF
- Se omitido: bloqueia número UNIVERSALMENTE

**Resposta:** HTTP 201 (Created)

### 5.2. Remover da Blacklist - `/v1/blacklist/destroy`

**Método:** POST

Mesmos parâmetros de `/blacklist/store`.

**Resposta:** HTTP 204 (No Content)

---

## 🎯 6. SEGMENTOS (CENTROS DE CUSTO)

### 6.1. Listar Segmentos - `/v1/sms/segments`

**Método:** POST

**Resposta:**
```json
{
  "segments": [
    {
      "id": 1,
      "name": "Corporativo"
    },
    {
      "id": 2,
      "name": "Marketing"
    },
    {
      "id": 3,
      "name": "Vendas"
    }
  ]
}
```

**Uso:**
- Parâmetro `tenant_segment_id` no envio de SMS
- Se não informado: usa "Corporativo" como padrão
- Permite rastreamento de custos por departamento

---

## 🔧 7. GERENCIAMENTO DE CAMPANHAS

### 7.1. Pausar Campanha - `/v1/sms/jobs/{jobId}/pause`

**Método:** POST

Pausa o envio de uma campanha em andamento.

### 7.2. Retomar Campanha - `/v1/sms/jobs/{jobId}/play`

**Método:** POST

Retoma o envio de uma campanha pausada.

---

## 🔗 8. OUTROS RECURSOS

### 8.1. Listar APIs Configuradas - `/v1/sms/apis`

**Método:** POST

Lista todas as APIs de SMS cadastradas na conta.

### 8.2. Listar Layouts - `/v1/sms/layouts`

**Método:** POST

Lista layouts de mensagens disponíveis.

### 8.3. Logs de Encurtador - `/v1/sms/accesses`

**Método:** POST

Visualiza acessos a links encurtados em mensagens SMS.

### 8.4. Testar Webhook - `/v1/sms/webhook`

**Método:** POST

Endpoint para testar integração de webhook.

---

# PARTE 2: FUNCIONALIDADES QUE NOSSA SOLUÇÃO ATUAL JÁ TEM

## ✅ Implementado

1. **Envio Básico de SMS** (`/v1/sms/store`)
   - ✅ Envio individual via ChatRoom
   - ✅ Parâmetro `sms_api_id`
   - ✅ Estrutura de mensagens correta

2. **Tratamento de Erros**
   - ✅ Try/catch básico
   - ✅ Logging de erros

3. **Integração com ChatRoom**
   - ✅ Envio de mensagens individuais
   - ✅ Atualização de status na conversa

---

# PARTE 3: MELHORIAS PROPOSTAS PARA NOSSA SOLUÇÃO

## 🚀 PRIORIDADE ALTA (Implementar Imediatamente)

### 1. ⭐ Webhook para Atualização Automática de Status

**Problema Atual:** Não sabemos quando mensagens são entregues/falharam

**Solução:**
```python
# No módulo chatroom_sms
class ChatroomConversation(models.Model):
    _inherit = 'chatroom.conversation'

    sms_request_id = fields.Char(
        string='SMS Request ID',
        help='ID da requisição na Kolmeya (para rastreamento)'
    )
    sms_message_id = fields.Char(
        string='SMS Message ID',
        help='ID da mensagem específica na Kolmeya'
    )
    sms_status = fields.Selection([
        ('pending', 'Pendente'),
        ('sent', 'Enviado'),
        ('delivered', 'Entregue'),
        ('failed', 'Falhou'),
        ('rejected', 'Rejeitado'),
        ('expired', 'Expirado')
    ], string='Status SMS', default='pending')
    sms_status_updated_at = fields.Datetime(
        string='Status Atualizado Em'
    )
```

**Criar Controller para Webhook:**
```python
# controllers/webhook_kolmeya.py
from odoo import http
from odoo.http import request
import logging
import json

_logger = logging.getLogger(__name__)

class KolmeyaWebhookController(http.Controller):

    @http.route('/chatroom/webhook/kolmeya/status',
                type='json', auth='none', methods=['POST'], csrf=False)
    def receive_status_update(self):
        """Recebe atualizações de status da Kolmeya"""
        try:
            data = json.loads(request.httprequest.data)
            _logger.info(f"Webhook Kolmeya Status: {data}")

            request_id = data.get('id')
            messages = data.get('messages', [])

            for msg in messages:
                msg_id = msg.get('id')
                status_code = msg.get('status_code')
                status_text = msg.get('status')

                # Mapear status_code para nosso campo
                status_map = {
                    3: 'delivered',
                    4: 'failed',
                    5: 'rejected',
                    6: 'expired'
                }

                new_status = status_map.get(status_code, 'pending')

                # Buscar conversa pelo message_id
                conversation = request.env['chatroom.conversation'].sudo().search([
                    ('sms_message_id', '=', msg_id)
                ], limit=1)

                if conversation:
                    conversation.write({
                        'sms_status': new_status,
                        'sms_status_updated_at': fields.Datetime.now()
                    })
                    _logger.info(f"Status atualizado: {conversation.id} -> {new_status}")

            return {'status': 'success'}

        except Exception as e:
            _logger.error(f"Erro no webhook Kolmeya: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    @http.route('/chatroom/webhook/kolmeya/reply',
                type='json', auth='none', methods=['POST'], csrf=False)
    def receive_reply(self):
        """Recebe respostas de clientes via SMS"""
        try:
            data = json.loads(request.httprequest.data)
            _logger.info(f"Webhook Kolmeya Reply: {data}")

            reply_data = data.get('reply', {})
            reply_text = reply_data.get('reply')
            message_data = reply_data.get('message', {})
            phone = message_data.get('phone')
            original_msg_id = message_data.get('id')

            # Buscar conversa original
            original_conv = request.env['chatroom.conversation'].sudo().search([
                ('sms_message_id', '=', original_msg_id)
            ], limit=1)

            if original_conv and original_conv.room_id:
                # Criar nova conversa com a resposta do cliente
                request.env['chatroom.conversation'].sudo().create({
                    'room_id': original_conv.room_id.id,
                    'body': reply_text,
                    'author_id': original_conv.room_id.customer_id.id,
                    'is_sms': True,
                    'sms_status': 'delivered'
                })
                _logger.info(f"Resposta registrada para room {original_conv.room_id.id}")

            return {'status': 'success'}

        except Exception as e:
            _logger.error(f"Erro no webhook reply: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}
```

**Atualizar Método de Envio:**
```python
def send_sms_chatroom(self, phone, message, room_id=None):
    """Envio com webhook configurado"""
    url = "https://kolmeya.com.br/api/v1/sms/store"
    headers = {
        "Authorization": f"Bearer {self.get_token()}",
        "Content-Type": "application/json"
    }

    # URL do webhook (configurar no ir.config_parameter)
    webhook_url = self.env['ir.config_parameter'].sudo().get_param(
        'chatroom_sms.webhook_url',
        'https://seu-servidor.com/chatroom/webhook/kolmeya/status'
    )

    payload = {
        "sms_api_id": int(self.api_id),
        "webhook_url": webhook_url,  # NOVO!
        "reference": f"room_{room_id}" if room_id else None,  # NOVO!
        "messages": [{
            "phone": int(phone),
            "message": message,
            "reference": f"msg_{room_id}"  # NOVO!
        }]
    }

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    # Salvar IDs para rastreamento
    if result.get('valids'):
        msg_data = result['valids'][0]
        return {
            'success': True,
            'request_id': result.get('id'),
            'message_id': msg_data.get('id'),
            'reference': msg_data.get('reference')
        }

    return {'success': False, 'error': result}
```

**Benefícios:**
- ✅ Rastreamento automático de entregas
- ✅ Notificação de falhas em tempo real
- ✅ Registro de respostas de clientes
- ✅ Compliance e auditoria melhorados

---

### 2. ⭐ Consulta de Saldo Automática

**Problema Atual:** Não sabemos quantos créditos temos

**Solução:**
```python
class ChatroomSmsApi(models.Model):
    _inherit = 'chatroom.sms.api'

    balance = fields.Float(
        string='Saldo Disponível',
        readonly=True,
        help='Saldo de créditos SMS na Kolmeya'
    )
    balance_last_update = fields.Datetime(
        string='Saldo Atualizado Em',
        readonly=True
    )
    balance_warning_threshold = fields.Float(
        string='Alerta de Saldo Baixo',
        default=100.0,
        help='Emitir alerta quando saldo for menor que este valor'
    )

    def update_balance(self):
        """Atualiza saldo da conta Kolmeya"""
        for api in self:
            try:
                url = "https://kolmeya.com.br/api/v1/sms/balance"
                headers = {
                    "Authorization": f"Bearer {api.get_token()}",
                    "Content-Type": "application/json"
                }

                response = requests.post(url, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    balance = float(result.get('balance', 0))

                    api.write({
                        'balance': balance,
                        'balance_last_update': fields.Datetime.now()
                    })

                    # Enviar alerta se saldo baixo
                    if balance < api.balance_warning_threshold:
                        api._send_low_balance_notification(balance)

                    _logger.info(f"Saldo atualizado: {balance}")

            except Exception as e:
                _logger.error(f"Erro ao atualizar saldo: {e}", exc_info=True)

    def _send_low_balance_notification(self, current_balance):
        """Envia notificação de saldo baixo"""
        # Buscar usuários admin
        admin_group = self.env.ref('base.group_system')
        admins = self.env['res.users'].search([
            ('groups_id', 'in', admin_group.id)
        ])

        # Criar atividade/notificação
        self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get_id('chatroom.sms.api'),
            'res_id': self.id,
            'activity_type_id': self.env.ref('mail.mail_activity_data_warning').id,
            'summary': f'Saldo SMS Baixo: {current_balance}',
            'note': f'O saldo de créditos SMS está abaixo do limite. '
                    f'Saldo atual: {current_balance}. '
                    f'Limite configurado: {self.balance_warning_threshold}',
            'user_id': admins[0].id if admins else self.env.user.id
        })

    @api.model
    def cron_update_balance(self):
        """Cron job para atualizar saldo diariamente"""
        apis = self.search([('active', '=', True)])
        apis.update_balance()
```

**Criar Cron Job:**
```xml
<!-- data/cron_sms_balance.xml -->
<odoo>
    <data noupdate="1">
        <record id="cron_sms_balance_update" model="ir.cron">
            <field name="name">Update SMS Balance</field>
            <field name="model_id" ref="model_chatroom_sms_api"/>
            <field name="state">code</field>
            <field name="code">model.cron_update_balance()</field>
            <field name="interval_number">1</field>
            <field name="interval_type">days</field>
            <field name="numbercall">-1</field>
            <field name="active" eval="True"/>
        </record>
    </data>
</odoo>
```

**Benefícios:**
- ✅ Saber sempre quanto saldo temos
- ✅ Alertas automáticos de saldo baixo
- ✅ Evitar falhas por falta de créditos

---

### 3. ⭐ Tratamento de Blacklist e "Não Perturbe"

**Problema Atual:** Não sabemos se números estão bloqueados

**Solução:**
```python
class ChatroomRoom(models.Model):
    _inherit = 'chatroom.room'

    phone_blacklisted = fields.Boolean(
        string='Telefone em Blacklist',
        compute='_compute_phone_status',
        store=True
    )
    phone_not_disturb = fields.Boolean(
        string='Não Perturbe Ativo',
        compute='_compute_phone_status',
        store=True
    )
    phone_status_checked_at = fields.Datetime(
        string='Status Verificado Em'
    )

    @api.depends('mobile_number')
    def _compute_phone_status(self):
        """Verifica status do telefone antes de enviar"""
        # Este campo seria atualizado ao tentar enviar SMS
        # e receber resposta da API indicando blacklist/not_disturb
        pass

    def add_to_blacklist(self, document=None):
        """Adiciona telefone à blacklist"""
        self.ensure_one()
        if not self.mobile_number:
            return

        api = self.env['chatroom.sms.api'].search([('active', '=', True)], limit=1)
        if not api:
            return

        url = "https://kolmeya.com.br/api/v1/blacklist/store"
        headers = {
            "Authorization": f"Bearer {api.get_token()}",
            "Content-Type": "application/json"
        }

        phone_data = {
            "phone": int(''.join(filter(str.isdigit, self.mobile_number)))
        }

        if document:
            phone_data['document'] = document

        payload = {
            "tenant_id": int(api.tenant_id),
            "phones": [phone_data]
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 201:
                self.phone_blacklisted = True
                _logger.info(f"Telefone {self.mobile_number} adicionado à blacklist")

        except Exception as e:
            _logger.error(f"Erro ao adicionar blacklist: {e}", exc_info=True)

    def remove_from_blacklist(self):
        """Remove telefone da blacklist"""
        # Similar ao add_to_blacklist mas usando /v1/blacklist/destroy
        pass
```

**Atualizar Método de Envio para Registrar Status:**
```python
def send_sms_chatroom(self, phone, message, room_id=None):
    """Envio com registro de status de blacklist/not_disturb"""
    # ... código de envio ...

    result = response.json()

    # Processar respostas
    if result.get('blacklist'):
        # Marcar rooms como blacklisted
        for bl_phone in result['blacklist']:
            room = self.env['chatroom.room'].search([
                ('mobile_number', 'like', str(bl_phone['phone'])[-9:])
            ])
            if room:
                room.phone_blacklisted = True
                room.phone_status_checked_at = fields.Datetime.now()

    if result.get('not_disturb'):
        # Marcar rooms com not_disturb
        for nd_phone in result['not_disturb']:
            room = self.env['chatroom.room'].search([
                ('mobile_number', 'like', str(nd_phone['phone'])[-9:])
            ])
            if room:
                room.phone_not_disturb = True
                room.phone_status_checked_at = fields.Datetime.now()

    return result
```

**Benefícios:**
- ✅ Evitar tentar enviar para números bloqueados
- ✅ Compliance com "Não Perturbe" (Lei SP)
- ✅ Reduzir custos de tentativas inválidas

---

## 🎯 PRIORIDADE MÉDIA (Implementar em 2-4 Semanas)

### 4. Histórico e Rastreamento Completo

**Criar Modelo de Log de SMS:**
```python
class ChatroomSmsLog(models.Model):
    _name = 'chatroom.sms.log'
    _description = 'Log de Envios SMS'
    _order = 'create_date desc'

    room_id = fields.Many2one('chatroom.room', string='Sala', ondelete='cascade')
    conversation_id = fields.Many2one('chatroom.conversation', string='Conversa')

    phone = fields.Char(string='Telefone')
    message = fields.Text(string='Mensagem')

    request_id = fields.Char(string='Request ID Kolmeya')
    message_id = fields.Char(string='Message ID Kolmeya')
    reference = fields.Char(string='Referência')

    status = fields.Selection([
        ('pending', 'Pendente'),
        ('sent', 'Enviado'),
        ('delivered', 'Entregue'),
        ('failed', 'Falhou'),
        ('rejected', 'Rejeitado'),
        ('expired', 'Expirado')
    ], string='Status', default='pending')

    status_code = fields.Integer(string='Código Status')
    status_message = fields.Text(string='Mensagem Status')

    sent_at = fields.Datetime(string='Enviado Em')
    delivered_at = fields.Datetime(string='Entregue Em')

    cost = fields.Float(string='Custo Estimado')
    segment_id = fields.Many2one('chatroom.sms.segment', string='Centro de Custo')

    error_message = fields.Text(string='Mensagem de Erro')
```

**View:**
```xml
<record id="view_chatroom_sms_log_tree" model="ir.ui.view">
    <field name="name">chatroom.sms.log.tree</field>
    <field name="model">chatroom.sms.log</field>
    <field name="arch" type="xml">
        <tree string="Log SMS">
            <field name="create_date"/>
            <field name="phone"/>
            <field name="message"/>
            <field name="status"/>
            <field name="delivered_at"/>
            <field name="room_id"/>
        </tree>
    </field>
</record>

<record id="action_chatroom_sms_log" model="ir.actions.act_window">
    <field name="name">Log SMS</field>
    <field name="res_model">chatroom.sms.log</field>
    <field name="view_mode">tree,form</field>
</record>

<menuitem id="menu_chatroom_sms_log"
          name="Log SMS"
          parent="chatroom.menu_chatroom_config"
          action="action_chatroom_sms_log"
          sequence="50"/>
```

---

### 5. Envio em Lote Otimizado

**Adicionar Funcionalidade de Envio em Massa:**
```python
class ChatroomSendBulkSms(models.TransientModel):
    _name = 'chatroom.send.bulk.sms'
    _description = 'Envio SMS em Lote'

    room_ids = fields.Many2many('chatroom.room', string='Salas')
    message = fields.Text(string='Mensagem', required=True)
    segment_id = fields.Many2one('chatroom.sms.segment', string='Centro de Custo')

    test_mode = fields.Boolean(
        string='Modo Teste',
        help='Envia apenas para 5 contatos para teste'
    )

    skip_blacklist = fields.Boolean(
        string='Pular Blacklist',
        default=True
    )
    skip_not_disturb = fields.Boolean(
        string='Pular Não Perturbe',
        default=True
    )

    def send_bulk_sms(self):
        """Envia SMS em lote (até 1000 por vez)"""
        self.ensure_one()

        rooms = self.room_ids
        if self.test_mode:
            rooms = rooms[:5]

        # Filtrar
        if self.skip_blacklist:
            rooms = rooms.filtered(lambda r: not r.phone_blacklisted)
        if self.skip_not_disturb:
            rooms = rooms.filtered(lambda r: not r.phone_not_disturb)

        # Dividir em lotes de 1000
        batch_size = 1000
        for i in range(0, len(rooms), batch_size):
            batch = rooms[i:i+batch_size]
            self._send_batch(batch)

    def _send_batch(self, rooms):
        """Envia um lote de até 1000 SMS"""
        api = self.env['chatroom.sms.api'].search([('active', '=', True)], limit=1)
        if not api:
            raise UserError("Nenhuma API SMS configurada")

        messages = []
        for room in rooms:
            if room.mobile_number:
                messages.append({
                    "phone": int(''.join(filter(str.isdigit, room.mobile_number))),
                    "message": self.message,
                    "reference": f"room_{room.id}"
                })

        if not messages:
            return

        url = "https://kolmeya.com.br/api/v1/sms/store"
        headers = {
            "Authorization": f"Bearer {api.get_token()}",
            "Content-Type": "application/json"
        }

        payload = {
            "sms_api_id": int(api.api_id),
            "messages": messages,
            "tenant_segment_id": self.segment_id.kolmeya_id if self.segment_id else None,
            "webhook_url": self.env['ir.config_parameter'].sudo().get_param(
                'chatroom_sms.webhook_url'
            )
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            result = response.json()

            # Criar logs
            for valid_msg in result.get('valids', []):
                self.env['chatroom.sms.log'].create({
                    'phone': valid_msg.get('phone'),
                    'message': self.message,
                    'request_id': result.get('id'),
                    'message_id': valid_msg.get('id'),
                    'reference': valid_msg.get('reference'),
                    'status': 'sent',
                    'sent_at': fields.Datetime.now()
                })

            _logger.info(f"Lote enviado: {len(result.get('valids', []))} válidos, "
                        f"{len(result.get('invalids', []))} inválidos")

        except Exception as e:
            _logger.error(f"Erro ao enviar lote: {e}", exc_info=True)
            raise
```

---

### 6. Dashboard e Relatórios

**Criar Dashboard de SMS:**
```python
class ChatroomSmsDashboard(models.Model):
    _name = 'chatroom.sms.dashboard'
    _description = 'Dashboard SMS'
    _auto = False  # View SQL

    period = fields.Date(string='Período')
    total_sent = fields.Integer(string='Total Enviados')
    total_delivered = fields.Integer(string='Total Entregues')
    total_failed = fields.Integer(string='Total Falhados')
    delivery_rate = fields.Float(string='Taxa de Entrega %')
    total_replies = fields.Integer(string='Total Respostas')
    avg_cost = fields.Float(string='Custo Médio')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'chatroom_sms_dashboard')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW chatroom_sms_dashboard AS (
                SELECT
                    ROW_NUMBER() OVER () as id,
                    DATE(sent_at) as period,
                    COUNT(*) as total_sent,
                    SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as total_delivered,
                    SUM(CASE WHEN status IN ('failed', 'rejected', 'expired') THEN 1 ELSE 0 END) as total_failed,
                    (SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END)::float /
                     NULLIF(COUNT(*), 0) * 100) as delivery_rate,
                    SUM(cost) as avg_cost,
                    0 as total_replies
                FROM chatroom_sms_log
                WHERE sent_at IS NOT NULL
                GROUP BY DATE(sent_at)
                ORDER BY DATE(sent_at) DESC
            )
        """)
```

---

## 💡 PRIORIDADE BAIXA (Futuro - Nice to Have)

### 7. Integração com Relatórios Avançados Kolmeya

- Consultar `/v1/sms/reports/quantity-jobs` mensalmente
- Gerar gráficos de uso por centro de custo
- Análise de ROI de campanhas SMS

### 8. Gerenciamento de Campanhas

- Pausar/Retomar campanhas (`/jobs/{id}/pause` e `/jobs/{id}/play`)
- Agendar envios em massa
- Templates de mensagens

### 9. Encurtador de Links

- Integrar com `/v1/sms/accesses` para rastrear cliques
- Gerar links curtos automaticamente
- Analytics de cliques por campanha

### 10. Autenticação 2FA

- Usar endpoint `/v1/sms/store-token` para códigos
- Integração com login do Odoo
- Verificação de transações sensíveis

---

# PARTE 4: PLANO DE IMPLEMENTAÇÃO RECOMENDADO

## Fase 1 - Essencial (1-2 Semanas)

✅ **Semana 1:**
1. Implementar webhooks de status
2. Adicionar campos `sms_request_id`, `sms_message_id`, `sms_status` ao modelo
3. Criar controllers de webhook
4. Testar recebimento de status

✅ **Semana 2:**
1. Implementar consulta de saldo
2. Criar cron job de atualização diária
3. Sistema de alertas de saldo baixo
4. Testar e ajustar

## Fase 2 - Importante (2-3 Semanas)

✅ **Semana 3:**
1. Implementar tratamento de blacklist/not_disturb
2. Adicionar campos no modelo chatroom.room
3. Métodos de adicionar/remover blacklist

✅ **Semana 4-5:**
1. Criar modelo chatroom.sms.log
2. Registrar todos os envios
3. Views e menu de consulta
4. Relatórios básicos

## Fase 3 - Avançado (1 Mês)

✅ **Mês 2:**
1. Envio em lote otimizado
2. Wizard de envio em massa
3. Dashboard de SMS
4. Relatórios avançados

## Fase 4 - Extras (Conforme Demanda)

- Gerenciamento de campanhas
- Templates
- Encurtador de links
- 2FA

---

# PARTE 5: RESUMO EXECUTIVO DE BENEFÍCIOS

## Implementando as Melhorias Prioritárias, Você Terá:

### 🎯 Rastreamento Completo
- ✅ Saber EXATAMENTE quando cada SMS foi entregue
- ✅ Notificação automática de falhas
- ✅ Registro de respostas de clientes

### 💰 Controle Financeiro
- ✅ Monitoramento de saldo em tempo real
- ✅ Alertas de saldo baixo
- ✅ Evitar surpresas de créditos esgotados

### 🚫 Compliance
- ✅ Respeitar blacklist automaticamente
- ✅ Conformidade com lei "Não Perturbe"
- ✅ Auditoria completa de envios

### 📊 Gestão e Analytics
- ✅ Histórico completo de envios
- ✅ Taxa de entrega
- ✅ Relatórios por período
- ✅ Dashboard visual

### ⚡ Eficiência Operacional
- ✅ Envio em lote (até 1000 por vez)
- ✅ Menos tentativas inválidas
- ✅ Processos automatizados

---

## 📝 CÓDIGO DE CONFIGURAÇÃO INICIAL

```xml
<!-- data/config_parameters.xml -->
<odoo>
    <data noupdate="1">
        <!-- URL do Webhook -->
        <record id="chatroom_sms_webhook_url" model="ir.config_parameter">
            <field name="key">chatroom_sms.webhook_url</field>
            <field name="value">https://seu-servidor.odoo.com/chatroom/webhook/kolmeya/status</field>
        </record>

        <!-- URL do Webhook de Respostas -->
        <record id="chatroom_sms_webhook_reply_url" model="ir.config_parameter">
            <field name="key">chatroom_sms.webhook_reply_url</field>
            <field name="value">https://seu-servidor.odoo.com/chatroom/webhook/kolmeya/reply</field>
        </record>
    </data>
</odoo>
```

**IMPORTANTE:** Substituir `https://seu-servidor.odoo.com` pela URL real do servidor Odoo.

---

**Status:** ✅ DOCUMENTAÇÃO COMPLETA
**Data:** 16/11/2025
**Próxima Ação:** Revisar e priorizar implementações conforme necessidade do negócio
