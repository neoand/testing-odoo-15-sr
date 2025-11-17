from odoo import fields, models, api, _

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    reason_for_check_in = fields.Char("Reason for Check In ")
    reason_for_check_out = fields.Char("Reason for Check Out")

    def update_reason(self, employee_id, reason=None):
        self.ensure_one()
        if employee_id and reason:            
            employee = self.env['hr.employee'].sudo().search([('id','=',employee_id)])
            if employee.attendance_state == 'checked_in':
                self.sudo().update({'reason_for_check_in' : reason})
            if employee.attendance_state == 'checked_out':
                self.sudo().update({'reason_for_check_out' : reason})
        