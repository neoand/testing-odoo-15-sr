# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class WebhookKolmeya(http.Controller):
    """
    Controller para receber webhooks da plataforma Kolmeya
    """

    @http.route('/chatroom/webhook/kolmeya/status', type='json', auth='none', csrf=False, methods=['POST'])
    def webhook_status(self, **kwargs):
        """
        Webhook para receber atualizações de status de mensagens

        Payload esperado:
        {
            "id": "message_id",
            "messages": [
                {
                    "id": "msg_123",
                    "status_code": 3,
                    "status": "delivered",
                    "delivered_at": "2024-01-15T10:30:00Z"
                }
            ]
        }

        Status codes:
        1 = Sent (Enviado)
        2 = Pending (Pendente)
        3 = Delivered (Entregue)
        4 = Failed (Falhou)
        5 = Undelivered (Não entregue)
        """
        try:
            # Lê o payload JSON
            payload = json.loads(request.httprequest.data.decode('utf-8'))

            _logger.info('Webhook de status recebido: %s', payload)

            message_id = payload.get('id')
            messages = payload.get('messages', [])

            if not messages:
                _logger.warning('Webhook sem mensagens: %s', payload)
                return {'status': 'success', 'message': 'Sem mensagens para processar'}

            # Mapeia status codes para strings
            status_map = {
                1: 'sent',
                2: 'pending',
                3: 'delivered',
                4: 'failed',
                5: 'undelivered'
            }

            processed_count = 0

            for msg_data in messages:
                msg_id = msg_data.get('id')
                status_code = msg_data.get('status_code')
                status = msg_data.get('status') or status_map.get(status_code, 'unknown')
                delivered_at = msg_data.get('delivered_at')

                if not msg_id:
                    _logger.warning('Mensagem sem ID, ignorando: %s', msg_data)
                    continue

                # Busca o log de SMS pelo message_id externo
                sms_log = request.env['chatroom.sms.log'].sudo().search([
                    ('message_id', '=', msg_id)
                ], limit=1)

                if sms_log:
                    update_values = {
                        'status': status,
                        'status_code': status_code
                    }

                    if delivered_at:
                        update_values['delivered_at'] = delivered_at

                    sms_log.write(update_values)

                    # Atualiza também a conversation relacionada se existir
                    if sms_log.conversation_id:
                        sms_log.conversation_id.write({
                            'delivery_status': status
                        })

                    _logger.info(
                        'SMS log #%s atualizado para status "%s" (code: %s)',
                        sms_log.id, status, status_code
                    )
                    processed_count += 1
                else:
                    _logger.warning('SMS log não encontrado para message_id: %s', msg_id)

            return {
                'status': 'success',
                'processed': processed_count,
                'total': len(messages)
            }

        except Exception as e:
            _logger.exception('Erro ao processar webhook de status')
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/chatroom/webhook/kolmeya/reply', type='json', auth='none', csrf=False, methods=['POST'])
    def webhook_reply(self, **kwargs):
        """
        Webhook para receber respostas de clientes

        Payload esperado:
        {
            "reply": {
                "reply": "Texto da resposta do cliente",
                "message": {
                    "id": "msg_123",
                    "to": "5511999999999",
                    "from": "5511888888888"
                },
                "received_at": "2024-01-15T10:30:00Z"
            }
        }
        """
        try:
            # Lê o payload JSON
            payload = json.loads(request.httprequest.data.decode('utf-8'))

            _logger.info('Webhook de resposta recebido: %s', payload)

            reply_data = payload.get('reply', {})
            reply_text = reply_data.get('reply')
            message_info = reply_data.get('message', {})
            received_at = reply_data.get('received_at')

            if not reply_text:
                _logger.warning('Webhook sem texto de resposta: %s', payload)
                return {'status': 'success', 'message': 'Sem resposta para processar'}

            # Extrai informações da mensagem original
            original_msg_id = message_info.get('id')
            customer_phone = message_info.get('from')
            our_phone = message_info.get('to')

            if not customer_phone:
                _logger.error('Webhook sem telefone do cliente: %s', payload)
                return {'status': 'error', 'message': 'Telefone do cliente não informado'}

            # Limpa o número de telefone
            phone_clean = ''.join(filter(str.isdigit, customer_phone))

            # Busca ou cria a sala (room)
            room = request.env['chatroom.room'].sudo().search([
                ('phone', '=', phone_clean)
            ], limit=1)

            if not room:
                # Cria uma nova sala para este cliente
                room = request.env['chatroom.room'].sudo().create({
                    'name': 'Cliente %s' % phone_clean[-8:],
                    'phone': phone_clean,
                    'status': 'active'
                })
                _logger.info('Nova sala criada para telefone %s', phone_clean)

            # Cria a conversation com a resposta do cliente
            conversation_vals = {
                'room_id': room.id,
                'message': reply_text,
                'is_customer_message': True,
                'delivery_status': 'delivered'
            }

            if received_at:
                conversation_vals['date'] = received_at

            conversation = request.env['chatroom.conversation'].sudo().create(conversation_vals)

            _logger.info(
                'Resposta do cliente registrada na sala #%s: %s',
                room.id, reply_text[:50]
            )

            # Se temos o ID da mensagem original, vincula
            if original_msg_id:
                original_log = request.env['chatroom.sms.log'].sudo().search([
                    ('message_id', '=', original_msg_id)
                ], limit=1)

                if original_log:
                    original_log.write({
                        'has_reply': True,
                        'reply_text': reply_text
                    })

            # Atualiza status da sala
            room.write({
                'last_message': reply_text[:100],
                'last_message_date': received_at or conversation.date
            })

            return {
                'status': 'success',
                'room_id': room.id,
                'conversation_id': conversation.id
            }

        except Exception as e:
            _logger.exception('Erro ao processar webhook de resposta')
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/chatroom/webhook/kolmeya/test', type='json', auth='public', csrf=False, methods=['GET', 'POST'])
    def webhook_test(self, **kwargs):
        """
        Endpoint de teste para verificar se os webhooks estão funcionando

        Pode ser acessado via GET ou POST
        """
        try:
            from datetime import datetime

            _logger.info('Webhook de teste acessado')

            # Tenta ler payload se houver
            payload = None
            try:
                if request.httprequest.data:
                    payload = json.loads(request.httprequest.data.decode('utf-8'))
            except:
                pass

            return {
                'status': 'ok',
                'message': 'Webhook está funcionando corretamente',
                'timestamp': datetime.now().isoformat(),
                'method': request.httprequest.method,
                'payload_received': payload,
                'headers': dict(request.httprequest.headers)
            }

        except Exception as e:
            _logger.exception('Erro no webhook de teste')
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/chatroom/webhook/kolmeya/info', type='http', auth='public', csrf=False)
    def webhook_info(self, **kwargs):
        """
        Endpoint para exibir informações sobre os webhooks disponíveis
        """
        info_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Chatroom Webhooks - Kolmeya Integration</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }
                .method { color: #28a745; font-weight: bold; }
                .url { color: #007bff; }
                code { background: #eee; padding: 2px 5px; }
            </style>
        </head>
        <body>
            <h1>Chatroom Webhooks - Kolmeya Integration</h1>

            <div class="endpoint">
                <h3><span class="method">POST</span> /chatroom/webhook/kolmeya/status</h3>
                <p>Recebe atualizações de status de mensagens enviadas.</p>
                <p><strong>Auth:</strong> none</p>
                <p><strong>Type:</strong> JSON</p>
            </div>

            <div class="endpoint">
                <h3><span class="method">POST</span> /chatroom/webhook/kolmeya/reply</h3>
                <p>Recebe respostas de clientes às mensagens enviadas.</p>
                <p><strong>Auth:</strong> none</p>
                <p><strong>Type:</strong> JSON</p>
            </div>

            <div class="endpoint">
                <h3><span class="method">GET/POST</span> /chatroom/webhook/kolmeya/test</h3>
                <p>Endpoint de teste para verificar conectividade.</p>
                <p><strong>Auth:</strong> public</p>
                <p><strong>Type:</strong> JSON</p>
            </div>

            <hr>
            <p><em>Desenvolvido para integração com a plataforma Kolmeya SMS</em></p>
        </body>
        </html>
        """

        return request.make_response(
            info_html,
            headers=[('Content-Type', 'text/html')]
        )
