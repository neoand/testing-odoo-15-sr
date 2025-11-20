#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para implementar cálculo de segmentos SMS
FASE 1 - Funcionalidade 1
"""

# Adicionar campo cost_per_segment no provider
PROVIDER_FIELD_ADDITION = """
    # Cost Configuration
    cost_per_segment = fields.Float(
        string='Cost per Segment (R$)',
        default=0.10,
        digits=(10, 4),
        help='Cost per SMS segment (160 characters)'
    )
"""

# Método calculate_sms_segments para adicionar no provider
PROVIDER_METHOD = """
    def calculate_sms_segments(self, message_body):
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

# Campos para adicionar no sms.message
MESSAGE_FIELDS = """
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

if __name__ == '__main__':
    print("Script de implementação criado.")
    print("Use este script para aplicar as modificações nos arquivos.")

