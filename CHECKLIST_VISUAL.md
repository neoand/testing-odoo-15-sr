# 📋 CHECKLIST VISUAL - Refatoração chatroom_sms_advanced

**Imprima e cole na parede! ✂️**

---

## 🎯 OBJETIVO PRINCIPAL

```
┌─────────────────────────────────────────────────────────┐
│  TRANSFORMAR chatroom_sms_advanced DE:                 │
│                                                         │
│  ❌ Sistema DUPLICADO (80% código redundante)          │
│                                                         │
│  PARA:                                                  │
│                                                         │
│  ✅ Sistema INTEGRADO (features REALMENTE novas)       │
└─────────────────────────────────────────────────────────┘
```

---

## 📅 SEMANA 1: PREPARAÇÃO E LIMPEZA

### DIA 1: BACKUP ✅
```
┌─────────────────────────────────────────┐
│ ☐ Backup local do módulo                │
│ ☐ Backup no servidor                    │
│ ☐ Backup banco de dados                 │
│ ☐ Criar branch Git                      │
│ ☐ Documentar estado atual               │
└─────────────────────────────────────────┘
```

### DIA 2: LIMPEZA ✅
```
┌─────────────────────────────────────────┐
│ ☐ Atualizar __manifest__.py             │
│   - depends: sms_base_sr, sms_kolmeya   │
│   - incrementar versão                  │
│                                         │
│ ☐ DELETAR modelos duplicados:          │
│   ☐ chatroom_sms_log.py                │
│   ☐ chatroom_sms_api.py                │
│   ☐ chatroom_room.py                   │
│   ☐ webhook_kolmeya.py                 │
│                                         │
│ ☐ DELETAR views duplicadas              │
│ ☐ Atualizar __init__.py                 │
│ ☐ Commit: "refactor: remove duplicates" │
└─────────────────────────────────────────┘
```

### DIA 3: SMS.MESSAGE (INHERIT) ✅
```
┌─────────────────────────────────────────┐
│ ☐ Criar sms_message_advanced.py         │
│   ☐ _inherit = 'sms.message'            │
│   ☐ + scheduled_date                    │
│   ☐ + campaign_id                       │
│   ☐ + link_tracking_ids                 │
│   ☐ + tag_ids                           │
│   ☐ + blacklist_reason                  │
│                                         │
│ ☐ Criar sms_message_advanced_views.xml  │
│   ☐ Extend form view                    │
│   ☐ Extend tree view                    │
│   ☐ Adicionar filtros                   │
│                                         │
│ ☐ Criar chatroom_sms_tag.py             │
│ ☐ Atualizar security/ir.model.access    │
│ ☐ TESTAR instalação                     │
│ ☐ Commit: "feat: sms.message advanced"  │
└─────────────────────────────────────────┘
```

### DIA 4: SMS.PROVIDER (INHERIT) ✅
```
┌─────────────────────────────────────────┐
│ ☐ Criar sms_provider_advanced.py        │
│   ☐ _inherit = 'sms.provider'           │
│   ☐ + auto_balance_check                │
│   ☐ + balance_alert_threshold           │
│   ☐ + dnd_enabled                       │
│   ☐ + dnd_start_hour / dnd_end_hour     │
│   ☐ + webhook_url_custom                │
│                                         │
│ ☐ Criar sms_provider_advanced_views.xml │
│ ☐ TESTAR consulta saldo                 │
│ ☐ Commit: "feat: sms.provider advanced" │
└─────────────────────────────────────────┘
```

### DIA 5: CHATROOM (INHERIT) ✅
```
┌─────────────────────────────────────────┐
│ ☐ Criar chatroom_conversation_sms.py    │
│   ☐ _inherit = 'acrux.chat.conversation'│
│   ☐ + sms_last_sent                     │
│   ☐ + sms_last_received                 │
│   ☐ + sms_delivery_rate                 │
│   ☐ + sms_tag_ids                       │
│   ☐ + action_schedule_sms()             │
│                                         │
│ ☐ Criar conversation_sms_views.xml      │
│ ☐ TESTAR integração ChatRoom            │
│ ☐ Commit: "feat: chatroom integration"  │
└─────────────────────────────────────────┘
```

---

## 📅 SEMANA 2: FEATURES NOVAS

### DIA 6: AGENDAMENTO ✅
```
┌─────────────────────────────────────────┐
│ ☐ Criar chatroom_sms_scheduled.py       │
│   ☐ Modelo completo                     │
│   ☐ + recorrência (daily/weekly/monthly)│
│   ☐ + cron_send_scheduled_sms()         │
│   ☐ + _create_next_recurrence()         │
│                                         │
│ ☐ Criar sms_scheduled_views.xml         │
│   ☐ Tree/Form/Kanban views              │
│   ☐ Filtros por estado                  │
│                                         │
│ ☐ Criar data/cron_sms_scheduled.xml     │
│   ☐ Roda a cada 5 minutos               │
│                                         │
│ ☐ Criar wizard schedule                 │
│ ☐ TESTAR agendamento manual             │
│ ☐ TESTAR agendamento via cron           │
│ ☐ TESTAR recorrência                    │
│ ☐ Commit: "feat: SMS scheduling"        │
└─────────────────────────────────────────┘
```

### DIA 7: CAMPANHAS ✅
```
┌─────────────────────────────────────────┐
│ ☐ Criar chatroom_sms_campaign.py        │
│   ☐ Modelo completo                     │
│   ☐ + partner_ids (Many2many)           │
│   ☐ + template_id                       │
│   ☐ + domain_filter                     │
│   ☐ + stats (sent/delivered/failed)     │
│   ☐ + action_start_campaign()           │
│                                         │
│ ☐ Criar sms_campaign_views.xml          │
│   ☐ Form view completa                  │
│   ☐ Tree view                           │
│   ☐ Stats em separadores                │
│                                         │
│ ☐ TESTAR criação campanha               │
│ ☐ TESTAR envio em lote                  │
│ ☐ TESTAR stats                          │
│ ☐ Commit: "feat: SMS campaigns"         │
└─────────────────────────────────────────┘
```

### DIA 8: BLACKLIST ✅
```
┌─────────────────────────────────────────┐
│ ☐ Criar chatroom_sms_blacklist.py       │
│   ☐ Modelo completo                     │
│   ☐ + reason (user_request/auto/manual) │
│   ☐ + synced_kolmeya (Boolean)          │
│   ☐ + sync_to_kolmeya()                 │
│   ☐ + cron_sync_blacklist()             │
│                                         │
│ ☐ Criar sms_blacklist_views.xml         │
│                                         │
│ ☐ Criar data/cron_sync_blacklist.xml    │
│   ☐ Sync a cada 1 hora                  │
│                                         │
│ ☐ TESTAR adicionar blacklist            │
│ ☐ TESTAR sync Kolmeya                   │
│ ☐ TESTAR validação ao enviar SMS        │
│ ☐ Commit: "feat: SMS blacklist"         │
└─────────────────────────────────────────┘
```

### DIA 9: DASHBOARD ✅
```
┌─────────────────────────────────────────┐
│ ☐ Criar chatroom_sms_dashboard.py       │
│   ☐ _auto = False (SQL View)            │
│   ☐ init() com CREATE VIEW               │
│   ☐ Stats por dia/provider              │
│                                         │
│ ☐ Criar sms_dashboard_views.xml         │
│   ☐ Kanban view (cards por dia)         │
│   ☐ Graph view (bar chart)              │
│   ☐ Pivot view (análise)                │
│                                         │
│ ☐ TESTAR visualizações                  │
│ ☐ TESTAR filtros                        │
│ ☐ Commit: "feat: SMS dashboard"         │
└─────────────────────────────────────────┘
```

### DIA 10: WIZARD BULK SEND ✅
```
┌─────────────────────────────────────────┐
│ ☐ Adaptar chatroom_send_bulk_sms.py     │
│   ☐ USA sms.message (não chatroom.log!) │
│   ☐ USA sms.template                    │
│   ☐ + selection_type (manual/domain)    │
│   ☐ + scheduled_date                    │
│   ☐ + estimated_cost                    │
│                                         │
│ ☐ Atualizar wizard views                │
│                                         │
│ ☐ TESTAR envio manual                   │
│ ☐ TESTAR envio via domain               │
│ ☐ TESTAR com template                   │
│ ☐ TESTAR agendamento                    │
│ ☐ Commit: "feat: bulk send wizard"      │
└─────────────────────────────────────────┘
```

---

## 📅 SEMANA 3: TESTES E DEPLOY

### DIA 11-12: TESTES COMPLETOS ✅
```
┌─────────────────────────────────────────┐
│ ☐ TESTES UNITÁRIOS:                     │
│   ☐ Criar SMS simples                   │
│   ☐ Criar SMS agendado                  │
│   ☐ Criar campanha                      │
│   ☐ Adicionar blacklist                 │
│   ☐ Sync blacklist Kolmeya              │
│                                         │
│ ☐ TESTES INTEGRAÇÃO:                    │
│   ☐ Envio via ChatRoom                  │
│   ☐ Recebimento reply                   │
│   ☐ Webhook status                      │
│   ☐ Webhook reply                       │
│   ☐ Consulta saldo                      │
│                                         │
│ ☐ TESTES CRON:                          │
│   ☐ Agendamento (5 min)                 │
│   ☐ Saldo (6 horas)                     │
│   ☐ Blacklist sync (1 hora)             │
│                                         │
│ ☐ TESTES UI:                            │
│   ☐ Dashboard (Kanban/Graph/Pivot)      │
│   ☐ Wizard bulk send                    │
│   ☐ Wizard schedule                     │
│   ☐ Conversas SMS no ChatRoom           │
│                                         │
│ ☐ Correção de bugs encontrados          │
│ ☐ Commit: "test: all tests passing"     │
└─────────────────────────────────────────┘
```

### DIA 13: DEPLOY STAGING ✅
```
┌─────────────────────────────────────────┐
│ ☐ Criar test_db limpo (opcional)        │
│ ☐ Atualizar módulo em staging           │
│ ☐ Verificar logs (sem erros)            │
│ ☐ Importar dados teste                  │
│ ☐ Rodar todos testes novamente           │
│ ☐ Performance check                     │
│ ☐ Documentar issues encontrados         │
│ ☐ Corrigir issues críticos              │
└─────────────────────────────────────────┘
```

### DIA 14: TESTES USUÁRIOS ✅
```
┌─────────────────────────────────────────┐
│ ☐ Preparar ambiente demo                │
│ ☐ Criar dados fictícios                 │
│ ☐ Treinar 2-3 usuários                  │
│ ☐ Coletar feedback                      │
│ ☐ Ajustes de UX                         │
│ ☐ Correções finais                      │
│ ☐ Documentação usuário final            │
│ ☐ Commit: "docs: user documentation"    │
└─────────────────────────────────────────┘
```

### DIA 15: DEPLOY PRODUÇÃO ✅
```
┌─────────────────────────────────────────┐
│ ☐ VERIFICAÇÕES PRÉ-DEPLOY:              │
│   ☐ Backup BD produção                  │
│   ☐ Backup módulo atual produção        │
│   ☐ Todos testes passando               │
│   ☐ Logs staging limpos                 │
│   ☐ Aprovação stakeholders              │
│                                         │
│ ☐ DEPLOY:                               │
│   ☐ Sync código para servidor           │
│   ☐ Atualizar módulo odoo_15            │
│   ☐ Reiniciar Odoo                      │
│   ☐ Smoke tests                         │
│   ☐ Monitorar logs (30 min)             │
│                                         │
│ ☐ PÓS-DEPLOY:                           │
│   ☐ Testar envio SMS real               │
│   ☐ Testar webhook real                 │
│   ☐ Verificar crons rodando             │
│   ☐ Dashboard funcionando               │
│   ☐ ChatRoom integrado                  │
│                                         │
│ ☐ COMUNICAÇÃO:                          │
│   ☐ Notificar usuários                  │
│   ☐ Disponibilizar documentação         │
│   ☐ Canal suporte disponível            │
│                                         │
│ ☐ Commit: "release: v2.0.0 production"  │
│ ☐ Tag Git: v2.0.0                       │
└─────────────────────────────────────────┘
```

---

## 🔥 CHECKLIST DIÁRIO (TODOS OS DIAS)

```
┌─────────────────────────────────────────┐
│ MANHÃ:                                  │
│ ☐ Pull latest do Git                   │
│ ☐ Revisar plano do dia                 │
│ ☐ Verificar test_db funcionando        │
│                                         │
│ DURANTE:                                │
│ ☐ Commit frequente (1-2 por feature)   │
│ ☐ Testar cada mudança                  │
│ ☐ Documentar problemas encontrados     │
│                                         │
│ FIM DO DIA:                             │
│ ☐ Push commits para Git                │
│ ☐ Sync código para servidor            │
│ ☐ Atualizar checklist                  │
│ ☐ Planejar dia seguinte                │
└─────────────────────────────────────────┘
```

---

## 🚨 COMANDOS EMERGÊNCIA

```
┌─────────────────────────────────────────────────────────┐
│ PROBLEMA: Módulo quebrou                               │
│ SOLUÇÃO:                                               │
│   ssh odoo-rc "cd /odoo && sudo systemctl stop odoo"   │
│   # Restaurar backup                                   │
│   ssh odoo-rc "sudo systemctl start odoo"              │
│                                                        │
│ PROBLEMA: Banco corrompido                            │
│ SOLUÇÃO:                                               │
│   ssh odoo-rc "sudo -u postgres psql"                  │
│   # DROP DATABASE test_db;                            │
│   # CREATE DATABASE test_db;                          │
│   # Restaurar backup .sql                             │
│                                                        │
│ PROBLEMA: Git confuso                                  │
│ SOLUÇÃO:                                               │
│   git status                                           │
│   git stash  # Salva mudanças                         │
│   git checkout main                                    │
│   git checkout -b nova-branch                          │
│   git stash pop  # Restaura mudanças                  │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 PROGRESSO GERAL

```
╔════════════════════════════════════════════════════════╗
║                   PROGRESSO TOTAL                      ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  SEMANA 1: [___________________________________] 0%    ║
║            Preparação + Limpeza + Inherit              ║
║                                                        ║
║  SEMANA 2: [___________________________________] 0%    ║
║            Features Novas (Agendamento/Campanhas)      ║
║                                                        ║
║  SEMANA 3: [___________________________________] 0%    ║
║            Testes + Deploy                             ║
║                                                        ║
║  TOTAL:    [___________________________________] 0%    ║
║                                                        ║
╚════════════════════════════════════════════════════════╝

Atualizar diariamente! ✏️
```

---

## 🎯 META FINAL

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│        ✅ MÓDULO REFATORADO E FUNCIONANDO 100%          │
│                                                         │
│  • Zero duplicação de código                           │
│  • Integração completa com ChatRoom                    │
│  • 5 funcionalidades novas:                            │
│    1. Agendamento (com recorrência)                    │
│    2. Campanhas SMS                                    │
│    3. Dashboard visual                                 │
│    4. Blacklist management                             │
│    5. Bulk send wizard                                 │
│                                                         │
│  • Todos testes passando                               │
│  • Documentação completa                               │
│  • Deploy produção OK                                  │
│                                                         │
│                 🎉 MISSÃO CUMPRIDA! 🎉                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

**DICAS FINAIS:**

1. ✂️ **Imprima esta checklist** e cole na parede
2. ✅ **Marque** cada item conforme completa
3. 📝 **Anote** problemas encontrados ao lado
4. 🔄 **Revise** no fim de cada dia
5. 🎯 **Foque** em completar um dia de cada vez

**Não tente fazer tudo de uma vez!**

**Siga o plano. Teste cada passo. Comemmore pequenas vitórias.**

---

**BOA SORTE! VOCÊ CONSEGUE! 💪**

**Data de início:** ___/___/_____
**Data de conclusão:** ___/___/_____
