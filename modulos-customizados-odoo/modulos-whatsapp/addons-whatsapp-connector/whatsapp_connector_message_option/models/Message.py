# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Message(models.Model):
    _inherit = 'acrux.chat.message'

    date_delete = fields.Datetime('Date Delete')
    quote_id = fields.Many2one('acrux.chat.message', 'Queted Message', ondelete='set null')

    @api.model
    def get_fields_to_read(self):
        fields_to_read = super(Message, self).get_fields_to_read()
        fields_to_read.append('quote_id')
        fields_to_read.append('date_delete')
        return fields_to_read

    def message_parse(self):
        message = super(Message, self).message_parse()
        if self.quote_id and self.quote_id.msgid:
            message['quote_msg_id'] = self.quote_id.msgid
        return message

    def get_js_dict(self):
        data = super(Message, self).get_js_dict()
        fields_to_read = self.get_fields_to_read()
        fields_to_read = list(filter(lambda key: key != 'quote_id', fields_to_read))
        quoted_data = {msg['id']: msg for msg in self.mapped('quote_id').read(fields_to_read)}
        for msg in data:
            if msg['quote_id']:
                msg['quote_id'] = quoted_data[msg['quote_id'][0]]
        return data

    def process_message_event(self, data):
        self.ensure_one()
        if data['type'] == 'deleted':
            self.set_deleted()
        else:
            super(Message, self).process_message_event(data)

    def set_deleted(self):
        self.clean_content()
        self.write({
            'ttype': 'text',
            'text': _('Deleted'),
            'date_delete': fields.Datetime.now()
        })
