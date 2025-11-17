# 🐛 Histórico de Erros Resolvidos

> **Propósito:** Documentar TODOS os erros encontrados e suas soluções para nunca cometer o mesmo erro duas vezes.

---

## Como Usar Este Arquivo

**Quando um erro for resolvido:**
1. Adicione entrada no topo (mais recente primeiro)
2. Use template abaixo
3. Seja ESPECÍFICO - detalhes salvam tempo futuro
4. Inclua código/SQL quando relevante

**Template:**
```markdown
### [YYYY-MM-DD] Título Curto do Erro

**Contexto:** Onde/quando aconteceu
**Sintoma:** O que vimos (erro, comportamento)
**Causa Raiz:** Por que aconteceu
**Solução:** Como corrigimos
**Prevenção:** Como evitar no futuro
**Tags:** #tag1 #tag2
```

---

## 📋 Erros Resolvidos

### [2025-11-16] Admin User Locked Out

**Contexto:** Após reorganização de permissões, admin não conseguia acessar

**Sintoma:**
- Erro ao tentar acessar configurações
- "Access Denied" em várias views
- Admin perdeu grupo base.group_system

**Causa Raiz:**
Script de reorganização de permissões removeu inadvertidamente grupos críticos do usuário admin

**Solução:**
```sql
-- Restaurar grupos do admin
INSERT INTO res_groups_users_rel (gid, uid)
SELECT g.id, 2  -- uid 2 = admin
FROM res_groups g
WHERE g.id IN (
    SELECT id FROM res_groups
    WHERE name IN ('Administration / Settings', 'Sales / Manager', 'Technical Features')
)
ON CONFLICT DO NOTHING;
```

**Prevenção:**
- SEMPRE fazer backup antes de mexer em permissões
- NUNCA modificar permissões do uid=2 (admin) sem confirmação explícita
- Criar script de verificação de integridade de permissões

**Tags:** #security #permissions #admin #crítico

---

### [2025-11-16] Vendedores Vendo Oportunidades de Outros

**Contexto:** Após instalação do módulo SMS, vendedores viam todas as oportunidades

**Sintoma:**
- Vendedor A via oportunidades do Vendedor B
- Vazamento de informações sensíveis
- Violação de privacidade

**Causa Raiz:**
Record rules do CRM foram sobrescritas por módulo customizado que não implementou filtros corretos

**Solução:**
```xml
<record id="crm_lead_rule_salesman" model="ir.rule">
    <field name="name">Vendedor vê apenas suas oportunidades</field>
    <field name="model_id" ref="crm.model_crm_lead"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
</record>
```

**Prevenção:**
- Sempre criar record rules para novos modelos
- TESTAR com usuários não-admin
- Code review obrigatório para security-related changes

**Tags:** #security #crm #record-rules #privacidade

---

### [2025-11-16] Fotos de Funcionários Perdidas

**Contexto:** Imagens de res.partner desaparecendo aleatoriamente

**Sintoma:**
- Campo `image_1920` fica NULL
- Acontece em updates do partner
- Não há padrão claro

**Causa Raiz:**
**EM INVESTIGAÇÃO** - Possíveis causas:
1. Override incorreto do método write()
2. Limpeza automática de attachments
3. Módulo third-party interferindo

**Solução:**
Ainda não resolvido completamente. Workaround temporário:
- Backup diário de ir_attachment
- Monitorar logs quando acontecer

**Próximos Passos:**
1. Adicionar logging em res.partner.write()
2. Verificar ir_attachment.gc (garbage collector)
3. Revisar módulos instalados que tocam em res.partner

**Tags:** #bug #res-partner #images #investigating

---

### [2025-11-16] SMS Não Sendo Enviado

**Contexto:** Integração Kolmeya API falhando silenciosamente

**Sintoma:**
- Status "sent" no Odoo
- SMS nunca chega
- Sem erro nos logs

**Causa Raiz:**
Timeout muito curto (5s) causava falha antes da API responder, mas exception não era capturada corretamente

**Solução:**
```python
def send_sms(self, phone, message):
    try:
        response = requests.post(
            KOLMEYA_URL,
            json={'phone': phone, 'message': message},
            timeout=30  # Aumentado de 5 para 30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        _logger.error(f'Timeout sending SMS to {phone}')
        raise UserError(_('SMS service timeout. Try again later.'))
    except requests.exceptions.RequestException as e:
        _logger.error(f'Error sending SMS: {e}')
        raise UserError(_('Failed to send SMS: %s') % str(e))
```

**Prevenção:**
- Usar timeouts adequados (30s para APIs externas)
- SEMPRE capturar exceptions corretamente
- Logar erros de integração
- Mostrar erro para usuário quando falhar

**Tags:** #integration #kolmeya #sms #api #timeout

---

### [2025-11-15] Performance Degradada no CRM

**Contexto:** Listagem de oportunidades levando >10s para carregar

**Sintoma:**
- View tree muito lenta
- Query PostgreSQL executando por segundos
- CPU do servidor em 100%

**Causa Raiz:**
N+1 queries em campo computado `partner_phone` que buscava telefone sem cache

**Solução:**
```python
# ANTES (ruim)
@api.depends('partner_id')
def _compute_partner_phone(self):
    for record in self:
        record.partner_phone = record.partner_id.phone  # N+1!

# DEPOIS (bom)
@api.depends('partner_id.phone')
def _compute_partner_phone(self):
    for record in self:
        record.partner_phone = record.partner_id.phone  # Cached!
```

**Prevenção:**
- Sempre usar `@api.depends()` com campos relacionados completos
- Usar `mapped()` quando iterar sobre múltiplos records
- Profile queries com pg_stat_statements
- Monitorar slow queries

**Tags:** #performance #crm #n+1 #optimization

---

## 🔍 Erros Comuns - Quick Reference

### Permission Denied
1. Verificar ir.model.access.csv
2. Verificar record rules
3. Testar com `sudo()` para isolar problema
4. Verificar grupos do usuário

### Field Not Found
1. Model está registrado no `__init__.py`?
2. Campo existe no modelo Python?
3. Module foi atualizado? (`-u module`)
4. Typo no nome do campo?

### Import Error
1. Módulo está em addons-path?
2. `__init__.py` importa o arquivo?
3. Dependências no manifest?
4. Syntax error no Python?

### View Error
1. XML bem formado?
2. ID único?
3. Model correto no view?
4. Herança (inherit_id) existe?

### API Integration Fails
1. Network connectivity?
2. Timeout adequado?
3. Exception handling correto?
4. Credentials válidos?
5. Rate limiting?

---

## 📊 Estatísticas

**Total de erros documentados:** 5
**Críticos resolvidos:** 2
**Em investigação:** 1
**Prevenção estabelecida:** 5

---

**Última atualização:** 2025-11-17
**Próxima revisão:** Sempre que novo erro for resolvido

---

## 📝 Template para Novo Erro

Copie e cole quando resolver um novo erro:

```markdown
### [YYYY-MM-DD] Título Curto do Erro

**Contexto:**

**Sintoma:**

**Causa Raiz:**

**Solução:**
```código ou descrição```

**Prevenção:**

**Tags:** #tag1 #tag2
```
