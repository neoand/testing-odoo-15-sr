
from odoo import models, fields, api


class Conversation(models.Model):

    _inherit = 'acrux.chat.conversation'

    allow_record_audio = fields.Boolean(related='connector_id.allow_record_audio',
                                        store=False)

    @api.model
    def get_fields_to_read(self):
        fields_to_read = super(Conversation, self).get_fields_to_read()
        fields_to_read.append('allow_record_audio')
        return fields_to_read
