# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AcruxChatConnector(models.Model):
    """
    Estende acrux.chat.connector para suportar SMS (Kolmeya).

    Adiciona connector type 'sms' ao lado de 'apichat', 'gupshup', etc.
    """
    _inherit = 'acrux.chat.connector'

    connector_type = fields.Selection(
        selection_add=[('sms', 'SMS (Kolmeya)')],
        ondelete={'sms': 'cascade'}
    )

    # Referência ao provider SMS (Kolmeya)
    sms_provider_id = fields.Many2one('sms.provider', 'SMS Provider',
                                      domain=[('provider_type', '=', 'kolmeya')],
                                      help='Kolmeya SMS provider for this connector')

    # Campos específicos SMS (copiados do provider para facilitar)
    sms_api_token = fields.Char('Kolmeya API Token', related='sms_provider_id.kolmeya_api_token', readonly=True)
    sms_segment_id = fields.Integer('Segment ID', related='sms_provider_id.kolmeya_segment_id', readonly=True)
    sms_balance = fields.Float('SMS Balance', related='sms_provider_id.kolmeya_balance', readonly=True)

    # Estatísticas SMS
    sms_sent_count = fields.Integer('SMS Sent', compute='_compute_sms_stats', store=False)
    sms_received_count = fields.Integer('SMS Received', compute='_compute_sms_stats', store=False)
    sms_total_cost = fields.Float('Total Cost', compute='_compute_sms_stats', store=False)

    @api.depends('connector_type')
    def _compute_sms_stats(self):
        """Calcula estatísticas de SMS para este connector"""
        for connector in self:
            if connector.connector_type == 'sms':
                # Conta conversas SMS deste connector
                conversations = self.env['acrux.chat.conversation'].search([
                    ('connector_id', '=', connector.id),
                    ('channel_type', '=', 'sms'),
                ])

                # Busca mensagens SMS relacionadas
                sms_messages = self.env['sms.message'].search([
                    ('partner_id', 'in', conversations.mapped('res_partner_id').ids),
                ])

                sent = sms_messages.filtered(lambda m: m.direction == 'outgoing')
                received = sms_messages.filtered(lambda m: m.direction == 'incoming')

                connector.sms_sent_count = len(sent)
                connector.sms_received_count = len(received)

                # Custo aproximado (R$ 0,10 por SMS)
                connector.sms_total_cost = len(sent) * 0.10
            else:
                connector.sms_sent_count = 0
                connector.sms_received_count = 0
                connector.sms_total_cost = 0.0

    @api.model
    def create(self, vals):
        """Validação ao criar connector SMS"""
        if vals.get('connector_type') == 'sms':
            if not vals.get('sms_provider_id'):
                raise UserError(_('SMS connector requires a Kolmeya provider'))

        return super(AcruxChatConnector, self).create(vals)

    def write(self, vals):
        """Validação ao editar connector SMS"""
        if vals.get('connector_type') == 'sms' or (self.connector_type == 'sms' and 'sms_provider_id' in vals):
            if not vals.get('sms_provider_id') and not self.sms_provider_id:
                raise UserError(_('SMS connector requires a Kolmeya provider'))

        return super(AcruxChatConnector, self).write(vals)

    def action_test_connection(self):
        """
        Testa conexão do connector.

        Para SMS: verifica saldo Kolmeya.
        Para WhatsApp: usa método padrão.
        """
        self.ensure_one()

        if self.connector_type == 'sms':
            if not self.sms_provider_id:
                raise UserError(_('No SMS provider configured'))

            # Testa saldo Kolmeya
            try:
                self.sms_provider_id.action_check_balance()
                balance = self.sms_provider_id.kolmeya_balance

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connection Successful'),
                        'message': _('Kolmeya SMS connected. Balance: R$ %.2f') % balance,
                        'type': 'success',
                        'sticky': False,
                    }
                }
            except Exception as e:
                raise UserError(_('Connection failed: %s') % str(e))
        else:
            # WhatsApp/outros: usa método padrão
            return super(AcruxChatConnector, self).action_test_connection()

    def ca_request(self, url, data=None, method='POST'):
        """
        Sobrescreve método de requisição HTTP para SMS.

        Para SMS, delega ao provider Kolmeya.
        Para WhatsApp, usa método padrão.
        """
        if self.connector_type == 'sms':
            # SMS não usa ca_request - usa Kolmeya API diretamente
            raise UserError(_('SMS connector does not support ca_request. Use sms_provider_id methods instead.'))
        else:
            return super(AcruxChatConnector, self).ca_request(url, data, method)
