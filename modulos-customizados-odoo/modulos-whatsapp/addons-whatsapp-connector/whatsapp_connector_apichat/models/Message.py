# -*- coding: utf-8 -*-

from odoo import models


class AcruxChatMessages(models.Model):
    _inherit = 'acrux.chat.message'

    def message_parse(self):
        '''
            :overide
        '''
        self.ensure_one()
        out = super(AcruxChatMessages, self).message_parse()
        if self.connector_id.apichat_is_direct():
            if out['type'] in ['image', 'video']:
                if out['text']:
                    out['caption'] = out['text']
                del out['filename']
                del out['text']
            elif out['type'] == 'file':
                del out['text']
            elif out['type'] == 'location':
                out['latitude'] = float(out['latitude'])
                out['longitude'] = float(out['longitude'])
            out['number'] = out['to']
            out['external_id'] = out['id']
            del out['to']
            del out['id']
            if hasattr(self, 'quote_id') and getattr(self, 'quote_id'):
                out['quote_msg_obj'] = getattr(self, 'quote_id')
        return out
