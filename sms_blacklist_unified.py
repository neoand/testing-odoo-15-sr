# -*- coding: utf-8 -*-
"""
SMS Blacklist Model
==================

From chatroom_sms_advanced - enhanced for unified system

PARA: /odoo/custom/addons_custom/sms_core_unified/models/sms_blacklist.py
"""

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class SMSBlacklist(models.Model):
    """
    SMS Blacklist - Prevent sending to blocked numbers
    """
    _name = 'sms.blacklist'
    _description = 'SMS Blacklist Management'
    _order = 'create_date DESC'

    phone = fields.Char(string='Phone Number', required=True, index=True)
    reason = fields.Text(string='Blacklist Reason', required=True)
    active = fields.Boolean(string='Active', default=True)

    # Metadata
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    create_date = fields.Datetime(string='Created Date', readonly=True)

    # Statistics
    blocked_count = fields.Integer(string='Blocked Messages', readonly=True, default=0)
    last_blocked = fields.Datetime(string='Last Blocked', readonly=True)

    _sql_constraints = [
        ('phone_unique', 'UNIQUE(phone)', 'Phone number already in blacklist'),
    ]

    @api.model
    def is_phone_blacklisted(self, phone):
        """Check if phone is blacklisted"""
        blacklist = self.search([
            ('phone', '=', phone),
            ('active', '=', True)
        ], limit=1)

        return bool(blacklist)

    def increment_blocked_count(self):
        """Increment blocked count"""
        self.write({
            'blocked_count': self.blocked_count + 1,
            'last_blocked': fields.Datetime.now()
        })

    @api.model
    def add_to_blacklist(self, phone, reason='Manual addition'):
        """Add phone to blacklist"""
        existing = self.search([('phone', '=', phone)], limit=1)

        if existing:
            if not existing.active:
                existing.write({'active': True, 'reason': reason})
            return existing
        else:
            return self.create({
                'phone': phone,
                'reason': reason
            })