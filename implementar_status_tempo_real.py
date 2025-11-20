#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para implementar consulta de status em tempo real
FASE 1 - Funcionalidade 2
"""

import re

# 1. MODIFICAR sms_provider.py - Adicionar métodos de status
provider_file = '/tmp/sms_provider_current2.py'
with open(provider_file, 'r') as f:
    provider_content = f.read()

# Método para consultar status de mensagem específica
status_message_method = """
    def get_message_status(self, external_id):
        \"\"\"
        Get real-time status of a specific message from Kolmeya
        
        Args:
            external_id (str): External message ID from Kolmeya
            
        Returns:
            dict: {
                'status': str,
                'delivered_at': datetime (optional),
                'failed_at': datetime (optional),
                'error_message': str (optional),
                'raw_response': dict
            }
        \"\"\"
        self.ensure_one()
        
        if not self.kolmeya_api_key:
            return {
                'status': 'unknown',
                'error': 'API key not configured'
            }
        
        if self.provider_type != 'kolmeya':
            return {
                'status': 'unknown',
                'error': 'Status check only available for Kolmeya provider'
            }
        
        try:
            response = requests.post(
                f'{self.kolmeya_api_url}/sms/status/message',
                json={'message_id': external_id},
                headers={
                    'Authorization': f'Bearer {self.kolmeya_api_key}',
                    'Content-Type': 'application/json'
                },
                timeout=self.timeout_seconds
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Map Kolmeya status to Odoo states
            kolmeya_status = result.get('status', '').lower()
            status_map = {
                'sent': 'sent',
                'delivered': 'delivered',
                'failed': 'error',
                'pending': 'outgoing',
                'rejected': 'error'
            }
            
            odoo_status = status_map.get(kolmeya_status, 'unknown')
            
            return {
                'status': odoo_status,
                'delivered_at': result.get('delivered_at'),
                'failed_at': result.get('failed_at'),
                'error_message': result.get('error_message'),
                'raw_response': result
            }
            
        except requests.exceptions.RequestException as e:
            _logger.error(f'Error checking message status: {str(e)}')
            return {
                'status': 'unknown',
                'error': str(e)
            }

    def get_request_status(self, request_id):
        \"\"\"
        Get status of a request (batch of messages) from Kolmeya
        
        Args:
            request_id (str): Request ID from Kolmeya
            
        Returns:
            dict: Status information for the request
        \"\"\"
        self.ensure_one()
        
        if not self.kolmeya_api_key or self.provider_type != 'kolmeya':
            return {
                'status': 'unknown',
                'error': 'Status check only available for Kolmeya provider'
            }
        
        try:
            response = requests.post(
                f'{self.kolmeya_api_url}/sms/status/request',
                json={'request_id': request_id},
                headers={
                    'Authorization': f'Bearer {self.kolmeya_api_key}',
                    'Content-Type': 'application/json'
                },
                timeout=self.timeout_seconds
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            _logger.error(f'Error checking request status: {str(e)}')
            return {
                'status': 'unknown',
                'error': str(e)
            }

    @api.model
    def cron_update_message_statuses(self):
        \"\"\"
        Cron job to update status of pending/outgoing messages
        Should run every 5 minutes
        \"\"\"
        # Find messages that need status update
        messages = self.env['sms.message'].search([
            ('state', 'in', ['outgoing', 'sent']),
            ('external_id', '!=', False),
            ('provider_id.provider_type', '=', 'kolmeya')
        ], limit=100)  # Limit to avoid timeout
        
        updated_count = 0
        for message in messages:
            try:
                status_info = message.provider_id.get_message_status(message.external_id)
                
                if status_info.get('status') and status_info['status'] != 'unknown':
                    update_vals = {'state': status_info['status']}
                    
                    if status_info.get('delivered_at'):
                        update_vals['delivery_date'] = status_info['delivered_at']
                    
                    if status_info.get('error_message'):
                        update_vals['error_message'] = status_info['error_message']
                    
                    message.write(update_vals)
                    updated_count += 1
                    
            except Exception as e:
                _logger.error(f'Error updating status for message {message.id}: {str(e)}')
                continue
        
        _logger.info(f'Updated status for {updated_count} messages')
        return True

"""

# Adicionar métodos antes de action_test_connection
if 'def get_message_status' not in provider_content:
    provider_content = provider_content.replace(
        "    def action_test_connection(self):",
        status_message_method + "    def action_test_connection(self):"
    )
    print("✅ Métodos de status adicionados em sms_provider")

# Salvar provider modificado
with open('/tmp/sms_provider_status.py', 'w') as f:
    f.write(provider_content)

# 2. MODIFICAR sms_message.py - Adicionar método para atualizar status
message_file = '/tmp/sms_message_current2.py'
with open(message_file, 'r') as f:
    message_content = f.read()

# Método para atualizar status manualmente
update_status_method = """
    def action_check_status(self):
        \"\"\"
        Manually check and update message status from provider
        \"\"\"
        self.ensure_one()
        
        if not self.provider_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('No provider configured for this message'),
                    'type': 'warning'
                }
            }
        
        if not self.external_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Message has not been sent yet (no external ID)'),
                    'type': 'warning'
                }
            }
        
        # Get status from provider
        status_info = self.provider_id.get_message_status(self.external_id)
        
        if status_info.get('error'):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Status Check Failed'),
                    'message': _('Error checking status: %s') % status_info['error'],
                    'type': 'danger'
                }
            }
        
        # Update message with new status
        update_vals = {}
        if status_info.get('status'):
            update_vals['state'] = status_info['status']
        
        if status_info.get('delivered_at'):
            update_vals['delivery_date'] = status_info['delivered_at']
        
        if status_info.get('error_message'):
            update_vals['error_message'] = status_info['error_message']
        
        if update_vals:
            self.write(update_vals)
        
        # Show notification
        status_display = {
            'sent': _('Sent'),
            'delivered': _('Delivered'),
            'error': _('Error'),
            'outgoing': _('Outgoing'),
            'unknown': _('Unknown')
        }
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Status Updated'),
                'message': _('Message status: %s') % status_display.get(
                    status_info.get('status', 'unknown'),
                    status_info.get('status', 'unknown')
                ),
                'type': 'success'
            }
        }

"""

# Adicionar método após action_reset_to_draft
if 'def action_check_status' not in message_content:
    pattern = r'(    def action_reset_to_draft\(self\):.*?        \}\n)'
    replacement = r'\1' + update_status_method
    message_content = re.sub(pattern, replacement, message_content, flags=re.DOTALL)
    print("✅ Método action_check_status adicionado em sms_message")

# Salvar message modificado
with open('/tmp/sms_message_status.py', 'w') as f:
    f.write(message_content)

print("\n✅ Arquivos modificados criados:")
print("   - /tmp/sms_provider_status.py")
print("   - /tmp/sms_message_status.py")

