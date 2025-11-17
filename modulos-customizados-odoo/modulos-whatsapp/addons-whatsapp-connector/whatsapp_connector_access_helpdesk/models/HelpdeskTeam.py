# -*- coding: utf-8 -*-
from odoo import models, fields


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.ticket.team'

    chatroom_user_ids = fields.Many2many('res.users', 'chatroom_allowed_helpdesk_team_users', 'team_id', 'user_id',
                                         string='ChatRoom Users')
