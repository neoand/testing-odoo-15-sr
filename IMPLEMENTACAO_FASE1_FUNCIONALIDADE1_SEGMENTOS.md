# 📏 FASE 1 - Funcionalidade 1: Cálculo Inteligente de Segmentos

> **Data:** 2025-11-20
> **Prioridade:** 🔴 **ALTA**
> **Status:** 🚧 **EM DESENVOLVIMENTO**

---

## 🎯 **OBJETIVO**

Implementar cálculo automático de segmentos SMS antes do envio, permitindo:
- ✅ Custo exato antes de enviar
- ✅ Validação de tamanho de mensagem
- ✅ Prevenção de surpresas na fatura
- ✅ Exibição clara de quantos segmentos serão enviados

---

## 📋 **PLANO DE IMPLEMENTAÇÃO**

### **1. Adicionar Método de Cálculo de Segmentos**
- Endpoint: `POST /sms/segments`
- Método: `calculate_sms_segments()` em `sms_provider.py`

### **2. Adicionar Campos no Modelo SMS Message**
- `segment_count` - Quantidade de segmentos
- `estimated_cost` - Custo estimado baseado em segmentos

### **3. Atualizar Método de Envio**
- Calcular segmentos antes de enviar
- Armazenar segment_count no registro
- Calcular e armazenar estimated_cost

### **4. Atualizar Views**
- Mostrar segment_count na tree view
- Mostrar estimated_cost na form view
- Adicionar widget de preview com segmentos

### **5. Adicionar Validação**
- Validar tamanho máximo de mensagem
- Alertar se mensagem muito longa
- Sugerir otimização

---

## 🔧 **IMPLEMENTAÇÃO**

### **Passo 1: Método de Cálculo de Segmentos**

```python
def calculate_sms_segments(self, message_body):
    """
    Calculate SMS segments using Kolmeya API
    
    Args:
        message_body (str): Message content
        
    Returns:
        dict: {
            'segments': int,
            'total_chars': int,
            'chars_per_segment': int,
            'estimated_cost': float
        }
    """
    self.ensure_one()
    
    if not self.kolmeya_api_key:
        return {
            'segments': 1,
            'total_chars': len(message_body),
            'chars_per_segment': 160,
            'estimated_cost': 0.0,
            'error': 'API key not configured'
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
        
        # Calculate estimated cost (assuming R$ 0.10 per segment)
        cost_per_segment = 0.10  # TODO: Get from provider configuration
        estimated_cost = segment_count * cost_per_segment
        
        return {
            'segments': segment_count,
            'total_chars': len(message_body),
            'chars_per_segment': 160,
            'estimated_cost': estimated_cost,
            'segments_data': segments_data
        }
        
    except requests.exceptions.RequestException as e:
        _logger.error(f'Error calculating segments: {str(e)}')
        # Fallback: simple calculation
        segment_count = (len(message_body) // 160) + 1
        return {
            'segments': segment_count,
            'total_chars': len(message_body),
            'chars_per_segment': 160,
            'estimated_cost': segment_count * 0.10,
            'error': str(e)
        }
```

### **Passo 2: Campos no Modelo SMS Message**

```python
# Adicionar em sms_message.py
segment_count = fields.Integer(
    string='Segments',
    readonly=True,
    help='Number of SMS segments (160 chars per segment)'
)

estimated_cost = fields.Float(
    string='Estimated Cost (R$)',
    digits=(10, 2),
    readonly=True,
    help='Estimated cost based on segments'
)

actual_cost = fields.Float(
    string='Actual Cost (R$)',
    digits=(10, 2),
    readonly=True,
    help='Actual cost after sending'
)
```

### **Passo 3: Atualizar Método de Envio**

```python
def action_send(self):
    """Send SMS with segment calculation"""
    self.ensure_one()
    
    if not self.provider_id:
        raise UserError(_('Please select an SMS Provider'))
    
    # Calculate segments before sending
    segment_info = self.provider_id.calculate_sms_segments(self.body)
    
    # Update message with segment information
    self.write({
        'segment_count': segment_info['segments'],
        'estimated_cost': segment_info['estimated_cost']
    })
    
    # Continue with normal send process...
    # (resto do código de envio)
```

---

## 📝 **PRÓXIMOS PASSOS**

1. ✅ Implementar método `calculate_sms_segments()`
2. ⏳ Adicionar campos no modelo `sms.message`
3. ⏳ Atualizar método `action_send()`
4. ⏳ Atualizar views
5. ⏳ Adicionar validações
6. ⏳ Testar implementação

---

**Status:** 🚧 **Implementação iniciada**

