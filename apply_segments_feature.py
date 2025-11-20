#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para aplicar funcionalidade de cálculo de segmentos
"""

import sys
import re

# 1. MODIFICAR sms_provider.py
provider_file = '/tmp/sms_provider_current.py'
with open(provider_file, 'r') as f:
    provider_content = f.read()

# Adicionar campo cost_per_segment após dnd_end_hour
cost_per_segment_field = """    dnd_end_hour = fields.Integer(string='DND End Hour', default=8)

    # Cost Configuration
    cost_per_segment = fields.Float(
        string='Cost per Segment (R$)',
        default=0.10,
        digits=(10, 4),
        help='Cost per SMS segment (160 characters)'
    )
"""

if 'cost_per_segment' not in provider_content:
    provider_content = provider_content.replace(
        "    dnd_end_hour = fields.Integer(string='DND End Hour', default=8)\n",
        cost_per_segment_field
    )
    print("✅ Campo cost_per_segment adicionado")

# Adicionar método calculate_sms_segments antes de action_test_connection
calculate_method = """    def calculate_sms_segments(self, message_body):
        \"\"\"
        Calculate SMS segments using Kolmeya API
        
        Args:
            message_body (str): Message content
            
        Returns:
            dict: {
                'segments': int,
                'total_chars': int,
                'chars_per_segment': int,
                'estimated_cost': float,
                'error': str (optional)
            }
        \"\"\"
        self.ensure_one()
        
        if not self.kolmeya_api_key:
            # Fallback: simple calculation
            segment_count = (len(message_body) // 160) + 1
            return {
                'segments': segment_count,
                'total_chars': len(message_body),
                'chars_per_segment': 160,
                'estimated_cost': segment_count * (self.cost_per_segment or 0.10),
                'error': 'API key not configured - using fallback calculation'
            }
        
        try:
            response = requests.post(
                f'{self.kolmeya_api_url}/sms/segments',
                json={'message': message_body},
                headers={
                    'Authorization': f'Bearer {self.kolmeya_api_key}',
                    'Content-Type': 'application/json'
                },
                timeout=self.timeout_seconds
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract segment information
            segments_data = result.get('segments', [])
            segment_count = len(segments_data) if isinstance(segments_data, list) else 1
            
            # Calculate estimated cost
            cost_per_segment = self.cost_per_segment or 0.10
            estimated_cost = segment_count * cost_per_segment
            
            return {
                'segments': segment_count,
                'total_chars': len(message_body),
                'chars_per_segment': 160,
                'estimated_cost': estimated_cost,
                'segments_data': segments_data
            }
            
        except requests.exceptions.RequestException as e:
            _logger.warning(f'Error calculating segments via API: {str(e)}. Using fallback calculation.')
            # Fallback: simple calculation
            segment_count = (len(message_body) // 160) + 1
            cost_per_segment = self.cost_per_segment or 0.10
            return {
                'segments': segment_count,
                'total_chars': len(message_body),
                'chars_per_segment': 160,
                'estimated_cost': segment_count * cost_per_segment,
                'error': f'API error: {str(e)} - using fallback'
            }

"""

if 'def calculate_sms_segments' not in provider_content:
    provider_content = provider_content.replace(
        "    def action_test_connection(self):",
        calculate_method + "    def action_test_connection(self):"
    )
    print("✅ Método calculate_sms_segments adicionado")

# Salvar provider modificado
with open('/tmp/sms_provider_modified.py', 'w') as f:
    f.write(provider_content)

# 2. MODIFICAR sms_message.py
message_file = '/tmp/sms_message_current.py'
with open(message_file, 'r') as f:
    message_content = f.read()

# Adicionar campos de segmentos após cost
segment_fields = """    cost = fields.Float(string='Cost (R$)', digits=(10, 4), readonly=True)
    
    # Segment Information
    segment_count = fields.Integer(
        string='Segments',
        readonly=True,
        help='Number of SMS segments (160 characters per segment)'
    )
    
    estimated_cost = fields.Float(
        string='Estimated Cost (R$)',
        digits=(10, 4),
        readonly=True,
        help='Estimated cost based on segments before sending'
    )
    
    actual_cost = fields.Float(
        string='Actual Cost (R$)',
        digits=(10, 4),
        readonly=True,
        help='Actual cost after sending (updated from provider response)'
    )
"""

if 'segment_count' not in message_content:
    message_content = message_content.replace(
        "    cost = fields.Float(string='Cost (R$)', digits=(10, 4), readonly=True)\n    delivery_date",
        segment_fields + "    delivery_date"
    )
    print("✅ Campos de segmentos adicionados em sms.message")

# Atualizar action_send para calcular segmentos
action_send_update = """    def action_send(self):
        \"\"\"
        Send SMS with segment calculation
        \"\"\"
        self.ensure_one()
        
        if self.state not in ['draft', 'error']:
            raise UserError(_('Apenas SMS rascunho ou com erro podem ser enviados.'))
        
        # Calculate segments before sending
        if self.provider_id:
            segment_info = self.provider_id.calculate_sms_segments(self.body)
            self.write({
                'segment_count': segment_info['segments'],
                'estimated_cost': segment_info['estimated_cost']
            })
        
        # Continue with normal send process
        self.write({
            'state': 'outgoing',
            'sent_date': fields.Datetime.now()
        })
        
        # Simular sucesso (implementação real virá depois)
        self.write({
            'state': 'sent',
            'external_id': f'demo_{self.id}',
            'error_message': False,
            'actual_cost': self.estimated_cost or 0.0
        })
        
        _logger.info(f'SMS {self.id} enviado com sucesso (simulado)')
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('SMS Sent'),
                'message': _('SMS sent successfully to %s (%d segments, R$ %.2f)') % (
                    self.phone,
                    self.segment_count or 1,
                    self.estimated_cost or 0.0
                ),
                'type': 'success'
            }
        }
"""

if 'segment_info = self.provider_id.calculate_sms_segments' not in message_content:
    # Encontrar e substituir action_send
    pattern = r'    def action_send\(self\):.*?        \}\n'
    message_content = re.sub(pattern, action_send_update, message_content, flags=re.DOTALL)
    print("✅ Método action_send atualizado com cálculo de segmentos")

# Salvar message modificado
with open('/tmp/sms_message_modified.py', 'w') as f:
    f.write(message_content)

print("\n✅ Arquivos modificados criados:")
print("   - /tmp/sms_provider_modified.py")
print("   - /tmp/sms_message_modified.py")

