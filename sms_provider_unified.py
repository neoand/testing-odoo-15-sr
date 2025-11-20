# -*- coding: utf-8 -*-
"""
SMS Provider Model - UNIFIED VERSION
==================================

Unifica funcionalidade de:
- sms_base_sr/models/sms_provider.py (provider base)
- sms_kolmeya/models/sms_provider_kolmeya.py (Kolmeya specific)

PARA: /odoo/custom/addons_custom/sms_core_unified/models/sms_provider.py
"""

from odoo import models, fields, api, _
import logging
import requests
import jwt
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class SMSProvider(models.Model):
    """
    UNIFIED SMS Provider Model
    """
    _name = 'sms.provider'
    _description = 'SMS Provider - Unified Configuration'
    _order = 'sequence, name'

    name = fields.Char(string='Provider Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string='Description')

    # Provider Type
    provider_type = fields.Selection([
        ('kolmeya', 'Kolmeya'),
        ('twilio', 'Twilio'),
        ('aws_sns', 'AWS SNS'),
        ('custom', 'Custom API'),
    ], string='Provider Type', required=True, default='kolmeya')

    # Kolmeya Specific Configuration
    kolmeya_api_url = fields.Char(string='Kolmeya API URL', default='https://api.kolmeya.com/v1')
    kolmeya_api_key = fields.Char(string='Kolmeya API Key')
    kolmeya_webhook_secret = fields.Char(string='Webhook Secret')

    # General Configuration
    default_from = fields.Char(string='Default From Number')
    max_retries = fields.Integer(string='Max Retries', default=3)
    timeout_seconds = fields.Integer(string='Timeout (seconds)', default=30)

    # Statistics
    total_sent = fields.Integer(string='Total Sent', readonly=True)
    total_failed = fields.Integer(string='Total Failed', readonly=True)
    last_used = fields.Datetime(string='Last Used', readonly=True)

    @api.model
    def _send_sms_unified(self, sms_record):
        """
        UNIFIED send method - routes to appropriate provider
        This RESOLVES provider conflicts between modules
        """
        self.ensure_one()

        try:
            if self.provider_type == 'kolmeya':
                return self._send_kolmeya_unified(sms_record)
            elif self.provider_type == 'twilio':
                return self._send_twilio_unified(sms_record)
            elif self.provider_type == 'aws_sns':
                return self._send_aws_sns_unified(sms_record)
            else:
                return self._send_custom_unified(sms_record)

        except Exception as e:
            _logger.error(f'Provider {self.name} send failed: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def _send_kolmeya_unified(self, sms_record):
        """
        UNIFIED Kolmeya send - combines sms_kolmeya + sms_base_sr functionality
        """
        if not self.kolmeya_api_key:
            return {'success': False, 'error': 'Kolmeya API key not configured'}

        # Prepare data (from sms_kolmeya + enhanced)
        data = {
            'phone': sms_record.phone,
            'message': sms_record.body,
            'from': self.default_from or 'SempreReal',
            'external_id': str(sms_record.id),
            'callback_url': self._get_webhook_url(),
        }

        # Send request (enhanced error handling from sms_kolmeya)
        try:
            response = requests.post(
                f'{self.kolmeya_api_url}/sms/send',
                json=data,
                headers={
                    'Authorization': f'Bearer {self.kolmeya_api_key}',
                    'Content-Type': 'application/json'
                },
                timeout=self.timeout_seconds
            )

            response.raise_for_status()
            result = response.json()

            # Update statistics (from sms_base_sr)
            self.write({
                'total_sent': self.total_sent + 1,
                'last_used': fields.Datetime.now()
            })

            _logger.info(f'Kolmeya SMS sent: {result}')

            return {
                'success': True,
                'external_id': result.get('message_id'),
                'provider_response': result
            }

        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Kolmeya API timeout'}
        except requests.exceptions.RequestException as e:
            _logger.error(f'Kolmeya API error: {str(e)}')
            return {'success': False, 'error': f'Kolmeya API error: {str(e)}'}

    def _send_twilio_unified(self, sms_record):
        """Twilio provider implementation (future)"""
        return {'success': False, 'error': 'Twilio provider not implemented yet'}

    def _send_aws_sns_unified(self, sms_record):
        """AWS SNS provider implementation (future)"""
        return {'success': False, 'error': 'AWS SNS provider not implemented yet'}

    def _send_custom_unified(self, sms_record):
        """Custom API provider implementation (future)"""
        return {'success': False, 'error': 'Custom provider not implemented yet'}

    def _get_webhook_url(self):
        """Generate webhook URL for delivery receipts"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f'{base_url}/sms/webhook/kolmeya'

    @api.model
    def get_default_provider(self):
        """Get active default provider"""
        provider = self.search([
            ('active', '=', True),
            ('provider_type', '!=', False)
        ], order='sequence', limit=1)

        return provider or self.browse()

    def action_test_connection(self):
        """Test provider connection"""
        self.ensure_one()

        try:
            if self.provider_type == 'kolmeya':
                # Test Kolmeya API connection
                response = requests.get(
                    f'{self.kolmeya_api_url}/status',
                    headers={'Authorization': f'Bearer {self.kolmeya_api_key}'},
                    timeout=10
                )

                if response.status_code == 200:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Connection Test'),
                            'message': _('Successfully connected to Kolmeya API'),
                            'type': 'success'
                        }
                    }
                else:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Connection Test Failed'),
                            'message': _('Kolmeya API returned status: %s') % response.status_code,
                            'type': 'warning'
                        }
                    }

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Test Failed'),
                    'message': _('Error connecting to provider: %s') % str(e),
                    'type': 'danger'
                }
            }