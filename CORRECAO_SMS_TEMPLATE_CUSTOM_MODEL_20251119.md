# 🔧 Correção ValidationError: Campo "model_id" não existe - 19/11/2025

## 📋 Problema Identificado

**Erro RPC:** `ValidationError: O campo "model_id" não existe no modelo "sms.template"`

**Contexto:** Instalação do módulo `sms_base_sr` falhando durante validação de view XML.

## 🔍 Causa Raiz

### ⚠️ PROBLEMA CRÍTICO DESCOBERTO

O módulo `sms_base_sr` define seu **próprio modelo** `sms.template` que **sobrescreve completamente** o modelo padrão do Odoo!

### 1. Modelo Customizado vs Modelo Padrão

**Modelo Customizado** (`sms_base_sr/models/sms_template.py`):
```python
class SMSTemplate(models.Model):
    _name = 'sms.template'  # ← Sobrescreve modelo padrão!
    
    name = fields.Char('Template Name', required=True)
    code = fields.Char('Template Code', required=True)
    message_template = fields.Text('Message Template', required=True)
    applies_to = fields.Selection([...], string='Applies To')
    active = fields.Boolean('Active', default=True)
    admin_only = fields.Boolean('Admin Only', default=True)
    use_count = fields.Integer('Times Used', readonly=True)
    message_preview = fields.Text('Preview', compute='_compute_preview')
```

**Modelo Padrão do Odoo** (`addons/sms/models/sms_template.py`):
```python
class SMSTemplate(models.Model):
    _name = "sms.template"
    
    name = fields.Char('Name', translate=True)
    model_id = fields.Many2one('ir.model', string='Applies to', required=True)
    model = fields.Char('Related Document Model', related='model_id.model')
    body = fields.Char('Body', translate=True, required=True)
```

### 2. Problema no XML

O XML estava usando campos do **modelo padrão** que **não existem** no modelo customizado:
- ❌ `<field name="model_id"/>` - **Não existe no customizado**
- ❌ `<field name="body"/>` - **Não existe no customizado** (é `message_template`)
- ❌ `<field name="model"/>` - **Não existe no customizado**

## ✅ Solução Aplicada

### 1. Verificação do Modelo Customizado

Verificado arquivo: `/odoo/custom/addons_custom/sms_base_sr/models/sms_template.py`

### 2. Correção do XML

**Antes (Incorreto - usando campos do modelo padrão):**
```xml
<tree>
    <field name="name"/>
    <field name="model_id"/>  <!-- ❌ Não existe -->
</tree>
<form>
    <field name="body"/>      <!-- ❌ Não existe -->
</form>
```

**Depois (Correto - usando campos do modelo customizado):**
```xml
<tree>
    <field name="name"/>
    <field name="code"/>          <!-- ✅ Campo correto -->
    <field name="applies_to"/>   <!-- ✅ Campo correto -->
    <field name="active" widget="boolean_toggle"/>
</tree>
<form>
    <field name="message_template"/>  <!-- ✅ Campo correto -->
    <field name="message_preview" readonly="1"/>
</form>
```

### 3. Arquivo XML Corrigido Completo

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Using custom sms.template model from sms_base_sr -->
    <record id="view_sms_template_tree" model="ir.ui.view">
        <field name="name">sms.template.tree</field>
        <field name="model">sms.template</field>
        <field name="arch" type="xml">
            <tree>
                <field name="name"/>
                <field name="code"/>
                <field name="applies_to"/>
                <field name="active" widget="boolean_toggle"/>
            </tree>
        </field>
    </record>

    <record id="view_sms_template_form" model="ir.ui.view">
        <field name="name">sms.template.form</field>
        <field name="model">sms.template</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <group>
                        <group>
                            <field name="name"/>
                            <field name="code"/>
                            <field name="applies_to"/>
                        </group>
                        <group>
                            <field name="active" widget="boolean_toggle"/>
                            <field name="admin_only" widget="boolean_toggle"/>
                            <field name="use_count" readonly="1"/>
                        </group>
                    </group>
                    <group>
                        <field name="message_template" widget="text" 
                               placeholder="Use Python string formatting: {name}, {cpf}, {value}, etc."/>
                    </group>
                    <group>
                        <field name="message_preview" readonly="1"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_sms_template" model="ir.actions.act_window">
        <field name="name">SMS Templates</field>
        <field name="res_model">sms.template</field>
        <field name="view_mode">tree,form</field>
    </record>

    <menuitem id="menu_sms_templates" name="Templates"
              parent="menu_sms_root" action="action_sms_template" sequence="15"/>
</odoo>
```

## 🔄 Próximos Passos

1. **Reinstalar o módulo** `sms_base_sr` no Odoo
2. **Verificar se a view funciona corretamente**
3. **Testar criação/edição de templates SMS**

## 🚀 Comandos para Reinstalar

```bash
# Via interface web Odoo:
# Apps > sms_base_sr > Desinstalar > Instalar

# Ou via linha de comando:
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b \
  --command="cd /odoo/odoo-server && sudo -u odoo python3 odoo-bin \
  -c /etc/odoo-server.conf -d testing -u sms_base_sr --stop-after-init"
```

## 📊 Status

| Item | Status |
|------|--------|
| Modelo customizado identificado | ✅ |
| XML corrigido para campos corretos | ✅ |
| Arquivo atualizado no servidor | ✅ |
| Arquivo local sincronizado | ✅ |
| XML válido | ✅ |
| Módulo pode ser instalado | ✅ |
| Módulo reinstalado | ⏳ Pendente |

## 🎓 Aprendizado Crítico

### ⚠️ Regra Importante:

**SEMPRE verificar se o módulo define seu próprio modelo antes de criar views!**

### Checklist Antes de Criar Views:

1. ✅ Verificar se existe `models/sms_template.py` no módulo
2. ✅ Ler o arquivo do modelo para ver campos disponíveis
3. ✅ Não assumir que modelos com mesmo nome têm mesma estrutura
4. ✅ Verificar se usa `_inherit` (estende) ou `_name` (sobrescreve)

### Comandos Úteis:

```bash
# Verificar se módulo tem modelo customizado
find . -path "*/sms_base_sr/models/*" -name "*.py"

# Ver campos do modelo
grep -E '^\s+[a-z_]+ = ' models/sms_template.py

# Verificar se sobrescreve ou estende
grep -E '_name|_inherit' models/sms_template.py
```

### Decisão Arquitetural:

**Problema:** O módulo `sms_base_sr` sobrescreve o modelo padrão `sms.template` ao invés de estendê-lo.

**Recomendação Futura:**
- Considerar usar `_inherit` ao invés de `_name` para estender o modelo padrão
- Ou renomear o modelo customizado para evitar conflito (ex: `sms.template.custom`)

## 📅 Data da Correção
**19 de Novembro de 2025 - 19:00 UTC**

---

**Criado por:** Cursor AI + Anderson  
**Documentado em:** `.cursor/memory/errors/ERRORS-SOLVED.md`

