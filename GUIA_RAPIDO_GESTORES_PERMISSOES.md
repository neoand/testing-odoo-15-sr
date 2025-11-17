# 🎯 GUIA RÁPIDO PARA GESTORES - PERMISSÕES ODOO 15 REALCRED

**Versão:** 1.0
**Data:** 17/11/2025
**Última Atualização:** 17/11/2025
**Responsável:** TI RealCred (ti@semprereal.com)

---

## 📋 ÍNDICE

1. [Visão Rápida](#visão-rápida)
2. [Perfis Disponíveis](#perfis-disponíveis)
3. [Como Solicitar Permissões](#como-solicitar-permissões)
4. [Casos Comuns](#casos-comuns)
5. [Checklist de Onboarding](#checklist-de-onboarding)
6. [Checklist de Offboarding](#checklist-de-offboarding)
7. [Quando Escalar para TI](#quando-escalar-para-ti)
8. [Contatos](#contatos)

---

## 🎯 VISÃO RÁPIDA

### O que você precisa saber em 30 segundos:

**EXISTEM 5 PERFIS PRINCIPAIS:**
1. **Vendedor** → Vê só suas vendas e oportunidades
2. **Líder de Vendas** → Vê vendas da equipe toda
3. **Operacional** → Gerencia CRM e pedidos (sem deletar vendas)
4. **Financeiro** → Acesso total contabilidade + leitura CRM
5. **RH** → Acesso apenas ao módulo RH + Admin

**REGRA DE OURO:**
- ✅ Sempre usar perfis predefinidos (não criar grupos customizados)
- ✅ Um usuário pode ter MÚLTIPLOS perfis se necessário
- ✅ Todos têm acesso TOTAL aos Contatos (res.partner)

**TEMPO DE ATENDIMENTO:**
- Solicitações simples: **Até 2 horas**
- Solicitações complexas: **Até 1 dia útil**

---

## 👥 PERFIS DISPONÍVEIS

### 1. VENDEDOR (Salespeople)
**Cargo típico:** Consultor de Vendas, Representante Comercial

**O que pode fazer:**
- ✅ Ver, criar e editar SUAS oportunidades (CRM)
- ✅ Ver, criar e editar SEUS pedidos de venda
- ✅ Deletar SUAS oportunidades e pedidos
- ✅ CRUD completo em Contatos

**O que NÃO pode fazer:**
- ❌ Ver oportunidades/vendas de outros vendedores
- ❌ Ver relatórios consolidados
- ❌ Acessar módulos financeiros ou RH

**Grupo Odoo:** `Sales / User: Own Documents Only` (ID: 13)

---

### 2. LÍDER DE VENDAS (Sales Leader)
**Cargo típico:** Gerente de Vendas, Coordenador Comercial, Supervisor de Vendas

**O que pode fazer:**
- ✅ Ver, criar e editar TODAS as oportunidades da empresa (CRM)
- ✅ Ver, criar e editar TODOS os pedidos de venda
- ✅ Deletar oportunidades e pedidos de QUALQUER vendedor
- ✅ Acessar relatórios e dashboards consolidados
- ✅ CRUD completo em Contatos

**O que NÃO pode fazer:**
- ❌ Acessar módulos financeiros (contas a pagar/receber, contabilidade)
- ❌ Acessar módulo RH
- ❌ Configurar sistema ou instalar módulos

**Grupo Odoo:** `Sales / User: All Documents` (ID: 14)

---

### 3. OPERACIONAL (Operations Team)
**Cargo típico:** Analista de Operações, Back-office, Suporte de Vendas

**O que pode fazer:**
- ✅ Ver, criar e editar TODAS as oportunidades (CRM) - **CRUD COMPLETO**
- ✅ Deletar oportunidades
- ✅ Ver, criar e editar TODOS os pedidos de venda - **SEM DELETAR**
- ✅ CRUD completo em Contatos

**O que NÃO pode fazer:**
- ❌ Deletar pedidos de venda (sales orders)
- ❌ Acessar módulos financeiros
- ❌ Acessar módulo RH

**Grupo Odoo:** `Operacional` (ID: 154) - **CUSTOMIZADO REALCRED**

**⚠️ DIFERENÇA IMPORTANTE:**
- **CRM:** Pode deletar oportunidades
- **Vendas:** NÃO pode deletar pedidos (proteção de dados)

---

### 4. FINANCEIRO (Finance Team)
**Cargo típico:** Contador, Analista Financeiro, Controller

**O que pode fazer:**
- ✅ Acesso TOTAL aos módulos financeiros:
  - Contabilidade (journal entries, reconciliação)
  - Contas a Pagar
  - Contas a Receber
  - Relatórios fiscais
- ✅ **APENAS LEITURA** no CRM (para consultar negociações)
- ✅ CRUD completo em Contatos

**O que NÃO pode fazer:**
- ❌ Criar/editar/deletar oportunidades (CRM)
- ❌ Criar/editar/deletar pedidos de venda
- ❌ Acessar módulo RH

**Grupo Odoo:** `Accounting / Accountant` (ID: 45)

---

### 5. RH (Human Resources)
**Cargo típico:** Analista de RH, Gerente de Pessoas, DP

**O que pode fazer:**
- ✅ Acesso TOTAL ao módulo RH:
  - Cadastro de funcionários
  - Departamentos
  - Contratos
  - Férias/Ausências
  - Avaliações
- ✅ Acesso de ADMINISTRADOR (configurações do sistema)
- ✅ CRUD completo em Contatos

**O que NÃO pode fazer:**
- ❌ Acessar CRM
- ❌ Acessar Vendas
- ❌ Acessar Financeiro

**Grupo Odoo:** `HR / Officer` + `Administration / Settings` (IDs: 58 + 3)

**⚠️ ATENÇÃO:** Este é o perfil mais restritivo. Acesso APENAS ao módulo RH e configurações do sistema.

---

## 📝 COMO SOLICITAR PERMISSÕES

### NOVO COLABORADOR (Onboarding)

**PASSO 1:** Identifique o cargo
- Vendedor
- Líder de Vendas
- Operacional
- Financeiro
- RH
- Outro (especificar)

**PASSO 2:** Envie email para TI (ti@semprereal.com) com:

```
Assunto: [ODOO] Novo Usuário - [NOME DO COLABORADOR]

Dados do colaborador:
- Nome completo: [nome]
- Email corporativo: [email@semprereal.com]
- Cargo: [cargo]
- Departamento: [departamento]
- Gestor direto: [nome do gestor]
- Data de início: [DD/MM/AAAA]

Perfil de acesso solicitado:
[X] Vendedor
[ ] Líder de Vendas
[ ] Operacional
[ ] Financeiro
[ ] RH
[ ] Outro: [especificar]

Justificativa (se "Outro"):
[descrever necessidade específica]

Autorização:
- Gestor responsável: [nome]
- Email do gestor: [email]
```

**PASSO 3:** Aguarde confirmação da TI (até 2 horas)

---

### MUDANÇA DE PERMISSÕES (Usuário Existente)

**Quando solicitar:**
- Promoção interna (vendedor → líder)
- Mudança de departamento
- Necessidade temporária de acesso adicional
- Acesso especial para projeto específico

**Email para TI:**

```
Assunto: [ODOO] Alteração de Permissões - [NOME DO USUÁRIO]

Dados do usuário:
- Nome: [nome]
- Email: [email atual no sistema]
- Cargo atual: [cargo atual]
- Novo cargo (se aplicável): [novo cargo]

Alteração solicitada:
- Perfil atual: [perfil atual]
- Novo perfil: [perfil desejado]
- Motivo da mudança: [promoção/mudança de depto/temporário/projeto]
- Data de início: [DD/MM/AAAA]
- Data de término (se temporário): [DD/MM/AAAA]

Justificativa:
[explicar por que o usuário precisa do novo perfil]

Autorização:
- Gestor responsável: [nome]
- Email do gestor: [email]
```

---

### REMOÇÃO DE ACESSO (Offboarding)

**Email para TI:**

```
Assunto: [ODOO] Desativação de Usuário - [NOME]

Dados:
- Nome: [nome]
- Email: [email]
- Último dia de trabalho: [DD/MM/AAAA]
- Motivo: [demissão/desligamento/transferência]

Ações necessárias:
[ ] Desativar acesso imediatamente
[ ] Transferir oportunidades para: [nome do novo responsável]
[ ] Transferir pedidos de venda para: [nome do novo responsável]
[ ] Manter histórico visível para: [nome do gestor]

Autorização:
- Gestor: [nome]
- RH: [nome]
```

---

## 🔥 CASOS COMUNS

### CASO 1: Novo Vendedor na Equipe
**Situação:** Contratamos um novo consultor de vendas

**Solução:**
1. Perfil: **Vendedor** (Own Documents Only)
2. Tempo de setup: 1-2 horas
3. O que ele poderá fazer imediatamente:
   - Criar suas próprias oportunidades
   - Converter oportunidades em pedidos
   - Ver/editar seus contatos

**Próximos passos:**
- Gerente deve atribuir região/território (se aplicável)
- Configurar metas de vendas
- Adicionar ao time de vendas correto

---

### CASO 2: Promoção de Vendedor para Líder
**Situação:** Vendedor promovido a Gerente de Vendas

**Solução:**
1. Alterar perfil de **Vendedor** → **Líder de Vendas**
2. Tempo: 30 minutos
3. Mudanças imediatas:
   - ✅ Passa a ver TODAS as oportunidades (não só as dele)
   - ✅ Passa a ver TODOS os pedidos da empresa
   - ✅ Pode deletar/editar vendas de outros vendedores
   - ✅ Acessa dashboards e relatórios consolidados

**⚠️ ATENÇÃO:** Comunicar à equipe sobre a mudança!

---

### CASO 3: Analista que precisa de múltiplos acessos
**Situação:** Analista de Operações que também precisa ver dados financeiros

**Solução:**
1. Perfil PRINCIPAL: **Operacional**
2. Perfil ADICIONAL: **Financeiro** (apenas leitura em CRM)
3. Resultado final:
   - CRM: CRUD completo (do Operacional)
   - Vendas: CRU sem delete (do Operacional)
   - Financeiro: Acesso total (do Financeiro)

**⚠️ IMPORTANTE:** Sempre especificar qual é o perfil PRINCIPAL do usuário.

---

### CASO 4: Acesso temporário para auditoria
**Situação:** Auditor externo precisa de acesso read-only por 15 dias

**Solução:**
1. Criar usuário temporário
2. Perfil: **Portal** com acesso customizado
3. **IMPORTANTE:** Especificar data de EXPIRAÇÃO
4. Email para TI deve incluir:
   - Data de início: [DD/MM/AAAA]
   - Data de término: [DD/MM/AAAA]
   - Módulos que pode acessar: [listar]
   - Permissões: **APENAS LEITURA**

---

### CASO 5: Usuário não consegue criar oportunidade
**Situação:** Vendedor reclama que não consegue criar leads/oportunidades

**DIAGNÓSTICO RÁPIDO:**

**1. Verificar perfil do usuário:**
- Perfil correto? (Vendedor, Líder ou Operacional)
- Está no grupo "Sales / User"?

**2. Verificar se está ativo:**
- Usuário está marcado como "Active" no sistema?

**3. Verificar time de vendas:**
- Usuário está associado a um Sales Team?
- O time está ativo?

**4. Se TUDO estiver OK e ainda não funcionar:**
- Escalar para TI IMEDIATAMENTE
- Incluir print do erro (se houver)
- Informar exatamente qual ação o usuário tentou fazer

**SLA:** Problemas de acesso a CRM são **PRIORIDADE ALTA** (resolução em até 2 horas).

---

## ✅ CHECKLIST DE ONBOARDING

Use este checklist ao solicitar acesso para novo colaborador:

### ANTES DE SOLICITAR:
- [ ] Tenho o email corporativo do colaborador (@semprereal.com)
- [ ] Sei qual o cargo exato
- [ ] Sei qual departamento/equipe
- [ ] Sei qual perfil de acesso necessário
- [ ] Tenho autorização do gestor direto

### INFORMAÇÕES PARA TI:
- [ ] Nome completo
- [ ] Email corporativo
- [ ] Cargo
- [ ] Departamento
- [ ] Data de início
- [ ] Perfil solicitado (Vendedor/Líder/Operacional/Financeiro/RH)
- [ ] Nome do gestor responsável
- [ ] Email do gestor para confirmação

### APÓS CRIAÇÃO DO USUÁRIO:
- [ ] Usuário recebeu email com credenciais
- [ ] Usuário conseguiu fazer primeiro login
- [ ] Usuário consegue acessar módulos necessários
- [ ] Usuário foi adicionado ao Sales Team correto (se vendas)
- [ ] Configurar assinatura de email (se necessário)
- [ ] Treinar usuário nos processos básicos

**TEMPO TOTAL ESTIMADO:** 1-2 horas (da solicitação até usuário operacional)

---

## 🔒 CHECKLIST DE OFFBOARDING

Use este checklist ao desligar um colaborador:

### IMEDIATO (Último dia de trabalho):
- [ ] Desativar usuário no Odoo
- [ ] Transferir oportunidades abertas para outro vendedor
- [ ] Transferir pedidos em andamento
- [ ] Atualizar contatos (trocar responsável)
- [ ] Remover de todos os Sales Teams

### ATÉ 24H APÓS DESLIGAMENTO:
- [ ] Verificar se há dados importantes para exportar
- [ ] Garantir que relatórios históricos ainda funcionam
- [ ] Atualizar organograma (se aplicável)
- [ ] Comunicar time sobre redistribuição de contas

### ATÉ 7 DIAS:
- [ ] Revisar permissões da equipe (se era líder)
- [ ] Verificar se há processos bloqueados esperando aprovação dele
- [ ] Arquivar dados conforme política de retenção

**⚠️ NUNCA DELETAR USUÁRIOS!** Sempre DESATIVAR. Deletar quebra histórico de vendas.

---

## 🚨 QUANDO ESCALAR PARA TI

### ESCALAR IMEDIATAMENTE (Prioridade Alta):

1. **Usuário não consegue criar oportunidades/vendas**
   - SLA: 2 horas
   - Impacto: Perda de vendas

2. **Usuário vê dados que NÃO deveria ver**
   - SLA: 1 hora
   - Impacto: Segurança/conformidade

3. **Múltiplos usuários reportando mesmo problema**
   - SLA: 1 hora
   - Impacto: Operação da empresa

4. **Desligamento de funcionário (acesso deve ser revogado)**
   - SLA: Imediato
   - Impacto: Segurança

### ESCALAR EM 1 DIA ÚTIL (Prioridade Média):

1. **Usuário precisa de perfil customizado**
2. **Mudança de departamento/cargo**
3. **Acesso temporário para projeto**
4. **Dúvidas sobre qual perfil usar**

### NÃO PRECISA ESCALAR (Resolva você mesmo):

1. **Usuário esqueceu senha**
   - Usar "Reset Password" na tela de login

2. **Usuário quer mudar idioma/timezone**
   - Preferences → Language/Timezone

3. **Dúvidas sobre como usar módulo**
   - Ver FAQ de Permissões ou treinamento do módulo

---

## 📞 CONTATOS

### TI RealCred
**Email:** ti@semprereal.com
**Horário:** Segunda a Sexta, 8h-18h
**SLA:**
- Prioridade Alta: 1-2 horas
- Prioridade Média: 1 dia útil
- Prioridade Baixa: 3 dias úteis

### Emergências (Fora do horário comercial)
**Telefone:** [Inserir telefone de plantão]
**Critérios para emergência:**
- Sistema totalmente fora do ar
- Vazamento de dados
- Incidente de segurança

### Documentação Adicional
- **FAQ Completo:** `/odoo_15_sr/FAQ_PERMISSOES_ODOO15_REALCRED.md`
- **Matriz de Permissões:** `/odoo_15_sr/MATRIZ_PERMISSOES_REALCRED.md`
- **Plano de Reorganização:** `/odoo_15_sr/PLANO_REORGANIZACAO_PERMISSOES_ODOO15.md`

---

## 📊 RESUMO EXECUTIVO

| Perfil | Cargo Típico | CRM | Vendas | Financeiro | RH |
|--------|--------------|-----|--------|------------|-----|
| **Vendedor** | Consultor | CRUD (próprias) | CRUD (próprias) | ❌ | ❌ |
| **Líder** | Gerente | CRUD (todas) | CRUD (todas) | ❌ | ❌ |
| **Operacional** | Analista | CRUD (todas) | CRU (todas) | ❌ | ❌ |
| **Financeiro** | Contador | Read-only | ❌ | CRUD | ❌ |
| **RH** | Analista RH | ❌ | ❌ | ❌ | CRUD |

**Legenda:**
- CRUD = Create, Read, Update, Delete (acesso completo)
- CRU = Create, Read, Update (SEM delete)
- Read-only = Apenas leitura
- ❌ = Sem acesso

---

## 🎯 DICAS FINAIS

1. **Sempre use perfis predefinidos** - Não peça perfis "customizados" a menos que REALMENTE necessário

2. **Um usuário pode ter múltiplos perfis** - Se alguém precisa de CRM + Financeiro, pode ter ambos os grupos

3. **Menos é mais** - Peça apenas os acessos REALMENTE necessários para o trabalho

4. **Documente tudo** - Sempre envie email formal com justificativa e autorização

5. **Revise periodicamente** - A cada 6 meses, revise se sua equipe ainda precisa dos mesmos acessos

6. **Comunique mudanças** - Sempre avise a equipe quando houver mudanças de permissões

7. **Treine sua equipe** - Garanta que todos saibam usar os módulos que têm acesso

8. **Nunca compartilhe senhas** - Cada pessoa deve ter seu próprio usuário

---

**FIM DO GUIA**

**Versão:** 1.0
**Última atualização:** 17/11/2025
**Responsável:** TI RealCred
**Contato:** ti@semprereal.com
