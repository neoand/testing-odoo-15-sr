# ✅ Correção: Campos de Balance no Modelo SMS Provider

> **Data:** 2025-11-20
> **Erro:** `O campo "balance" não existe no modelo "sms.provider"`

---

## 🐛 Problema Identificado

A view `sms_provider_views.xml` estava tentando usar campos que não existiam no modelo `sms.provider`:
- ❌ `balance`
- ❌ `balance_warning_enabled`
- ❌ `balance_warning_threshold`
- ❌ `balance_last_check`
- ❌ `balance_warning_user_ids`
- ❌ `dnd_enabled`
- ❌ `dnd_start_hour`
- ❌ `dnd_end_hour`

---

## ✅ Solução Aplicada

Adicionados os campos faltantes ao modelo `sms_provider.py`:

### **Campos de Balance:**
```python
# Balance
balance = fields.Float(string='Current Balance (R$)', readonly=True, default=0.0, digits=(10, 2))
balance_warning_enabled = fields.Boolean(string='Enable Balance Warning', default=True)
balance_warning_threshold = fields.Float(string='Balance Warning Threshold (R$)', default=100.0, digits=(10, 2))
balance_last_check = fields.Datetime(string='Last Balance Check', readonly=True)
balance_warning_user_ids = fields.Many2many(
    'res.users',
    'sms_provider_balance_warning_users_rel',
    'provider_id',
    'user_id',
    string='Warning Recipients'
)
```

### **Campos de DND (Do Not Disturb):**
```python
# DND (Do Not Disturb)
dnd_enabled = fields.Boolean(string='Enable DND', default=True)
dnd_start_hour = fields.Integer(string='DND Start Hour', default=22)
dnd_end_hour = fields.Integer(string='DND End Hour', default=8)
```

---

## 📍 Localização

Campos adicionados após a linha 56 (depois de `last_used`), antes do método `_send_sms_unified()`.

---

## 🎯 Status

- ✅ Campos adicionados ao modelo
- ✅ View `sms_provider_views.xml` agora pode usar os campos
- ✅ Pronto para atualizar o módulo

---

## ⚠️ Próximos Passos

1. ✅ **Atualizar o módulo** `sms_core_unified` via interface web
2. ✅ **Verificar** se a view carrega corretamente
3. ✅ **Testar** funcionalidades de balance

---

**Status:** ✅ **Corrigido - Campos adicionados ao modelo**

