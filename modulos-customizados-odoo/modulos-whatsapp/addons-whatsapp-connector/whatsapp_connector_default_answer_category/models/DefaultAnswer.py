# -*- coding: utf-8 -*-
from odoo import models, fields, api


class DefaultAnswer(models.Model):
    _inherit = 'acrux.chat.default.answer'

    category_id = fields.Many2one('acrux.chat.default.answer.category',
                                  string='Category', ondelete='set null')

    @api.model
    def get_fields_to_read(self):
        out = super(DefaultAnswer, self).get_fields_to_read()
        out.append('category_id')
        return out
