# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SMSProvider(models.Model):
    _name = 'sms.provider'
    _description = 'SMS Provider'
    _order = 'sequence, name'

    name = fields.Char('Provider Name', required=True)
    provider_type = fields.Selection([
        ('mock', 'Mock Provider (Testing)')
    ], string='Provider Type', required=True, default='mock')

    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)

    # Configuration
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    # Statistics
    message_count = fields.Integer('Total Messages', compute='_compute_statistics')
    delivered_count = fields.Integer('Delivered Messages', compute='_compute_statistics')
    error_count = fields.Integer('Failed Messages', compute='_compute_statistics')

    def _compute_statistics(self):
        for provider in self:
            messages = self.env['sms.message'].search([('provider_id', '=', provider.id)])
            provider.message_count = len(messages)
            provider.delivered_count = len(messages.filtered(lambda m: m.state == 'delivered'))
            provider.error_count = len(messages.filtered(lambda m: m.state in ['error', 'rejected']))

    def _send_sms(self, sms_message):
        """
        Send SMS via provider - TO BE OVERRIDDEN in provider-specific modules

        Args:
            sms_message: sms.message recordset

        Returns:
            dict: Response from provider
        """
        self.ensure_one()

        if self.provider_type == 'mock':
            # Mock provider for testing
            _logger.info(f"[MOCK] Sending SMS to {sms_message.phone}: {sms_message.body}")
            sms_message.write({
                'state': 'sent',
                'provider_message_id': f'mock_{sms_message.id}',
                'sent_date': fields.Datetime.now()
            })
            return {'status': 'success', 'message_id': f'mock_{sms_message.id}'}
        else:
            raise UserError(_('Provider type "%s" not implemented') % self.provider_type)

    def _send_batch(self, messages_data):
        """
        Send batch of SMS messages

        Args:
            messages_data: list of dicts with 'phone', 'message', 'reference'

        Returns:
            dict: Response from provider
        """
        self.ensure_one()
        raise NotImplementedError('Batch sending must be implemented in provider-specific module')

    def action_view_messages(self):
        """View all messages for this provider"""
        self.ensure_one()
        return {
            'name': _('SMS Messages'),
            'type': 'ir.actions.act_window',
            'res_model': 'sms.message',
            'view_mode': 'tree,form',
            'domain': [('provider_id', '=', self.id)],
            'context': {'default_provider_id': self.id}
        }
