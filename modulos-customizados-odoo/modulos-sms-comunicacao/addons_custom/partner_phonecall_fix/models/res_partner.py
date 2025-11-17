# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    phonecall_ids = fields.One2many(
        "crm.phonecall",
        "partner_id",
        string="Ligações Telefônicas"
    )
    
    phonecall_count = fields.Integer(
        string="Número de Ligações",
        compute="_compute_phonecall_count"
    )

    @api.depends("phonecall_ids")
    def _compute_phonecall_count(self):
        for partner in self:
            partner.phonecall_count = len(partner.phonecall_ids)

    def action_view_phonecall(self):
        self.ensure_one()
        action = {
            "name": "Ligações Telefônicas",
            "type": "ir.actions.act_window",
            "res_model": "crm.phonecall",
            "view_mode": "tree,form",
            "domain": [("partner_id", "=", self.id)],
            "context": {
                "default_partner_id": self.id,
                "search_default_partner_id": self.id,
            },
        }
        return action
