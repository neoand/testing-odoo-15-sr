# Kolmeya SMS Integration - Odoo realcred

**Date:** 2025-11-15
**Status:** Analysis Complete - Integration Pending

---

## 📋 Executive Summary

Kolmeya é uma plataforma inteligente de mensagens SMS homologada pela Anatel, com sede em São Paulo. O Odoo realcred atualmente possui módulos SMS nativos instalados, mas **NÃO está integrado** com a API Kolmeya. Este documento fornece análise completa para implementação da integração.

---

## 🔐 Credenciais Kolmeya

### Acesso Web
```
URL: https://kolmeya.com.br/
Usuário: SUPERVISAO@REALCREDEMPRESTIMO.COM.BR
Senha: Anca741@
```

### API Access
```
Base URL: https://kolmeya.com.br/api
Token: Bearer 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY
Documentação: https://kolmeya.com.br/docs/api/
```

**IMPORTANTE:** Token válido indefinidamente. Requer whitelist de IP para segurança.

### Informações da Empresa
```
CNPJ: 30.184.356/0001-93
Telefone: (11) 99331-3806 (WhatsApp disponível)
Endereço: Rua Amaral Gama, 380, 15º Andar, Santana, São Paulo, SP
```

---

## 🎯 Recursos Kolmeya

### Funcionalidades Principais

1. **SMS Short Code Homologado Anatel**
   - Entrega quase instantânea
   - 99.8% de efetividade de entrega
   - Taxa de abertura acima de 90%
   - Tempo médio de leitura: ~5 segundos
   - Funciona sem internet ativa

2. **Qualificação de Respostas**
   - Análise automática de respostas (positivas/negativas)
   - Identificação por palavras-chave
   - Categorização inteligente

3. **Processamento de Dados**
   - Identifica números com baixa performance
   - Supressão automática para reduzir custos
   - Relatórios de números inválidos

4. **Segmentação WhatsApp**
   - Identifica números com WhatsApp ativo
   - Entrega direcionada de campanhas

5. **Link Shortener**
   - Encurtamento e rastreamento de links
   - Analytics detalhados: cliques, localização, dispositivo
   - Link shortener específico para WhatsApp

6. **Anti-Fraude**
   - Monitoramento de campanhas suspeitas
   - Detecção de links maliciosos
   - Proteção contra envios fraudulentos

---

## 📡 API Kolmeya - Endpoints Principais

### Autenticação
```
Header: Authorization: Bearer {token}
```

### Envio de SMS
| Endpoint | Método | Descrição | Limite |
|----------|--------|-----------|--------|
| `/v1/sms/store` | POST | Envio em massa | 1-1000 SMS/request |
| `/v1/sms/store-token` | POST | Token único | 1 SMS (sem 0800/links) |

### Gestão de Campanhas
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/v1/sms/jobs/{id}/pause` | POST | Pausar campanha |
| `/v1/sms/jobs/{id}/play` | POST | Retomar campanha |
| `/v1/sms/layouts` | POST | Templates de mensagens |
| `/v1/sms/segments` | POST | Centros de custo |

### Status e Relatórios
| Endpoint | Método | Descrição | Período |
|----------|--------|-----------|---------|
| `/v1/sms/status/request` | POST | Status de requisição | - |
| `/v1/sms/status/message` | POST | Status de mensagem individual | - |
| `/v1/sms/reports/statuses` | POST | Relatório de status | 7 dias |
| `/v1/sms/reports/jobs` | POST | Lista de jobs recentes | 7 dias |
| `/v1/sms/reports/quantity-jobs` | POST | Resumo por período | Custom |
| `/v1/sms/reports/invalid-records` | POST | Números inválidos removidos | - |

### Respostas e Analytics
| Endpoint | Método | Descrição | Retenção |
|----------|--------|-----------|----------|
| `/v1/sms/replys` | POST | Respostas via API | 168 horas |
| `/v1/sms/replys-web` | POST | Respostas via Web | 168 horas |
| `/v1/sms/accesses` | POST | Logs de acesso ao shortener | - |

### Blacklist
| Endpoint | Método | Descrição | Limite |
|----------|--------|-----------|--------|
| `/v1/blacklist/store` | POST | Adicionar números | 1-1000 números |
| `/v1/blacklist/destroy` | POST | Remover números | - |

### Conta
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/v1/sms/balance` | POST | Consultar saldo |
| `/v1/sms/webhook` | POST | Testar webhook |

---

## 📊 Status Codes Kolmeya

| Código | Significado |
|--------|-------------|
| 1 | Tentando enviar |
| 2 | Enviado |
| 3 | Entregue |
| 4 | Não entregue |
| 5 | Rejeitado pela operadora |
| 6 | Expirado |

---

## 🔍 Situação Atual no Odoo

### Módulos SMS Instalados
```
✅ sms                       - Módulo base SMS
✅ calendar_sms              - SMS para calendário
✅ crm_sms                   - SMS para CRM
✅ mass_mailing_crm_sms      - Mailing SMS CRM
✅ mass_mailing_sale_sms     - Mailing SMS Vendas
✅ mass_mailing_sms          - Mailing SMS geral
✅ sale_sms                  - SMS para vendas
✅ stock_sms                 - SMS para estoque
✅ website_crm_sms           - SMS website CRM
✅ website_sms               - SMS website

❌ event_sms                 - NÃO instalado
❌ mass_mailing_event_sms    - NÃO instalado
❌ mass_mailing_event_track_sms - NÃO instalado
```

### Estado Atual do SMS
```sql
-- Estatísticas de mensagens SMS:
Error: 8 mensagens
Canceled: 2 mensagens
```

**Conclusão:** SMS está configurado mas apresenta erros. Nenhum gateway ativo detectado.

### Tabelas SMS no Database
```
- sms_sms                  (mensagens)
- sms_template             (templates)
- sms_composer             (compositor)
- sms_cancel               (cancelamento)
- sms_resend               (reenvio)
- confirm_stock_sms        (confirmação estoque)
- mailing_sms_test         (teste mailing)
```

---

## 🚀 Plano de Integração Kolmeya

### Fase 1: Preparação (1-2 dias)

**1.1. Whitelist de IP**
- [ ] Solicitar IP público do servidor Odoo
- [ ] Cadastrar IP na plataforma Kolmeya
- [ ] Validar acesso à API

**1.2. Desenvolvimento do Módulo**
- [ ] Criar módulo `sms_kolmeya`
- [ ] Implementar provider Kolmeya no Odoo
- [ ] Configurar autenticação Bearer token

**1.3. Estrutura do Módulo**
```
/odoo/odoo-server/addons/sms_kolmeya/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── sms_api.py          # Provider Kolmeya
│   └── sms_sms.py          # Override modelo SMS
├── data/
│   └── sms_data.xml        # Dados iniciais
├── views/
│   └── sms_views.xml       # Views admin
└── security/
    └── ir.model.access.csv
```

### Fase 2: Implementação Core (2-3 dias)

**2.1. Endpoints Prioritários**
```python
# Envio
POST /v1/sms/store          # Envio em massa (alta prioridade)
POST /v1/sms/store-token    # Envio token (média prioridade)

# Status
POST /v1/sms/status/message # Status individual (alta prioridade)
POST /v1/sms/reports/statuses # Relatório (alta prioridade)

# Respostas
POST /v1/sms/replys         # Capturar respostas (média prioridade)

# Conta
POST /v1/sms/balance        # Consultar saldo (alta prioridade)
```

**2.2. Funcionalidades Core**
- [ ] Envio de SMS individual
- [ ] Envio em massa (batch até 1000)
- [ ] Callback de status (webhook)
- [ ] Consulta de saldo
- [ ] Tratamento de erros Kolmeya
- [ ] Retry automático em caso de falha

**2.3. Mapeamento de Status**
```python
KOLMEYA_TO_ODOO_STATUS = {
    1: 'outgoing',    # Tentando enviar
    2: 'sent',        # Enviado
    3: 'sent',        # Entregue
    4: 'error',       # Não entregue
    5: 'error',       # Rejeitado
    6: 'error',       # Expirado
}
```

### Fase 3: Funcionalidades Avançadas (3-5 dias)

**3.1. Link Shortener**
- [ ] Integrar `/v1/sms/accesses` para tracking
- [ ] Criar relatórios de cliques
- [ ] Analytics de localização/dispositivo

**3.2. Blacklist**
- [ ] Sincronizar blacklist Odoo ↔ Kolmeya
- [ ] Auto-adicionar números com erro
- [ ] Interface de gestão de blacklist

**3.3. Templates**
- [ ] Integrar `/v1/sms/layouts`
- [ ] Sincronizar templates Odoo → Kolmeya
- [ ] Editor de templates

**3.4. Respostas**
- [ ] Webhook para receber respostas
- [ ] Criar thread de conversa no Odoo
- [ ] Notificações de respostas

**3.5. Relatórios**
- [ ] Dashboard de envios
- [ ] Relatório de efetividade
- [ ] Análise de custo por campanha
- [ ] Identificação de números inválidos

### Fase 4: Otimizações (2-3 dias)

**4.1. Performance**
- [ ] Queue de envio assíncrono
- [ ] Cache de status
- [ ] Batch otimizado (1000 msgs/request)

**4.2. Compliance**
- [ ] Verificação "Não Perturbe" (SP)
- [ ] Validação de número brasileiro
- [ ] Horário permitido de envio

**4.3. Segurança**
- [ ] Criptografar token no database
- [ ] Log de auditoria
- [ ] Rate limiting

---

## 💡 Melhorias Recomendadas

### Curto Prazo (Imediato)

1. **Corrigir SMS com Erro**
   - Investigar 8 mensagens com erro
   - Identificar causa raiz
   - Implementar retry

2. **Implementar Provider Kolmeya**
   - Criar módulo básico
   - Configurar envio simples
   - Testar com 10-20 mensagens

3. **Configurar Webhook**
   - Endpoint para receber status
   - Atualização automática de estado

### Médio Prazo (1-2 meses)

1. **Automações CRM**
   - SMS automático em lead novo
   - SMS de follow-up pós-venda
   - SMS de lembrete de pagamento

2. **Templates Inteligentes**
   - Personalização com dados do cliente
   - A/B testing de mensagens
   - Horário otimizado de envio

3. **Analytics**
   - Dashboard de performance
   - ROI por campanha
   - Taxa de conversão via SMS

### Longo Prazo (3-6 meses)

1. **WhatsApp Integration**
   - Usar segmentação WhatsApp Kolmeya
   - Fallback SMS → WhatsApp
   - Chat unificado

2. **IA e Automação**
   - Qualificação automática de respostas
   - Chatbot para respostas comuns
   - Sentiment analysis

3. **Multi-Canal**
   - Orquestração SMS + Email + WhatsApp
   - Preferência de canal por cliente
   - Journey personalizado

---

## 🔧 Exemplo de Código - Envio SMS

### Python - Provider Kolmeya
```python
import requests
from odoo import models, api

class SmsApiKolmeya(models.AbstractModel):
    _inherit = 'sms.api'

    @api.model
    def _send_sms_kolmeya(self, numbers, message):
        """Enviar SMS via Kolmeya API"""

        url = "https://kolmeya.com.br/api/v1/sms/store"
        headers = {
            "Authorization": "Bearer 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY",
            "Content-Type": "application/json"
        }

        # Preparar payload (até 1000 números)
        payload = {
            "messages": [
                {
                    "to": number,
                    "message": message,
                    "segment_id": 1  # Centro de custo
                }
                for number in numbers[:1000]
            ]
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            return {
                'success': True,
                'job_id': result.get('job_id'),
                'request_id': result.get('request_id')
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
```

### Webhook - Receber Status
```python
from odoo import http
from odoo.http import request

class KolmeyaWebhook(http.Controller):

    @http.route('/kolmeya/webhook/status', type='json', auth='public', csrf=False)
    def kolmeya_status_update(self, **kwargs):
        """Receber updates de status da Kolmeya"""

        data = request.jsonrequest

        # Mapear status Kolmeya → Odoo
        status_map = {
            1: 'outgoing',
            2: 'sent',
            3: 'sent',
            4: 'error',
            5: 'error',
            6: 'error'
        }

        sms_id = data.get('reference_id')  # ID do Odoo
        kolmeya_status = data.get('status')

        sms = request.env['sms.sms'].sudo().browse(int(sms_id))
        if sms:
            sms.write({
                'state': status_map.get(kolmeya_status, 'error'),
                'failure_type': data.get('error_code') if kolmeya_status in [4,5,6] else False
            })

        return {'success': True}
```

---

## 📈 Casos de Uso - Odoo RealCred

### 1. CRM - Novo Lead
```
Trigger: Lead criado via website
Ação: Enviar SMS de boas-vindas
Template: "Olá {nome}! Recebemos seu pedido de empréstimo. Em breve nossa equipe entrará em contato. RealCred"
```

### 2. Vendas - Proposta Enviada
```
Trigger: Orçamento enviado
Ação: SMS com link da proposta
Template: "Sua proposta está pronta! Acesse: {link}. Dúvidas? Ligue (11) 1234-5678"
```

### 3. Cobrança - Lembrete de Vencimento
```
Trigger: 3 dias antes do vencimento
Ação: SMS de lembrete
Template: "Lembrete: Parcela de R$ {valor} vence em {data}. PIX: {chave_pix}"
```

### 4. Pós-Venda - Satisfação
```
Trigger: 7 dias após contrato
Ação: Pesquisa de satisfação
Template: "Como foi sua experiência com a RealCred? Responda 1-5. Sua opinião é importante!"
```

### 5. Stock - Confirmação de Entrega
```
Trigger: Pedido enviado
Ação: SMS de rastreamento
Template: "Seu pedido #{numero} foi enviado! Rastreie: {link_rastreio}"
```

---

## 🎯 Métricas de Sucesso

### KPIs Técnicos
- Taxa de entrega: > 98%
- Tempo médio de envio: < 5 segundos
- Taxa de erro: < 2%
- Uptime API: > 99.5%

### KPIs de Negócio
- Taxa de abertura: > 90%
- Taxa de resposta: > 15%
- Conversão lead → venda: Benchmark atual + 10%
- ROI por SMS: > R$ 3 para cada R$ 1 gasto

---

## 💰 Estimativa de Custos

### Desenvolvimento
```
Fase 1 (Preparação):        8-16 horas
Fase 2 (Core):             16-24 horas
Fase 3 (Avançado):         24-40 horas
Fase 4 (Otimização):       16-24 horas
---------------------------------------------
TOTAL:                     64-104 horas
```

### Operacional
```
- Custo por SMS: Consultar com Kolmeya
- Volume estimado/mês: A definir
- Custo mensal estimado: A calcular
```

---

## ⚠️ Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| IP não whitelistado | Média | Alto | Validar antes de deploy |
| Limite de API excedido | Baixa | Médio | Implementar queue + retry |
| Webhook não recebido | Média | Médio | Polling alternativo de status |
| Token expirado | Baixa | Alto | Monitoramento + alerta |
| Números inválidos | Alta | Baixo | Validação pré-envio |
| Custo excessivo | Média | Alto | Budget alerts + aprovação |

---

## 📝 Checklist de Deploy

### Pré-Deploy
- [ ] IP whitelistado na Kolmeya
- [ ] Token validado e funcionando
- [ ] Módulo `sms_kolmeya` desenvolvido
- [ ] Testes em ambiente staging
- [ ] Documentação técnica completa
- [ ] Treinamento da equipe

### Deploy
- [ ] Backup do database
- [ ] Instalar módulo em produção
- [ ] Configurar token no Odoo
- [ ] Configurar webhook URL
- [ ] Testar envio de 5-10 SMS
- [ ] Validar recebimento de status

### Pós-Deploy
- [ ] Monitorar logs por 48h
- [ ] Validar 100% das mensagens
- [ ] Ajustar rate limiting se necessário
- [ ] Coletar feedback da equipe
- [ ] Documentar lições aprendidas

---

## 🔗 Links Úteis

- **Kolmeya Website:** https://kolmeya.com.br/
- **API Docs:** https://kolmeya.com.br/docs/api/
- **Odoo SMS Module:** `/odoo/odoo-server/addons/sms/`
- **Documentação Odoo SMS:** https://www.odoo.com/documentation/15.0/developer/howtos/sms_gateway.html

---

## 📞 Contatos

### Kolmeya Suporte
- Telefone: (11) 99331-3806
- Email: (consultar no painel)
- WhatsApp: Disponível

### Responsável Interno
- Email: SUPERVISAO@REALCREDEMPRESTIMO.COM.BR

---

## 📅 Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| 2025-11-15 | 1.0 | Documento inicial - Análise completa Kolmeya | Claude Code |

---

**Status:** ✅ Documentação Completa - Aguardando aprovação para implementação

**Próximo Passo:** Whitelist de IP + Desenvolvimento do módulo `sms_kolmeya`
