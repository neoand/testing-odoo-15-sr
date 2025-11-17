from odoo import models, fields, api, _
import pytz

class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    def parse_param(self, vals, mode='in'):
        if self._context.get('ismobile', None):
            vals.update({'ismobile_check_' + mode: self._context.get('ismobile', None)})
        if self._context.get('geospatial_id', None):
            vals.update({'geospatial_check_' + mode + '_id': self._context.get('geospatial_id', None)})
        if self._context.get('ip_id', None):
            vals.update({'ip_check_' + mode + '_id': self._context.get('ip_id', None)})
        if self._context.get('ip', None):
            vals.update({'ip_check_' + mode: self._context.get('ip', None)})
        if self._context.get('geo', None):
            vals.update({'geo_check_' + mode: self._context.get('geo', None)})
        if self._context.get('token', None):
            vals.update({'token_check_' + mode + '_id': self._context.get('token', None)})
        if self._context.get('webcam', None):
            vals.update({'webcam_check_' + mode: self._context.get('webcam', None)})
        if self._context.get('user_agent_html', None):
            vals.update({'user_agent_html_check_' + mode: self._context.get('user_agent_html', None)})
        if self._context.get('face_recognition_image', None):
            vals.update({'face_recognition_image_check_' + mode: self._context.get('face_recognition_image', None)})
        if self._context.get('kiosk_shop_id', None):
            vals.update({'kiosk_shop_id_check_' + mode: self._context.get('kiosk_shop_id', None)})

        access_allowed = self._context.get('access_allowed', None)
        access_denied = self._context.get('access_denied', None)
        access_allowed_disable = self._context.get('access_allowed_disable', None)
        access_denied_disable = self._context.get('access_denied_disable', None)
        accesses = self._context.get('accesses', None)
        if accesses:
            for key, value in accesses.items():
                if value.get('enable', False):
                    if value.get('access', False):
                        vals.update({key + '_check_' + mode: access_allowed})
                    else:
                        vals.update({key + '_check_' + mode: access_denied})
                else:
                    if value.get('access', False):
                        vals.update({key + '_check_' + mode: access_allowed_disable})
                    else:
                        vals.update({key + '_check_' + mode: access_denied_disable})

    attendance_break_state = fields.Selection(string="Attendance Break Status", compute='_compute_attendance_break_state',
                                              selection=[('break', 'Break'), ('resume', 'Resume')], default='resume')

    @api.depends('last_attendance_id.check_in', 'last_attendance_id.check_out', 'last_attendance_id')
    def _compute_attendance_break_state(self):
        for employee in self:
            attendance = employee.last_attendance_id.sudo()
            employee.attendance_break_state = 'resume'
            if attendance.break_ids:
                break_obj = self.env['hr.attendance.break'].search(
                    [('attendance_id', '=', attendance.id)], limit=1, order='create_date desc')
                employee.attendance_break_state = break_obj.attendance_break_state if break_obj.attendance_break_state else 'resume'

    def attendance_break_manual(self, next_action, snap=None, entered_pin=None):
        self.ensure_one()
        can_check_without_pin = not self.env.user.has_group('hr_attendance.group_hr_attendance_use_pin') or (
            self.user_id == self.env.user and entered_pin is None)
        if can_check_without_pin or entered_pin is not None and entered_pin == self.sudo().pin:
            if snap:
                return self.attendance_break_resume_action(next_action, snap)
            else:
                return self.attendance_break_resume_action(next_action)
        return {'warning': _('Wrong PIN')}

    def attendance_break_resume_action(self, next_action, snap=None):
        self.ensure_one()
        action_date = fields.Datetime.now()
        for employee in self:
            attendance = employee.last_attendance_id.sudo()
            if employee.attendance_state == 'checked_in':
                break_obj = self.env['hr.attendance.break'].search(
                    [('attendance_id', '=', attendance.id), ('break_time', '!=', False)], limit=1, order='create_date desc')

                vals = {}
                action_date = pytz.utc.localize(action_date).astimezone(pytz.timezone(employee._get_tz()))
                action_date =  action_date.strftime('%Y-%m-%d %H:%M:%S')
                if employee.attendance_break_state == 'break' and break_obj.break_time != False:
                    break_obj.update({
                        'resume_time': action_date,
                        'attendance_break_state': 'resume',
                        'webcam_check_out': snap,
                    })
                    self.parse_param(vals, 'out')
                    break_obj.write(vals)
                else:
                    break_obj.create({
                        'attendance_id': attendance.id,
                        'employee_id': employee.id,
                        'break_time': action_date,
                        'attendance_break_state': 'break',
                        'webcam_check_in': snap,
                    })
                    self.parse_param(vals)
                    break_obj.write(vals)

        employee = self.sudo()
        action_message = self.env.ref(
            'hr_attendance.hr_attendance_action_greeting_message').read()[0]

        action_message['attendance'] = attendance.read()[0]
        action_message['next_action'] = next_action

        break_obj = self.env['hr.attendance.break'].search(
            [('attendance_id', '=', attendance.id)], limit=1, order='create_date desc')
        action_message['attendance_break_state'] = break_obj.attendance_break_state if break_obj.attendance_break_state else 'resume'
        return {'action': action_message}
