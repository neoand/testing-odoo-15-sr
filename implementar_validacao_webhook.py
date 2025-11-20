#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para implementar validação de webhook
FASE 1 - Funcionalidade 9
"""

import re

# 1. MELHORAR sms_webhook.py - Adicionar validação completa
webhook_file = '/tmp/sms_webhook_current.py'
with open(webhook_file, 'r') as f:
    webhook_content = f.read()

# Melhorar método de validação de assinatura
validation_improvements = """
    def _verify_kolmeya_signature(self, payload, signature):
        \"\"\"
        Verify the X-Kolmeya-Signature header using HMAC-SHA256
        
        Args:
            payload (dict): Webhook payload
            signature (str): Signature from X-Kolmeya-Signature header
            
        Returns:
            bool: True if signature is valid
        \"\"\"
        if not signature:
            _logger.warning(\"Kolmeya Webhook: No signature provided\")
            return False
        
        # Get the secret from the provider configuration
        provider = http.request.env['sms.provider'].sudo().search([
            ('provider_type', '=', 'kolmeya'),
            ('kolmeya_webhook_secret', '!=', False),
            ('active', '=', True)
        ], limit=1)
        
        if not provider:
            _logger.warning(\"Kolmeya Webhook: No active Kolmeya provider with webhook secret found\")
            return False
        
        webhook_secret = provider.kolmeya_webhook_secret
        if not webhook_secret:
            _logger.warning(\"Kolmeya Webhook: No webhook secret configured\")
            return False
        
        try:
            # Recreate the signature
            # Kolmeya typically signs the raw request body
            import json
            signed_payload = json.dumps(payload, separators=(',', ':'))  # Ensure consistent JSON string
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                signed_payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Use constant-time comparison to prevent timing attacks
            is_valid = hmac.compare_digest(expected_signature, signature)
            
            if not is_valid:
                _logger.warning(f\"Kolmeya Webhook: Invalid signature. Expected: {expected_signature[:10]}..., Got: {signature[:10]}...\")
            
            return is_valid
            
        except Exception as e:
            _logger.error(f\"Kolmeya Webhook: Error verifying signature: {str(e)}\")
            return False

    def _validate_webhook_payload(self, payload):
        \"\"\"
        Validate webhook payload structure
        
        Args:
            payload (dict): Webhook payload
            
        Returns:
            tuple: (is_valid, error_message)
        \"\"\"
        if not isinstance(payload, dict):
            return False, 'Payload must be a dictionary'
        
        # Required fields for delivery receipt
        if 'message_id' not in payload:
            return False, 'Missing required field: message_id'
        
        if 'status' not in payload:
            return False, 'Missing required field: status'
        
        # Validate status values
        valid_statuses = ['sent', 'delivered', 'failed', 'pending', 'rejected']
        if payload.get('status') not in valid_statuses:
            return False, f'Invalid status: {payload.get(\"status\")}. Must be one of: {valid_statuses}'
        
        return True, None

    def _log_webhook_attempt(self, payload, is_valid, error_message=None):
        \"\"\"
        Log webhook attempt for security auditing
        
        Args:
            payload (dict): Webhook payload
            is_valid (bool): Whether webhook is valid
            error_message (str): Error message if invalid
        \"\"\"
        import json
        log_data = {
            'timestamp': fields.Datetime.now().isoformat(),
            'is_valid': is_valid,
            'message_id': payload.get('message_id'),
            'status': payload.get('status'),
            'ip_address': http.request.httprequest.remote_addr,
            'user_agent': http.request.httprequest.headers.get('User-Agent', 'Unknown')
        }
        
        if error_message:
            log_data['error'] = error_message
        
        _logger.info(f\"Webhook attempt logged: {json.dumps(log_data)}\")

"""

# Substituir método _verify_kolmeya_signature existente
if 'def _verify_kolmeya_signature(self, payload, signature):' in webhook_content:
    # Substituir método existente
    pattern = r'    def _verify_kolmeya_signature\(self, payload, signature\):.*?return hmac\.compare_digest\(expected_signature, signature\)'
    replacement = validation_improvements
    webhook_content = re.sub(pattern, replacement, webhook_content, flags=re.DOTALL)
    print("✅ Método _verify_kolmeya_signature melhorado")
else:
    # Adicionar métodos antes do método kolmeya_webhook
    webhook_content = webhook_content.replace(
        "    @http.route('/sms/webhook/kolmeya'",
        validation_improvements + "    @http.route('/sms/webhook/kolmeya'"
    )
    print("✅ Métodos de validação adicionados")

# Melhorar método kolmeya_webhook para usar validação
webhook_improvement = """
        # Validate webhook signature (if secret is configured)
        signature = http.request.httprequest.headers.get('X-Kolmeya-Signature')
        if signature:
            if not self._verify_kolmeya_signature(request_data, signature):
                self._log_webhook_attempt(request_data, False, 'Invalid signature')
                _logger.warning(\"Kolmeya Webhook: Invalid signature received.\")
                return {'status': 'error', 'message': 'Invalid signature'}
        
        # Validate payload structure
        is_valid, error_msg = self._validate_webhook_payload(request_data)
        if not is_valid:
            self._log_webhook_attempt(request_data, False, error_msg)
            _logger.warning(f\"Kolmeya Webhook: Invalid payload: {error_msg}\")
            return {'status': 'error', 'message': error_msg}
        
        # Log valid webhook attempt
        self._log_webhook_attempt(request_data, True)
"""

# Adicionar validação no início do método kolmeya_webhook
if 'def _validate_webhook_payload' in webhook_content:
    # Já tem validação, apenas melhorar
    pattern = r'(        request_data = http\.request\.jsonrequest\n        _logger\.info\(f\"Kolmeya Webhook received:.*?\n)'
    replacement = r'\1' + webhook_improvement
    webhook_content = re.sub(pattern, replacement, webhook_content, flags=re.DOTALL)
    print("✅ Validação adicionada ao método kolmeya_webhook")
else:
    # Adicionar validação
    pattern = r'(        request_data = http\.request\.jsonrequest\n        _logger\.info\(f\"Kolmeya Webhook received:.*?\n\n)'
    replacement = r'\1' + webhook_improvement
    webhook_content = re.sub(pattern, replacement, webhook_content, flags=re.DOTALL)
    print("✅ Validação adicionada ao método kolmeya_webhook")

# Verificar imports
if 'import hmac' not in webhook_content:
    webhook_content = webhook_content.replace(
        "import logging\nimport json\nimport hmac\nimport hashlib",
        "import logging\nimport json\nimport hmac\nimport hashlib\nfrom odoo import fields"
    )
    print("✅ Import fields adicionado")

# Salvar webhook modificado
with open('/tmp/sms_webhook_validated.py', 'w') as f:
    f.write(webhook_content)

print("\n✅ Arquivo modificado criado:")
print("   - /tmp/sms_webhook_validated.py")

