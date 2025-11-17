# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import fields, models


class ResPertner(models.Model):

    _inherit = 'res.partner'

    attachment_ids = fields.One2many('ir.attachment', 'partner_id')
    count_doct = fields.Integer(compute='_compute_count_doct', string="Document Count")

    # Function to count total attachments of partner
    def _compute_count_doct(self):
        for partner in self:
            partner.count_doct = len(partner.attachment_ids.ids)

    # Action to open documents of specific contact
    def action_get_attachment_tree_view(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['name'] = "Documents"
        action['domain'] = [('partner_id', '=', self.id)]
        action['context'] = {'default_partner_id': self.id,'default_public':True}
        return action
