# MATRIZ DE PERMISSÕES - ODOO 15 REALCRED

**Versão:** 2.0 (Pós-Fase 4)
**Data:** 17/11/2025
**Responsável:** TI RealCred
**Status:** ✅ Atualizado e Validado

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Matriz Completa: Cargo × Perfil × Módulos](#matriz-completa)
3. [Detalhamento por Perfil](#detalhamento-por-perfil)
4. [Hierarquia de Grupos](#hierarquia-de-grupos)
5. [Como Atribuir Grupos](#como-atribuir-grupos)
6. [Casos de Uso Comuns](#casos-de-uso-comuns)

---

## 🎯 VISÃO GERAL

### Princípio Fundamental

**NUNCA atribua grupos "implied" manualmente!**

❌ **ERRADO:**
- Atribuir Internal User (1) + Technical Features (6) + Mail Template Editor (12)...

✅ **CERTO:**
- Atribuir apenas Sales / User: Own Documents Only (13)
- O Odoo aplica automaticamente os 22 grupos implied

### Grupos por Nível

| Nível | Total Grupos | Descrição |
|-------|--------------|-----------|
| **Nível 1** | 1-3 grupos | Apenas grupos "pai" (Sales, Accounting, HR, etc.) |
| **Nível 2** | 20-25 grupos | Grupos "pai" + implied automaticamente |
| **Nível 3** | 40+ grupos | ❌ **INCORRETO** - Grupos redundantes atribuídos manualmente |

**Após Fase 3:** Média de 17 grupos/usuário (Nível 2) ✅

---

## 📊 MATRIZ COMPLETA

### Legenda de Permissões

- **CRUD:** Create, Read, Update, Delete (acesso total)
- **CRU:** Create, Read, Update (sem delete)
- **R:** Read apenas (somente leitura)
- **-:** Sem acesso
- **Own:** Apenas seus próprios documentos
- **Team:** Documentos do seu time
- **All:** Todos os documentos

---

### Tabela Principal

| Cargo / Função | Perfil Odoo | Grupo ID | Contatos | CRM | Vendas | Financeiro | RH | Projetos |
|----------------|-------------|----------|----------|-----|--------|------------|----|---------|
| **Vendedor Júnior** | User: Own Documents Only | 13 | CRUD | Own CRUD | Own CRU | - | - | R |
| **Vendedor Pleno** | User: All Documents | 14 | CRUD | Team CRUD | Team CRUD | - | - | R |
| **Líder de Vendas** | User: All Documents | 14 | CRUD | Team CRUD | Team CRUD | - | - | CRU |
| **Gerente de Vendas** | Sales Administrator | 15 | CRUD | All CRUD | All CRUD | R | - | CRU |
| **Analista Operacional** | Operacional | 154 | CRUD | All CRUD | All CRU | - | - | R |
| **Back-Office** | Operacional | 154 | CRUD | All CRUD | All CRU | - | - | R |
| **Inside Sales** | Operacional | 154 | CRUD | All CRUD | All CRU | - | - | R |
| **Analista Financeiro** | Accountant | 45 | CRUD | R | R | CRUD | - | - |
| **Contador** | Accountant | 45 | CRUD | R | R | CRUD | - | - |
| **Controller** | Advisor | 46 | CRUD | R | R | CRUD | - | - |
| **Analista RH** | HR PRO / User | 93 | CRUD | - | - | - | CRUD | - |
| **Gerente RH** | HR PRO / Manager | 94 | CRUD | - | - | - | CRUD | - |
| **Diretor RH** | HR PRO / Admin | 95 | CRUD | - | - | - | CRUD | - |
| **Gerente de Projetos** | Project / Manager | - | CRUD | R | R | - | - | CRUD |
| **Analista Marketing** | (custom) | - | CRUD | R | R | - | - | R |
| **Administrador Sistema** | Settings / Administration | 2 | CRUD | CRUD | CRUD | CRUD | CRUD | CRUD |

---

## 🔍 DETALHAMENTO POR PERFIL

---

### 1. Vendedor Júnior

**Grupo:** Sales / User: Own Documents Only (ID: 13)

**Total de Grupos:** ~22 (1 atribuído + 21 implied)

#### Permissões Detalhadas

| Módulo | Modelo | Permissão | Observação |
|--------|--------|-----------|------------|
| **Contatos** | res.partner | CRUD | Todos os contatos (desde Fase 2) |
| **CRM** | crm.lead | CRUD | Apenas onde `user_id = você` |
| **CRM** | crm.team | R | Pode ver times, não editar |
| **CRM** | crm.stage | R | Pode ver estágios, não criar novos |
| **Vendas** | sale.order | CRU | Apenas seus pedidos, não delete |
| **Vendas** | sale.order.line | CRU | Linhas dos seus pedidos |
| **Produtos** | product.product | R | Catálogo completo de produtos |
| **Produtos** | product.template | R | Templates de produtos |

#### O Que VÊ no Menu

✅ **Vê:**
- CRM (apenas suas oportunidades)
- Vendas (apenas seus pedidos)
- Contatos
- Produtos (catálogo)

❌ **NÃO Vê:**
- Relatórios consolidados do time
- Oportunidades de outros vendedores
- Configurações de CRM/Vendas
- Módulos financeiros
- Módulos de RH

#### Casos de Uso

- Criar oportunidade para si mesmo
- Criar pedido de venda
- Editar suas oportunidades
- Adicionar/editar contatos

---

### 2. Líder de Vendas / Vendedor Pleno

**Grupo:** Sales / User: All Documents (ID: 14)

**Total de Grupos:** ~23 (1 atribuído + 22 implied)

#### Permissões Detalhadas

| Módulo | Modelo | Permissão | Escopo |
|--------|--------|-----------|--------|
| **Contatos** | res.partner | CRUD | Todos |
| **CRM** | crm.lead | CRUD | Onde `team_id = seu time` |
| **CRM** | crm.lead (sem dono) | CRUD | Oportunidades sem vendedor |
| **Vendas** | sale.order | CRUD | Do seu time |
| **Produtos** | product.product | CRUD | Todos |

#### Diferença do Vendedor Júnior

| Aspecto | Júnior (13) | Pleno (14) |
|---------|-------------|------------|
| **Oportunidades** | Apenas suas | Todo o time |
| **Pedidos** | Apenas seus | Todo o time |
| **Produtos** | Leitura | CRUD |
| **Reatribuir** | ❌ Não | ✅ Sim |

#### O Que MAIS Pode Fazer

- Reatribuir oportunidades entre membros do time
- Ver todas oportunidades do time
- Dar suporte a outros vendedores
- Criar produtos novos

---

### 3. Gerente de Vendas

**Grupo:** Sales / Administrator (ID: 15)

**Total de Grupos:** ~24 (1 atribuído + 23 implied)

#### Permissões Detalhadas

| Módulo | Ação | Permissão |
|--------|------|-----------|
| **CRM** | Ver oportunidades | TODAS (todos os times) |
| **CRM** | Configurar estágios | ✅ Sim |
| **CRM** | Criar/editar times | ✅ Sim |
| **CRM** | Configurar pipelines | ✅ Sim |
| **Vendas** | Ver pedidos | TODOS |
| **Vendas** | Deletar pedidos | ✅ Sim |
| **Vendas** | Configurar | ✅ Sim |

#### Acesso a Configurações

✅ **Pode Configurar:**
- Times de vendas (membros, responsável)
- Estágios do pipeline CRM
- Tipos de atividades
- Regras de pontuação de leads
- Templates de email de vendas
- Metas e quotas
- Produtos e variantes

❌ **NÃO Pode:**
- Configurações do sistema (apenas Settings/Administration)
- Instalar/desinstalar módulos
- Gerenciar usuários e permissões
- Configurações financeiras

---

### 4. Operacional (Back-Office, Inside Sales)

**Grupo:** Operacional (ID: 154) - Customizado RealCred

**Total de Grupos:** ~23 (1 atribuído + 22 implied)

#### Permissões Detalhadas

| Módulo | Modelo | Create | Read | Update | Delete | Observação |
|--------|--------|--------|------|--------|--------|------------|
| **CRM** | crm.lead | ✅ | ✅ | ✅ | ✅ | CRUD completo |
| **Vendas** | sale.order | ✅ | ✅ | ✅ | ❌ | **SEM DELETE** |
| **Vendas** | sale.order.line | ✅ | ✅ | ✅ | ❌ | **SEM DELETE** |
| **Contatos** | res.partner | ✅ | ✅ | ✅ | ✅ | CRUD completo |
| **Produtos** | product.product | ❌ | ✅ | ✅ | ❌ | Editar, não criar |

#### Por Que SEM Delete em Vendas?

**Segurança:**
- Pedidos confirmados NÃO devem ser deletados
- Devem ser **cancelados** (mantém histórico)
- Previne perda acidental de dados
- Mantém auditoria completa

**Como Cancelar Pedido:**
1. Abrir pedido
2. Botão "Cancelar"
3. Pedido fica com state = "cancel"
4. Histórico mantido

#### Casos de Uso Típicos

- Criar oportunidades para vendedores externos
- Dar suporte em negociações complexas
- Criar pedidos de vendas pós-fechamento
- Corrigir erros em pedidos (valores, produtos)
- Adicionar observações e follow-ups
- Atualizar estágios de oportunidades

#### Diferença do Líder de Vendas

| Aspecto | Líder (14) | Operacional (154) |
|---------|------------|-------------------|
| **CRM** | Team CRUD | All CRUD |
| **Vendas Delete** | ✅ Sim | ❌ Não |
| **Escopo CRM** | Apenas do time | Todos os times |
| **Foco** | Gerenciar vendedores | Dar suporte operacional |

---

### 5. Financeiro (Accountant)

**Grupo:** Accounting / Accountant (ID: 45)

**Total de Grupos:** ~variável (depende de módulos financeiros instalados)

#### Permissões Detalhadas

| Módulo | Permissão | Observação |
|--------|-----------|------------|
| **Contabilidade** | CRUD | Plano de contas, lançamentos, diário |
| **Faturamento** | CRUD | Criar/editar faturas |
| **Pagamentos** | CRUD | Registrar pagamentos |
| **CRM** | R | **APENAS LEITURA** (contexto) |
| **Vendas** | R | **APENAS LEITURA** (contexto) |
| **Relatórios** | R | Financeiros, balanços, DRE |

#### Por Que Acesso a CRM/Vendas?

**Necessidade de Contexto:**
- Entender origem de faturas
- Análise de margem por oportunidade
- Projeções financeiras baseadas em pipeline
- Conciliação de vendas × recebimentos

**Limitação de Segurança:**
- NÃO pode criar oportunidades
- NÃO pode editar dados comerciais
- NÃO pode alterar valores de vendas
- Apenas **leitura** para análise

#### Odoo Community vs Enterprise

⚠️ **Atenção:** RealCred usa Odoo **Community**

| Funcionalidade | Community | Enterprise |
|----------------|-----------|------------|
| **Faturamento** | ✅ Sim | ✅ Sim |
| **Pagamentos** | ✅ Sim | ✅ Sim |
| **Contabilidade Básica** | ✅ Sim | ✅ Sim |
| **Contabilidade Avançada** | ❌ Não | ✅ Sim |
| **Plano de Contas** | ⚠️ Limitado | ✅ Completo |
| **Conciliação Bancária** | ⚠️ Básica | ✅ Avançada |

---

### 6. RH (HR PRO)

**Grupos:** HR PRO / User (93), Manager (94), Admin (95)

#### Permissões por Nível

| Nível | Grupo | Funcionários | Férias | Ponto | Salários | Avaliações |
|-------|-------|--------------|--------|-------|----------|------------|
| **User** | 93 | R | CRUD próprias | CRUD próprio | ❌ | R próprias |
| **Manager** | 94 | CRUD equipe | CRUD equipe | R equipe | R equipe | CRUD equipe |
| **Admin** | 95 | CRUD todos | CRUD todos | CRUD todos | CRUD todos | CRUD todos |

#### Dados Sensíveis Protegidos

❌ **Usuários NÃO-RH NÃO vêem:**
- Salários de funcionários
- Avaliações de desempenho
- Dados médicos
- Documentos pessoais
- Férias de outros (exceto próprias)
- Informações bancárias

✅ **Usuários Comuns PODEM ver:**
- Próprias férias e saldo
- Próprio ponto eletrônico
- Próprios dados cadastrais
- Organograma da empresa (dependendo de config)

---

## 🏗️ HIERARQUIA DE GRUPOS

### Diagrama Completo

```
Settings / Administration (2) ← Acesso TOTAL
│
├─ Sales / Administrator (15)
│  └─ Sales / User: All Documents (14)
│     └─ Sales / User: Own Documents Only (13)
│        └─ Internal User (1)
│           └─ 19 grupos técnicos (implied)
│
├─ Operacional (154) ← RealCred Custom
│  └─ Sales / User: All Documents (14)
│     └─ Sales / User: Own Documents Only (13)
│        └─ Internal User (1)
│           └─ 19 grupos técnicos
│
├─ Accounting / Accountant (45)
│  └─ Internal User (1)
│     └─ 19 grupos técnicos
│
└─ HR PRO / Admin (95)
   └─ HR PRO / Manager (94)
      └─ HR PRO / User (93)
         └─ Internal User (1)
            └─ 19 grupos técnicos
```

### Grupos Técnicos (Implied Automaticamente)

Quando você atribui **Internal User (1)**, o Odoo aplica automaticamente:

1. Technical Features (6)
2. Mail Template Editor (12)
3. Show Lead Menu (16)
4. Show Recurring Revenues Menu (17)
5. Enable form view for phone calls (19)
6. Enable PIN use (26)
7. Manage Multiple Units of Measure (30)
8. Analytic Accounting (39)
9. Analytic Accounting Tags (40)
10. Tax display B2B (41)
11. A warning can be set on a partner (Account) (47)
12. Lock Confirmed Sales (59)
13. Use Subtasks (66)
14. Use Rating on Project (67)
15. Use Stages on Project (68)
16. Use Recurring Tasks (69)
17. Use Task Dependencies (70)
18. Send an automatic reminder email to confirm delivery (74)
19. Access to Private Addresses (11)

**Total:** 19 grupos técnicos

---

## 🎓 COMO ATRIBUIR GRUPOS

### Passo a Passo

1. **Ir em Configurações → Usuários & Empresas → Usuários**

2. **Clicar no usuário**

3. **Aba "Direitos de Acesso"**

4. **Atribuir APENAS o grupo principal:**

   ✅ **CERTO:**
   - Marcar: Sales / User: Own Documents Only
   - Odoo aplica automaticamente Internal User + 19 técnicos
   - **Total:** ~22 grupos

   ❌ **ERRADO:**
   - Marcar: Sales / User: Own Documents Only
   - E TAMBÉM marcar: Internal User
   - E TAMBÉM marcar: Technical Features
   - etc...
   - **Resultado:** Grupos redundantes!

5. **Salvar**

6. **Usuário faz logout/login** (aplicar mudanças)

---

### Checklist de Atribuição

Antes de atribuir grupos, pergunte:

- [ ] Qual é o cargo/função da pessoa?
- [ ] Quais módulos ela precisa acessar?
- [ ] Ela vê apenas seus docs, do time, ou todos?
- [ ] Ela precisa de permissão de delete?
- [ ] Há dados sensíveis que ela NÃO deve ver?

**Então escolha O GRUPO MAIS ESPECÍFICO:**

| Se a pessoa é... | Atribua... |
|------------------|------------|
| Vendedor júnior/individual | Sales / User: Own Documents Only (13) |
| Vendedor pleno/líder de equipe | Sales / User: All Documents (14) |
| Gerente de vendas | Sales / Administrator (15) |
| Back-office/operações | Operacional (154) |
| Contador/financeiro | Accounting / Accountant (45) |
| Analista RH | HR PRO / User (93) |
| Gerente RH | HR PRO / Manager (94) |
| Administrador do sistema | Settings / Administration (2) |

---

## 📚 CASOS DE USO COMUNS

### Caso 1: Novo Vendedor Contratado

**Situação:** João foi contratado como vendedor júnior.

**Ação:**
1. Criar usuário: joão@realcred.com.br
2. Atribuir grupo: **Sales / User: Own Documents Only (13)**
3. Atribuir time de vendas: Time Sul
4. Salvar

**Resultado:**
- João vê apenas SUAS oportunidades
- Pode criar pedidos para si
- Tem acesso a contatos e produtos
- **Total:** ~22 grupos (automaticamente)

---

### Caso 2: Vendedor Promovido a Líder

**Situação:** Maria era vendedora júnior e foi promovida a líder de equipe.

**Ação:**
1. Editar usuário maria@realcred.com.br
2. **Remover:** Sales / User: Own Documents Only (13)
3. **Adicionar:** Sales / User: All Documents (14)
4. Definir como líder do time no módulo Vendas
5. Salvar

**Resultado:**
- Maria agora vê TODAS oportunidades do time
- Pode reatribuir oportunidades
- Pode editar oportunidades de outros vendedores do time

---

### Caso 3: Back-Office Precisa Dar Suporte

**Situação:** Ana trabalha no back-office e precisa criar oportunidades para vendedores externos.

**Ação:**
1. Criar usuário: ana@realcred.com.br
2. Atribuir grupo: **Operacional (154)**
3. Salvar

**Resultado:**
- Ana vê TODAS oportunidades (todos times)
- Pode criar oportunidades para qualquer vendedor
- Pode criar/editar pedidos
- **NÃO pode deletar** pedidos (segurança)

---

### Caso 4: Financeiro Precisa Ver Pipeline

**Situação:** Contador Carlos precisa ver oportunidades para projeções financeiras.

**Ação:**
1. Editar usuário carlos@realcred.com.br
2. Já tem: Accounting / Accountant (45)
3. Verificar se módulo realcred_permissions está instalado
4. Carlos automaticamente tem **READ em CRM**

**Resultado:**
- Carlos vê todas oportunidades (somente leitura)
- NÃO pode criar/editar oportunidades
- Pode analisar pipeline para projeções

---

### Caso 5: Funcionário Mudou de Área

**Situação:** Pedro era vendedor e foi transferido para o RH.

**Ação:**
1. Editar usuário pedro@realcred.com.br
2. **Remover:** Sales / User: Own Documents Only (13)
3. **Adicionar:** HR PRO / User (93)
4. Salvar

**Resultado:**
- Pedro perde acesso a CRM e Vendas
- Ganha acesso a módulos de RH
- Pode gerenciar próprias férias e ver dados da equipe

---

## 🔐 POLÍTICAS DE SEGURANÇA

### Princípios Fundamentais

1. **Menor Privilégio:**
   - Conceda apenas permissões necessárias
   - Comece com grupo mais restritivo
   - Aumente conforme necessário

2. **Segregação de Funções:**
   - Quem cria pedidos NÃO aprova pagamentos
   - Quem vende NÃO faz contabilidade
   - Operacional NÃO pode deletar vendas

3. **Auditoria:**
   - Revisar grupos trimestralmente
   - Remover grupos ao desativar usuário
   - Documentar mudanças de permissões

4. **Dados Sensíveis:**
   - Salários: Apenas RH + Admin
   - Margem de lucro: Apenas Financeiro + Admin
   - Dados pessoais: Apenas RH + Próprio usuário

---

## 📞 SUPORTE E DÚVIDAS

### Para Usuários

**Dúvida:** "Não consigo ver um menu que meu colega vê"
**Resposta:** Vocês têm grupos diferentes. Consulte o FAQ ou abra chamado com TI.

**Dúvida:** "Erro: Você não tem permissão para executar esta ação"
**Resposta:** Você não tem o grupo necessário. Solicite ao gestor que abra chamado com TI justificando a necessidade.

### Para Gestores

**Solicitar Permissão:**
1. Email para: ti@realcred.com.br
2. Assunto: "Solicitação de Permissão - [Nome do Usuário]"
3. Corpo:
   - Nome e email do usuário
   - Cargo/função
   - Módulos necessários
   - Justificativa
   - Se é temporário ou permanente

**Prazo:** 24-48h úteis

### Para TI

**Referências:**
- `FAQ_PERMISSOES_ODOO15_REALCRED.md` - FAQ completo
- `RELATORIO_EXECUCAO_FASE1_PERMISSOES.md` - Fase 1
- `RELATORIO_EXECUCAO_FASE2_PERMISSOES.md` - Fase 2
- Database: Tabelas `res_groups`, `ir_model_access`, `ir_rule`

---

## 📝 REGISTRO DE MUDANÇAS

| Data | Versão | Mudanças |
|------|--------|----------|
| 17/11/2025 | 2.0 | Atualização pós-Fase 4: Documentação completa, hierarquias, casos de uso |
| 17/11/2025 | 1.5 | Pós-Fase 3: Atualização de média de grupos (17) |
| 17/11/2025 | 1.0 | Pós-Fase 2: Criação inicial com requisitos implementados |

---

**Última Atualização:** 17/11/2025
**Responsável:** TI RealCred
**Versão Odoo:** 15.0 Community
**Database:** realcred
**Status:** ✅ Ativo e Validado
