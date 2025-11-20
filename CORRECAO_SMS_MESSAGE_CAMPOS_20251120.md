# 🔧 Correção: Campos Faltantes em sms.message

> **Data:** 2025-11-20
> **Erro:** `Modelo não encontrado: sms.campaign`

---

## 🐛 Problema Identificado

O modelo `sms.message` estava faltando campos que são referenciados pelos models avançados:

- ❌ `campaign_id` - Referenciado por `sms.campaign`
- ❌ `scheduled_id` - Referenciado por `sms.scheduled`
- ❌ `provider_id` - Referenciado por ambos
- ❌ `cost` - Para estatísticas
- ❌ `delivery_date` - Para tracking

---

## ✅ Solução Aplicada

Adicionados os campos faltantes ao modelo `sms.message`:

```python
# Relacionamentos com campanhas e agendamentos
campaign_id = fields.Many2one('sms.campaign', string='Campaign', ondelete='set null', tracking=True)
scheduled_id = fields.Many2one('sms.scheduled', string='Scheduled Task', ondelete='set null', tracking=True)

# Provider
provider_id = fields.Many2one('sms.provider', string='SMS Provider', tracking=True)

# Campos adicionais para estatísticas
cost = fields.Float(string='Cost (R$)', digits=(10, 4), readonly=True)
delivery_date = fields.Datetime(string='Delivery Date', readonly=True)
```

---

## 📋 Status

- ✅ Campos adicionados
- ✅ Cache limpo
- ✅ Pronto para atualizar módulo

---

**Próximo passo:** Atualizar o módulo `sms_core_unified` via interface web.

