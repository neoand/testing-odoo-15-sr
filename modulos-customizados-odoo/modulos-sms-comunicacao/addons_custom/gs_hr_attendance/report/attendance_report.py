# -*- coding: utf-8 -*-

import pytz
from odoo import models
from odoo import models, api, fields, _
from datetime import datetime,timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)


class AttendanceReport(models.AbstractModel):
    _name = 'report.attendance.report.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        # print(po)
        # _logger.debug('========='*40,data,lines)

        self.gather_data()
        sheet = workbook.add_worksheet(_('General Report'))
        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'center',
                'bold': True})
        format4 = workbook.add_format({'align':'center', 'left':True, 'right':True, 'bottom': True, 'top': True, 'font_size': 10,'num_format': '#,##0.00', 'bold': True, 'bg_color':'#dbeb34'})
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'right': True, 'left': True,'bottom': True, 'top': True, 'bold': True, 'font_color':'#ffffff','bg_color':'#000000'})
        format23 = workbook.add_format({'font_size': 10, 'align': 'left', 'right': False, 'left': False,'bottom': False, 'top': False, 'bold': True, 'text_wrap': True})
        format22 = workbook.add_format({'font_size': 10, 'align': 'left', 'right': True, 'left': True,'bottom': True, 'top': True, 'bold': False, 'text_wrap': True})
        format24 = workbook.add_format({'font_size': 10, 'align': 'left', 'right': True, 'left': True,'bottom': True, 'top': True, 'bold': False, 'text_wrap': True, 'num_format': '#,##0.00'})

        sheet.set_column(0, 0, 18)
        sheet.set_column(1, 1, 18)
        sheet.set_column(2, 2, 18)
        sheet.set_column(3, 3, 18)
        sheet.set_column(4, 4, 18)
        sheet.set_column(5, 5, 28)
        sheet.set_column(6, 6, 17)
        sheet.set_column(7, 7, 30)
        sheet.set_column(8, 8, 15)
        sheet.set_column(9, 9, 15)
        sheet.set_column(10, 10, 15)
        sheet.set_column(11, 11, 15)
        sheet.set_column(12, 12, 15)
        sheet.set_column(13, 13, 15)
        sheet.set_column(14, 14, 15)
        sheet.set_column(15, 15, 15)
        sheet.set_column(16, 16, 15)
            
        sheet.merge_range('A5:F5', self.env.user.company_id.name, format1)
        sheet.merge_range('B7:D7', _("Fecha de impresión: "+datetime.today().replace(microsecond=0).strftime('%d-%m-%Y %H:%M:%S')),format23)

        sheet.write(9, 0, _('Empleado'), format21)
        # sheet.write(9, 1, _('Hora Entrada'), format21)
        sheet.write(9, 1, _('Estado'), format21)
        sheet.write(9, 2, _('Entrada'), format21)
        sheet.write(9, 3, _('Salida'), format21)

        
        index = 10

        attendances = self.env['hr.attendance'].search([('check_in','>=', data.get('start_date')),('check_out','<=', data.get('end_date'))])        
        user_tz = self.env.user.tz or self.env.context.get('tz')
        for attendance in attendances:
            check_in_date = pytz.utc.localize(attendance.check_in).astimezone(pytz.timezone(user_tz))
            check_out_date = pytz.utc.localize(attendance.check_out).astimezone(pytz.timezone(user_tz))
            sheet.write(index, 0, attendance.employee_id.name , format22)
            # sheet.write(index, 1, attendance.in_hour , format22)
            sheet.write(index, 1, attendance.state , format22)
            sheet.write(index, 2, check_in_date.strftime('%d-%m-%Y %H:%M:%S'), format22)
            sheet.write(index, 3, check_out_date.strftime('%d-%m-%Y %H:%M:%S') , format22)
            index +=1

    def gather_data(self):
        pass