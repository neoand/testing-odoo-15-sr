# Kolmeya SMS - Architecture Recommendations

**Date:** 2025-11-15
**Based on:** GitHub Open Source Research (OCA + Community Best Practices)
**Purpose:** Design robust, maintainable SMS integration for SempreReal

---

## 📋 Executive Summary

After comprehensive research of open-source SMS modules (OCA connector-telephony, GatewayAPI, Twilio, queue_job, mail_tracking), we've identified **architectural patterns and best practices** to make the Kolmeya integration enterprise-grade.

### Key Recommendations

1. **Modular Architecture** - Separate core SMS abstraction from Kolmeya provider
2. **Secure Webhooks** - JWT authentication for reply/status webhooks
3. **Job Queue Integration** - Async processing with retry logic
4. **Chatter Integration** - SMS tracking visible in message history
5. **Provider Abstraction** - Future-proof design for multiple SMS providers

---

## 🏗️ Proposed Module Structure

### Current Approach (Single Module)
```
contacts_realcred/
├── models/
│   ├── contacts_realcred.py          # Everything in one file
│   └── contacts_realcred_campaign.py
└── views/
```

**Issues:**
- ❌ Tight coupling to Kolmeya API
- ❌ Hard to test without real API calls
- ❌ Can't switch providers easily
- ❌ No separation of concerns

### Recommended Approach (Modular)
```
sms_base_sr/                          # 📦 Core SMS abstraction (provider-agnostic)
├── models/
│   ├── sms_message.py                # Base SMS message model
│   ├── sms_template.py               # Template system
│   ├── sms_provider.py               # Provider interface
│   └── res_partner.py                # Add SMS capability to partners
├── controllers/
│   └── webhook.py                    # Base webhook controller
└── security/
    └── ir.model.access.csv

sms_kolmeya/                          # 📦 Kolmeya-specific provider
├── models/
│   ├── sms_provider_kolmeya.py       # Kolmeya implementation
│   └── kolmeya_api.py                # API wrapper class
├── controllers/
│   └── kolmeya_webhook.py            # Kolmeya webhook handler
└── data/
    └── sms_provider_data.xml         # Auto-configure Kolmeya provider

contacts_realcred_sms/                # 📦 SempreReal business logic
├── models/
│   ├── contacts_realcred_campaign.py # Enhanced with SMS capability
│   └── contacts_realcred_batch.py    # Add send_sms() method
└── views/
    └── campaign_sms_views.xml        # SMS-specific UI
```

**Benefits:**
- ✅ Can add Twilio/AWS SNS later without touching existing code
- ✅ Core SMS logic reusable across modules
- ✅ Easy to mock providers for testing
- ✅ Clear separation: base → provider → business logic

---

## 🔒 Security Best Practices

### 1. Webhook Authentication (from GatewayAPI pattern)

**Current Risk:** Unauthenticated webhooks = anyone can POST fake replies/statuses

**Recommended Solution: JWT Signature Validation**

```python
# sms_base_sr/controllers/webhook.py
import jwt
from odoo import http
from odoo.http import request

class SMSWebhookController(http.Controller):

    @http.route('/sms/webhook/reply', type='json', auth='public', methods=['POST'], csrf=False)
    def receive_reply(self, **kwargs):
        """Receive SMS reply - MUST validate signature first"""

        # 1. Get JWT secret from system parameters
        ICP = request.env['ir.config_parameter'].sudo()
        jwt_secret = ICP.get_param('sms.webhook.jwt_secret')

        if not jwt_secret:
            return {'error': 'Webhook not configured'}, 503

        # 2. Extract JWT signature from header
        jwt_token = request.httprequest.headers.get('X-SMS-Signature')
        if not jwt_token:
            return {'error': 'Missing signature'}, 401

        # 3. Verify JWT
        try:
            payload = jwt.decode(jwt_token, jwt_secret, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return {'error': 'Invalid signature'}, 403

        # 4. Process webhook data
        return self._process_reply(request.jsonrequest)

    def _process_reply(self, data):
        """Override in provider-specific controller"""
        raise NotImplementedError
```

**Configuration:**
```python
# Generate secure JWT secret
import secrets
jwt_secret = secrets.token_urlsafe(64)

# Store in system parameters (Admin → Settings → Technical → Parameters)
sms.webhook.jwt_secret = "YOUR_GENERATED_SECRET"

# Share with Kolmeya support to configure their webhook calls
```

### 2. Credential Storage (from OCA connector-telephony)

**Current Risk:** API token hardcoded in Python files

**Recommended Solution: Use server_environment or keychain**

```python
# sms_kolmeya/models/sms_provider_kolmeya.py
from odoo import models, fields

class SMSProviderKolmeya(models.Model):
    _inherit = 'sms.provider'

    provider_type = fields.Selection(selection_add=[('kolmeya', 'Kolmeya')])

    # Stored encrypted in database
    kolmeya_api_token = fields.Char(
        'API Token',
        groups='base.group_system'  # Only admins see
    )
    kolmeya_segment_id = fields.Integer('Segment ID', default=109)

    def _kolmeya_send_batch(self, messages):
        """Send via Kolmeya API"""
        self.ensure_one()

        # Use instance token, not hardcoded
        headers = {
            'Authorization': f'Bearer {self.kolmeya_api_token}',
            'Content-Type': 'application/json'
        }
        # ... rest of implementation
```

### 3. Rate Limiting Protection

```python
# sms_kolmeya/models/kolmeya_api.py
import time
from odoo.exceptions import UserError

class KolmeyaAPI:
    """Kolmeya API wrapper with built-in rate limiting"""

    def __init__(self, token, segment_id=109):
        self.token = token
        self.segment_id = segment_id
        self._last_rate_limit = None

    def send_batch(self, messages, auto_wait=True):
        """Send with automatic rate limit handling"""

        response = requests.post(
            f"{self.BASE_URL}/sms/store",
            json={'messages': messages},
            headers={'Authorization': f'Bearer {self.token}'},
            timeout=30
        )

        # Check rate limit header
        rate_remaining = response.headers.get('X-RateLimit-Remaining')
        if rate_remaining:
            rate_remaining = int(rate_remaining)
            self._last_rate_limit = rate_remaining

            # Auto-throttle if getting close
            if rate_remaining < 50 and auto_wait:
                _logger.warning(f"Rate limit baixo ({rate_remaining}), aguardando 60s...")
                time.sleep(60)

        if response.status_code == 429:
            raise UserError("Rate limit excedido. Aguarde alguns minutos.")

        response.raise_for_status()
        return response.json()
```

---

## 🔄 Queue Integration (from OCA queue_job)

### Why Use Job Queue?

**Current Problem:**
- Sending 10,000 SMS = HTTP request blocked for 30+ seconds
- User waits, browser times out
- If fails, no automatic retry

**Solution: Async Jobs**

```python
# contacts_realcred_sms/models/contacts_realcred_campaign.py
from odoo import models, fields, api
from odoo.addons.queue_job.job import job

class ContactsRealcredCampaign(models.Model):
    _inherit = 'contacts.realcred.campaign'

    # NOVO: Job tracking
    sms_job_uuid = fields.Char('Job UUID', readonly=True)
    sms_job_state = fields.Selection([
        ('pending', 'Pendente'),
        ('started', 'Processando'),
        ('done', 'Concluído'),
        ('failed', 'Falhou')
    ], string='Status do Envio')

    def check_data_kolmeya_send(self):
        """Schedule async job instead of sending immediately"""
        self.ensure_one()

        # Create job with retry pattern
        job_obj = self.with_delay(
            priority=10,
            max_retries=5,
            eta=30  # Start in 30 seconds
        ).process_sms_campaign()

        # Store job reference
        self.write({
            'sms_job_uuid': job_obj.uuid,
            'sms_job_state': 'pending'
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Envio Agendado',
                'message': f'Campanha será processada em background. Job: {job_obj.uuid}',
                'type': 'success',
                'sticky': False,
            }
        }

    @job(retry_pattern={1: 60, 2: 180, 3: 600, 5: 1800})
    def process_sms_campaign(self):
        """
        Actual sending logic - runs in background

        Retry pattern (from OCA best practices):
        - 1st retry: wait 60s
        - 2nd retry: wait 180s (3 min)
        - 3rd retry: wait 600s (10 min)
        - 5th retry: wait 1800s (30 min)
        """
        self.ensure_one()
        self.sms_job_state = 'started'

        try:
            # Prepare messages
            messages = []
            sms_records = []

            for contact in self.contacts_realcred_campaign_ids:
                if not (contact.telefone1 and contact.updated_limit and not contact.falecido):
                    continue

                # Create SMS record
                sms = self.env['sms.message'].create({
                    'partner_id': contact.partner_id.id,
                    'phone': contact.telefone1,
                    'body': self._render_message(contact),
                    'campaign_id': self.id,
                    'state': 'outgoing'
                })
                sms_records.append(sms)

                messages.append({
                    'phone': contact.telefone1.strip(),
                    'message': sms.body.strip(),
                    'reference': str(sms.id)
                })

            # Send via provider (batches of 1000)
            provider = self.env['sms.provider'].search([('provider_type', '=', 'kolmeya')], limit=1)

            for i in range(0, len(messages), 1000):
                batch = messages[i:i+1000]
                result = provider._send_batch(batch)

                # Update SMS records with job_id
                job_id = result.get('id')
                batch_sms = sms_records[i:i+1000]
                for sms in batch_sms:
                    sms.write({
                        'kolmeya_job_id': job_id,
                        'state': 'sent'
                    })

            # Mark campaign as completed
            self.write({
                'state_sms': 'finished',
                'sms_job_state': 'done'
            })

        except Exception as e:
            self.sms_job_state = 'failed'
            raise  # Re-raise for job retry mechanism

    def _render_message(self, contact):
        """Render message with variable substitution"""
        template_data = {
            'name': contact.name or '',
            'cpf': contact.cpf or '',
            'vi_rmi': f"R$ {contact.vi_rmi:,.2f}" if contact.vi_rmi else '',
        }
        return self.sms_template_id.render(template_data)
```

**Required Dependency:**
```python
# contacts_realcred_sms/__manifest__.py
{
    'depends': ['sms_base_sr', 'sms_kolmeya', 'queue_job', 'contacts_realcred'],
}
```

---

## 📊 SMS Tracking in Chatter (from OCA mail_tracking)

### Visual SMS History

**User Experience Goal:** Vendedoras see SMS history like emails in chatter

```python
# sms_base_sr/models/sms_message.py
from odoo import models, fields, api

class SMSMessage(models.Model):
    _name = 'sms.message'
    _description = 'SMS Message'
    _inherit = ['mail.thread']  # Enable chatter
    _order = 'create_date DESC'

    # Relations
    partner_id = fields.Many2one('res.partner', 'Destinatário', required=True)
    campaign_id = fields.Many2one('contacts.realcred.campaign', 'Campanha')

    # Content
    phone = fields.Char('Telefone', required=True)
    body = fields.Text('Mensagem', required=True)
    direction = fields.Selection([
        ('outgoing', 'Enviado'),
        ('incoming', 'Recebido')
    ], default='outgoing', required=True)

    # Status tracking
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('outgoing', 'Aguardando Envio'),
        ('sent', 'Enviado'),
        ('delivered', 'Entregue'),
        ('error', 'Erro'),
        ('rejected', 'Rejeitado'),
        ('expired', 'Expirado')
    ], default='draft', required=True, tracking=True)

    # Provider data
    provider_id = fields.Many2one('sms.provider', 'Provedor')
    kolmeya_job_id = fields.Char('Kolmeya Job ID')
    kolmeya_message_id = fields.Char('Kolmeya Message ID')

    # Metadata
    sent_date = fields.Datetime('Data de Envio')
    delivered_date = fields.Datetime('Data de Entrega')
    error_message = fields.Text('Mensagem de Erro')

    @api.model
    def create(self, vals):
        """Post to chatter on creation"""
        sms = super().create(vals)

        # Log in partner's chatter
        if sms.partner_id:
            icon = '📤' if sms.direction == 'outgoing' else '📥'
            sms.partner_id.message_post(
                body=f"{icon} SMS {sms.direction}: {sms.body}",
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )

        return sms

    def write(self, vals):
        """Log status changes in chatter"""
        result = super().write(vals)

        if 'state' in vals:
            for sms in self:
                status_icon = {
                    'sent': '📤',
                    'delivered': '✅',
                    'error': '❌',
                    'rejected': '⛔',
                    'expired': '⏰'
                }.get(sms.state, '🔄')

                sms.message_post(
                    body=f"{status_icon} Status alterado para: {sms.state}",
                    message_type='notification'
                )

        return result
```

### Integration with res.partner

```python
# sms_base_sr/models/res_partner.py
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # SMS Statistics
    sms_count = fields.Integer('Total SMS', compute='_compute_sms_stats')
    sms_sent_count = fields.Integer('SMS Enviados', compute='_compute_sms_stats')
    sms_received_count = fields.Integer('SMS Recebidos', compute='_compute_sms_stats')
    last_sms_date = fields.Datetime('Último SMS', compute='_compute_sms_stats')

    @api.depends('sms_message_ids')
    def _compute_sms_stats(self):
        for partner in self:
            sms_messages = partner.sms_message_ids
            partner.sms_count = len(sms_messages)
            partner.sms_sent_count = len(sms_messages.filtered(lambda s: s.direction == 'outgoing'))
            partner.sms_received_count = len(sms_messages.filtered(lambda s: s.direction == 'incoming'))
            partner.last_sms_date = sms_messages[0].create_date if sms_messages else False

    # Smart button action
    def action_view_sms_messages(self):
        """Open SMS messages for this partner"""
        return {
            'name': 'Mensagens SMS',
            'type': 'ir.actions.act_window',
            'res_model': 'sms.message',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }
```

**UI Enhancement:**
```xml
<!-- sms_base_sr/views/res_partner_views.xml -->
<record id="view_partner_form_sms" model="ir.ui.view">
    <field name="name">res.partner.form.sms</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <xpath expr="//div[@name='button_box']" position="inside">
            <button name="action_view_sms_messages" type="object"
                    class="oe_stat_button" icon="fa-comment-o">
                <field name="sms_count" widget="statinfo" string="SMS"/>
            </button>
        </xpath>
    </field>
</record>
```

---

## 🔔 Bidirectional Communication

### Reply Capture Architecture

```python
# sms_kolmeya/controllers/kolmeya_webhook.py
from odoo import http
from odoo.http import request
import logging
import jwt

_logger = logging.getLogger(__name__)

class KolmeyaWebhookController(http.Controller):

    @http.route('/kolmeya/webhook/reply', type='json', auth='public', methods=['POST'], csrf=False)
    def receive_reply(self, **kwargs):
        """
        Receive SMS reply from Kolmeya

        Expected payload from Kolmeya:
        {
            "id": "reply-uuid",
            "phone": "5548991910234",
            "message": "Sim, tenho interesse!",
            "received_at": "2025-11-15T18:30:00Z",
            "original_message_id": "original-uuid"  # If replying to our message
        }
        """

        # 1. Validate JWT signature
        if not self._validate_webhook_signature():
            return {'status': 'error', 'message': 'Invalid signature'}, 403

        # 2. Get payload
        data = request.jsonrequest
        _logger.info(f"Kolmeya Reply Webhook: {data}")

        # 3. Process reply
        try:
            sms = request.env['sms.message'].sudo().create({
                'direction': 'incoming',
                'phone': data.get('phone'),
                'body': data.get('message'),
                'state': 'delivered',
                'kolmeya_message_id': data.get('id'),
                'delivered_date': data.get('received_at')
            })

            # 4. Try to match to existing contact
            partner = self._find_partner_by_phone(data.get('phone'))
            if partner:
                sms.partner_id = partner.id

                # Post in chatter
                partner.message_post(
                    body=f"📥 Resposta SMS recebida: {data.get('message')}",
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment'  # Creates activity
                )

                # 5. Create activity for vendedor
                self._create_reply_activity(partner, sms)

            return {'status': 'success', 'sms_id': sms.id}

        except Exception as e:
            _logger.error(f"Error processing reply: {e}")
            return {'status': 'error', 'message': str(e)}, 500

    @http.route('/kolmeya/webhook/status', type='json', auth='public', methods=['POST'], csrf=False)
    def receive_status(self, **kwargs):
        """
        Receive delivery status update

        Expected payload:
        {
            "message_id": "uuid",
            "status_code": 3,  # 1=trying, 2=sent, 3=delivered, 4=failed, 5=rejected, 6=expired
            "status": "Entregue",
            "updated_at": "2025-11-15T18:31:00Z"
        }
        """

        if not self._validate_webhook_signature():
            return {'status': 'error', 'message': 'Invalid signature'}, 403

        data = request.jsonrequest
        message_id = data.get('message_id')
        status_code = data.get('status_code')

        # Find SMS by Kolmeya ID
        sms = request.env['sms.message'].sudo().search([
            ('kolmeya_message_id', '=', message_id)
        ], limit=1)

        if not sms:
            return {'status': 'error', 'message': 'SMS not found'}, 404

        # Map Kolmeya status to our states
        status_map = {
            1: 'outgoing',   # Trying to send
            2: 'sent',       # Sent to operator
            3: 'delivered',  # Delivered
            4: 'error',      # Not delivered
            5: 'rejected',   # Rejected by operator
            6: 'expired'     # Expired
        }

        new_state = status_map.get(status_code)
        if new_state:
            vals = {'state': new_state}

            if new_state == 'delivered':
                vals['delivered_date'] = data.get('updated_at')
            elif new_state in ['error', 'rejected']:
                vals['error_message'] = data.get('status')

            sms.write(vals)

        return {'status': 'success'}

    def _validate_webhook_signature(self):
        """Validate JWT signature from Kolmeya"""
        try:
            ICP = request.env['ir.config_parameter'].sudo()
            jwt_secret = ICP.get_param('kolmeya.webhook.jwt_secret')

            if not jwt_secret:
                _logger.warning("Kolmeya webhook JWT secret not configured")
                return False

            jwt_token = request.httprequest.headers.get('X-Kolmeya-Signature')
            if not jwt_token:
                _logger.warning("Missing X-Kolmeya-Signature header")
                return False

            payload = jwt.decode(jwt_token, jwt_secret, algorithms=['HS256'])
            return True

        except jwt.InvalidTokenError as e:
            _logger.error(f"Invalid JWT signature: {e}")
            return False

    def _find_partner_by_phone(self, phone):
        """Find partner by phone number (try multiple formats)"""
        if not phone:
            return None

        # Clean phone
        phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '')

        # Search patterns
        Partner = request.env['res.partner'].sudo()

        # Try exact match
        partner = Partner.search([
            '|', ('phone', '=', phone_clean),
            ('mobile', '=', phone_clean)
        ], limit=1)

        if partner:
            return partner

        # Try contacts_realcred_batch
        Batch = request.env['contacts.realcred.batch'].sudo()
        batch = Batch.search([
            '|', ('telefone1', 'ilike', phone_clean[-8:]),  # Last 8 digits
            ('whatsapp1', 'ilike', phone_clean[-8:])
        ], limit=1)

        return batch.partner_id if batch else None

    def _create_reply_activity(self, partner, sms):
        """Create activity to alert vendedor"""
        Activity = request.env['mail.activity'].sudo()

        # Find vendedor (user_id in partner or campaign)
        user = partner.user_id or partner.team_id.user_id
        if not user:
            user = request.env.ref('base.user_admin')

        Activity.create({
            'res_id': partner.id,
            'res_model_id': request.env['ir.model']._get('res.partner').id,
            'activity_type_id': request.env.ref('mail.mail_activity_data_call').id,
            'summary': f'Resposta SMS: {sms.phone}',
            'note': f'<p><strong>Cliente respondeu SMS:</strong></p><p>{sms.body}</p>',
            'user_id': user.id,
            'date_deadline': fields.Date.today()
        })
```

---

## 📝 Template System

### Flexible Template Engine

```python
# sms_base_sr/models/sms_template.py
from odoo import models, fields, api
from jinja2 import Template

class SMSTemplate(models.Model):
    _name = 'sms.template'
    _description = 'SMS Template'

    name = fields.Char('Nome', required=True)
    code = fields.Char('Código', required=True)

    # Template content
    message_template = fields.Text(
        'Template da Mensagem',
        required=True,
        help="Use variáveis Jinja2: {{ partner.name }}, {{ campaign.vi_rmi }}, etc."
    )

    # Preview
    message_preview = fields.Text('Preview', compute='_compute_preview')

    # Aplicação
    applies_to = fields.Selection([
        ('res_partner', 'Contatos'),
        ('contacts_realcred', 'Base Realcred'),
        ('crm_lead', 'Oportunidades'),
        ('all', 'Todos')
    ], default='all', required=True)

    # Control
    active = fields.Boolean(default=True)
    admin_only = fields.Boolean('Apenas Admin Pode Editar', default=True)

    @api.depends('message_template')
    def _compute_preview(self):
        """Generate preview with sample data"""
        for template in self:
            try:
                jinja_template = Template(template.message_template)
                preview = jinja_template.render(
                    partner={'name': 'João Silva', 'cpf': '123.456.789-00'},
                    campaign={'vi_rmi': 'R$ 1.500,00'},
                    user={'name': 'Vendedora Ana'}
                )
                template.message_preview = preview
            except Exception as e:
                template.message_preview = f"Erro no template: {e}"

    def render(self, data):
        """Render template with actual data"""
        self.ensure_one()
        jinja_template = Template(self.message_template)
        return jinja_template.render(**data)


# Example templates to create
# data/sms_template_data.xml
"""
<odoo>
    <record id="template_realcred_margem" model="sms.template">
        <field name="name">RealCred - Margem Disponível</field>
        <field name="code">realcred_margem</field>
        <field name="applies_to">contacts_realcred</field>
        <field name="message_template">Ola {{ partner.name }}! Voce tem R$ {{ campaign.margem_disponivel }} disponiveis para emprestimo. Consultor: {{ user.name }}. Ligue: (48) 3333-4444</field>
    </record>

    <record id="template_realcred_oferta" model="sms.template">
        <field name="name">RealCred - Oferta Especial</field>
        <field name="code">realcred_oferta</field>
        <field name="applies_to">contacts_realcred</field>
        <field name="message_template">{{ partner.name }}, oferta exclusiva! Emprestimo de ate {{ campaign.vi_rmi }} com juros reduzidos. Responda SIM para falar com consultor.</field>
    </record>
</odoo>
"""
```

---

## 🧪 Testing Strategy

### Mock Provider for Tests

```python
# sms_base_sr/tests/test_sms_sending.py
from odoo.tests import TransactionCase
from unittest.mock import patch, MagicMock

class TestSMSSending(TransactionCase):

    def setUp(self):
        super().setUp()

        # Create mock provider
        self.provider = self.env['sms.provider'].create({
            'name': 'Mock Provider',
            'provider_type': 'mock'
        })

        # Create test partner
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'phone': '5548991910234'
        })

    @patch('requests.post')
    def test_send_sms_success(self, mock_post):
        """Test successful SMS sending"""

        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'job-123',
            'valids': [{'id': 'msg-456', 'phone': '5548991910234'}]
        }
        mock_post.return_value = mock_response

        # Send SMS
        sms = self.env['sms.message'].create({
            'partner_id': self.partner.id,
            'phone': '5548991910234',
            'body': 'Test message',
            'provider_id': self.provider.id
        })
        sms.send()

        # Assertions
        self.assertEqual(sms.state, 'sent')
        self.assertTrue(sms.kolmeya_message_id)
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_send_sms_rate_limit(self, mock_post):
        """Test rate limit handling"""

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response

        sms = self.env['sms.message'].create({
            'partner_id': self.partner.id,
            'phone': '5548991910234',
            'body': 'Test',
            'provider_id': self.provider.id
        })

        # Should raise exception
        with self.assertRaises(Exception):
            sms.send()

        self.assertEqual(sms.state, 'error')
```

---

## 📈 Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Create `sms_base_sr` module
  - [ ] `sms.message` model
  - [ ] `sms.template` model
  - [ ] `sms.provider` abstract model
  - [ ] Basic webhook controller
  - [ ] Security groups

### Phase 2: Kolmeya Integration (Week 1-2)
- [ ] Create `sms_kolmeya` module
  - [ ] `KolmeyaAPI` wrapper class
  - [ ] `sms.provider.kolmeya` implementation
  - [ ] Webhook handlers (reply + status)
  - [ ] JWT authentication setup
  - [ ] Rate limiting logic

### Phase 3: SempreReal Business Logic (Week 2)
- [ ] Create `contacts_realcred_sms` module
  - [ ] Enhance `contacts.realcred.campaign` with SMS
  - [ ] Integrate job queue
  - [ ] Campaign templates (4 pre-defined)
  - [ ] Batch sending (1000/batch)

### Phase 4: UI/UX (Week 3)
- [ ] SMS tracking in chatter
- [ ] Partner SMS history (smart button)
- [ ] Campaign SMS statistics
- [ ] Activity alerts for replies
- [ ] Dashboard widgets

### Phase 5: Testing & Deployment (Week 3-4)
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests with Kolmeya sandbox
- [ ] Load testing (10K messages)
- [ ] User acceptance testing (vendedoras)
- [ ] Production deployment
- [ ] Monitor webhook reliability

---

## 🎯 Success Metrics

### Technical Metrics
- ✅ **Modularity**: Can swap Kolmeya for Twilio in < 2 hours
- ✅ **Reliability**: 99.5%+ message delivery rate
- ✅ **Performance**: Send 10K messages in < 5 minutes
- ✅ **Security**: 0 unauthorized webhook acceptances
- ✅ **Testability**: 80%+ code coverage

### Business Metrics
- ✅ **Vendedora Efficiency**: Reply alert < 1 minute
- ✅ **Response Rate**: Track SMS → Lead conversion
- ✅ **Cost Tracking**: Monitor R$/SMS per campaign
- ✅ **User Adoption**: 100% vendedoras using SMS in 30 days

---

## 🔐 Security Checklist

Before going to production:

- [ ] JWT secret generated (64+ chars)
- [ ] API token stored in encrypted field (not code)
- [ ] Webhook endpoints CSRF-exempt but JWT-protected
- [ ] Rate limiting configured (500 req/period)
- [ ] IP whitelist verified with Kolmeya
- [ ] HTTPS-only webhook URLs
- [ ] Log all webhook attempts (success + failures)
- [ ] Admin-only template editing
- [ ] Blacklist integration tested
- [ ] LGPD compliance: opt-out mechanism

---

## 📚 Dependencies

### Required Odoo Modules
```python
# sms_base_sr/__manifest__.py
{
    'depends': [
        'base',
        'mail',        # For chatter integration
    ]
}

# sms_kolmeya/__manifest__.py
{
    'depends': [
        'sms_base_sr',
    ]
}

# contacts_realcred_sms/__manifest__.py
{
    'depends': [
        'sms_base_sr',
        'sms_kolmeya',
        'queue_job',           # OCA module
        'contacts_realcred',   # Existing module
    ]
}
```

### Python Packages
```bash
# requirements.txt
PyJWT==2.8.0       # For webhook authentication
requests>=2.31.0   # For HTTP requests
```

---

## 🆚 Architecture Comparison

### Before (Current Approach)

```
User clicks "Send SMS"
    ↓
contacts_realcred.py:check_data_kolmeya_send()
    ↓
Hardcoded API call with token in code
    ↓
Only logs, doesn't actually send
    ↓
No tracking, no retry, no webhook
```

**Issues:**
- ❌ Tight coupling to Kolmeya
- ❌ No error handling
- ❌ No bidirectional communication
- ❌ Token in code (security risk)
- ❌ Blocking operation (timeout risk)

### After (Recommended Approach)

```
User clicks "Send SMS"
    ↓
Campaign.check_data_kolmeya_send()
    ↓
Create async job (queue_job)
    ↓
Job runs in background
    ├─ Create sms.message records
    ├─ Call provider._send_batch()
    │   └─ KolmeyaAPI.send() with token from db
    ├─ Update SMS states
    └─ Log in chatter

Webhook receives reply ← Kolmeya
    ↓
Validate JWT signature
    ↓
Create incoming sms.message
    ↓
Find partner by phone
    ↓
Post in chatter + Create activity
    ↓
Vendedora notified immediately
```

**Benefits:**
- ✅ Non-blocking async operations
- ✅ Automatic retries on failure
- ✅ Secure credential storage
- ✅ Full tracking in chatter
- ✅ Bidirectional communication
- ✅ Provider-agnostic (can add Twilio later)
- ✅ Testable with mocks

---

## 💡 Additional Ideas from Research

### 1. SMS Composer (like Email Composer)

```python
# Similar to mail.compose.message
class SMSComposer(models.TransientModel):
    _name = 'sms.composer'
    _description = 'SMS Composer Wizard'

    partner_ids = fields.Many2many('res.partner', 'Destinatários')
    template_id = fields.Many2one('sms.template', 'Template')
    body = fields.Text('Mensagem', required=True)

    def send_sms(self):
        """Send SMS to selected partners"""
        for partner in self.partner_ids:
            if partner.mobile or partner.phone:
                self.env['sms.message'].create({
                    'partner_id': partner.id,
                    'phone': partner.mobile or partner.phone,
                    'body': self.body,
                    'state': 'outgoing'
                }).send()
```

### 2. SMS Blacklist Management

```python
# Sync Odoo blacklist with Kolmeya
class SMSBlacklist(models.Model):
    _name = 'sms.blacklist'
    _description = 'SMS Blacklist'

    phone = fields.Char('Phone', required=True, index=True)
    active = fields.Boolean(default=True)
    reason = fields.Selection([
        ('optout', 'Opt-out'),
        ('bounce', 'Hard Bounce'),
        ('complaint', 'Reclamação'),
        ('manual', 'Bloqueio Manual')
    ])

    @api.model
    def sync_with_kolmeya(self):
        """Sync blacklist bidirectionally"""
        # Get Kolmeya blacklist
        # Add to local blacklist
        # Push local blacklist to Kolmeya
```

### 3. SMS Campaign Statistics

```python
# Real-time campaign dashboard
class SMSCampaignStats(models.Model):
    _inherit = 'contacts.realcred.campaign'

    sms_sent = fields.Integer(compute='_compute_sms_stats')
    sms_delivered = fields.Integer(compute='_compute_sms_stats')
    sms_replied = fields.Integer(compute='_compute_sms_stats')
    sms_conversion_rate = fields.Float(compute='_compute_sms_stats')

    def _compute_sms_stats(self):
        for campaign in self:
            messages = self.env['sms.message'].search([
                ('campaign_id', '=', campaign.id)
            ])
            campaign.sms_sent = len(messages.filtered(lambda m: m.state == 'sent'))
            campaign.sms_delivered = len(messages.filtered(lambda m: m.state == 'delivered'))

            replies = messages.filtered(lambda m: m.direction == 'incoming')
            campaign.sms_replied = len(replies)
            campaign.sms_conversion_rate = (len(replies) / len(messages) * 100) if messages else 0
```

### 4. Cost Tracking

```python
# Track SMS costs per campaign
class SMSMessage(models.Model):
    _inherit = 'sms.message'

    cost = fields.Float('Custo (R$)', default=0.10)  # R$ 0.10 per SMS

class ContactsRealcredCampaign(models.Model):
    _inherit = 'contacts.realcred.campaign'

    sms_total_cost = fields.Float('Custo Total SMS', compute='_compute_sms_cost')

    def _compute_sms_cost(self):
        for campaign in self:
            messages = self.env['sms.message'].search([('campaign_id', '=', campaign.id)])
            campaign.sms_total_cost = sum(messages.mapped('cost'))
```

---

## 🎓 Key Learnings from OCA

### 1. From base_sms_client
- **Lesson**: Provider abstraction layer makes switching easy
- **Implementation**: Create `sms.provider` abstract model

### 2. From GatewayAPI SMS
- **Lesson**: JWT webhooks prevent unauthorized access
- **Implementation**: Validate signature on all webhook endpoints

### 3. From queue_job
- **Lesson**: Retry patterns handle transient failures
- **Implementation**: Use `@job` decorator with retry_pattern

### 4. From mail_tracking
- **Lesson**: Users love seeing communication history in one place
- **Implementation**: Integrate SMS with chatter using message_post

### 5. From Twilio Integration
- **Lesson**: Modular architecture (base + provider + business)
- **Implementation**: 3 separate modules (sms_base_sr, sms_kolmeya, contacts_realcred_sms)

---

## ✅ Final Recommendations

### DO ✅

1. **Modular Design**: 3 modules (base → provider → business)
2. **Async Processing**: Use queue_job for all sends
3. **Secure Webhooks**: JWT authentication mandatory
4. **Chatter Integration**: All SMS visible in partner history
5. **Testing**: 80%+ coverage before production
6. **Provider Abstraction**: Design for multiple providers from day 1
7. **Activity Alerts**: Immediate notification on replies
8. **Rate Limiting**: Built-in protection against API limits

### DON'T ❌

1. **Don't hardcode tokens**: Use encrypted database fields
2. **Don't block UI**: Always use async jobs for sending
3. **Don't skip webhooks**: Required for bidirectional communication
4. **Don't ignore rate limits**: Monitor X-RateLimit-Remaining header
5. **Don't store credentials in code**: Security vulnerability
6. **Don't send without tracking**: Every SMS = sms.message record
7. **Don't forget LGPD**: Implement opt-out mechanism
8. **Don't skip testing**: Mock providers for unit tests

---

## 📞 Next Steps

1. **Review this document** with team
2. **Decide on architecture**: Modular vs. Monolithic
3. **Plan sprints**: 4-week implementation
4. **Setup development environment**: Install queue_job
5. **Create module structure**: sms_base_sr + sms_kolmeya
6. **Start coding**: Begin with Phase 1 (Foundation)

---

**Document Created:** 2025-11-15
**Author:** Claude Code
**Based On:** OCA connector-telephony, GatewayAPI SMS, Twilio, queue_job, mail_tracking
**Status:** Ready for Implementation

**Remember:** Good architecture pays for itself in maintainability, testability, and future flexibility. The modular approach may take 20% longer to build but will save 200% time in maintenance and extensions.
