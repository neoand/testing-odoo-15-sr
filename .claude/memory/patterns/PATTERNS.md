# 🎨 Padrões e Boas Práticas Descobertas

> **Propósito:** Documentar padrões de código, soluções elegantes e boas práticas específicas deste projeto.

---

## 🏗️ Padrões Arquiteturais

### 1. Estrutura de Módulo Odoo

```
module_name/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── model_name.py
├── views/
│   ├── menu.xml
│   └── model_views.xml
├── security/
│   ├── security_groups.xml
│   ├── ir.model.access.csv
│   └── record_rules.xml
├── data/
│   └── data.xml
├── wizard/
│   ├── __init__.py
│   └── wizard_name.py
├── static/
│   ├── src/
│   │   ├── js/
│   │   ├── scss/
│   │   └── xml/
│   └── description/
│       ├── icon.png
│       └── index.html
└── tests/
    ├── __init__.py
    └── test_model.py
```

**Por que assim:**
- Organização clara
- Fácil navegação
- Padrão Odoo oficial
- Compatível com OCA

---

## 💻 Padrões de Código Python

### 1. Model Base Template

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class ModelName(models.Model):
    """Docstring descrevendo o modelo."""

    _name = 'module.model'
    _description = 'Descrição do Modelo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # ====== CAMPOS ======

    name = fields.Char(
        string='Nome',
        required=True,
        tracking=True,
        index=True,
        help='Nome principal'
    )

    active = fields.Boolean(
        string='Ativo',
        default=True
    )

    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('done', 'Concluído'),
    ], string='Status', default='draft', tracking=True)

    # ====== CONSTRAINTS ======

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Nome deve ser único!'),
    ]

    @api.constrains('field')
    def _check_field(self):
        for record in self:
            if not record.field:
                raise ValidationError(_('Validação falhou!'))

    # ====== COMPUTE ======

    @api.depends('field')
    def _compute_something(self):
        for record in self:
            record.computed_field = record.field * 2

    # ====== ONCHANGE ======

    @api.onchange('field')
    def _onchange_field(self):
        if self.field:
            self.other_field = self.field

    # ====== CRUD OVERRIDES ======

    @api.model
    def create(self, vals):
        # Lógica antes
        record = super(ModelName, self).create(vals)
        # Lógica depois
        return record

    def write(self, vals):
        # Lógica antes
        result = super(ModelName, self).write(vals)
        # Lógica depois
        return result

    def unlink(self):
        # Validações
        if self.filtered(lambda r: r.state != 'draft'):
            raise UserError(_('Não pode deletar registro confirmado!'))
        return super(ModelName, self).unlink()

    # ====== ACTIONS ======

    def action_confirm(self):
        """Confirma o registro."""
        self.ensure_one()
        self.write({'state': 'done'})
        self.message_post(body=_('Registro confirmado'))
        return True

    # ====== HELPERS ======

    def _helper_method(self):
        """Método auxiliar privado."""
        self.ensure_one()
        # Lógica
        pass
```

**Padrão:**
- Seções claramente demarcadas
- Ordem lógica (campos → constraints → compute → actions)
- Docstrings em português
- Logging adequado
- Type hints quando possível

---

### 2. Tratamento de Exceptions

```python
def send_sms(self):
    """Envia SMS com tratamento robusto de erros."""
    try:
        response = requests.post(
            url,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        _logger.error('Timeout sending SMS to %s', self.phone)
        raise UserError(_(
            'O serviço de SMS não respondeu a tempo. '
            'Por favor, tente novamente em alguns minutos.'
        ))

    except requests.exceptions.HTTPError as e:
        _logger.error('HTTP error sending SMS: %s', e)
        if e.response.status_code == 401:
            raise UserError(_('Credenciais inválidas. Contate o administrador.'))
        elif e.response.status_code == 429:
            raise UserError(_('Limite de SMS excedido. Aguarde antes de tentar novamente.'))
        else:
            raise UserError(_('Erro ao enviar SMS: %s') % str(e))

    except requests.exceptions.RequestException as e:
        _logger.exception('Unexpected error sending SMS')
        raise UserError(_('Erro inesperado: %s') % str(e))
```

**Padrão:**
- Exceptions específicas primeiro
- Logging adequado por severidade
- Mensagens amigáveis para usuário
- Informação técnica nos logs

---

### 3. Otimização de Performance

```python
# ❌ RUIM - N+1 queries
def bad_method(self):
    for record in self:
        partner_name = record.partner_id.name  # Query a cada iteração!
        print(partner_name)

# ✅ BOM - Single query
def good_method(self):
    # Opção 1: depends correto
    @api.depends('partner_id.name')
    def _compute_partner_name(self):
        for record in self:
            record.partner_name = record.partner_id.name  # Cached!

    # Opção 2: mapped
    partners = self.mapped('partner_id')  # Uma query só
    for partner in partners:
        print(partner.name)

    # Opção 3: read
    data = self.read(['partner_id'])  # Query otimizada
```

**Padrão:**
- Sempre usar `@api.depends` com campos relacionados completos
- Preferir `mapped()` a loops
- Usar `read()` quando só precisa de alguns campos
- Profile com pg_stat_statements

---

## 🎯 Padrões de Views XML

### 1. Form View Completa

```xml
<record id="view_model_form" model="ir.ui.view">
    <field name="name">model.model.form</field>
    <field name="model">module.model</field>
    <field name="arch" type="xml">
        <form string="Título">
            <!-- Header com ações e statusbar -->
            <header>
                <button name="action_confirm"
                        string="Confirmar"
                        type="object"
                        class="oe_highlight"
                        attrs="{'invisible': [('state', '!=', 'draft')]}"/>
                <field name="state" widget="statusbar"/>
            </header>

            <sheet>
                <!-- Button box -->
                <div class="oe_button_box" name="button_box">
                    <button name="toggle_active" type="object"
                            class="oe_stat_button" icon="fa-archive">
                        <field name="active" widget="boolean_button"/>
                    </button>
                </div>

                <!-- Título -->
                <div class="oe_title">
                    <h1><field name="name" placeholder="Nome..."/></h1>
                </div>

                <!-- Grupos -->
                <group>
                    <group name="left">
                        <field name="field1"/>
                        <field name="field2"/>
                    </group>
                    <group name="right">
                        <field name="field3"/>
                        <field name="field4"/>
                    </group>
                </group>

                <!-- Notebook -->
                <notebook>
                    <page string="Info" name="info">
                        <field name="description"/>
                    </page>
                </notebook>
            </sheet>

            <!-- Chatter -->
            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="activity_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

**Padrão:**
- Estrutura consistente: header → sheet → chatter
- Names em elementos para facilitar herança
- Button box para ações rápidas
- Groups de 2 colunas
- Notebook para conteúdo extenso

---

### 2. Tree View com Decorations

```xml
<record id="view_model_tree" model="ir.ui.view">
    <field name="name">model.model.tree</field>
    <field name="model">module.model</field>
    <field name="arch" type="xml">
        <tree string="Lista"
              decoration-muted="active == False"
              decoration-success="state == 'done'"
              decoration-danger="state == 'cancel'"
              decoration-info="state == 'draft'">
            <field name="name"/>
            <field name="partner_id"/>
            <field name="state"/>
            <field name="active" invisible="1"/>
        </tree>
    </field>
</record>
```

**Padrão:**
- Decorations para feedback visual
- Campos importantes visíveis
- Campos auxiliares com invisible="1"
- String descritivo

---

## 🔒 Padrões de Security

### 0. Record Rules - Padrão Correto ⭐ CRÍTICO

**Erro Comum que Bloqueia Tudo:**
```xml
<!-- ❌ ERRADO - Bloqueia TUDO -->
<record id="rule_name" model="ir.rule">
    <field name="name">Rule Name</field>
    <field name="model_id" ref="model_name"/>
    <field name="perm_read" eval="False"/>  <!-- BLOQUEIA - domain nunca é consultado! -->
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

**Padrão Correto:**
```xml
<!-- ✅ CORRETO - Permite + Filtra com domain -->
<record id="rule_name" model="ir.rule">
    <field name="name">Rule Description - Group Name Access</field>
    <field name="model_id" ref="model_name"/>
    <field name="perm_read" eval="True"/>      <!-- PERMITE leitura -->
    <field name="perm_write" eval="False"/>    <!-- Bloqueia escrita -->
    <field name="perm_create" eval="False"/>   <!-- Bloqueia criação -->
    <field name="perm_unlink" eval="False"/>   <!-- Bloqueia deleção -->
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

**Regra de Ouro:**
- Record rules SEMPRE têm `perm_read=True`
- O `domain_force` é que filtra quem vê o quê
- NUNCA use `perm_read=False` em rules com domain_force
- Bloqueie escrita/criação/deleção conforme necessário

**Por quê?**
```
Fluxo de Segurança Odoo:
1. Verifica access rights (ir.model.access.csv) → perm_read=1?
2. Verifica record rules (ir.rule)
   - Se perm_read=False → ❌ BLOQUEIA (domain não é consultado!)
   - Se perm_read=True → Aplica domain_force para filtrar (SQL WHERE)
   - Domain controla quem vê cada registro
```

**Exemplo Real:**
```xml
<!-- Domain: usuário vê APENAS seus próprios leads -->
<field name="domain_force">[('user_id', '=', user.id)]</field>

<!-- Sem perm_read=True, o domain nunca é executado! -->
<!-- Resultado: nada é visível para ninguém -->
```

---

### 1. Security Completo

```
security/
├── security_groups.xml    # Grupos
├── ir.model.access.csv    # Access rights
└── record_rules.xml       # Record rules
```

**security_groups.xml:**
```xml
<record id="group_custom_user" model="res.groups">
    <field name="name">Custom User</field>
    <field name="category_id" ref="base.module_category_custom"/>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
</record>
```

**ir.model.access.csv:**
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,model.user,model_module_model,base.group_user,1,1,1,0
access_model_manager,model.manager,model_module_model,base.group_system,1,1,1,1
```

**record_rules.xml (CORRETO):**
```xml
<record id="model_rule_own" model="ir.rule">
    <field name="name">Ver apenas próprios registros</field>
    <field name="model_id" ref="model_module_model"/>
    <field name="perm_read" eval="True"/>      <!-- ✅ Permite -->
    <field name="perm_write" eval="False"/>    <!-- Bloqueia -->
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

---

## 🧪 Padrões de Testes

```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestModel(TransactionCase):

    def setUp(self):
        super(TestModel, self).setUp()
        self.Model = self.env['module.model']
        self.record = self.Model.create({'name': 'Test'})

    def test_create(self):
        """Testa criação de registro."""
        record = self.Model.create({'name': 'Test 2'})
        self.assertTrue(record)
        self.assertEqual(record.name, 'Test 2')

    def test_constraint(self):
        """Testa constraint de validação."""
        with self.assertRaises(ValidationError):
            self.Model.create({'name': False})

    def test_compute(self):
        """Testa campo computado."""
        self.record.field = 10
        self.assertEqual(self.record.computed_field, 20)
```

---

## 📊 Padrões SQL

### Queries Complexas

```python
def _get_statistics(self):
    """Usa SQL direto quando ORM é insuficiente."""
    self.env.cr.execute("""
        SELECT
            user_id,
            COUNT(*) as count,
            SUM(amount) as total
        FROM crm_lead
        WHERE state = 'done'
        GROUP BY user_id
        ORDER BY total DESC
    """)
    return self.env.cr.dictfetchall()
```

**Quando usar SQL direto:**
- Agregações complexas
- Performance crítica
- Reports
- Bulk operations

**Cuidados:**
- SEMPRE sanitize inputs com `%s`
- NUNCA use string formatting
- Commit manual se necessário
- Documentar query

---

## 🎯 Anti-Patterns (Evitar!)

### ❌ Não Fazer

```python
# 1. String formatting em queries (SQL INJECTION!)
self.env.cr.execute(f"SELECT * FROM table WHERE id = {user_input}")

# 2. Commit desnecessário
self.env.cr.commit()  # Odoo gerencia isso!

# 3. Browse sem necessidade
for id in ids:
    record = self.browse(id)  # Lento!

# 4. Search sem limit
all_records = self.env['huge.model'].search([])  # OOM!

# 5. Compute sem store para campos muito usados
@api.depends('partner_id')
def _compute_partner_name(self):  # Calculado sempre!
    ...
```

### ✅ Fazer

```python
# 1. Use %s para parâmetros
self.env.cr.execute("SELECT * FROM table WHERE id = %s", (user_input,))

# 2. Deixe Odoo gerenciar transactions

# 3. Browse de uma vez
records = self.browse(ids)

# 4. Use limit
records = self.env['huge.model'].search([], limit=1000)

# 5. Store quando fizer sentido
@api.depends('partner_id.name')
def _compute_partner_name(self):
    ...
partner_name = fields.Char(compute='_compute_partner_name', store=True)
```

---

## 🌐 Padrões de Troubleshooting de Rede

### 1. Serviço Não Acessível Externamente - Checklist Sistemático

**Problema:** Serviço (Odoo, Nginx, etc.) roda mas não aceita conexões externas

**Checklist em Ordem (camada por camada):**

```bash
# ====== CAMADA 1: Processo Rodando? ======
ps aux | grep PROCESSO | grep -v grep
# ✅ Se vazio: processo parado - iniciar
# ✅ Se mostra: processo rodando - ir para camada 2

# ====== CAMADA 2: Porta Escutando? ======
sudo ss -tlnp | grep PORTA
# ✅ Se vazio: processo não escuta nessa porta - verificar config
# ✅ Se mostra: porta escutando - ir para camada 3

# ====== CAMADA 3: Interface Correta? ======
sudo ss -tlnp | grep PORTA | grep -E '0.0.0.0|127.0.0.1'
# ✅ 0.0.0.0:PORTA → Aceita externo ✅
# ❌ 127.0.0.1:PORTA → Apenas localhost ❌
# Se 127.0.0.1 e precisa externo: mudar config (http_interface, etc)

# ====== CAMADA 4: Teste Interno ======
curl -I http://localhost:PORTA
# ✅ Se responde: serviço OK internamente - ir para camada 5
# ❌ Se falha: problema na aplicação - verificar logs

# ====== CAMADA 5: Firewall Local (iptables) ======
sudo iptables -L -n | grep PORTA
# Verificar se há regra DROP/REJECT bloqueando porta

# ====== CAMADA 6: Firewall Cloud (GCP/AWS/Azure) ======
# GCP:
gcloud compute firewall-rules list --filter="tcp:PORTA"
# ✅ Se vazio: sem regra - criar regra
# ✅ Se mostra: regra existe - verificar target-tags

# ====== CAMADA 7: Teste Externo ======
curl -I http://IP_EXTERNO:PORTA
# ✅ Se responde: TUDO OK! ✅
# ❌ Se falha: voltar camadas 5-6
```

**Pattern Geral:**
```
Processo → Porta → Interface → Teste Interno → Firewall Local → Firewall Cloud → Teste Externo
```

**Ferramentas Chave:**
- `ps aux` - verificar processo
- `ss -tlnp` / `netstat -tlnp` - verificar porta e interface
- `curl -I` - testar conectividade HTTP
- `iptables -L` - firewall local
- `gcloud compute firewall-rules` - firewall cloud (GCP)

---

### 2. Odoo http_interface - Quando Usar Cada Opção

**Configuração:** `/etc/odoo-server.conf` → `http_interface`

**Opção 1: http_interface = 127.0.0.1** (Apenas Localhost)
```
Odoo escuta: 127.0.0.1:8069
Aceita conexões de: APENAS localhost
Uso: Quando Nginx/Apache faz reverse proxy
```

**Fluxo:**
```
Internet → Nginx (443) → localhost:8069 (Odoo) ✅
Internet → 8069 (Odoo) ❌ Bloqueado
```

**Quando usar:**
- ✅ Produção com reverse proxy (Nginx/Apache)
- ✅ SSL/HTTPS via Nginx
- ✅ Load balancing
- ✅ Cache estático
- ✅ **Segurança:** Odoo não exposto diretamente

**Opção 2: http_interface = 0.0.0.0** (Todas Interfaces)
```
Odoo escuta: 0.0.0.0:8069
Aceita conexões de: localhost + rede externa
Uso: Acesso direto ou testing
```

**Fluxo:**
```
Internet → 8069 (Odoo) ✅ Direto
localhost → 8069 (Odoo) ✅ Também funciona
```

**Quando usar:**
- ✅ Ambiente de testing/development
- ✅ Prototipagem rápida
- ✅ Quando não há reverse proxy
- ⚠️ **Atenção:** Odoo exposto diretamente (usar firewall!)

**Opção 3: http_interface = IP_ESPECÍFICO** (Uma Interface)
```
Odoo escuta: 10.0.0.5:8069
Aceita conexões de: Apenas rede do IP específico
Uso: Casos avançados (multi-network)
```

**Decisão Rápida:**
```
Tem Nginx/Apache? → 127.0.0.1 (localhost)
Acesso direto? → 0.0.0.0 (todas interfaces)
Multi-network? → IP específico
```

**CRÍTICO:** Após mudar `http_interface`, SEMPRE:
```bash
sudo pkill -9 -f 'odoo-bin'  # Matar processos antigos
sudo -u odoo python3 ./odoo-bin -c /etc/odoo-server.conf &
sudo ss -tlnp | grep 8069  # Validar nova interface
```

---

### 3. GCP Firewall - Pattern de Criação

**Estrutura de Comando:**
```bash
gcloud compute firewall-rules create RULE_NAME \
  --project=PROJECT_ID \           # Projeto GCP
  --direction=INGRESS \            # Entrada (INGRESS) ou Saída (EGRESS)
  --priority=1000 \                # 0-65535 (menor = maior prioridade)
  --network=default \              # Rede (geralmente 'default')
  --action=ALLOW \                 # ALLOW ou DENY
  --rules=tcp:PORTA \              # tcp:80, udp:53, etc
  --source-ranges=0.0.0.0/0 \      # 0.0.0.0/0 = qualquer IP
  --target-tags=TAG \              # Tag da instância alvo
  --description="Description"
```

**Exemplo Real:**
```bash
gcloud compute firewall-rules create allow-odoo-8069 \
  --project=webserver-258516 \
  --direction=INGRESS \
  --priority=1000 \
  --network=default \
  --action=ALLOW \
  --rules=tcp:8069 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=http-server \
  --description="Allow Odoo direct access on port 8069"
```

**Validação:**
```bash
# 1. Verificar regra criada
gcloud compute firewall-rules list --filter="name=allow-odoo-8069"

# 2. Verificar se instância tem a tag
gcloud compute instances describe INSTANCE \
  --zone=ZONE \
  --format="value(tags.items)"
# Output deve conter: http-server
```

**Pattern Comum - Portas Web:**
```bash
# HTTP (80)
--rules=tcp:80 --target-tags=http-server

# HTTPS (443)
--rules=tcp:443 --target-tags=https-server

# Odoo direto (8069)
--rules=tcp:8069 --target-tags=http-server

# Odoo longpolling (8072)
--rules=tcp:8072 --target-tags=http-server

# PostgreSQL (5432) - CUIDADO: restringir source-ranges!
--rules=tcp:5432 --source-ranges=10.0.0.0/8

# SSH (22) - Geralmente já existe regra default
--rules=tcp:22
```

**Segurança - source-ranges:**
```bash
# ⚠️ PÚBLICO (todos IPs):
--source-ranges=0.0.0.0/0

# ✅ RESTRITO (apenas escritório):
--source-ranges=203.0.113.0/24

# ✅ MÚLTIPLOS RANGES:
--source-ranges=203.0.113.0/24,198.51.100.0/24

# ✅ REDE INTERNA:
--source-ranges=10.0.0.0/8
```

---

## 🛠️ Pattern Cheatsheet - Comandos Rápidos

### Odoo Troubleshooting One-Liner

```bash
# Diagnóstico completo de acessibilidade
echo "1. Processo:" && ps aux | grep odoo-bin | grep -v grep | wc -l && \
echo "2. Porta:" && sudo ss -tlnp | grep 8069 && \
echo "3. Config:" && sudo grep http_interface /etc/odoo-server.conf && \
echo "4. Teste:" && curl -I http://localhost:8069
```

### GCP Firewall One-Liner

```bash
# Verificar completo para uma porta
gcloud compute firewall-rules list --filter="tcp:8069" --format="table(name,allowed,targetTags)" && \
gcloud compute instances describe odoo-sr-tensting --zone=southamerica-east1-b --format="value(tags.items)"
```

---

**Última atualização:** 2025-11-18
**Contribuir:** Adicione novos padrões conforme descobertos!
