# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Conversation(models.Model):
    _inherit = 'acrux.chat.conversation'

    def new_message_hook(self, message_id, limit, data, last_sent):
        if data['quote_msg_id']:
            AcruxChatMessages = self.env['acrux.chat.message']
            message_obj = AcruxChatMessages.search([('contact_id', '=', message_id.contact_id.id),
                                                    ('msgid', '=', data['quote_msg_id'])], limit=1)
            if message_obj:
                message_id.write({'quote_id': message_obj.id})
        return super(Conversation, self).new_message_hook(message_id, limit, data, last_sent)

    @api.model
    def parse_message_receive(self, connector_id, message):
        data_msg = super(Conversation, self).parse_message_receive(connector_id, message)
        data_msg['quote_msg_id'] = message.get('quote_msg_id')
        return data_msg

    def delete_message(self, msg_id, for_me):
        self.ensure_one()
        AcruxChatMessages = self.env['acrux.chat.message']
        message_obj = AcruxChatMessages.browse(msg_id)
        self.connector_id.ca_request('delete_message', data=False, params={
            'number': self.connector_id.clean_id(self.number),
            'msg_id': message_obj.msgid,
            'for_me': 'true' if for_me else 'false',
            'from_me': 'true' if message_obj.from_me else 'false',
        })
        message_obj.write({'date_delete': fields.Datetime.now()})
        return message_obj.get_js_dict()

    @api.model
    def new_webhook_event(self, connector_id, event):
        if event.get('type') == 'deleted':
            self.new_message_event(connector_id, event['msgid'], event)
        else:
            super(Conversation, self).new_webhook_event(connector_id, event)
