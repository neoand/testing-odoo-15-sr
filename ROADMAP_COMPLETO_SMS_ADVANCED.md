# ROADMAP COMPLETO - SMS ADVANCED MODULE

**Data Criação:** 16/11/2025
**Última Atualização:** 16/11/2025
**Versão Atual:** 15.0.2.0.0
**Versão Alvo:** 15.0.3.0.0

---

## ÍNDICE

1. [Status Atual](#status-atual)
2. [Fase 1: Fundação (Concluída)](#fase-1-fundação-concluída)
3. [Fase 2: Checkbox SMS no Chatter (Próxima)](#fase-2-checkbox-sms-no-chatter-próxima)
4. [Fase 3: Melhorias Incrementais](#fase-3-melhorias-incrementais)
5. [Fase 4: Features Avançadas](#fase-4-features-avançadas)
6. [Fase 5: Enterprise Features](#fase-5-enterprise-features)
7. [Comandos Úteis](#comandos-úteis)
8. [Checklist de Deploy](#checklist-de-deploy)

---

## STATUS ATUAL

### Módulo Base: chatroom_sms_advanced v15.0.2.0.0

**Estado:** ✅ INSTALADO E FUNCIONANDO

**Componentes Implementados:**
- ✅ Herança de `sms.message` com campos avançados
- ✅ Herança de `sms.provider` com configurações extras
- ✅ Modelo `sms.scheduled` (agendamento)
- ✅ Modelo `sms.campaign` (campanhas)
- ✅ Modelo `sms.blacklist` (lista negra)
- ✅ Modelo `sms.dashboard` (analytics SQL view)
- ✅ Wizard `sms.bulk.send` (envio em massa)
- ✅ Views XML (form, tree, kanban, graph)
- ✅ Security groups e permissões
- ✅ Cron jobs (agendamento, sync)
- ✅ Menus configurados
- ✅ Ícone profissional (141x141 PNG)

**Pendente:**
- ⏳ Checkbox SMS no chatter
- ⏳ Templates SMS específicos
- ⏳ Link tracking
- ⏳ Shortlinks automáticos
- ⏳ Relatórios avançados
- ⏳ Integração WhatsApp

---

## FASE 1: FUNDAÇÃO (CONCLUÍDA)

### DIA 1-2: Setup e Estrutura Base ✅

**Objetivos:**
- [x] Análise dos módulos existentes (sms_base_sr, sms_kolmeya)
- [x] Criação da estrutura do módulo chatroom_sms_advanced
- [x] Configuração de dependências corretas
- [x] Definição de modelos usando _inherit

**Entregas:**
- [x] `__manifest__.py` configurado
- [x] Estrutura de diretórios criada
- [x] Security groups definidos
- [x] Documentação: ANALISE_ESTRUTURA_SMS_EXISTENTE.md

### DIA 3-4: Modelos Core ✅

**Objetivos:**
- [x] Implementar `sms_message_advanced.py` (_inherit sms.message)
- [x] Implementar `sms_provider_advanced.py` (_inherit sms.provider)
- [x] Criar modelos novos (scheduled, campaign, blacklist)
- [x] Criar SQL View dashboard

**Entregas:**
- [x] 6 arquivos Python de modelos
- [x] Campos computados e métodos
- [x] Constraints e validações
- [x] XML views básicas

### DIA 5-6: Views e UI ✅

**Objetivos:**
- [x] Criar todas as views XML (form, tree, search)
- [x] Implementar kanban para campanhas
- [x] Implementar graphs para dashboard
- [x] Adicionar filtros e agrupamentos

**Entregas:**
- [x] 7 arquivos XML de views
- [x] Menus estruturados
- [x] Actions configuradas
- [x] Ícone do módulo (PNG 141x141)

### DIA 7-8: Wizards e Automação ✅

**Objetivos:**
- [x] Wizard de envio em massa
- [x] Cron job para SMS agendados
- [x] Cron job para sync blacklist
- [x] Templates de campanhas

**Entregas:**
- [x] `sms_bulk_send.py` wizard
- [x] 3 arquivos XML de cron
- [x] Templates de campanha (data/)

### DIA 9-10: Instalação e Testes ✅

**Objetivos:**
- [x] Instalação no servidor
- [x] Correção de 6 erros encontrados
- [x] Configuração de permissões
- [x] Testes de funcionalidades

**Entregas:**
- [x] Módulo instalado (state=installed)
- [x] Todas as views funcionando
- [x] Logs sem erros
- [x] Documentação: INSTALACAO_COMPLETA_SMS_ADVANCED.md

### DIA 11: Ícone e Acessibilidade ✅

**Objetivos:**
- [x] Criar ícone profissional para o módulo
- [x] Configurar web_icon em menus.xml
- [x] Testar visibilidade no app switcher
- [x] Documentar processo de criação de ícone

**Entregas:**
- [x] icon.png (141x141 pixels, 7.0 KB)
- [x] web_icon configurado
- [x] Documentação: ICONE_SMS_FINAL_PROFISSIONAL.md

**Status Fase 1:** ✅ 100% COMPLETA

---

## FASE 2: CHECKBOX SMS NO CHATTER (PRÓXIMA)

**Prioridade:** 🔥 ALTA
**Estimativa:** 8-12 horas (2-3 dias)
**Versão Alvo:** 15.0.2.1.0

### DIA 12-13: Pesquisa e Planejamento ✅

**Objetivos:**
- [x] Pesquisar estrutura do `mail.compose.message`
- [x] Pesquisar integração SMS via `sms.composer`
- [x] Analisar método `_message_sms()`
- [x] Documentar viabilidade e implementação

**Entregas:**
- [x] Documentação completa: PESQUISA_CHATTER_SMS_CHECKBOX.md (1.100+ linhas)
- [x] Código de implementação completo
- [x] Casos de uso detalhados
- [x] Alternativas consideradas

**Status:** ✅ CONCLUÍDO

### DIA 14: Implementação do Modelo Python ⏳

**Objetivos:**
- [ ] Criar `wizard/mail_compose_sms.py`
- [ ] Implementar campo `send_sms` (Boolean)
- [ ] Adicionar campos computados (sms_recipients_count, sms_partner_numbers)
- [ ] Override do método `action_send_mail()`
- [ ] Implementar `_send_sms_to_recipients()`
- [ ] Implementar `_prepare_sms_body()` (HTML → texto)
- [ ] Implementar `_send_sms_via_message_sms()`
- [ ] Implementar `_send_sms_direct()`

**Entregas:**
```python
chatroom_sms_advanced/
└── wizard/
    ├── __init__.py (atualizar)
    └── mail_compose_sms.py (NOVO - ~400 linhas)
```

**Código:**
```python
class MailComposerSMS(models.TransientModel):
    _inherit = 'mail.compose.message'

    send_sms = fields.Boolean('Also send as SMS', default=False)
    sms_recipients_count = fields.Integer(compute='_compute_sms_recipients_count')
    sms_partner_numbers = fields.Text(compute='_compute_sms_partner_numbers')

    def action_send_mail(self):
        result = super().action_send_mail()
        if self.send_sms:
            self._send_sms_to_recipients()
        return result
```

**Validações a Implementar:**
- ✓ Verificar destinatários com número válido
- ✓ Bloquear se nenhum destinatário tem número
- ✓ Avisar se mensagem > 160 caracteres
- ✓ Verificar blacklist antes de enviar
- ✓ Remover HTML do corpo da mensagem

**Testes Unitários:**
```bash
# Testar imports
python3 -c "from odoo.addons.chatroom_sms_advanced.wizard.mail_compose_sms import MailComposerSMS"

# Testar conversão HTML → texto
# Testar validação de números
# Testar envio combinado (email + SMS)
```

### DIA 15: Implementação da View XML ⏳

**Objetivos:**
- [ ] Criar `wizard/mail_compose_sms_views.xml`
- [ ] Herdar view `email_compose_message_wizard_form`
- [ ] Adicionar checkbox "Also send as SMS"
- [ ] Adicionar grupo "SMS Options"
- [ ] Adicionar contador de destinatários
- [ ] Adicionar warnings (sem número, tamanho)
- [ ] Adicionar lista de números (debug)

**Entregas:**
```xml
chatroom_sms_advanced/
└── wizard/
    └── mail_compose_sms_views.xml (NOVO)
```

**XML Structure:**
```xml
<record id="email_compose_message_wizard_form_sms" model="ir.ui.view">
    <field name="inherit_id" ref="mail.email_compose_message_wizard_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='body']" position="after">
            <group name="sms_options" string="SMS Options">
                <field name="send_sms" widget="boolean_toggle"/>
                <!-- Info recipients count -->
                <!-- Warning no recipients -->
                <!-- Debug phone list -->
            </group>
        </xpath>
    </field>
</record>
```

**Elementos UI:**
- ✓ Checkbox toggle moderno
- ✓ Alert info (quantos destinatários)
- ✓ Alert warning (sem números válidos)
- ✓ Lista de números (somente admin)
- ✓ Visibilidade condicional (attrs)

### DIA 16: Integração e Testes ⏳

**Objetivos:**
- [ ] Atualizar `__manifest__.py` (adicionar dependências mail, sms)
- [ ] Atualizar `wizard/__init__.py` (import mail_compose_sms)
- [ ] Atualizar `security/ir.model.access.csv` (permissões)
- [ ] Incrementar versão para 15.0.2.1.0
- [ ] Testar instalação/atualização do módulo
- [ ] Testar funcionalidade completa

**Entregas:**
```python
# __manifest__.py
'version': '15.0.2.1.0',
'depends': [
    'mail',  # NOVO
    'sms',   # NOVO
    'sms_base_sr',
    'sms_kolmeya',
    'contact_center_sms',
],
'data': [
    # ...
    'wizard/mail_compose_sms_views.xml',  # NOVO
],
```

**Testes de Integração:**

1. **Teste 1: Envio Simples**
```python
# Via shell Odoo
partner = env['res.partner'].create({
    'name': 'João Teste',
    'email': 'joao@teste.com',
    'mobile': '+5511987654321',
})

composer = env['mail.compose.message'].create({
    'model': 'res.partner',
    'res_id': partner.id,
    'subject': 'Teste',
    'body': '<p>Mensagem de teste</p>',
    'partner_ids': [(6, 0, [partner.id])],
    'send_sms': True,
})

composer.action_send_mail()

# Verificar: email enviado + SMS enviado
```

2. **Teste 2: Múltiplos Destinatários**
```python
# 3 partners: 2 com número, 1 sem
# Resultado esperado: 2 SMS enviados, 3 emails enviados
```

3. **Teste 3: Blacklist**
```python
# Partner em blacklist
# Resultado esperado: Email enviado, SMS bloqueado
```

4. **Teste 4: HTML → Texto**
```python
# Corpo com HTML complexo
# Resultado esperado: SMS com texto limpo
```

**Critérios de Aceitação:**
- ✓ Checkbox aparece no composer
- ✓ Contador mostra números válidos corretamente
- ✓ Email sempre enviado
- ✓ SMS enviado apenas se checkbox marcado
- ✓ Validações funcionam (sem número, blacklist)
- ✓ Chatter mostra ambas mensagens (email + SMS)
- ✓ Sem erros no log

### DIA 17: Documentação e Rollout ⏳

**Objetivos:**
- [ ] Criar guia de usuário (como usar checkbox)
- [ ] Criar guia de administrador (configuração)
- [ ] Atualizar ROADMAP com status
- [ ] Deploy em staging
- [ ] Testes com usuários reais
- [ ] Deploy em produção

**Entregas:**
- [ ] GUIA_USUARIO_CHECKBOX_SMS.md
- [ ] GUIA_ADMIN_CHECKBOX_SMS.md
- [ ] Screenshots da funcionalidade
- [ ] Vídeo tutorial (opcional)

**Deploy Staging:**
```bash
# 1. Backup
ssh odoo-rc "cd /odoo/custom/addons_custom && sudo cp -r chatroom_sms_advanced chatroom_sms_advanced.backup_$(date +%Y%m%d)"

# 2. Deploy código
scp -r chatroom_sms_advanced odoo-rc:/tmp/
ssh odoo-rc "sudo cp -r /tmp/chatroom_sms_advanced /odoo/custom/addons_custom/"

# 3. Atualizar módulo
ssh odoo-rc "cd /odoo/odoo-server && sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d realcred -u chatroom_sms_advanced --stop-after-init"

# 4. Reiniciar
ssh odoo-rc "sudo systemctl restart odoo-server"

# 5. Verificar logs
ssh odoo-rc "tail -100 /var/log/odoo/odoo-server.log | grep -i error"
```

**Deploy Produção:**
- [ ] Aprovação stakeholders
- [ ] Backup BD completo
- [ ] Janela de manutenção agendada
- [ ] Rollback plan preparado
- [ ] Monitoramento pós-deploy

**Status Fase 2:** ⏳ 50% COMPLETA (Pesquisa OK, Implementação Pendente)

---

## FASE 3: MELHORIAS INCREMENTAIS

**Prioridade:** 🟡 MÉDIA
**Estimativa:** 20-30 horas (1-2 semanas)
**Versão Alvo:** 15.0.3.0.0

### Feature 3.1: Template SMS Específico

**Objetivo:** Criar templates específicos para SMS (diferentes do email)

**Implementação:**
```python
# Adicionar campo em mail.compose.message
class MailComposerSMS(models.TransientModel):
    _inherit = 'mail.compose.message'

    sms_template_id = fields.Many2one('sms.template', 'SMS Template')

    def _prepare_sms_body(self):
        if self.sms_template_id:
            # Renderiza template SMS
            return self.sms_template_id.render(self.res_id)
        else:
            # Converte email → SMS
            return super()._prepare_sms_body()
```

**UI:**
```xml
<field name="sms_template_id"
       attrs="{'invisible': [('send_sms', '=', False)]}"/>
```

**Benefícios:**
- Mensagens SMS otimizadas (curtas e diretas)
- Melhor controle sobre conteúdo
- Templates reutilizáveis

**Estimativa:** 6-8 horas

### Feature 3.2: Preview do SMS

**Objetivo:** Mostrar preview do SMS antes de enviar

**Implementação:**
```xml
<field name="sms_preview" widget="text" readonly="1"
       attrs="{'invisible': [('send_sms', '=', False)]}"/>
```

```python
sms_preview = fields.Text(
    'SMS Preview',
    compute='_compute_sms_preview'
)

@api.depends('body', 'sms_template_id')
def _compute_sms_preview(self):
    for rec in self:
        rec.sms_preview = rec._prepare_sms_body()
```

**UI Enhancements:**
- Contador de caracteres em tempo real
- Indicador de múltiplos SMS (se > 160 chars)
- Estimativa de custo

**Estimativa:** 4-6 horas

### Feature 3.3: Respeitar Opt-in/Opt-out

**Objetivo:** Só enviar SMS para clientes que autorizaram

**Implementação:**
```python
# Adicionar campo em res.partner
class Partner(models.Model):
    _inherit = 'res.partner'

    sms_opt_in = fields.Boolean('SMS Opt-in', default=False)
    sms_opt_in_date = fields.Datetime('SMS Opt-in Date')
    sms_opt_out_date = fields.Datetime('SMS Opt-out Date')

# Validar em mail.compose.message
def _send_sms_to_recipients(self):
    valid_partners = self.partner_ids.filtered(
        lambda p: (p.mobile or p.phone) and p.sms_opt_in
    )
    # ...
```

**LGPD Compliance:**
- Campo opt-in obrigatório
- Log de consentimento
- Facilitar opt-out
- Respeitar blacklist

**Estimativa:** 8-10 horas

### Feature 3.4: Horário Inteligente (DND)

**Objetivo:** Não enviar SMS em horários inadequados

**Implementação:**
```python
def _check_dnd_time(self, partner):
    """Verifica se está em horário de envio permitido"""
    now = fields.Datetime.context_timestamp(self, fields.Datetime.now())
    hour = now.hour

    # DND: 22h às 8h
    if hour >= 22 or hour < 8:
        # Agenda para 8h do próximo dia
        return False
    return True

def _send_sms_to_recipients(self):
    for partner in valid_partners:
        if not self._check_dnd_time(partner):
            # Criar SMS agendado
            self.env['sms.scheduled'].create({...})
        else:
            # Enviar imediatamente
            self._send_sms_direct(...)
```

**Configurável:**
- Horário de início DND (default: 22h)
- Horário de fim DND (default: 8h)
- Respeitar fuso horário do destinatário

**Estimativa:** 6-8 horas

---

## FASE 4: FEATURES AVANÇADAS

**Prioridade:** 🟢 BAIXA
**Estimativa:** 40-60 horas (2-3 semanas)
**Versão Alvo:** 15.0.4.0.0

### Feature 4.1: Link Tracking e Shortlinks

**Objetivo:** Rastrear cliques em links enviados via SMS

**Implementação:**

1. **Modelo de Tracking:**
```python
class SMSLinkTracking(models.Model):
    _name = 'sms.link.tracking'

    sms_id = fields.Many2one('sms.message', required=True, ondelete='cascade')
    original_url = fields.Char('Original URL', required=True)
    short_url = fields.Char('Short URL', required=True)
    clicked_date = fields.Datetime('Clicked Date')
    ip_address = fields.Char('IP Address')
    user_agent = fields.Char('User Agent')
```

2. **Processamento de URLs:**
```python
def _process_sms_links(self, body):
    """
    Encontra URLs no corpo do SMS e substitui por shortlinks
    """
    import re
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', body)

    for url in urls:
        # Gera shortlink
        short = self._generate_shortlink(url)
        # Substitui no corpo
        body = body.replace(url, short)

    return body
```

3. **Redirect Controller:**
```python
class SMSLinkController(http.Controller):
    @http.route('/sms/l/<string:code>', auth='public')
    def redirect_link(self, code):
        tracking = request.env['sms.link.tracking'].sudo().search([
            ('short_url', 'like', code)
        ], limit=1)

        if tracking:
            # Registra clique
            tracking.write({
                'clicked_date': fields.Datetime.now(),
                'ip_address': request.httprequest.remote_addr,
                'user_agent': request.httprequest.user_agent.string,
            })

            # Redireciona
            return request.redirect(tracking.original_url)
```

**Benefícios:**
- Analytics de cliques
- URLs curtas economizam caracteres
- Rastreamento de conversão

**Estimativa:** 12-16 horas

### Feature 4.2: Agendamento Inteligente

**Objetivo:** Agendar envio de SMS para horário otimizado

**Implementação:**
```python
class MailComposerSMS(models.TransientModel):
    _inherit = 'mail.compose.message'

    sms_schedule_type = fields.Selection([
        ('now', 'Send Now'),
        ('scheduled', 'Scheduled Date'),
        ('optimized', 'Optimized Time'),
    ], default='now')

    sms_schedule_date = fields.Datetime('Schedule Date')

    def _get_optimized_send_time(self, partner):
        """
        Calcula melhor horário para enviar baseado em:
        - Histórico de cliques do partner
        - Horário comercial
        - Fuso horário
        """
        # ML ou regras simples
        # Retorna: próximo horário otimizado
```

**Analytics:**
- Taxa de abertura por horário
- Taxa de clique por dia da semana
- Melhor horário por segmento de cliente

**Estimativa:** 16-20 horas

### Feature 4.3: Retry Automático

**Objetivo:** Tentar reenviar SMS que falharam

**Implementação:**
```python
class SMSMessage(models.Model):
    _inherit = 'sms.message'

    retry_count = fields.Integer('Retry Count', default=0)
    max_retry = fields.Integer('Max Retries', default=3)
    next_retry_date = fields.Datetime('Next Retry Date')

    def cron_retry_failed_sms(self):
        """Cron que roda a cada hora"""
        failed_sms = self.search([
            ('state', '=', 'failed'),
            ('retry_count', '<', 'max_retry'),
            ('next_retry_date', '<=', fields.Datetime.now()),
        ])

        for sms in failed_sms:
            # Incrementa contador
            sms.retry_count += 1

            # Calcula próximo retry (exponential backoff)
            next_retry = fields.Datetime.now() + timedelta(hours=2**sms.retry_count)
            sms.next_retry_date = next_retry

            # Tenta reenviar
            sms.action_send()
```

**Estratégias:**
- Exponential backoff (1h, 2h, 4h, 8h)
- Máximo de tentativas configurável
- Notificação após falha definitiva

**Estimativa:** 8-10 hours

### Feature 4.4: Relatórios Avançados

**Objetivo:** Dashboards e relatórios detalhados

**Implementação:**

1. **Relatório de Entregas:**
```python
class SMSDeliveryReport(models.TransientModel):
    _name = 'sms.delivery.report'

    date_from = fields.Date()
    date_to = fields.Date()
    provider_id = fields.Many2one('sms.provider')

    def generate_report(self):
        # SQL query agregando dados
        # Gera gráficos (Chart.js)
```

2. **Métricas:**
- Taxa de entrega por provider
- Custo médio por SMS
- Tempo médio de entrega
- Taxa de erro por tipo
- ROI de campanhas

3. **Exportação:**
- PDF (reportlab)
- Excel (xlsxwriter)
- CSV

**Estimativa:** 12-16 horas

---

## FASE 5: ENTERPRISE FEATURES

**Prioridade:** 🔵 FUTURA
**Estimativa:** 80-120 horas (1-2 meses)
**Versão Alvo:** 15.0.5.0.0

### Feature 5.1: MMS (SMS com Imagem)

**Objetivo:** Enviar SMS com imagens/mídia

**Requisitos:**
- Provider com suporte MMS
- Upload de imagens
- Redimensionamento automático
- Validação de tamanho (< 500KB)

**Estimativa:** 20-24 horas

### Feature 5.2: SMS Interativo (Respostas)

**Objetivo:** Receber e processar respostas de SMS

**Implementação:**
```python
class SMSInbound(models.Model):
    _name = 'sms.inbound'

    from_number = fields.Char()
    to_number = fields.Char()
    body = fields.Text()
    received_date = fields.Datetime()
    original_sms_id = fields.Many2one('sms.message')

    def process_response(self):
        """
        Processa resposta e cria ação adequada:
        - Criar lead no CRM
        - Atualizar ticket de suporte
        - Opt-out automático
        """
```

**Webhooks:**
- Receber respostas via webhook do provider
- Parser de comandos (STOP, HELP, etc)
- Auto-responder

**Estimativa:** 24-30 horas

### Feature 5.3: Integração WhatsApp Business API

**Objetivo:** Enviar mensagens via WhatsApp além de SMS

**Implementação:**
```python
class MailComposerSMS(models.TransientModel):
    _inherit = 'mail.compose.message'

    send_via = fields.Selection([
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('both', 'Both'),
    ], default='sms')

    whatsapp_template_id = fields.Many2one('whatsapp.template')
```

**Requisitos:**
- WhatsApp Business API account
- Templates aprovados pelo WhatsApp
- Webhooks para respostas
- Rich media (imagens, vídeos, documentos)

**Estimativa:** 40-50 horas

### Feature 5.4: A/B Testing de Mensagens

**Objetivo:** Testar diferentes versões de mensagem SMS

**Implementação:**
```python
class SMSCampaign(models.Model):
    _inherit = 'sms.campaign'

    ab_test_enabled = fields.Boolean()
    variant_a_template = fields.Many2one('sms.template')
    variant_b_template = fields.Many2one('sms.template')
    ab_split_percent = fields.Integer(default=50)  # 50% A, 50% B

    def send_campaign_ab_test(self):
        total = len(self.partner_ids)
        split_at = int(total * (self.ab_split_percent / 100))

        # Grupo A
        group_a = self.partner_ids[:split_at]
        self._send_to_group(group_a, self.variant_a_template)

        # Grupo B
        group_b = self.partner_ids[split_at:]
        self._send_to_group(group_b, self.variant_b_template)
```

**Analytics:**
- Taxa de abertura A vs B
- Taxa de clique A vs B
- Conversão A vs B
- Winner automático

**Estimativa:** 16-20 horas

---

## COMANDOS ÚTEIS

### Git

```bash
# Commit incremental
git add chatroom_sms_advanced/wizard/mail_compose_sms.py
git commit -m "feat(chatter): add SMS checkbox to mail composer"

# Ver diff
git diff HEAD~1

# Criar branch para feature
git checkout -b feature/sms-checkbox-chatter

# Merge quando pronto
git checkout main
git merge feature/sms-checkbox-chatter
```

### Odoo - Desenvolvimento Local

```bash
# Atualizar módulo
cd /Users/andersongoliveira/odoo_15_sr
python3 odoo-bin -c odoo.conf -d test_db -u chatroom_sms_advanced --stop-after-init

# Shell interativo
python3 odoo-bin shell -c odoo.conf -d test_db

# Teste rápido
python3 -c "from odoo.addons.chatroom_sms_advanced.wizard.mail_compose_sms import MailComposerSMS; print('OK')"
```

### Odoo - Servidor Remoto

```bash
# Deploy código
scp -r chatroom_sms_advanced odoo-rc:/tmp/
ssh odoo-rc "sudo cp -r /tmp/chatroom_sms_advanced /odoo/custom/addons_custom/"
ssh odoo-rc "sudo chown -R odoo:odoo /odoo/custom/addons_custom/chatroom_sms_advanced"

# Atualizar módulo
ssh odoo-rc "cd /odoo/odoo-server && sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d realcred -u chatroom_sms_advanced --stop-after-init"

# Ver logs em tempo real
ssh odoo-rc "tail -f /var/log/odoo/odoo-server.log | grep -i 'chatroom_sms\|error'"

# Reiniciar Odoo
ssh odoo-rc "sudo systemctl restart odoo-server"

# Verificar status
ssh odoo-rc "sudo systemctl status odoo-server"
```

### Debugging

```bash
# Python shell no servidor
ssh odoo-rc "cd /odoo/odoo-server && sudo -u odoo python3"
>>> import odoo
>>> odoo.__version__

# Teste de imports
ssh odoo-rc "cd /odoo/odoo-server && python3 -c 'from odoo.addons.chatroom_sms_advanced.wizard.mail_compose_sms import MailComposerSMS'"

# Verificar módulo instalado
ssh odoo-rc "sudo -u postgres psql realcred -c \"SELECT name, state FROM ir_module_module WHERE name = 'chatroom_sms_advanced';\""

# Ver configuração do módulo
ssh odoo-rc "sudo -u postgres psql realcred -c \"SELECT web_icon FROM ir_ui_menu WHERE name = 'SMS Advanced';\""
```

### Backup e Restore

```bash
# Backup BD
ssh odoo-rc "sudo -u postgres pg_dump realcred > /tmp/realcred_backup_$(date +%Y%m%d_%H%M%S).sql"

# Backup módulo
ssh odoo-rc "cd /odoo/custom/addons_custom && sudo tar -czf chatroom_sms_advanced_$(date +%Y%m%d).tar.gz chatroom_sms_advanced"

# Download backup
scp odoo-rc:/tmp/realcred_backup_*.sql ~/backups/

# Restore (caso necessário)
ssh odoo-rc "sudo -u postgres psql realcred < /tmp/realcred_backup_XXXXXX.sql"
```

---

## CHECKLIST DE DEPLOY

### Pré-Deploy

- [ ] Código revisado (code review)
- [ ] Testes unitários passando
- [ ] Testes de integração passando
- [ ] Backup BD criado
- [ ] Backup módulo criado
- [ ] Documentação atualizada
- [ ] Changelog criado
- [ ] Aprovação stakeholders
- [ ] Janela de manutenção agendada
- [ ] Plano de rollback preparado

### Deploy Staging

- [ ] Deploy código em staging
- [ ] Atualizar módulo em staging
- [ ] Verificar logs (sem erros)
- [ ] Teste funcional completo
- [ ] Teste de performance
- [ ] Teste com usuários beta
- [ ] Correções de bugs (se houver)
- [ ] Validação final

### Deploy Produção

- [ ] Comunicar usuários (manutenção)
- [ ] Backup final BD produção
- [ ] Backup módulo produção
- [ ] Deploy código em produção
- [ ] Atualizar módulo em produção
- [ ] Reiniciar Odoo
- [ ] Verificar logs (sem erros)
- [ ] Smoke test (funcionalidades críticas)
- [ ] Monitorar por 1 hora
- [ ] Comunicar usuários (fim manutenção)

### Pós-Deploy

- [ ] Monitoramento 24h
- [ ] Coletar feedback usuários
- [ ] Documentar issues encontradas
- [ ] Planejar hotfixes (se necessário)
- [ ] Atualizar roadmap com status
- [ ] Celebrar! 🎉

---

## TRACKING DE PROGRESSO

### Resumo Geral

| Fase | Status | Progresso | Versão |
|------|--------|-----------|---------|
| Fase 1: Fundação | ✅ Completa | 100% | 15.0.2.0.0 |
| Fase 2: Checkbox SMS | ⏳ Em Andamento | 50% | 15.0.2.1.0 |
| Fase 3: Melhorias | 📋 Planejada | 0% | 15.0.3.0.0 |
| Fase 4: Features Avançadas | 📋 Planejada | 0% | 15.0.4.0.0 |
| Fase 5: Enterprise | 📋 Futura | 0% | 15.0.5.0.0 |

### Próximos Passos (Imediatos)

1. **HOJE:** Implementar `mail_compose_sms.py` (modelo Python)
2. **AMANHÃ:** Implementar view XML do checkbox
3. **DIA 3:** Testes e integração
4. **DIA 4:** Deploy staging e validação
5. **DIA 5:** Deploy produção

### Métricas de Sucesso

**Fase 2 (Checkbox SMS):**
- [ ] 0 erros de instalação/atualização
- [ ] Checkbox aparece em todos os modelos com chatter
- [ ] Taxa de sucesso envio SMS > 95%
- [ ] Tempo de resposta < 2s (envio combinado)
- [ ] Satisfação usuários > 4/5

**Fase 3 (Melhorias):**
- [ ] Templates SMS usados em > 70% envios
- [ ] Opt-in implementado (LGPD compliance)
- [ ] 0 SMS enviados fora de horário DND
- [ ] Preview reduz erros em 50%

**Fase 4 (Features Avançadas):**
- [ ] Click-through rate > 10%
- [ ] Retry automático recupera > 30% falhas
- [ ] Relatórios usados semanalmente
- [ ] ROI tracking habilitado

---

## NOTAS FINAIS

### Priorização

**Critérios de Prioridade:**
1. 🔥 Impacto no usuário (alto = prioridade)
2. 💰 Valor de negócio (ROI esperado)
3. ⚙️ Complexidade técnica (baixa = prioridade)
4. 🔗 Dependências (bloqueantes = prioridade)

**Decisões de Trade-off:**
- Fase 2 (Checkbox) prioritária: alto impacto, baixa complexidade
- Fase 3 (Melhorias) antes de Fase 4: fundação sólida
- Fase 5 (Enterprise) pode ser descontinuada se ROI baixo

### Riscos Identificados

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| API Kolmeya indisponível | Baixa | Alto | Cache local, retry, fallback provider |
| Performance (envio massa) | Média | Médio | Batch processing, async workers |
| LGPD compliance | Baixa | Alto | Opt-in obrigatório, audit logs |
| Custo SMS elevado | Média | Médio | Alertas de threshold, approval workflow |
| Integração WhatsApp complexa | Alta | Baixo | POC primeiro, MVP reduzido |

### Contatos e Recursos

**Stakeholders:**
- Anderson Oliveira (Desenvolvedor)
- [Nome] (Product Owner)
- [Nome] (QA/Tester)

**Recursos Externos:**
- Kolmeya API Docs: [URL]
- Odoo Community Forum: https://www.odoo.com/forum
- WhatsApp Business API: https://business.whatsapp.com

**Documentação Relacionada:**
- `/odoo_15_sr/ANALISE_ESTRUTURA_SMS_EXISTENTE.md`
- `/odoo_15_sr/PESQUISA_CHATTER_SMS_CHECKBOX.md`
- `/odoo_15_sr/INSTALACAO_COMPLETA_SMS_ADVANCED.md`
- `/odoo_15_sr/ICONE_SMS_FINAL_PROFISSIONAL.md`
- `/odoo_15_sr/COMO_ACESSAR_SMS_ADVANCED.md`

---

**FIM DO ROADMAP COMPLETO**

**Última atualização:** 16/11/2025
**Próxima revisão:** Ao final de cada fase
**Mantenedor:** Anderson Oliveira
