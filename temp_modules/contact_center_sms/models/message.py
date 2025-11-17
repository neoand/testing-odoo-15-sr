# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class AcruxChatMessage(models.Model):
    """
    Estende acrux.chat.message para suportar mensagens SMS.

    Adiciona campos/métodos específicos para SMS enquanto mantém
    compatibilidade com WhatsApp.
    """
    _inherit = 'acrux.chat.message'

    # Referência ao SMS original (se mensagem veio de SMS)
    sms_message_id = fields.Many2one('sms.message', 'SMS Message',
                                     ondelete='set null', index=True,
                                     help='Original SMS message linked to this chat message')

    # Informações específicas SMS
    is_sms = fields.Boolean('Is SMS', compute='_compute_is_sms', store=True,
                            help='True if this message is from SMS channel')

    sms_segment_count = fields.Integer('SMS Segments', compute='_compute_sms_info', store=False)
    sms_cost = fields.Float('SMS Cost', compute='_compute_sms_info', store=False)

    @api.depends('contact_id.channel_type')
    def _compute_is_sms(self):
        """Marca mensagem como SMS baseado no canal da conversa"""
        for msg in self:
            msg.is_sms = msg.contact_id.channel_type == 'sms' if msg.contact_id else False

    @api.depends('text', 'is_sms')
    def _compute_sms_info(self):
        """Calcula segmentos e custo para mensagens SMS"""
        for msg in self:
            if msg.is_sms and msg.text:
                text_len = len(msg.text)
                # SMS: 160 chars por segmento (padrão), 70 se tiver unicode
                has_unicode = any(ord(c) > 127 for c in msg.text)
                segment_size = 70 if has_unicode else 160
                msg.sms_segment_count = (text_len // segment_size) + (1 if text_len % segment_size else 0)
                # Custo aproximado: R$ 0,10 por segmento
                msg.sms_cost = msg.sms_segment_count * 0.10
            else:
                msg.sms_segment_count = 0
                msg.sms_cost = 0.0

    @api.model
    def create(self, vals):
        """Valida mensagens SMS no create"""
        msg = super(AcruxChatMessage, self).create(vals)

        # Log para debug
        if msg.is_sms:
            _logger.info(f"Created SMS message {msg.id} in conversation {msg.contact_id.id}")

        return msg
