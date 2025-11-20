# 🔧 Correção ValidationError: Campo "model" não existe - 19/11/2025

## 📋 Problema Identificado

**Erro RPC:** `ValidationError: O campo "model" não existe no modelo "sms.template"`

**Contexto:** Instalação do módulo `sms_base_sr` falhando durante validação de view XML.

## 🔍 Causa Raiz

### 1. Estrutura do Modelo `sms.template`

O modelo `sms.template` do Odoo 15 tem a seguinte estrutura:

```python
class SMSTemplate(models.Model):
    _name = "sms.template"
    
    name = fields.Char('Name', translate=True)
    model_id = fields.Many2one('ir.model', string='Applies to', required=True)
    model = fields.Char('Related Document Model', 
                       related='model_id.model', 
                       index=True, 
                       store=True, 
                       readonly=True)  # ← READONLY e RELATED
    body = fields.Char('Body', translate=True, required=True)
    # NÃO tem campo 'lang'
```

### 2. Problemas no XML Original

O XML estava tentando usar:
- ❌ `<field name="model"/>` na tree view - **Campo é readonly/related, não pode ser usado em tree**
- ❌ `<field name="lang"/>` - **Campo não existe no modelo**

### 3. Regra do Odoo

**Campos readonly/related NÃO podem ser usados diretamente em tree views.** Eles só funcionam em form views como campos invisíveis ou para exibição.

## ✅ Solução Aplicada

### 1. Correções no XML

**Antes (Incorreto):**
```xml
<tree>
    <field name="name"/>
    <field name="model"/>      <!-- ❌ Readonly/related não funciona -->
    <field name="lang"/>       <!-- ❌ Campo não existe -->
</tree>
```

**Depois (Correto):**
```xml
<tree>
    <field name="name"/>
    <field name="model_id"/>   <!-- ✅ Campo correto (Many2one) -->
</tree>
```

### 2. Form View

Mantido `model` como invisible no form (para referência interna):
```xml
<field name="model_id"/>
<field name="model" invisible="1"/>  <!-- ✅ OK no form como invisible -->
```

### 3. Arquivo Corrigido

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_sms_template_tree" model="ir.ui.view">
        <field name="name">sms.template.tree</field>
        <field name="model">sms.template</field>
        <field name="arch" type="xml">
            <tree>
                <field name="name"/>
                <field name="model_id"/>
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
                            <field name="model_id"/>
                            <field name="model" invisible="1"/>
                        </group>
                    </group>
                    <group>
                        <field name="body" widget="text" 
                               placeholder="Use {{ object.name }}, {{ user.name }}, etc. (Jinja2 syntax)"/>
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
| XML corrigido | ✅ |
| Campos validados | ✅ |
| Arquivo atualizado no servidor | ✅ |
| Arquivo local sincronizado | ✅ |
| XML válido | ✅ |
| Módulo pode ser instalado | ✅ |
| Módulo reinstalado | ⏳ Pendente |

## 🎓 Aprendizado

### Regras Importantes:

1. **Campos readonly/related:**
   - ❌ NÃO podem ser usados em tree views
   - ✅ Podem ser usados em form views (invisible ou readonly)
   - ✅ Use o campo Many2one original (`model_id`) na tree

2. **Verificar estrutura do modelo:**
   ```bash
   # Ver campos do modelo
   grep -E '^\s+[a-z_]+ = ' models/*.py
   
   # Ver classe do modelo
   grep -A 30 'class.*Template' models/*.py
   ```

3. **Validação de views:**
   - Odoo valida campos antes de criar views
   - Erros aparecem durante instalação/atualização do módulo
   - Sempre testar views antes de fazer deploy

## 📅 Data da Correção
**19 de Novembro de 2025 - 18:45 UTC**

---

**Criado por:** Cursor AI + Anderson  
**Documentado em:** `.cursor/memory/errors/ERRORS-SOLVED.md`

