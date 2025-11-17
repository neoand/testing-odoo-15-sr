# Fix: SMS Wizard - Preenchimento Automático de Telefone

**Data**: 2025-11-15
**Issue**: Quando abria o wizard de SMS do botão no parceiro, o telefone não era preenchido automaticamente
**Status**: ✅ Corrigido

---

## Problema Relatado

Quando o usuário:
1. Abria um contato (res.partner)
2. Clicava no ícone SMS
3. O wizard abria mas **não mostrava o número de telefone automaticamente**
4. Tinha que digitar manualmente, mesmo o contato tendo telefone

---

## Causa Raiz

O wizard `sms.compose` não estava:
1. Pegando o `active_id` do contexto quando aberto do formulário de parceiro
2. Preenchendo automaticamente o campo `partner_ids`
3. Mostrando os números de telefone dos parceiros selecionados

---

## Correções Aplicadas

### 1. Arquivo: `wizard/sms_compose.py`

**Adicionado método `default_get()`**:
```python
@api.model
def default_get(self, fields_list):
    """Override to populate partner_ids from context"""
    res = super(SMSComposer, self).default_get(fields_list)

    # Get active_id from context (when opened from partner form)
    active_model = self.env.context.get('active_model')
    active_id = self.env.context.get('active_id')

    if active_model == 'res.partner' and active_id:
        res['partner_ids'] = [(6, 0, [active_id])]

    # Also check for default_partner_ids in context
    if self.env.context.get('default_partner_ids'):
        res['partner_ids'] = self.env.context.get('default_partner_ids')

    return res
```

**Adicionado campo computed `phone_numbers`**:
```python
@api.depends('partner_ids')
def _compute_phone_numbers(self):
    """Display phone numbers of selected partners"""
    for rec in self:
        phones = []
        for partner in rec.partner_ids:
            phone = partner.mobile or partner.phone
            if phone:
                phones.append(f"{partner.name}: {phone}")
            else:
                phones.append(f"{partner.name}: [SEM TELEFONE]")
        rec.phone_numbers = '\n'.join(phones) if phones else 'Nenhum destinatário selecionado'
```

**Melhorias adicionais**:
- Campo `partner_ids` agora é `required=True`
- Validação melhorada - erro se parceiro não tem telefone
- Mensagem de sucesso ao enviar SMS

### 2. Arquivo: `views/sms_compose_views.xml`

**View reorganizada** para melhor UX:
```xml
<form string="Send SMS">
    <group>
        <group>
            <field name="partner_ids" widget="many2many_tags"/>
            <field name="phone_numbers" readonly="1" widget="text"/>
        </group>
        <group>
            <field name="template_id"/>
            <field name="provider_id"/>
            <field name="char_count" readonly="1"/>
        </group>
    </group>
    <group>
        <field name="body" widget="text" placeholder="Digite sua mensagem aqui..." required="1"/>
    </group>
    <footer>
        <button string="Enviar SMS" name="action_send_sms" type="object" class="btn-primary"/>
        <button string="Cancelar" class="btn-secondary" special="cancel"/>
    </footer>
</form>
```

**Melhorias na view**:
- Campo `phone_numbers` agora é exibido (readonly)
- Mostra nome e telefone de cada destinatário
- Avisos se parceiro não tem telefone
- Textos em português
- Layout mais organizado

### 3. Arquivo: `views/sms_template_views.xml`

**Corrigido** para usar campos corretos do modelo padrão `sms.template`:
- Removido campos customizados: `code`, `applies_to`, `admin_only`, `message_template`, `message_preview`
- Usando campos padrão Odoo: `name`, `model_id`, `model`, `body`, `lang`
- Sintaxe Jinja2 no placeholder: `{{ object.name }}`, `{{ user.name }}`

---

## Como Funciona Agora

### Fluxo Completo:

1. **Usuário abre parceiro**
   - Ex: https://odoo.semprereal.com/web#id=1865&model=res.partner

2. **Clica no botão "Send SMS"** (ícone de avião)

3. **Wizard abre COM:**
   - ✅ Parceiro já selecionado automaticamente
   - ✅ Telefone exibido: "Nome do Cliente: 5548991910234"
   - ✅ Provider Kolmeya pré-selecionado
   - ✅ Contador de caracteres
   - ✅ Opção de selecionar template

4. **Usuário pode:**
   - Ver claramente qual número será usado
   - Selecionar um template (opcional)
   - Digitar ou editar mensagem
   - Clicar "Enviar SMS"

5. **Sistema:**
   - Valida se parceiro tem telefone
   - Cria sms.message
   - Envia via Kolmeya API
   - Mostra notificação de sucesso

---

## Exemplo de Uso

### Caso 1: Abrir do Parceiro (active_id)
```
Contexto: {'active_model': 'res.partner', 'active_id': 1865}
Resultado: partner_ids = [(6, 0, [1865])]
Mostra: "João Silva: 5548991910234"
```

### Caso 2: Múltiplos Parceiros
```
Contexto: {'default_partner_ids': [(6, 0, [1865, 1866, 1867])]}
Resultado: 3 parceiros selecionados
Mostra:
"João Silva: 5548991910234
Maria Santos: 5548991221131
Pedro Oliveira: [SEM TELEFONE]"
Erro ao enviar: "Partner Pedro Oliveira has no phone number"
```

---

## Testes Realizados

✅ Wizard abre do parceiro com telefone preenchido
✅ Campo phone_numbers mostra nome e número
✅ Validação de parceiro sem telefone
✅ Envio de SMS funciona
✅ Template selection funciona
✅ Contador de caracteres funciona
✅ Módulo carrega sem erros

---

## Arquivos Modificados

```
/odoo/custom/addons_custom/sms_base_sr/
├── wizard/sms_compose.py (atualizado)
├── views/sms_compose_views.xml (atualizado)
└── views/sms_template_views.xml (corrigido)
```

---

## Próximos Passos

1. ✅ Testar wizard no ambiente de produção
2. ✅ Verificar se telefone aparece automaticamente
3. ✅ Enviar SMS de teste real
4. ⏳ Feedback do usuário

---

## Rollback (se necessário)

Se precisar reverter as mudanças:

```bash
ssh odoo-rc
cd /odoo/custom/addons_custom/sms_base_sr

# Restaurar backup (se fez backup antes)
# ou desinstalar e reinstalar módulo limpo
```

---

**Fix testado e funcionando!** 🚀
