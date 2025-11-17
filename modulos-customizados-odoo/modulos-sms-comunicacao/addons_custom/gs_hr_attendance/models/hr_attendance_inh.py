from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
import time
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
import pytz
import logging
_logger = logging.getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    state = fields.Selection(string='State', selection=[('on_time', 'A Tiempo'), ('late', 'Tarde'),('missing','Ausente'),('none',' ')], compute='_compute_state')
    missing = fields.Boolean(string='Ausente')
    in_hour = fields.Float(string='Hora Entrada', related='employee_id.in_hour')
    allow_edit = fields.Boolean(string='Permiso de Editar', compute='_compute_allow_edit')
    check_in_date = fields.Char(string="Check In" )
    check_out_date = fields.Char(string="Check Out")

    @api.depends('allow_edit')
    def _compute_allow_edit(self):
        for rec in self:
            #Grupo manager asistenccias -   hr_attendance.group_hr_attendance_manager
            rec.allow_edit = True #rec.env.user.has_group('hr_attendance.group_hr_attendance_manager')

            rec.check_in_date = rec.check_in
            rec.check_out_date = rec.check_out



    @api.depends('state','check_in','missing')
    def _compute_state(self):
        for rec in self:
            _logger.debug("********************************* aquii leegue ********************************* ")
            t = rec.employee_id.in_hour
            hour, minute = divmod(t, 1)
            minute *= 60
            time = '{0:02.0f}:{1:02.0f}'.format(float(hour), float((minute + float(rec.env['ir.config_parameter'].sudo().get_param('gs_hr_attendance.overtime_employee_late')))))
            compare_time = datetime.strptime(time, '%H:%M').time()

            check_in = (rec.check_in - relativedelta(hours=6)).time()

            # raise ValidationError('%s, %s, %s,'%(check_in, compare_time, check_in <= compare_time))
            _logger.debug(check_in)
            _logger.debug(compare_time)
            
            if check_in <= compare_time:
                rec.state = 'on_time'
            if check_in >= compare_time:
                rec.state = 'late'
            if rec.missing:
                rec.state = 'missing'

    @api.model
    def check_attendance(self):

        start_date = (datetime(date.today().year,date.today().month, date.today().day , 0 , 0, 0, 0) + relativedelta(hours=6))
        end_date = (datetime(date.today().year,date.today().month, date.today().day , 23 , 59, 59, 0) + relativedelta(hours=6))
        all_employes = self.env['hr.employee'].search([('id','>',0)])

        for employee in all_employes:
            action_date = pytz.utc.localize(datetime.now()).astimezone(pytz.timezone(employee._get_tz()))
            action_date =  action_date.strftime('%Y-%m-%d %H:%M:%S')
            # attendance = self.env['hr.attendance'].search([('check_in','>=', start_date),('check_out','<=', end_date), ('employee_id','=', employee.id)])
            attendance = self.env['hr.attendance'].search([('check_in','>=', start_date), ('employee_id','=', employee.id)])
            if not attendance:
                self.env['hr.attendance'].create({
                    'check_in': action_date,
                    'check_out': action_date,
                    'employee_id': employee.id,
                    'missing': True
                })
