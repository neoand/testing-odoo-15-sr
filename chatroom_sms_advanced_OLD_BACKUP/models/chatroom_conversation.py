# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ChatroomConversation(models.Model):
    _inherit = 'chatroom.conversation'

    sms_request_id = fields.Char(
        string='ID Requisição Kolmeya',
        help='Identificador único da requisição de envio na API Kolmeya',
        copy=False
    )
    sms_message_id = fields.Char(
        string='ID Mensagem Kolmeya',
        index=True,
        help='Identificador único da mensagem na API Kolmeya',
        copy=False
    )
    sms_status = fields.Selection(
        selection=[
            ('pending', 'Pendente'),
            ('sent', 'Enviado'),
            ('delivered', 'Entregue'),
            ('failed', 'Falhou'),
            ('rejected', 'Rejeitado'),
            ('expired', 'Expirado'),
        ],
        string='Status SMS',
        default='pending',
        help='Status atual do SMS na operadora',
        copy=False
    )
    sms_status_updated_at = fields.Datetime(
        string='Status Atualizado Em',
        help='Data e hora da última atualização de status',
        copy=False
    )
    sms_reference = fields.Char(
        string='Referência',
        help='Referência customizada para identificação do SMS',
        copy=False
    )

    def update_sms_status(self, status, message_id=None, status_message=None):
        """Atualiza o status do SMS e registra no log"""
        self.ensure_one()

        values = {
            'sms_status': status,
            'sms_status_updated_at': fields.Datetime.now()
        }

        if message_id:
            values['sms_message_id'] = message_id

        self.write(values)

        # Atualiza também o log de SMS se existir
        if self.sms_message_id or message_id:
            sms_log = self.env['chatroom.sms.log'].search([
                ('message_id', '=', message_id or self.sms_message_id)
            ], limit=1)

            if sms_log:
                log_values = {'status': status}

                if status_message:
                    log_values['status_message'] = status_message

                if status == 'sent':
                    log_values['sent_at'] = fields.Datetime.now()
                elif status == 'delivered':
                    log_values['delivered_at'] = fields.Datetime.now()
                elif status in ('failed', 'rejected', 'expired'):
                    log_values['error_message'] = status_message or f'SMS {status}'

                sms_log.write(log_values)

        _logger.info(
            f"Status SMS atualizado para conversa {self.id}: {status} "
            f"(message_id: {message_id or self.sms_message_id})"
        )

        return True

    def action_view_sms_log(self):
        """Abre a visualização do log de SMS relacionado"""
        self.ensure_one()

        if not self.sms_message_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Aviso'),
                    'message': _('Esta conversa não possui um SMS associado.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        sms_log = self.env['chatroom.sms.log'].search([
            ('message_id', '=', self.sms_message_id)
        ], limit=1)

        if not sms_log:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Aviso'),
                    'message': _('Log de SMS não encontrado.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        return {
            'name': _('Log SMS'),
            'type': 'ir.actions.act_window',
            'res_model': 'chatroom.sms.log',
            'res_id': sms_log.id,
            'view_mode': 'form',
            'target': 'new',
        }
