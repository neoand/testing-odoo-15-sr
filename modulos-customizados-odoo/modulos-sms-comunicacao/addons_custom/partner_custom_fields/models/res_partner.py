# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
import time
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"
    type_sex =   fields.Selection([('Masculino', 'Masculino'), ('Feminino', 'Feminino'),],string='Sexo')
    date_birth =   fields.Date(string='Data de Nascimento')
    age = fields.Integer(readonly=True, compute="_compute_age",string='Edad',search="_search_field")
    especie = fields.Char(string='Espécie')
    nb = fields.Char(string='Matricula', tracking=True)
    vl_bruto_atrasados = fields.Char(string='Vl Bruto Atrasados', tracking=True)
    salario = fields.Char(string='Salario', tracking=True)
    data_ddb = fields.Date(string='Data do despacho do beneficio' , tracking=True)
    cpf = fields.Char(string='CPF', tracking=True)
    @api.depends("date_birth")
    def _compute_age(self):
        for record in self:
            age = 0
            if record.date_birth:
                age = relativedelta(fields.Date.today(), record.date_birth).years
            record.age = age


    def _search_field(self, operator, value):
        field_id = self.search([]).filtered(lambda x : x.age == value )
        return [('id', operator, [x.id for x in field_id] if field_id else False )]
