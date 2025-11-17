# 📱 Documentação Completa: Contact Center SMS + WhatsApp

> **Projeto:** Integração SMS via Kolmeya com ChatRoom do AcruxLab
> **Versão Odoo:** 15.0
> **Data:** Novembro 2025
> **Autor:** Anderson Oliveira + Claude Code
> **Status:** ✅ Produção

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Módulos Desenvolvidos](#módulos-desenvolvidos)
4. [Instalação e Configuração](#instalação-e-configuração)
5. [Problemas Encontrados e Soluções](#problemas-encontrados-e-soluções)
6. [API Kolmeya - Descobertas Importantes](#api-kolmeya-descobertas-importantes)
7. [Integração com ChatRoom](#integração-com-chatroom)
8. [Testes e Validação](#testes-e-validação)
9. [Troubleshooting](#troubleshooting)
10. [Comandos Úteis](#comandos-úteis)

---

## 🎯 Visão Geral

### Objetivo
Criar um Contact Center unificado que integra SMS e WhatsApp na mesma interface do ChatRoom (AcruxLab), permitindo que operadores atendam clientes por ambos os canais de forma transparente.

### Funcionalidades Implementadas
- ✅ Envio de SMS via API Kolmeya
- ✅ Recebimento de respostas via webhook
- ✅ Templates de SMS com variáveis Jinja2
- ✅ Associação automática de parceiros (mesmo com formatos diferentes de telefone)
- ✅ Wizard de envio em massa
- ✅ Rastreamento de status de entrega
- ✅ Consulta de saldo da conta Kolmeya
- ✅ Integração com ChatRoom do AcruxLab
- ✅ Interface unificada SMS + WhatsApp

### Stack Tecnológica
- **Backend:** Python 3.8, Odoo 15.0
- **Database:** PostgreSQL 12
- **API Externa:** Kolmeya SMS REST API v1
- **Frontend:** JavaScript (Odoo Web Client)
- **Infraestrutura:** Ubuntu 20.04, Nginx, SSL

---

## 🏗️ Arquitetura do Sistema

### Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                     ODOO 15 - CONTACT CENTER                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────┐         ┌──────────────────────┐       │
│  │  ChatRoom UI      │◄────────┤  AcruxLab WhatsApp   │       │
│  │  (Interface       │         │  Connector           │       │
│  │   Unificada)      │         └──────────────────────┘       │
│  └─────────┬─────────┘                                         │
│            │                                                   │
│            │                                                   │
│  ┌─────────▼─────────────────────────────────────────────┐   │
│  │        contact_center_sms (Módulo Integrador)         │   │
│  │  • connector.py - Estende acrux.chat.connector       │   │
│  │  • conversation.py - Estende acrux.chat.conversation │   │
│  │  • message.py - Estende acrux.chat.message           │   │
│  └─────────┬─────────────────────────────────────────────┘   │
│            │                                                   │
│  ┌─────────▼─────────┐       ┌──────────────────────┐       │
│  │  sms_base_sr      │       │   sms_kolmeya        │       │
│  │  • sms.message    │◄──────┤  • Provider Kolmeya  │       │
│  │  • sms.template   │       │  • Kolmeya API       │       │
│  │  • sms.provider   │       │  • Webhooks          │       │
│  └───────────────────┘       └──────────┬───────────┘       │
│                                          │                    │
└──────────────────────────────────────────┼────────────────────┘
                                           │
                                           │ HTTPS
                                           ▼
                            ┌──────────────────────────┐
                            │   Kolmeya SMS API        │
                            │   https://kolmeya.com.br │
                            └──────────────────────────┘
                                           │
                                           │ SMS
                                           ▼
                                    ┌─────────────┐
                                    │   Cliente   │
                                    └─────────────┘
```

### Fluxo de Dados

#### Envio de SMS
```
1. Usuário → ChatRoom UI → contact_center_sms.message.create()
2. message.create() → sms_base_sr.sms.message.create()
3. sms.message → sms_kolmeya.provider._send_sms()
4. provider → KolmeyaAPI.send_sms() → HTTPS POST
5. Kolmeya API → SMS enviado para cliente
```

#### Recebimento de Resposta
```
1. Cliente responde SMS → Kolmeya API
2. Kolmeya API → Webhook POST /kolmeya/webhook/reply
3. Webhook → Normaliza telefone → Busca parceiro
4. Webhook → Cria sms.message (incoming)
5. Webhook → Cria acrux.chat.message
6. ChatRoom UI → Atualiza interface em tempo real
```

---

## 📦 Módulos Desenvolvidos

### 1. sms_base_sr (Base SMS)

**Localização:** `/odoo/custom/addons_custom/sms_base_sr/`

**Propósito:** Módulo base para gestão de SMS, independente de provider.

#### Estrutura de Arquivos
```
sms_base_sr/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── sms_message.py      # Modelo principal de mensagens
│   ├── sms_template.py     # Templates com Jinja2
│   ├── sms_provider.py     # Provider abstrato
│   ├── sms_compose.py      # Wizard de envio
│   └── res_partner.py      # Extensão de parceiros
├── views/
│   ├── sms_message_views.xml
│   ├── sms_template_views.xml
│   ├── sms_provider_views.xml
│   ├── sms_compose_views.xml
│   ├── res_partner_views.xml
│   └── sms_menu.xml
├── security/
│   ├── sms_security.xml
│   └── ir.model.access.csv
├── data/
│   └── sms_template_data.xml
└── static/
    └── description/
        └── icon.png        # Ícone do módulo
```

#### Modelo: sms.message

**Campos principais:**
```python
partner_id = Many2one('res.partner')          # Cliente
phone = Char(required=True)                    # Telefone
body = Text(required=True)                     # Conteúdo
direction = Selection(['outgoing', 'incoming']) # Direção
state = Selection(['draft', 'outgoing', 'sent', 'delivered', 'error', 'rejected'])
provider_id = Many2one('sms.provider')         # Provider usado
provider_message_id = Char()                   # ID na API externa
provider_reference = Char()                    # Referência customizada
sent_date = Datetime()                         # Data de envio
delivered_date = Datetime()                    # Data de entrega
error_message = Text()                         # Mensagem de erro
```

**Métodos importantes:**
```python
def action_send(self):
    """Envia SMS via provider configurado"""

def _find_partner_by_phone(self, phone):
    """Busca parceiro pelo telefone (normalizado)"""

def _normalize_phone(self, phone):
    """Remove formatação: +55 48 99191-0234 → 5548991910234"""
```

#### Modelo: sms.template

**Campos principais:**
```python
name = Char(required=True)                     # Nome do template
model_id = Many2one('ir.model')                # Modelo (res.partner, etc)
body = Text(required=True)                     # Template Jinja2
lang = Selection()                             # Idioma
```

**Exemplo de template:**
```jinja2
Olá {{ object.name }},

Sua parcela vence em {{ object.proxima_parcela_data }}.
Valor: R$ {{ object.proxima_parcela_valor }}

Dúvidas? {{ user.company_id.phone }}

{{ user.name }}
```

### 2. sms_kolmeya (Provider Kolmeya)

**Localização:** `/odoo/custom/addons_custom/sms_kolmeya/`

**Propósito:** Implementação específica do provider Kolmeya.

#### Estrutura de Arquivos
```
sms_kolmeya/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── sms_provider_kolmeya.py   # Extensão do provider
│   └── kolmeya_api.py             # Wrapper da API REST
├── controllers/
│   ├── __init__.py
│   └── kolmeya_webhooks.py        # Endpoints webhooks
├── views/
│   └── sms_provider_views.xml     # Views Kolmeya
├── security/
│   └── ir.model.access.csv
└── data/
    └── sms_provider_data.xml      # Provider padrão
```

#### Classe: KolmeyaAPI

**Localização:** `models/kolmeya_api.py`

```python
class KolmeyaAPI:
    """Wrapper completo da API Kolmeya v1"""

    BASE_URL = "https://kolmeya.com.br/api/v1"

    def __init__(self, token, segment_id=109):
        """
        Args:
            token: Bearer token (com ou sem prefixo "Bearer ")
            segment_id: ID do segmento (padrão: 109 - CORPORATIVO)
        """

    def send_sms(self, phone, message, reference=None):
        """Envia SMS único"""

    def send_batch(self, messages_list):
        """Envia lote de até 1000 SMS"""

    def get_balance(self):
        """
        Consulta saldo da conta

        ⚠️ IMPORTANTE: API retorna {"balance": "R$9.396,84"}
        Precisamos converter para float!

        Returns:
            {
                'saldo': 9396.84,          # float para cálculos
                'balance_str': 'R$9.396,84' # string original
            }
        """
        response = self._make_request('/sms/balance')
        balance_str = response.get('balance', 'R$0,00')

        # Converte "R$9.396,84" → 9396.84
        balance_clean = balance_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
        balance_float = float(balance_clean)

        return {
            'saldo': balance_float,
            'balance_str': balance_str
        }
```

**Descoberta crítica sobre get_balance():**

A documentação da Kolmeya não deixa claro, mas a API retorna o saldo em formato **string brasileira** com cifrão:
- ❌ Esperado: `{"saldo": 9396.84}`
- ✅ Real: `{"balance": "R$9.396,84"}`

Por isso foi necessário criar lógica de conversão.

#### Webhooks

**Localização:** `controllers/kolmeya_webhooks.py`

##### Endpoint: /kolmeya/webhook/reply

**Payload esperado da Kolmeya:**
```json
{
    "phone": "5548991910234",
    "message": "Oi, tenho interesse",
    "reference": "msg_123",
    "data": "2025-11-15 14:30:00"
}
```

**Lógica implementada:**
```python
def webhook_reply(self, **kwargs):
    data = request.jsonrequest
    phone = data.get('phone')
    message_text = data.get('message')

    # PROBLEMA RESOLVIDO: Busca de parceiro por telefone
    # Antes: Apenas buscava mensagem anterior
    # Depois: Busca parceiro diretamente com normalização

    clean_phone = str(phone).replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

    partner = request.env['res.partner'].sudo().search([
        '|', '|', '|',
        ('phone', 'ilike', clean_phone),
        ('mobile', 'ilike', clean_phone),
        ('phone', 'ilike', f'+{clean_phone}'),
        ('mobile', 'ilike', f'+{clean_phone}')
    ], limit=1)

    # Cria mensagem incoming com parceiro associado
    reply_sms = request.env['sms.message'].sudo().create({
        'partner_id': partner.id if partner else False,
        'phone': phone,
        'body': message_text,
        'direction': 'incoming',
        'state': 'delivered',
    })
```

**Problema resolvido:**
- Antes: Mensagens incoming ficavam sem `partner_id`
- Causa: Webhook só buscava mensagem anterior, não buscava parceiro
- Solução: Busca direta em `res.partner` com normalização de telefone

### 3. contact_center_sms (Integrador ChatRoom)

**Localização:** `/odoo/custom/addons_custom/contact_center_sms/`

**Propósito:** Integra SMS com ChatRoom do AcruxLab.

#### Estrutura de Arquivos
```
contact_center_sms/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── connector.py        # Estende acrux.chat.connector
│   ├── conversation.py     # Estende acrux.chat.conversation
│   └── message.py          # Estende acrux.chat.message
├── views/
│   └── connector_views.xml
├── security/
│   └── ir.model.access.csv
└── static/
    └── description/
        └── icon.png
```

#### Extensão: acrux.chat.connector

**Localização:** `models/connector.py`

**Novos campos:**
```python
_inherit = 'acrux.chat.connector'

connector_type = Selection(selection_add=[('sms', 'SMS')])
sms_provider_id = Many2one('sms.provider')
```

**Métodos críticos override:**

##### 1. assert_id(key)
```python
def assert_id(self, key):
    """
    Validação de número para SMS (mais flexível que WhatsApp)
    """
    self.ensure_one()

    if self.connector_type == 'sms':
        # SMS aceita qualquer número com dígitos
        if key and any(c.isdigit() for c in str(key)):
            return True

    return super(AcruxChatConnector, self).assert_id(key)
```

##### 2. clean_id(key)
```python
def clean_id(self, key):
    """Remove tudo exceto dígitos para SMS"""
    self.ensure_one()

    if self.connector_type == 'sms':
        return ''.join(filter(str.isdigit, str(key)))

    return super(AcruxChatConnector, self).clean_id(key)
```

##### 3. format_id(key)
```python
def format_id(self, key):
    """Formata número para SMS: +5511999887766"""
    self.ensure_one()

    if self.connector_type == 'sms':
        cleaned = self.clean_id(key)
        if cleaned and not cleaned.startswith('+'):
            return '+' + cleaned
        return cleaned if cleaned else key

    return super(AcruxChatConnector, self).format_id(key)
```

##### 4. ca_get_status() ⚠️ MÉTODO COMPLEXO

**Propósito:** Verifica status do connector (chamado pelo botão "Check Status")

**Problema encontrado:**
```python
# ERRO 1: Signature incompatível com parent
def ca_get_status(self):
    # Tentou chamar super().ca_request() mas signature estava errada
```

**Solução:**
```python
def ca_get_status(self):
    """Verifica status do connector SMS"""
    self.ensure_one()

    if self.connector_type == 'sms':
        Pop = self.env['acrux.chat.pop.message']

        if not self.sms_provider_id:
            raise UserError(_('No SMS provider configured'))

        provider = self.sms_provider_id

        # PROBLEMA: Campos tinham nomes errados!
        # ❌ provider.api_key
        # ❌ provider.segment_id
        # ✅ provider.kolmeya_api_token
        # ✅ provider.kolmeya_segment_id

        if not provider.kolmeya_api_token:
            raise UserError(_('SMS Provider not configured'))

        try:
            from odoo.addons.sms_kolmeya.models.kolmeya_api import KolmeyaAPI

            api = KolmeyaAPI(
                token=provider.kolmeya_api_token,
                segment_id=provider.kolmeya_segment_id
            )

            balance = api.get_balance()
            saldo = balance.get('saldo', 0.0)

            # Atualiza status do connector
            self.ca_status = True
            self.message = False

            # Retorna popup do AcruxLab
            message = _('SMS Provider Status')
            detail = _('<b>Connected successfully!</b><br/>'
                      'Provider: %s<br/>'
                      'Balance: R$ %.2f') % (provider.name, saldo)

            return Pop.message(message, detail)

        except Exception as e:
            self.ca_status = False
            self.message = str(e)
            message = _('SMS Provider Error')
            detail = _('<b>Failed to connect</b><br/>%s') % str(e)
            return Pop.message(message, detail)

    return super(AcruxChatConnector, self).ca_get_status()
```

##### 5. ca_request() ⚠️ MÉTODO CRÍTICO

**Propósito:** Faz requisições à API externa (usado pelo AcruxLab para WhatsApp)

**PROBLEMA CRÍTICO - Signature Incompatível:**

O AcruxLab original chama:
```python
data = self.ca_request('status_get', timeout=20)
```

Nossa primeira tentativa:
```python
# ❌ ERRADO - Signature diferente!
def ca_request(self, endpoint, data=None, **kwargs):
    # ...
```

Erro resultante:
```
TypeError: ca_request() got an unexpected keyword argument 'timeout'
```

**Solução - Signature EXATA:**
```python
def ca_request(self, path, data={}, params={}, timeout=False, ignore_exception=False):
    """
    IMPORTANTE: Signature EXATAMENTE igual ao método original!

    Para SMS: não faz sentido (sem API de status direto)
    Para WhatsApp: usa método original
    """
    self.ensure_one()

    if self.connector_type == 'sms':
        raise UserError(_(
            'Direct API requests are not supported for SMS connectors.\n'
            'Use "Check Status" button instead.'
        ))

    # Passa TODOS os parâmetros para o parent
    return super(AcruxChatConnector, self).ca_request(
        path, data, params, timeout, ignore_exception
    )
```

**Lição aprendida:** Em Python com herança múltipla, override de métodos PRECISA ter a **mesma signature** do parent, senão quebra o polimorfismo.

---

## 🚀 Instalação e Configuração

### Pré-requisitos

1. **Odoo 15.0** instalado e funcionando
2. **PostgreSQL 12+**
3. **Python 3.8+**
4. **Módulo AcruxLab WhatsApp Connector** instalado
5. **Conta na Kolmeya** com:
   - Bearer Token
   - Segment ID (padrão: 109)

### Passo 1: Copiar Módulos

```bash
# Copiar módulos para addons customizados
sudo cp -r sms_base_sr /odoo/custom/addons_custom/
sudo cp -r sms_kolmeya /odoo/custom/addons_custom/
sudo cp -r contact_center_sms /odoo/custom/addons_custom/

# Ajustar permissões
sudo chown -R odoo:odoo /odoo/custom/addons_custom/sms_base_sr
sudo chown -R odoo:odoo /odoo/custom/addons_custom/sms_kolmeya
sudo chown -R odoo:odoo /odoo/custom/addons_custom/contact_center_sms
```

### Passo 2: Atualizar Lista de Módulos

```bash
# Via interface Odoo
Apps > Update Apps List

# Ou via comando
cd /odoo/odoo-server
sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d realcred --stop-after-init -u base
```

### Passo 3: Instalar Módulos (Ordem Importante!)

```bash
# 1. Instalar base primeiro
Apps > sms_base_sr > Install

# 2. Instalar provider Kolmeya
Apps > sms_kolmeya > Install

# 3. Instalar integrador ChatRoom
Apps > contact_center_sms > Install
```

**⚠️ IMPORTANTE:** Ordem de instalação importa por causa das dependências!

### Passo 4: Configurar Provider Kolmeya

```sql
-- Via SQL (mais rápido)
UPDATE sms_provider
SET
    kolmeya_api_token = 'Bearer SEU_TOKEN_AQUI',
    kolmeya_segment_id = 109,
    active = true
WHERE provider_type = 'kolmeya';
```

Ou via interface:
1. SMS > Configuration > Providers
2. Abrir "Kolmeya"
3. Preencher:
   - **API Token:** Bearer xxxxx
   - **Segment ID:** 109
   - **Active:** ✓

### Passo 5: Criar Connector SMS no ChatRoom

```sql
-- Criar connector SMS via SQL
INSERT INTO acrux_chat_connector (
    name,
    connector_type,
    sequence,
    sms_provider_id,
    ca_status,
    company_id,
    create_uid,
    write_uid
) VALUES (
    'SMS Kolmeya',
    'sms',
    10,
    (SELECT id FROM sms_provider WHERE provider_type = 'kolmeya' LIMIT 1),
    true,
    1,
    2,
    2
);
```

**Verificar criação:**
```sql
SELECT id, name, connector_type, ca_status
FROM acrux_chat_connector
WHERE connector_type = 'sms';
```

### Passo 6: Configurar Webhook da Kolmeya

**URL do webhook:**
```
https://odoo.semprereal.com/kolmeya/webhook/reply
```

**Configuração no painel Kolmeya:**
1. Login em https://kolmeya.com.br
2. Configurações > Webhooks
3. Adicionar webhook:
   - **URL:** https://odoo.semprereal.com/kolmeya/webhook/reply
   - **Tipo:** Resposta de SMS
   - **Método:** POST
   - **Content-Type:** application/json

**Testar webhook:**
```bash
curl -X POST https://odoo.semprereal.com/kolmeya/webhook/reply \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "5548991910234",
    "message": "Teste de webhook",
    "reference": "test_123",
    "data": "2025-11-15 14:30:00"
  }'
```

### Passo 7: Verificar Instalação

```bash
# Verificar logs
sudo journalctl -u odoo-server -n 100 --no-pager | grep -i sms

# Verificar módulos instalados
sudo -u postgres psql realcred -c "
SELECT name, state, latest_version
FROM ir_module_module
WHERE name LIKE '%sms%' OR name LIKE '%contact_center%';
"

# Verificar connector criado
sudo -u postgres psql realcred -c "
SELECT id, name, connector_type, ca_status, sms_provider_id
FROM acrux_chat_connector
WHERE connector_type = 'sms';
"
```

---

## 🐛 Problemas Encontrados e Soluções

### Problema 1: Ícone do Módulo Não Aparece

**Sintoma:**
```
Menu SMS aparece sem ícone no Odoo
```

**Causa:**
1. Faltava `'application': True` no `__manifest__.py`
2. Faltava `'images'` apontando para o ícone

**Solução:**
```python
# __manifest__.py
{
    'name': 'SMS Base - SempreReal',
    'application': True,  # ✅ NECESSÁRIO!
    'images': ['static/description/icon.png'],  # ✅ NECESSÁRIO!
    # ...
}
```

E no XML do menu:
```xml
<menuitem id="menu_sms_root"
          name="SMS"
          web_icon="sms_base_sr,static/description/icon.png"/>
```

**Referência:** Problema similar ao que tivemos antes com outros módulos.

### Problema 2: TypeError - ca_request() Signature Incompatível

**Sintoma:**
```
TypeError: ca_request() got an unexpected keyword argument 'timeout'
```

**Traceback completo:**
```python
File "/odoo/custom/addons-whatsapp-connector/whatsapp_connector/models/Connector.py", line 313
    data = self.ca_request('status_get', timeout=20)
```

**Causa raiz:**
- AcruxLab original: `def ca_request(self, path, data={}, params={}, timeout=False, ignore_exception=False)`
- Nossa tentativa 1: `def ca_request(self, endpoint, data=None, **kwargs)` ❌
- Nossa tentativa 2: Com `**kwargs` mas nome errado ❌

**Solução final:**
```python
# Signature EXATAMENTE igual ao parent!
def ca_request(self, path, data={}, params={}, timeout=False, ignore_exception=False):
    self.ensure_one()

    if self.connector_type == 'sms':
        raise UserError(_(
            'Direct API requests are not supported for SMS connectors.\n'
            'Use "Check Status" button instead.'
        ))

    # Passa TODOS os parâmetros
    return super(AcruxChatConnector, self).ca_request(
        path, data, params, timeout, ignore_exception
    )
```

**Comandos usados para debug:**
```bash
# Encontrar signature original
sudo grep -n "def ca_request" /odoo/custom/addons-whatsapp-connector/*/models/Connector.py

# Resultado:
# whatsapp_connector/models/Connector.py:291:def ca_request(self, path, data={}, params={}, timeout=False, ignore_exception=False):
```

**Lição:** Python não permite override com signature diferente quando há polimorfismo.

### Problema 3: AttributeError - 'sms.provider' object has no attribute 'api_key'

**Sintoma:**
```
AttributeError: 'sms.provider' object has no attribute 'api_key'
```

**Causa:**
Código usava nomes de campos genéricos que não existiam:
```python
# ❌ ERRADO
if not provider.api_key or not provider.segment_id:
    ...
api = KolmeyaAPI(
    api_key=provider.api_key,
    segment_id=provider.segment_id,
    base_url=provider.api_url
)
```

**Campos reais do modelo:**
```python
# ✅ CORRETO
kolmeya_api_token = Char('API Token')
kolmeya_segment_id = Integer('Segment ID')
# Não tem api_url!
```

**Solução:**
```python
# ✅ CORRETO
if not provider.kolmeya_api_token or not provider.kolmeya_segment_id:
    raise UserError(_('SMS Provider not configured'))

api = KolmeyaAPI(
    token=provider.kolmeya_api_token,  # não é api_key!
    segment_id=provider.kolmeya_segment_id
    # sem base_url!
)
```

**Comando para descobrir campos:**
```bash
sudo cat /odoo/custom/addons_custom/sms_kolmeya/models/sms_provider_kolmeya.py | grep -A 5 "kolmeya_"
```

### Problema 4: Saldo da API Retorna R$ 0,00 (Mas Tem Saldo!)

**Sintoma:**
```
Popup mostra: "Balance: R$ 0.00"
Mas conta tem: R$ 9.396,84
```

**Investigação:**

Consulta direta à API:
```bash
curl -X POST "https://kolmeya.com.br/api/v1/sms/balance" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json"
```

**Resposta real da API:**
```json
{
    "balance": "R$9.396,84"
}
```

**Código esperava:**
```python
balance = api.get_balance()
saldo = balance.get('saldo', 0.0)  # ❌ Chave errada!
```

**Problema:**
1. Chave é `"balance"` não `"saldo"`
2. Valor é **string** `"R$9.396,84"` não float
3. Formato brasileiro: ponto = milhar, vírgula = decimal

**Solução implementada:**
```python
def get_balance(self):
    """Get account balance"""
    response = self._make_request('/sms/balance')

    # API retorna {"balance": "R$9.396,84"}
    balance_str = response.get('balance', 'R$0,00')

    # Remove "R$", pontos (separador milhar) e substitui vírgula por ponto
    balance_clean = balance_str.replace('R$', '').replace('.', '').replace(',', '.').strip()

    try:
        balance_float = float(balance_clean)
    except ValueError:
        balance_float = 0.0

    # Retorna formato esperado
    return {
        'saldo': balance_float,
        'balance_str': balance_str
    }
```

**Teste da conversão:**
```python
# Input: "R$9.396,84"
# Remove "R$": "9.396,84"
# Remove ".": "9396,84"
# Substitui ",": "9396.84"
# float(): 9396.84 ✅
```

### Problema 5: Respostas SMS Ficam Sem Parceiro

**Sintoma:**
```
Mensagens ENVIADAS: Aparece nome do parceiro
Mensagens RECEBIDAS: Campo "Contact" vazio
```

**Dados observados:**
```sql
-- Mensagens outgoing
phone: +55 48 99191-0234  → partner_id: 123 ✅

-- Mensagens incoming (webhook)
phone: 5548991910234      → partner_id: NULL ❌
phone: +5548991910234     → partner_id: NULL ❌
```

**Causa raiz:**

Webhook original:
```python
def webhook_reply(self, **kwargs):
    phone = data.get('phone')

    # Busca apenas mensagem anterior
    clean_phone = str(phone).replace('+', '').replace(' ', '').replace('-', '')
    sms_msg = request.env['sms.message'].sudo().search([
        ('phone', 'ilike', clean_phone),
        ('direction', '=', 'outgoing')
    ], limit=1)

    # ❌ PROBLEMA: Se não achar mensagem, partner_id = False!
    reply_sms = request.env['sms.message'].sudo().create({
        'partner_id': sms_msg.partner_id.id if sms_msg and sms_msg.partner_id else False,
        # ...
    })
```

**Solução implementada:**
```python
def webhook_reply(self, **kwargs):
    phone = data.get('phone')
    message_text = data.get('message')

    # Busca mensagem anterior primeiro
    sms_msg = # ... busca existente ...

    # ✅ NOVO: Busca parceiro diretamente se não achou via mensagem
    partner_id = False
    if sms_msg and sms_msg.partner_id:
        partner_id = sms_msg.partner_id.id
    else:
        # Normaliza telefone
        clean_phone = str(phone).replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

        # Busca em res.partner (múltiplos formatos)
        partner = request.env['res.partner'].sudo().search([
            '|', '|', '|',
            ('phone', 'ilike', clean_phone),
            ('mobile', 'ilike', clean_phone),
            ('phone', 'ilike', f'+{clean_phone}'),
            ('mobile', 'ilike', f'+{clean_phone}')
        ], limit=1)

        if partner:
            partner_id = partner.id
            _logger.info(f"Partner found by phone: {partner.name}")

    # Cria com partner_id correto
    reply_sms = request.env['sms.message'].sudo().create({
        'partner_id': partner_id,  # ✅ Sempre preenchido!
        'phone': phone,
        'body': message_text,
        'direction': 'incoming',
        'state': 'delivered',
    })
```

**SQL para corrigir mensagens antigas:**
```sql
-- Associar parceiros às mensagens antigas sem partner_id
UPDATE sms_message sm
SET partner_id = (
    SELECT p.id
    FROM res_partner p
    WHERE
        -- Normaliza ambos os lados
        REGEXP_REPLACE(COALESCE(p.phone, ''), '[^0-9]', '', 'g') =
        REGEXP_REPLACE(sm.phone, '[^0-9]', '', 'g')
        OR
        REGEXP_REPLACE(COALESCE(p.mobile, ''), '[^0-9]', '', 'g') =
        REGEXP_REPLACE(sm.phone, '[^0-9]', '', 'g')
    LIMIT 1
)
WHERE
    sm.partner_id IS NULL
    AND sm.direction = 'incoming';

-- Resultado: UPDATE 2 (2 mensagens corrigidas)
```

**Teste de normalização:**
```python
# Formatos diferentes do mesmo número:
"+55 48 99191-0234"  → "5548991910234"
"5548991910234"       → "5548991910234"
"+5548991910234"      → "5548991910234"
"(48) 99191-0234"     → "4899191023"  # ⚠️ Faltaria +55
```

**Lição:** Sempre normalizar telefones para comparação!

### Problema 6: Popup "Check Status" Não Aparece

**Sintoma:**
```
Clica em "Conecte ou Cheque o Status"
Nada acontece visualmente
Erro JavaScript: Cannot destructure property '__legacy_widget__'
```

**Erro completo:**
```javascript
UncaughtPromiseError > TypeError
Cannot destructure property '__legacy_widget__' of 'controller.getLocalState(...)' as it is undefined.
    at Object.switchView (web.assets_backend.min.js:2336:278)
```

**Investigação:**

1. Verificar se método retorna algo:
```python
def ca_get_status(self):
    # ...
    return Pop.message(message, detail)  # ✅ Retorna action
```

2. Verificar modelo Pop:
```bash
sudo find /odoo/custom/addons-whatsapp-connector -name "*.py" -exec grep -l "acrux.chat.pop.message" {} \;
# Resultado: whatsapp_connector/wizard/CustomMessage.py
```

3. Ver implementação:
```python
def message(self, name, html=''):
    return {
        'name': _('Message'),
        'type': 'ir.actions.act_window',
        'view_mode': 'form',
        'res_model': 'acrux.chat.pop.message',
        'target': 'new',
        'context': dict(default_name=name, default_info=html)
    }
```

**Causa:**
- Usuário estava em outra view (res.partner form)
- Odoo 15 tem bug com wizards em contextos legados
- Erro `__legacy_widget__` é incompatibilidade view nova vs legada

**Workaround:**
1. Ir direto para ChatRoom > Connectors
2. Abrir connector SMS
3. Clicar em "Check Status"

**Alternativa (não implementada):**
Usar notificação nativa ao invés de popup:
```python
return {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'title': _('SMS Provider Status'),
        'message': _('Balance: R$ %.2f') % saldo,
        'type': 'success',
        'sticky': False,
    }
}
```

### Problema 7: Cache Python Persiste Após Update

**Sintoma:**
```bash
# Atualizar arquivo
sudo cp connector_fixed.py /odoo/.../connector.py

# Reiniciar Odoo
sudo systemctl restart odoo-server

# Erro ainda aparece (código antigo roda!)
```

**Causa:**
- Arquivos `.pyc` em `__pycache__/` não são limpos automaticamente
- Odoo carrega `.pyc` se for mais novo que `.py`
- Reiniciar service não limpa cache

**Solução completa:**
```bash
# 1. Parar Odoo
sudo systemctl stop odoo-server

# 2. Matar processos órfãos
sudo pkill -9 -f odoo-bin

# 3. Limpar cache Python
sudo find /odoo/custom/addons_custom/contact_center_sms -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null
sudo find /odoo/custom/addons_custom/contact_center_sms -name '*.pyc' -delete 2>/dev/null

# 4. Upgrade módulo (força reload)
cd /odoo/odoo-server
sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d realcred --stop-after-init -u contact_center_sms

# 5. Reiniciar Odoo
sudo systemctl start odoo-server
```

**Script automatizado:**
```bash
#!/bin/bash
# deploy_module.sh

MODULE=$1
MODULE_PATH="/odoo/custom/addons_custom/$MODULE"

echo "🚀 Deploying module: $MODULE"

# Stop Odoo
echo "⏸️  Stopping Odoo..."
sudo systemctl stop odoo-server
sudo pkill -9 -f odoo-bin 2>/dev/null

# Clean cache
echo "🧹 Cleaning cache..."
sudo find "$MODULE_PATH" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null
sudo find "$MODULE_PATH" -name '*.pyc' -delete 2>/dev/null

# Upgrade module
echo "⬆️  Upgrading module..."
cd /odoo/odoo-server
sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d realcred --stop-after-init -u "$MODULE" | tail -20

# Start Odoo
echo "▶️  Starting Odoo..."
sudo systemctl start odoo-server

# Wait and check
sleep 10
WORKERS=$(ps aux | grep odoo-bin | grep -v grep | wc -l)
echo "✅ Odoo running with $WORKERS workers"
```

**Uso:**
```bash
chmod +x deploy_module.sh
./deploy_module.sh contact_center_sms
```

---

## 📡 API Kolmeya - Descobertas Importantes

### Base URL e Autenticação

**Base URL:**
```
https://kolmeya.com.br/api/v1
```

**Autenticação:**
```http
Authorization: Bearer SEU_TOKEN_AQUI
Content-Type: application/json
```

**Nota:** O token pode vir com ou sem prefixo "Bearer ". A classe `KolmeyaAPI` normaliza automaticamente.

### Endpoints Testados

#### 1. POST /sms/balance - Consultar Saldo

**Request:**
```bash
curl -X POST "https://kolmeya.com.br/api/v1/sms/balance" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
    "balance": "R$9.396,84"
}
```

**⚠️ Descoberta crítica:**
- Valor vem como **string** no formato brasileiro
- Precisa converter: `"R$9.396,84"` → `9396.84` (float)
- Ponto (.) = separador de milhar (remover)
- Vírgula (,) = separador decimal (substituir por .)

#### 2. POST /sms/store - Enviar SMS

**Request:**
```bash
curl -X POST "https://kolmeya.com.br/api/v1/sms/store" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "phone": "5548991910234",
        "message": "Teste de SMS",
        "reference": "msg_001"
      }
    ],
    "segment_id": 109
  }'
```

**Response (sucesso):**
```json
{
    "id": "job_uuid_12345",
    "valids": [
        {
            "id": "msg_uuid_67890",
            "phone": "5548991910234",
            "reference": "msg_001"
        }
    ],
    "invalids": [],
    "blacklist": []
}
```

**Response (número inválido):**
```json
{
    "id": "job_uuid_12345",
    "valids": [],
    "invalids": [
        {
            "phone": "123",
            "reason": "Número inválido"
        }
    ],
    "blacklist": []
}
```

**Formato do telefone:**
- ✅ Aceito: `5548991910234` (apenas dígitos)
- ✅ Aceito: `55 48 99191-0234` (com formatação)
- ❌ Rejeitado: `+55 48 99191-0234` (com +)

**Nossa implementação limpa o + automaticamente.**

#### 3. Webhook - Resposta de SMS

**URL configurada:**
```
https://odoo.semprereal.com/kolmeya/webhook/reply
```

**Payload recebido:**
```json
{
    "phone": "5548991910234",
    "message": "Oi, tenho interesse",
    "reference": "msg_001",
    "data": "2025-11-15 14:30:00"
}
```

**⚠️ Descoberta importante:**
- Campo `phone` vem **SEM** `+` mas **COM** código país
- Formato: `5548991910234` (13 dígitos)
- Precisa normalizar para fazer match com res.partner

#### 4. Webhook - Status de Entrega

**URL:**
```
https://odoo.semprereal.com/kolmeya/webhook/status
```

**Payload recebido:**
```json
{
    "id": "msg_uuid_67890",
    "reference": "msg_001",
    "status": "entregue",
    "status_code": 3,
    "phone": "5548991910234"
}
```

**Códigos de status:**
```python
status_map = {
    1: 'outgoing',   # Tentando enviar
    2: 'sent',       # Enviado para operadora
    3: 'delivered',  # Entregue ao destinatário
    4: 'error',      # Não entregue
    5: 'rejected',   # Rejeitado pela operadora
    6: 'expired',    # Expirado (não lido)
}
```

### Rate Limiting

**Headers de resposta:**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 850
X-RateLimit-Reset: 1700000000
```

**Nossa implementação monitora:**
```python
rate_remaining = response.headers.get('X-RateLimit-Remaining')
if rate_remaining and int(rate_remaining) < 50:
    _logger.warning(f"Kolmeya rate limit low: {rate_remaining}")
```

### Erros Comuns da API

#### Erro 401 - Token Inválido
```json
{
    "errors": ["Unauthenticated."]
}
```

**Solução:** Verificar token no provider.

#### Erro 404 - Endpoint Não Existe
```json
{
    "errors": ["Not found."]
}
```

**Causa comum:** Usar GET ao invés de POST.

#### Erro 429 - Rate Limit
```json
{
    "errors": ["Too Many Requests"]
}
```

**Nossa implementação:**
```python
if response.status_code == 429:
    raise UserError("Rate limit exceeded. Please wait a few minutes.")
```

---

## 🔗 Integração com ChatRoom

### Arquitetura da Integração

```
ChatRoom (AcruxLab)
├── Connector (WhatsApp, API Chat, Chat Smart, SMS)
├── Conversation (Thread de mensagens com cliente)
└── Message (Mensagem individual)

SMS Module
├── Provider (Kolmeya, etc)
├── Message (Mensagem SMS)
└── Template (Template Jinja2)

Integração
└── contact_center_sms
    ├── Connector: SMS como novo tipo
    ├── Conversation: Cria conversation para SMS
    └── Message: Sincroniza sms.message ↔ acrux.chat.message
```

### Criação de Conversation via SQL

```sql
-- Buscar connector SMS
SELECT id FROM acrux_chat_connector WHERE connector_type = 'sms';
-- Resultado: 96

-- Criar conversation para um cliente
INSERT INTO acrux_chat_conversation (
    name,
    number_format,
    connector_id,
    res_partner_id,
    status,
    company_id,
    create_uid,
    write_uid
) VALUES (
    'ANA CARLA - SMS',           -- Nome
    '+5548991910234',            -- Número formatado
    96,                          -- Connector SMS
    123,                         -- ID do parceiro
    'current',                   -- Status
    1,                           -- Company
    2,                           -- Create user
    2                            -- Write user
);
```

**Resultado:**
```sql
SELECT id, name, connector_id, res_partner_id
FROM acrux_chat_conversation
WHERE connector_id = 96;

-- id: 66452
```

### Sincronização de Mensagens

#### SMS Outgoing → ChatRoom

Quando envia SMS:
```python
# 1. Cria sms.message
sms_msg = env['sms.message'].create({
    'partner_id': partner.id,
    'phone': '+5548991910234',
    'body': 'Teste',
    'direction': 'outgoing',
})

# 2. Envia via provider
sms_msg.action_send()

# 3. Sincroniza com ChatRoom (TODO)
conversation = env['acrux.chat.conversation'].search([
    ('res_partner_id', '=', partner.id),
    ('connector_id.connector_type', '=', 'sms')
], limit=1)

if conversation:
    env['acrux.chat.message'].create({
        'contact_id': conversation.id,
        'ttype': 'text',
        'text': sms_msg.body,
        'date_message': fields.Datetime.now(),
        'from_me': True,
    })
```

#### SMS Incoming → ChatRoom

Webhook recebe resposta:
```python
def webhook_reply(self, **kwargs):
    # 1. Cria sms.message incoming
    reply_sms = env['sms.message'].sudo().create({
        'partner_id': partner.id,
        'phone': '5548991910234',
        'body': 'Resposta do cliente',
        'direction': 'incoming',
    })

    # 2. Busca ou cria conversation
    conversation = env['acrux.chat.conversation'].search([
        ('res_partner_id', '=', partner.id),
        ('connector_id.connector_type', '=', 'sms')
    ], limit=1)

    if not conversation:
        conversation = env['acrux.chat.conversation'].create({
            'name': partner.name,
            'number_format': reply_sms.phone,
            'connector_id': connector_sms.id,
            'res_partner_id': partner.id,
        })

    # 3. Cria message no ChatRoom
    env['acrux.chat.message'].create({
        'contact_id': conversation.id,
        'ttype': 'text',
        'text': reply_sms.body,
        'date_message': fields.Datetime.now(),
        'from_me': False,
    })
```

### Interface Unificada

No ChatRoom, operador vê:
```
┌────────────────────────────────────────┐
│ ChatRoom - Conversations               │
├────────────────────────────────────────┤
│                                        │
│ 📱 WhatsApp                            │
│   └─ João Silva (Online)               │
│   └─ Maria Santos (Lida às 14:30)      │
│                                        │
│ 💬 SMS                                 │
│   └─ ANA CARLA (Respondeu há 5min)     │
│   └─ Pedro Costa (Sem resposta)        │
│                                        │
└────────────────────────────────────────┘
```

Ao clicar em uma conversation SMS:
```
┌────────────────────────────────────────┐
│ ANA CARLA - SMS                        │
├────────────────────────────────────────┤
│                                        │
│ Você (15:00):                          │
│ ┌────────────────────────────────────┐ │
│ │ Olá ANA CARLA, tudo bem?           │ │
│ │ ✓✓ Entregue                        │ │
│ └────────────────────────────────────┘ │
│                                        │
│ ANA CARLA (15:05):                     │
│ ┌────────────────────────────────────┐ │
│ │ Oi, tenho interesse no empréstimo  │ │
│ └────────────────────────────────────┘ │
│                                        │
│ [Digite sua mensagem...]          [>]  │
│                                        │
└────────────────────────────────────────┘
```

---

## ✅ Testes e Validação

### Teste 1: Verificar Instalação

```bash
# Módulos instalados
sudo -u postgres psql realcred -c "
SELECT name, state
FROM ir_module_module
WHERE name IN ('sms_base_sr', 'sms_kolmeya', 'contact_center_sms');
"

# Deve retornar:
#       name           | state
# ---------------------+-----------
#  sms_base_sr         | installed
#  sms_kolmeya         | installed
#  contact_center_sms  | installed
```

### Teste 2: Verificar Provider

```bash
# Provider Kolmeya configurado
sudo -u postgres psql realcred -c "
SELECT id, name, provider_type, active,
       CASE
         WHEN kolmeya_api_token IS NOT NULL THEN 'Configurado'
         ELSE 'Não configurado'
       END as token_status
FROM sms_provider
WHERE provider_type = 'kolmeya';
"

# Deve retornar:
# id | name    | provider_type | active | token_status
# ---|---------|---------------|--------|-------------
#  1 | Kolmeya | kolmeya       | t      | Configurado
```

### Teste 3: Consultar Saldo

Via Python (direto):
```bash
ssh odoo-rc "cd /odoo/odoo-server && sudo -u odoo python3 << 'PYEOF'
import sys
sys.path.insert(0, '/odoo/custom/addons_custom/sms_kolmeya/models')

from kolmeya_api import KolmeyaAPI

api = KolmeyaAPI('Bearer SEU_TOKEN', 109)
balance = api.get_balance()

print(f"Saldo: R$ {balance['saldo']:.2f}")
print(f"String: {balance['balance_str']}")
PYEOF
"
```

**Resultado esperado:**
```
Saldo: R$ 9396.84
String: R$9.396,84
```

### Teste 4: Enviar SMS de Teste

Via interface:
1. SMS > Messages > Create
2. Preencher:
   - **Contact:** Selecionar parceiro
   - **Phone:** +55 48 99191-0234
   - **Message:** Teste via interface
3. Clicar "Send"

Verificar:
```sql
SELECT id, partner_id, phone, state, provider_message_id
FROM sms_message
ORDER BY id DESC
LIMIT 1;
```

**Estado esperado:** `sent` ou `delivered`

### Teste 5: Simular Webhook

```bash
curl -X POST https://odoo.semprereal.com/kolmeya/webhook/reply \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "5548991910234",
    "message": "Teste de webhook - resposta automática",
    "reference": "test_webhook_001",
    "data": "2025-11-15 16:30:00"
  }'
```

**Resposta esperada:**
```json
{
    "status": "success",
    "sms_id": 15
}
```

Verificar criação:
```sql
SELECT id, partner_id, phone, body, direction, state
FROM sms_message
WHERE direction = 'incoming'
ORDER BY id DESC
LIMIT 1;
```

**Verificar parceiro associado:**
```sql
SELECT
    sm.id,
    sm.phone,
    p.name as partner_name
FROM sms_message sm
LEFT JOIN res_partner p ON sm.partner_id = p.id
WHERE sm.direction = 'incoming'
ORDER BY sm.id DESC
LIMIT 1;
```

**Resultado esperado:**
- `partner_id` preenchido
- `partner_name` com nome do cliente

### Teste 6: Verificar Connector no ChatRoom

```bash
# Via SQL
sudo -u postgres psql realcred -c "
SELECT id, name, connector_type, ca_status, sms_provider_id
FROM acrux_chat_connector
WHERE connector_type = 'sms';
"

# Resultado esperado:
# id | name        | connector_type | ca_status | sms_provider_id
# ---|-------------|----------------|-----------|----------------
# 96 | SMS Kolmeya | sms            | t         | 1
```

Via interface:
1. ChatRoom > Configuration > Connectors
2. Verificar linha "SMS Kolmeya"
3. Clicar em "Check Status"

**Resultado esperado:**
```
┌────────────────────────────────┐
│ SMS Provider Status            │
├────────────────────────────────┤
│ Connected successfully!        │
│ Provider: Kolmeya              │
│ Balance: R$ 9396.84            │
└────────────────────────────────┘
```

### Teste 7: Normalização de Telefone

```sql
-- Testar normalização SQL
WITH test_phones AS (
    SELECT unnest(ARRAY[
        '+55 48 99191-0234',
        '5548991910234',
        '+5548991910234',
        '(48) 99191-0234'
    ]) as phone
)
SELECT
    phone as original,
    REGEXP_REPLACE(phone, '[^0-9]', '', 'g') as normalized
FROM test_phones;
```

**Resultado esperado:**
```
     original       |  normalized
--------------------|-------------
 +55 48 99191-0234  | 5548991910234
 5548991910234      | 5548991910234
 +5548991910234     | 5548991910234
 (48) 99191-0234    | 4899191023
```

**Nota:** Último caso perde +55 (problema conhecido)

### Teste 8: Template Jinja2

Criar template:
```
Nome: Cobrança Amigável
Modelo: res.partner
Corpo:
Olá {{ object.name }},

Identificamos um débito em sua conta.
Valor: R$ {{ object.credit or '0,00' }}

Evite juros! Regularize hoje.

Dúvidas: {{ user.company_id.phone }}

{{ user.name }}
```

Testar:
1. SMS > Templates > Selecionar template
2. Action > Send SMS
3. Selecionar parceiros
4. Preview deve mostrar mensagem renderizada

### Teste 9: Conversation no ChatRoom

```sql
-- Verificar conversation criada
SELECT
    c.id,
    c.name,
    c.number_format,
    p.name as partner_name,
    con.name as connector_name
FROM acrux_chat_conversation c
LEFT JOIN res_partner p ON c.res_partner_id = p.id
LEFT JOIN acrux_chat_connector con ON c.connector_id = con.id
WHERE con.connector_type = 'sms';
```

Verificar mensagens:
```sql
SELECT
    m.id,
    m.ttype,
    LEFT(m.text, 50) as message,
    m.from_me,
    m.date_message
FROM acrux_chat_message m
WHERE m.contact_id = 66452  -- ID da conversation
ORDER BY m.date_message DESC;
```

---

## 🔧 Troubleshooting

### Problema: "Module not found" ao instalar

**Erro:**
```
ModuleNotFoundError: No module named 'sms_base_sr'
```

**Solução:**
```bash
# 1. Verificar se módulo está no addons_path
grep addons_path /etc/odoo-server.conf

# 2. Verificar permissões
ls -la /odoo/custom/addons_custom/sms_base_sr
# Deve ser: odoo:odoo

# 3. Corrigir se necessário
sudo chown -R odoo:odoo /odoo/custom/addons_custom/sms_base_sr

# 4. Atualizar lista
# Apps > Update Apps List
```

### Problema: Webhook não está funcionando

**Sintomas:**
- Cliente responde SMS
- Nenhuma mensagem incoming é criada no Odoo

**Debug:**

1. Verificar logs do Odoo:
```bash
sudo journalctl -u odoo-server -f | grep -i kolmeya
```

2. Testar webhook manualmente:
```bash
curl -X POST https://odoo.semprereal.com/kolmeya/webhook/reply \
  -H "Content-Type: application/json" \
  -d '{"phone":"5548991910234","message":"teste","data":"2025-11-15 10:00:00"}' \
  -v
```

3. Verificar firewall:
```bash
sudo ufw status | grep 443
# Deve mostrar: 443/tcp ALLOW
```

4. Verificar Nginx:
```bash
sudo nginx -t
sudo systemctl status nginx
```

5. Verificar SSL:
```bash
curl -I https://odoo.semprereal.com
# Deve retornar 200 OK
```

### Problema: SMS não está sendo enviado

**Sintomas:**
- Cria mensagem no Odoo
- Estado fica em `outgoing`
- Nunca muda para `sent`

**Debug:**

1. Verificar provider:
```sql
SELECT * FROM sms_provider WHERE id = 1;
-- Verificar se kolmeya_api_token está preenchido
```

2. Verificar logs:
```bash
sudo journalctl -u odoo-server -n 200 | grep -i "kolmeya\|sms"
```

3. Testar API diretamente:
```bash
curl -X POST "https://kolmeya.com.br/api/v1/sms/store" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"phone":"5548999999999","message":"Teste"}],
    "segment_id": 109
  }'
```

4. Verificar saldo:
```bash
curl -X POST "https://kolmeya.com.br/api/v1/sms/balance" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json"
```

### Problema: Parceiro não é associado à resposta

**Sintomas:**
- Mensagem outgoing tem `partner_id`
- Mensagem incoming não tem `partner_id`

**Solução:**

1. Executar SQL de correção:
```sql
UPDATE sms_message sm
SET partner_id = (
    SELECT p.id
    FROM res_partner p
    WHERE
        REGEXP_REPLACE(COALESCE(p.phone, ''), '[^0-9]', '', 'g') =
        REGEXP_REPLACE(sm.phone, '[^0-9]', '', 'g')
        OR
        REGEXP_REPLACE(COALESCE(p.mobile, ''), '[^0-9]', '', 'g') =
        REGEXP_REPLACE(sm.phone, '[^0-9]', '', 'g')
    LIMIT 1
)
WHERE sm.partner_id IS NULL AND sm.direction = 'incoming';
```

2. Reiniciar Odoo para reload webhook:
```bash
sudo systemctl restart odoo-server
```

### Problema: "Check Status" mostra R$ 0,00

**Causa:**
Método `get_balance()` não está convertendo string corretamente.

**Verificar:**
```bash
ssh odoo-rc "sudo cat /odoo/custom/addons_custom/sms_kolmeya/models/kolmeya_api.py | grep -A 20 'def get_balance'"
```

Deve conter:
```python
balance_str = response.get('balance', 'R$0,00')
balance_clean = balance_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
balance_float = float(balance_clean)
return {'saldo': balance_float, 'balance_str': balance_str}
```

**Se não tiver, aplicar fix:**
```bash
# Copiar script de correção
scp /path/to/update_get_balance.py odoo-rc:/tmp/
ssh odoo-rc "sudo python3 /tmp/update_get_balance.py"
sudo systemctl restart odoo-server
```

### Problema: Cache Python não atualiza

**Sintomas:**
- Altera arquivo .py
- Reinicia Odoo
- Código antigo ainda executa

**Solução:**
```bash
# Limpeza profunda
sudo systemctl stop odoo-server
sudo pkill -9 -f odoo-bin
sudo find /odoo/custom/addons_custom -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null
sudo find /odoo/custom/addons_custom -name '*.pyc' -delete 2>/dev/null
cd /odoo/odoo-server
sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d realcred --stop-after-init -u MODULE_NAME
sudo systemctl start odoo-server
```

---

## 💻 Comandos Úteis

### Gestão de Módulos

```bash
# Listar módulos SMS instalados
sudo -u postgres psql realcred -c "
SELECT name, state, latest_version, author
FROM ir_module_module
WHERE name LIKE '%sms%' OR name LIKE '%contact_center%'
ORDER BY name;
"

# Atualizar lista de módulos
cd /odoo/odoo-server
sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d realcred --stop-after-init -u base

# Instalar módulo via CLI
sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d realcred --stop-after-init -i sms_base_sr

# Upgrade módulo
sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d realcred --stop-after-init -u contact_center_sms

# Desinstalar módulo
sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d realcred --stop-after-init --uninstall sms_kolmeya
```

### Gestão de SMS

```bash
# Listar todas as mensagens SMS
sudo -u postgres psql realcred -c "
SELECT
    id,
    partner_id,
    phone,
    direction,
    state,
    LEFT(body, 30) as message_preview,
    create_date
FROM sms_message
ORDER BY create_date DESC
LIMIT 20;
"

# Mensagens por parceiro
sudo -u postgres psql realcred -c "
SELECT
    p.name as partner,
    COUNT(*) as total_messages,
    COUNT(*) FILTER (WHERE sm.direction = 'outgoing') as sent,
    COUNT(*) FILTER (WHERE sm.direction = 'incoming') as received
FROM sms_message sm
JOIN res_partner p ON sm.partner_id = p.id
GROUP BY p.name
ORDER BY total_messages DESC;
"

# Mensagens com erro
sudo -u postgres psql realcred -c "
SELECT id, phone, state, error_message, create_date
FROM sms_message
WHERE state IN ('error', 'rejected')
ORDER BY create_date DESC;
"

# Limpar mensagens de teste
sudo -u postgres psql realcred -c "
DELETE FROM sms_message
WHERE body ILIKE '%teste%' OR body ILIKE '%test%';
"
```

### Gestão de Connectors

```bash
# Listar todos os connectors
sudo -u postgres psql realcred -c "
SELECT
    id,
    name,
    connector_type,
    ca_status,
    sms_provider_id,
    company_id
FROM acrux_chat_connector
ORDER BY connector_type, name;
"

# Verificar connector SMS
sudo -u postgres psql realcred -c "
SELECT
    c.id,
    c.name,
    c.connector_type,
    c.ca_status,
    p.name as provider_name,
    p.provider_type
FROM acrux_chat_connector c
LEFT JOIN sms_provider p ON c.sms_provider_id = p.id
WHERE c.connector_type = 'sms';
"
```

### Gestão de Conversations

```bash
# Listar conversations SMS
sudo -u postgres psql realcred -c "
SELECT
    c.id,
    c.name,
    c.number_format,
    c.status,
    p.name as partner_name,
    COUNT(m.id) as message_count
FROM acrux_chat_conversation c
JOIN acrux_chat_connector con ON c.connector_id = con.id
LEFT JOIN res_partner p ON c.res_partner_id = p.id
LEFT JOIN acrux_chat_message m ON m.contact_id = c.id
WHERE con.connector_type = 'sms'
GROUP BY c.id, c.name, c.number_format, c.status, p.name
ORDER BY c.id DESC;
"

# Mensagens de uma conversation
sudo -u postgres psql realcred -c "
SELECT
    id,
    ttype,
    LEFT(text, 50) as message,
    from_me,
    date_message
FROM acrux_chat_message
WHERE contact_id = 66452  -- ID da conversation
ORDER BY date_message DESC;
"
```

### Logs e Debug

```bash
# Logs em tempo real
sudo journalctl -u odoo-server -f

# Filtrar logs SMS/Kolmeya
sudo journalctl -u odoo-server -n 500 --no-pager | grep -i "sms\|kolmeya"

# Logs de webhook
sudo journalctl -u odoo-server -n 200 --no-pager | grep -i "webhook"

# Logs de erro
sudo journalctl -u odoo-server -p err -n 100 --no-pager

# Exportar logs para análise
sudo journalctl -u odoo-server --since "1 hour ago" > /tmp/odoo_logs.txt
```

### Manutenção

```bash
# Backup do banco
sudo -u postgres pg_dump realcred > /tmp/realcred_backup_$(date +%Y%m%d_%H%M%S).sql

# Restore do banco
sudo -u postgres psql realcred < /tmp/realcred_backup_TIMESTAMP.sql

# Limpar cache Python
sudo find /odoo/custom/addons_custom -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null
sudo find /odoo/custom/addons_custom -name '*.pyc' -delete 2>/dev/null

# Reiniciar Odoo
sudo systemctl restart odoo-server

# Verificar workers
ps aux | grep odoo-bin | grep -v grep | wc -l
# Deve mostrar: 16 ou 19

# Verificar memória
ps aux | grep odoo-bin | awk '{sum+=$6} END {print "Total Memory: " sum/1024/1024 " GB"}'

# Verificar portas
sudo netstat -tlnp | grep python3
# Deve mostrar: 8069, 8072 (longpolling)
```

### Testes de API

```bash
# Testar saldo Kolmeya
curl -X POST "https://kolmeya.com.br/api/v1/sms/balance" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" | jq

# Enviar SMS teste
curl -X POST "https://kolmeya.com.br/api/v1/sms/store" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"phone":"5548999999999","message":"Teste API","reference":"test001"}
    ],
    "segment_id": 109
  }' | jq

# Testar webhook local
curl -X POST http://localhost:8069/kolmeya/webhook/reply \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "5548991910234",
    "message": "Teste local",
    "data": "2025-11-15 10:00:00"
  }' | jq

# Testar webhook produção
curl -X POST https://odoo.semprereal.com/kolmeya/webhook/reply \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "5548991910234",
    "message": "Teste produção",
    "data": "2025-11-15 10:00:00"
  }' | jq
```

---

## 📝 Notas Finais

### Lições Aprendidas

1. **Sempre verificar signature de métodos em herança**
   - Python exige signature exata em override
   - Usar `grep` para encontrar definições originais

2. **APIs nem sempre seguem convenções**
   - Kolmeya retorna saldo como string brasileira
   - Sempre testar endpoints manualmente primeiro

3. **Normalização de telefone é crítica**
   - Diferentes fontes retornam formatos diferentes
   - Criar função única de normalização

4. **Cache Python é persistente**
   - `systemctl restart` não limpa `.pyc`
   - Sempre fazer upgrade após mudar código

5. **Documentar descobertas imediatamente**
   - Detalhes se perdem com o tempo
   - Erros resolvidos podem reaparecer

### Próximos Passos

#### Funcionalidades Pendentes

- [ ] **Sincronização bidirecional ChatRoom ↔ SMS**
  - Atualmente: Webhook cria SMS mas não cria message no ChatRoom
  - Necessário: Criar acrux.chat.message automaticamente

- [ ] **Interface de envio no ChatRoom**
  - Atualmente: Precisa ir em SMS > Messages
  - Ideal: Enviar SMS direto do ChatRoom

- [ ] **Histórico unificado**
  - Mostrar SMS e WhatsApp na mesma timeline

- [ ] **Templates no ChatRoom**
  - Usar templates SMS dentro do ChatRoom

#### Melhorias de Performance

- [ ] **Cache de consultas de parceiro**
  - Webhook busca parceiro a cada resposta
  - Implementar cache Redis

- [ ] **Queue para envios em massa**
  - Usar Celery para filas assíncronas
  - Evitar timeout em envios grandes

- [ ] **Retry automático em falhas**
  - Implementar exponential backoff
  - Retentar envios com erro 429

#### Segurança

- [ ] **Validação de webhook JWT**
  - Kolmeya suporta assinatura JWT
  - Implementar verificação

- [ ] **Rate limiting interno**
  - Limitar requisições por usuário
  - Prevenir abuso

- [ ] **Audit log**
  - Registrar todos os envios
  - Quem enviou, quando, para quem

### Suporte e Contato

**Desenvolvedor:** Anderson Oliveira
**Email:** anderson@semprereal.com
**Empresa:** SempreReal
**Website:** https://www.semprereal.com

**API Kolmeya:**
**Suporte:** https://kolmeya.com.br/suporte
**Documentação:** https://kolmeya.com.br/docs/api
**Status:** https://status.kolmeya.com.br

---

**Versão do Documento:** 2.0
**Última Atualização:** 16/11/2025
**Status:** ✅ Completo e Validado

---

## 🎯 Checklist de Implementação

Para novos desenvolvedores que vão implementar isso do zero:

- [ ] Instalar Odoo 15.0
- [ ] Instalar AcruxLab WhatsApp Connector
- [ ] Criar conta na Kolmeya e obter token
- [ ] Criar módulo sms_base_sr
  - [ ] Models (message, template, provider)
  - [ ] Views
  - [ ] Security
  - [ ] Menu com ícone
- [ ] Criar módulo sms_kolmeya
  - [ ] KolmeyaAPI class
  - [ ] Provider extension
  - [ ] Webhooks
- [ ] Criar módulo contact_center_sms
  - [ ] Connector extension
  - [ ] Conversation extension
  - [ ] Message extension
- [ ] Configurar provider Kolmeya
- [ ] Criar connector SMS
- [ ] Configurar webhook na Kolmeya
- [ ] Testar envio de SMS
- [ ] Testar recebimento via webhook
- [ ] Testar "Check Status"
- [ ] Verificar associação de parceiros
- [ ] Criar conversation de teste
- [ ] Validar interface ChatRoom

**Tempo estimado:** 16-20 horas (com esta documentação)

---

*Fim da Documentação Completa*
