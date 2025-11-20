# ✅ Correção: URL do Webhook Kolmeya

> **Data:** 2025-11-20
> **Status:** ✅ **CORRIGIDO**

---

## 🐛 **ERRO IDENTIFICADO**

```
SSLError: HTTPSConnectionPool(host='api.kolmeya.com', port=443)
```

**Causa:** O método `configure_webhook()` estava usando a URL antiga `api.kolmeya.com` ao invés da URL correta `kolmeya.com.br/api/v1`.

---

## ✅ **SOLUÇÃO APLICADA**

### **1. Correção no Método `configure_webhook()`:**
```python
# Antes (ERRADO):
response = requests.post(
    f'{self.kolmeya_api_url}/sms/webhook',  # Usava URL antiga se configurada
    ...
)

# Depois (CORRETO):
# Ensure we use the correct Kolmeya API URL
if not self.kolmeya_api_url or 'api.kolmeya.com' in self.kolmeya_api_url:
    # Use correct URL if not set or if using old URL
    api_url = 'https://kolmeya.com.br/api/v1'
else:
    api_url = self.kolmeya_api_url

response = requests.post(
    f'{api_url}/sms/webhook',
    ...
)
```

---

## 📋 **ARQUIVO MODIFICADO**

- ✅ `sms_core_unified/models/sms_provider.py`
  - Método `configure_webhook()` corrigido
  - Validação de URL adicionada
  - Cache limpo

---

## 🧪 **VALIDAÇÃO**

- ✅ URL correta: `https://kolmeya.com.br/api/v1`
- ✅ Validação de URL antiga adicionada
- ✅ Sintaxe Python válida
- ✅ Cache limpo

---

## 📝 **PRÓXIMOS PASSOS**

1. ⏳ **Aguardar** alguns segundos para Odoo recarregar
2. ⏳ **Tentar configurar webhook novamente** no provider
3. ⏳ **Verificar** se o erro SSL foi resolvido

---

## 💡 **NOTA**

A URL correta da API Kolmeya é:
- ✅ **Correta:** `https://kolmeya.com.br/api/v1`
- ❌ **Antiga (errada):** `https://api.kolmeya.com/v1`

---

**Status:** ✅ **Correção aplicada - Webhook deve funcionar agora**

