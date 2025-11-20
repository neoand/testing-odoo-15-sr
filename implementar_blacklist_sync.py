#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para implementar sincronização bidirecional de blacklist
FASE 1 - Funcionalidade 3
"""

import re

# 1. MODIFICAR sms_blacklist.py
blacklist_file = '/tmp/sms_blacklist_current.py'
with open(blacklist_file, 'r') as f:
    blacklist_content = f.read()

# Métodos para sincronização com Kolmeya
sync_methods = """
    def sync_to_kolmeya(self, provider_id=None):
        \"\"\"
        Sync this blacklist entry to Kolmeya provider
        
        Args:
            provider_id: Optional provider ID, if None uses default Kolmeya provider
        \"\"\"
        self.ensure_one()
        
        if not provider_id:
            provider = self.env['sms.provider'].search([
                ('active', '=', True),
                ('provider_type', '=', 'kolmeya'),
                ('kolmeya_api_key', '!=', False)
            ], limit=1)
        else:
            provider = provider_id
        
        if not provider:
            _logger.warning(f'No active Kolmeya provider found for blacklist sync')
            return False
        
        if not provider.kolmeya_api_key:
            _logger.warning(f'Kolmeya provider {provider.name} has no API key')
            return False
        
        try:
            response = requests.post(
                f'{provider.kolmeya_api_url}/blacklist/store',
                json={'phone': self.phone},
                headers={
                    'Authorization': f'Bearer {provider.kolmeya_api_key}',
                    'Content-Type': 'application/json'
                },
                timeout=provider.timeout_seconds
            )
            
            response.raise_for_status()
            _logger.info(f'Blacklist entry {self.phone} synced to Kolmeya')
            return True
            
        except requests.exceptions.RequestException as e:
            _logger.error(f'Error syncing blacklist entry {self.phone} to Kolmeya: {str(e)}')
            return False

    def remove_from_kolmeya(self, provider_id=None):
        \"\"\"
        Remove this blacklist entry from Kolmeya provider
        
        Args:
            provider_id: Optional provider ID, if None uses default Kolmeya provider
        \"\"\"
        self.ensure_one()
        
        if not provider_id:
            provider = self.env['sms.provider'].search([
                ('active', '=', True),
                ('provider_type', '=', 'kolmeya'),
                ('kolmeya_api_key', '!=', False)
            ], limit=1)
        else:
            provider = provider_id
        
        if not provider:
            _logger.warning(f'No active Kolmeya provider found for blacklist removal')
            return False
        
        try:
            response = requests.post(
                f'{provider.kolmeya_api_url}/blacklist/destroy',
                json={'phone': self.phone},
                headers={
                    'Authorization': f'Bearer {provider.kolmeya_api_key}',
                    'Content-Type': 'application/json'
                },
                timeout=provider.timeout_seconds
            )
            
            response.raise_for_status()
            _logger.info(f'Blacklist entry {self.phone} removed from Kolmeya')
            return True
            
        except requests.exceptions.RequestException as e:
            _logger.error(f'Error removing blacklist entry {self.phone} from Kolmeya: {str(e)}')
            return False

    @api.model
    def cron_sync_blacklist(self):
        \"\"\"
        Cron job to sync blacklist with Kolmeya provider
        Syncs all active blacklist entries to Kolmeya
        Should run every 1 hour
        \"\"\"
        _logger.info(\"Starting blacklist sync with Kolmeya...\")
        
        # Get default Kolmeya provider
        provider = self.env['sms.provider'].search([
            ('active', '=', True),
            ('provider_type', '=', 'kolmeya'),
            ('kolmeya_api_key', '!=', False)
        ], limit=1)
        
        if not provider:
            _logger.warning('No active Kolmeya provider found for blacklist sync')
            return False
        
        # Get all active blacklist entries
        blacklist_entries = self.search([('active', '=', True)])
        
        synced_count = 0
        failed_count = 0
        
        for entry in blacklist_entries:
            try:
                if entry.sync_to_kolmeya(provider):
                    synced_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                _logger.error(f'Error syncing blacklist entry {entry.phone}: {str(e)}')
                failed_count += 1
                continue
        
        _logger.info(f'Blacklist sync completed: {synced_count} synced, {failed_count} failed')
        return True

    def action_sync_to_kolmeya(self):
        \"\"\"
        Manual action to sync this blacklist entry to Kolmeya
        \"\"\"
        self.ensure_one()
        
        if self.sync_to_kolmeya():
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Blacklist Synced'),
                    'message': _('Blacklist entry %s synced to Kolmeya successfully') % self.phone,
                    'type': 'success'
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Failed'),
                    'message': _('Failed to sync blacklist entry to Kolmeya. Check logs for details.'),
                    'type': 'warning',
                    'sticky': True
                }
            }

    def action_remove_from_kolmeya(self):
        \"\"\"
        Manual action to remove this blacklist entry from Kolmeya
        \"\"\"
        self.ensure_one()
        
        if self.remove_from_kolmeya():
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Blacklist Removed'),
                    'message': _('Blacklist entry %s removed from Kolmeya successfully') % self.phone,
                    'type': 'success'
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Removal Failed'),
                    'message': _('Failed to remove blacklist entry from Kolmeya. Check logs for details.'),
                    'type': 'warning',
                    'sticky': True
                }
            }

    @api.model
    def create(self, vals):
        \"\"\"
        Override create to auto-sync to Kolmeya when entry is created
        \"\"\"
        record = super(SMSBlacklist, self).create(vals)
        
        # Auto-sync to Kolmeya if active
        if record.active:
            record.sync_to_kolmeya()
        
        return record

    def write(self, vals):
        \"\"\"
        Override write to sync changes to Kolmeya
        \"\"\"
        # If phone is being changed, remove old from Kolmeya
        if 'phone' in vals:
            for record in self:
                if record.phone:
                    record.remove_from_kolmeya()
        
        result = super(SMSBlacklist, self).write(vals)
        
        # Sync to Kolmeya if active
        if 'active' in vals and vals['active']:
            for record in self:
                record.sync_to_kolmeya()
        elif 'active' in vals and not vals['active']:
            # Remove from Kolmeya if deactivated
            for record in self:
                record.remove_from_kolmeya()
        
        return result

    def unlink(self):
        \"\"\"
        Override unlink to remove from Kolmeya before deletion
        \"\"\"
        # Remove from Kolmeya before deletion
        for record in self:
            record.remove_from_kolmeya()
        
        return super(SMSBlacklist, self).unlink()

"""

# Verificar se já tem import requests
if 'import requests' not in blacklist_content:
    # Adicionar import após outros imports
    blacklist_content = blacklist_content.replace(
        "from odoo import models, fields, api, _\nimport logging",
        "from odoo import models, fields, api, _\nimport logging\nimport requests"
    )
    print("✅ Import requests adicionado")

# Substituir método cron_sync_blacklist existente ou adicionar novos métodos
if 'def sync_to_kolmeya' not in blacklist_content:
    # Adicionar métodos antes do método cron_sync_blacklist existente
    if 'def cron_sync_blacklist' in blacklist_content:
        # Substituir método existente
        pattern = r'    @api\.model\s+def cron_sync_blacklist\(self\):.*?return True'
        replacement = sync_methods
        blacklist_content = re.sub(pattern, replacement, blacklist_content, flags=re.DOTALL)
        print("✅ Método cron_sync_blacklist substituído e novos métodos adicionados")
    else:
        # Adicionar no final da classe
        pattern = r'(    def increment_blocked_count\(self\):.*?        \}\n)'
        replacement = r'\1' + sync_methods
        blacklist_content = re.sub(pattern, replacement, blacklist_content, flags=re.DOTALL)
        print("✅ Métodos de sincronização adicionados")

# Salvar blacklist modificado
with open('/tmp/sms_blacklist_sync.py', 'w') as f:
    f.write(blacklist_content)

print("\n✅ Arquivo modificado criado:")
print("   - /tmp/sms_blacklist_sync.py")

