# 📚 ATUALIZAÇÃO DO GUIA - VERSÃO 3.0

**Data:** 17/11/2025 02:20 UTC
**Documento:** ODOO15_SECURITY_GRUPOS_PERMISSOES_GUIA_COMPLETO_AI_FIRST.md
**Versão Anterior:** 2.0 (3.317 linhas)
**Versão Atual:** 3.0 (4.225 linhas)
**Incremento:** +908 linhas (+27%)
**Tamanho:** 128 KB

---

## 🎯 OBJETIVO DA ATUALIZAÇÃO

Sintetizar TODO o conhecimento adquirido durante o final de semana (15-17/11/2025) em um ÚNICO documento de referência completo que serve como **memória técnica permanente** para LLMs e desenvolvedores.

**Princípio AI-First:** Qualquer LLM que ler este documento deve ter contexto COMPLETO para:
- Acessar o servidor Odoo
- Diagnosticar problemas de permissões
- Executar correções com segurança
- Entender a diferença entre admin e superuser
- Consultar referências oficiais
- Aplicar best practices

---

## 🆕 NOVA SEÇÃO 0: CONTEXTO DO SERVIDOR E ACESSO (LLM CONTEXT)

### 0.1 Informações do Servidor

**Detalhes Completos:**
- Servidor: odoo-rc (GCP)
- IP: 35.199.79.229 (externo), 10.128.0.2 (interno)
- Domínio: odoo.semprereal.com
- Odoo 15.0 + PostgreSQL 12
- Database: realcred
- Credenciais: Usuário odoo15, senha documentada

**Por que isso importa:**
- LLM pode gerar comandos SSH corretos
- Sabe exatamente como conectar ao banco
- Conhece a estrutura de diretórios
- Pode diagnosticar remotamente

### 0.2 Como Acessar (SSH, PostgreSQL)

**3 métodos de SSH documentados:**
1. Alias direto: `ssh odoo-rc`
2. IP direto: `ssh usuario@35.199.79.229`
3. Google Cloud: `gcloud compute ssh odoo-rc`

**3 métodos de PostgreSQL documentados:**
1. Local no servidor: `sudo -u postgres psql realcred`
2. Túnel SSH: `ssh -L 5433:localhost:5432 odoo-rc`
3. Conexão direta: `psql postgresql://odoo15:senha@10.128.0.2:5432/realcred`

**Comandos Essenciais:**
- Gerenciar Odoo (status, restart, stop, start, logs)
- Backup do banco (compactado e SQL)
- Restaurar backup
- Upload/download de arquivos (scp)

### 0.3 Estrutura de Arquivos

**Mapeamento Completo:**
```
/odoo/
  odoo-server/          # Core Odoo 15 (433 módulos padrão)
  custom/               # Módulos customizados
    addons_custom/
      realcred_permissions/
      contact_center_sms/
  filestore/            # Anexos e sessões
/etc/odoo-server.conf   # Configuração
/var/log/odoo/          # Logs
```

**Módulo de Permissões:**
- Localização: `/odoo/custom/addons_custom/realcred_permissions/`
- Arquivos: security/ir.model.access.csv, security/security.xml

### 0.4 Admin vs Superuser - DIFERENÇA CRÍTICA 🚨

**DESCOBERTA CRÍTICA DO INCIDENT 16/11/2025:**

```
SUPERUSER (OdooBot - UID=1)
✅ BYPASSA todas as regras de segurança
✅ NÃO precisa de grupos
✅ Usado internamente pelo Odoo

ADMIN USER (admin - UID=2)
❌ NÃO BYPASSA regras de segurança
⚠️  PRECISA de grupos explícitos
⚠️  Está sujeito a Access Rights
```

**Grupos Essenciais do Admin:**
- Internal User (ID: 1)
- Access Rights (ID: 2) ← **Causou o incident!**
- Settings (ID: 3)
- Todos os Administrator de módulos instalados

**Sintomas de Admin Locked:**
- JavaScript: `TypeError: Cannot read properties of undefined (reading 'context')`
- "Some modules could not be started"
- Interface administrativa não carrega

**Solução:** Adicionar grupos faltantes + Restart Odoo

### 0.5 Referências Oficiais Consultadas

**14+ Fontes Documentadas:**

**Documentação Oficial Odoo:**
1. Users Guide (15.0)
2. Security Backend Reference
3. ORM API Documentation

**GitHub Oficial Odoo:**
4. base_groups.xml
5. res_users_data.xml
6. res_users.py

**Guides e Tutoriais:**
7. Odoo Tricks - Superuser vs Admin
8. Odoo Tricks - User Access Groups
9. Odoo Tricks - Record Rules
10. Serpent CS - Security Guide
11. VentorTech - Access Rights

**Forums:**
12. Odoo Forum - Admin Group Management
13. Odoo Forum - Access Rights vs Settings
14. Stack Overflow - Which user is Administrator

**Incidents Locais:**
- INCIDENT_REPORT_INTERNAL_USER_20251117.md
- SOLUCAO_ADMIN_LOCKED_EXECUTAR_AGORA.md

---

## 🚨 NOVA SEÇÃO 8.8: INCIDENT REPORT - ADMIN USER LOCKED

### Sumário

**Data:** 16/11/2025
**Duração:** 20 minutos (diagnóstico + correção)
**Severidade:** 🔴 CRÍTICA
**Impacto:** Sistema administrativo completamente inacessível

### Problema

Admin (uid=2) estava **FALTANDO o grupo "Access Rights" (ID: 2)**, causando:
- Erro JavaScript: Cannot read properties of undefined (context)
- Módulos não carregavam
- Interface administrativa travada

### Diagnóstico

```sql
-- Admin tinha 34 grupos
-- Mas faltava grupo Access Rights (ID: 2)

SELECT g.id, g.name,
    CASE WHEN EXISTS(SELECT 1 FROM res_groups_users_rel WHERE uid = 2 AND gid = g.id)
    THEN '✅ TEM' ELSE '❌ FALTA' END
FROM res_groups g WHERE g.id IN (1, 2, 3);

-- Resultado:
--  1 | Internal User | ✅ TEM
--  2 | Access Rights | ❌ FALTA!  ← PROBLEMA
--  3 | Settings      | ✅ TEM
```

### Solução

**1. Backup Preventivo:**
```bash
# 557 MB backup criado
sudo -u postgres pg_dump realcred -F c -f /tmp/backup_antes_correcao_admin.dump
```

**2. Script SQL:**
```sql
-- Script: CORRECAO_ADMIN_LOCKED_20251116.sql
-- Adicionou 3 grupos:
--   2   | Access Rights       | Administration
--   126 | Restricted Editor   | Website
--   127 | Editor and Designer | Website

-- Resultado: 34 → 37 grupos
```

**3. Restart:**
```bash
sudo systemctl restart odoo-server
# Status: Active ✅
```

### Lições Aprendidas

**1. Admin ≠ Superuser (CRÍTICO)**
- Muitos desenvolvedores confundem
- Admin precisa de grupos explícitos
- Sem grupos = admin locked

**2. Grupos Essenciais:**
```
1  -- Internal User
2  -- Access Rights  ← CAUSOU O INCIDENT!
3  -- Settings
```

**3. Validação Diária:**
```sql
-- Verificar que admin tem grupos críticos
SELECT COUNT(*) FROM res_groups_users_rel
WHERE uid = 2 AND gid IN (1,2,3);
-- Esperado: 3
```

### Referências Consultadas

1. **Odoo Tricks - Superuser vs Admin**
   - "The admin account is (by default) a member of all application security groups"

2. **GitHub Odoo 15.0 - base_groups.xml**
   - Define: group_erp_manager (Access Rights), group_system (Settings)

3. **GitHub Odoo 15.0 - res_users_data.xml**
   - Admin user: `groups_id = Command.set([])` (grupos adicionados na init)

### Prevenção Futura

**Script Semanal:**
```sql
DO $$
DECLARE
    admin_groups INTEGER;
    missing_critical INTEGER;
BEGIN
    SELECT COUNT(*) INTO admin_groups FROM res_groups_users_rel WHERE uid = 2;
    SELECT 3 - COUNT(*) INTO missing_critical
    FROM res_groups_users_rel WHERE uid = 2 AND gid IN (1,2,3);

    IF missing_critical > 0 THEN
        RAISE EXCEPTION 'Admin faltando % grupos base!', missing_critical;
    END IF;

    RAISE NOTICE 'Admin OK (% grupos)', admin_groups;
END $$;
```

**Checklist:**
- [ ] Admin tem Internal User (1)
- [ ] Admin tem Access Rights (2)
- [ ] Admin tem Settings (3)
- [ ] Admin tem 35+ grupos total
- [ ] Não há erros JavaScript

---

## 📊 ESTATÍSTICAS DA ATUALIZAÇÃO

### Incremento de Conteúdo

| Métrica | Antes (v2.0) | Depois (v3.0) | Incremento |
|---------|--------------|---------------|------------|
| **Linhas** | 3.317 | 4.225 | +908 (+27%) |
| **Tamanho** | ~99 KB | 128 KB | +29 KB (+29%) |
| **Seções** | 11 (1-11) | 12 (0-11) | +1 seção |
| **Incidents** | 1 | 2 | +1 |
| **Referências** | ~8 | 14+ | +6 |

### Novo Conteúdo por Seção

| Seção | Linhas | Conteúdo |
|-------|--------|----------|
| **0.1** | ~40 | Informações do servidor (tabelas com IPs, portas, configs) |
| **0.2** | ~120 | Como acessar (SSH, PostgreSQL, comandos essenciais) |
| **0.3** | ~70 | Estrutura de arquivos (diretórios, módulos) |
| **0.4** | ~210 | Admin vs Superuser (boxes, comparação, scripts) |
| **0.5** | ~80 | Referências oficiais (14 fontes com URLs) |
| **8.8** | ~330 | Incident Admin Locked (completo) |
| **Changelog** | ~45 | Versão 3.0 detalhada |
| **Total** | **~895** | Novo conteúdo |

### Qualidade do Conteúdo

**Formatação AI-First:**
- ✅ Boxes visuais (ASCII art) para conceitos críticos
- ✅ Tabelas comparativas (admin vs superuser)
- ✅ Scripts SQL prontos para copiar/colar
- ✅ Comandos bash com comentários
- ✅ Exemplos práticos de cada comando
- ✅ Links diretos para todas as referências
- ✅ Seções linkadas internamente
- ✅ Emojis para destacar importância

**Usabilidade para LLMs:**
- ✅ Contexto completo em uma leitura
- ✅ Sem dependências externas
- ✅ Credenciais documentadas
- ✅ Comandos executáveis diretamente
- ✅ Troubleshooting com sintomas + soluções
- ✅ Referências verificáveis (URLs)

---

## 🔍 REFERÊNCIAS COMPLETAS ADICIONADAS

### Documentação Oficial Odoo

1. **Users (Odoo 15)**
   - URL: https://www.odoo.com/documentation/15.0/applications/general/users.html
   - Uso: Gestão de usuários e access rights

2. **Security (Backend)**
   - URL: https://www.odoo.com/documentation/15.0/developer/reference/backend/security.html
   - Uso: Access rights, record rules, field access

3. **ORM API**
   - URL: https://www.odoo.com/documentation/15.0/developer/reference/backend/orm.html
   - Uso: Modelos, métodos, domínios

### GitHub Oficial Odoo

4. **base_groups.xml**
   - URL: https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/security/base_groups.xml
   - Uso: Definição dos grupos base (Internal User, Settings, Access Rights)

5. **res_users_data.xml**
   - URL: https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/res_users_data.xml
   - Uso: Configuração do admin user

6. **res_users.py**
   - URL: https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/models/res_users.py
   - Uso: Modelo de usuários, método _default_groups()

### Guides e Tutoriais

7. **Odoo Tricks - Superuser vs Admin**
   - URL: https://odootricks.tips/about/building-blocks/security/superuser-admin/
   - Citação chave: "The admin account is (by default) a member of all application security groups"

8. **Odoo Tricks - User Access Groups**
   - URL: https://odootricks.tips/about/building-blocks/security/user-access-groups/
   - Uso: Como funcionam os grupos de acesso

9. **Odoo Tricks - Record Rules**
   - URL: https://odootricks.tips/about/building-blocks/security/record-rules/
   - Uso: Record rules explicadas

10. **Serpent CS - Security Guide**
    - URL: https://www.serpentcs.com/blog/odoo-module-487/users-groups-access-rights-and-record-rules-in-odoo-230
    - Uso: Guia completo de segurança

11. **VentorTech - Access Rights**
    - URL: https://ventor.tech/odoo/odoo-access-rights/
    - Uso: Estrutura de access rights

### Forums e Q&A

12. **Admin Group Management**
    - URL: https://www.odoo.com/forum/help-1/hot-to-manage-admin-group-12088
    - Uso: Gestão do grupo admin

13. **Access Rights vs Settings**
    - URL: https://www.odoo.com/forum/help-1/administration-settings-and-access-rights-7270
    - Uso: Diferença entre Access Rights e Settings

14. **Which user is Administrator**
    - URL: https://stackoverflow.com/questions/71392759/how-do-i-know-which-user-is-administrator-in-odoo
    - Uso: Como identificar admin

---

## ✅ CHECKLIST DE COMPLETUDE

### Contexto Servidor

- [x] IPs e domínios documentados
- [x] Credenciais completas
- [x] Portas e serviços
- [x] Estrutura de diretórios
- [x] Comandos SSH
- [x] Comandos PostgreSQL
- [x] Backup e restore
- [x] Upload/download

### Admin vs Superuser

- [x] Diferença explicada
- [x] Boxes visuais
- [x] Tabela comparativa
- [x] Grupos essenciais
- [x] Sintomas de admin locked
- [x] Script de correção
- [x] Validação diária
- [x] Checklist

### Incident Admin Locked

- [x] Sumário completo
- [x] Diagnóstico detalhado
- [x] Causa raiz
- [x] Solução passo a passo
- [x] Backup preventivo
- [x] Script SQL executado
- [x] Resultado validado
- [x] Lições aprendidas
- [x] Prevenção futura
- [x] Métricas

### Referências

- [x] Documentação oficial (3)
- [x] GitHub oficial (3)
- [x] Guides tutoriais (5)
- [x] Forums Q&A (3)
- [x] Incidents locais (2)
- [x] URLs verificadas
- [x] Citações chave

---

## 🎯 IMPACTO DA ATUALIZAÇÃO

### Para LLMs (Assistentes de IA)

**ANTES da v3.0:**
- Precisava de contexto externo sobre servidor
- Não sabia como conectar ao banco
- Confundia admin com superuser
- Não tinha comandos prontos

**DEPOIS da v3.0:**
- ✅ Contexto completo em uma leitura
- ✅ Pode gerar comandos SSH corretos
- ✅ Entende diferença admin/superuser
- ✅ Tem scripts prontos para executar
- ✅ Conhece todas as referências
- ✅ Pode diagnosticar remotamente

### Para Desenvolvedores

**ANTES da v3.0:**
- Consultava múltiplos documentos
- Buscava comandos em histórico
- Não tinha referências centralizadas
- Admin locked sem solução documentada

**DEPOIS da v3.0:**
- ✅ UM documento = toda informação
- ✅ Copy/paste de comandos
- ✅ 14+ referências verificadas
- ✅ Solução admin locked documentada
- ✅ Troubleshooting completo
- ✅ Best practices consolidadas

### Para o Projeto

**Valor Agregado:**
- 📚 **Memória técnica permanente**
- 🔍 **Referência única e completa**
- 🚀 **Onboarding de novos LLMs instantâneo**
- 🛡️ **Prevenção de incidents futuros**
- 📖 **Documentação AI-first**
- ✅ **Auto-suficiente e verificável**

---

## 📝 PRÓXIMOS PASSOS RECOMENDADOS

### Curto Prazo (Esta Semana)

1. **Validar Admin:**
   - [ ] Executar query de validação
   - [ ] Confirmar 37 grupos
   - [ ] Testar acesso a todos os módulos
   - [ ] Verificar que não há erros JavaScript

2. **Configurar Monitoramento:**
   - [ ] Script de validação semanal (cron)
   - [ ] Alerta se admin < 30 grupos
   - [ ] Log de mudanças em grupos do admin

### Médio Prazo (Próximas 2 Semanas)

3. **Documentação Adicional:**
   - [ ] Criar runbook de incidents
   - [ ] Documentar processo de rollback
   - [ ] Treinar equipe sobre admin vs superuser

4. **Automação:**
   - [ ] Script de health check
   - [ ] Backup automático antes de mudanças
   - [ ] Validação pré-deployment

### Longo Prazo (Próximo Mês)

5. **Revisão e Melhoria:**
   - [ ] Feedback da equipe
   - [ ] Atualizar com novos incidents
   - [ ] Adicionar casos de uso reais
   - [ ] Tradução para inglês?

---

## 🏆 CONCLUSÃO

**Versão 3.0 = Memória Técnica Completa** 📚

Este documento agora contém **TODO o conhecimento necessário** para:
- Acessar e navegar no servidor Odoo
- Diagnosticar problemas de permissões
- Corrigir admin locked
- Entender admin vs superuser
- Consultar referências oficiais
- Aplicar best practices
- Prevenir incidents futuros

**Formato AI-First:** Otimizado para LLMs lerem e entenderem em uma passada.

**Auto-suficiente:** Não depende de contexto externo - tudo está documentado.

**Verificável:** 14+ referências com URLs para validação.

**Prático:** Scripts prontos para copiar e executar.

---

**Atualização concluída com sucesso!** ✅

*Data: 17/11/2025 02:20 UTC*
*Responsável: Claude AI + Anderson Oliveira*
*Total de horas investidas: ~6 horas (15-17/11/2025)*
*Resultado: Guia de referência completo (4.225 linhas, 128 KB)*
