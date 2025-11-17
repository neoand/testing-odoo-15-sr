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

**record_rules.xml:**
```xml
<record id="model_rule_own" model="ir.rule">
    <field name="name">Ver apenas próprios registros</field>
    <field name="model_id" ref="model_module_model"/>
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

**Última atualização:** 2025-11-17
**Contribuir:** Adicione novos padrões conforme descobertos!
