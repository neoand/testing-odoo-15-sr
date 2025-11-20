# 🔧 Correção: Ordem de Carregamento de Models

> **Data:** 2025-11-20
> **Erro:** `Modelo não encontrado: sms.campaign`

---

## 🐛 Problema Identificado

O Odoo está tentando carregar as views dos models avançados (`sms.campaign`, `sms.scheduled`, `sms.dashboard`) **antes** que esses models sejam registrados no registry.

Isso acontece porque:
1. As views são carregadas na ordem especificada no `data` do manifest
2. Os models são carregados automaticamente quando o módulo é importado
3. Mas se houver algum erro ao registrar os models, as views falham

---

## ✅ Solução Aplicada

**Estratégia em 2 etapas:**

### Etapa 1: Registrar Models Primeiro
- Remover temporariamente as views avançadas do manifest
- Atualizar o módulo para registrar os models
- Verificar se os models foram registrados corretamente

### Etapa 2: Adicionar Views Depois
- Após os models estarem registrados, adicionar as views de volta
- Atualizar o módulo novamente

---

## 📋 Manifest Temporário (Etapa 1)

```python
'data': [
    'security/sms_security.xml',
    'views/sms_message_views.xml',
    'views/sms_menu.xml',
    'data/sms_blacklist_data.xml',
    'security/ir.model.access.csv',
    # Views avançadas comentadas temporariamente
    # 'views/sms_campaign_views.xml',
    # 'views/sms_scheduled_views.xml',
    # 'views/sms_dashboard_views.xml',
    # 'views/sms_bulk_send_views.xml',
    # 'data/cron_sms_scheduled.xml',
],
```

---

## 🎯 Próximos Passos

1. ✅ Atualizar módulo com manifest temporário
2. ⏳ Verificar se models foram registrados
3. ⏳ Adicionar views de volta ao manifest
4. ⏳ Atualizar módulo novamente

---

**Status:** 🔄 Em progresso - Etapa 1 aplicada

