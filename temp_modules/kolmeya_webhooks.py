# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import logging
import json

_logger = logging.getLogger(__name__)


class KolmeyaWebhookController(http.Controller):
    """
    Webhook controller for Kolmeya SMS callbacks

    Endpoints:
    - /kolmeya/webhook/reply - SMS replies from recipients
    - /kolmeya/webhook/status - Delivery status updates
    """

    @http.route('/kolmeya/webhook/reply', type='json', auth='public', methods=['POST'], csrf=False)
    def webhook_reply(self, **kwargs):
        """
        Receive SMS replies from Kolmeya

        Expected payload:
        {
            "phone": "5548999999999",
            "message": "Resposta do cliente",
            "reference": "message_id",
            "data": "2025-11-15 14:30:00"
        }
        """
        try:
            data = request.jsonrequest
            _logger.info(f"Kolmeya reply webhook received: {data}")

            phone = data.get('phone')
            message_text = data.get('message')
            reference = data.get('reference')

            if not phone or not message_text:
                return {'status': 'error', 'message': 'Missing phone or message'}

            # Find original SMS message by reference or phone
            sms_msg = None
            if reference:
                sms_msg = request.env['sms.message'].sudo().search([
                    ('provider_reference', '=', reference)
                ], limit=1)

            if not sms_msg:
                # Search by phone number
                clean_phone = str(phone).replace('+', '').replace(' ', '').replace('-', '')
                sms_msg = request.env['sms.message'].sudo().search([
                    ('phone', 'ilike', clean_phone),
                    ('direction', '=', 'outgoing')
                ], order='sent_date desc', limit=1)

            # Create incoming SMS message
            reply_sms = request.env['sms.message'].sudo().create({
                'partner_id': sms_msg.partner_id.id if sms_msg and sms_msg.partner_id else False,
                'phone': phone,
                'body': message_text,
                'direction': 'incoming',
                'state': 'delivered',
                'delivered_date': data.get('data'),
                'provider_reference': reference,
            })

            # Link to original message if found
            if sms_msg:
                reply_sms.write({'parent_id': sms_msg.id})

                # Post in chatter of original message
                sms_msg.message_post(
                    body=f"📱 <b>Resposta recebida:</b><br/>{message_text}",
                    message_type='notification',
                    subtype_xmlid='mail.mt_note'
                )

            # Notify assigned user/vendor
            if sms_msg and sms_msg.partner_id:
                self._notify_reply(sms_msg.partner_id, reply_sms)

            _logger.info(f"Reply SMS created: {reply_sms.id}")

            return {'status': 'success', 'sms_id': reply_sms.id}

        except Exception as e:
            _logger.error(f"Error processing Kolmeya reply webhook: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    @http.route('/kolmeya/webhook/status', type='json', auth='public', methods=['POST'], csrf=False)
    def webhook_status(self, **kwargs):
        """
        Receive delivery status updates from Kolmeya

        Expected payload:
        {
            "id": "message_uuid",
            "reference": "our_reference",
            "status": "entregue",
            "status_code": 3,
            "phone": "5548999999999"
        }
        """
        try:
            data = request.jsonrequest
            _logger.info(f"Kolmeya status webhook received: {data}")

            message_id = data.get('id')
            reference = data.get('reference')
            status = data.get('status')
            status_code = data.get('status_code')

            # Find SMS message
            sms_msg = None
            if message_id:
                sms_msg = request.env['sms.message'].sudo().search([
                    ('provider_message_id', '=', message_id)
                ], limit=1)

            if not sms_msg and reference:
                sms_msg = request.env['sms.message'].sudo().search([
                    ('provider_reference', '=', reference)
                ], limit=1)

            if not sms_msg:
                return {'status': 'error', 'message': 'SMS message not found'}

            # Map Kolmeya status codes to Odoo states
            status_map = {
                1: 'outgoing',   # Tentando enviar
                2: 'sent',       # Enviado
                3: 'delivered',  # Entregue
                4: 'error',      # Não entregue
                5: 'rejected',   # Rejeitado
                6: 'expired',    # Expirado
            }

            new_state = status_map.get(int(status_code), 'sent')

            # Update SMS message
            vals = {'state': new_state}
            if new_state == 'delivered':
                vals['delivered_date'] = request.env.cr.now()

            sms_msg.write(vals)

            # Post update in chatter
            status_emoji = {
                'delivered': '✅',
                'error': '❌',
                'rejected': '⛔',
                'expired': '⏰'
            }.get(new_state, '📱')

            sms_msg.message_post(
                body=f"{status_emoji} Status atualizado: <b>{status}</b>",
                message_type='notification',
                subtype_xmlid='mail.mt_note'
            )

            return {'status': 'success', 'sms_id': sms_msg.id, 'new_state': new_state}

        except Exception as e:
            _logger.error(f"Error processing Kolmeya status webhook: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    def _notify_reply(self, partner, reply_sms):
        """
        Notify assigned salesperson about SMS reply

        Args:
            partner: res.partner who replied
            reply_sms: incoming sms.message record
        """
        try:
            # Find assigned user (vendor)
            user_to_notify = partner.user_id

            if not user_to_notify:
                # Try to find user from team or default
                user_to_notify = request.env.ref('base.user_admin')

            # Create activity for the user
            request.env['mail.activity'].sudo().create({
                'activity_type_id': request.env.ref('mail.mail_activity_data_todo').id,
                'summary': f'📱 SMS Reply from {partner.name}',
                'note': f'<p><b>{partner.name}</b> replied to SMS:</p><p>{reply_sms.body}</p>',
                'res_id': partner.id,
                'res_model_id': request.env['ir.model']._get('res.partner').id,
                'user_id': user_to_notify.id,
                'date_deadline': request.env.cr.now(),
            })

            _logger.info(f"Activity created for user {user_to_notify.name} about reply from {partner.name}")

        except Exception as e:
            _logger.error(f"Error notifying user about reply: {e}")
