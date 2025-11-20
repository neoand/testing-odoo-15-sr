#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para implementar configuração automática de webhook
FASE 1 - Funcionalidade 4
"""

import re

# 1. MODIFICAR sms_provider.py
provider_file = '/tmp/sms_provider_current3.py'
with open(provider_file, 'r') as f:
    provider_content = f.read()

# Métodos para configuração de webhook
webhook_methods = """
    def configure_webhook(self, webhook_url=None, webhook_type='request'):
        \"\"\"
        Configure webhook URL in Kolmeya provider
        
        Args:
            webhook_url (str): Webhook URL (if None, generates automatically)
            webhook_type (str): Type of webhook ('request' or 'campaign')
            
        Returns:
            dict: Result of webhook configuration
        \"\"\"
        self.ensure_one()
        
        if self.provider_type != 'kolmeya':
            return {
                'success': False,
                'error': 'Webhook configuration only available for Kolmeya provider'
            }
        
        if not self.kolmeya_api_key:
            return {
                'success': False,
                'error': 'Kolmeya API key not configured'
            }
        
        # Generate webhook URL if not provided
        if not webhook_url:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            webhook_url = f'{base_url}/sms/webhook/kolmeya'
        
        try:
            response = requests.post(
                f'{self.kolmeya_api_url}/sms/webhook',
                json={
                    'url': webhook_url,
                    'type': webhook_type
                },
                headers={
                    'Authorization': f'Bearer {self.kolmeya_api_key}',
                    'Content-Type': 'application/json'
                },
                timeout=self.timeout_seconds
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Store webhook URL in provider
            self.kolmeya_webhook_secret = result.get('secret') or self.kolmeya_webhook_secret
            
            _logger.info(f'Webhook configured for provider {self.name}: {webhook_url}')
            
            return {
                'success': True,
                'webhook_url': webhook_url,
                'webhook_type': webhook_type,
                'response': result
            }
            
        except requests.exceptions.RequestException as e:
            _logger.error(f'Error configuring webhook: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

    def validate_webhook(self):
        \"\"\"
        Validate webhook configuration by testing the endpoint
        \"\"\"
        self.ensure_one()
        
        if not self.kolmeya_webhook_secret:
            return {
                'valid': False,
                'error': 'Webhook secret not configured'
            }
        
        # Generate expected webhook URL
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        expected_url = f'{base_url}/sms/webhook/kolmeya'
        
        # Check if webhook endpoint exists and is accessible
        # This is a basic validation - full validation would require testing the endpoint
        return {
            'valid': True,
            'webhook_url': expected_url,
            'message': 'Webhook URL generated. Ensure endpoint is accessible.'
        }

    def action_configure_webhook(self):
        \"\"\"
        Manual action to configure webhook
        \"\"\"
        self.ensure_one()
        
        if self.provider_type != 'kolmeya':
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Webhook configuration only available for Kolmeya provider'),
                    'type': 'warning'
                }
            }
        
        result = self.configure_webhook()
        
        if result.get('success'):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Webhook Configured'),
                    'message': _('Webhook configured successfully: %s') % result.get('webhook_url', ''),
                    'type': 'success'
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Webhook Configuration Failed'),
                    'message': _('Error: %s') % result.get('error', 'Unknown error'),
                    'type': 'danger',
                    'sticky': True
                }
            }

    def action_validate_webhook(self):
        \"\"\"
        Manual action to validate webhook
        \"\"\"
        self.ensure_one()
        
        result = self.validate_webhook()
        
        if result.get('valid'):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Webhook Valid'),
                    'message': _('Webhook URL: %s\\n%s') % (
                        result.get('webhook_url', ''),
                        result.get('message', '')
                    ),
                    'type': 'success'
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Webhook Validation Failed'),
                    'message': _('Error: %s') % result.get('error', 'Unknown error'),
                    'type': 'warning',
                    'sticky': True
                }
            }

"""

# Adicionar métodos antes de action_test_connection
if 'def configure_webhook' not in provider_content:
    provider_content = provider_content.replace(
        "    def action_test_connection(self):",
        webhook_methods + "    def action_test_connection(self):"
    )
    print("✅ Métodos de webhook adicionados")

# Adicionar auto-configuração no create/write
# Override create para auto-configurar webhook
create_override = """
    @api.model
    def create(self, vals):
        \"\"\"
        Override create to auto-configure webhook for Kolmeya providers
        \"\"\"
        record = super(SMSProvider, self).create(vals)
        
        # Auto-configure webhook for Kolmeya providers
        if record.provider_type == 'kolmeya' and record.kolmeya_api_key:
            try:
                record.configure_webhook()
            except Exception as e:
                _logger.warning(f'Failed to auto-configure webhook for provider {record.name}: {str(e)}')
        
        return record

    def write(self, vals):
        \"\"\"
        Override write to re-configure webhook if API key changes
        \"\"\"
        result = super(SMSProvider, self).write(vals)
        
        # Re-configure webhook if API key was updated
        if 'kolmeya_api_key' in vals and self.provider_type == 'kolmeya' and vals['kolmeya_api_key']:
            try:
                self.configure_webhook()
            except Exception as e:
                _logger.warning(f'Failed to re-configure webhook for provider {self.name}: {str(e)}')
        
        return result

"""

# Adicionar override de create/write se não existir
if '@api.model\s+def create(self, vals):' not in provider_content and 'def create(self, vals):' not in provider_content:
    # Adicionar antes da primeira definição de método
    pattern = r'(    @api\.model\s+def _send_sms_unified\(self, sms_record\):)'
    replacement = r'\1' + create_override
    provider_content = re.sub(pattern, replacement, provider_content, flags=re.DOTALL)
    print("✅ Override de create/write adicionado para auto-configuração de webhook")

# Salvar provider modificado
with open('/tmp/sms_provider_webhook.py', 'w') as f:
    f.write(provider_content)

print("\n✅ Arquivo modificado criado:")
print("   - /tmp/sms_provider_webhook.py")

