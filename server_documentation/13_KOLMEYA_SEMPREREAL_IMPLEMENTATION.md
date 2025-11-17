# Kolmeya SMS Integration - SempreReal Strategy

**Date:** 2025-11-15
**Status:** Implementation Plan - Ready to Execute
**Focus:** Aposentados/Pensionistas + Respostas Bidirecionais

---

## 📊 Situação Atual - Análise Completa

### Database Real

**Tabela `contacts_realcred_batch`:**
```
Total de registros: 2.5+ MILHÕES de aposentados/pensionistas
├── Espécie 41: 1,128,302 registros
├── Espécie 21: 360,322 registros
├── Espécie 87: 350,282 registros
├── Espécie 88: 251,830 registros
└── Outras espécies: ~500K registros

Campos principais:
- telefone1, whatsapp1 (para envio)
- cpf, name, nb (identificação)
- vi_rmi, salario, margem* (dados financeiros)
- updated_limit, falecido (filtros de validação)
- campaing_id (vínculo com campanha)
```

### Módulo Existente: `contacts_realcred`

**Localização:** `/odoo/custom/addons_custom/contacts_realcred/`

**Funcionalidade Atual:**
```python
# Método check_data_kolmeya_send() EXISTE mas NÃO ENVIA!
def check_data_kolmeya_send(self):
    # 1. Busca campanhas com state_sms = 'process'
    # 2. Monta payload com substituição de variáveis:
    #    |NOME| → contact.name
    #    |CPF| → contact.cpf
    #    |VI_RM| → contact.vi_rmi
    # 3. Valida: telefone1 AND updated_limit AND falecido == False
    # 4. Monta structure: {'reference': campaign, 'messages': [{phone, message}]}
    # 5. APENAS LOGA - NÃO ENVIA DE FATO!
    # 6. Marca como 'finished'
```

**Estados de Campanha:**
- `state_sms`: draft → process → finished
- `state_update_info`: draft → process → updated

**Campanhas Reais:**
```
ID 114: "teste 2025" - finished
ID 111: "Nova Margem" - finished - "Oí, |NOME| teste de envío |VI_RM|"
ID 110: "Campanha Milionária" - draft
```

---

## 🎯 Casos de Uso - SempreReal

### Caso 1: Envio de Campanhas Massivas (CORE)

**Fluxo Atual (Não Funcional):**
```
1. Admin cria campanha em contacts_realcred_batch
2. Seleciona aposentados/pensionistas
3. Define mensagem template com variáveis
4. Clica "Enviar Campanha"
5. Sistema marca como 'process'
6. Cron executa check_data_kolmeya_send()
7. ❌ Apenas loga, não envia de fato
```

**Fluxo Desejado (NOVO):**
```
1. Admin cria campanha em contacts_realcred_batch ✅
2. Seleciona aposentados/pensionistas ✅
3. Define mensagem template com variáveis ✅
4. Clica "Enviar Campanha" ✅
5. Sistema marca como 'process' ✅
6. Cron executa check_data_kolmeya_send() ✅
7. 🆕 ENVIA VIA KOLMEYA API
   └── POST /v1/sms/store com até 1000 msgs/batch
8. 🆕 SALVA job_id e request_id
9. 🆕 Webhook recebe status de entrega
10. 🆕 Marca mensagens como enviada/entregue/erro
```

### Caso 2: Respostas de Campanhas (CRÍTICO)

**Problema Atual:**
- Kolmeya envia campanhas massivas
- Pessoas respondem com "SIM", "INTERESSADO", "QUERO"
- ❌ Respostas ficam PERDIDAS no Kolmeya
- ❌ Vendedores NÃO SÃO ALERTADOS

**Solução Nova:**
```
1. 🆕 Webhook Kolmeya → Odoo (/kolmeya/webhook/reply)
2. 🆕 Sistema identifica número que respondeu
3. 🆕 Busca contact em contacts_realcred_batch
4. 🆕 Cria/atualiza res.partner se não existir
5. 🆕 Cria CRM Lead automaticamente com:
   - Nome do aposentado
   - Telefone que respondeu
   - Mensagem recebida
   - Dados de margem disponível
   - Tag: "Respondeu SMS"
6. 🆕 ALERTA IMEDIATO ao vendedor via:
   - Notificação Odoo (chatter)
   - Email (opcional)
   - Dashboard de leads quentes
7. 🆕 Vendedor pode RESPONDER direto do CRM
   └── Envia SMS via Kolmeya
```

### Caso 3: Envio Individual (res.partner, CRM, Sales)

**Necessidade:**
Vendedoras podem enviar mensagens pré-definidas desde:
- `res.partner` (contatos)
- `crm.lead` (oportunidades)
- `sale.order` (pedidos)

**Solução:**
```python
# Botão "Enviar SMS" em res.partner
def action_send_sms_template(self):
    # 1. Abre wizard com templates pré-definidos
    # 2. Admin já criou templates com variáveis
    # 3. Vendedor seleciona template
    # 4. Preview com dados preenchidos
    # 5. Confirma envio
    # 6. Envia via Kolmeya
    # 7. Salva histórico no chatter
```

---

## 🔧 Implementação Técnica

### Fase 1: Integração Base Kolmeya (2-3 dias)

#### 1.1. Novo Modelo: `kolmeya.sms.message`

**Objetivo:** Rastrear TODAS as mensagens enviadas/recebidas

```python
class KolmeyaSmsMessage(models.Model):
    _name = 'kolmeya.sms.message'
    _description = 'Kolmeya SMS Message Tracking'
    _order = 'create_date desc'

    # Identificação
    name = fields.Char('Reference', required=True)
    kolmeya_job_id = fields.Char('Kolmeya Job ID')
    kolmeya_request_id = fields.Char('Kolmeya Request ID')
    kolmeya_message_id = fields.Char('Kolmeya Message ID')

    # Direção
    direction = fields.Selection([
        ('outbound', 'Enviado'),
        ('inbound', 'Recebido')
    ], default='outbound', required=True)

    # Dados da mensagem
    phone = fields.Char('Telefone', required=True)
    message = fields.Text('Mensagem', required=True)

    # Status (Kolmeya codes)
    status = fields.Selection([
        ('1', 'Tentando enviar'),
        ('2', 'Enviado'),
        ('3', 'Entregue'),
        ('4', 'Não entregue'),
        ('5', 'Rejeitado'),
        ('6', 'Expirado'),
    ], string='Status Kolmeya')

    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('queued', 'Na fila'),
        ('sending', 'Enviando'),
        ('sent', 'Enviado'),
        ('delivered', 'Entregue'),
        ('failed', 'Falha'),
        ('received', 'Recebido'),
    ], default='draft')

    # Vínculos
    campaign_id = fields.Many2one('contacts.realcred.campaign', 'Campanha')
    contact_id = fields.Many2one('contacts.realcred.batch', 'Aposentado')
    partner_id = fields.Many2one('res.partner', 'Parceiro')
    lead_id = fields.Many2one('crm.lead', 'Lead')
    sale_id = fields.Many2one('sale.order', 'Pedido')

    # Resposta (para respostas)
    parent_id = fields.Many2one('kolmeya.sms.message', 'Mensagem Original')
    reply_ids = fields.One2many('kolmeya.sms.message', 'parent_id', 'Respostas')

    # Metadados
    error_message = fields.Text('Erro')
    sent_date = fields.Datetime('Data de Envio')
    delivered_date = fields.Datetime('Data de Entrega')
```

#### 1.2. Novo Modelo: `kolmeya.sms.template`

**Objetivo:** Templates pré-definidos pelo admin

```python
class KolmeyaSmsTemplate(models.Model):
    _name = 'kolmeya.sms.template'
    _description = 'Kolmeya SMS Templates'

    name = fields.Char('Nome do Template', required=True)
    code = fields.Char('Código Único', required=True)

    # Contexto de uso
    model_id = fields.Many2one('ir.model', 'Modelo Aplicável')
    applies_to = fields.Selection([
        ('contacts_realcred', 'Aposentados/Pensionistas'),
        ('res_partner', 'Contatos Gerais'),
        ('crm_lead', 'Leads/Oportunidades'),
        ('sale_order', 'Pedidos de Venda'),
        ('all', 'Todos'),
    ], default='all', string='Aplica-se a')

    # Template
    message_template = fields.Text('Template da Mensagem', required=True,
        help="Use variáveis: {name}, {cpf}, {vi_rmi}, {phone}, etc.")

    # Variáveis disponíveis (info)
    available_variables = fields.Text('Variáveis Disponíveis',
        compute='_compute_available_variables',
        help="Lista de variáveis que podem ser usadas neste template")

    # Configurações
    active = fields.Boolean('Ativo', default=True)
    require_approval = fields.Boolean('Requer Aprovação Admin', default=False)

    # Exemplos
    preview_example = fields.Text('Exemplo de Mensagem',
        compute='_compute_preview')

    def _compute_available_variables(self):
        for record in self:
            if record.applies_to == 'contacts_realcred':
                record.available_variables = """
{name} - Nome
{cpf} - CPF
{phone} - Telefone
{vi_rmi} - Valor RMI
{margem} - Margem Disponível
{especie} - Espécie do Benefício
                """
            elif record.applies_to == 'res_partner':
                record.available_variables = """
{name} - Nome
{phone} - Telefone
{email} - Email
{city} - Cidade
                """
            # ... outros contextos

    @api.depends('message_template', 'applies_to')
    def _compute_preview(self):
        for record in self:
            # Gera exemplo com dados fictícios
            example_data = {
                'name': 'João da Silva',
                'cpf': '123.456.789-00',
                'vi_rmi': 'R$ 2.500,00',
                'phone': '(11) 99999-9999',
            }
            try:
                record.preview_example = record.message_template.format(**example_data)
            except:
                record.preview_example = 'Template inválido'
```

#### 1.3. Modificar `contacts.realcred.campaign`

```python
class ContactsRealcredCampaign(models.Model):
    _inherit = 'contacts.realcred.campaign'

    # NOVO: Template
    sms_template_id = fields.Many2one('kolmeya.sms.template',
        'Template SMS',
        domain="[('applies_to', 'in', ['contacts_realcred', 'all'])]")

    # NOVO: Tracking
    kolmeya_job_id = fields.Char('Kolmeya Job ID')
    total_messages = fields.Integer('Total Mensagens', compute='_compute_stats')
    sent_messages = fields.Integer('Enviadas', compute='_compute_stats')
    delivered_messages = fields.Integer('Entregues', compute='_compute_stats')
    failed_messages = fields.Integer('Falhas', compute='_compute_stats')
    replied_messages = fields.Integer('Respostas', compute='_compute_stats')

    # NOVO: Mensagens
    message_ids = fields.One2many('kolmeya.sms.message', 'campaign_id',
        'Mensagens SMS')

    def _compute_stats(self):
        for rec in self:
            rec.total_messages = len(rec.message_ids)
            rec.sent_messages = len(rec.message_ids.filtered(lambda m: m.state in ['sent', 'delivered']))
            rec.delivered_messages = len(rec.message_ids.filtered(lambda m: m.state == 'delivered'))
            rec.failed_messages = len(rec.message_ids.filtered(lambda m: m.state == 'failed'))
            rec.replied_messages = len(rec.message_ids.filtered(lambda m: m.reply_ids))

    def check_data_kolmeya_send(self):
        """NOVO: Integração real com Kolmeya"""
        import requests

        KOLMEYA_API_URL = "https://kolmeya.com.br/api/v1/sms/store"
        KOLMEYA_TOKEN = "Bearer 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY"

        campaigns = self.env['contacts.realcred.campaign'].search([
            ('state_sms', '=', 'process')
        ])

        for campaign in campaigns:
            # Validações
            if not campaign.message and not campaign.sms_template_id:
                _logger.error(f"Campanha {campaign.id} sem mensagem ou template")
                continue

            # Preparar mensagens em batches de 1000
            all_messages = []
            sms_records = []

            for contact in campaign.contacts_realcred_campaign_ids:
                # Validação
                if not (contact.telefone1 and contact.updated_limit and not contact.falecido):
                    continue

                # Preparar dados para template
                template_data = {
                    'name': contact.name or '',
                    'cpf': contact.cpf or '',
                    'vi_rmi': f"R$ {contact.vi_rmi:,.2f}" if contact.vi_rmi else '',
                    'phone': contact.telefone1 or '',
                    'margem': contact.margemDisponivel or '',
                    'especie': contact.especie or '',
                }

                # Renderizar mensagem
                if campaign.sms_template_id:
                    message_text = campaign.sms_template_id.message_template.format(**template_data)
                else:
                    # Método antigo (compatibilidade)
                    message_text = campaign.message
                    message_text = message_text.replace('|NOME|', template_data['name'])
                    message_text = message_text.replace('|CPF|', template_data['cpf'])
                    message_text = message_text.replace('|VI_RM|', template_data['vi_rmi'])

                # Criar registro de tracking
                sms_record = self.env['kolmeya.sms.message'].create({
                    'name': f"{campaign.name_campaign} - {contact.name}",
                    'campaign_id': campaign.id,
                    'contact_id': contact.id,
                    'partner_id': contact.cpf_id.id if contact.cpf_id else False,
                    'phone': contact.telefone1,
                    'message': message_text,
                    'direction': 'outbound',
                    'state': 'queued',
                })
                sms_records.append(sms_record)

                all_messages.append({
                    'to': contact.telefone1.strip(),
                    'message': message_text.strip(),
                    'reference_id': str(sms_record.id),  # Para rastrear no webhook
                })

            # Enviar em batches de 1000
            batch_size = 1000
            for i in range(0, len(all_messages), batch_size):
                batch = all_messages[i:i+batch_size]

                payload = {
                    'messages': batch,
                    'segment_id': 1,  # Centro de custo padrão
                }

                headers = {
                    'Authorization': KOLMEYA_TOKEN,
                    'Content-Type': 'application/json',
                }

                try:
                    response = requests.post(
                        KOLMEYA_API_URL,
                        json=payload,
                        headers=headers,
                        timeout=30
                    )
                    response.raise_for_status()

                    result = response.json()
                    job_id = result.get('job_id')
                    request_id = result.get('request_id')

                    # Atualizar registros do batch
                    batch_records = sms_records[i:i+batch_size]
                    for sms in batch_records:
                        sms.write({
                            'kolmeya_job_id': job_id,
                            'kolmeya_request_id': request_id,
                            'state': 'sending',
                            'sent_date': fields.Datetime.now(),
                        })

                    # Salvar job_id na campanha
                    if not campaign.kolmeya_job_id:
                        campaign.kolmeya_job_id = job_id

                    _logger.info(f"Batch {i//batch_size + 1} enviado: {len(batch)} mensagens - Job ID: {job_id}")

                except requests.exceptions.RequestException as e:
                    _logger.error(f"Erro ao enviar batch {i//batch_size + 1}: {str(e)}")

                    # Marcar mensagens como falha
                    batch_records = sms_records[i:i+batch_size]
                    for sms in batch_records:
                        sms.write({
                            'state': 'failed',
                            'error_message': str(e),
                        })

            # Marcar campanha como finalizada
            campaign.state_sms = 'finished'
            _logger.info(f"Campanha {campaign.name_campaign} finalizada: {len(all_messages)} mensagens enviadas")
```

#### 1.4. Webhook para Receber Status

```python
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class KolmeyaWebhookController(http.Controller):

    @http.route('/kolmeya/webhook/status', type='json', auth='public', csrf=False, methods=['POST'])
    def kolmeya_status_webhook(self, **kwargs):
        """
        Recebe atualizações de status do Kolmeya

        Payload esperado:
        {
            "reference_id": "123",  # ID do kolmeya.sms.message
            "status": "3",  # 1-6 (ver doc Kolmeya)
            "error_code": "...",
            "delivered_at": "2025-11-15 18:00:00"
        }
        """
        data = request.jsonrequest

        try:
            reference_id = data.get('reference_id')
            status = data.get('status')
            error_code = data.get('error_code')
            delivered_at = data.get('delivered_at')

            # Mapear status Kolmeya → Odoo
            status_map = {
                '1': 'sending',     # Tentando enviar
                '2': 'sent',        # Enviado
                '3': 'delivered',   # Entregue
                '4': 'failed',      # Não entregue
                '5': 'failed',      # Rejeitado
                '6': 'failed',      # Expirado
            }

            # Buscar mensagem
            sms = request.env['kolmeya.sms.message'].sudo().search([
                ('id', '=', int(reference_id))
            ], limit=1)

            if sms:
                update_vals = {
                    'status': str(status),
                    'state': status_map.get(str(status), 'failed'),
                }

                if delivered_at:
                    update_vals['delivered_date'] = delivered_at

                if error_code:
                    update_vals['error_message'] = error_code

                sms.write(update_vals)

                _logger.info(f"Status atualizado para SMS {reference_id}: {status}")

                return {'success': True, 'message': 'Status updated'}
            else:
                _logger.warning(f"SMS {reference_id} não encontrado")
                return {'success': False, 'error': 'SMS not found'}

        except Exception as e:
            _logger.error(f"Erro no webhook de status: {str(e)}")
            return {'success': False, 'error': str(e)}
```

---

### Fase 2: Respostas Bidirecionais (3-4 dias)

#### 2.1. Webhook para Receber Respostas

```python
@http.route('/kolmeya/webhook/reply', type='json', auth='public', csrf=False, methods=['POST'])
def kolmeya_reply_webhook(self, **kwargs):
    """
    Recebe respostas de SMS enviadas

    Payload esperado:
    {
        "phone": "11999999999",
        "message": "SIM QUERO",
        "received_at": "2025-11-15 18:30:00",
        "original_message_id": "123"  # Se disponível
    }
    """
    data = request.jsonrequest

    try:
        phone = data.get('phone')
        message_text = data.get('message')
        received_at = data.get('received_at')
        original_id = data.get('original_message_id')

        # 1. Criar registro da resposta
        reply_sms = request.env['kolmeya.sms.message'].sudo().create({
            'name': f"Resposta de {phone}",
            'direction': 'inbound',
            'phone': phone,
            'message': message_text,
            'state': 'received',
            'create_date': received_at or fields.Datetime.now(),
        })

        # 2. Vincular à mensagem original (se disponível)
        if original_id:
            original_sms = request.env['kolmeya.sms.message'].sudo().search([
                ('id', '=', int(original_id))
            ], limit=1)

            if original_sms:
                reply_sms.parent_id = original_sms.id
                reply_sms.campaign_id = original_sms.campaign_id.id
                reply_sms.contact_id = original_sms.contact_id.id

        # 3. Buscar contato por telefone
        contact = None

        # 3a. Buscar em contacts_realcred_batch
        contact = request.env['contacts.realcred.batch'].sudo().search([
            ('telefone1', '=', phone)
        ], limit=1)

        if contact:
            reply_sms.contact_id = contact.id
            if contact.cpf_id:
                reply_sms.partner_id = contact.cpf_id.id

        # 3b. Se não encontrou, buscar em res.partner
        if not reply_sms.partner_id:
            partner = request.env['res.partner'].sudo().search([
                '|',
                ('phone', '=', phone),
                ('mobile', '=', phone)
            ], limit=1)

            if partner:
                reply_sms.partner_id = partner.id

        # 4. CRIAR LEAD AUTOMATICAMENTE
        lead_data = {
            'name': f'Resposta SMS: {phone}',
            'type': 'opportunity',
            'phone': phone,
            'description': f"Resposta recebida: {message_text}",
            'tag_ids': [(4, request.env.ref('kolmeya_sms.tag_sms_reply').id)],
            'priority': '2',  # Alta prioridade
        }

        # Adicionar dados do contato se encontrado
        if contact:
            lead_data.update({
                'name': f'Resposta SMS: {contact.name}',
                'partner_id': contact.cpf_id.id if contact.cpf_id else False,
                'description': f"""
Resposta recebida: {message_text}

Dados do Aposentado:
- CPF: {contact.cpf}
- Nome: {contact.name}
- Benefício (NB): {contact.nb}
- Espécie: {contact.especie}
- RMI: R$ {contact.vi_rmi:,.2f}
- Margem Disponível: {contact.margemDisponivel}
- Telefone: {contact.telefone1}
                """,
            })

        # Criar Lead
        lead = request.env['crm.lead'].sudo().create(lead_data)
        reply_sms.lead_id = lead.id

        # 5. NOTIFICAR VENDEDOR
        # 5a. Determinar vendedor responsável
        sales_team = request.env['crm.team'].sudo().search([
            ('name', '=', 'SMS Responses')
        ], limit=1)

        if not sales_team:
            sales_team = request.env['crm.team'].sudo().search([], limit=1)

        if sales_team and sales_team.user_id:
            assignee = sales_team.user_id
        else:
            # Vendedor padrão ou admin
            assignee = request.env.ref('base.user_admin')

        lead.user_id = assignee.id

        # 5b. Enviar notificação via chatter
        lead.message_post(
            body=f"""
            <p><strong>🔔 Nova Resposta de SMS!</strong></p>
            <p>Telefone: <strong>{phone}</strong></p>
            <p>Mensagem: <em>"{message_text}"</em></p>
            <p>Recebido em: {received_at}</p>
            <p><strong>AÇÃO REQUERIDA: Entre em contato imediatamente!</strong></p>
            """,
            subject='Nova Resposta SMS - Ação Imediata',
            message_type='notification',
            partner_ids=[assignee.partner_id.id],
        )

        # 5c. Enviar email de alerta (opcional)
        template = request.env.ref('kolmeya_sms.email_template_sms_reply_alert', raise_if_not_found=False)
        if template:
            template.send_mail(lead.id, force_send=True)

        _logger.info(f"Resposta processada: {phone} → Lead {lead.id}")

        return {
            'success': True,
            'lead_id': lead.id,
            'message': 'Reply processed and lead created'
        }

    except Exception as e:
        _logger.error(f"Erro no webhook de resposta: {str(e)}")
        return {'success': False, 'error': str(e)}
```

#### 2.2. Dashboard de Respostas

```python
class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # NOVO: Vínculos SMS
    sms_message_ids = fields.One2many('kolmeya.sms.message', 'lead_id',
        'Mensagens SMS')
    sms_replied = fields.Boolean('Respondeu SMS',
        compute='_compute_sms_replied', store=True)
    last_sms_reply = fields.Text('Última Resposta SMS',
        compute='_compute_sms_replied', store=True)

    @api.depends('sms_message_ids')
    def _compute_sms_replied(self):
        for lead in self:
            inbound_messages = lead.sms_message_ids.filtered(
                lambda m: m.direction == 'inbound'
            )
            lead.sms_replied = bool(inbound_messages)
            lead.last_sms_reply = inbound_messages[0].message if inbound_messages else False

    def action_send_sms_reply(self):
        """Botão para vendedor responder SMS"""
        return {
            'name': 'Enviar SMS',
            'type': 'ir.actions.act_window',
            'res_model': 'kolmeya.sms.composer',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lead_id': self.id,
                'default_phone': self.phone or self.mobile,
                'default_partner_id': self.partner_id.id,
            }
        }
```

---

### Fase 3: Envio Individual e Templates (2 dias)

#### 3.1. Wizard de Composição SMS

```python
class KolmeyaSmsComposer(models.TransientModel):
    _name = 'kolmeya.sms.composer'
    _description = 'SMS Composer Wizard'

    # Contexto
    lead_id = fields.Many2one('crm.lead', 'Lead')
    partner_id = fields.Many2one('res.partner', 'Parceiro')
    sale_id = fields.Many2one('sale.order', 'Pedido')
    contact_id = fields.Many2one('contacts.realcred.batch', 'Aposentado')

    # Destinatário
    phone = fields.Char('Telefone', required=True)
    recipient_name = fields.Char('Nome', compute='_compute_recipient')

    # Mensagem
    template_id = fields.Many2one('kolmeya.sms.template', 'Template',
        domain="[('active', '=', True)]")
    message = fields.Text('Mensagem', required=True)

    # Preview
    preview = fields.Text('Preview', compute='_compute_preview')
    char_count = fields.Integer('Caracteres', compute='_compute_preview')

    @api.depends('partner_id', 'lead_id', 'sale_id', 'contact_id')
    def _compute_recipient(self):
        for rec in self:
            if rec.partner_id:
                rec.recipient_name = rec.partner_id.name
            elif rec.lead_id:
                rec.recipient_name = rec.lead_id.partner_name or rec.lead_id.name
            elif rec.contact_id:
                rec.recipient_name = rec.contact_id.name
            elif rec.sale_id:
                rec.recipient_name = rec.sale_id.partner_id.name
            else:
                rec.recipient_name = ''

    @api.onchange('template_id')
    def _onchange_template(self):
        if self.template_id:
            # Preparar dados para template
            data = self._get_template_data()
            try:
                self.message = self.template_id.message_template.format(**data)
            except KeyError as e:
                raise UserError(f"Template inválido: variável {e} não encontrada")

    def _get_template_data(self):
        """Obter dados do contexto para preencher template"""
        data = {}

        if self.partner_id:
            data.update({
                'name': self.partner_id.name or '',
                'phone': self.partner_id.phone or self.partner_id.mobile or '',
                'email': self.partner_id.email or '',
                'city': self.partner_id.city or '',
            })

        if self.contact_id:
            data.update({
                'name': self.contact_id.name or '',
                'cpf': self.contact_id.cpf or '',
                'vi_rmi': f"R$ {self.contact_id.vi_rmi:,.2f}" if self.contact_id.vi_rmi else '',
                'phone': self.contact_id.telefone1 or '',
                'margem': self.contact_id.margemDisponivel or '',
                'especie': self.contact_id.especie or '',
            })

        if self.lead_id:
            data.update({
                'name': self.lead_id.partner_name or self.lead_id.name or '',
                'phone': self.lead_id.phone or self.lead_id.mobile or '',
                'expected_revenue': f"R$ {self.lead_id.expected_revenue:,.2f}" if self.lead_id.expected_revenue else '',
            })

        if self.sale_id:
            data.update({
                'name': self.sale_id.partner_id.name or '',
                'order_number': self.sale_id.name or '',
                'amount_total': f"R$ {self.sale_id.amount_total:,.2f}",
            })

        return data

    @api.depends('message')
    def _compute_preview(self):
        for rec in self:
            rec.preview = rec.message
            rec.char_count = len(rec.message) if rec.message else 0

    def action_send_sms(self):
        """Enviar SMS via Kolmeya"""
        self.ensure_one()

        if not self.phone or not self.message:
            raise UserError("Telefone e mensagem são obrigatórios!")

        # Criar registro de tracking
        sms = self.env['kolmeya.sms.message'].create({
            'name': f"SMS para {self.recipient_name or self.phone}",
            'phone': self.phone,
            'message': self.message,
            'direction': 'outbound',
            'state': 'queued',
            'partner_id': self.partner_id.id if self.partner_id else False,
            'lead_id': self.lead_id.id if self.lead_id else False,
            'sale_id': self.sale_id.id if self.sale_id else False,
            'contact_id': self.contact_id.id if self.contact_id else False,
        })

        # Enviar via Kolmeya
        result = sms.action_send()

        if result.get('success'):
            # Registrar no chatter do objeto de origem
            if self.lead_id:
                self.lead_id.message_post(
                    body=f"📱 SMS enviado para {self.phone}: {self.message}",
                    subject='SMS Enviado'
                )
            elif self.partner_id:
                self.partner_id.message_post(
                    body=f"📱 SMS enviado: {self.message}",
                    subject='SMS Enviado'
                )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'SMS Enviado!',
                    'message': f'Mensagem enviada para {self.phone}',
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            raise UserError(f"Erro ao enviar SMS: {result.get('error')}")
```

#### 3.2. Método de Envio Individual

```python
class KolmeyaSmsMessage(models.Model):
    _name = 'kolmeya.sms.message'

    def action_send(self):
        """Enviar mensagem individual via Kolmeya"""
        self.ensure_one()

        import requests

        KOLMEYA_API_URL = "https://kolmeya.com.br/api/v1/sms/store"
        KOLMEYA_TOKEN = "Bearer 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY"

        payload = {
            'messages': [{
                'to': self.phone,
                'message': self.message,
                'reference_id': str(self.id),
            }],
            'segment_id': 1,
        }

        headers = {
            'Authorization': KOLMEYA_TOKEN,
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(
                KOLMEYA_API_URL,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()

            self.write({
                'kolmeya_job_id': result.get('job_id'),
                'kolmeya_request_id': result.get('request_id'),
                'state': 'sending',
                'sent_date': fields.Datetime.now(),
            })

            return {'success': True, 'job_id': result.get('job_id')}

        except requests.exceptions.RequestException as e:
            self.write({
                'state': 'failed',
                'error_message': str(e),
            })

            return {'success': False, 'error': str(e)}
```

---

## 📋 Checklist de Implementação

### Preparação
- [ ] Whitelist IP do servidor odoo-rc na plataforma Kolmeya
- [ ] Testar token Kolmeya via cURL
- [ ] Criar backup do módulo `contacts_realcred` atual
- [ ] Backup do database

### Desenvolvimento
- [ ] Criar módulo `kolmeya_sms` em `/odoo/custom/addons_custom/`
- [ ] Implementar modelos:
  - [ ] `kolmeya.sms.message`
  - [ ] `kolmeya.sms.template`
  - [ ] `kolmeya.sms.composer` (wizard)
- [ ] Herdar `contacts.realcred.campaign`
- [ ] Herdar `crm.lead`
- [ ] Herdar `res.partner`
- [ ] Herdar `sale.order`
- [ ] Implementar controllers (webhooks)
- [ ] Criar views e menus
- [ ] Criar templates de SMS padrão (data)
- [ ] Criar email template para alertas

### Testes
- [ ] Teste envio individual (1 SMS)
- [ ] Teste envio batch pequeno (100 SMS)
- [ ] Teste recebimento de status via webhook
- [ ] Teste recebimento de resposta via webhook
- [ ] Teste criação automática de Lead
- [ ] Teste notificação de vendedor
- [ ] Teste templates de mensagem
- [ ] Teste desde res.partner
- [ ] Teste desde crm.lead
- [ ] Teste desde sale.order

### Deploy
- [ ] Deploy em staging
- [ ] Testes com vendedores
- [ ] Ajustes de UX
- [ ] Deploy em produção
- [ ] Treinamento equipe
- [ ] Monitoramento 48h

---

## 🎨 Interface de Usuário

### Novos Menus

```
SMS Kolmeya
├── Dashboard
│   ├── Mensagens Enviadas (hoje, semana, mês)
│   ├── Taxa de Entrega
│   ├── Respostas Recebidas
│   └── Leads Gerados
├── Mensagens
│   ├── Todas as Mensagens
│   ├── Enviadas
│   ├── Recebidas (Respostas)
│   └── Falhadas
├── Templates
│   ├── Templates SMS
│   └── Criar Novo Template
└── Configurações
    ├── API Kolmeya
    └── Webhooks
```

### Botões Adicionados

**Em `res.partner`:**
- [Enviar SMS] → Abre wizard com templates

**Em `crm.lead`:**
- [Enviar SMS] → Abre wizard com templates
- [Responder SMS] → Se cliente respondeu SMS

**Em `sale.order`:**
- [Enviar SMS] → Ex: confirmação de pedido

**Em `contacts.realcred.campaign`:**
- [Selecionar Template] (novo)
- [Preview Mensagens] (novo)
- [Ver Estatísticas] (novo)

---

## 📊 Dashboards e Relatórios

### Dashboard SMS (Novo)

```python
class KolmeyaDashboard(models.Model):
    _name = 'kolmeya.dashboard'
    _description = 'Kolmeya SMS Dashboard'
    _auto = False

    # Campos agregados
    date = fields.Date('Data')
    campaign_id = fields.Many2one('contacts.realcred.campaign', 'Campanha')
    total_sent = fields.Integer('Enviadas')
    total_delivered = fields.Integer('Entregues')
    total_failed = fields.Integer('Falhas')
    total_replies = fields.Integer('Respostas')
    total_leads_created = fields.Integer('Leads Criados')
    delivery_rate = fields.Float('Taxa de Entrega %')
    reply_rate = fields.Float('Taxa de Resposta %')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'kolmeya_dashboard')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW kolmeya_dashboard AS (
                SELECT
                    ROW_NUMBER() OVER() as id,
                    DATE(create_date) as date,
                    campaign_id,
                    COUNT(*) as total_sent,
                    COUNT(*) FILTER (WHERE state = 'delivered') as total_delivered,
                    COUNT(*) FILTER (WHERE state = 'failed') as total_failed,
                    COUNT(DISTINCT reply_ids) as total_replies,
                    COUNT(DISTINCT lead_id) FILTER (WHERE lead_id IS NOT NULL) as total_leads_created,
                    ROUND(
                        (COUNT(*) FILTER (WHERE state = 'delivered')::float /
                         NULLIF(COUNT(*), 0) * 100), 2
                    ) as delivery_rate,
                    ROUND(
                        (COUNT(DISTINCT reply_ids)::float /
                         NULLIF(COUNT(*), 0) * 100), 2
                    ) as reply_rate
                FROM kolmeya_sms_message
                WHERE direction = 'outbound'
                GROUP BY DATE(create_date), campaign_id
            )
        """)
```

---

## 💰 Estimativa de Custos

### Desenvolvimento
```
Fase 1 (Integração Base):       16-24 horas
Fase 2 (Respostas):             24-32 horas
Fase 3 (Envio Individual):      16-24 horas
Testes e Ajustes:               16-24 horas
----------------------------------------------
TOTAL:                          72-104 horas
```

### Operacional
```
Volume estimado: 100K-500K SMS/mês
Custo Kolmeya: Consultar tabela de preços
ROI esperado: 3x-5x do custo de SMS (baseado em conversão de leads)
```

---

## 🚀 Próximos Passos Imediatos

1. **Hoje:**
   - [ ] Solicitar whitelist de IP na Kolmeya
   - [ ] Testar API com cURL

2. **Amanhã:**
   - [ ] Criar estrutura do módulo `kolmeya_sms`
   - [ ] Implementar modelos base
   - [ ] Modificar `check_data_kolmeya_send()`

3. **Esta Semana:**
   - [ ] Implementar webhook de status
   - [ ] Implementar webhook de respostas
   - [ ] Testes em staging

4. **Próxima Semana:**
   - [ ] Deploy em produção
   - [ ] Treinamento vendedores
   - [ ] Primeira campanha real

---

**Status:** ✅ Plano Completo - Pronto para Implementação
**Próxima Ação:** Whitelist de IP + Começar Fase 1
