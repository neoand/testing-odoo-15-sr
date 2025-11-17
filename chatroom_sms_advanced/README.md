# ChatRoom SMS Advanced

**Version:** 15.0.2.0.0
**Author:** Realcred - Anderson Oliveira
**Date:** 16/11/2025

## Descrição

Módulo avançado de SMS que estende a funcionalidade base do sistema SMS (sms_base_sr, sms_kolmeya, contact_center_sms).

**IMPORTANTE:** Este módulo NÃO duplica funcionalidades existentes. Ele apenas ESTENDE os módulos base com recursos avançados.

## Recursos Principais

### 1. SMS Agendado (Scheduled SMS)
- Agendamento único ou recorrente (diário, semanal, mensal)
- Execução automática via cron (a cada 5 minutos)
- Seleção manual de destinatários ou filtro por domínio
- Histórico de execuções e estatísticas

### 2. Campanhas SMS (SMS Campaigns)
- Criação de campanhas de marketing
- Envio em massa com tracking
- Estatísticas em tempo real:
  - Taxa de entrega
  - Custo total
  - Mensagens enviadas/entregues/falhas
- Segmentação de público por filtros dinâmicos

### 3. Dashboard Analítico (SQL View)
- Visualizações: Graph, Pivot, Kanban, Tree
- Métricas agregadas por período/provedor/campanha
- Análise de custos e performance
- Comparação entre providers

### 4. Blacklist Avançada
- Gerenciamento de números bloqueados
- Sincronização automática com Kolmeya
- Múltiplas razões de bloqueio
- Validação antes do envio

### 5. Wizard de Envio em Massa
- Interface amigável para envio bulk
- Estimativa de custo antes do envio
- Preview de mensagem
- Filtro de blacklist automático
- Integração com campanhas

### 6. Extensões de Modelos Existentes

#### sms.message (extended)
- Campo: `campaign_id` - Campanha associada
- Campo: `scheduled_id` - Tarefa agendada
- Campo: `cost` - Custo da mensagem
- Método: `action_send()` - Verifica blacklist antes de enviar

#### sms.provider (extended)
- Alertas de saldo baixo
- DND (Do Not Disturb) - Horários proibidos
- Estatísticas de performance
- Verificação automática de saldo

## Dependências

```python
'depends': [
    'sms_base_sr',           # Core SMS - OBRIGATÓRIO
    'sms_kolmeya',           # Provider Kolmeya - OBRIGATÓRIO
    'contact_center_sms',    # Integração ChatRoom - OBRIGATÓRIO
]
```

## Instalação

```bash
# 1. Copiar módulo para addons_custom
cp -r chatroom_sms_advanced /odoo/custom/addons_custom/

# 2. Atualizar lista de apps
odoo-bin -c odoo.conf -d DATABASE -u all --stop-after-init

# 3. Instalar módulo via interface
# Apps > Search "SMS Advanced" > Install
```

## Configuração

### 1. Grupos de Segurança

- **SMS Advanced User**: Pode visualizar e usar recursos
- **SMS Advanced Manager**: Acesso completo (criar, editar, deletar)

### 2. Cron Jobs (Automáticos)

| Cron | Intervalo | Função |
|------|-----------|--------|
| Process Scheduled SMS | 5 minutos | Processa SMS agendados |
| Check Provider Balance | 6 horas | Verifica saldo do provider |
| Sync Blacklist | 1 hora | Sincroniza blacklist com Kolmeya |

### 3. Configurar Provider

1. Ir em: SMS Advanced > Configuration
2. Abrir provider existente
3. Aba "Advanced Settings":
   - Habilitar alerta de saldo
   - Definir threshold (ex: R$ 100)
   - Configurar DND (ex: 22h - 8h)

## Uso

### Criar Campanha

1. **Menu:** SMS Advanced > Campaigns > Create
2. **Configurar:**
   - Nome da campanha
   - Template de mensagem
   - Destinatários (manual ou filtro)
3. **Iniciar:** Botão "Start Campaign"

### Agendar SMS

1. **Menu:** SMS Advanced > Scheduled SMS > Create
2. **Configurar:**
   - Tipo: Once, Daily, Weekly, Monthly
   - Data/Hora
   - Template
   - Destinatários
3. **Ativar:** Botão "Activate"

### Envio em Massa

1. **Menu:** SMS Advanced > Send Bulk SMS
2. **Ou:** Contacts > Selecionar parceiros > Action > Send Bulk SMS
3. **Configurar:**
   - Selecionar destinatários
   - Template ou mensagem manual
   - Criar campanha (opcional)
4. **Enviar:** Botão "Send SMS"

### Ver Dashboard

1. **Menu:** SMS Advanced > Dashboard
2. **Visualizações disponíveis:**
   - Graph: Tendências ao longo do tempo
   - Pivot: Análise multidimensional
   - Kanban: Cards com métricas

## Estrutura de Arquivos

```
chatroom_sms_advanced/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── sms_message_advanced.py      (inherit sms.message)
│   ├── sms_provider_advanced.py     (inherit sms.provider)
│   ├── sms_scheduled.py              (new model)
│   ├── sms_campaign.py               (new model)
│   ├── sms_blacklist.py              (new model)
│   └── sms_dashboard.py              (SQL view)
├── wizard/
│   ├── __init__.py
│   └── sms_bulk_send.py
├── views/
│   ├── sms_scheduled_views.xml
│   ├── sms_campaign_views.xml
│   ├── sms_blacklist_views.xml
│   ├── sms_dashboard_views.xml
│   ├── sms_message_advanced_views.xml
│   ├── sms_provider_advanced_views.xml
│   └── menus.xml
├── wizard/
│   └── sms_bulk_send_views.xml
├── security/
│   ├── sms_advanced_security.xml
│   └── ir.model.access.csv
├── data/
│   ├── cron_sms_scheduled.xml
│   └── sms_campaign_templates.xml
└── static/
    ├── description/
    │   └── icon.png
    └── src/
        ├── css/
        │   └── sms_dashboard.css
        └── js/
            └── sms_dashboard.js
```

## API / Métodos Principais

### sms.scheduled

```python
# Executar tarefa agendada manualmente
scheduled = env['sms.scheduled'].browse(ID)
scheduled.action_run_now()

# Processar todas pendentes (cron)
env['sms.scheduled'].cron_process_scheduled_sms()
```

### sms.campaign

```python
# Iniciar campanha
campaign = env['sms.campaign'].browse(ID)
campaign.action_start_campaign()

# Ver estatísticas
stats = env['sms.campaign'].get_campaign_summary()
```

### sms.blacklist

```python
# Verificar se número está bloqueado
is_blocked, reason = env['sms.blacklist'].is_blacklisted('+5511999999999')

# Adicionar à blacklist
env['sms.blacklist'].add_to_blacklist(
    phone='+5511999999999',
    reason='manual',
    notes='Cliente solicitou'
)

# Sincronizar com Kolmeya
env['sms.blacklist'].search([]).sync_to_kolmeya()
```

### sms.dashboard

```python
# Obter resumo do dashboard
summary = env['sms.dashboard'].get_dashboard_summary(
    period_start='2025-01-01',
    period_end='2025-01-31'
)

# Comparar providers
comparison = env['sms.dashboard'].get_provider_comparison()

# Dados de tendência (últimos 30 dias)
trend = env['sms.dashboard'].get_trend_data(days=30)
```

## Troubleshooting

### Problema: Cron não está executando

**Solução:**
```bash
# Verificar crons ativos
SELECT * FROM ir_cron WHERE active = true AND name LIKE '%SMS%';

# Executar manualmente via Python
env['sms.scheduled'].cron_process_scheduled_sms()
```

### Problema: Blacklist não sincroniza com Kolmeya

**Solução:**
1. Verificar se `sms_kolmeya` está instalado
2. Verificar configuração do provider (API token)
3. Executar sync manual:
```python
env['sms.blacklist'].search([('synced_kolmeya', '=', False)]).sync_to_kolmeya()
```

### Problema: Dashboard não mostra dados

**Solução:**
```sql
-- Verificar se view existe
SELECT * FROM information_schema.views WHERE table_name = 'sms_dashboard';

-- Recriar view
DROP VIEW IF EXISTS sms_dashboard;
-- Então: Apps > SMS Advanced > Upgrade
```

## Changelog

### Version 15.0.2.0.0 (16/11/2025)
- ✅ Refatoração completa do módulo
- ✅ Remoção de código duplicado
- ✅ Integração com sms_base_sr, sms_kolmeya, contact_center_sms
- ✅ Novos recursos: Scheduled, Campaigns, Dashboard
- ✅ Blacklist avançada com sync Kolmeya
- ✅ Wizard de envio em massa
- ✅ Extensão de modelos existentes (inherit)

### Version 15.0.1.0.0 (Deprecated)
- ⚠️ Versão antiga com código duplicado
- ⚠️ Não usar em produção

## Suporte

**Desenvolvedor:** Anderson Oliveira
**Empresa:** Realcred
**Email:** anderson@realcred.com.br
**Data:** 16/11/2025

---

**Licença:** LGPL-3
**Compatibilidade:** Odoo 15.0+
