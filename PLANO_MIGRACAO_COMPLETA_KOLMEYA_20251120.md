# 📋 Plano de Migração Completa - Kolmeya + Funcionalidades Avançadas

> **Data:** 2025-11-20
> **Objetivo:** Migrar todas as funcionalidades Kolmeya e avançadas para `sms_core_unified`

---

## 🔍 Funcionalidades Encontradas

### 1. API Kolmeya (Já Parcialmente Implementado)

**Localização atual:**
- ✅ `sms_core_unified/models/sms_provider.py` - Implementação básica
- ✅ JWT authentication
- ✅ Webhook URL generation
- ✅ Send SMS method

**Funcionalidades encontradas em outros módulos:**
- `contacts_realcred/models/crm_lead.py` - `getSmsKolmeya()` - Busca replies
- `contacts_realcred/data/ir_cron.xml` - Crons para verificar SMS Kolmeya
- URL: `https://kolmeya.com.br/api/v1/sms/replys-web`

### 2. Funcionalidades Avançadas (Backup)

**Models encontrados:**
- ✅ `sms.campaign` - Campanhas de SMS
- ✅ `sms.scheduled` - Agendamento de SMS
- ✅ `sms.dashboard` - Dashboard de estatísticas
- ✅ `sms_provider_advanced` - Provider avançado

**Views encontradas:**
- ✅ `sms_campaign_views.xml`
- ✅ `sms_scheduled_views.xml`
- ✅ `sms_dashboard_views.xml`
- ✅ `sms_bulk_send_views.xml` (wizard)

**Data files:**
- ✅ `cron_sms_scheduled.xml` - Cron para execução agendada
- ✅ `sms_campaign_templates.xml` - Templates de campanha

### 3. Webhooks e Callbacks

**Encontrado:**
- ✅ Webhook URL generation em `sms_provider.py`
- ✅ Callback URL: `/sms/webhook/kolmeya`
- ⚠️ Controller não encontrado (precisa ser criado)

---

## 📦 Estrutura de Migração

### Fase 1: Models Avançados

1. **sms_campaign.py**
   - Migrar para `sms_core_unified/models/`
   - Adaptar para usar models unificados
   - Manter funcionalidades: bulk send, segments, statistics

2. **sms_scheduled.py**
   - Migrar para `sms_core_unified/models/`
   - Adaptar para usar models unificados
   - Manter funcionalidades: one-time, recurring, cron

3. **sms_dashboard.py**
   - Migrar para `sms_core_unified/models/`
   - SQL view para analytics
   - Manter funcionalidades: statistics, reporting

### Fase 2: API Kolmeya Completa

1. **Métodos adicionais:**
   - `getSmsKolmeya()` - Buscar replies
   - Status checking melhorado
   - Delivery receipts

2. **Webhook Controller:**
   - Criar `controllers/sms_webhook.py`
   - Endpoint: `/sms/webhook/kolmeya`
   - Processar delivery receipts

3. **Crons:**
   - Migrar crons do `contacts_realcred`
   - Adicionar ao `sms_core_unified`

### Fase 3: Views e Wizards

1. **Views:**
   - Migrar views de campanhas
   - Migrar views de agendamento
   - Migrar views de dashboard

2. **Wizards:**
   - Migrar `sms_bulk_send` wizard

### Fase 4: Security e Menus

1. **Security:**
   - Adicionar permissões para novos models
   - Atualizar `ir.model.access.csv`

2. **Menus:**
   - Adicionar menus para campanhas
   - Adicionar menus para agendamento
   - Adicionar menus para dashboard

---

## 🎯 Ordem de Execução

1. ✅ **Ler todos os arquivos** (em progresso)
2. ⏳ **Migrar models avançados**
3. ⏳ **Completar API Kolmeya**
4. ⏳ **Criar webhook controller**
5. ⏳ **Migrar views e wizards**
6. ⏳ **Atualizar security e menus**
7. ⏳ **Testar tudo**

---

**Status:** 🔄 Em progresso - Coletando informações

