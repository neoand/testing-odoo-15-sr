from email.policy import default
from odoo import _, api, fields, models, tools

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
import pytz


class HrAttendaceReportWizard(models.TransientModel):
    _name = 'hr.attendance.report.wizard'
    _description = 'HrAttendaceReport'

    

    start_date = fields.Datetime(string='Desde', default = lambda self: self.get_start_date())
    end_date = fields.Datetime(string='Hasta',default = lambda self: self.get_end_date())

    def get_start_date(self):
        return (datetime(date.today().year,date.today().month, date.today().day , 0 , 0, 0, 0) + relativedelta(hours=6))
         

    def get_end_date(self):
        return (datetime(date.today().year,date.today().month, date.today().day , 23 , 59, 59, 0) + relativedelta(hours=6))



    def generate_report(self):
        print('Generate report')
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return self.env.ref('gs_hr_attendance.action_attendance_report_xls').report_action(self, data=data)