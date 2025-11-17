# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class DefaultAnswerCategory(models.Model):
    _name = 'acrux.chat.default.answer.category'
    _description = 'Default Answer Category'
    _order = 'sequence'

    name = fields.Char('Name', required=True)
    sequence = fields.Integer('Sequence')

    _sql_constraints = [
        ('name', 'unique (name)', _('Name has to be unique.'))
    ]

    @api.onchange('name')
    def on_change_name(self):
        for record in self:
            if record.name:
                record.name = record.name.strip().title()
