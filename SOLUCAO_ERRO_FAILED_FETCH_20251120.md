# ✅ Solução: Erro "Failed to fetch"

> **Data:** 2025-11-20
> **Erro:** `UncaughtPromiseError > TypeError: Failed to fetch`
> **Causa:** `KeyError: 'Field model_id referenced in related field definition sms.template.preview.model_id does not exist.'`

---

## 🐛 Problema Identificado

O erro "Failed to fetch" no frontend era causado por um erro no backend:

1. ❌ O modelo `sms.template` tinha um método `action_preview()` que tentava abrir uma janela com o modelo `sms.template.preview`
2. ❌ O modelo `sms.template.preview` não existia no código
3. ❌ Mas havia registros no banco de dados tentando criar campos relacionados que referenciam `model_id` inexistente
4. ❌ Isso impedia o Odoo de carregar o registry corretamente

---

## ✅ Soluções Aplicadas

### 1. Correção do método `action_preview()`

**Antes:**
```python
return {
    'type': 'ir.actions.act_window',
    'res_model': 'sms.template.preview',  # ❌ Modelo não existe
    ...
}
```

**Depois:**
```python
return {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'title': _('Template Preview'),
        'message': rendered,
        'type': 'info',
        'sticky': True,
    }
}
```

### 2. Limpeza do banco de dados

Removidos registros órfãos do modelo `sms.template.preview` do banco de dados.

---

## 📋 Status Final

- ✅ `sms_template.py` corrigido
- ✅ Banco de dados limpo
- ✅ Cache limpo
- ✅ Odoo reiniciado
- ✅ **HTTP 200** - Odoo funcionando corretamente

---

## 🎯 Resultado

O Odoo está respondendo corretamente agora. O erro "Failed to fetch" foi resolvido.

---

**Status:** ✅ **RESOLVIDO**

