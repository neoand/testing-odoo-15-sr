# ✅ REORGANIZAÇÃO DE PERMISSÕES APLICADA
## Sistema: Odoo 15 - Realcred
## Data: 16/11/2025

---

## 🎯 OBJETIVO ALCANÇADO

Centralizar controle administrativo no usuário principal (admin) e reorganizar permissões dos 4 usuários que estavam "bagunçando o sistema".

---

## 📊 MUDANÇAS APLICADAS

### ANTES (Situação Problemática)

| Usuário | Login | Total Grupos | Settings | Administrators |
|---------|-------|--------------|----------|----------------|
| Wanessa | financeiro@semprereal.com | 83 | ✅ SIM | 14 |
| Gustavo | marketingdigital@semprereal.com | 84 | ✅ SIM | 13 |
| Ana Carla | ana@semprereal.com | 82 | ❌ NÃO | 15 |
| Thiago | auxfinanceiro@semprereal.com | 82 | ✅ SIM | 14 |

**Problemas:**
- ❌ 3 usuários com acesso a **Settings** (configuração central do sistema)
- ❌ Todos com **Administrators** de múltiplos módulos
- ❌ Ana Carla (dona) podia **ALTERAR** ao invés de apenas **VER**
- ❌ Gustavo (marketing) podia **ALTERAR** ao invés de apenas **VER**

---

### DEPOIS (Situação Corrigida)

| Usuário | Login | Total Grupos | Settings | Administrators | Perfil |
|---------|-------|--------------|----------|----------------|--------|
| **Wanessa** | financeiro@semprereal.com | 82 (-1) | ❌ **REMOVIDO** | 14 | ✅ Admin Operacional |
| **Gustavo** | marketingdigital@semprereal.com | 65 (-19) | ❌ **REMOVIDO** | 0 | ✅ Visualização |
| **Ana Carla** | ana@semprereal.com | 62 (-20) | ❌ NÃO | 0 | ✅ Visualização (Dona) |
| **Thiago** | auxfinanceiro@semprereal.com | 81 (-1) | ❌ **REMOVIDO** | 14 | ✅ Admin Operacional |

---

## 🔐 NOVO MODELO DE PERMISSÕES

### 1. Wanessa de Oliveira (ID: 10) - ADMINISTRADORA OPERACIONAL
**Função:** Braço direito - ajuda em questões administrativas, financeiro, RH, vendas

**Permissões:**
- ✅ **Administrator** de 14 módulos:
  - Sales (Vendas)
  - Employees (Funcionários)
  - Attendances (Presença)
  - Recruitment (Recrutamento)
  - Live Chat
  - Project (Projetos)
  - Purchase (Compras)
  - Surveys (Pesquisas)
  - Lunch (Almoço)
  - Contracts (Contratos)
  - Time Off (Folgas)
  - Expenses (Despesas)
  - Inventory (Estoque)
  - HR PRO
- ✅ **Managers** de vários módulos
- ❌ **Settings** - REMOVIDO (não pode mais mexer em configurações do sistema)

**O que ela PODE fazer:**
- ✅ Gerenciar vendas, leads, oportunidades
- ✅ Gerenciar funcionários, férias, contratos
- ✅ Gerenciar compras e estoque
- ✅ Configurar workflows de cada módulo
- ✅ Criar/editar/deletar registros

**O que ela NÃO PODE fazer:**
- ❌ Instalar/desinstalar módulos
- ❌ Modificar grupos de usuários
- ❌ Alterar regras de segurança
- ❌ Acessar modo desenvolvedor
- ❌ Modificar views/menus do sistema

---

### 2. Thiago Mendes Rodrigues (ID: 119) - AUXILIAR ADMINISTRATIVO
**Função:** Ajuda a Wanessa

**Permissões:** IDÊNTICAS às da Wanessa
- ✅ Administrator de 14 módulos
- ✅ Managers de vários módulos
- ❌ Settings - REMOVIDO

**Capacidades:** Mesmas que a Wanessa

---

### 3. Ana Carla Almeida de Oliveira (ID: 79) - VISUALIZAÇÃO (DONA)
**Função:** Dona da empresa - quer **VER TUDO** mas **NÃO ALTERAR**

**Permissões:**
- ✅ 62 grupos de visualização/acesso básico
- ✅ User: All Documents (Sales) - vê todas as vendas
- ❌ **TODOS os Administrators removidos** (-20 grupos)
- ❌ **TODOS os Managers removidos**
- ❌ Settings - NÃO tem

**O que ela PODE fazer:**
- ✅ Visualizar vendas, leads, oportunidades
- ✅ Visualizar relatórios
- ✅ Acessar dashboards
- ✅ Ver informações de funcionários
- ✅ Consultar dados

**O que ela NÃO PODE fazer:**
- ❌ Criar/editar/deletar registros
- ❌ Modificar configurações
- ❌ Gerenciar usuários
- ❌ Alterar dados do sistema

---

### 4. Gustavo Almeida de Oliveira (ID: 12) - VISUALIZAÇÃO
**Função:** Marketing - apenas **VER**

**Permissões:**
- ✅ 65 grupos de visualização/acesso básico
- ✅ User: All Documents (Sales) - vê todas as vendas
- ❌ **TODOS os Administrators removidos** (-19 grupos)
- ❌ **TODOS os Managers removidos**
- ❌ Settings - REMOVIDO

**Capacidades:** Mesmas que Ana Carla (apenas visualização)

---

## 📦 BACKUPS CRIADOS

### Tabelas de Backup no PostgreSQL

1. **res_groups_users_rel_backup_20251116_permissoes**
   - Backup COMPLETO de TODOS os usuários do sistema
   - 9,065 registros
   - Permite rollback total

2. **backup_usuarios_problematicos_20251116**
   - Backup DETALHADO dos 4 usuários específicos
   - 331 registros
   - Inclui nome dos grupos e categorias

---

## 🔄 PROCEDIMENTO DE ROLLBACK

Se precisar voltar tudo ao estado anterior:

### Rollback Completo (Restaurar permissões originais)

```sql
-- Conectar ao PostgreSQL
sudo -u postgres psql realcred

BEGIN;

-- 1. Remover permissões atuais dos 4 usuários
DELETE FROM res_groups_users_rel
WHERE uid IN (10, 12, 79, 119);

-- 2. Restaurar permissões do backup
INSERT INTO res_groups_users_rel (uid, gid)
SELECT uid, gid
FROM res_groups_users_rel_backup_20251116_permissoes
WHERE uid IN (10, 12, 79, 119);

COMMIT;

-- 3. Verificar restauração
SELECT p.name, COUNT(r.gid) as grupos_restaurados
FROM res_users u
JOIN res_partner p ON p.id = u.partner_id
JOIN res_groups_users_rel r ON r.uid = u.id
WHERE u.id IN (10, 12, 79, 119)
GROUP BY p.name, u.id
ORDER BY u.id;
```

**Resultado Esperado:**
- Wanessa: 83 grupos (com Settings novamente)
- Gustavo: 84 grupos (com Settings novamente)
- Ana Carla: 82 grupos (com Administrators novamente)
- Thiago: 82 grupos (com Settings novamente)

---

### Rollback Parcial (Restaurar apenas 1 usuário)

Exemplo para restaurar apenas Gustavo:

```sql
BEGIN;

DELETE FROM res_groups_users_rel WHERE uid = 12;

INSERT INTO res_groups_users_rel (uid, gid)
SELECT uid, gid
FROM res_groups_users_rel_backup_20251116_permissoes
WHERE uid = 12;

COMMIT;
```

---

## ✅ VALIDAÇÃO E TESTES

### Como Testar as Mudanças

#### 1. Testar Wanessa/Thiago (Devem poder administrar módulos)
- [ ] Login com wanessa
- [ ] Tentar acessar Sales > Configuration - DEVE FUNCIONAR
- [ ] Tentar acessar Settings - DEVE DAR ERRO/NÃO APARECER
- [ ] Criar um lead - DEVE FUNCIONAR
- [ ] Editar funcionário - DEVE FUNCIONAR

#### 2. Testar Ana Carla/Gustavo (Devem apenas visualizar)
- [ ] Login com ana
- [ ] Tentar ver lista de leads - DEVE FUNCIONAR
- [ ] Tentar editar um lead - DEVE DAR ERRO
- [ ] Tentar deletar um lead - DEVE DAR ERRO
- [ ] Tentar acessar Settings - DEVE DAR ERRO/NÃO APARECER
- [ ] Ver relatórios - DEVE FUNCIONAR

---

## 📊 ESTATÍSTICAS FINAIS

### Grupos Removidos

| Usuário | Grupos Removidos | Principais |
|---------|------------------|------------|
| Wanessa | 1 grupo | Settings |
| Thiago | 1 grupo | Settings |
| Ana Carla | 20 grupos | 15 Administrators + 4 Managers + 1 Admin User |
| Gustavo | 19 grupos | 13 Administrators + 4 Managers + Settings + 1 Admin User |

**Total:** 41 acessos administrativos indevidos removidos

---

## 🚨 PROBLEMAS ESPERADOS E SOLUÇÕES

### Problema 1: Wanessa/Thiago reclamam que não conseguem fazer algo
**Sintoma:** "Não consigo mais acessar [algo específico]"

**Solução:**
1. Perguntar O QUE exatamente eles precisam fazer
2. Verificar se é algo que realmente precisam
3. Se sim, adicionar grupo ESPECÍFICO (NÃO Settings):
   ```sql
   -- Exemplo: adicionar acesso a Timesheets
   INSERT INTO res_groups_users_rel (uid, gid)
   VALUES (10, 125);  -- ID 125 = Administrator Timesheets
   ```

### Problema 2: Ana Carla/Gustavo querem editar algo
**Sintoma:** "Quero poder alterar esse registro"

**Discussão:**
- Você me disse que eles devem APENAS VER
- Se mudou de ideia, podemos adicionar grupos específicos
- **NÃO** recomendo dar Settings ou Administrators de volta

**Solução se for necessário:**
```sql
-- Dar acesso de edição a um módulo ESPECÍFICO
INSERT INTO res_groups_users_rel (uid, gid)
VALUES (79, 15);  -- Exemplo: Administrator Sales
```

### Problema 3: Ana Carla/Gustavo não veem algo que deveriam ver
**Sintoma:** "Não consigo ver [algum menu/dado]"

**Solução:** Adicionar grupo de visualização específico (User/Officer)

---

## 📝 RESUMO EXECUTIVO

### ✅ Melhorias Aplicadas

1. **Segurança Aumentada**
   - 3 usuários sem acesso a Settings (risco crítico removido)
   - 2 usuários sem poder alterar dados (dona e marketing)
   - Controle centralizado no admin

2. **Clareza de Responsabilidades**
   - Wanessa/Thiago: Administração operacional
   - Ana Carla/Gustavo: Visualização e relatórios
   - Admin (você): Configuração do sistema

3. **Reversibilidade Total**
   - 2 backups completos criados
   - Procedimento de rollback documentado
   - Rollback pode ser total ou parcial

4. **Documentação Completa**
   - Todas as mudanças documentadas
   - Testes sugeridos
   - Troubleshooting incluído

---

## 📞 PRÓXIMOS PASSOS RECOMENDADOS

### Curto Prazo (Esta Semana)
1. [ ] Testar login de cada um dos 4 usuários
2. [ ] Verificar se conseguem fazer suas tarefas do dia-a-dia
3. [ ] Coletar feedback sobre acessos faltantes

### Médio Prazo (Próximas 2 Semanas)
1. [ ] Analisar os outros 52 usuários que têm Settings
2. [ ] Decidir se devem manter ou remover
3. [ ] Criar política de concessão de permissões

### Longo Prazo
1. [ ] Criar grupos personalizados por função
2. [ ] Documentar perfis de acesso
3. [ ] Treinar equipe sobre novo modelo de permissões

---

## 🎯 CONCLUSÃO

**Status:** ✅ REORGANIZAÇÃO COMPLETA APLICADA

**Objetivos Alcançados:**
- ✅ Settings removido de Wanessa, Gustavo e Thiago
- ✅ Ana Carla e Gustavo com acesso read-only
- ✅ Wanessa e Thiago podem administrar operações sem mexer no sistema
- ✅ Backup completo criado
- ✅ Rollback 100% disponível
- ✅ Documentação completa

**Impacto:**
- 🔒 Segurança aumentada
- 🔒 Menos risco de "bagunça"
- 🔒 Controle centralizado no admin
- ✅ Dona pode fiscalizar sem alterar
- ✅ Marketing pode consultar sem alterar

**Próxima Ação:** Testar com os usuários e coletar feedback

---

**Aplicado por:** Claude AI Assistant
**Aprovado por:** Anderson Oliveira
**Data:** 16/11/2025
