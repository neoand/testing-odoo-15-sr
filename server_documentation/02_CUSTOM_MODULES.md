# Módulos Customizados - odoo-rc

**Data da documentação:** 2025-11-15
**Servidor:** odoo-rc (35.199.79.229)

---

## Estrutura de Diretórios Custom

### Tamanhos por Diretório
```
195M    /odoo/custom/addons_custom
65M     /odoo/custom/hr_attendance_pro
39M     /odoo/custom/l10n_br_base
33M     /odoo/custom/social
17M     /odoo/custom/addons-whatsapp-connector
15M     /odoo/custom/om_account_accountant
7.1M    /odoo/custom/helpdesk
2.6M    /odoo/custom/helpdesk-15.0
```

**Total:** ~373 MB de módulos customizados

---

## 1. Addons Custom (/odoo/custom/addons_custom/) - 195 MB

### Módulos de Interface/UX
- **web_responsive** - Interface responsiva para mobile
- **muk_web_theme** - Tema customizado
- **web_drop_target** - Drag & drop de arquivos
- **web_no_bubble** - Controle de eventos UI

### Módulos de Integração
- **3cxcrm** - Integração com 3CX telefonia
- **xf_excel_odoo_connector** - Conector Excel
- **auto_backup_odoo** - Backup automático

### Módulos de CRM
- **crm_phonecall** - Registro de ligações
- **crm_products** - Produtos no CRM
- **contacts_realcred** - Contatos customizados Realcred

### Módulos de RH/Attendance
- **gs_hr_attendance** - Ponto eletrônico
- **attendance_reason** - Motivos de ponto
- **hr_employee_medical_examination** - Exames médicos
- **employee_documents_expiry** - Vencimento de documentos

### Módulos de Gestão Documental
- **dms** - Document Management System
- **jt_contacts_documents** - Documentos de contatos
- **partner_firstname** - Nome/Sobrenome separados
- **partner_custom_fields** - Campos customizados de parceiros

### Módulos de Relatórios/Análise
- **report_xlsx** - Relatórios em Excel
- **ks_dashboard_ninja** - Dashboard ninja
- **ks_dn_advance** - Dashboard ninja avançado

### Módulos Financeiros
- **oi_bank_reconciliation** - Conciliação bancária

### Módulos de Gestão de Sessões
- **advanced_session_management** - Gestão avançada de sessões

---

## 2. WhatsApp Connector (/odoo/custom/addons-whatsapp-connector/) - 17 MB

### Módulos Core
- **whatsapp_connector** - Conector base WhatsApp
- **whatsapp_connector_admin** - Administração
- **whatsapp_connector_bot** - Bot automatizado
- **whatsapp_connector_chatsmart** - Chat inteligente
- **whatsapp_connector_chatter** - Integração com chatter Odoo

### Integrações WhatsApp
- **whatsapp_connector_crm** - WhatsApp + CRM
- **whatsapp_connector_helpdesk** - WhatsApp + Helpdesk
- **whatsapp_connector_send_account** - Envio faturas
- **whatsapp_connector_send_crm** - Envio CRM
- **whatsapp_connector_send_helpdesk** - Envio helpdesk
- **whatsapp_connector_send_purchase** - Envio compras
- **whatsapp_connector_send_repair** - Envio reparos
- **whatsapp_connector_send_sale** - Envio vendas
- **whatsapp_connector_send_stock** - Envio estoque
- **whatsapp_connector_send_subscription** - Envio assinaturas

### Funcionalidades WhatsApp
- **whatsapp_connector_mass** - Envio em massa
- **whatsapp_connector_template_base** - Templates base
- **whatsapp_connector_access** - Controle de acesso
- **whatsapp_connector_access_crm** - Acesso CRM
- **whatsapp_connector_access_helpdesk** - Acesso helpdesk
- **whatsapp_connector_apichat** - API chat
- **whatsapp_connector_assign_agent** - Atribuir agente
- **whatsapp_connector_audio_record** - Gravação de áudio
- **whatsapp_connector_default_answer_category** - Respostas padrão
- **whatsapp_connector_message_option** - Opções de mensagem
- **whatsapp_connector_product_option** - Opções de produto
- **whatsapp_connector_show_all_conversation** - Ver todas conversas
- **whatsapp_connector_split_new_chat** - Dividir conversas
- **whatsapp_connector_tags** - Tags para conversas

---

## 3. Helpdesk (/odoo/custom/helpdesk/) - 7.1 MB

### Módulos
- **helpdesk_mgmt** - Gestão de helpdesk base
- **helpdesk_mgmt_project** - Integração com projetos
- **helpdesk_mgmt_rating** - Avaliações
- **helpdesk_mgmt_timesheet** - Timesheet
- **helpdesk_mgmtsystem_nonconformity** - Não conformidades
- **helpdesk_type** - Tipos de tickets

**Nota:** Existe também `/odoo/custom/helpdesk-15.0/` (2.6 MB) - versão alternativa

---

## 4. Localização Brasil (/odoo/custom/l10n_br_base/) - 39 MB

### Módulos Fiscais
- **l10n_br_base** - Base localização Brasil
- **l10n_br_fiscal** - Módulo fiscal brasileiro
- **l10n_br_account** - Contabilidade Brasil
- **l10n_br_nfe** - Nota Fiscal Eletrônica
- **l10n_br_nfe_spec** - Especificação NFe
- **l10n_br_nfse** - Nota Fiscal Serviços Eletrônica

### Módulos de Pagamento Brasil
- **account_payment_mode** - Modos de pagamento
- **account_payment_order** - Ordens de pagamento
- **account_payment_partner** - Pagamento de parceiros
- **l10n_br_account_payment_brcobranca** - Cobrança Brasil
- **l10n_br_account_payment_order** - Ordem pagamento BR
- **payment_pagseguro** - Gateway PagSeguro

### Módulos de Negócio Brasil
- **l10n_br_sale** - Vendas Brasil
- **l10n_br_purchase** - Compras Brasil
- **l10n_br_stock** - Estoque Brasil
- **l10n_br_contract** - Contratos Brasil
- **l10n_br_crm** - CRM Brasil
- **l10n_br_hr** - RH Brasil
- **l10n_br_portal** - Portal Brasil
- **l10n_br_website_sale** - E-commerce Brasil

### Módulos de Suporte Brasil
- **l10n_br_zip** - CEP/Endereços
- **l10n_br_currency_rate_update** - Atualização câmbio
- **l10n_br_resource** - Recursos Brasil
- **l10n_br_coa** - Plano de contas
- **l10n_br_coa_generic** - Plano contas genérico
- **l10n_br_coa_simple** - Plano contas simples
- **l10n_br_account_due_list** - Lista de vencimentos
- **l10n_br_mis_report** - Relatórios MIS
- **account_due_list** - Lista vencimentos
- **contract** - Contratos
- **spec_driven_model** - Modelos driven

---

## 5. Social (/odoo/custom/social/) - 33 MB

### Módulos de Email
- **base_search_mail_content** - Busca em emails
- **mail_activity_board** - Quadro de atividades
- **mail_activity_creator** - Criador de atividades
- **mail_activity_done** - Atividades concluídas
- **mail_activity_partner** - Atividades parceiro
- **mail_activity_team** - Atividades time
- **mail_attach_existing_attachment** - Anexar arquivos
- **mail_autosubscribe** - Auto subscrição
- **mail_debrand** - Remove marca Odoo
- **mail_optional_follower_notification** - Notificações opcionais
- **mail_outbound_static** - Email estático
- **mail_preview_base** - Preview de email
- **mail_show_follower** - Mostrar seguidores
- **mail_tracking** - Rastreamento de email

### Integração
- **whatsapp_integration** - Integração WhatsApp

---

## 6. HR Attendance Pro (/odoo/custom/hr_attendance_pro/) - 65 MB

Módulo profissional de controle de ponto eletrônico e gestão de frequência.

---

## 7. Account Accountant (/odoo/custom/om_account_accountant/) - 15 MB

Módulo de contabilidade avançada.

---

## 8. IURD CM MX (/odoo/iurd-cm-mx/)

**IMPORTANTE:** Diretório adicional não incluído no addons_path padrão!

### Conteúdo
- **custom/** - Módulos customizados específicos
- **ingresos_cm/** - Gestão de ingressos
- **whatsapp_connector_SO** - Conector WhatsApp Sales Order
- **whatsapp_connector_pack_SO** - Pack WhatsApp SO
- **whatsapp_connector_premium** - WhatsApp premium

**Nota:** Este diretório está em `/odoo/iurd-cm-mx/` mas NÃO está no `addons_path` do arquivo de configuração. Pode estar inativo ou em desenvolvimento.

---

## Dependências Python Customizadas (/odoo/requirements.txt)

```
werkzeug==0.16.1
erpbrasil.assinatura
erpbrasil.base
erpbrasil.edoc
erpbrasil.edoc.pdf
erpbrasil.transmissao
nfelib
num2words
odoo_test_helper
pycep_correios
workalendar
xmldiff
html2text
phonenumbers
selenium
voximplant-apiclient
vobject
pysftp
dropbox
tqdm
boto3
botocore
simplejson
```

### Categorias de Dependências

**Fiscal Brasil:**
- erpbrasil.* (assinatura, base, edoc, pdf, transmissão)
- nfelib (Nota Fiscal Eletrônica)
- pycep_correios (CEP)

**Comunicação:**
- voximplant-apiclient (Telefonia)
- phonenumbers (Validação telefone)

**Automação/Testes:**
- selenium (Automação web)
- odoo_test_helper

**Storage:**
- boto3, botocore (AWS S3)
- dropbox (Dropbox)
- pysftp (SFTP)

**Utilidades:**
- num2words (Números por extenso)
- workalendar (Calendário/feriados)
- xmldiff (Comparação XML)
- html2text (Conversão HTML)
- vobject (vCard/iCal)
- tqdm (Progress bar)
- simplejson (JSON)

---

## Resumo de Módulos por Categoria

### CRM & Vendas
- CRM base + phonecall + products
- WhatsApp integrado
- Localização Brasil vendas

### Helpdesk
- Gestão completa de tickets
- Integração WhatsApp
- Timesheet e projetos
- Avaliações

### RH & Ponto
- Ponto eletrônico profissional
- Controle de ausências
- Gestão de documentos
- Exames médicos

### Fiscal & Financeiro
- NFe, NFse completo
- Pagamentos Brasil
- Conciliação bancária
- Contratos

### Comunicação
- WhatsApp (30+ módulos)
- Email tracking
- Notificações

### Interface
- Tema responsivo
- Dashboard ninja
- Relatórios Excel

---

## Comandos Úteis

### Listar módulos instalados no BD
```bash
ssh odoo-rc "sudo -u postgres psql realcred -c \"SELECT name, state FROM ir_module_module WHERE state = 'installed' ORDER BY name;\""
```

### Ver tamanho dos módulos
```bash
ssh odoo-rc "du -sh /odoo/custom/*"
```

### Backup dos módulos custom
```bash
ssh odoo-rc "tar -czf /tmp/odoo_custom_$(date +%Y%m%d).tar.gz /odoo/custom/"
```

### Verificar módulos com erros
```bash
ssh odoo-rc "sudo tail -f /var/log/odoo/odoo-server.log | grep -i error"
```

---

## Atenção

1. **Sessões acumuladas:** `/odoo/filestore/sessions` com 5.7 GB - limpar periodicamente
2. **IURD CM MX:** Diretório `/odoo/iurd-cm-mx/` não está no addons_path - verificar se está ativo
3. **Backup regular:** Total de ~373 MB de módulos custom - fazer backup regular
4. **Dependências:** Verificar se todas as dependências Python estão instaladas
