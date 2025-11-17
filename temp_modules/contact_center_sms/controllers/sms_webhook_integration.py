# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class SMSWebhookIntegration(http.Controller):
    """
    Integra webhooks Kolmeya com ChatRoom.

    Quando SMS chega via webhook, cria/atualiza conversa no ChatRoom
    ao invés de apenas criar sms.message.
    """

    @http.route('/kolmeya/webhook/reply', type='json', auth='public', methods=['POST'], csrf=False)
    def webhook_reply_chatroom(self, **kwargs):
        """
        Webhook de resposta SMS - integrado ao ChatRoom.

        Fluxo:
        1. Recebe SMS via Kolmeya webhook
        2. Cria sms.message (incoming)
        3. Busca/cria conversa ChatRoom
        4. Adiciona mensagem ao thread
        5. Notifica agente via bus
        """
        try:
            data = request.jsonrequest
            _logger.info(f"Received SMS reply webhook: {data}")

            # Extrai dados Kolmeya
            phone = data.get('phone')
            message_text = data.get('message')
            reference = data.get('reference')  # ID da mensagem original (se houver)
            received_at = data.get('received_at')

            if not phone or not message_text:
                return {'status': 'error', 'message': 'Missing phone or message'}

            # Busca/cria parceiro
            partner = request.env['res.partner'].sudo().search([
                '|',
                ('mobile', '=', phone),
                ('phone', '=', phone),
            ], limit=1)

            if not partner:
                # Cria parceiro novo
                partner = request.env['res.partner'].sudo().create({
                    'name': f'SMS Contact {phone}',
                    'mobile': phone,
                    'customer_rank': 1,
                })
                _logger.info(f"Created new partner {partner.id} for phone {phone}")

            # Cria sms.message incoming
            sms_message = request.env['sms.message'].sudo().create({
                'partner_id': partner.id,
                'phone': phone,
                'body': message_text,
                'direction': 'incoming',
                'state': 'delivered',
                'date': received_at or False,
            })

            _logger.info(f"Created incoming SMS message {sms_message.id}")

            # Busca conversa ChatRoom existente
            conversation = request.env['acrux.chat.conversation'].sudo().search([
                ('number', '=', phone),
                ('channel_type', '=', 'sms'),
            ], limit=1)

            if conversation:
                _logger.info(f"Found existing SMS conversation {conversation.id}")
                # Adiciona ao thread existente
                conversation._add_sms_to_thread(sms_message)
            else:
                _logger.info(f"Creating new SMS conversation for {phone}")
                # Cria nova conversa via método helper
                conversation = request.env['acrux.chat.conversation'].sudo().create_from_sms(sms_message)

            # Posta no chatter da conversa
            conversation.message_post(
                body=f"📱 <b>SMS recebido:</b><br/>{message_text}",
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

            return {
                'status': 'success',
                'sms_id': sms_message.id,
                'conversation_id': conversation.id,
                'partner_id': partner.id,
            }

        except Exception as e:
            _logger.error(f"Error processing SMS webhook: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    @http.route('/kolmeya/webhook/status', type='json', auth='public', methods=['POST'], csrf=False)
    def webhook_status_chatroom(self, **kwargs):
        """
        Webhook de status SMS - integrado ao ChatRoom.

        Atualiza status da mensagem SMS e conversa ChatRoom.
        """
        try:
            data = request.jsonrequest
            _logger.info(f"Received SMS status webhook: {data}")

            reference = data.get('reference')  # provider_reference do SMS
            status = data.get('status')  # delivered, failed, etc
            error_code = data.get('error_code')
            error_message = data.get('error_message')

            if not reference:
                return {'status': 'error', 'message': 'Missing reference'}

            # Busca SMS por provider_reference
            sms_message = request.env['sms.message'].sudo().search([
                ('provider_reference', '=', reference),
            ], limit=1)

            if not sms_message:
                _logger.warning(f"SMS not found for reference {reference}")
                return {'status': 'error', 'message': f'SMS not found: {reference}'}

            # Mapeia status Kolmeya -> Odoo
            status_map = {
                'sent': 'sent',
                'delivered': 'delivered',
                'failed': 'failed',
                'expired': 'failed',
            }
            odoo_status = status_map.get(status, 'sent')

            # Atualiza SMS
            update_vals = {'state': odoo_status}
            if error_code:
                update_vals['error_code'] = error_code
            if error_message:
                update_vals['error_message'] = error_message

            sms_message.write(update_vals)

            _logger.info(f"Updated SMS {sms_message.id} status to {odoo_status}")

            # Busca conversa ChatRoom relacionada
            conversation = request.env['acrux.chat.conversation'].sudo().search([
                ('number', '=', sms_message.phone),
                ('channel_type', '=', 'sms'),
            ], limit=1)

            if conversation:
                # Posta atualização no chatter
                status_emoji = {
                    'delivered': '✅',
                    'sent': '📤',
                    'failed': '❌',
                }.get(odoo_status, '📨')

                conversation.message_post(
                    body=f"{status_emoji} SMS {odoo_status}: {sms_message.body[:50]}...",
                    message_type='notification',
                )

            return {
                'status': 'success',
                'sms_id': sms_message.id,
                'new_status': odoo_status,
            }

        except Exception as e:
            _logger.error(f"Error processing status webhook: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}
