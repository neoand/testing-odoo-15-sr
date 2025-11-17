from odoo import _, api, fields, models



class ProductBank(models.Model):

    _name = 'product.bank'
    name = fields.Char(string="Banco")


class Promotora(models.Model):

    _name = 'product.promotora'
    name = fields.Char(string="Promotora")

class Categoria(models.Model):

    _name = 'product.categoria'
    name = fields.Char(string="Categoria")

class Convenio(models.Model):

    _name = 'product.convenio'
    name = fields.Char(string="Convenios")


class ProductsInherint(models.Model):

    _inherit = 'product.template'

    bank = fields.Many2one('product.bank')
    promotora = fields.Many2one('product.promotora')
    categoria = fields.Many2one('product.categoria')
    convenio = fields.Many2one('product.convenio')
    prazos = fields.Integer(string="Prazos")