# 🔧 Instruções: Corrigir URL do Provider no Banco de Dados

> **Data:** 2025-11-20
> **Status:** ⚠️ **AÇÃO NECESSÁRIA**

---

## 🐛 **PROBLEMA IDENTIFICADO**

O log mostra que ainda está usando `api.kolmeya.com`:
```
SSL Error testing Kolmeya connection: HTTPSConnectionPool(host='api.kolmeya.com', port=443)
```

**Causa:** O provider no banco de dados ainda tem a URL antiga (`api.kolmeya.com`) configurada.

---

## ✅ **SOLUÇÃO**

### **Opção 1: Corrigir via Interface Odoo (Recomendado)**

1. Acesse **SMS Providers** no Odoo
2. Abra o provider Kolmeya
3. Verifique o campo **"Kolmeya API URL"**
4. Se estiver como `https://api.kolmeya.com/v1`, altere para:
   - `https://kolmeya.com.br/api/v1`
5. Salve o registro

### **Opção 2: Corrigir via SQL (Avançado)**

```sql
-- Verificar URLs atuais
SELECT id, name, kolmeya_api_url 
FROM sms_provider 
WHERE provider_type = 'kolmeya';

-- Corrigir URL antiga
UPDATE sms_provider 
SET kolmeya_api_url = 'https://kolmeya.com.br/api/v1'
WHERE provider_type = 'kolmeya' 
  AND (kolmeya_api_url LIKE '%api.kolmeya.com%' OR kolmeya_api_url IS NULL);
```

---

## 📋 **VALIDAÇÃO**

Após corrigir, verifique:
1. ✅ URL do provider está como `https://kolmeya.com.br/api/v1`
2. ✅ Teste de conexão funciona
3. ✅ Webhook pode ser configurado

---

## 💡 **NOTA**

O código agora tem proteção automática que corrige a URL se detectar a antiga, mas é melhor corrigir diretamente no banco para evitar problemas.

---

**Status:** ⚠️ **Corrigir URL do provider no banco de dados**

