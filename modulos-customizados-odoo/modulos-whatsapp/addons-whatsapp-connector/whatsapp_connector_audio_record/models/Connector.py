
from odoo import models, fields


class Connector(models.Model):

    _inherit = 'acrux.chat.connector'

    allow_record_audio = fields.Boolean('Allow Record Audio', default=False)
