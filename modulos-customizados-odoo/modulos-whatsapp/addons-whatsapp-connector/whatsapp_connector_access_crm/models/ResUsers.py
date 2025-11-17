# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    chatroom_access_crm_team_ids = fields.Many2many('crm.team', 'chatroom_allowed_crm_team_users', 'user_id', 'team_id',
                                                    string='ChatRoom CRM Team Access')

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['chatroom_access_crm_team_ids']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['chatroom_access_crm_team_ids']
