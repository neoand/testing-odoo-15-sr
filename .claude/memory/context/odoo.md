# 🎓 Conhecimento Odoo 15 - Específico do Projeto

## Patterns Odoo Usados

### Models
- Herança por `_inherit` para estender models existentes
- `_name` para criar novos models
- `_description` sempre obrigatório
- `_order` para ordenação default
- `_rec_name` para display_name customizado

### Campos Especiais
- `active` - Soft delete
- `sequence` - Ordenação manual
- `company_id` - Multi-company
- `create_date`, `create_uid` - Automático
- `write_date`, `write_uid` - Automático

### Decoradores Importantes
- `@api.depends()` - Compute fields
- `@api.onchange()` - Onchange client-side
- `@api.constrains()` - Validações
- `@api.model` - Método de classe
- `@api.model_create_multi` - Batch create

### Security Layers

#### 1. Access Rights (ir.model.access.csv)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_crm_lead_user,crm.lead.user,model_crm_lead,sales_team.group_sale_salesman,1,1,1,0
```

#### 2. Record Rules (XML)
```xml
<record id="rule_name" model="ir.rule">
    <field name="name">Rule Name</field>
    <field name="model_id" ref="model_crm_lead"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

#### 3. Field-Level Security
- `groups="base.group_system"`
- `groups="sales_team.group_sale_manager"`

### ORM Methods

#### Search
```python
# Básico
records = self.env['model.name'].search([('field', '=', value)])

# Com limite e ordem
records = self.env['model.name'].search([...], limit=10, order='name')

# Count
count = self.env['model.name'].search_count([...])

# Apenas IDs
ids = self.env['model.name'].search([...])._ids
```

#### Create
```python
# Single
record = self.env['model.name'].create({'field': value})

# Multi (Odoo 15+)
records = self.env['model.name'].create([{'field': 1}, {'field': 2}])
```

#### Write
```python
records.write({'field': new_value})
```

#### Unlink
```python
records.unlink()
```

### Domínios Complexos

```python
# AND (default)
[('field1', '=', value1), ('field2', '=', value2)]

# OR
['|', ('field1', '=', value1), ('field2', '=', value2)]

# NOT
['!', ('field', '=', value)]

# IN
[('field', 'in', [1, 2, 3])]

# LIKE
[('name', 'ilike', 'search%')]

# Related field
[('partner_id.country_id.code', '=', 'BR')]
```

### Chatter (Mail Thread)

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    field = fields.Char(tracking=True)  # Tracking changes

    def action(self):
        self.message_post(
            body="Message",
            subject="Subject",
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )
```

### Computed Fields

```python
@api.depends('line_ids.price')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('price'))
```

### Constraints

```python
# SQL
_sql_constraints = [
    ('name_unique', 'UNIQUE(name)', 'Name must be unique!'),
]

# Python
@api.constrains('age')
def _check_age(self):
    for record in self:
        if record.age < 18:
            raise ValidationError('Must be 18+')
```

### Wizards

- Usar `models.TransientModel`
- Cleanup automático após 1h
- Bom para ações multi-step

### Ações do Servidor

```python
def action_confirm(self):
    self.ensure_one()  # Garante single record
    self.write({'state': 'confirmed'})
    return True  # ou {'type': 'ir.actions.act_window', ...}
```

### QWeb (Reports/Views)

```xml
<t t-foreach="docs" t-as="doc">
    <span t-field="doc.name"/>
    <span t-esc="doc.amount"/>
    <t t-if="doc.active">Active</t>
</t>
```

### JavaScript (Odoo 15)

```javascript
odoo.define('module.name', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');

    var MyField = AbstractField.extend({
        // Implementation
    });

    return MyField;
});
```

## Problemas Comuns e Soluções

### 1. N+1 Queries
❌ BAD:
```python
for record in records:
    print(record.partner_id.name)  # Query cada vez!
```

✅ GOOD:
```python
records = records.with_prefetch()  # ou
partners = records.mapped('partner_id')  # Fetch all at once
```

### 2. Missing Dependencies
- Sempre adicionar módulos necessários em `depends` do manifest

### 3. Cache Issues
```python
self.invalidate_cache()  # Limpar cache
self.env.cr.commit()     # Commit (cuidado!)
```

### 4. Translations
```python
from odoo import _

raise UserError(_('Message to translate'))
```

## Best Practices

1. **Use `self.ensure_one()`** em métodos que operam em single record
2. **Prefira `mapped()`** a loops quando possível
3. **Use `sudo()` com cuidado** - sempre verificar segurança
4. **Documente código complexo** em português
5. **Teste com diferentes perfis** de usuário
6. **Use `_logger`** para debug, não print()
7. **Valide inputs** sempre
8. **Sanitize HTML** em campos text/html

---

**Última atualização:** 2025-11-17
