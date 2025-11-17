# -*- coding: utf-8 -*-
from odoo import models, fields


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    chatroom_user_ids = fields.Many2many('res.users', 'chatroom_allowed_crm_team_users', 'team_id', 'user_id',
                                         string='ChatRoom Users')
