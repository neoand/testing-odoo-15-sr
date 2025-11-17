# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class SMSProvider(models.Model):
    """
    Extends sms.provider from sms_base_sr with:
    - Balance warning system
    - Auto balance check
    - Last check tracking
    """
    _inherit = 'sms.provider'

    # ========== BALANCE WARNING ==========
    balance_warning_enabled = fields.Boolean(
        string='Enable Balance Warning',
        default=True,
        help='Send warning when balance is below threshold'
    )

    balance_warning_threshold = fields.Float(
        string='Balance Warning Threshold (R$)',
        default=100.0,
        help='Minimum balance before sending warning'
    )

    balance_last_check = fields.Datetime(
        string='Last Balance Check',
        readonly=True,
        help='Last time balance was checked'
    )

    balance_warning_user_ids = fields.Many2many(
        'res.users',
        'sms_provider_balance_warning_users_rel',
        'provider_id',
        'user_id',
        string='Warning Recipients',
        help='Users to notify when balance is low'
    )

    # ========== DND (Do Not Disturb) ==========
    dnd_enabled = fields.Boolean(
        string='Enable DND',
        default=True,
        help='Prevent SMS sending during DND hours'
    )

    dnd_start_hour = fields.Integer(
        string='DND Start Hour',
        default=22,
        help='DND start hour (0-23)'
    )

    dnd_end_hour = fields.Integer(
        string='DND End Hour',
        default=8,
        help='DND end hour (0-23)'
    )

    # ========== STATISTICS ==========
    total_sent_count = fields.Integer(
        string='Total Sent',
        compute='_compute_statistics',
        help='Total SMS sent through this provider'
    )

    total_delivered_count = fields.Integer(
        string='Total Delivered',
        compute='_compute_statistics',
        help='Total SMS delivered'
    )

    total_failed_count = fields.Integer(
        string='Total Failed',
        compute='_compute_statistics',
        help='Total SMS failed'
    )

    delivery_rate = fields.Float(
        string='Delivery Rate (%)',
        compute='_compute_statistics',
        help='Percentage of delivered messages'
    )

    # ========== COMPUTE METHODS ==========
    @api.depends('name')
    def _compute_statistics(self):
        """Compute provider statistics from sms.message"""
        for provider in self:
            messages = self.env['sms.message'].search([
                ('provider_id', '=', provider.id)
            ])

            provider.total_sent_count = len(messages.filtered(
                lambda m: m.state in ['sent', 'delivered']
            ))
            provider.total_delivered_count = len(messages.filtered(
                lambda m: m.state == 'delivered'
            ))
            provider.total_failed_count = len(messages.filtered(
                lambda m: m.state in ['error', 'rejected']
            ))

            # Calculate delivery rate
            if provider.total_sent_count > 0:
                provider.delivery_rate = (
                    provider.total_delivered_count / provider.total_sent_count
                ) * 100
            else:
                provider.delivery_rate = 0.0

    # ========== BALANCE METHODS ==========
    def update_balance(self):
        """
        Update provider balance
        This method should be implemented by specific provider modules
        (like sms_kolmeya) but we provide a hook here
        """
        self.ensure_one()

        # Update last check time
        self.balance_last_check = fields.Datetime.now()

        # If balance field exists (from sms_kolmeya), check threshold
        if hasattr(self, 'balance') and self.balance_warning_enabled:
            if self.balance < self.balance_warning_threshold:
                self._send_balance_warning()

        _logger.info(f"Balance updated for provider {self.name}")

    def _send_balance_warning(self):
        """Send warning notification when balance is low"""
        self.ensure_one()

        if not self.balance_warning_user_ids:
            _logger.warning(f"No warning recipients configured for provider {self.name}")
            return

        # Create activity for each user
        for user in self.balance_warning_user_ids:
            self.activity_schedule(
                'mail.mail_activity_data_warning',
                user_id=user.id,
                summary=_('Low SMS Balance Warning'),
                note=_(
                    'Provider "%s" balance is low: R$ %.2f\n'
                    'Threshold: R$ %.2f\n\n'
                    'Please recharge to avoid service interruption.'
                ) % (
                    self.name,
                    self.balance if hasattr(self, 'balance') else 0.0,
                    self.balance_warning_threshold
                )
            )

        _logger.warning(
            f"Low balance warning sent for provider {self.name}: "
            f"R$ {self.balance if hasattr(self, 'balance') else 0.0}"
        )

    @api.model
    def cron_check_balance(self):
        """
        Cron job to check balance of all active providers
        Should run every 6 hours
        """
        providers = self.search([
            ('balance_warning_enabled', '=', True)
        ])

        for provider in providers:
            try:
                provider.update_balance()
            except Exception as e:
                _logger.error(f"Error checking balance for {provider.name}: {e}")

    # ========== DND METHODS ==========
    def is_dnd_time(self):
        """
        Check if current time is within DND hours
        Returns True if should NOT send SMS
        """
        self.ensure_one()

        if not self.dnd_enabled:
            return False

        current_hour = fields.Datetime.now().hour

        # Handle overnight DND (e.g., 22:00 to 08:00)
        if self.dnd_start_hour > self.dnd_end_hour:
            return current_hour >= self.dnd_start_hour or current_hour < self.dnd_end_hour
        # Normal DND (e.g., 12:00 to 14:00)
        else:
            return self.dnd_start_hour <= current_hour < self.dnd_end_hour

    # ========== ACTION METHODS ==========
    def action_view_messages(self):
        """View all messages sent through this provider"""
        self.ensure_one()

        return {
            'name': _('SMS Messages'),
            'type': 'ir.actions.act_window',
            'res_model': 'sms.message',
            'view_mode': 'tree,form',
            'domain': [('provider_id', '=', self.id)],
            'context': {'default_provider_id': self.id}
        }

    def action_check_balance_now(self):
        """Manual balance check"""
        self.ensure_one()
        self.update_balance()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Balance Updated'),
                'message': _('Balance check completed'),
                'type': 'success',
            }
        }
