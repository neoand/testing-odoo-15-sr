# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AcruxChatConversation(models.Model):
    """
    Estende acrux.chat.conversation para suportar SMS além de WhatsApp.

    Esta é a peça-chave do Contact Center Unificado:
    - Adiciona channel_type para distinguir SMS/WhatsApp/Instagram
    - Reutiliza toda arquitetura ChatRoom (Kanban, Agents, Templates)
    - Permite interface única para todos canais
    """
    _inherit = 'acrux.chat.conversation'

    # Campo principal: tipo de canal
    channel_type = fields.Selection([
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('instagram', 'Instagram'),
        ('messenger', 'Messenger'),
    ], string='Channel Type', default='whatsapp', required=True, index=True,
       help='Communication channel: SMS, WhatsApp, Instagram or Messenger')

    # Referência ao SMS original (quando conversa iniciada por SMS)
    sms_message_id = fields.Many2one('sms.message', 'Original SMS',
                                     ondelete='set null', index=True,
                                     help='Original SMS message that started this conversation')

    @api.model
    def create_from_sms(self, sms_message):
        """
        Cria uma conversa ChatRoom a partir de SMS recebido.

        Integra SMS ao fluxo do ChatRoom:
        1. Busca conversa existente (mesmo número + canal SMS)
        2. Se não existe, cria nova conversa
        3. Adiciona mensagem ao thread
        4. Notifica agente via bus

        Args:
            sms_message: recordset de sms.message (incoming)

        Returns:
            acrux.chat.conversation record
        """
        if not sms_message.partner_id:
            raise UserError(_('SMS must have a partner to create conversation'))

        # Busca conversa existente (mesmo número + canal SMS)
        existing = self.search([
            ('number', '=', sms_message.phone),
            ('channel_type', '=', 'sms'),
        ], limit=1)

        if existing:
            _logger.info(f"Found existing SMS conversation {existing.id} for {sms_message.phone}")
            # Adiciona mensagem ao thread existente
            existing._add_sms_to_thread(sms_message)
            return existing

        # Cria nova conversa SMS
        # NOTA: Precisamos de um connector SMS válido
        sms_connector = self.env['acrux.chat.connector'].search([
            ('connector_type', '=', 'sms'),
        ], limit=1)

        if not sms_connector:
            raise UserError(_('No SMS connector configured. Please create one first.'))

        conversation = self.create({
            'name': sms_message.partner_id.name or sms_message.phone,
            'number': sms_message.phone,
            'number_format': sms_message.phone,  # Já formatado
            'connector_id': sms_connector.id,
            'res_partner_id': sms_message.partner_id.id,
            'channel_type': 'sms',
            'sms_message_id': sms_message.id,
            'border_color': '#FF6B6B',  # Vermelho para SMS (vs verde WhatsApp)
        })

        _logger.info(f"Created new SMS conversation {conversation.id} for {sms_message.phone}")

        # Adiciona primeira mensagem
        conversation._add_sms_to_thread(sms_message)

        # Auto-assign se houver agente disponível
        conversation._auto_assign_agent()

        return conversation

    def _add_sms_to_thread(self, sms_message):
        """
        Adiciona mensagem SMS ao thread da conversa.

        Cria acrux.chat.message vinculado ao sms.message original.
        """
        self.ensure_one()

        # Cria mensagem no ChatRoom
        msg_vals = {
            'contact_id': self.id,
            'ttype': 'text',
            'text': sms_message.body,
            'from_me': sms_message.direction == 'outgoing',
            'date_message': sms_message.date or fields.Datetime.now(),
        }

        chat_message = self.env['acrux.chat.message'].create(msg_vals)

        _logger.info(f"Added SMS to conversation thread: {chat_message.id}")

        # Atualiza última mensagem da conversa
        self.write({
            'last_received': fields.Datetime.now() if not msg_vals['from_me'] else self.last_received,
            'last_activity': fields.Datetime.now(),
        })

        # Notifica via bus (real-time)
        if not msg_vals['from_me']:
            self._notify_new_message(chat_message)

        return chat_message

    def _auto_assign_agent(self):
        """Auto-atribui agente disponível para nova conversa SMS"""
        self.ensure_one()

        if self.agent_id:
            return  # Já tem agente

        # Busca agente online disponível
        available_agent = self.env['res.users'].search([
            ('acrux_chat_active', '=', True),  # Online no ChatRoom
        ], limit=1)

        if available_agent:
            self.write({'agent_id': available_agent.id})
            _logger.info(f"Auto-assigned agent {available_agent.name} to SMS conversation {self.id}")

    def _notify_new_message(self, message):
        """Notifica agente via bus sobre nova mensagem SMS"""
        self.ensure_one()

        notification = {
            'type': 'new_message',
            'conversation_id': self.id,
            'message_id': message.id,
            'channel_type': 'sms',
            'from': self.name,
            'text': message.text[:100] if message.text else '',  # Preview
        }

        # Envia via Odoo bus (WebSocket)
        self.env['bus.bus']._sendone(
            f'acrux_chat_channel_{self.connector_id.id}',
            'new_message',
            notification
        )

    def send_sms_message(self, body):
        """
        Envia SMS através da conversa ChatRoom.

        Integra envio SMS ao fluxo do ChatRoom:
        1. Cria sms.message
        2. Envia via Kolmeya
        3. Adiciona ao thread da conversa
        4. Atualiza status

        Args:
            body: texto da mensagem

        Returns:
            sms.message record
        """
        self.ensure_one()

        if self.channel_type != 'sms':
            raise UserError(_('This conversation is not SMS type'))

        # Busca provider Kolmeya
        provider = self.env['sms.provider'].search([
            ('provider_type', '=', 'kolmeya'),
        ], limit=1)

        if not provider:
            raise UserError(_('No Kolmeya SMS provider configured'))

        # Cria SMS message
        sms = self.env['sms.message'].create({
            'partner_id': self.res_partner_id.id,
            'phone': self.number,
            'body': body,
            'direction': 'outgoing',
            'state': 'draft',
            'provider_id': provider.id,
        })

        # Envia via Kolmeya
        sms.action_send()

        # Adiciona ao thread da conversa
        self._add_sms_to_thread(sms)

        _logger.info(f"Sent SMS via conversation {self.id}: {sms.id}")

        return sms
