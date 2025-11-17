# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.osv import expression

GROUP_TEAM = 'whatsapp_connector_access_helpdesk.chat_access_helpdesk_team'
GROUP_EMPTY = 'whatsapp_connector_access_helpdesk.chat_access_helpdesk_empty'


class Conversation(models.Model):
    _inherit = 'acrux.chat.conversation'

    access_helpdesk_team_id = fields.Many2one('helpdesk.ticket.team', string='HelpDesk Access',
                                              domain="[('company_id', 'in', [company_id, False])]",
                                              ondelete='set null')

    @api.model
    def get_access_agent(self, args):
        ret = super(Conversation, self).get_access_agent(args)
        flag = [x for x in args if x[0] in ['id', 'access_helpdesk_team_id']] if args else False
        is_team = self.env.user.has_group(GROUP_TEAM)
        is_empty = self.env.user.has_group(GROUP_EMPTY) and not is_team
        if not flag and (is_team or is_empty):
            out = []
            if is_team:
                team_ids = self.env.user.chatroom_access_hd_team_ids.ids
                if team_ids:
                    out = [('access_helpdesk_team_id', 'in', team_ids)]
                else:
                    out = [(0, '=', 1)]
            else:
                out = [('access_helpdesk_team_id', '=', False)]
            if ret:
                ret = expression.OR([out, ret])
            else:
                ret = out
        return ret

    def parse_notification(self, datas):
        ''' is ensure_one '''
        flag = [x for x in datas if x[1] == 'new_messages']
        if flag:
            users = self.sudo().env.ref('whatsapp_connector.group_chat_basic_extra').users.filtered('acrux_chat_active')
            datas = self.acrux_access_field_empty(datas, users, self.access_helpdesk_team_id, GROUP_EMPTY, GROUP_TEAM)
            member_ids = self.access_helpdesk_team_id.chatroom_user_ids.ids
            datas = self.acrux_access_member_ids(datas, users, member_ids,
                                           'whatsapp_connector_access_helpdesk.chat_access_helpdesk_team')
        return super(Conversation, self).parse_notification(datas)
