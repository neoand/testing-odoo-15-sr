# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ChatroomSmsLog(models.Model):
    _name = 'chatroom.sms.log'
    _description = 'Log de Envios SMS'
    _order = 'create_date desc'
    _rec_name = 'phone'

    room_id = fields.Many2one(
        'chatroom.room',
        string='Sala',
        ondelete='cascade',
        help='Sala de chat relacionada ao envio'
    )
    conversation_id = fields.Many2one(
        'chatroom.conversation',
        string='Conversa',
        ondelete='set null',
        help='Conversa relacionada ao SMS'
    )
    phone = fields.Char(
        string='Telefone',
        required=True,
        help='Número de telefone destinatário (com código do país)'
    )
    message = fields.Text(
        string='Mensagem',
        required=True,
        help='Conteúdo da mensagem SMS enviada'
    )
    request_id = fields.Char(
        string='Request ID Kolmeya',
        index=True,
        help='Identificador único da requisição na API Kolmeya',
        copy=False
    )
    message_id = fields.Char(
        string='Message ID Kolmeya',
        index=True,
        help='Identificador único da mensagem na API Kolmeya',
        copy=False
    )
    reference = fields.Char(
        string='Referência',
        help='Referência customizada para identificação',
        copy=False
    )
    status = fields.Selection(
        selection=[
            ('pending', 'Pendente'),
            ('sent', 'Enviado'),
            ('delivered', 'Entregue'),
            ('failed', 'Falhou'),
            ('rejected', 'Rejeitado'),
            ('expired', 'Expirado'),
        ],
        string='Status',
        default='pending',
        required=True,
        help='Status atual do SMS na operadora',
        copy=False
    )
    status_code = fields.Integer(
        string='Código de Status',
        help='Código HTTP de status da resposta da API',
        copy=False
    )
    status_message = fields.Text(
        string='Mensagem de Status',
        help='Mensagem detalhada do status retornado pela API',
        copy=False
    )
    sent_at = fields.Datetime(
        string='Enviado Em',
        help='Data e hora em que o SMS foi enviado à operadora',
        copy=False
    )
    delivered_at = fields.Datetime(
        string='Entregue Em',
        help='Data e hora em que o SMS foi entregue ao destinatário',
        copy=False
    )
    cost = fields.Float(
        string='Custo Estimado',
        digits=(10, 4),
        help='Custo estimado do envio em reais (R$)',
        copy=False
    )
    segment_id = fields.Many2one(
        'chatroom.sms.segment',
        string='Centro de Custo',
        ondelete='set null',
        help='Centro de custo/segmento para contabilização'
    )
    error_message = fields.Text(
        string='Mensagem de Erro',
        help='Mensagem de erro caso o envio tenha falho',
        copy=False
    )
    webhook_received_at = fields.Datetime(
        string='Webhook Recebido Em',
        help='Data e hora em que o webhook de status foi recebido',
        copy=False
    )

    # Campos computados
    delivery_time = fields.Integer(
        string='Tempo de Entrega (seg)',
        compute='_compute_delivery_time',
        store=True,
        help='Tempo decorrido entre envio e entrega em segundos'
    )
    message_length = fields.Integer(
        string='Tamanho da Mensagem',
        compute='_compute_message_length',
        store=True,
        help='Número de caracteres da mensagem'
    )
    sms_parts = fields.Integer(
        string='Partes SMS',
        compute='_compute_sms_parts',
        store=True,
        help='Número de partes/créditos utilizados (1 SMS = 160 caracteres)'
    )

    @api.depends('sent_at', 'delivered_at')
    def _compute_delivery_time(self):
        """Calcula o tempo de entrega em segundos"""
        for log in self:
            if log.sent_at and log.delivered_at:
                delta = log.delivered_at - log.sent_at
                log.delivery_time = int(delta.total_seconds())
            else:
                log.delivery_time = 0

    @api.depends('message')
    def _compute_message_length(self):
        """Calcula o tamanho da mensagem"""
        for log in self:
            log.message_length = len(log.message) if log.message else 0

    @api.depends('message_length')
    def _compute_sms_parts(self):
        """Calcula o número de partes SMS necessárias"""
        for log in self:
            if log.message_length == 0:
                log.sms_parts = 0
            elif log.message_length <= 160:
                log.sms_parts = 1
            else:
                # Mensagens concatenadas usam 153 caracteres por parte
                log.sms_parts = (log.message_length + 152) // 153

    def update_status_from_webhook(self, status, message_id=None, status_message=None,
                                   status_code=None, delivered_at=None):
        """Atualiza o status do log a partir de um webhook"""
        self.ensure_one()

        values = {
            'status': status,
            'webhook_received_at': fields.Datetime.now()
        }

        if message_id:
            values['message_id'] = message_id

        if status_message:
            values['status_message'] = status_message

        if status_code:
            values['status_code'] = status_code

        if status == 'sent' and not self.sent_at:
            values['sent_at'] = fields.Datetime.now()

        if status == 'delivered':
            values['delivered_at'] = delivered_at or fields.Datetime.now()

        if status in ('failed', 'rejected', 'expired'):
            values['error_message'] = status_message or f'SMS {status}'

        self.write(values)

        # Atualiza também a conversa se existir
        if self.conversation_id:
            self.conversation_id.update_sms_status(status, message_id, status_message)

        _logger.info(
            f"Status do log SMS {self.id} atualizado para '{status}' "
            f"(message_id: {message_id or self.message_id})"
        )

        return True

    def action_retry_send(self):
        """Tenta reenviar o SMS"""
        self.ensure_one()

        if self.status not in ('failed', 'rejected', 'expired'):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Aviso'),
                    'message': _('Apenas SMS com falha podem ser reenviados.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        # Chama o método de envio SMS (deve ser implementado em outro módulo)
        try:
            sms_sender = self.env['chatroom.sms.sender']
            result = sms_sender.send_sms(
                phone=self.phone,
                message=self.message,
                reference=self.reference,
                room_id=self.room_id.id if self.room_id else None,
                segment_id=self.segment_id.id if self.segment_id else None
            )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sucesso'),
                    'message': _('SMS reenviado com sucesso.'),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            _logger.error(f"Erro ao reenviar SMS: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Erro'),
                    'message': _('Erro ao reenviar SMS: %s') % str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }

    @api.model
    def get_statistics(self, date_from=None, date_to=None, segment_id=None):
        """Retorna estatísticas de envio de SMS"""
        domain = []

        if date_from:
            domain.append(('create_date', '>=', date_from))
        if date_to:
            domain.append(('create_date', '<=', date_to))
        if segment_id:
            domain.append(('segment_id', '=', segment_id))

        logs = self.search(domain)

        stats = {
            'total': len(logs),
            'pending': len(logs.filtered(lambda l: l.status == 'pending')),
            'sent': len(logs.filtered(lambda l: l.status == 'sent')),
            'delivered': len(logs.filtered(lambda l: l.status == 'delivered')),
            'failed': len(logs.filtered(lambda l: l.status == 'failed')),
            'rejected': len(logs.filtered(lambda l: l.status == 'rejected')),
            'expired': len(logs.filtered(lambda l: l.status == 'expired')),
            'total_cost': sum(logs.mapped('cost')),
            'total_parts': sum(logs.mapped('sms_parts')),
            'avg_delivery_time': sum(logs.mapped('delivery_time')) / len(logs) if logs else 0,
            'delivery_rate': (len(logs.filtered(lambda l: l.status == 'delivered')) / len(logs) * 100) if logs else 0,
        }

        return stats
