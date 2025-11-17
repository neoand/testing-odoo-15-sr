# Resumo Executivo - Análise Sistema SMS Odoo 15

**Data:** 16/11/2025
**Objetivo:** Guia rápido para refatoração do chatroom_sms_advanced

---

## 1. O QUE FOI DESCOBERTO

### Sistema SMS Existente (3 módulos em produção):

#### sms_base_sr (BASE)
- Modelos: `sms.message`, `sms.provider`, `sms.template`, `res.partner` (extend)
- Wizard: `sms.compose`
- Funcionalidade: Core do sistema SMS

#### sms_kolmeya (PROVIDER)
- Classe: `KolmeyaAPI` (wrapper completo da API)
- Extend: `sms.provider` (adiciona type='kolmeya')
- Webhooks: `/kolmeya/webhook/reply`, `/kolmeya/webhook/status`

#### contact_center_sms (CHATROOM)
- Extend: `acrux.chat.connector`, `acrux.chat.conversation`, `acrux.chat.message`
- Feature: Integra SMS ao ChatRoom WhatsApp
- Campo chave: `channel_type` = 'sms' | 'whatsapp' | 'instagram'

---

## 2. O QUE ESTÁ ERRADO NO NOSSO MÓDULO

### Problemas Críticos:

1. **Modelos Duplicados** (80% do código!)
   - `chatroom.sms.log` → JÁ EXISTE `sms.message`
   - `chatroom.sms.api` → JÁ EXISTE `KolmeyaAPI`
   - `chatroom.sms.template` → JÁ EXISTE `sms.template`

2. **Dependências Erradas**
   ```python
   # ERRADO (atual)
   'depends': ['base', 'web', 'mail', 'chatroom']

   # CORRETO (novo)
   'depends': ['sms_base_sr', 'sms_kolmeya', 'contact_center_sms']
   ```

3. **Webhooks Duplicados**
   - Nossos endpoints conflitam com os existentes
   - Webhooks JÁ funcionam no contact_center_sms

4. **Não usa ChatRoom**
   - Criamos sistema paralelo
   - ChatRoom JÁ tem integração SMS via `acrux.chat.conversation`

---

## 3. AÇÃO IMEDIATA NECESSÁRIA

### O QUE FAZER:

#### FASE 1: REMOVER (Duplicatas)

**Excluir estes modelos:**
```python
# models/chatroom_sms_log.py → DELETAR
# models/chatroom_sms_api.py → DELETAR
# models/chatroom_sms_template.py → DELETAR (se existir)
# models/chatroom_room.py → DELETAR
# controllers/webhook_kolmeya.py → DELETAR
```

**Excluir estas views:**
```xml
# views/chatroom_sms_log_views.xml → DELETAR
# views/chatroom_sms_template_views.xml → DELETAR (se existir)
# views/chatroom_room_views.xml → DELETAR
```

---

#### FASE 2: ATUALIZAR (__manifest__.py)

```python
{
    'name': 'ChatRoom SMS Advanced',
    'version': '15.0.2.0.0',  # INCREMENTAR versão
    'depends': [
        'sms_base_sr',           # Base SMS
        'sms_kolmeya',           # Provider
        'contact_center_sms',    # ChatRoom Integration
    ],
    'data': [
        'security/ir.model.access.csv',

        # NOVOS modelos (não duplicados)
        'views/sms_message_advanced_views.xml',      # Extend sms.message
        'views/sms_provider_advanced_views.xml',     # Extend sms.provider
        'views/chatroom_conversation_sms_views.xml', # Extend acrux.chat.conversation

        # Features NOVAS
        'views/chatroom_sms_scheduled_views.xml',    # NOVO
        'views/chatroom_sms_campaign_views.xml',     # NOVO
        'views/chatroom_sms_dashboard_views.xml',    # NOVO
        'views/chatroom_sms_blacklist_views.xml',    # NOVO

        # Wizards (adaptados)
        'wizard/chatroom_send_bulk_sms_views.xml',   # Adaptar para usar sms.message

        # Crons
        'data/cron_sms_balance.xml',
        'data/cron_sms_scheduled.xml',
        'data/cron_sync_blacklist.xml',

        'views/menus.xml',
    ],
}
```

---

#### FASE 3: CRIAR _inherit (Estender modelos existentes)

**models/sms_message_advanced.py** (NOVO)
```python
from odoo import models, fields, api

class SMSMessage(models.Model):
    _inherit = 'sms.message'

    # Agendamento
    scheduled_date = fields.Datetime('Scheduled Date')
    is_scheduled = fields.Boolean('Scheduled', compute='_compute_is_scheduled', store=True)

    # Campanha
    campaign_id = fields.Many2one('chatroom.sms.campaign', 'Campaign')

    # Link tracking
    link_tracking_ids = fields.One2many('chatroom.sms.link.tracking', 'sms_id')

    # Blacklist
    blacklist_reason = fields.Selection([
        ('user_request', 'User Request'),
        ('auto_bounce', 'Auto Bounce'),
        ('manual', 'Manual'),
    ])

    @api.depends('scheduled_date')
    def _compute_is_scheduled(self):
        now = fields.Datetime.now()
        for rec in self:
            rec.is_scheduled = bool(rec.scheduled_date and rec.scheduled_date > now)
```

**models/sms_provider_advanced.py** (NOVO)
```python
from odoo import models, fields

class SMSProvider(models.Model):
    _inherit = 'sms.provider'

    # Auto-consulta saldo
    auto_balance_check = fields.Boolean('Auto Check Balance', default=True)
    balance_check_interval = fields.Integer('Check Interval (hours)', default=6)
    balance_alert_threshold = fields.Float('Alert Threshold (R$)', default=100.0)
    balance_alert_user_ids = fields.Many2many('res.users', string='Alert Users')

    # DND (Do Not Disturb)
    dnd_enabled = fields.Boolean('Enable DND', default=True)
    dnd_start_hour = fields.Integer('DND Start Hour', default=22)
    dnd_end_hour = fields.Integer('DND End Hour', default=8)

    # Webhook customizado
    webhook_url_custom = fields.Char('Custom Webhook URL')
```

**models/chatroom_conversation_sms.py** (NOVO)
```python
from odoo import models, fields

class AcruxChatConversation(models.Model):
    _inherit = 'acrux.chat.conversation'

    # Stats SMS
    sms_last_sent = fields.Datetime('Last SMS Sent')
    sms_last_received = fields.Datetime('Last SMS Received')
    sms_delivery_rate = fields.Float('Delivery Rate %', compute='_compute_sms_stats')

    # Tags
    sms_tag_ids = fields.Many2many('chatroom.sms.tag', string='SMS Tags')

    # Priority
    is_priority = fields.Boolean('Priority Conversation')

    def action_schedule_sms(self):
        """Abre wizard agendamento"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'chatroom.sms.schedule.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_conversation_id': self.id}
        }
```

---

#### FASE 4: CRIAR MODELOS NOVOS (Features que NÃO existem)

**models/chatroom_sms_scheduled.py** (NOVO)
```python
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ChatroomSMSScheduled(models.Model):
    _name = 'chatroom.sms.scheduled'
    _description = 'Scheduled SMS Messages'
    _order = 'scheduled_date'

    name = fields.Char('Description', required=True)
    sms_message_id = fields.Many2one('sms.message', 'SMS Message', required=True)
    scheduled_date = fields.Datetime('Scheduled Date', required=True, index=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ], default='pending', required=True, index=True)

    # Recorrência
    is_recurring = fields.Boolean('Recurring')
    recurrence_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ])
    recurrence_interval = fields.Integer('Interval', default=1)

    def cron_send_scheduled_sms(self):
        """Cron: envia SMS agendados (executa a cada 5 min)"""
        pending = self.search([
            ('state', '=', 'pending'),
            ('scheduled_date', '<=', fields.Datetime.now()),
        ])

        for scheduled in pending:
            try:
                scheduled.sms_message_id.action_send()
                scheduled.state = 'sent'

                # Cria próxima recorrência se necessário
                if scheduled.is_recurring:
                    scheduled._create_next_recurrence()

            except Exception as e:
                scheduled.state = 'failed'
                _logger.error(f"Failed to send scheduled SMS {scheduled.id}: {e}")

    def _create_next_recurrence(self):
        """Cria próxima ocorrência agendada"""
        self.ensure_one()

        if not self.is_recurring:
            return

        # Calcula próxima data
        from dateutil.relativedelta import relativedelta

        next_date = self.scheduled_date
        if self.recurrence_type == 'daily':
            next_date += relativedelta(days=self.recurrence_interval)
        elif self.recurrence_type == 'weekly':
            next_date += relativedelta(weeks=self.recurrence_interval)
        elif self.recurrence_type == 'monthly':
            next_date += relativedelta(months=self.recurrence_interval)

        # Cria novo SMS
        new_sms = self.sms_message_id.copy({'scheduled_date': next_date})

        # Cria novo agendamento
        self.create({
            'name': self.name,
            'sms_message_id': new_sms.id,
            'scheduled_date': next_date,
            'is_recurring': True,
            'recurrence_type': self.recurrence_type,
            'recurrence_interval': self.recurrence_interval,
        })
```

**models/chatroom_sms_campaign.py** (NOVO)
```python
from odoo import models, fields, api

class ChatroomSMSCampaign(models.Model):
    _name = 'chatroom.sms.campaign'
    _description = 'SMS Campaigns'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Campaign Name', required=True, tracking=True)
    description = fields.Text('Description')

    # Target
    partner_ids = fields.Many2many('res.partner', string='Recipients')
    domain_filter = fields.Char('Domain Filter', help='Ex: [("customer_rank", ">", 0)]')

    # Template
    template_id = fields.Many2one('sms.template', 'Template', required=True)

    # Provider
    provider_id = fields.Many2one('sms.provider', 'SMS Provider',
                                 default=lambda self: self.env['sms.provider'].search([('provider_type', '=', 'kolmeya')], limit=1))

    # Stats
    sms_message_ids = fields.One2many('sms.message', 'campaign_id', string='SMS Messages')
    total_sent = fields.Integer('Total Sent', compute='_compute_stats', store=True)
    total_delivered = fields.Integer('Total Delivered', compute='_compute_stats', store=True)
    total_failed = fields.Integer('Total Failed', compute='_compute_stats', store=True)
    delivery_rate = fields.Float('Delivery Rate %', compute='_compute_stats', store=True)
    total_cost = fields.Float('Total Cost (R$)', compute='_compute_stats', store=True)

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('canceled', 'Canceled'),
    ], default='draft', required=True, tracking=True)

    @api.depends('sms_message_ids.state', 'sms_message_ids.cost')
    def _compute_stats(self):
        for campaign in self:
            messages = campaign.sms_message_ids
            campaign.total_sent = len(messages.filtered(lambda m: m.state in ['sent', 'delivered']))
            campaign.total_delivered = len(messages.filtered(lambda m: m.state == 'delivered'))
            campaign.total_failed = len(messages.filtered(lambda m: m.state in ['error', 'rejected']))
            campaign.delivery_rate = (campaign.total_delivered / campaign.total_sent * 100) if campaign.total_sent else 0
            campaign.total_cost = sum(messages.mapped('cost'))

    def action_start_campaign(self):
        """Inicia campanha - envia SMS para todos recipients"""
        self.ensure_one()

        # Aplica domain filter se fornecido
        partners = self.partner_ids
        if self.domain_filter:
            try:
                domain = eval(self.domain_filter)
                partners = self.env['res.partner'].search(domain)
            except Exception as e:
                raise UserError(f"Invalid domain filter: {e}")

        # Cria e envia SMS para cada partner
        created_count = 0
        for partner in partners:
            phone = partner.mobile or partner.phone
            if not phone:
                continue

            # Renderiza template
            body = self.template_id.render({
                'name': partner.name,
                'phone': phone,
            })

            # Cria SMS
            sms = self.env['sms.message'].create({
                'partner_id': partner.id,
                'phone': phone,
                'body': body,
                'campaign_id': self.id,
                'provider_id': self.provider_id.id,
            })

            # Envia
            sms.action_send()
            created_count += 1

        self.state = 'running'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Campaign Started',
                'message': f'{created_count} SMS messages sent!',
                'type': 'success',
            }
        }

    def action_mark_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'canceled'
```

**models/chatroom_sms_blacklist.py** (NOVO)
```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ChatroomSMSBlacklist(models.Model):
    _name = 'chatroom.sms.blacklist'
    _description = 'SMS Blacklist (Do Not Disturb)'
    _order = 'added_date DESC'

    phone = fields.Char('Phone Number', required=True, index=True)
    partner_id = fields.Many2one('res.partner', 'Partner', index=True)

    reason = fields.Selection([
        ('user_request', 'User Request'),
        ('auto_bounce', 'Auto Bounce'),
        ('manual', 'Manual'),
        ('legal', 'Legal Requirement'),
    ], required=True, default='manual')

    notes = fields.Text('Notes')

    added_date = fields.Datetime('Added Date', default=fields.Datetime.now, readonly=True)
    added_by = fields.Many2one('res.users', 'Added By', default=lambda self: self.env.user, readonly=True)

    synced_kolmeya = fields.Boolean('Synced with Kolmeya', default=False, readonly=True)
    last_sync_date = fields.Datetime('Last Sync Date', readonly=True)

    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('phone_unique', 'unique(phone)', 'Phone number already in blacklist!')
    ]

    @api.model
    def create(self, vals):
        """Ao criar, já marca para sync"""
        record = super().create(vals)

        # Auto-sync se provider configurado
        if self.env['sms.provider'].search([('provider_type', '=', 'kolmeya')], limit=1):
            record.sync_to_kolmeya()

        return record

    def sync_to_kolmeya(self):
        """Sincroniza blacklist local com Kolmeya"""
        provider = self.env['sms.provider'].search([('provider_type', '=', 'kolmeya')], limit=1)
        if not provider:
            _logger.warning("No Kolmeya provider found for blacklist sync")
            return

        from odoo.addons.sms_kolmeya.models.kolmeya_api import KolmeyaAPI

        try:
            api = KolmeyaAPI(provider.kolmeya_api_token, provider.kolmeya_segment_id)

            phones_to_sync = self.filtered(lambda b: not b.synced_kolmeya and b.active)
            if not phones_to_sync:
                return

            phone_list = [b.phone for b in phones_to_sync]

            # Adiciona à blacklist Kolmeya
            result = api.add_to_blacklist(phone_list)

            # Marca como sincronizado
            phones_to_sync.write({
                'synced_kolmeya': True,
                'last_sync_date': fields.Datetime.now(),
            })

            _logger.info(f"Synced {len(phone_list)} phones to Kolmeya blacklist")

        except Exception as e:
            _logger.error(f"Error syncing blacklist to Kolmeya: {e}")
            raise

    def action_remove_from_blacklist(self):
        """Remove da blacklist (local e Kolmeya)"""
        self.ensure_one()

        provider = self.env['sms.provider'].search([('provider_type', '=', 'kolmeya')], limit=1)
        if provider and self.synced_kolmeya:
            from odoo.addons.sms_kolmeya.models.kolmeya_api import KolmeyaAPI
            api = KolmeyaAPI(provider.kolmeya_api_token, provider.kolmeya_segment_id)
            api.remove_from_blacklist([self.phone])

        self.active = False

    @api.model
    def cron_sync_blacklist(self):
        """Cron: sincroniza blacklist não sincronizada"""
        to_sync = self.search([('synced_kolmeya', '=', False), ('active', '=', True)])
        if to_sync:
            to_sync.sync_to_kolmeya()
```

**models/chatroom_sms_dashboard.py** (NOVO)
```python
from odoo import models, fields, tools

class ChatroomSMSDashboard(models.Model):
    _name = 'chatroom.sms.dashboard'
    _description = 'SMS Dashboard Statistics'
    _auto = False  # SQL View
    _order = 'date DESC'

    date = fields.Date('Date', readonly=True)
    provider_id = fields.Many2one('sms.provider', 'Provider', readonly=True)

    total_sent = fields.Integer('Total Sent', readonly=True)
    total_delivered = fields.Integer('Total Delivered', readonly=True)
    total_failed = fields.Integer('Total Failed', readonly=True)
    total_pending = fields.Integer('Total Pending', readonly=True)

    delivery_rate = fields.Float('Delivery Rate %', readonly=True)
    failure_rate = fields.Float('Failure Rate %', readonly=True)

    total_cost = fields.Float('Total Cost (R$)', readonly=True)
    avg_cost_per_sms = fields.Float('Avg Cost per SMS', readonly=True)

    total_segments = fields.Integer('Total SMS Segments', readonly=True)

    def init(self):
        """Cria SQL view para estatísticas"""
        tools.drop_view_if_exists(self.env.cr, 'chatroom_sms_dashboard')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW chatroom_sms_dashboard AS (
                SELECT
                    ROW_NUMBER() OVER (ORDER BY DATE(sent_date) DESC, provider_id) as id,
                    DATE(sent_date) as date,
                    provider_id,

                    COUNT(*) as total_sent,
                    SUM(CASE WHEN state = 'delivered' THEN 1 ELSE 0 END) as total_delivered,
                    SUM(CASE WHEN state IN ('error', 'rejected', 'expired') THEN 1 ELSE 0 END) as total_failed,
                    SUM(CASE WHEN state IN ('draft', 'outgoing', 'sent') THEN 1 ELSE 0 END) as total_pending,

                    ROUND(
                        CAST(SUM(CASE WHEN state = 'delivered' THEN 1 ELSE 0 END) AS NUMERIC) /
                        NULLIF(COUNT(*), 0) * 100,
                        2
                    ) as delivery_rate,

                    ROUND(
                        CAST(SUM(CASE WHEN state IN ('error', 'rejected') THEN 1 ELSE 0 END) AS NUMERIC) /
                        NULLIF(COUNT(*), 0) * 100,
                        2
                    ) as failure_rate,

                    SUM(cost) as total_cost,
                    AVG(cost) as avg_cost_per_sms,
                    SUM(sms_count) as total_segments

                FROM sms_message
                WHERE sent_date IS NOT NULL
                GROUP BY DATE(sent_date), provider_id
            )
        """)
```

---

#### FASE 5: ADAPTAR WIZARDS

**wizard/chatroom_send_bulk_sms.py** (ADAPTAR)
```python
from odoo import models, fields, api
from odoo.exceptions import UserError

class ChatroomSendBulkSMS(models.TransientModel):
    _name = 'chatroom.send.bulk.sms'
    _description = 'Send Bulk SMS Wizard'

    # Seleção
    selection_type = fields.Selection([
        ('manual', 'Manual Selection'),
        ('domain', 'Domain Filter'),
        ('campaign', 'From Campaign'),
    ], default='manual', required=True)

    partner_ids = fields.Many2many('res.partner', string='Recipients')
    domain_filter = fields.Char('Domain Filter')
    campaign_id = fields.Many2one('chatroom.sms.campaign', 'Campaign')

    # Mensagem
    template_id = fields.Many2one('sms.template', 'Template')  # USA sms.template!
    body = fields.Text('Message', required=True)

    # Provider
    provider_id = fields.Many2one('sms.provider', 'SMS Provider', required=True,
                                 default=lambda self: self.env['sms.provider'].search([('provider_type', '=', 'kolmeya')], limit=1))

    # Agendamento
    send_now = fields.Boolean('Send Now', default=True)
    scheduled_date = fields.Datetime('Schedule Date')

    # Stats
    total_recipients = fields.Integer('Total Recipients', compute='_compute_stats')
    estimated_cost = fields.Float('Estimated Cost (R$)', compute='_compute_stats')

    @api.depends('partner_ids', 'body')
    def _compute_stats(self):
        for wizard in self:
            wizard.total_recipients = len(wizard.partner_ids)

            # Estima custo (R$ 0.10 por 160 chars)
            char_count = len(wizard.body or '')
            segments = (char_count // 160) + (1 if char_count % 160 else 0) if char_count else 0
            wizard.estimated_cost = wizard.total_recipients * segments * 0.10

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            # Preview com primeiro partner
            if self.partner_ids:
                partner = self.partner_ids[0]
                self.body = self.template_id.render({
                    'name': partner.name,
                    'phone': partner.mobile or partner.phone,
                })
            else:
                self.body = self.template_id.message_template

    def action_send_bulk(self):
        """Envia SMS em lote usando sms.message"""
        self.ensure_one()

        if not self.partner_ids:
            raise UserError("No recipients selected!")

        # Lista de SMS criados
        sms_messages = self.env['sms.message']

        for partner in self.partner_ids:
            phone = partner.mobile or partner.phone
            if not phone:
                continue

            # Renderiza template para cada partner
            if self.template_id:
                body = self.template_id.render({
                    'name': partner.name,
                    'phone': phone,
                })
            else:
                body = self.body

            # Cria SMS usando sms.message existente!
            sms = self.env['sms.message'].create({
                'partner_id': partner.id,
                'phone': phone,
                'body': body,
                'provider_id': self.provider_id.id,
                'campaign_id': self.campaign_id.id if self.campaign_id else False,
                'scheduled_date': self.scheduled_date if not self.send_now else False,
            })

            sms_messages |= sms

        # Envia agora ou agenda
        if self.send_now:
            # Envia todos
            for sms in sms_messages:
                sms.action_send()
        else:
            # Cria agendamentos
            for sms in sms_messages:
                self.env['chatroom.sms.scheduled'].create({
                    'name': f"Bulk SMS - {sms.partner_id.name}",
                    'sms_message_id': sms.id,
                    'scheduled_date': self.scheduled_date,
                })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Bulk SMS',
                'message': f'{len(sms_messages)} SMS {"sent" if self.send_now else "scheduled"}!',
                'type': 'success',
            }
        }
```

---

## 4. CHECKLIST DE MIGRAÇÃO

### Preparação:
- [ ] Backup completo do módulo atual
- [ ] Criar branch Git: `refactor/chatroom_sms_advanced_v2`
- [ ] Documentar todos arquivos atuais

### Remover Duplicatas:
- [ ] Deletar `models/chatroom_sms_log.py`
- [ ] Deletar `models/chatroom_sms_api.py`
- [ ] Deletar `models/chatroom_room.py`
- [ ] Deletar `controllers/webhook_kolmeya.py`
- [ ] Deletar views relacionadas

### Atualizar Manifest:
- [ ] Alterar depends para `['sms_base_sr', 'sms_kolmeya', 'contact_center_sms']`
- [ ] Atualizar lista de data files
- [ ] Incrementar versão para 15.0.2.0.0

### Criar _inherit:
- [ ] `models/sms_message_advanced.py`
- [ ] `models/sms_provider_advanced.py`
- [ ] `models/chatroom_conversation_sms.py`

### Criar Modelos Novos:
- [ ] `models/chatroom_sms_scheduled.py`
- [ ] `models/chatroom_sms_campaign.py`
- [ ] `models/chatroom_sms_blacklist.py`
- [ ] `models/chatroom_sms_dashboard.py`

### Adaptar Wizards:
- [ ] Atualizar `wizard/chatroom_send_bulk_sms.py` para usar `sms.message`
- [ ] Criar `wizard/chatroom_sms_schedule_wizard.py`

### Criar Views:
- [ ] `views/sms_message_advanced_views.xml` (form inherit)
- [ ] `views/sms_provider_advanced_views.xml` (form inherit)
- [ ] `views/chatroom_sms_scheduled_views.xml`
- [ ] `views/chatroom_sms_campaign_views.xml`
- [ ] `views/chatroom_sms_blacklist_views.xml`
- [ ] `views/chatroom_sms_dashboard_views.xml` (kanban/graph)

### Criar Crons:
- [ ] `data/cron_sms_balance.xml` (check balance a cada 6h)
- [ ] `data/cron_sms_scheduled.xml` (envia agendados a cada 5min)
- [ ] `data/cron_sync_blacklist.xml` (sync blacklist a cada 1h)

### Security:
- [ ] Atualizar `security/ir.model.access.csv`
- [ ] Atualizar `security/sms_security.xml`

### Testes:
- [ ] Teste: criar SMS agendado
- [ ] Teste: criar campanha
- [ ] Teste: envio em lote
- [ ] Teste: blacklist sync
- [ ] Teste: dashboard stats
- [ ] Teste: integração ChatRoom

---

## 5. PRIORIDADES

### PRIORIDADE ALTA (Fazer Primeiro):

1. **Remover duplicatas** - Evitar conflitos
2. **Atualizar __manifest__.py** - Dependências corretas
3. **Criar _inherit básicos** - Funcionalidade mínima
4. **Adaptar wizard bulk send** - Feature mais usada

### PRIORIDADE MÉDIA:

5. **Modelo scheduled** - Agendamento
6. **Modelo campaign** - Campanhas
7. **Dashboard** - Visualização
8. **Crons** - Automação

### PRIORIDADE BAIXA:

9. **Blacklist management** - Feature extra
10. **Link tracking** - Analytics avançado
11. **Reports customizados** - Extras

---

## 6. COMANDOS SSH ÚTEIS

```bash
# Ver estrutura SMS base
ssh odoo-rc "ls -la /odoo/custom/addons_custom/sms_base_sr/models/"

# Ver KolmeyaAPI
ssh odoo-rc "cat /odoo/custom/addons_custom/sms_kolmeya/models/kolmeya_api.py | grep 'def '"

# Ver modelos contact_center
ssh odoo-rc "ls -la /odoo/custom/addons_custom/contact_center_sms/models/"

# Testar conexão Kolmeya
ssh odoo-rc "cd /odoo && python3 -c 'from addons.sms_kolmeya.models.kolmeya_api import KolmeyaAPI; api = KolmeyaAPI(\"Bearer TOKEN\", 109); print(api.get_balance())'"
```

---

## 7. NEXT STEPS (AGORA!)

### Passo 1: Criar branch
```bash
cd /Users/andersongoliveira/odoo_15_sr/
git checkout -b refactor/chatroom_sms_advanced_v2
```

### Passo 2: Backup
```bash
cp -r chatroom_sms_advanced chatroom_sms_advanced.BACKUP
```

### Passo 3: Iniciar refatoração
1. Atualizar `__manifest__.py`
2. Remover arquivos duplicados
3. Criar primeiro `_inherit` (sms_message_advanced.py)
4. Testar instalação

### Passo 4: Incrementar
- Adicionar features uma por vez
- Testar cada adição
- Commit frequente

---

## CONCLUSÃO

**Tempo estimado:** 10-15 dias de trabalho

**Benefícios:**
- Elimina duplicação de código (80% redução)
- Integração completa com ChatRoom
- Usa infraestrutura testada (sms_base_sr + sms_kolmeya)
- Adiciona features realmente novas
- Manutenção mais fácil

**Riscos:**
- Refatoração grande
- Possível quebra de funcionalidade atual
- Necessário testes extensivos

**Mitigação:**
- Backup completo antes
- Branch separado
- Testes incrementais
- Deploy staging primeiro

---

**FIM DO RESUMO EXECUTIVO**
