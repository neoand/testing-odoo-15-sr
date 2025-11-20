# 🔧 Correção: Permissões de Acesso - SMS Core Unified

> **Data:** 2025-11-20
> **Erro:** `Você não tem permissão para acessar registros 'SMS Provider - Unified Configuration' (sms.provider)`

---

## 🐛 Problema Identificado

O arquivo `ir.model.access.csv` estava incompleto, faltando permissões para vários models:

- ❌ `sms.provider` - Sem permissões
- ❌ `sms.template` - Sem permissões
- ❌ `sms.blacklist` - Sem permissões
- ❌ `sms.bulk.send` - Sem permissões

---

## ✅ Solução Aplicada

Atualizado `ir.model.access.csv` com permissões completas para todos os models:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sms_message_user,sms.message.user,model_sms_message,base.group_user,1,1,1,1
access_sms_campaign_user,sms.campaign.user,model_sms_campaign,base.group_user,1,1,1,1
access_sms_scheduled_user,sms.scheduled.user,model_sms_scheduled,base.group_user,1,1,1,1
access_sms_dashboard_user,sms.dashboard.user,model_sms_dashboard,base.group_user,1,0,0,0
access_sms_template_user,sms.template.user,model_sms_template,base.group_user,1,1,1,1
access_sms_provider_user,sms.provider.user,model_sms_provider,base.group_user,1,1,1,1
access_sms_blacklist_user,sms.blacklist.user,model_sms_blacklist,base.group_user,1,1,1,1
access_sms_bulk_send_user,sms.bulk.send.user,model_sms_bulk_send,base.group_user,1,1,1,1
```

---

## 📋 Permissões Configuradas

### Models com Acesso Completo (Read, Write, Create, Unlink):
- ✅ `sms.message`
- ✅ `sms.campaign`
- ✅ `sms.scheduled`
- ✅ `sms.template`
- ✅ `sms.provider`
- ✅ `sms.blacklist`
- ✅ `sms.bulk.send`

### Models com Acesso Somente Leitura:
- ✅ `sms.dashboard` - Apenas leitura (é uma view SQL)

---

## 🎯 Status

- ✅ `ir.model.access.csv` atualizado
- ✅ Permissões antigas removidas do banco
- ✅ Pronto para atualizar módulo

---

## ⚠️ IMPORTANTE

**Após atualizar o módulo, você precisará:**

1. **Fazer logout e login novamente** para que as permissões sejam recarregadas
2. Ou **atualizar o módulo** novamente para garantir que as permissões sejam aplicadas

---

**Próximo passo:** Atualizar o módulo `sms_core_unified` e fazer logout/login.

