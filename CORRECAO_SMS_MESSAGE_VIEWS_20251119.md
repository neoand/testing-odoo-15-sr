# 🔧 Correção: sms_message_views.xml - Campos inexistentes

> **Data:** 2025-11-19
> **Erro:** `O campo "provider_id" não existe no modelo "sms.message"`

---

## 📋 Problema Identificado

**Erro RPC:** A view `sms_message_views.xml` estava tentando usar campos que não existem no modelo `sms.message`.

**Sintoma:**
```
ValidationError: O campo "provider_id" não existe no modelo "sms.message"
```

**Campos problemáticos:**
- `provider_id` - Não existe
- `cost` - Não existe
- `segments` - Não existe
- `delivery_date` - Não existe
- `template_id` - Não existe
- `retry_count` - Não existe

---

## 🔍 Causa Raiz

### Modelo Simplificado vs View Completa

**Problema:** O modelo `sms.message` é uma **versão simplificada** que não tem todos os campos que a view estava tentando usar.

**Campos disponíveis no modelo:**
```python
# Campos básicos
phone = fields.Char(...)
body = fields.Text(...)
state = fields.Selection([...])

# Relacionamentos
partner_id = fields.Many2one('res.partner', ...)
user_id = fields.Many2one('res.users', ...)

# Campos de controle
sent_date = fields.Datetime(...)
error_message = fields.Text(...)
external_id = fields.Char(...)
```

**Campos que a view tentava usar (mas não existem):**
- ❌ `provider_id` - Provider usado para envio
- ❌ `cost` - Custo do SMS
- ❌ `segments` - Segmentos da mensagem
- ❌ `delivery_date` - Data de entrega
- ❌ `template_id` - Template usado
- ❌ `retry_count` - Contador de tentativas

---

## ✅ Solução Aplicada

### Remover Campos Inexistentes da View

**Mudanças na Tree View:**
```xml
<!-- Antes (Incorreto) -->
<tree>
    <field name="phone"/>
    <field name="partner_id"/>
    <field name="body"/>
    <field name="state"/>
    <field name="provider_id"/>  <!-- ← Não existe -->
    <field name="cost"/>          <!-- ← Não existe -->
    <field name="create_date"/>
</tree>

<!-- Depois (Correto) -->
<tree>
    <field name="phone"/>
    <field name="partner_id"/>
    <field name="body"/>
    <field name="state"/>
    <field name="user_id"/>       <!-- ← Existe -->
    <field name="sent_date"/>     <!-- ← Existe -->
    <field name="create_date"/>
</tree>
```

**Mudanças na Form View:**
```xml
<!-- Antes (Incorreto) -->
<group>
    <field name="provider_id" required="1"/>  <!-- ← Não existe -->
    <field name="template_id"/>                 <!-- ← Não existe -->
</group>
<group>
    <field name="cost" readonly="1"/>         <!-- ← Não existe -->
    <field name="segments" readonly="1"/>      <!-- ← Não existe -->
    <field name="delivery_date" readonly="1"/> <!-- ← Não existe -->
</group>

<!-- Depois (Correto) -->
<group>
    <field name="partner_id"/>
    <field name="user_id"/>
</group>
<group>
    <field name="sent_date" readonly="1"/>
    <field name="external_id" readonly="1"/>
</group>
```

**Mudanças na Search View:**
```xml
<!-- Antes (Incorreto) -->
<field name="provider_id"/>  <!-- ← Não existe -->
<filter string="Provider" name="group_provider" context="{'group_by': 'provider_id'}"/>  <!-- ← Não existe -->

<!-- Depois (Correto) -->
<!-- Removido provider_id -->
<filter string="User" name="group_user" context="{'group_by': 'user_id'}"/>  <!-- ← Existe -->
```

**Mudanças no Statusbar:**
```xml
<!-- Antes (Incorreto) -->
<field name="state" widget="statusbar" statusbar_visible="draft,outgoing,sent,delivered,error,canceled"/>
<!--                                                                  ^^^^^^^^ Não existe -->

<!-- Depois (Correto) -->
<field name="state" widget="statusbar" statusbar_visible="draft,outgoing,sent,error,canceled"/>
```

---

## 🎓 Lições Aprendidas

### 1. Validar Campos Antes de Usar

**Regra:** Sempre verificar quais campos existem no modelo antes de criar views.

**Como verificar:**
```bash
# Ver campos do modelo
grep -E '^\s+[a-z_]+ = fields\.' models/sms_message.py
```

### 2. Modelo Simplificado vs Completo

**Problema:** O modelo `sms.message` é uma versão simplificada criada para resolver conflitos. Campos avançados como `provider_id`, `cost`, etc. podem ser adicionados depois quando necessário.

**Solução:** Views devem usar apenas campos que existem no modelo atual.

### 3. Statusbar States

**Regra:** Os estados no `statusbar_visible` devem corresponder exatamente aos estados definidos no `Selection` do campo `state`.

**Exemplo:**
```python
# Modelo
state = fields.Selection([
    ('draft', 'Draft'),
    ('outgoing', 'Outgoing'), 
    ('sent', 'Sent'),
    ('error', 'Error'),
    ('canceled', 'Canceled')
], ...)

# View (correto)
<field name="state" widget="statusbar" statusbar_visible="draft,outgoing,sent,error,canceled"/>
```

---

## 📊 Comparação

### Antes
- Tree View: 7 campos (2 inexistentes)
- Form View: 10 campos (5 inexistentes)
- Search View: Referencia `provider_id` (inexistente)
- **Status:** ❌ Erro de validação

### Depois
- Tree View: 7 campos (todos existem) ✅
- Form View: 7 campos (todos existem) ✅
- Search View: Apenas campos existentes ✅
- **Status:** ✅ Pronto para uso

---

## ✅ Status

- ✅ View atualizada (apenas campos existentes)
- ✅ Tree view corrigida
- ✅ Form view corrigida
- ✅ Search view corrigida
- ✅ Statusbar corrigido
- ✅ Pronto para atualizar módulo

---

## 🔄 Próximos Passos

1. **Tentar atualizar o módulo novamente:**
   - Views agora usam apenas campos existentes
   - Não deve haver mais erros de validação

2. **Se precisar adicionar campos avançados:**
   - Adicionar campos ao modelo primeiro
   - Depois atualizar views para usar novos campos

---

## 📝 Campos Disponíveis no Modelo

**Campos básicos:**
- ✅ `phone` - Número de telefone
- ✅ `body` - Mensagem
- ✅ `state` - Status (draft, outgoing, sent, error, canceled)

**Relacionamentos:**
- ✅ `partner_id` - Contato
- ✅ `user_id` - Usuário

**Campos de controle:**
- ✅ `sent_date` - Data de envio
- ✅ `error_message` - Mensagem de erro
- ✅ `external_id` - ID externo

**Campos automáticos:**
- ✅ `create_date` - Data de criação
- ✅ `write_date` - Data de modificação
- ✅ `id` - ID do registro

---

**Criado em:** 2025-11-19
**Status:** ✅ Correção aplicada

