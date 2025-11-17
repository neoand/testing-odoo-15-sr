# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    chatroom_edit_default_answer = fields.Boolean(string='Edit before send',
                                                  config_parameter='chatroom.edit.default.answer')
