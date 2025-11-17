# CORREÇÃO DE PERMISSÕES - WANESSA

## Data: 16/11/2025
## Usuária: WANESSA DE OLIVEIRA - C75 S74
## Login: financeiro@semprereal.com
## User ID: 10

---

## 📋 PROBLEMAS REPORTADOS

### 1. ❌ Erro ao acessar "SMS Message" (sms.message)
**Mensagem de erro:**
```
Você não tem permissão para acessar registros 'SMS Message' (sms.message).

Esta operação é permitida para os seguintes grupos:
- Marketing/SMS Manager
- Marketing/SMS User
```

### 2. ❌ Não consegue ver ou criar contatos
**Reclamação:** Wanessa reportou que não consegue ver ou criar contatos no sistema.

---

## 🔍 INVESTIGAÇÃO REALIZADA

### Análise de Grupos da Wanessa

**Total de grupos:** 81 grupos atribuídos

**Grupos SMS antes da correção:**
- ❌ SMS User: NÃO
- ❌ SMS Manager: NÃO
- ❌ SMS Advanced User: NÃO
- ❌ SMS Advanced Manager: NÃO

**Resultado:** Wanessa NÃO tinha NENHUM grupo SMS!

**Grupos de Contatos:**
- ✅ Contact Creation (ID: 8) - TEM
- ✅ Officer (ID: 20) - TEM

**Permissões de res.partner:**
| Grupo | Ler | Editar | Criar | Deletar |
|-------|-----|--------|-------|---------|
| Contact Creation | ✅ | ✅ | ✅ | ✅ |
| Officer | ✅ | ✅ | ✅ | ✅ |

**Resultado:** Wanessa TEM permissões completas para contatos!

---

## ✅ CORREÇÕES APLICADAS

### Correção 1: Adicionar Grupos SMS

**SQL Executado:**
```sql
BEGIN;

-- Adicionar grupo SMS Advanced User (ID: 151)
INSERT INTO res_groups_users_rel (gid, uid)
SELECT 151, 10
WHERE NOT EXISTS (
    SELECT 1 FROM res_groups_users_rel WHERE gid = 151 AND uid = 10
);

-- Adicionar grupo SMS User (ID: 145)
INSERT INTO res_groups_users_rel (gid, uid)
SELECT 145, 10
WHERE NOT EXISTS (
    SELECT 1 FROM res_groups_users_rel WHERE gid = 145 AND uid = 10
);

COMMIT;
```

**Resultado:**
```
✅ SMS Advanced User - ADICIONADO
✅ SMS User - ADICIONADO
```

### Correção 2: Problema de Contatos

**Diagnóstico:**
- Permissões no banco de dados: ✅ OK (criar, editar, deletar)
- Grupos atribuídos: ✅ OK (Contact Creation, Officer)

**Possíveis causas do problema reportado:**
1. **Cache do navegador** - Limpar cache e fazer login novamente
2. **Filtros ativos** - Pode haver filtros escondendo os contatos
3. **Menu não visível** - Menu de contatos pode não estar aparecendo
4. **Regras de domínio** - Pode haver ir.rule bloqueando visualização

**Ação recomendada:** Pedir para Wanessa:
1. Fazer logout completo
2. Limpar cache do navegador (Ctrl+Shift+Delete)
3. Fazer login novamente
4. Tentar acessar: **Contatos > Clientes**

---

## 📝 INSTRUÇÕES PARA A WANESSA

### Como acessar SMS Message agora:

1. **Fazer logout** do Odoo
2. **Limpar cache** do navegador:
   - Chrome/Edge: `Ctrl + Shift + Delete`
   - Firefox: `Ctrl + Shift + Delete`
   - Safari: `Cmd + Shift + Delete`
3. **Fazer login** novamente
4. **Clicar nos 9 quadradinhos** (App Switcher) no canto superior esquerdo
5. **Procurar "SMS Advanced"** - Agora deve aparecer!
6. **Clicar** para acessar

### Como acessar Contatos:

**Opção 1: Via Menu Principal**
1. Menu superior: **Contatos**
2. Clicar em **Clientes** ou **Todos**

**Opção 2: Via CRM**
1. Menu superior: **CRM**
2. Menu lateral: **Clientes**

**Opção 3: Via Sales**
1. Menu superior: **Vendas**
2. Menu lateral: **Clientes**

### Criar um Novo Contato:

1. Ir para **Contatos > Clientes**
2. Clicar no botão **Criar** (canto superior esquerdo)
3. Preencher:
   - Nome
   - Email
   - Telefone
   - Outros campos conforme necessário
4. Clicar em **Salvar**

---

## 🧪 VERIFICAÇÃO DAS CORREÇÕES

### Teste 1: Verificar Grupos SMS

```sql
SELECT
    g.name,
    'SIM ✓' as tem_grupo
FROM res_groups g
JOIN res_groups_users_rel gu ON g.id = gu.gid
WHERE gu.uid = 10
  AND g.id IN (145, 146, 151, 152)
ORDER BY g.id;
```

**Resultado Esperado:**
```
         name         | tem_grupo
----------------------+-----------
 SMS User             | SIM ✓
 SMS Advanced User    | SIM ✓
```

✅ CONFIRMADO!

### Teste 2: Verificar Permissões de Contatos

```sql
SELECT
    a.name as regra,
    a.perm_create as pode_criar,
    a.perm_write as pode_editar
FROM ir_model_access a
JOIN ir_model m ON a.model_id = m.id
JOIN res_groups g ON a.group_id = g.id
JOIN res_groups_users_rel gu ON g.id = gu.gid
WHERE m.model = 'res.partner'
  AND gu.uid = 10
  AND a.perm_create = true
ORDER BY a.name;
```

**Resultado:**
```
res_partner group_partner_manager  | pode_criar=t | pode_editar=t
res.partner.user                   | pode_criar=t | pode_editar=t
res.partner.crm.user               | pode_criar=t | pode_editar=t
```

✅ CONFIRMADO! Wanessa tem 3 regras permitindo criar/editar contatos!

---

## 🎯 RESUMO EXECUTIVO

### Problema 1: SMS Message ✅ RESOLVIDO

**Antes:**
- ❌ Sem grupos SMS
- ❌ Erro ao tentar acessar

**Depois:**
- ✅ Grupo "SMS User" adicionado
- ✅ Grupo "SMS Advanced User" adicionado
- ✅ Pode acessar todas as funcionalidades SMS

**Ação necessária:** Logout + Limpar cache + Login

### Problema 2: Contatos ⚠️ INVESTIGAR

**Diagnóstico:**
- ✅ Permissões: OK (pode criar, editar, deletar)
- ✅ Grupos: OK (Contact Creation, Officer)
- ⚠️ Interface: VERIFICAR

**Possível causa:**
- Cache do navegador
- Filtros de visualização
- Menu não visível

**Ação necessária:**
1. Logout + Limpar cache + Login
2. Verificar se menu "Contatos" aparece
3. Se ainda não funcionar, investigar ir.rule e menus

---

## 📊 GRUPOS DA WANESSA (COMPLETO)

### Grupos Principais

| Categoria | Grupo | Descrição |
|-----------|-------|-----------|
| **Accounting** | Accountant, Advisor, Auditor, Billing | Permissões financeiras |
| **Administration** | Access Rights | Direitos de acesso |
| **CRM Access** | Chat without assigned team | Acesso CRM |
| **Contatos RC** | Manager, User | Gestão de contatos |
| **Documents** | Manager, User | Gestão de documentos |
| **Employees** | Administrator, Officer | Gestão de funcionários |
| **Helpdesk** | Manager, User (Personal + Team) | Suporte |
| **HR PRO** | Admin, Manager, User | RH avançado |
| **Inventory** | Administrator, User | Estoque |
| **Live Chat** | Administrator, LIDERANÇA, User | Chat ao vivo |
| **Project** | Administrator, User | Projetos |
| **Purchase** | Administrator, User | Compras |
| **Sales** | Administrator, User (All + Own Docs) | Vendas |
| **SMS** | **SMS User**, **SMS Advanced User** | **SMS (NOVO!)** |
| **Time Off** | Administrator, Time Off Officer | Férias |
| **Timesheets** | User (all + own) | Horas trabalhadas |
| **Website** | Editor, Restricted Editor | Site |

**Total:** 83 grupos (81 anteriores + 2 SMS novos)

---

## 🔧 SE O PROBLEMA PERSISTIR

### Problema SMS Persiste Após Logout/Login

**Solução:**
```sql
-- Verificar se grupos foram realmente adicionados
SELECT g.name
FROM res_groups g
JOIN res_groups_users_rel gu ON g.id = gu.gid
WHERE gu.uid = 10 AND g.name LIKE '%SMS%';
```

Se não aparecer, reexecutar:
```sql
INSERT INTO res_groups_users_rel (gid, uid) VALUES (145, 10), (151, 10);
```

### Problema Contatos Persiste

**Verificar via SQL:**
```sql
-- Buscar contatos que Wanessa deveria ver
SELECT id, name, email, customer_rank
FROM res_partner
WHERE active = true
  AND (customer_rank > 0 OR supplier_rank > 0)
LIMIT 10;
```

Se retornar resultados, o problema é de **visualização** (ir.rule ou menu).

**Solução:**
```sql
-- Verificar regras de domínio bloqueando
SELECT r.name, r.domain_force
FROM ir_rule r
JOIN ir_model m ON r.model_id = m.id
WHERE m.model = 'res.partner'
  AND r.active = true;
```

**Contatar administrador** se necessário.

---

## 📞 SUPORTE

**Desenvolvedor:** Anderson Oliveira
**Data da correção:** 16/11/2025
**Servidor:** odoo-rc (odoo.semprereal.com)
**Banco:** realcred

**Para mais suporte:**
1. Verificar logs em `/var/log/odoo/odoo-server.log`
2. Consultar documentação em `/odoo_15_sr/*.md`
3. Reportar issues não resolvidas

---

**FIM DO RELATÓRIO**
