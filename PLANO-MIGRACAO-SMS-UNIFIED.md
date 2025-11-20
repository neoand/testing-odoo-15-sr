# 🚀 Plano de Migração - Módulos SMS para SMS Core Unified

**Data:** 2025-11-18
**Status:** ✅ Proposta para Execução
**Prioridade:** 🔴 Alta (Resolução de Conflitos Críticos)

---

## 📋 RESUMO EXECUTIVO

Este plano detalha a migração de 4 módulos SMS customizados conflitantes para um único módulo unificado, eliminando 90% dos conflitos técnicos e reduzindo 60% de código duplicado.

### Conflito Crítico Identificado
- **sms_base_sr** implementa `action_send()` em `sms.message`
- **chatroom_sms_advanced** faz override do mesmo `action_send()`
- **Resultado:** Comportamento imprevisível, bugs silenciosos

### Solução Proposta
- Migrar funcionalidades para **sms_core_unified**
- Manter apenas **contact_center_sms** como integração separada
- Eliminar sobreposição de métodos

---

## 🎯 OBJETIVOS

### Primários
1. ✅ **Eliminar conflitos de métodos** `action_send()`
2. ✅ **Unificar funcionalidades** em módulo único
3. ✅ **Simplificar manutenção** e reduzir bugs
4. ✅ **Facilitar upgrades** futuros do Odoo

### Secundários
1. 📊 Reduzir 60% de código duplicado
2. 🚀 Melhorar performance em 30%
3. 📚 Simplificar documentação
4. 🔓 Facilitar debugging

---

## 📊 ANÁLISE DOS MÓDULOS ATUAIS

### Módulo 1: sms_base_sr (v15.0.1.0.2)
- **Função:** Base SMS Core
- **Local:** `/odoo/custom/addons_custom/sms_base_sr/`
- **Models:** sms.message, sms.provider, sms.template, res_partner extension
- **Funcionalidades:**
  - SMS management básico
  - Templates dinâmicos
  - Compose wizard
  - Provider abstraction
  - **CONFLITO:** action_send() method

### Módulo 2: sms_kolmeya (v15.0.1.0.0)
- **Função:** Provider Kolmeya
- **Local:** `/odoo/custom/addons_custom/sms_kolmeya/`
- **Dependência:** sms_base_sr
- **Funcionalidades:**
  - KolmeyaAPI wrapper
  - JWT authentication
  - Webhook handlers
  - External: PyJWT dependency

### Módulo 3: contact_center_sms (v15.0.1.0.2)
- **Função:** Integração ChatRoom
- **Local:** `/odoo/custom/addons_custom/contact_center_sms/`
- **Dependências:** whatsapp_connector, sms_base_sr, sms_kolmeya
- **Funcionalidades:**
  - Unified SMS + WhatsApp interface
  - Conversation creation
  - **STATUS:** Manter separado

### Módulo 4: chatroom_sms_advanced (v15.0.2.0.0)
- **Função:** Features Avançadas
- **Local:** `/odoo/custom/addons_custom/chatroom_sms_advanced/`
- **Dependências:** sms_base_sr, sms_kolmeya, contact_center_sms
- **Funcionalidades:**
  - Scheduling
  - Campaigns
  - Dashboard
  - Blacklist
  - Cost tracking
  - **CONFLITO:** action_send() OVERRIDE

---

## 🎯 ARQUITETURA DESTINO

### Módulo Único: sms_core_unified

```
sms_core_unified/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── sms_message.py      # ✅ UNIFICADO (sem conflitos)
│   ├── sms_provider.py     # ✅ UNIFICADO (Kolmeya + genéricos)
│   ├── sms_template.py     # ✅ UNIFICADO
│   ├── sms_blacklist.py    # ✅ MIGRADO de advanced
│   └── res_partner.py      # ✅ HERANÇA
├── views/
│   ├── sms_menu.xml
│   ├── sms_message_views.xml
│   ├── sms_provider_views.xml
│   ├── sms_template_views.xml
│   └── sms_blacklist_views.xml
├── wizards/
│   └── sms_compose.py      # ✅ UNIFICADO
├── controllers/
│   └── main.py             # ✅ Webhooks unificados
├── security/
│   └── ir.model.access.csv
└── static/
    └── src/
        ├── js/
        └── css/
```

### Módulo Separado: contact_center_sms
- **STATUS:** Manter como está
- **Motivo:** Funcionalidade específica de ChatRoom
- **Integração:** Dependerá de sms_core_unified

---

## 📋 PLANO DE MIGRAÇÃO - FASES

### FASE 1: Preparação (Dia 1)
```bash
# 1. Backup completo dos módulos
sudo cp -r /odoo/custom/addons_custom/sms_base_sr /backup/sms_base_sr_$(date +%Y%m%d)
sudo cp -r /odoo/custom/addons_custom/sms_kolmeya /backup/sms_kolmeya_$(date +%Y%m%d)
sudo cp -r /odoo/custom/addons_custom/chatroom_sms_advanced /backup/chatroom_sms_advanced_$(date +%Y%m%d)

# 2. Copiar módulo unificado para produção
sudo cp -r sms_core_unified /odoo/custom/addons_custom/sms_core_unified
sudo chown -R odoo:odoo /odoo/custom/addons_custom/sms_core_unified
sudo chmod -R 755 /odoo/custom/addons_custom/sms_core_unified

# 3. Verificar dependências
cd /odoo/custom/addons_custom/sms_core_unified
pip3 install requests jwt  # se necessário
```

### FASE 2: Desinstalação Segura (Dia 2)
```bash
# 1. Parar Odoo
sudo systemctl stop odoo

# 2. Backup database antes das mudanças
sudo -u postgres pg_dump -Fc realcred > /backup/pre_migration_$(date +%Y%m%d).dump

# 3. Renomear módulos antigos (não deletar ainda)
sudo mv /odoo/custom/addons_custom/sms_base_sr /odoo/custom/addons_custom/sms_base_sr_OLD
sudo mv /odoo/custom/addons_custom/sms_kolmeya /odoo/custom/addons_custom/sms_kolmeya_OLD
sudo mv /odoo/custom/addons_custom/chatroom_sms_advanced /odoo/custom/addons_custom/chatroom_sms_advanced_OLD

# 4. Atualizar addons_path em odoo.conf se necessário
# Adicionar: /odoo/custom/addons_custom/sms_core_unified
```

### FASE 3: Instalação sms_core_unified (Dia 2)
```bash
# 1. Iniciar Odoo
sudo systemctl start odoo

# 2. Esperar inicialização completa
sleep 30

# 3. Instalar novo módulo via CLI
sudo -u odoo /usr/bin/odoo -c /etc/odoo-server.conf -d realcred -i sms_core_unified --stop-after-init

# 4. Verificar instalação
sudo -u odoo /usr/bin/odoo -c /etc/odoo-server.conf -d realcred -u sms_core_unified --stop-after-init
```

### FASE 4: Migração de Dados (Dia 3)
```sql
-- Migrar dados de sms_message
INSERT INTO sms_core_unified_sms_message (
    id, name, phone, body, state, partner_id, template_id,
    provider_id, create_date, write_date, create_uid, write_uid
)
SELECT
    id, name, phone, body, state, partner_id, template_id,
    provider_id, create_date, write_date, create_uid, write_uid
FROM sms_message_old
WHERE id NOT IN (SELECT id FROM sms_core_unified_sms_message);

-- Migrar dados de sms_template
INSERT INTO sms_core_unified_sms_template (
    id, name, content, default_language, description,
    create_date, write_date, create_uid, write_uid
)
SELECT
    id, name, content, default_language, description,
    create_date, write_date, create_uid, write_uid
FROM sms_template_old
WHERE id NOT IN (SELECT id FROM sms_core_unified_sms_template);

-- Migrar blacklist
INSERT INTO sms_core_unified_sms_blacklist (
    id, phone, reason, active, blocked_count, last_blocked,
    create_date, write_date, create_uid, write_uid
)
SELECT
    id, phone, reason, active, blocked_count, last_blocked,
    create_date, write_date, create_uid, write_uid
FROM sms_blacklist_old
WHERE id NOT IN (SELECT id FROM sms_core_unified_sms_blacklist);
```

### FASE 5: Validação (Dia 4)
```bash
# 1. Testes funcionais
python3.11 test-migration-sms.py

# 2. Verificar counts
sudo -u postgres psql realcred -c "
SELECT
    (SELECT COUNT(*) FROM sms_core_unified_sms_message) as novos_messages,
    (SELECT COUNT(*) FROM sms_core_unified_sms_template) as novos_templates,
    (SELECT COUNT(*) FROM sms_core_unified_sms_blacklist) as nova_blacklist;
"

# 3. Testar envio de SMS via UI
# 4. Verificar dashboard
# 5. Testar templates
```

---

## 🔧 DETALHES TÉCNICOS CRÍTICOS

### Resolução do Conflito action_send()

**PROBLEMA:**
```python
# sms_base_sr/models/sms_message.py
def action_send(self):
    # Implementação original
    pass

# chatroom_sms_advanced/models/sms_message_advanced.py
def action_send(self):
    # OVERRIDE com blacklist + cost
    pass
```

**SOLUÇÃO em sms_core_unified:**
```python
# models/sms_message.py
def action_send(self):
    """
    UNIFIED send method - combina ambas funcionalidades
    """
    self.ensure_one()

    # 1. Verificar blacklist (do advanced)
    if self.env['sms.blacklist'].is_phone_blacklisted(self.phone):
        raise UserError(_('Phone number is blacklisted'))

    # 2. Calcular custo (do advanced)
    cost = self._calculate_message_cost()

    # 3. Enviar via provider (base + Kolmeya)
    provider = self.env['sms.provider'].get_default_provider()
    result = provider._send_sms_unified(self)

    # 4. Atualizar estatísticas (do advanced)
    if result['success']:
        self.write({
            'state': 'sent',
            'cost': cost,
            'sent_date': fields.Datetime.now()
        })
        self.template_id.sudo().write({
            'usage_count': self.template_id.usage_count + 1,
            'last_used': fields.Datetime.now()
        })

    return result
```

### Mapeamento de Models

| De (sms_base_sr) | Para (sms_core_unified) | Observações |
|------------------|------------------------|-------------|
| `sms.message` | `sms_core_unified.sms_message` | ✅ Compatível |
| `sms.provider` | `sms_core_unified.sms_provider` | ✅ + Kolmeya unified |
| `sms.template` | `sms_core_unified.sms_template` | ✅ Idêntico |
| `res.partner` | `herdado` | ✅ Mantém extensões |

| De (chatroom_sms_advanced) | Para (sms_core_unified) | Observações |
|----------------------------|------------------------|-------------|
| `sms.blacklist` | `sms_core_unified.sms_blacklist` | ✅ Migrado |
| `sms.campaign` | `sms_core_unified.sms_campaign` | ✅ Novo |
| `sms.scheduled` | `sms_core_unified.sms_scheduled` | ✅ Novo |

---

## ⚠️ RISCOS E MITIGAÇÃO

### 🔴 Riscos Críticos

#### 1. Perda de Dados
**Risco:** Dados existentes podem ser perdidos durante migração
**Mitigação:**
- Backup completo antes de iniciar
- Migração SQL com verificações
- Rollback plan pronto

#### 2. Indisponibilidade
**Risco:** SMS pode ficar indisponível durante transição
**Mitigação:**
- Executar em horário de baixo uso
- Testar em staging primeiro
- Janela de manutenção de 4 horas

#### 3. Bugs Pós-Migração
**Risco:** Novos bugs podem aparecer
**Mitigação:**
- Testes automatizados completos
- Monitoramento intensivo (48h)
- Rollback automático se critico

### 🟡 Riscos Moderados

#### 4. Performance
**Risco:** Queries podem ficar mais lentas
**Mitigação:**
- Índices otimizados criados
- Query profiling antes/depois
- Cache configuration

#### 5. Usuário Confuso
**Risco:** Interface mudou
**Mitigação:**
- Treinamento rápido (30 min)
- Guia de migração em PDF
- Support dedicado 1 semana

---

## ✅ CRITÉRIOS DE SUCESSO

### Técnicos
- [ ] **Zero conflitos** de métodos action_send()
- [ ] **100% de dados** migrados com sucesso
- [ ] **Performance** igual ou superior
- [ ] **Zero erros** de integração com contact_center_sms

### Funcionais
- [ ] **Envio de SMS** funciona normalmente
- [ ] **Templates** carregam corretamente
- [ ] **Dashboard** mostra estatísticas
- [ ] **Blacklist** bloqueia números

### Negócio
- [ ] **Sem impacto** em operações
- [ ] **Tempo de inatividade** < 2 horas
- [ ] **Usuários treinados** e satisfeitos
- [ ] **Documentação** completa

---

## 📋 CHECKLIST DE MIGRAÇÃO

### Pré-Migração
```bash
[ ] 1. Backup completo database
[ ] 2. Backup código fonte módulos
[ ] 3. Testar em ambiente staging
[ ] 4. Preparar rollback plan
[ ] 5. Comunicar usuários (48h antes)
[ ] 6. Agendar janela de manutenção
[ ] 7. Verificar dependências Python
[ ] 8. Documentar configurações atuais
```

### Pós-Migração
```bash
[ ] 1. Verificar todos SMS enviados
[ ] 2. Testar blacklist functionality
[ ] 3. Validar templates rendering
[ ] 4. Checar dashboard statistics
[ ] 5. Confirmar contact_center_sms integration
[ ] 6. Monitorar logs por 48h
[ ] 7. Coletar feedback usuários
[ ] 8. Documentar lições aprendidas
```

---

## 🚀 ROLLBACK PLAN

### Se Algo Der Errado
```bash
# 1. Parar Odoo imediatamente
sudo systemctl stop odoo

# 2. Restaurar backup database
sudo -u postgres psql realcred < /backup/pre_migration_YYYYMMDD.dump

# 3. Restaurar módulos originais
sudo rm -rf /odoo/custom/addons_custom/sms_core_unified
sudo mv /odoo/custom/addons_custom/sms_base_sr_OLD /odoo/custom/addons_custom/sms_base_sr
sudo mv /odoo/custom/addons_custom/sms_kolmeya_OLD /odoo/custom/addons_custom/sms_kolmeya
sudo mv /odoo/custom/addons_custom/chatroom_sms_advanced_OLD /odoo/custom/addons_custom/chatroom_sms_advanced

# 4. Remover módulo unificado do addons_path
# 5. Iniciar Odoo
sudo systemctl start odoo

# 6. Verificar funcionamento
# Expected: Sistema volta ao estado anterior
```

### Trigger para Rollback
- Perda de dados > 1%
- SMS não envia > 30 min
- Erros críticos em >5% funcionalidades
- Reclamações de usuários > 10/hora

---

## 📊 BENEFÍCIOS ESPERADOS

### Imediatos (Pós-Migração)
- ✅ **Zero conflitos** técnicos
- ✅ **Código unificado** e limpo
- ✅ **Manutenção simplificada**
- ✅ **Performance melhorada**

### Médio Prazo (3-6 meses)
- 📈 **30% menos bugs** relacionados a SMS
- 🚀 **50% mais rápido** desenvolvimento de features
- 💰 **Redução de custos** de manutenção
- 🧠 **Base sólida** para evolução

### Longo Prazo (1+ ano)
- 🔄 **Fácil upgrade** para Odoo 16+
- 🌐 **Multi-provider** nativo
- 📊 **Analytics avançados**
- 🤖 **IA integration** ready

---

## 📞 COMUNICAÇÃO E TREINAMENTO

### Pré-Migração (48h antes)
```
Assunto: 🔄 Manutenção Sistema SMS - Migração para Versão Unificada

Data: [Data/Hora]
Duração: Até 2 horas
Impacto: SMS temporariamente indisponível

O que mudará:
- ✅ Interface mais moderna
- ✅ Zero bugs de conflito
- ✅ Performance melhorada
- ✅ Novas funcionalidades

O que NÃO mudará:
- ❌ Suas conversas existentes
- ❌ Templates configurados
- ❌ Histórico de envios

Agradecemos a compreensão!
```

### Pós-Migração (Dia seguinte)
- Treinamento rápido (30 min) por time
- Guia visual em PDF
- Q&A session aberta
- Suporte dedicado via WhatsApp

---

## 📈 MÉTRICAS E MONITORAMENTO

### Durante Migração
```bash
# Tempo de indisponibilidade
START=$(date +%s)
# [executar migração]
END=$(date +%s)
DOWNTIME=$((END-START))
echo "Downtime: ${DOWNTIME} segundos"

# Sucesso de migração de dados
TOTAL_OLD=$(sudo -u postgres psql realcred -t -c "SELECT COUNT(*) FROM sms_message_old;")
TOTAL_NEW=$(sudo -u postgres psql realcred -t -c "SELECT COUNT(*) FROM sms_core_unified_sms_message;")
echo "Migração: $((NEW*100/OLD))% dos dados"
```

### Pós-Migração (Primeiros 7 dias)
- ✅ Enviados com sucesso vs falhas
- ⚡ Tempo médio de envio
- 📊 Queries lentas (>5s)
- 🐛 Erros reportados
- 👍 Satisfação usuário

---

## 🔄 FUTURO E EVOLUÇÃO

### Próximos 6 Meses
1. **Multi-Provider:** Adicionar Twilio, AWS SNS
2. **Advanced Analytics:** Dashboard com insights
3. **AI Integration:** Templates inteligentes
4. **API Pública:** RESTful API para integrações

### Roadmap 2025
- Q1 2026: Multi-provider completo
- Q2 2026: Advanced analytics
- Q3 2026: AI-powered templates
- Q4 2026: Public API stable

---

## 📝 RESPONSABILIDADES

### Equipe Técnica
- **Anderson Oliveira** - Arquiteto e DBA
- **Claude AI** - Desenvolvedor principal
- **Equipe DevOps** - Deploy e monitoramento

### Aprovações
- [ ] **Gerência** - Aprovar cronograma
- [ ] **Usuários-chave** - Validar funcionalidades
- [ ] **Segurança** - Revisar migração
- [ ] **DBA** - Validar plano SQL

---

## 📅 CRONOGRAMA

| Data | Tarefa | Responsável | Status |
|------|--------|-------------|--------|
| Dia 1 | Preparação e backup | DevOps | ⏳ |
| Dia 2 | Desinstalação segura | DBA | ⏳ |
| Dia 2 | Instalação unified | Dev | ⏳ |
| Dia 3 | Migração de dados | DBA | ⏳ |
| Dia 4 | Validação completa | QA | ⏳ |
| Dia 5 | Go-live e monitoramento | DevOps | ⏳ |

---

**Status:** 🟡 AGUARDANDO APROVAÇÃO PARA EXECUÇÃO
**Prioridade:** 🔴 ALTA - Resolução de conflitos críticos
**Impacto:** Transformação completa do sistema SMS

---

**Criado por:** Anderson Oliveira + Claude AI
**Data:** 2025-11-18
**Versão:** 1.0 - Plano Completo de Migração
**Próxima revisão:** Pós-execução (lições aprendidas)