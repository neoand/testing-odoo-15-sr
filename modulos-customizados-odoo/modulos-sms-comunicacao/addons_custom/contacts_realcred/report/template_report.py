# -*- coding: utf-8 -*-

from odoo import models
from odoo import models, api, fields, _
from datetime import datetime,timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)


class GeneralReport(models.AbstractModel):
    _name = 'report.contacts.realcred.batch.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

        self.gather_data()
        sheet = workbook.add_worksheet('Reporte')

        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'right': True, 'left': True,'bottom': True, 'top': True, 'bold': True, 'font_color':'#ffffff','bg_color':'#000000'})



        sheet.write(0, 0, _('Nome'), format21)
        sheet.write(0, 1, _('CPF'), format21)
        sheet.write(0, 2, _('DDD'), format21)
        sheet.write(0, 3, _('Telefone'), format21)
        sheet.write(0, 4, _('TipoTelefone'), format21)
        sheet.write(0, 5, _('Ranking'), format21)
        sheet.write(0, 6, _('Score'), format21)

        index = 1

        for order in lines.contacts_realcred_campaign_ids:
            sheet.write(index, 0, order.name )
            sheet.write(index, 1, order.cpf )
            sheet.write(index, 2, order.cpf )
            sheet.write(index, 3, order.cpf )
            sheet.write(index, 4, order.cpf )
            sheet.write(index, 5, order.cpf )

            index +=1

    def gather_data(self):
        pass
