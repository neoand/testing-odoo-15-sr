#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para implementar integração com Contatos
FASE 1 - Funcionalidade 7
"""

# Criar arquivo de integração com Contatos
partner_integration_content = """# -*- coding: utf-8 -*-
\"\"\"
Partner Integration - SMS Core Unified
======================================

Integração de SMS com módulo de Contatos (res.partner)
\"\"\"

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    \"\"\"
    Extend res.partner to add SMS functionality
    \"\"\"
    _inherit = 'res.partner'

    # SMS Statistics
    sms_message_count = fields.Integer(
        string='SMS Messages',
        compute='_compute_sms_statistics',
        help='Number of SMS messages sent to this contact'
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
    
    sms_delivery_rate = fields.Float(
        string='SMS Delivery Rate (%)',
        compute='_compute_sms_statistics',
        digits=(5, 2),
        help='Percentage of delivered SMS messages'
    )

    @api.depends('mobile', 'phone')
    def _compute_sms_statistics(self):
        \"\"\"Compute SMS statistics for this contact\"\"\"
        for partner in self:
            messages = self.env['sms.message'].search([
                ('partner_id', '=', partner.id)
            ])
            
            partner.sms_message_count = len(messages)
            
            sent_messages = messages.filtered(lambda m: m.state in ['sent', 'delivered'])
            partner.sms_total_cost = sum(sent_messages.mapped('actual_cost')) or sum(sent_messages.mapped('estimated_cost')) or 0.0
            
            if sent_messages:
                partner.sms_last_sent = max(sent_messages.mapped('sent_date'))
            else:
                partner.sms_last_sent = False
            
            # Calculate delivery rate
            if sent_messages:
                delivered = len(messages.filtered(lambda m: m.state == 'delivered'))
                partner.sms_delivery_rate = (delivered / len(sent_messages)) * 100
            else:
                partner.sms_delivery_rate = 0.0

    def action_send_sms(self):
        \"\"\"
        Open SMS compose wizard for this contact
        \"\"\"
        self.ensure_one()
        
        if not self.mobile and not self.phone:
            raise UserError(_('Contact does not have a phone number'))
        
        # Get default provider
        provider = self.env['sms.provider'].get_default_provider()
        if not provider:
            raise UserError(_('No active SMS provider configured'))
        
        # Open SMS compose wizard
        return {
            'name': _('Send SMS to %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'sms.bulk.send',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_ids': [(6, 0, [self.id])],
                'default_provider_id': provider.id,
            }
        }

    def action_view_sms_messages(self):
        \"\"\"
        View all SMS messages sent to this contact
        \"\"\"
        self.ensure_one()
        
        return {
            'name': _('SMS Messages'),
            'type': 'ir.actions.act_window',
            'res_model': 'sms.message',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
                'default_provider_id': self.env['sms.provider'].get_default_provider().id
            }
        }

    def action_add_to_blacklist(self):
        \"\"\"
        Add contact's phone to blacklist
        \"\"\"
        self.ensure_one()
        
        phone = self.mobile or self.phone
        if not phone:
            raise UserError(_('Contact does not have a phone number'))
        
        blacklist = self.env['sms.blacklist'].add_to_blacklist(
            phone,
            reason=f'Added from contact: {self.name}'
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Added to Blacklist'),
                'message': _('Phone number %s added to blacklist') % phone,
                'type': 'success'
            }
        }

"""

# Salvar arquivo
with open('/tmp/res_partner_sms.py', 'w') as f:
    f.write(partner_integration_content)

print("✅ Arquivo de integração Contatos criado:")
print("   - /tmp/res_partner_sms.py")

