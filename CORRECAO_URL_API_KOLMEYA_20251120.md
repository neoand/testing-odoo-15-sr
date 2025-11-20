# ✅ Correção: URL Base da API Kolmeya

> **Data:** 2025-11-20
> **Problema:** URL base da API estava incorreta
> **Status:** ✅ **CORRIGIDO**

---

## 🔍 **Problema Identificado**

**URL Incorreta (antes):**
```
https://api.kolmeya.com/v1
```

**URL Correta (documentação):**
```
https://kolmeya.com.br/api/v1
```

---

## 📝 **Arquivos Corrigidos**

### **1. `sms_core_unified/models/sms_provider.py`**
```python
# ANTES
kolmeya_api_url = fields.Char(
    string='Kolmeya API URL',
    default='https://api.kolmeya.com/v1'  # ❌ ERRADO
)

# DEPOIS
kolmeya_api_url = fields.Char(
    string='Kolmeya API URL',
    default='https://kolmeya.com.br/api/v1'  # ✅ CORRETO
)
```

### **2. `sms_core_unified/views/sms_provider_views.xml`**
```xml
<!-- ANTES -->
<field name="kolmeya_api_url" placeholder="https://api.kolmeya.com/v1"/>

<!-- DEPOIS -->
<field name="kolmeya_api_url" placeholder="https://kolmeya.com.br/api/v1"/>
```

---

## 🧪 **Próximos Passos**

1. ✅ Arquivos corrigidos no servidor
2. ⏳ **Reiniciar Odoo** para carregar mudanças
3. ⏳ **Testar conexão** novamente com URL correta
4. ⏳ **Atualizar providers existentes** (se necessário)

---

## 💡 **Nota Importante**

Se já existem providers configurados com a URL antiga, será necessário:
1. Atualizar manualmente via interface Odoo, OU
2. Executar script SQL para atualizar em massa:

```sql
UPDATE sms_provider 
SET kolmeya_api_url = 'https://kolmeya.com.br/api/v1'
WHERE kolmeya_api_url = 'https://api.kolmeya.com/v1';
```

---

**Status:** ✅ **Correção aplicada - Aguardando teste**

