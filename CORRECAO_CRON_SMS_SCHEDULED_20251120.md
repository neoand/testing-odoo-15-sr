# 🔧 Correção: Referências ao Módulo Removido em cron_sms_scheduled.xml

> **Data:** 2025-11-20
> **Erro:** `ValueError: External ID not found in the system: sms_base_sr.model_sms_provider`

---

## 🐛 Problema Identificado

O arquivo `cron_sms_scheduled.xml` estava referenciando modelos do módulo `sms_base_sr` que foi removido:

- ❌ `sms_base_sr.model_sms_provider` - Não existe mais
- ❌ `model_sms_blacklist` - Referência sem módulo

---

## ✅ Solução Aplicada

Corrigidas todas as referências para usar o módulo correto `sms_core_unified`:

**Antes:**
```xml
<field name="model_id" ref="sms_base_sr.model_sms_provider"/>
<field name="model_id" ref="model_sms_blacklist"/>
```

**Depois:**
```xml
<field name="model_id" ref="sms_core_unified.model_sms_provider"/>
<field name="model_id" ref="sms_core_unified.model_sms_blacklist"/>
```

---

## 📋 Crons Corrigidos

1. ✅ **cron_process_scheduled_sms** - Processa SMS agendados
2. ✅ **cron_check_provider_balance** - Verifica saldo dos providers
3. ✅ **cron_sync_blacklist** - Sincroniza blacklist com provider

---

## 🎯 Status

- ✅ `cron_sms_scheduled.xml` corrigido
- ✅ Todas as referências atualizadas
- ✅ Pronto para atualizar módulo

---

**Próximo passo:** Atualizar o módulo `sms_core_unified` novamente.

