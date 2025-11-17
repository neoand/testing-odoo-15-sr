# Plano de Ação - Refatoração chatroom_sms_advanced

**Data:** 16/11/2025
**Objetivo:** Guia passo-a-passo para refatorar o módulo

---

## DIA 1: PREPARAÇÃO E BACKUP

### Manhã (2-3h)

#### 1.1 Backup Completo
```bash
cd /Users/andersongoliveira/odoo_15_sr/

# Backup local
cp -r chatroom_sms_advanced chatroom_sms_advanced.BACKUP_$(date +%Y%m%d)

# Commit estado atual
git add chatroom_sms_advanced/
git commit -m "Backup: estado antes da refatoração v2"

# Criar branch
git checkout -b refactor/chatroom_sms_advanced_v2
```

#### 1.2 Documentar Estado Atual
```bash
# Lista todos arquivos
find chatroom_sms_advanced/ -type f -name "*.py" > ARQUIVOS_ANTES.txt
find chatroom_sms_advanced/ -type f -name "*.xml" >> ARQUIVOS_ANTES.txt

# Conta linhas de código
wc -l chatroom_sms_advanced/models/*.py > LINHAS_ANTES.txt
```

#### 1.3 Backup Servidor (SSH)
```bash
# Conectar ao servidor
ssh odoo-rc

# Backup do módulo atual
cd /odoo/custom/addons_custom/
sudo cp -r chatroom_sms_advanced chatroom_sms_advanced.BACKUP_20251116

# Backup BD (opcional)
sudo -u postgres pg_dump odoo_15 > /tmp/odoo_15_backup_20251116.sql

exit
```

### Tarde (3-4h)

#### 1.4 Estudar Código Existente
- [ ] Ler TODOS os modelos atuais
- [ ] Mapear dependências entre arquivos
- [ ] Identificar funcionalidades únicas
- [ ] Listar campos customizados

#### 1.5 Criar Plano Detalhado
- [ ] Listar arquivos a DELETAR
- [ ] Listar arquivos a CRIAR
- [ ] Listar arquivos a ADAPTAR
- [ ] Definir ordem de implementação

---

## DIA 2: LIMPEZA E MANIFEST

### Manhã (3-4h)

#### 2.1 Atualizar __manifest__.py

**ANTES:**
```python
{
    'name': 'ChatRoom SMS Advanced',
    'version': '15.0.1.0.0',
    'depends': ['base', 'web', 'mail', 'chatroom'],
    # ...
}
```

**DEPOIS:**
```python
{
    'name': 'ChatRoom SMS Advanced',
    'version': '15.0.2.0.0',  # INCREMENTAR
    'depends': [
        'sms_base_sr',           # Base SMS
        'sms_kolmeya',           # Provider Kolmeya
        'contact_center_sms',    # ChatRoom Integration
    ],
    'data': [
        # Security
        'security/sms_security.xml',
        'security/ir.model.access.csv',

        # Views - Inherit (estender modelos existentes)
        'views/sms_message_advanced_views.xml',
        'views/sms_provider_advanced_views.xml',
        'views/chatroom_conversation_sms_views.xml',

        # Views - Novos modelos
        'views/chatroom_sms_scheduled_views.xml',
        'views/chatroom_sms_campaign_views.xml',
        'views/chatroom_sms_blacklist_views.xml',
        'views/chatroom_sms_dashboard_views.xml',

        # Wizards
        'wizard/chatroom_send_bulk_sms_views.xml',
        'wizard/chatroom_sms_schedule_wizard_views.xml',

        # Data
        'data/cron_sms_balance.xml',
        'data/cron_sms_scheduled.xml',
        'data/cron_sync_blacklist.xml',

        # Menus
        'views/menus.xml',
    ],
    'external_dependencies': {
        'python': ['dateutil'],
    },
}
```

#### 2.2 Deletar Arquivos Duplicados

```bash
cd chatroom_sms_advanced/

# Deletar modelos duplicados
rm models/chatroom_sms_log.py
rm models/chatroom_sms_api.py
rm models/chatroom_room.py

# Deletar controllers duplicados
rm controllers/webhook_kolmeya.py

# Deletar views duplicadas
rm views/chatroom_sms_log_views.xml
rm views/chatroom_room_views.xml

# Commit mudanças
git add -A
git commit -m "refactor: remove modelos duplicados"
```

### Tarde (3-4h)

#### 2.3 Atualizar models/__init__.py

**ANTES:**
```python
from . import chatroom_sms_log
from . import chatroom_sms_api
from . import chatroom_room
from . import chatroom_conversation
# ...
```

**DEPOIS:**
```python
# Inherit (estende modelos existentes)
from . import sms_message_advanced
from . import sms_provider_advanced
from . import chatroom_conversation_sms

# Novos modelos
from . import chatroom_sms_scheduled
from . import chatroom_sms_campaign
from . import chatroom_sms_blacklist
from . import chatroom_sms_dashboard
from . import chatroom_sms_tag
```

#### 2.4 Atualizar controllers/__init__.py

```python
# Apenas se houver controllers customizados
# Remover imports de webhook_kolmeya
```

#### 2.5 Teste Básico

```bash
# No servidor
ssh odoo-rc

cd /odoo
sudo -u odoo ./odoo-bin -c odoo.conf -d test_db --stop-after-init --log-level=warn

# Verificar se módulos base carregam
# Não deve ter erros de import
```

---

## DIA 3: CRIAR _INHERIT (SMS.MESSAGE)

### Manhã (4-5h)

#### 3.1 Criar models/sms_message_advanced.py

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class SMSMessage(models.Model):
    _inherit = 'sms.message'

    # ========== AGENDAMENTO ==========
    scheduled_date = fields.Datetime(
        'Scheduled Date',
        help='When this SMS should be sent (if scheduled)'
    )
    is_scheduled = fields.Boolean(
        'Is Scheduled',
        compute='_compute_is_scheduled',
        store=True,
        help='True if SMS is scheduled for future sending'
    )

    # ========== CAMPANHA ==========
    campaign_id = fields.Many2one(
        'chatroom.sms.campaign',
        'Campaign',
        ondelete='set null',
        index=True,
        help='Campaign this SMS belongs to'
    )

    # ========== LINK TRACKING ==========
    link_tracking_ids = fields.One2many(
        'chatroom.sms.link.tracking',
        'sms_id',
        string='Link Clicks'
    )
    link_clicks = fields.Integer(
        'Link Clicks',
        compute='_compute_link_clicks',
        store=True
    )

    # ========== BLACKLIST ==========
    blacklist_reason = fields.Selection([
        ('user_request', 'User Request'),
        ('auto_bounce', 'Auto Bounce'),
        ('manual', 'Manual'),
        ('legal', 'Legal Requirement'),
    ], string='Blacklist Reason')

    # ========== TAGS ==========
    tag_ids = fields.Many2many(
        'chatroom.sms.tag',
        string='Tags',
        help='Tags for categorization'
    )

    # ========== PRIORITY ==========
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'High'),
    ], default='0', string='Priority')

    # ========== COMPUTED FIELDS ==========

    @api.depends('scheduled_date')
    def _compute_is_scheduled(self):
        """Marca como agendado se data futura"""
        now = fields.Datetime.now()
        for rec in self:
            rec.is_scheduled = bool(
                rec.scheduled_date and
                rec.scheduled_date > now and
                rec.state in ['draft', 'outgoing']
            )

    @api.depends('link_tracking_ids')
    def _compute_link_clicks(self):
        """Conta cliques em links"""
        for rec in self:
            rec.link_clicks = len(rec.link_tracking_ids)

    # ========== ACTIONS ==========

    def action_schedule(self):
        """Abre wizard de agendamento"""
        self.ensure_one()
        return {
            'name': _('Schedule SMS'),
            'type': 'ir.actions.act_window',
            'res_model': 'chatroom.sms.schedule.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sms_message_id': self.id,
                'default_scheduled_date': fields.Datetime.now(),
            }
        }

    def action_view_tracking(self):
        """Ver tracking de links"""
        self.ensure_one()
        return {
            'name': _('Link Tracking'),
            'type': 'ir.actions.act_window',
            'res_model': 'chatroom.sms.link.tracking',
            'view_mode': 'tree,form',
            'domain': [('sms_id', '=', self.id)],
            'context': {'default_sms_id': self.id}
        }

    # ========== CONSTRAINTS ==========

    @api.constrains('scheduled_date')
    def _check_scheduled_date(self):
        """Valida data de agendamento"""
        for rec in self:
            if rec.scheduled_date and rec.scheduled_date < fields.Datetime.now():
                raise ValidationError(_('Scheduled date must be in the future'))

    # ========== OVERRIDE ==========

    def action_send(self):
        """Override: verifica blacklist antes de enviar"""
        for sms in self:
            # Verifica blacklist
            blacklisted = self.env['chatroom.sms.blacklist'].search([
                ('phone', '=', sms.phone),
                ('active', '=', True),
            ], limit=1)

            if blacklisted:
                sms.write({
                    'state': 'rejected',
                    'error_message': f'Phone in blacklist: {blacklisted.reason}',
                    'blacklist_reason': blacklisted.reason,
                })
                continue

        # Chama método original
        return super(SMSMessage, self).action_send()

    @api.model
    def create(self, vals):
        """Override: validação adicional"""
        # Validação de agendamento
        if vals.get('scheduled_date'):
            if vals['scheduled_date'] < fields.Datetime.now():
                raise ValidationError(_('Cannot schedule SMS in the past'))

        return super(SMSMessage, self).create(vals)
```

#### 3.2 Criar views/sms_message_advanced_views.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Inherit form view -->
    <record id="view_sms_message_form_advanced" model="ir.ui.view">
        <field name="name">sms.message.form.advanced</field>
        <field name="model">sms.message</field>
        <field name="inherit_id" ref="sms_base_sr.view_sms_message_form"/>
        <field name="arch" type="xml">

            <!-- Adicionar botão Schedule -->
            <xpath expr="//header" position="inside">
                <button name="action_schedule"
                        string="Schedule"
                        type="object"
                        class="btn-primary"
                        attrs="{'invisible': [('state', '!=', 'draft')]}"/>
            </xpath>

            <!-- Adicionar campos no sheet -->
            <xpath expr="//field[@name='provider_id']" position="after">
                <field name="scheduled_date"
                       attrs="{'invisible': [('is_scheduled', '=', False)]}"/>
                <field name="is_scheduled" invisible="1"/>
                <field name="campaign_id"/>
                <field name="priority"/>
            </xpath>

            <!-- Adicionar notebook com abas extras -->
            <xpath expr="//field[@name='error_message']" position="after">
                <notebook>
                    <page string="Advanced" name="advanced">
                        <group>
                            <group>
                                <field name="tag_ids" widget="many2many_tags"/>
                                <field name="blacklist_reason"
                                       attrs="{'invisible': [('state', '!=', 'rejected')]}"/>
                            </group>
                            <group>
                                <field name="link_clicks"/>
                            </group>
                        </group>

                        <!-- Link Tracking -->
                        <group string="Link Tracking"
                               attrs="{'invisible': [('link_clicks', '=', 0)]}">
                            <field name="link_tracking_ids" nolabel="1">
                                <tree>
                                    <field name="url"/>
                                    <field name="clicked_date"/>
                                    <field name="ip_address"/>
                                </tree>
                            </field>
                        </group>
                    </page>
                </notebook>
            </xpath>

        </field>
    </record>

    <!-- Inherit tree view -->
    <record id="view_sms_message_tree_advanced" model="ir.ui.view">
        <field name="name">sms.message.tree.advanced</field>
        <field name="model">sms.message</field>
        <field name="inherit_id" ref="sms_base_sr.view_sms_message_tree"/>
        <field name="arch" type="xml">

            <xpath expr="//field[@name='state']" position="before">
                <field name="campaign_id" optional="hide"/>
                <field name="scheduled_date" optional="hide"/>
                <field name="is_scheduled" invisible="1"/>
            </xpath>

        </field>
    </record>

    <!-- Filtros adicionais -->
    <record id="view_sms_message_search_advanced" model="ir.ui.view">
        <field name="name">sms.message.search.advanced</field>
        <field name="model">sms.message</field>
        <field name="inherit_id" ref="sms_base_sr.view_sms_message_search"/>
        <field name="arch" type="xml">

            <xpath expr="//filter[@name='state_draft']" position="after">
                <filter name="scheduled" string="Scheduled"
                        domain="[('is_scheduled', '=', True)]"/>
                <filter name="with_campaign" string="Campaign SMS"
                        domain="[('campaign_id', '!=', False)]"/>
            </xpath>

            <xpath expr="//group" position="inside">
                <filter name="group_campaign" string="Campaign"
                        context="{'group_by': 'campaign_id'}"/>
            </xpath>

        </field>
    </record>

</odoo>
```

### Tarde (3-4h)

#### 3.3 Criar Modelo Helper: chatroom.sms.tag

```python
# models/chatroom_sms_tag.py
# -*- coding: utf-8 -*-
from odoo import models, fields


class ChatroomSMSTag(models.Model):
    _name = 'chatroom.sms.tag'
    _description = 'SMS Tag'
    _order = 'name'

    name = fields.Char('Tag Name', required=True)
    color = fields.Integer('Color', default=0)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Tag name must be unique!')
    ]
```

#### 3.4 Criar views/chatroom_sms_tag_views.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="view_chatroom_sms_tag_tree" model="ir.ui.view">
        <field name="name">chatroom.sms.tag.tree</field>
        <field name="model">chatroom.sms.tag</field>
        <field name="arch" type="xml">
            <tree string="SMS Tags" editable="bottom">
                <field name="name"/>
                <field name="color" widget="color_picker"/>
            </tree>
        </field>
    </record>

    <record id="action_chatroom_sms_tag" model="ir.actions.act_window">
        <field name="name">SMS Tags</field>
        <field name="res_model">chatroom.sms.tag</field>
        <field name="view_mode">tree,form</field>
    </record>

    <menuitem id="menu_chatroom_sms_tag"
              name="Tags"
              parent="sms_base_sr.menu_sms_config"
              action="action_chatroom_sms_tag"
              sequence="50"/>

</odoo>
```

#### 3.5 Atualizar security/ir.model.access.csv

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_chatroom_sms_tag_user,chatroom.sms.tag.user,model_chatroom_sms_tag,base.group_user,1,1,1,0
access_chatroom_sms_tag_manager,chatroom.sms.tag.manager,model_chatroom_sms_tag,base.group_system,1,1,1,1
```

#### 3.6 Teste

```bash
ssh odoo-rc

cd /odoo
sudo -u odoo ./odoo-bin -c odoo.conf -d test_db -u chatroom_sms_advanced --stop-after-init

# Verificar logs
# Não deve ter erros
```

---

## DIA 4: CRIAR _INHERIT (SMS.PROVIDER)

### Implementar sms_provider_advanced.py
(Similar ao dia 3, mas para sms.provider)

### Adicionar campos:
- auto_balance_check
- balance_alert_threshold
- dnd_enabled, dnd_start_hour, dnd_end_hour
- webhook_url_custom

---

## DIA 5: CRIAR MODELO SCHEDULED

### Implementar chatroom_sms_scheduled.py
### Criar views e cron
### Testar agendamento

---

## DIA 6: CRIAR MODELO CAMPAIGN

### Implementar chatroom_sms_campaign.py
### Criar views
### Testar criação de campanha

---

## DIA 7: CRIAR DASHBOARD

### Implementar chatroom_sms_dashboard.py (SQL View)
### Criar views Kanban/Graph
### Adicionar charts

---

## DIA 8: ADAPTAR WIZARD BULK SEND

### Atualizar chatroom_send_bulk_sms.py
### Usar sms.message ao invés de chatroom.sms.log
### Testar envio em lote

---

## DIA 9: CRIAR BLACKLIST

### Implementar chatroom_sms_blacklist.py
### Integrar com Kolmeya API
### Criar cron sync

---

## DIA 10-12: TESTES COMPLETOS

### Teste cada funcionalidade
### Correção de bugs
### Documentação

---

## DIA 13-14: DEPLOY

### Deploy staging
### Testes com usuários
### Deploy produção

---

## COMANDOS ÚTEIS

### Git
```bash
# Commit incremental
git add models/sms_message_advanced.py
git commit -m "feat: add sms.message advanced fields"

# Ver diff
git diff HEAD~1

# Voltar mudanças
git checkout models/sms_message_advanced.py
```

### Odoo
```bash
# Atualizar módulo
ssh odoo-rc "cd /odoo && sudo -u odoo ./odoo-bin -c odoo.conf -d odoo_15 -u chatroom_sms_advanced --stop-after-init"

# Ver logs
ssh odoo-rc "tail -f /var/log/odoo/odoo.log | grep chatroom_sms"

# Reiniciar Odoo
ssh odoo-rc "sudo systemctl restart odoo"
```

### Debugging
```bash
# Python shell no servidor
ssh odoo-rc "cd /odoo && sudo -u odoo python3"

# Teste import
>>> from odoo.addons.sms_kolmeya.models.kolmeya_api import KolmeyaAPI
>>> api = KolmeyaAPI("Bearer TOKEN", 109)
>>> print(api.get_balance())
```

---

## CHECKLIST FINAL ANTES DE DEPLOY

- [ ] Todos testes passam
- [ ] Sem erros no log
- [ ] Backup BD feito
- [ ] Migration script (se necessário)
- [ ] Documentação atualizada
- [ ] Code review
- [ ] Aprovação do cliente

---

**FIM DO PLANO DE AÇÃO**
