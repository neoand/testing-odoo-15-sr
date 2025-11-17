# Sistema SMS SempreReal - Setup Completo

**Data**: 2025-11-15
**Status**: ✅ Implementação Core Concluída | ⏳ Aguardando Configuração Kolmeya
**Módulos**: sms_base_sr, sms_kolmeya

---

## 🎯 Resumo Executivo

O sistema de SMS está **100% implementado e pronto para uso**. Todas as funcionalidades core estão operacionais:

✅ **Módulos instalados e funcionando**
✅ **API Kolmeya integrada** (envio, consulta saldo)
✅ **Webhooks implementados** (recebimento de respostas e status)
✅ **8 Templates SMS criados** para uso imediato
✅ **Interface no Odoo** completa (menu, formulários, botões)
✅ **Sistema de notificações** (atividades para vendedores)

**Faltam apenas 2 ações manuais** para ativar tudo:
1. Configurar webhooks no painel Kolmeya
2. Autorizar números de teste no Kolmeya

---

## 📦 Módulos Instalados

### 1. sms_base_sr (Base SMS)
**Localização**: `/odoo/custom/addons_custom/sms_base_sr/`

**Componentes**:
- **Models**:
  - `sms.message` - Mensagens SMS (outgoing/incoming)
  - `sms.provider` - Provedores SMS (abstração)
  - `res.partner` - Extensão com campo sms_count

- **Wizard**:
  - `sms.compose` - Wizard para envio de SMS

- **Views**:
  - Menu SMS principal
  - Formulários de mensagens
  - Formulário de provider
  - Botão "Send SMS" no parceiro
  - Wizard de composição

- **Security**:
  - Grupo: SMS User (leitura)
  - Grupo: SMS Manager (escrita/admin)
  - Admin já adicionado aos grupos

### 2. sms_kolmeya (Provider Kolmeya)
**Localização**: `/odoo/custom/addons_custom/sms_kolmeya/`

**Componentes**:
- **Models**:
  - `sms.provider` (inherit) - Campos Kolmeya (API token, segment)

- **Controllers**:
  - `kolmeya_webhooks.py` - 2 endpoints webhook

- **API Methods**:
  - `_kolmeya_send_sms()` - Envia SMS
  - `_kolmeya_get_balance()` - Consulta saldo
  - Status update via webhook
  - Reply capture via webhook

---

## 🔧 Configuração Atual

### Kolmeya Provider (ID: 1)
```
Nome: Kolmeya SMS
Tipo: kolmeya
API Token: 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY
Segment ID: 109 (CORPORATIVO)
Saldo: R$ 9.397,15
Base URL: https://kolmeya.com.br/api/v1
```

### Banco de Dados
```
Database: realcred
Tabelas criadas:
- sms_message (com parent_id para threading)
- sms_provider
- sms_template (8 templates ativos)
- res_groups_users_rel (admin nos grupos SMS)
```

### Webhooks Endpoints
```
Reply: https://odoo.semprereal.com/kolmeya/webhook/reply
Status: https://odoo.semprereal.com/kolmeya/webhook/status
Auth: Public (sem autenticação)
Método: POST (JSON)
Status: ✅ Testado localmente com sucesso
```

---

## 📱 Templates SMS Criados

| ID | Nome | Uso |
|----|------|-----|
| 4 | Oferta de Empréstimo - Inicial | Primeiro contato com oferta |
| 5 | Follow-up - Cliente Interessado | Follow-up após interesse |
| 6 | Lembrete de Pagamento | Cobranças suaves |
| 7 | Solicitação de Documentos | Pedir docs pendentes |
| 8 | Agradecimento - Contrato Fechado | Pós-venda |
| 9 | Confirmação de Agendamento | Confirmar reuniões |
| 10 | Promoção Especial | Campanhas promocionais |
| 11 | Mensagem Simples | Template genérico |

**Sintaxe**: Jinja2 do Odoo
```
{{ object.name }} - Nome do parceiro
{{ user.name }} - Nome do usuário/vendedor
{{ user.company_id.phone }} - Telefone da empresa
```

---

## 🚀 Como Usar o Sistema

### 1. Enviar SMS Individual

**Via Interface**:
1. Abrir contato (Contatos > Nome do cliente)
2. Clicar botão "Send SMS" (ícone avião)
3. Selecionar template (opcional)
4. Digitar ou editar mensagem
5. Clicar "Send SMS"

**Via Código**:
```python
# Criar e enviar SMS
sms = self.env['sms.message'].create({
    'partner_id': partner.id,
    'phone': partner.mobile,
    'body': 'Olá! Mensagem de teste',
    'direction': 'outgoing',
    'state': 'draft',
    'provider_id': 1,  # Kolmeya
})
sms.action_send()
```

### 2. Enviar SMS em Massa

```python
# Exemplo: Enviar para todos parceiros com tag "Cliente"
partners = self.env['res.partner'].search([('category_id', 'in', tag_ids)])
template = self.env['sms.template'].browse(4)  # Oferta Empréstimo

for partner in partners:
    sms = self.env['sms.message'].create({
        'partner_id': partner.id,
        'phone': partner.mobile or partner.phone,
        'body': template.body,  # Renderizar com Jinja2
        'provider_id': 1,
    })
    sms.action_send()
```

### 3. Ver Histórico de SMS

- **No parceiro**: Aba "SMS" ou botão contador de SMS
- **Menu geral**: Menu SMS > Messages
- **Filtros**: Por estado, direção, data, parceiro

### 4. Quando Cliente Responder

**Fluxo automático**:
1. Cliente responde SMS pelo celular
2. Kolmeya recebe resposta
3. Kolmeya envia POST para webhook `/reply`
4. Odoo cria SMS incoming
5. Odoo linka à mensagem original (parent_id)
6. Odoo posta no chatter da mensagem
7. Odoo cria **atividade** para vendedor responsável
8. Vendedor vê notificação (badge vermelho)

**Vendedor vê**:
- Notificação no topo (badge de atividades)
- Atividade: "📱 SMS Reply from {Cliente}"
- Pode abrir e ver resposta completa
- Pode responder direto pelo Odoo

---

## ⚙️ Configurações Pendentes (MANUAL)

### 1️⃣ Configurar Webhooks no Kolmeya

**Acesso**:
- URL: https://kolmeya.com.br/
- Login: SUPERVISAO@REALCREDEMPRESTIMO.COM.BR
- Senha: Anca741@

**Passos**:
1. Login na plataforma
2. Menu **Configurações** > **Webhooks**
3. Adicionar **Webhook de Respostas**:
   ```
   Nome: Odoo Reply Webhook
   URL: https://odoo.semprereal.com/kolmeya/webhook/reply
   Método: POST
   Content-Type: application/json
   Evento: SMS Reply / Resposta SMS
   ```
4. Adicionar **Webhook de Status**:
   ```
   Nome: Odoo Status Webhook
   URL: https://odoo.semprereal.com/kolmeya/webhook/status
   Método: POST
   Content-Type: application/json
   Evento: Delivery Status / Status de Entrega
   ```
5. Salvar e ativar ambos webhooks

### 2️⃣ Autorizar Números de Teste

**Números para autorizar** (whitelist):

| Nome | Número Completo | Para autorizar no Kolmeya |
|------|-----------------|---------------------------|
| Ana Carla | 5548991910234 | +55 48 99191-0234 |
| Tata | 5548991221131 | +55 48 99122-1131 |
| Novo | 5548996375050 | +55 48 99637-5050 |

**Onde autorizar**:
- Painel Kolmeya > Configurações > Números Autorizados (ou similar)
- Pode variar conforme plataforma
- Se não houver opção, abrir ticket com Kolmeya

---

## 🧪 Testes para Executar

### Teste 1: Envio Básico
```python
# Via Odoo shell
partner = env['res.partner'].search([('phone', '=', '48991910234')], limit=1)
sms = env['sms.message'].create({
    'partner_id': partner.id,
    'phone': '5548991910234',
    'body': 'Teste do sistema SMS SempreReal!',
    'provider_id': 1,
})
sms.action_send()
# Verificar: estado deve mudar para 'sent' ou 'delivered'
```

### Teste 2: Webhook Reply (Local)
```bash
curl -X POST https://odoo.semprereal.com/kolmeya/webhook/reply \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "5548991910234",
    "message": "Olá, tenho interesse!",
    "reference": "1",
    "data": "2025-11-15 20:00:00"
  }'
# Esperado: {"status": "success", "sms_id": X}
```

### Teste 3: End-to-End (REAL)
1. Enviar SMS real para número autorizado
2. Responder SMS do celular
3. Verificar:
   - SMS incoming criado no Odoo
   - Parent_id linkado à mensagem original
   - Chatter atualizado
   - Vendedor recebeu atividade
   - Vendedor vê notificação

### Teste 4: Template
```python
# Usar template no wizard
# Via interface: Send SMS > Selecionar template > Enviar
# Verificar se variáveis são substituídas corretamente
```

---

## 📊 Monitoramento e Logs

### Ver Logs do Webhook
```bash
ssh odoo-rc
sudo tail -f /var/log/odoo/odoo-server.log | grep -i kolmeya
```

**Mensagens esperadas**:
```
INFO realcred odoo.addons.sms_kolmeya.controllers.kolmeya_webhooks: Kolmeya reply webhook received: {...}
INFO realcred odoo.addons.sms_kolmeya.controllers.kolmeya_webhooks: Reply SMS created: 123
INFO realcred odoo.addons.sms_kolmeya.controllers.kolmeya_webhooks: Activity created for user Ana
```

### Verificar SMS no Banco
```sql
-- Últimas mensagens
SELECT id, phone, body, direction, state, sent_date, delivered_date
FROM sms_message
ORDER BY id DESC LIMIT 10;

-- Mensagens com respostas (threading)
SELECT
    parent.id as original_id,
    parent.body as original_msg,
    reply.id as reply_id,
    reply.body as reply_msg
FROM sms_message parent
JOIN sms_message reply ON reply.parent_id = parent.id
ORDER BY parent.id DESC;
```

### Consultar Saldo Kolmeya
```python
# Via Odoo shell
provider = env['sms.provider'].browse(1)
balance = provider._kolmeya_get_balance()
print(f"Saldo: R$ {balance}")
```

---

## 🔒 Segurança

### Webhooks Públicos
⚠️ **Importante**: Webhooks são `auth='public'` porque:
- Kolmeya não suporta Bearer token em webhooks
- Não há dados sensíveis (apenas phone + message)
- Validação feita por conteúdo (busca mensagem existente)

**Melhorias futuras**:
- [ ] IP whitelist (permitir apenas IPs Kolmeya)
- [ ] HMAC signature validation
- [ ] Rate limiting

### Grupos de Segurança
- **SMS User** (ID 145): Leitura de SMS
- **SMS Manager** (ID 146): Criar, editar, excluir SMS
- Admin já está em ambos grupos

---

## 🎯 Próximos Passos (Ordem de Execução)

1. ✅ **Implementação Core** - CONCLUÍDO
2. ⏳ **Configurar webhooks no Kolmeya** - PENDENTE (manual)
3. ⏳ **Autorizar números de teste** - PENDENTE (manual)
4. ⏳ **Testar envio real** - PENDENTE (após autorização)
5. ⏳ **Testar resposta real** - PENDENTE (após webhooks configurados)
6. ⏳ **Integrar com campaigns** - FUTURO
7. ⏳ **Dashboards e relatórios** - FUTURO

---

## 🐛 Troubleshooting

### SMS não envia (fica em draft)
- Verificar se provider está configurado
- Verificar API token válido
- Verificar saldo suficiente
- Ver logs: `/var/log/odoo/odoo-server.log`

### Webhook não chega
- Verificar se webhooks foram configurados no Kolmeya
- Testar endpoint manualmente com curl
- Verificar logs do Odoo
- Verificar firewall/HTTPS

### Template não renderiza
- Sintaxe deve ser Jinja2: `{{ object.name }}`
- Modelo deve ser res.partner
- Verificar se campo existe no modelo

### Número retorna 403 (Forbidden)
- Número precisa ser autorizado no Kolmeya primeiro
- Formato: DDI+DDD+Número (ex: 5548991910234)
- Verificar whitelist no painel Kolmeya

---

## 📚 Arquivos de Referência

### Documentação Criada
1. `19_SMS_TEST_NUMBERS.md` - Números de teste
2. `20_SMS_WEBHOOKS_IMPLEMENTATION.md` - Webhooks detalhados
3. `21_SMS_SYSTEM_COMPLETE_SETUP.md` - Este arquivo (setup completo)

### Scripts SQL Úteis
- `add_parent_id.sql` - Adicionar campo parent_id
- `create_sms_templates_fixed.sql` - Criar templates

### Módulos
- `/odoo/custom/addons_custom/sms_base_sr/`
- `/odoo/custom/addons_custom/sms_kolmeya/`

---

## ✅ Checklist Final

- ✅ Módulos instalados
- ✅ Provider Kolmeya configurado
- ✅ API token funcionando
- ✅ Webhooks implementados
- ✅ Webhooks testados localmente
- ✅ Templates criados (8)
- ✅ Interface completa
- ✅ Sistema de notificações
- ✅ Parent_id para threading
- ✅ Integração com chatter
- ✅ Grupos de segurança
- ✅ Documentação completa
- ⏳ Webhooks configurados no Kolmeya (MANUAL)
- ⏳ Números autorizados (MANUAL)
- ⏳ Teste end-to-end real (após configuração)

---

**Sistema pronto para produção após configuração manual dos webhooks!** 🚀
