# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    overtime_employee_late = fields.Integer(
        string="Tolerance Time In Favor Of Employee", readonly=False)


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        res['overtime_employee_late'] = self.env['ir.config_parameter'].sudo().get_param('gs_hr_attendance.overtime_employee_late', default=0.00)

        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('gs_hr_attendance.overtime_employee_late', self.overtime_employee_late)

        super(ResConfigSettings, self).set_values()
