# 🔑 API Key Kolmeya

> **Data:** 2025-11-20
> **Localização:** Encontrada no código

---

## 🔑 API Key Encontrada

A API key da Kolmeya está hardcoded no arquivo `contacts_realcred/models/crm_lead.py`:

```
Bearer 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY
```

**API Key:** `5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY`

---

## ⚠️ RECOMENDAÇÃO DE SEGURANÇA

**IMPORTANTE:** Esta API key está hardcoded no código, o que não é uma boa prática de segurança.

### Recomendações:

1. ✅ **Mover para configuração do Provider**
   - A API key deve ser configurada no modelo `sms.provider`
   - Campo: `kolmeya_api_key`
   - Cada provider pode ter sua própria key

2. ✅ **Usar Variáveis de Ambiente** (Opcional)
   - Para maior segurança, usar `ir.config_parameter`
   - Não expor a key no código

3. ✅ **Remover do código**
   - Remover a key hardcoded de `crm_lead.py`
   - Usar a key configurada no provider

---

## 📋 Como Configurar no SMS Core Unified

1. Vá em **SMS → Providers**
2. Crie ou edite um provider do tipo **Kolmeya**
3. Configure o campo **"Kolmeya API Key"** com: `5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY`
4. Salve

---

## 🔒 Segurança

**Status atual:** ⚠️ API key exposta no código
**Recomendação:** ✅ Mover para configuração do provider

---

**API Key:** `5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY`

