# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # SMS Statistics
    sms_message_ids = fields.One2many('sms.message', 'partner_id', string='SMS Messages')
    sms_count = fields.Integer('Total SMS', compute='_compute_sms_stats')
    sms_sent_count = fields.Integer('SMS Sent', compute='_compute_sms_stats')
    sms_received_count = fields.Integer('SMS Received', compute='_compute_sms_stats')
    last_sms_date = fields.Datetime('Last SMS', compute='_compute_sms_stats')

    @api.depends('sms_message_ids')
    def _compute_sms_stats(self):
        for partner in self:
            sms_messages = partner.sms_message_ids
            partner.sms_count = len(sms_messages)
            partner.sms_sent_count = len(sms_messages.filtered(lambda s: s.direction == 'outgoing'))
            partner.sms_received_count = len(sms_messages.filtered(lambda s: s.direction == 'incoming'))
            partner.last_sms_date = sms_messages[0].create_date if sms_messages else False

    def action_view_sms_messages(self):
        """Open SMS messages for this partner"""
        self.ensure_one()
        return {
            'name': 'SMS Messages',
            'type': 'ir.actions.act_window',
            'res_model': 'sms.message',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }

    def action_send_sms(self):
        """Open SMS composer wizard"""
        self.ensure_one()
        return {
            'name': 'Send SMS',
            'type': 'ir.actions.act_window',
            'res_model': 'sms.composer',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_ids': [(6, 0, self.ids)],
                'default_phone': self.mobile or self.phone
            }
        }
