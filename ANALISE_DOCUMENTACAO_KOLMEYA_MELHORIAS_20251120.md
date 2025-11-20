# 📚 Análise Completa: Documentação API Kolmeya + Melhorias

> **Data:** 2025-11-20
> **Fonte:** Documentação oficial Kolmeya (https://kolmeya.com.br/docs/api/)

---

## 🔍 **DESCOBERTAS CRÍTICAS**

### **1. URL BASE INCORRETA** ❌

**Problema Identificado:**
- **Nossa implementação:** `https://api.kolmeya.com/v1`
- **URL correta (documentação):** `https://kolmeya.com.br/api/v1`

**Impacto:**
- ❌ Todas as requisições estão falhando por URL incorreta
- ❌ Erro SSL pode ser causado por tentar acessar domínio errado

**Correção Necessária:**
```python
# ANTES (ERRADO)
kolmeya_api_url = 'https://api.kolmeya.com/v1'

# DEPOIS (CORRETO)
kolmeya_api_url = 'https://kolmeya.com.br/api/v1'
```

---

## 📋 **ENDPOINTS DA API KOLMEYA**

### **Endpoints Principais:**

| Endpoint | Método | Descrição | Status Implementação |
|----------|--------|-----------|----------------------|
| `/sms/store` | POST | Enviar SMS | ✅ Implementado (mas URL errada) |
| `/sms/balance` | POST | Consultar saldo | ✅ Implementado (mas URL errada) |
| `/sms/reply` | POST | Buscar replies | ✅ Implementado (mas URL errada) |
| `/sms/replyByWeb` | POST | Buscar replies via webhook | ❌ Não implementado |
| `/sms/status/message` | POST | Status de mensagem específica | ❌ Não implementado |
| `/sms/status/request` | POST | Status de requisição | ❌ Não implementado |
| `/sms/webhook` | POST | Configurar webhook | ❌ Não implementado |
| `/sms/segments` | POST | Calcular segmentos da mensagem | ❌ Não implementado |
| `/sms/apis` | POST | Listar APIs disponíveis | ❌ Não implementado |
| `/sms/accesses` | POST | Gerenciar acessos | ❌ Não implementado |
| `/sms/jobs/pause` | POST | Pausar job de envio | ❌ Não implementado |
| `/sms/jobs/play` | POST | Retomar job de envio | ❌ Não implementado |
| `/sms/reports/statuses` | POST | Relatório de statuses | ❌ Não implementado |
| `/sms/reports/statuses-by-job` | POST | Statuses por job | ❌ Não implementado |
| `/sms/reports/jobs` | POST | Relatório de jobs | ❌ Não implementado |
| `/sms/reports/quantity-jobs` | POST | Quantidade de jobs | ❌ Não implementado |
| `/sms/reports/invalid-records` | POST | Registros inválidos | ❌ Não implementado |
| `/sms/store-token` | POST | Armazenar token | ❌ Não implementado |
| `/sms/layouts` | POST | Layouts de mensagem | ❌ Não implementado |
| `/blacklist/store` | POST | Adicionar à blacklist | ❌ Não implementado |
| `/blacklist/destroy` | POST | Remover da blacklist | ❌ Não implementado |

---

## 🔧 **MELHORIAS IDENTIFICADAS**

### **1. CORREÇÃO URGENTE: URL Base** 🚨

**Prioridade:** 🔴 **CRÍTICA**

**Arquivo:** `sms_core_unified/models/sms_provider.py`

**Mudança:**
```python
# Linha ~30
kolmeya_api_url = fields.Char(
    string='Kolmeya API URL',
    default='https://kolmeya.com.br/api/v1'  # CORRIGIDO
)
```

---

### **2. Implementar Cálculo de Segmentos** 📊

**Prioridade:** 🟡 **MÉDIA**

**Descrição:**
A API Kolmeya oferece endpoint `/sms/segments` para calcular quantos segmentos uma mensagem terá (SMS pode ter múltiplos segmentos se > 160 caracteres).

**Benefício:**
- Calcular custo exato antes de enviar
- Mostrar ao usuário quantos segmentos serão enviados
- Melhorar estimativa de custo

**Implementação:**
```python
def _calculate_sms_segments(self, message_body):
    """Calculate SMS segments using Kolmeya API"""
    response = requests.post(
        f'{self.kolmeya_api_url}/sms/segments',
        json={'message': message_body},
        headers={'Authorization': f'Bearer {self.kolmeya_api_key}'},
        timeout=self.timeout_seconds
    )
    response.raise_for_status()
    result = response.json()
    return result.get('segments', [])
```

---

### **3. Implementar Consulta de Status de Mensagem** 📱

**Prioridade:** 🟡 **MÉDIA**

**Descrição:**
Endpoint `/sms/status/message` permite consultar status específico de uma mensagem enviada.

**Benefício:**
- Atualizar status de mensagens antigas
- Verificar delivery status manualmente
- Sincronizar status perdidos

**Implementação:**
```python
def get_message_status(self, external_id):
    """Get status of a specific message"""
    response = requests.post(
        f'{self.kolmeya_api_url}/sms/status/message',
        json={'message_id': external_id},
        headers={'Authorization': f'Bearer {self.kolmeya_api_key}'},
        timeout=self.timeout_seconds
    )
    response.raise_for_status()
    return response.json()
```

---

### **4. Implementar Sincronização de Blacklist** 🚫

**Prioridade:** 🟡 **MÉDIA**

**Descrição:**
Endpoints `/blacklist/store` e `/blacklist/destroy` permitem sincronizar blacklist com Kolmeya.

**Benefício:**
- Sincronizar blacklist bidirecionalmente
- Garantir que números bloqueados não sejam enviados
- Manter consistência entre Odoo e Kolmeya

**Implementação:**
```python
def sync_blacklist_to_kolmeya(self):
    """Sync blacklist entries to Kolmeya"""
    blacklist_entries = self.env['sms.blacklist'].search([
        ('active', '=', True)
    ])
    
    for entry in blacklist_entries:
        requests.post(
            f'{self.kolmeya_api_url}/blacklist/store',
            json={'phone': entry.phone},
            headers={'Authorization': f'Bearer {self.kolmeya_api_key}'},
            timeout=self.timeout_seconds
        )
```

---

### **5. Implementar Configuração de Webhook** 🔔

**Prioridade:** 🟢 **BAIXA** (já temos webhook básico)

**Descrição:**
Endpoint `/sms/webhook` permite configurar webhook programaticamente.

**Benefício:**
- Configurar webhook automaticamente ao criar provider
- Atualizar URL de webhook sem intervenção manual
- Validar webhook antes de usar

**Implementação:**
```python
def configure_webhook(self, webhook_url):
    """Configure webhook URL in Kolmeya"""
    response = requests.post(
        f'{self.kolmeya_api_url}/sms/webhook',
        json={'url': webhook_url},
        headers={'Authorization': f'Bearer {self.kolmeya_api_key}'},
        timeout=self.timeout_seconds
    )
    response.raise_for_status()
    return response.json()
```

---

### **6. Implementar Relatórios** 📈

**Prioridade:** 🟢 **BAIXA**

**Descrição:**
Vários endpoints de relatórios disponíveis:
- `/sms/reports/statuses` - Status geral
- `/sms/reports/jobs` - Jobs de envio
- `/sms/reports/invalid-records` - Registros inválidos

**Benefício:**
- Dashboard mais completo
- Analytics avançados
- Identificar problemas de envio

---

### **7. Implementar Controle de Jobs** ⏸️▶️

**Prioridade:** 🟢 **BAIXA**

**Descrição:**
Endpoints `/sms/jobs/pause` e `/sms/jobs/play` permitem pausar/retomar jobs de envio em massa.

**Benefício:**
- Pausar campanhas em andamento
- Retomar campanhas pausadas
- Controle fino sobre envios em massa

---

### **8. Melhorar Tratamento de Webhooks** 🔄

**Prioridade:** 🟡 **MÉDIA**

**Descrição:**
A documentação menciona dois tipos de webhooks:
1. **Webhook de Campanha** - Notificações sobre campanhas
2. **Webhook de Requisição** - Notificações sobre requisições individuais

**Melhoria:**
- Implementar handler para ambos os tipos
- Validar assinatura do webhook (se disponível)
- Processar diferentes tipos de eventos

---

### **9. Implementar Busca de Replies via Webhook** 💬

**Prioridade:** 🟡 **MÉDIA**

**Descrição:**
Endpoint `/sms/replyByWeb` permite buscar replies de forma mais eficiente.

**Benefício:**
- Buscar replies de forma mais eficiente
- Reduzir carga no servidor
- Melhor integração com webhooks

---

### **10. Melhorar Tratamento de Erros** ⚠️

**Prioridade:** 🟡 **MÉDIA**

**Melhorias:**
- Tratar códigos de erro específicos da API
- Implementar retry inteligente baseado no tipo de erro
- Logs mais detalhados com informações da resposta

**Códigos de Erro Comuns (da documentação):**
- `401` - Não autorizado (API key inválida)
- `403` - Proibido (sem permissão)
- `422` - Validação falhou (dados inválidos)

---

## 📊 **STATUS DA API KOLMEYA**

**Status Page:** https://status.kolmeya.com.br

**Status Atual:**
- ✅ **Operacional** (última verificação: 2025-11-20)
- ⚠️ **Incidente em 18/11** - Resolvido às 12:00

**Recomendação:**
- Monitorar status page antes de reportar problemas
- Implementar verificação automática de status

---

## 🎯 **PLANO DE AÇÃO PRIORITÁRIO**

### **Fase 1: Correções Críticas** (URGENTE)
1. ✅ Corrigir URL base da API
2. ✅ Testar conexão com URL correta
3. ✅ Atualizar todos os métodos que usam a URL

### **Fase 2: Melhorias Essenciais** (1-2 semanas)
1. Implementar cálculo de segmentos
2. Implementar consulta de status de mensagem
3. Melhorar tratamento de erros
4. Implementar sincronização de blacklist

### **Fase 3: Features Avançadas** (1 mês)
1. Implementar relatórios
2. Implementar controle de jobs
3. Melhorar webhooks
4. Implementar busca de replies via webhook

---

## 📝 **NOTAS IMPORTANTES**

### **Autenticação:**
- ✅ Usando Bearer Token corretamente
- ✅ Header: `Authorization: Bearer {token}`

### **Content-Type:**
- ✅ Usando `application/json` corretamente
- ✅ Headers corretos em todas as requisições

### **Timeout:**
- ✅ Timeout configurável (30s padrão)
- ✅ Retry logic implementado

### **Webhook:**
- ✅ Webhook básico implementado
- ⚠️ Falta validação de assinatura (se disponível)
- ⚠️ Falta suporte para múltiplos tipos de webhook

---

## 🔗 **REFERÊNCIAS**

- **Documentação:** https://kolmeya.com.br/docs/api/
- **Status Page:** https://status.kolmeya.com.br
- **Webhook Campanhas:** https://kolmeya.com.br/docs/api/articles/webhook-campanhas
- **Webhook Requisições:** https://kolmeya.com.br/docs/api/articles/webhook-requisicoes

---

**Próximo Passo:** Corrigir URL base e testar conexão novamente.

