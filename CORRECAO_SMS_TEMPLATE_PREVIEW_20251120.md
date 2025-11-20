# 🔧 Correção: Erro no sms.template.preview

> **Data:** 2025-11-20
> **Erro:** `KeyError: 'Field model_id referenced in related field definition sms.template.preview.model_id does not exist.'`

---

## 🐛 Problema Identificado

O método `action_preview()` do modelo `sms.template` estava tentando abrir uma janela com o modelo `sms.template.preview`, mas:

1. ❌ O modelo `sms.template.preview` não existe
2. ❌ Algum lugar estava tentando criar um campo relacionado `model_id` nesse modelo inexistente
3. ❌ Isso causava erro ao carregar o registry do Odoo

---

## ✅ Solução Aplicada

Substituído o método `action_preview()` para usar uma notificação ao invés de abrir uma janela com modelo inexistente:

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

---

## 📋 Status

- ✅ `sms_template.py` corrigido
- ✅ Cache limpo
- ✅ Odoo reiniciado
- ✅ Aguardando verificação

---

**Próximo passo:** Verificar se o Odoo está respondendo corretamente e se o erro foi resolvido.

