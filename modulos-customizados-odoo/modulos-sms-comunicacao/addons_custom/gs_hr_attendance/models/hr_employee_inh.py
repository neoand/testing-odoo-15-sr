from odoo import _, api, fields, models, tools


class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    in_hour = fields.Float(string='Hora de Entrada')

    
    
    

