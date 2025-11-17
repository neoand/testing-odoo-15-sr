# -*- coding: utf-8 -*-

from odoo import models, api, _ , fields
from odoo.addons.whatsapp_connector.tools import get_image_from_url
from datetime import datetime, date

class Conversation(models.Model):
    _inherit = 'acrux.chat.conversation'

    def update_conversation(self):
        '''
            :overide
        '''
        self.ensure_one()
        if self.connector_id.apichat_is_direct():
            params = {'number': self.number}
            try:
                data = self.connector_id.ca_request('conversations', params=params, timeout=5)
                if data:
                    image_url = data[0].get('image')
                    if image_url and image_url.startswith('http'):
                        raw = get_image_from_url(image_url)
                        if raw:
                            self.image_128 = raw
                    name = data[0].get('name')
                    if name:
                        self.name = name.strip()
            except Exception as _e:
                pass
        else:
            super(Conversation, self).update_conversation()

    @api.model
    def chat_update_event(self, connector_id, data):
        '''
            :overide
        '''
        if connector_id.apichat_is_direct():
            data['image_url'] = data['image']
        super(Conversation, self).chat_update_event(connector_id, data)


    @api.model
    def _get_message_allowed_types(self):
        return ['text', 'image', 'audio', 'video', 'file', 'location', 'sticker']

    @api.model
    def parse_message_receive(self, connector_id, message):
        ttype = message.get('type')
        text = message.get('text')
        text = text or ''
        if ttype not in self._get_message_allowed_types():
            text = text or 'Message type Not allowed (%s).' % ttype
            ttype = 'text'
        if message.get('time'):
            date_msg = datetime.fromtimestamp(message.get('time'))
        else:
            date_msg = fields.Datetime.now()
        out = {
            'ttype': ttype,
            'connector_id': connector_id.id,
            'name': message.get('name'),
            'msgid': message.get('id', False),
            'number': connector_id.clean_id(message.get('number', '')),
            'message': text.strip(),
            'filename': message.get('filename', ''),
            'url': message.get('url', ''),
            'time': date_msg,
            'conv_type': 'none',
        }
        if message.get('metadata'):
            out['metadata'] = message['metadata']
        if message.get('id'):
            if connector_id.connector_type in ['apichat.io', 'chatapi']:
                out['from_me'] = 'false' == 'true'
                if 'normal' in message.get('chat_type'):
                    out['conv_type'] = 'normal'
                else:
                    out['conv_type'] = 'normal'
            else:
                out['conv_type'] = 'normal'
        return out

    @api.model
    def parse_apichat_contact_message(self, message, vobject):
        def normalize(string):
            return str(string).strip('/n').strip(' ').strip(',').strip(' ').strip('/n')
        ignore = ['X-ABLABEL', 'VERSION', 'N', 'X-ABADR']
        cards_out = []
        for contact in message.get('contacts'):
            vobj = vobject.readOne(contact['vcard'].replace('|', '\n'))
            card_str = []
            for i in vobj.contents.keys():
                line = []
                for j in vobj.contents[i]:
                    if j.name not in ignore:
                        line.append('%s: %s' % (j.name, normalize(j.value)))
                if line:
                    card_str.append('\n'.join(line))
            if card_str:
                cards_out.append('\n'.join(card_str))
        return '\n\n'.join(cards_out)

    @api.model
    def parse_event_receive(self, connector_id, event):
        '''
            :overide
        '''
        if connector_id.apichat_is_direct():
            if event.get('type') == 'failed':
                out = {
                    'type': event.get('type'),
                    'msgid': event.get('id'),
                    'reason': event.get('reason'),
                }
            elif event.get('type') == 'deleted':
                out = {
                    'type': event.get('type'),
                    'msgid': event.get('id'),
                }
            else:
                out = event
        else:
            out = super(Conversation, self).parse_event_receive(connector_id, event)
        return out
