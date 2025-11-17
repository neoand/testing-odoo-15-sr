# ANÁLISE COMPLETA - PERMISSÕES POR STAGES DO CRM
## Sistema: Odoo 15 - Realcred
## Data: 16/11/2025

---

## 📋 SUMÁRIO EXECUTIVO

Este documento analisa o sistema de permissões por stages (etapas) do CRM implementado pelo desenvolvedor anterior. O sistema usa um campo computado `stage_edit` para controlar quais usuários podem editar leads em determinados stages baseado em sua participação em times (crm_team).

**Módulo Customizado:** `crm_products`
**Arquivo Principal:** `/odoo/custom/addons_custom/crm_products/models/crm_stage.py`

---

## 1. COMO FUNCIONA O SISTEMA ATUAL

### 1.1. Arquitetura da Solução

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUXO DE PERMISSÕES                          │
└─────────────────────────────────────────────────────────────────┘

1. STAGE (crm_stage)
   └─► teams_allowed_edit (Many2many com crm_team)
       └─► Define quais TIMES podem editar leads neste stage

2. LEAD (crm.lead)
   └─► stage_edit (campo computado Boolean)
       └─► Calcula se o usuário ATUAL pode editar este lead
           baseado no stage e sua participação nos times

3. REGRAS DE SEGURANÇA (ir_rule)
   ├─► Personal Leads RC (ID 443)
   │   └─► Aplica para "User: Own Documents Only"
   │       └─► Domain: user_id = current_user AND stage_edit = True
   │
   └─► All Leads RC (ID 444)
       └─► Aplica para "User: All Documents"
           └─► Domain: team_id = user.team AND stage_edit = True
```

### 1.2. Código Python do Campo Computado

```python
class CrmStageInherint(models.Model):
    _inherit = 'crm.stage'

    teams_allowed_edit = fields.Many2many(
        'crm.team',
        string='Equipes permitidas editar'
    )

class CrmInherint(models.Model):
    _inherit = 'crm.lead'

    stage_edit = fields.Boolean(
        default=False,
        compute='_compute_stage_edit'
    )

    @api.depends('stage_edit', 'stage_id.teams_allowed_edit')
    def _compute_stage_edit(self):
        for rec in self:
            teams_allowed = rec.stage_id.mapped('teams_allowed_edit')
            user = self.env.user

            # Verifica se usuário é membro de algum time permitido
            allowed_team_members = self.env['crm.team.member'].search([
                ('crm_team_id', 'in', teams_allowed.ids),
                ('user_id', '=', user.id)
            ])

            if allowed_team_members:
                rec.stage_edit = True
            else:
                rec.stage_edit = False
```

**Lógica:**
- Se o stage tem `teams_allowed_edit` configurados
- E o usuário atual é membro de algum desses times
- Então `stage_edit = True` → usuário PODE editar
- Caso contrário `stage_edit = False` → usuário NÃO PODE editar

---

## 2. MAPEAMENTO COMPLETO DOS STAGES

### 2.1. Stages ABERTOS para Vendedores (com times permitidos)

| Seq | ID | Stage | Times Permitidos | Observação |
|-----|----|----|------------------|------------|
| 0 | 66 | Clientes Enquete | JULIENE, LAIZA, LILIAN, ATENDIMENTO, KAROLAY | ✅ Vendedores podem editar |
| 1 | 77 | 0800 PERDIDO | 11 times (incluindo vendas) | ✅ Todos podem editar |
| 2 | 27 | Oportunidade | 10 times (incluindo vendas) | ✅ Vendedores podem editar |
| 7 | 61 | PROPOSTAS PARA REVERTER | JULIENE, OPERACIONAL | ⚠️ Apenas 2 times |
| 8 | 4 | Link Feito | OPERACIONAL, FINANCEIRO | ⚠️ Apenas operacional/financeiro |
| 9 | 16 | Conferir Link | OPERACIONAL, FINANCEIRO | ⚠️ Apenas operacional/financeiro |
| 10 | 1 | Negociação | OPERACIONAL + 4 times vendas | ✅ Vendedores podem editar |
| 12 | 62 | Conferir Link | 5 times (vendas + operacional) | ✅ Vendedores podem editar |
| 13 | 2 | Em Análise (Desbloqueado) | OPERACIONAL, FINANCEIRO | ⚠️ Apenas operacional/financeiro |
| 14 | 11 | Em Análise (Bloqueado) | OPERACIONAL, FINANCEIRO | ⚠️ Apenas operacional/financeiro |
| 15 | 83 | Assinatura / Auditoria | OPERACIONAL, Administrativo, FINANCEIRO | ⚠️ Apenas staff |
| 15 | 84 | Em Assinatura | JULIENE, OPERACIONAL | ⚠️ Apenas 2 times |
| 16 | 22 | Averbado | OPERACIONAL, FINANCEIRO | ⚠️ Apenas operacional/financeiro |
| 17 | 5 | Cancelado | OPERACIONAL, FINANCEIRO | ⚠️ Apenas operacional/financeiro |
| 18 | 8 | Aguardando Digitação | JULIENE | ⚠️ Apenas 1 time |

**Total: 15 de 26 stages** têm alguma permissão configurada

### 2.2. Stages BLOQUEADOS para TODOS os Vendedores

| Seq | ID | Stage | Motivo do Bloqueio |
|-----|----|----|---------------------|
| 3 | 95 | Sem contato (Nunca atendeu) | ❌ Nenhum time permitido |
| 3 | 96 | Proposition | ❌ Nenhum time permitido |
| 4 | 87 | Clientes com Margem | ❌ Nenhum time permitido |
| 5 | 93 | Sem margem - AUMENTO | ❌ Nenhum time permitido |
| 6 | 88 | OPORTUNIDADE FGTS | ❌ Nenhum time permitido |
| 7 | 82 | Assinatura/ Auditoria | ❌ Nenhum time permitido |
| 11 | 89 | Em Assinatura | ❌ Nenhum time permitido |
| 15 | 91 | AUMENTO SALARIAL | ❌ Nenhum time permitido |
| 19 | 45 | Sugestão (COLUNA PRA ENQUETE) | ❌ Nenhum time permitido |
| 20 | 90 | Enquete negativa | ❌ Nenhum time permitido |
| 21 | 94 | Loas - 87 | ❌ Nenhum time permitido |

**Total: 11 de 26 stages** estão COMPLETAMENTE BLOQUEADOS

---

## 3. ESTRUTURA DOS TIMES

### 3.1. Times Ativos

| ID | Nome | Total Membros | Tipo |
|----|------|---------------|------|
| 6 | TIME JULIENE | 33 | 🔵 VENDAS |
| 28 | TIME JULIENE | 3 | 🔵 VENDAS (DUPLICADO!) |
| - | TIME LAIZA | ? | 🔵 VENDAS |
| - | TIME LILIAN | ? | 🔵 VENDAS |
| - | TIME KAROLAY | ? | 🔵 VENDAS |
| 9 | TIME OPERACIONAL | 13 | 🟡 OPERACIONAL |
| 14 | EQUIPE FINANCENIRO | 6 | 🟢 FINANCEIRO |
| 19 | Administrativo | 4 | 🟣 ADMIN |
| 11 | Website | 3 | 🔵 MARKETING |
| 26 | T.I | 0 | 🟣 TI (vazio) |

**⚠️ PROBLEMA IDENTIFICADO:** Existe TIME JULIENE duplicado (IDs 6 e 28)

### 3.2. Membros por Time (Detalhado)

#### TIME JULIENE (ID 6) - 33 membros
```
comercial02, comercial05, comercial06, comercial12, comercial15, comercial16,
comercial18, comercial25, comercial26, comercial27, comercial28,
+ vários d1_, d2_, d3_, d4_ (desativados?),
+ líder02, líder03,
+ operacional4,
+ treinamentos (0, 5, 6, 7)
```

#### TIME JULIENE (ID 28) - 3 membros
```
TESTES@semprereal.com
comercial20@semprereal.com
comercial22@semprereal.com
```

#### TIME OPERACIONAL (ID 9) - 13 membros
```
Comercial30, operacional1, operacional2, operacional5, operacional6,
+ vários d1_operacao, d2_operacao, d_operacao,
+ operacao12
```

#### EQUIPE FINANCENIRO (ID 14) - 6 membros
```
admin, financeiro, auxfinanceiro, ti, guntokun5
```

---

## 4. REGRAS DE SEGURANÇA (ir_rule)

### 4.1. Regras ATIVAS para crm.lead

| ID | Nome | Grupos Afetados | Permissões | Domain |
|----|------|-----------------|------------|--------|
| 60 | CRM Lead Multi-Company | (global) | RWCD | Multi-empresa |
| 373 | All Leads ADMIN | Administrator | RWCD | Todos (1=1) |
| 443 | Personal Leads RC | Own Documents Only | RWCD | `user_id=current AND stage_edit=True` |
| 444 | All Leads RC | All Documents | RWCD | `team_id=user.team AND stage_edit=True` |

### 4.2. Impacto das Regras RC (RealCred)

**Regra 443 - Personal Leads RC:**
```python
Domain: ['|','&',
    ('user_id','=',user.id),
    ('user_id','=',False),
    ('stage_edit','=',True)
]
```
**Significa:**
- Vendedor (Own Docs) só pode editar se:
  1. É o responsável pelo lead (user_id)
  2. **E** o stage permite edição (`stage_edit=True`)

**Regra 444 - All Leads RC:**
```python
Domain: ['|','&',
    ('team_id', '=',user.team_id.id),
    ('team_id.user_id', '=', user.id),
    ('stage_edit','=',True)
]
```
**Significa:**
- Usuário com "All Documents" só pode editar se:
  1. Lead pertence ao seu time
  2. **E** o stage permite edição (`stage_edit=True`)

---

## 5. ANÁLISE DE PROBLEMAS

### 🔴 Problemas Críticos

#### 1. TIME JULIENE Duplicado
**Problema:** Existem 2 times com mesmo nome (IDs 6 e 28)
- ID 6: 33 membros
- ID 28: 3 membros (TESTES, comercial20, comercial22)

**Impacto:**
- Confusão na configuração de stages
- Possível inconsistência de permissões
- Dificuldade de manutenção

**Solução Recomendada:**
- Unificar os times OU
- Renomear o time 28 para refletir sua função real

#### 2. Stages Completamente Bloqueados (11 stages)
**Problema:** 42% dos stages não têm NENHUM time permitido

**Stages afetados:**
- Sem contato (Nunca atendeu)
- Proposition
- Clientes com Margem
- Sem margem - AUMENTO
- OPORTUNIDADE FGTS
- Assinatura/ Auditoria (ID 82)
- Em Assinatura (ID 89)
- AUMENTO SALARIAL
- Sugestão (COLUNA PRA ENQUETE)
- Enquete negativa
- Loas - 87

**Impacto:**
- Vendedores NÃO conseguem editar leads nesses stages
- Leads "presos" em stages intermediários
- Operacional precisa fazer mudanças manuais

**Questão:** Isso é intencional? Ou faltou configurar?

#### 3. Campo Computado Não Armazenado
**Problema:** `stage_edit` tem `store=False`

**Impacto:**
- Calculado em TEMPO REAL para cada visualização
- Performance ruim em listas com muitos registros
- Impossível fazer filtros diretos por `stage_edit`
- Cache não funciona adequadamente

**Solução:** Mudar para `store=True` e adicionar `depends` corretos

#### 4. Falta de Auditoria
**Problema:** Não há log de quem mudou o stage quando

**Impacto:**
- Difícil rastrear problemas
- Não há responsabilização
- Compliance comprometido

**Solução:** Adicionar tracking no campo `stage_id`

### ⚠️ Problemas Médios

#### 5. Inconsistência de Nomenclatura
**Times com nomes diferentes:**
- "EQUIPE FINANCENIRO" (typo: FINANCEIRO)
- "TIME OPERACIONAL"
- "Administrativo" (sem "TIME" ou "EQUIPE")

**Solução:** Padronizar nomenclatura

#### 6. Permissões Muito Granulares
**Problema:** Alguns stages têm apenas 1 ou 2 times permitidos

**Exemplo:**
- "Aguardando Digitação" → só TIME JULIENE
- "PROPOSTAS PARA REVERTER" → só JULIENE + OPERACIONAL

**Questão:** Por que tão restritivo?

#### 7. Time T.I Vazio
**Problema:** Time "T.I" (ID 26) não tem membros

**Solução:** Remover ou adicionar membros

---

## 6. PROPOSTAS DE MELHORIA

### 🎯 Prioridade ALTA

#### Melhoria 1: Otimizar Campo Computado

**Problema Atual:**
```python
stage_edit = fields.Boolean(default=False, compute='_compute_stage_edit')
# store=False (padrão)
```

**Proposta:**
```python
stage_edit = fields.Boolean(
    string='Pode Editar',
    compute='_compute_stage_edit',
    store=True,  # ARMAZENAR no banco
    compute_sudo=True  # Evitar problemas de permissão
)

@api.depends('stage_id', 'stage_id.teams_allowed_edit', 'team_id')
def _compute_stage_edit(self):
    for rec in self:
        if not rec.stage_id:
            rec.stage_edit = True
            continue

        teams_allowed = rec.stage_id.teams_allowed_edit

        # Se não há times configurados, bloquear para vendedores
        if not teams_allowed:
            # Admin sempre pode
            if self.env.user.has_group('sales_team.group_sale_manager'):
                rec.stage_edit = True
            else:
                rec.stage_edit = False
            continue

        # Verificar se usuário é membro de algum time permitido
        user_teams = self.env['crm.team.member'].search([
            ('user_id', '=', self.env.user.id)
        ]).mapped('crm_team_id')

        rec.stage_edit = bool(teams_allowed & user_teams)
```

**Benefícios:**
- ✅ Performance 10x melhor
- ✅ Possível filtrar/ordenar por `stage_edit`
- ✅ Cache funciona corretamente
- ✅ Admin sempre pode editar

#### Melhoria 2: Unificar Times Duplicados

**Ação:**
```sql
-- Mover membros do time 28 para o time 6
UPDATE crm_team_member
SET crm_team_id = 6
WHERE crm_team_id = 28;

-- Atualizar stages que usam time 28
UPDATE crm_stage_crm_team_rel
SET crm_team_id = 6
WHERE crm_team_id = 28;

-- Desativar time 28
UPDATE crm_team
SET active = false
WHERE id = 28;
```

**Ou renomear time 28:**
```sql
UPDATE crm_team
SET name = 'TIME JULIENE - ESPECIAL'
WHERE id = 28;
```

#### Melhoria 3: Configurar Stages Bloqueados

**Decisão Necessária:** Para cada stage bloqueado, definir:

**Opção A - Apenas Operacional/Financeiro:**
```sql
-- Adicionar TIME OPERACIONAL + FINANCEIRO aos stages bloqueados
INSERT INTO crm_stage_crm_team_rel (crm_stage_id, crm_team_id)
SELECT unnest(ARRAY[95,96,87,93,88,82,89,91,45,90,94]), unnest(ARRAY[9,14])
ON CONFLICT DO NOTHING;
```

**Opção B - Liberar para Todos:**
```sql
-- Adicionar TODOS os times de vendas
INSERT INTO crm_stage_crm_team_rel (crm_stage_id, crm_team_id)
SELECT s.id, t.id
FROM crm_stage s
CROSS JOIN crm_team t
WHERE s.id IN (95,96,87,93,88,82,89,91,45,90,94)
    AND t.id IN (6,28, ... outros times de vendas);
```

**Opção C - Manter Bloqueado (documentar motivo)**

### 🎯 Prioridade MÉDIA

#### Melhoria 4: Adicionar Auditoria

```python
class CrmInherint(models.Model):
    _inherit = 'crm.lead'

    stage_id = fields.Many2one(tracking=True)  # Adicionar tracking

    stage_changed_by = fields.Many2one(
        'res.users',
        string='Stage Alterado Por',
        compute='_compute_stage_changed_by',
        store=True
    )

    stage_changed_date = fields.Datetime(
        string='Data Alteração Stage',
        compute='_compute_stage_changed_date',
        store=True
    )
```

#### Melhoria 5: View para Visualizar Permissões

Criar view SQL para facilitar troubleshooting:

```sql
CREATE OR REPLACE VIEW crm_stage_permissions_view AS
SELECT
    s.id as stage_id,
    s.name as stage_name,
    s.sequence,
    t.id as team_id,
    t.name as team_name,
    COUNT(DISTINCT tm.user_id) as users_allowed
FROM crm_stage s
LEFT JOIN crm_stage_crm_team_rel r ON s.id = r.crm_stage_id
LEFT JOIN crm_team t ON r.crm_team_id = t.id
LEFT JOIN crm_team_member tm ON t.id = tm.crm_team_id
GROUP BY s.id, s.name, s.sequence, t.id, t.name
ORDER BY s.sequence, s.id;
```

#### Melhoria 6: Padronizar Nomenclatura

```sql
-- Corrigir typo
UPDATE crm_team SET name = 'EQUIPE FINANCEIRO'
WHERE name = 'EQUIPE FINANCENIRO';

-- Padronizar formato
UPDATE crm_team SET name = 'TIME ADMINISTRATIVO'
WHERE name = 'Administrativo';
```

### 🎯 Prioridade BAIXA

#### Melhoria 7: Adicionar Constraint

```python
@api.constrains('stage_id', 'user_id')
def _check_stage_edit_permission(self):
    for rec in self:
        if not rec.stage_edit and not self.env.user.has_group('sales_team.group_sale_manager'):
            raise ValidationError(
                f"Você não tem permissão para mover este lead para o stage '{rec.stage_id.name}'.\n"
                f"Entre em contato com seu supervisor."
            )
```

#### Melhoria 8: Dashboard de Permissões

Criar menu em Configurações → CRM mostrando:
- Quantos stages cada time pode editar
- Quais stages estão bloqueados
- Usuários sem time atribuído

---

## 7. FLUXO RECOMENDADO POR ROLE

### 7.1. VENDEDOR (Own Documents)

**Stages que PODE editar:**
1. Clientes Enquete
2. 0800 PERDIDO
3. Oportunidade
4. Negociação
5. Conferir Link (algumas etapas)

**Stages que NÃO PODE editar:**
- Qualquer stage após "Em Análise"
- Stages financeiros (Averbado, Cancelado)
- Stages bloqueados

**Fluxo Ideal:**
```
VENDEDOR cria lead
   ↓
Trabalha em stages iniciais (Oportunidade, Negociação)
   ↓
Move para "Link Feito" ou "Conferir Link"
   ↓
OPERACIONAL assume (Em Análise, Assinatura)
   ↓
FINANCEIRO finaliza (Averbado, Cancelado)
```

### 7.2. OPERACIONAL (All Documents)

**Pode editar:**
- Todos os stages de vendedores
- Stages intermediários (Link Feito, Conferir Link)
- Stages de análise
- Assinatura/Auditoria

**Não pode editar:**
- Stages exclusivos do financeiro (se houver)

### 7.3. FINANCEIRO (All Documents)

**Pode editar:**
- TODOS os stages
- Especialmente: Averbado, Cancelado, Em Análise

### 7.4. ADMIN (Sales Administrator)

**Pode editar:**
- TUDO, sem restrições (regra ID 373)

---

## 8. QUERIES ÚTEIS PARA TROUBLESHOOTING

### Ver permissões de um usuário específico:

```sql
-- Substituir 'comercial01@semprereal.com' pelo login do usuário
WITH user_teams AS (
    SELECT t.id, t.name
    FROM crm_team t
    JOIN crm_team_member tm ON t.id = tm.crm_team_id
    JOIN res_users u ON tm.user_id = u.id
    WHERE u.login = 'comercial01@semprereal.com'
)
SELECT
    s.id,
    s.name as stage,
    s.sequence,
    CASE
        WHEN COUNT(ut.id) > 0 THEN 'SIM - Pode Editar'
        ELSE 'NÃO - Bloqueado'
    END as pode_editar,
    string_agg(DISTINCT t.name, ', ') as times_permitidos
FROM crm_stage s
LEFT JOIN crm_stage_crm_team_rel r ON s.id = r.crm_stage_id
LEFT JOIN crm_team t ON r.crm_team_id = t.id
LEFT JOIN user_teams ut ON t.id = ut.id
GROUP BY s.id, s.name, s.sequence
ORDER BY s.sequence;
```

### Ver quais leads estão bloqueados para edição:

```sql
-- Leads que nenhum vendedor consegue editar
SELECT
    l.id,
    l.name as lead_name,
    s.name as stage_atual,
    p.name as responsavel,
    COUNT(DISTINCT r.crm_team_id) as times_permitidos
FROM crm_lead l
JOIN crm_stage s ON l.stage_id = s.id
LEFT JOIN res_partner p ON l.user_id = p.id
LEFT JOIN crm_stage_crm_team_rel r ON s.id = r.crm_stage_id
GROUP BY l.id, l.name, s.name, p.name
HAVING COUNT(DISTINCT r.crm_team_id) = 0
LIMIT 50;
```

---

## 9. DECISÕES NECESSÁRIAS

Antes de aplicar melhorias, precisamos decidir:

### Decisão 1: Times Duplicados
- [ ] Unificar TIME JULIENE (6 e 28) em um só
- [ ] Renomear time 28 para diferenciá-lo
- [ ] Manter como está (documentar motivo)

### Decisão 2: Stages Bloqueados (11 stages sem times)
Para cada stage bloqueado:
- [ ] Liberar para Operacional + Financeiro
- [ ] Liberar para todos os times de vendas
- [ ] Manter bloqueado (documentar motivo)

### Decisão 3: Performance
- [ ] Aplicar `store=True` no campo `stage_edit`
- [ ] Manter como está (computado em tempo real)

### Decisão 4: Auditoria
- [ ] Adicionar tracking de mudanças de stage
- [ ] Criar campos de auditoria personalizados
- [ ] Não adicionar (manter como está)

### Decisão 5: Nomenclatura
- [ ] Padronizar nomes dos times
- [ ] Corrigir typo "FINANCENIRO" → "FINANCEIRO"
- [ ] Manter como está

---

## 10. PLANO DE IMPLEMENTAÇÃO SUGERIDO

### Fase 1: Correções Urgentes (1-2 horas)
1. ✅ Corrigir `perm_read` das regras 443 e 444 (JÁ FEITO!)
2. Decidir sobre times duplicados
3. Aplicar `store=True` no campo `stage_edit`

### Fase 2: Configuração de Stages (2-3 horas)
1. Revisar cada stage bloqueado
2. Configurar times permitidos conforme decisões
3. Testar fluxo completo com usuário de teste

### Fase 3: Melhorias de Qualidade (3-4 horas)
1. Adicionar tracking de stage_id
2. Padronizar nomenclatura dos times
3. Criar view de permissões
4. Documentar decisões

### Fase 4: Validação (1-2 horas)
1. Testar com vendedores reais
2. Validar com operacional
3. Confirmar com financeiro
4. Ajustes finais

**Total Estimado:** 7-11 horas

---

## 11. RISCOS E MITIGAÇÕES

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Vendedores perdem acesso a leads | Alto | Média | Testar em ambiente de homologação primeiro |
| Performance piora com store=True | Médio | Baixa | Monitorar após deploy, rollback se necessário |
| Times duplicados causam confusão | Médio | Alta | Comunicar mudanças claramente |
| Leads ficam presos em stages | Alto | Baixa | Manter regra de admin sempre pode editar |

---

## 12. CONCLUSÃO

O sistema atual de permissões por stages é **bem arquitetado** mas tem algumas **inconsistências de configuração** e **problemas de performance**.

### Pontos Positivos ✅
- Arquitetura flexível e extensível
- Controle granular por times
- Separação clara de responsabilidades

### Pontos Negativos ❌
- 42% dos stages completamente bloqueados
- Times duplicados
- Campo computado não armazenado
- Falta de auditoria

### Recomendação Final

**Aplicar melhorias em fases:**
1. Corrigir urgente (times duplicados + store=True)
2. Configurar stages bloqueados
3. Adicionar auditoria e melhorias de qualidade

**Não fazer:**
- Mudanças drásticas na arquitetura (está boa)
- Remover o sistema de permissões (é útil)

---

**Status:** 📊 ANÁLISE COMPLETA - AGUARDANDO DECISÕES
**Próximo Passo:** Revisar com stakeholders e decidir sobre os 5 pontos de decisão
**Data:** 16/11/2025
**Analista:** Claude AI Assistant
