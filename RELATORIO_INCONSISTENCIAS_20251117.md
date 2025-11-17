# RELATÓRIO DE INCONSISTÊNCIAS E PROBLEMAS - ODOO 15 REALCRED

**Data da Análise:** 17/11/2025  
**Servidor:** odoo-rc (35.199.79.229 - GCP)  
**Database:** realcred

---

## 📋 RESUMO EXECUTIVO

### Problemas Críticos Encontrados: 2
1. ❌ **account.move** - SEM permissão para Internal User
2. ❌ **sale.order** - SEM permissão para Internal User

### Problemas Importantes: 3
1. ⚠️ **17 Permissões Duplicadas** - Podem causar confusão e problemas de performance
2. ⚠️ **3 Menus Críticos com Restrições** - Podem limitar acesso desnecessariamente
3. ⚠️ **50+ Módulos "Not Installable"** - Podem indicar problemas de configuração

### Correções Já Aplicadas: 6
- ✅ crm.lead, crm.stage, crm.tag - Permissões OK
- ✅ account.move.line - Permissão OK
- ✅ crm.phonecall - Permissão OK
- ✅ Menu CRM - Sem restrições

### Ações Prioritárias
1. **URGENTE:** Criar permissões para `account.move` e `sale.order`
2. **IMPORTANTE:** Remover permissões duplicadas
3. **RECOMENDADO:** Revisar restrições de menus e módulos not installable

---

## 🔴 PROBLEMAS CRÍTICOS ENCONTRADOS

### 1. PERMISSÕES FALTANDO PARA INTERNAL USER

#### ❌ account.move (Faturas/Lançamentos Contábeis)
- **Status:** SEM permissão para Internal User
- **Impacto:** Usuários internos não podem acessar faturas e lançamentos contábeis
- **Ação Necessária:** Criar permissão CRUD completa para Internal User

#### ❌ sale.order (Pedidos de Venda)
- **Status:** SEM permissão para Internal User
- **Impacto:** Usuários internos não podem acessar pedidos de venda
- **Ação Necessária:** Criar permissão CRUD completa para Internal User

---

## ⚠️ PROBLEMAS IMPORTANTES

### 2. PERMISSÕES DUPLICADAS (17 encontradas)

Permissões duplicadas podem causar:
- Confusão na aplicação de regras
- Possível degradação de performance
- Dificuldade na manutenção

**Modelos com permissões duplicadas:**
- `acrux.chat.conversation` - Internal User (2 permissões)
- `res.partner` - Administrator (2 permissões)
- `res.partner` - Internal User (2 permissões)
- `account.journal` - Administrator (2 permissões)
- `calendar.event.type` - Internal User (2 permissões)
- `sms.template` - Administrator (2 permissões)
- `account.tax` - User: Own Documents Only (2 permissões)
- `ir.model` - Internal User (2 permissões)
- `acrux.chat.message` - Internal User (2 permissões)
- `acrux.chat.connector` - Settings (2 permissões)
- `sms.provider` - SMS User (2 permissões)
- `res.partner` - User: Own Documents Only (2 permissões)
- `mail.activity.type` - Administrator (2 permissões)
- `sms.provider` - SMS Manager (2 permissões)
- `ir.attachment` - Internal User (2 permissões)
- `ir.model.fields` - Internal User (2 permissões)
- E mais...

**Ação Necessária:** Remover permissões duplicadas, mantendo apenas uma por modelo/grupo

---

### 3. MENUS COM RESTRIÇÕES DESNECESSÁRIAS

#### ⚠️ Menu "Vendas"
- **Restrito a:** Mostrar Recursos de Contabilidade - Somente Leitura
- **Impacto:** Usuários sem esse grupo não veem o menu de Vendas
- **Ação Necessária:** Remover restrição ou adicionar Internal User ao grupo

#### ⚠️ Menu "Contatos na Lista de Mailing"
- **Restrito a:** Usuário
- **Impacto:** Pode estar limitando acesso desnecessariamente
- **Ação Necessária:** Verificar se a restrição é necessária

---

## 📋 OUTRAS OBSERVAÇÕES

### 4. MÓDULOS MARCADOS COMO "NOT INSTALLABLE"

Os seguintes módulos aparecem como "not installable" nos logs:
- `crm_phonecall` - Módulo de ligações telefônicas
- `realcred_permissions` - Módulo de permissões customizadas
- `contacts_realcred` - Módulo customizado de contatos
- E muitos outros módulos customizados

**Possíveis causas:**
- Manifestos com problemas
- Dependências faltando
- Módulos desinstalados mas ainda referenciados

**Ação Necessária:** Verificar e corrigir manifestos ou remover referências

---

### 5. REGRAS DE REGISTRO RESTRITIVAS

Existem regras de registro que restringem acesso a "próprios registros" usando:
- `user.id`
- `create_uid`

**Impacto:** Usuários podem ver apenas registros que criaram, o que pode ser desejado ou não dependendo do caso de uso.

**Ação Necessária:** Revisar regras de registro para garantir que estão alinhadas com os requisitos de negócio.

---

## ✅ CORREÇÕES JÁ APLICADAS

1. ✅ **crm.lead** - Permissão CRUD criada para Internal User
2. ✅ **crm.stage** - Permissão CRUD criada para Internal User
3. ✅ **crm.tag** - Permissão CRUD atualizada para Internal User
4. ✅ **account.move.line** - Permissão CRUD criada para Internal User
5. ✅ **crm.phonecall** - Permissão CRUD atualizada para Internal User
6. ✅ **Menu CRM** - Restrições removidas, visível para todos

---

## 🎯 RECOMENDAÇÕES PRIORITÁRIAS

### Prioridade ALTA (Corrigir Imediatamente)

1. **Criar permissões para account.move e sale.order**
   - Impacto direto na funcionalidade
   - Usuários não conseguem trabalhar com faturas e pedidos

2. **Remover permissões duplicadas**
   - Limpar registros duplicados
   - Manter apenas uma permissão por modelo/grupo

### Prioridade MÉDIA

3. **Revisar restrições de menus**
   - Garantir que menus críticos estão acessíveis
   - Remover restrições desnecessárias

4. **Verificar módulos "not installable"**
   - Corrigir manifestos ou remover referências
   - Limpar banco de dados

### Prioridade BAIXA

5. **Revisar regras de registro**
   - Documentar regras existentes
   - Alinhar com requisitos de negócio

---

## 📊 ESTATÍSTICAS

- **Total de problemas críticos:** 2
- **Total de problemas importantes:** 3
- **Permissões duplicadas:** 17
- **Menus críticos com restrições:** 3
- **Módulos CRM not installable:** 7
- **Módulos totais not installable:** 50+

---

## ⚙️ CONFIGURAÇÃO DO SERVIDOR

### Arquivo: `/etc/odoo-server.conf`

**Configurações Principais:**
- **Workers:** 9
- **HTTP Port:** 8069
- **Longpolling Port:** 8072
- **Admin Password:** Configurado
- **Proxy Mode:** True
- **Database Filter:** realcred
- **Log Level:** info
- **Max Cron Threads:** 5
- **Memory Limits:**
  - Hard: 6 GB
  - Soft: 8 GB
- **Time Limits:**
  - CPU: 60s
  - Real: 120s
  - Cron: 600s

**Addons Paths:**
- `/odoo/odoo-server/addons`
- `/odoo/custom/addons_custom`
- `/odoo/custom/helpdesk`
- `/odoo/custom/l10n_br_base`
- `/odoo/custom/social`
- `/odoo/custom/addons-whatsapp-connector`
- `/odoo/custom/om_account_accountant`
- `/odoo/custom/hr_attendance_pro`

**Observações:**
- ✅ Configuração parece adequada
- ⚠️ Muitos paths de addons customizados (pode indicar fragmentação)
- ✅ Limites de memória e tempo configurados adequadamente

---

## 🔧 SCRIPTS DE CORREÇÃO

### Script 1: Criar Permissões Faltando

```python
# Executar via Odoo shell
internal_user = env.ref("base.group_user")

for model_name in ["account.move", "sale.order"]:
    model = env["ir.model"].search([("model", "=", model_name)], limit=1)
    if model:
        access = env["ir.model.access"].search([
            ("model_id", "=", model.id),
            ("group_id", "=", internal_user.id),
            ("active", "=", True)
        ], limit=1)
        if not access:
            env["ir.model.access"].create({
                "name": f"{model_name} - Internal User",
                "model_id": model.id,
                "group_id": internal_user.id,
                "perm_read": True,
                "perm_write": True,
                "perm_create": True,
                "perm_unlink": True,
            })
            env.cr.commit()
```

### Script 2: Remover Permissões Duplicadas

```python
# Executar via Odoo shell
env.cr.execute("""
    DELETE FROM ir_model_access a
    WHERE a.id NOT IN (
        SELECT MIN(id)
        FROM ir_model_access
        WHERE active = true
        GROUP BY model_id, group_id
    )
    AND a.active = true
""")
env.cr.commit()
```

---

**Relatório gerado em:** 17/11/2025 12:55 UTC  
**Próxima revisão recomendada:** Após aplicação das correções

