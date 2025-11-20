# ✅ Solução: Ordem do ir.model.access.csv no Manifest

> **Data:** 2025-11-19
> **Status:** ✅ Corrigido

---

## 🎯 Problema

O `ir.model.access.csv` estava sendo carregado **antes** dos models serem registrados, causando erro:

```
Nenhum registro encontrado para id externo 'model_sms_provider' no campo 'Model'
```

---

## ✅ Solução

**Reordenar arquivos no manifest** - mover `ir.model.access.csv` para o **final**:

### Antes (Incorreto):
```python
'data': [
    'security/ir.model.access.csv',  # ← PRIMEIRO (erro!)
    'security/sms_security.xml',
    'views/sms_message_views.xml',
    ...
]
```

### Depois (Correto):
```python
'data': [
    'security/sms_security.xml',      # ← Primeiro (não precisa de models)
    'views/sms_message_views.xml',    # Models carregados automaticamente
    'views/sms_menu.xml',
    'data/sms_providers.xml',
    'data/sms_blacklist_data.xml',
    'security/ir.model.access.csv',   # ← ÚLTIMO (precisa de models)
],
```

---

## 🎓 Regra Importante

**`ir.model.access.csv` deve SEMPRE vir no FINAL da lista `data`** porque:

1. Models são registrados quando o módulo é importado
2. CSV precisa referenciar models já registrados em `ir.model`
3. Se CSV vem antes, models ainda não existem

---

## ✅ Status

- ✅ Manifest atualizado
- ✅ CSV movido para o final
- ✅ Ordem correta aplicada
- ✅ Pronto para atualizar módulo

---

**Próximo passo:** Tentar atualizar o módulo novamente.

