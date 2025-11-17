# Webhooks Kolmeya - Implementação

**Data**: 2025-11-15
**Status**: ✅ Implementado
**Módulo**: sms_kolmeya

## 📡 Endpoints Criados

### 1. Webhook de Respostas
**URL**: `https://odoo.semprereal.com/kolmeya/webhook/reply`
**Método**: POST (JSON)
**Auth**: Public (sem autenticação - Kolmeya não suporta)

**Payload esperado**:
```json
{
    "phone": "5548999999999",
    "message": "Resposta do cliente",
    "reference": "message_id",
    "data": "2025-11-15 14:30:00"
}
```

**Funcionalidades**:
- ✅ Cria SMS incoming no Odoo
- ✅ Busca mensagem original por reference ou phone
- ✅ Linka resposta à mensagem original (parent_id)
- ✅ Posta no chatter da mensagem original
- ✅ Cria atividade para o vendedor responsável
- ✅ Notifica vendedor automaticamente

### 2. Webhook de Status
**URL**: `https://odoo.semprereal.com/kolmeya/webhook/status`
**Método**: POST (JSON)
**Auth**: Public

**Payload esperado**:
```json
{
    "id": "message_uuid",
    "reference": "our_reference",
    "status": "entregue",
    "status_code": 3,
    "phone": "5548999999999"
}
```

**Mapeamento de Status**:
- 1 → outgoing (Tentando enviar)
- 2 → sent (Enviado)
- 3 → delivered (Entregue ✅)
- 4 → error (Não entregue ❌)
- 5 → rejected (Rejeitado ⛔)
- 6 → expired (Expirado ⏰)

**Funcionalidades**:
- ✅ Atualiza estado do SMS automaticamente
- ✅ Registra data de entrega
- ✅ Posta update no chatter com emoji

## 🔧 Configuração no Kolmeya

Para ativar os webhooks na plataforma Kolmeya:

1. **Acesse**: https://kolmeya.com.br/
   - Login: SUPERVISAO@REALCREDEMPRESTIMO.COM.BR
   - Senha: Anca741@

2. **Configurações > Webhooks**

3. **Webhook de Respostas**:
   - URL: `https://odoo.semprereal.com/kolmeya/webhook/reply`
   - Método: POST
   - Content-Type: application/json
   - Eventos: SMS Reply

4. **Webhook de Status**:
   - URL: `https://odoo.semprereal.com/kolmeya/webhook/status`
   - Método: POST
   - Content-Type: application/json
   - Eventos: Delivery Status

## 🚀 Fluxo de Funcionamento

### Fluxo de Resposta (Reply)

```
1. Cliente responde SMS
   ↓
2. Kolmeya recebe resposta
   ↓
3. Kolmeya envia POST para /kolmeya/webhook/reply
   ↓
4. Odoo cria SMS incoming
   ↓
5. Odoo busca SMS original (por reference ou phone)
   ↓
6. Odoo linka resposta ao original (parent_id)
   ↓
7. Odoo posta no chatter da mensagem
   ↓
8. Odoo cria atividade para vendedor
   ↓
9. Vendedor recebe notificação automática
```

### Fluxo de Status

```
1. SMS é enviado via Kolmeya
   ↓
2. Kolmeya processa entrega
   ↓
3. Kolmeya envia status update
   ↓
4. Odoo atualiza estado do SMS
   ↓
5. Odoo registra data de entrega (se delivered)
   ↓
6. Odoo posta update no chatter
```

## 📊 Sistema de Alertas

### Quando Alguém Responde SMS

O sistema automaticamente:

1. **Cria Atividade** para o vendedor responsável
   - Tipo: To Do
   - Título: "📱 SMS Reply from {Cliente}"
   - Descrição: Texto da resposta
   - Prazo: Imediato (hoje)
   - Modelo: res.partner (contato que respondeu)

2. **Vendedor vê notificação** em:
   - Badge de atividades (topo direito)
   - Lista de atividades pendentes
   - Timeline do parceiro

3. **Vendedor pode**:
   - Ver resposta completa
   - Responder direto pelo Odoo
   - Marcar atividade como concluída

## 🔒 Segurança

⚠️ **IMPORTANTE**: Webhooks são públicos (auth='public') porque:
- Kolmeya não suporta autenticação Bearer em webhooks
- Não há dados sensíveis nos webhooks (apenas phone + message)
- Validação é feita por conteúdo (procura mensagem existente)

**Melhorias futuras**:
- [ ] Adicionar IP whitelist (permitir apenas IPs da Kolmeya)
- [ ] Implementar assinatura JWT/HMAC se Kolmeya suportar
- [ ] Rate limiting nos endpoints

## 🧪 Testando Webhooks

### Teste Manual via curl

**Teste Reply**:
```bash
curl -X POST https://odoo.semprereal.com/kolmeya/webhook/reply \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "5548991910234",
    "message": "Tenho interesse! Me ligue!",
    "reference": "1",
    "data": "2025-11-15 15:00:00"
  }'
```

**Teste Status**:
```bash
curl -X POST https://odoo.semprereal.com/kolmeya/webhook/status \
  -H "Content-Type: application/json" \
  -d '{
    "id": "uuid-da-mensagem",
    "reference": "1",
    "status": "entregue",
    "status_code": 3,
    "phone": "5548991910234"
  }'
```

## 📝 Logs

Todos os webhooks geram logs em `/var/log/odoo/odoo-server.log`:

```python
_logger.info(f"Kolmeya reply webhook received: {data}")
_logger.info(f"Reply SMS created: {reply_sms.id}")
_logger.info(f"Activity created for user {user.name}")
```

Para monitorar webhooks em tempo real:
```bash
sudo tail -f /var/log/odoo/odoo-server.log | grep kolmeya_webhook
```

## ✅ Checklist de Implementação

- ✅ Controller criado (kolmeya_webhooks.py)
- ✅ Endpoint /reply implementado
- ✅ Endpoint /status implementado
- ✅ Sistema de notificações (atividades)
- ✅ Integração com chatter
- ✅ Tratamento de erros e logging
- ⏳ Configuração no painel Kolmeya (pendente)
- ⏳ Testes com webhooks reais (pendente)
- ⏳ Documentação para usuários finais (pendente)

## 🎯 Próximos Passos

1. **Configurar webhooks na plataforma Kolmeya**
2. **Testar com SMS real**:
   - Enviar SMS para número de teste
   - Responder SMS
   - Verificar se webhook chega
   - Confirmar notificação ao vendedor
3. **Monitorar logs** nas primeiras 24h
4. **Ajustar conforme necessário**

## 📚 Referências

- [Documentação Kolmeya API](https://kolmeya.com.br/docs/api/)
- [Odoo Controllers](https://www.odoo.com/documentation/15.0/developer/reference/backend/http.html)
- [Mail Activities](https://www.odoo.com/documentation/15.0/developer/reference/backend/orm.html#mail-activity)
