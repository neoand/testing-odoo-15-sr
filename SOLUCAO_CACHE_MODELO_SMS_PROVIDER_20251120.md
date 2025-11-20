# ✅ Solução: Cache do Modelo SMS Provider

> **Data:** 2025-11-20
> **Erro:** `O campo "balance" não existe no modelo "sms.provider"` (mesmo após adicionar)

---

## 🐛 Problema Identificado

O erro persistia mesmo após adicionar os campos porque:
- ❌ O Odoo estava usando uma versão em cache do modelo Python
- ❌ Os arquivos `.pyc` estavam desatualizados
- ❌ O servidor precisava ser reiniciado para recarregar os modelos

---

## ✅ Solução Aplicada

### 1. **Verificação dos Campos**
- ✅ Campos confirmados no arquivo `sms_provider.py`
- ✅ Sintaxe correta verificada

### 2. **Limpeza de Cache**
```bash
sudo rm -rf /odoo/custom/addons_custom/sms_core_unified/__pycache__
sudo rm -rf /odoo/custom/addons_custom/sms_core_unified/models/__pycache__
```

### 3. **Reinicialização do Odoo**
```bash
sudo systemctl restart odoo-server
```

---

## 📋 Campos Confirmados no Modelo

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

# DND (Do Not Disturb)
dnd_enabled = fields.Boolean(string='Enable DND', default=True)
dnd_start_hour = fields.Integer(string='DND Start Hour', default=22)
dnd_end_hour = fields.Integer(string='DND End Hour', default=8)
```

---

## 🎯 Próximos Passos

1. ✅ **Aguardar** o Odoo reiniciar completamente (10-15 segundos)
2. ✅ **Atualizar o módulo** `sms_core_unified` via interface web
3. ✅ **Verificar** se a view carrega corretamente agora

---

## ⚠️ Nota Importante

Quando você adiciona novos campos a um modelo Python existente:
1. **Limpar cache** (`__pycache__`)
2. **Reiniciar Odoo** para recarregar os modelos
3. **Atualizar o módulo** para criar/atualizar as colunas no banco de dados

---

**Status:** ✅ **Cache limpo e Odoo reiniciado - Pronto para atualizar módulo**

