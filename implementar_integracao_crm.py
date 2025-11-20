#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para implementar integração com CRM
FASE 1 - Funcionalidade 6
"""

# Criar arquivo de integração com CRM
crm_integration_content = """# -*- coding: utf-8 -*-
\"\"\"
CRM Integration - SMS Core Unified
==================================

Integração de SMS com módulo CRM (Oportunidades)
\"\"\"

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    \"\"\"
    Extend CRM Lead to add SMS functionality
    \"\"\"
    _inherit = 'crm.lead'

    # SMS Statistics
    sms_message_count = fields.Integer(
        string='SMS Messages',
        compute='_compute_sms_statistics',
        help='Number of SMS messages sent to this opportunity'
    )
    
    sms_last_sent = fields.Datetime(
        string='Last SMS Sent',
        compute='_compute_sms_statistics',
        help='Date of last SMS sent'
    )
    
    sms_total_cost = fields.Float(
        string='Total SMS Cost (R$)',
        compute='_compute_sms_statistics',
        digits=(10, 2),
        help='Total cost of SMS messages sent'
    )

    @api.depends('partner_id')
    def _compute_sms_statistics(self):
        \"\"\"Compute SMS statistics for this opportunity\"\"\"
        for lead in self:
            if lead.partner_id:
                messages = self.env['sms.message'].search([
                    ('partner_id', '=', lead.partner_id.id),
                    ('state', 'in', ['sent', 'delivered'])
                ])
                
                lead.sms_message_count = len(messages)
                lead.sms_total_cost = sum(messages.mapped('actual_cost')) or sum(messages.mapped('estimated_cost')) or 0.0
                
                if messages:
                    lead.sms_last_sent = max(messages.mapped('sent_date'))
                else:
                    lead.sms_last_sent = False
            else:
                lead.sms_message_count = 0
                lead.sms_total_cost = 0.0
                lead.sms_last_sent = False

    def action_send_sms(self):
        \"\"\"
        Open SMS compose wizard for this opportunity
        \"\"\"
        self.ensure_one()
        
        if not self.partner_id:
            raise UserError(_('Please select a contact for this opportunity'))
        
        if not self.partner_id.mobile and not self.partner_id.phone:
            raise UserError(_('Contact does not have a phone number'))
        
        # Get default provider
        provider = self.env['sms.provider'].get_default_provider()
        if not provider:
            raise UserError(_('No active SMS provider configured'))
        
        # Open SMS compose wizard
        return {
            'name': _('Send SMS'),
            'type': 'ir.actions.act_window',
            'res_model': 'sms.bulk.send',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_ids': [(6, 0, [self.partner_id.id])],
                'default_provider_id': provider.id,
                'default_body': self._get_default_sms_body(),
            }
        }

    def _get_default_sms_body(self):
        \"\"\"
        Generate default SMS body based on opportunity
        \"\"\"
        self.ensure_one()
        
        # Template básico
        body = f'Olá {self.partner_id.name or "Cliente"},'
        
        if self.expected_revenue:
            body += f'\\n\\nSua oportunidade de R$ {self.expected_revenue:,.2f} está aguardando sua resposta.'
        
        if self.date_deadline:
            body += f'\\n\\nPrazo: {self.date_deadline.strftime("%d/%m/%Y")}'
        
        body += '\\n\\nEntre em contato conosco para mais informações.'
        
        return body

    def action_view_sms_messages(self):
        \"\"\"
        View all SMS messages sent to this opportunity's contact
        \"\"\"
        self.ensure_one()
        
        if not self.partner_id:
            raise UserError(_('Please select a contact for this opportunity'))
        
        return {
            'name': _('SMS Messages'),
            'type': 'ir.actions.act_window',
            'res_model': 'sms.message',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.partner_id.id)],
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_provider_id': self.env['sms.provider'].get_default_provider().id
            }
        }

    @api.model
    def create(self, vals):
        \"\"\"
        Override create to log SMS activity if needed
        \"\"\"
        record = super(CrmLead, self).create(vals)
        
        # Future: Auto-send SMS on opportunity creation (if configured)
        # For now, just create the record
        
        return record

    def write(self, vals):
        \"\"\"
        Override write to handle SMS-related updates
        \"\"\"
        result = super(CrmLead, self).write(vals)
        
        # Future: Auto-send SMS on stage change (if configured)
        # For now, just update the record
        
        return result

"""

# Salvar arquivo
with open('/tmp/crm_lead_sms.py', 'w') as f:
    f.write(crm_integration_content)

print("✅ Arquivo de integração CRM criado:")
print("   - /tmp/crm_lead_sms.py")

