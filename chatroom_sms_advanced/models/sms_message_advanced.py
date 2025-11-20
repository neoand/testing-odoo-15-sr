# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class SMSMessage(models.Model):
    """
    Extends sms.message from sms_base_sr with advanced features:
    - Campaign tracking
    - Scheduling support
    - Cost tracking
    - Blacklist integration
    """
    _inherit = 'sms.message'

    # ========== CAMPAIGN ==========
    campaign_id = fields.Many2one(
        'sms.campaign',
        string='Campaign',
        ondelete='set null',
        index=True,
        help='SMS Campaign this message belongs to'
    )

    # ========== SCHEDULED ==========
    scheduled_id = fields.Many2one(
        'sms.scheduled',
        string='Scheduled Task',
        ondelete='set null',
        index=True,
        help='Scheduled task that created this SMS'
    )

    # ========== COST ==========
    cost = fields.Float(
        string='Cost (R$)',
        digits=(10, 4),
        help='Cost of this SMS message'
    )

    # ========== COMPUTED FIELDS ==========
    is_scheduled = fields.Boolean(
        string='Is Scheduled',
        compute='_compute_is_scheduled',
        store=True,
        help='True if this SMS is part of a scheduled task'
    )

    # ========== COMPUTE METHODS ==========
    @api.depends('scheduled_id')
    def _compute_is_scheduled(self):
        """Compute if SMS is part of a scheduled task"""
        for record in self:
            record.is_scheduled = bool(record.scheduled_id)

    # ========== ONCHANGE METHODS ==========
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Auto-fill phone number when partner is selected"""
        if self.partner_id:
            self.phone = self.partner_id.mobile or self.partner_id.phone

    # ========== OVERRIDE METHODS ==========
    def action_send(self):
        """
        Override send to:
        1. Check blacklist
        2. Calculate cost
        3. Call parent send method
        """
        for sms in self:
            # Check if phone is blacklisted
            if sms.phone:
                blacklisted = self.env['sms.blacklist'].search([
                    ('phone', '=', sms.phone),
                    ('active', '=', True)
                ], limit=1)

                if blacklisted:
                    sms.write({
                        'state': 'error',
                        'error_message': _('Phone number is blacklisted: %s') % blacklisted.reason
                    })
                    _logger.warning(f"SMS to {sms.phone} blocked - blacklisted: {blacklisted.reason}")
                    continue

            # Calculate cost (estimated)
            if not sms.cost and sms.body:
                sms._compute_cost()

        # Call parent method for non-blacklisted messages
        valid_sms = self.filtered(lambda s: s.state != 'error')
        if valid_sms:
            return super(SMSMessage, valid_sms).action_send()

    def _compute_cost(self):
        """
        Calculate SMS cost based on message length
        - 1 segment (160 chars) = R$ 0.10
        - Each additional segment = R$ 0.10
        """
        for sms in self:
            if sms.body:
                char_count = len(sms.body)
                segments = (char_count // 160) + (1 if char_count % 160 else 0)
                sms.cost = segments * 0.10
            else:
                sms.cost = 0.0

    # ========== UTILITY METHODS ==========
    def action_view_campaign(self):
        """Open campaign view"""
        self.ensure_one()
        if not self.campaign_id:
            raise UserError(_('This SMS is not part of any campaign'))

        return {
            'name': _('Campaign'),
            'type': 'ir.actions.act_window',
            'res_model': 'sms.campaign',
            'res_id': self.campaign_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_add_to_blacklist(self):
        """Add this phone to blacklist"""
        self.ensure_one()
        if not self.phone:
            raise UserError(_('No phone number to blacklist'))

        # Check if already exists
        existing = self.env['sms.blacklist'].search([
            ('phone', '=', self.phone)
        ], limit=1)

        if existing:
            if not existing.active:
                existing.active = True
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Blacklist Updated'),
                        'message': _('Phone number re-activated in blacklist'),
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_('Phone number already in blacklist'))

        # Create new blacklist entry
        self.env['sms.blacklist'].create({
            'phone': self.phone,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'reason': 'manual',
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Added to Blacklist'),
                'message': _('Phone %s added to blacklist') % self.phone,
                'type': 'success',
            }
        }
