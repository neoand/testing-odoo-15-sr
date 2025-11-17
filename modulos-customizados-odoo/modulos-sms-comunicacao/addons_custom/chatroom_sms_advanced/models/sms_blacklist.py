# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SMSBlacklist(models.Model):
    """
    SMS Blacklist (Do Not Disturb)
    - Prevent SMS sending to blacklisted numbers
    - Sync with provider blacklist (Kolmeya)
    - Track blacklist reasons
    """
    _name = 'sms.blacklist'
    _description = 'SMS Blacklist'
    _order = 'create_date desc'

    # ========== BASIC INFO ==========
    phone = fields.Char(
        string='Phone Number',
        required=True,
        index=True,
        help='Phone number in format: +5511999999999 or 11999999999'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        index=True,
        help='Related partner if available'
    )

    # ========== REASON ==========
    reason = fields.Selection([
        ('user_request', 'User Request'),
        ('auto_bounce', 'Auto Bounce'),
        ('manual', 'Manual'),
        ('legal', 'Legal Requirement'),
    ], string='Reason', required=True, default='manual')

    notes = fields.Text(
        string='Notes',
        help='Additional information about why this number is blacklisted'
    )

    # ========== SYNC ==========
    synced_kolmeya = fields.Boolean(
        string='Synced with Kolmeya',
        default=False,
        readonly=True,
        help='True if synced with Kolmeya provider blacklist'
    )

    last_sync_date = fields.Datetime(
        string='Last Sync Date',
        readonly=True
    )

    # ========== TRACKING ==========
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck to temporarily disable without deleting'
    )

    create_date = fields.Datetime(
        string='Created On',
        readonly=True
    )

    create_uid = fields.Many2one(
        'res.users',
        string='Created By',
        readonly=True
    )

    # ========== SQL CONSTRAINTS ==========
    _sql_constraints = [
        ('phone_unique', 'unique(phone)', 'This phone number is already in the blacklist!')
    ]

    # ========== VALIDATION ==========
    @api.constrains('phone')
    def _check_phone_format(self):
        """Validate phone format"""
        for record in self:
            if not record.phone:
                continue

            # Remove common separators
            phone = record.phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

            # Check if contains only digits and optional +
            if not phone.replace('+', '').isdigit():
                raise ValidationError(_('Phone number must contain only digits and optional + prefix'))

            # Minimum length check
            if len(phone.replace('+', '')) < 10:
                raise ValidationError(_('Phone number must have at least 10 digits'))

    # ========== CREATE/WRITE OVERRIDE ==========
    @api.model
    def create(self, vals):
        """Override create to auto-sync with Kolmeya"""
        # Normalize phone before creating
        if 'phone' in vals:
            vals['phone'] = self._normalize_phone(vals['phone'])

        record = super(SMSBlacklist, self).create(vals)

        # Auto-sync with Kolmeya if available
        try:
            record.sync_to_kolmeya()
        except Exception as e:
            _logger.warning(f"Could not auto-sync blacklist to Kolmeya: {e}")

        return record

    def write(self, vals):
        """Override write to re-sync if phone changes"""
        # Normalize phone if being updated
        if 'phone' in vals:
            vals['phone'] = self._normalize_phone(vals['phone'])

        result = super(SMSBlacklist, self).write(vals)

        # Re-sync if phone changed or activated
        if 'phone' in vals or ('active' in vals and vals['active']):
            try:
                self.sync_to_kolmeya()
            except Exception as e:
                _logger.warning(f"Could not re-sync blacklist to Kolmeya: {e}")

        return result

    # ========== UTILITY METHODS ==========
    @staticmethod
    def _normalize_phone(phone):
        """Normalize phone number format"""
        if not phone:
            return phone

        # Remove all non-digit characters except +
        normalized = ''.join(c for c in phone if c.isdigit() or c == '+')

        # Ensure Brazilian format if not international
        if not normalized.startswith('+'):
            # If 11 digits and doesn't start with +, add +55
            if len(normalized) == 11:
                normalized = '+55' + normalized
            # If 10 digits, might need to add 9
            elif len(normalized) == 10:
                normalized = '+55' + normalized

        return normalized

    @api.model
    def is_blacklisted(self, phone):
        """
        Check if a phone number is blacklisted
        Returns: (is_blacklisted, reason)
        """
        if not phone:
            return False, None

        normalized_phone = self._normalize_phone(phone)

        blacklist = self.search([
            ('phone', '=', normalized_phone),
            ('active', '=', True)
        ], limit=1)

        if blacklist:
            return True, blacklist.reason
        return False, None

    @api.model
    def add_to_blacklist(self, phone, reason='manual', notes=None, partner_id=None):
        """
        Add phone to blacklist
        Returns: blacklist record
        """
        normalized_phone = self._normalize_phone(phone)

        # Check if already exists
        existing = self.search([('phone', '=', normalized_phone)], limit=1)
        if existing:
            if not existing.active:
                existing.write({
                    'active': True,
                    'reason': reason,
                    'notes': notes,
                })
                _logger.info(f"Reactivated blacklist for {normalized_phone}")
                return existing
            else:
                _logger.warning(f"Phone {normalized_phone} already in blacklist")
                return existing

        # Create new blacklist entry
        return self.create({
            'phone': normalized_phone,
            'partner_id': partner_id,
            'reason': reason,
            'notes': notes,
        })

    # ========== SYNC WITH KOLMEYA ==========
    def sync_to_kolmeya(self):
        """
        Sync blacklist to Kolmeya provider
        Uses KolmeyaAPI from sms_kolmeya module
        """
        if not self:
            return

        # Find active Kolmeya provider
        provider = self.env['sms.provider'].search([
            ('active', '=', True),
        ], limit=1)

        if not provider:
            _logger.warning("No active SMS provider found for blacklist sync")
            return

        # Check if provider has Kolmeya integration
        if not hasattr(provider, 'kolmeya_api_token'):
            _logger.warning("Provider does not have Kolmeya integration")
            return

        try:
            # Import KolmeyaAPI
            from odoo.addons.sms_kolmeya.models.kolmeya_api import KolmeyaAPI

            # Initialize API
            api = KolmeyaAPI(
                provider.kolmeya_api_token,
                provider.kolmeya_segment_id if hasattr(provider, 'kolmeya_segment_id') else None
            )

            # Filter records that need sync
            to_sync = self.filtered(lambda r: not r.synced_kolmeya and r.active)
            if not to_sync:
                _logger.info("No blacklist records to sync")
                return

            # Prepare phone list
            phone_list = [record.phone for record in to_sync]

            # Sync to Kolmeya
            # Note: Actual API method depends on sms_kolmeya implementation
            # This is a placeholder - adjust based on actual API
            if hasattr(api, 'add_to_blacklist'):
                result = api.add_to_blacklist(phone_list)
                _logger.info(f"Synced {len(phone_list)} phones to Kolmeya blacklist: {result}")
            else:
                _logger.warning("Kolmeya API does not support blacklist management")

            # Mark as synced
            to_sync.write({
                'synced_kolmeya': True,
                'last_sync_date': fields.Datetime.now(),
            })

        except ImportError:
            _logger.error("Could not import KolmeyaAPI - sms_kolmeya module not available")
        except Exception as e:
            _logger.error(f"Error syncing blacklist to Kolmeya: {e}")
            raise

    def action_remove_from_blacklist(self):
        """Remove from blacklist (deactivate)"""
        for record in self:
            record.active = False
            _logger.info(f"Removed {record.phone} from blacklist")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Removed from Blacklist'),
                'message': _('%d phone number(s) removed') % len(self),
                'type': 'success',
            }
        }

    # ========== CRON ==========
    @api.model
    def cron_sync_blacklist(self):
        """
        Cron job to sync unsynced blacklist entries
        Runs every hour
        """
        to_sync = self.search([
            ('synced_kolmeya', '=', False),
            ('active', '=', True)
        ])

        if to_sync:
            _logger.info(f"Cron: syncing {len(to_sync)} blacklist entries")
            to_sync.sync_to_kolmeya()
        else:
            _logger.info("Cron: no blacklist entries to sync")

        return True
