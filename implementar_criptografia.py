#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para implementar criptografia de dados sensíveis
FASE 1 - Funcionalidade 8
"""

import re

# 1. MODIFICAR sms_provider.py - Adicionar criptografia
provider_file = '/tmp/sms_provider_current4.py'
with open(provider_file, 'r') as f:
    provider_content = f.read()

# Verificar se já tem import de criptografia
if 'from cryptography' not in provider_content and 'import base64' not in provider_content:
    # Adicionar imports
    provider_content = provider_content.replace(
        "import requests\nimport jwt\nfrom datetime import datetime, timedelta",
        "import requests\nimport jwt\nfrom datetime import datetime, timedelta\nimport base64\nfrom cryptography.fernet import Fernet\nfrom cryptography.hazmat.primitives import hashes\nfrom cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC\nimport os"
    )
    print("✅ Imports de criptografia adicionados")

# Métodos de criptografia
encryption_methods = """
    @api.model
    def _get_encryption_key(self):
        \"\"\"
        Get or generate encryption key for sensitive data
        Uses system parameter or generates new one
        \"\"\"
        # Get encryption key from system parameters
        key_param = self.env['ir.config_parameter'].sudo().get_param(
            'sms_core_unified.encryption_key'
        )
        
        if key_param:
            return key_param.encode()
        
        # Generate new key if not exists
        # In production, this should be set manually via system parameters
        password = b'sms_core_unified_default_key_change_in_production'
        salt = b'sms_core_unified_salt'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        
        # Store in system parameters
        self.env['ir.config_parameter'].sudo().set_param(
            'sms_core_unified.encryption_key',
            key.decode()
        )
        
        return key

    def _encrypt_field(self, value):
        \"\"\"
        Encrypt a sensitive field value
        
        Args:
            value (str): Value to encrypt
            
        Returns:
            str: Encrypted value (base64 encoded)
        \"\"\"
        if not value:
            return value
        
        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            encrypted = fernet.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            _logger.error(f'Error encrypting field: {str(e)}')
            return value  # Return original if encryption fails

    def _decrypt_field(self, encrypted_value):
        \"\"\"
        Decrypt a sensitive field value
        
        Args:
            encrypted_value (str): Encrypted value (base64 encoded)
            
        Returns:
            str: Decrypted value
        \"\"\"
        if not encrypted_value:
            return encrypted_value
        
        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            decoded = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted = fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            _logger.error(f'Error decrypting field: {str(e)}')
            return encrypted_value  # Return original if decryption fails

    @api.model
    def create(self, vals):
        \"\"\"
        Override create to encrypt sensitive fields
        \"\"\"
        # Encrypt API keys before saving
        if 'kolmeya_api_key' in vals and vals['kolmeya_api_key']:
            vals['kolmeya_api_key'] = self._encrypt_field(vals['kolmeya_api_key'])
        
        if 'kolmeya_webhook_secret' in vals and vals['kolmeya_webhook_secret']:
            vals['kolmeya_webhook_secret'] = self._encrypt_field(vals['kolmeya_webhook_secret'])
        
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
        Override write to encrypt sensitive fields
        \"\"\"
        # Encrypt API keys before saving
        if 'kolmeya_api_key' in vals and vals['kolmeya_api_key']:
            vals['kolmeya_api_key'] = self._encrypt_field(vals['kolmeya_api_key'])
        
        if 'kolmeya_webhook_secret' in vals and vals['kolmeya_webhook_secret']:
            vals['kolmeya_webhook_secret'] = self._encrypt_field(vals['kolmeya_webhook_secret'])
        
        result = super(SMSProvider, self).write(vals)
        
        # Re-configure webhook if API key was updated
        if 'kolmeya_api_key' in vals and self.provider_type == 'kolmeya' and vals['kolmeya_api_key']:
            try:
                self.configure_webhook()
            except Exception as e:
                _logger.warning(f'Failed to re-configure webhook for provider {self.name}: {str(e)}')
        
        return result

    def read(self, fields=None, load='_classic_read'):
        \"\"\"
        Override read to decrypt sensitive fields
        \"\"\"
        records = super(SMSProvider, self).read(fields=fields, load=load)
        
        # Decrypt API keys when reading
        for record in records:
            if 'kolmeya_api_key' in record and record['kolmeya_api_key']:
                try:
                    record['kolmeya_api_key'] = self._decrypt_field(record['kolmeya_api_key'])
                except:
                    pass  # If decryption fails, keep encrypted value
            
            if 'kolmeya_webhook_secret' in record and record['kolmeya_webhook_secret']:
                try:
                    record['kolmeya_webhook_secret'] = self._decrypt_field(record['kolmeya_webhook_secret'])
                except:
                    pass  # If decryption fails, keep encrypted value
        
        return records

"""

# Verificar se métodos de criptografia já existem
if 'def _encrypt_field' not in provider_content:
    # Adicionar métodos antes de create/write se já existirem
    if 'def create(self, vals):' in provider_content:
        # Substituir create/write existentes
        pattern = r'    @api\.model\s+def create\(self, vals\):.*?        return record\n\n    def write\(self, vals\):.*?        return result\n'
        if re.search(pattern, provider_content, re.DOTALL):
            # Substituir create/write existentes
            replacement = encryption_methods
            provider_content = re.sub(pattern, replacement, provider_content, flags=re.DOTALL)
            print("✅ Métodos de criptografia adicionados (substituindo create/write)")
        else:
            # Adicionar métodos antes de create
            provider_content = provider_content.replace(
                "    @api.model\n    def create(self, vals):",
                encryption_methods + "    @api.model\n    def create(self, vals):"
            )
            print("✅ Métodos de criptografia adicionados")
    else:
        # Adicionar no final antes do último método
        provider_content = provider_content.rstrip() + '\n' + encryption_methods + '\n'
        print("✅ Métodos de criptografia adicionados no final")

# Salvar provider modificado
with open('/tmp/sms_provider_encrypted.py', 'w') as f:
    f.write(provider_content)

print("\n✅ Arquivo modificado criado:")
print("   - /tmp/sms_provider_encrypted.py")

