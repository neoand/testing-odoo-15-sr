# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .kolmeya_api import KolmeyaAPI
import logging

_logger = logging.getLogger(__name__)


class SMSProviderKolmeya(models.Model):
    _inherit = 'sms.provider'

    provider_type = fields.Selection(selection_add=[('kolmeya', 'Kolmeya')], ondelete={'kolmeya': 'cascade'})

    # Kolmeya-specific configuration
    kolmeya_api_token = fields.Char(
        'API Token',
        groups='base.group_system',
        help='Bearer token from Kolmeya (e.g., Bearer xxxxx...)'
    )
    kolmeya_segment_id = fields.Integer(
        'Segment ID',
        default=109,
        help='Kolmeya segment/cost center ID (default: 109 - CORPORATIVO)'
    )
    kolmeya_webhook_secret = fields.Char(
        'Webhook JWT Secret',
        groups='base.group_system',
        help='Secret for validating webhook signatures'
    )

    # Statistics
    kolmeya_balance = fields.Float('Balance (R$)', readonly=True)
    last_balance_check = fields.Datetime('Last Balance Check', readonly=True)

    def _send_sms(self, sms_message):
        """Send single SMS via Kolmeya"""
        self.ensure_one()

        if self.provider_type != 'kolmeya':
            return super()._send_sms(sms_message)

        if not self.kolmeya_api_token:
            raise UserError(_('Kolmeya API token not configured'))

        try:
            api = KolmeyaAPI(self.kolmeya_api_token, self.kolmeya_segment_id)

            # Clean phone number
            clean_phone = sms_message.phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

            # Send single message
            result = api.send_sms(
                phone=clean_phone,
                message=sms_message.body,
                reference=str(sms_message.id)
            )

            # Update SMS message
            if result.get('valids'):
                valid_msg = result['valids'][0]
                sms_message.write({
                    'state': 'sent',
                    'provider_message_id': valid_msg.get('id'),
                    'provider_job_id': result.get('id'),
                    'provider_reference': str(sms_message.id),
                    'sent_date': fields.Datetime.now()
                })
            elif result.get('invalids'):
                sms_message.write({
                    'state': 'error',
                    'error_message': 'Invalid phone number'
                })
            elif result.get('blacklist'):
                sms_message.write({
                    'state': 'rejected',
                    'error_message': 'Phone number in blacklist'
                })

            return result

        except Exception as e:
            _logger.error(f"Kolmeya SMS send error: {e}")
            sms_message.write({
                'state': 'error',
                'error_message': str(e)
            })
            raise

    def _send_batch(self, messages_data):
        """
        Send batch of SMS via Kolmeya

        Args:
            messages_data: list of dicts with 'phone', 'message', 'reference'

        Returns:
            dict: Response from Kolmeya
        """
        self.ensure_one()

        if self.provider_type != 'kolmeya':
            return super()._send_batch(messages_data)

        if not self.kolmeya_api_token:
            raise UserError(_('Kolmeya API token not configured'))

        try:
            api = KolmeyaAPI(self.kolmeya_api_token, self.kolmeya_segment_id)

            # Clean phone numbers in messages
            for msg_data in messages_data:
                msg_data['phone'] = msg_data['phone'].replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

            # Send batch (Kolmeya supports up to 1000 per batch)
            result = api.send_batch(messages_data)

            _logger.info(f"Kolmeya batch sent: {len(messages_data)} messages, Job ID: {result.get('id')}")

            return result

        except Exception as e:
            _logger.error(f"Kolmeya batch send error: {e}")
            raise

    def action_check_balance(self):
        """Check Kolmeya balance"""
        self.ensure_one()

        if self.provider_type != 'kolmeya':
            return

        if not self.kolmeya_api_token:
            raise UserError(_('Kolmeya API token not configured'))

        try:
            api = KolmeyaAPI(self.kolmeya_api_token, self.kolmeya_segment_id)
            balance_data = api.get_balance()

            self.write({
                'kolmeya_balance': balance_data.get('saldo', 0.0),
                'last_balance_check': fields.Datetime.now()
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Balance Check'),
                    'message': _('Current balance: R$ %.2f') % balance_data.get('saldo', 0.0),
                    'type': 'success',
                }
            }

        except Exception as e:
            raise UserError(_('Failed to check balance: %s') % str(e))

    def action_check_job_status(self):
        """Check status of recent jobs"""
        self.ensure_one()

        if self.provider_type != 'kolmeya':
            return

        # This would open a wizard to enter job ID and check status
        return {
            'name': _('Check Job Status'),
            'type': 'ir.actions.act_window',
            'res_model': 'kolmeya.job.status.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_provider_id': self.id}
        }
