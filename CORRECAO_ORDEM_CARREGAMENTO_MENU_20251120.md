# 🔧 Correção: Ordem de Carregamento - Menu antes das Views

> **Data:** 2025-11-20
> **Erro:** `ValueError: External ID not found in the system: sms_core_unified.action_sms_campaign`

---

## 🐛 Problema Identificado

O menu `sms_menu.xml` estava sendo carregado **ANTES** das views que definem as actions:

- ❌ Menu carregado primeiro → tenta referenciar `action_sms_campaign`
- ❌ Views carregadas depois → `action_sms_campaign` ainda não existe
- ❌ Erro: External ID not found

---

## ✅ Solução Aplicada

**Ordem correta no manifest:**

```python
'data': [
    'security/sms_security.xml',
    # Views PRIMEIRO (definem as actions)
    'views/sms_message_views.xml',
    'views/sms_campaign_views.xml',  # Define action_sms_campaign
    'views/sms_scheduled_views.xml',  # Define action_sms_scheduled
    'views/sms_dashboard_views.xml',  # Define action_sms_dashboard
    'views/sms_bulk_send_views.xml',
    # Menu DEPOIS das views (precisa das actions já definidas)
    'views/sms_menu.xml',
    # Data files
    'data/sms_blacklist_data.xml',
    'data/cron_sms_scheduled.xml',
    # CSV por último
    'security/ir.model.access.csv',
],
```

---

## 📋 Ordem de Carregamento Correta

1. ✅ **Security XML** - Grupos de usuários
2. ✅ **Views** - Definem as actions
3. ✅ **Menu** - Referencia as actions (já definidas)
4. ✅ **Data files** - Dados iniciais
5. ✅ **CSV** - Permissões (precisa dos models)

---

## 🎯 Status

- ✅ Manifest corrigido
- ✅ Ordem de carregamento ajustada
- ✅ Pronto para atualizar módulo

---

**Próximo passo:** Atualizar o módulo `sms_core_unified` novamente.

