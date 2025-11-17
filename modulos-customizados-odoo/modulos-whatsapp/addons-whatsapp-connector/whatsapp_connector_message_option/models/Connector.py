# -*- coding: utf-8 -*-

from odoo import models


class Connector(models.Model):
    _inherit = 'acrux.chat.connector'

    def get_actions(self):
        '''
            :overide
        '''
        self.ensure_one()
        actions = super(Connector, self).get_actions()
        actions['delete_message'] = 'delete'
        return actions
