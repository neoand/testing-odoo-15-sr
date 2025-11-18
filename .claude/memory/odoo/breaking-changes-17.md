# 🚀 Odoo 17 Breaking Changes & Migration Guide

> **Fonte:** Documentação Oficial + GitHub Issues + Comunidade
> **Data:** 2025-11-17
> **Status:** Conhecimento permanente
> **Migração de:** v15 → v17

---

## 📋 RESUMO EXECUTIVO

### Status de Suporte
- **Odoo 17.0:** ✅ Suportado oficialmente
- **Lançamento:** Outubro 2023
- **Enterprise Support:** Até ~Outubro 2026
- **Community:** Suporte comunitário ativo

### ⚠️ Recomendação de Migração
- **NÃO migrar** nos primeiros 3 meses após release
- **Aguardar** estabilização de bugs
- **Verificar** compatibilidade de módulos third-party
- **Testar** em staging por pelo menos 1 mês

---

## 🔄 PROCESSO DE MIGRAÇÃO (CRÍTICO!)

### Regra de Ouro

**❌ NÃO É POSSÍVEL** migrar diretamente v15 → v17!

**✅ CAMINHO OBRIGATÓRIO:** v15 → v16 → v17

### Opções de Migração

#### 1️⃣ Enterprise Edition (RECOMENDADO)

```
1. Backup completo database + filestore
2. Upload para https://upgrade.odoo.com/
3. Aguardar migração por Odoo Team (GRÁTIS!)
4. Download database migrada
5. Testar extensivamente
6. Deploy em produção
```

**Vantagens:**
- ✅ Grátis para clientes Enterprise
- ✅ Suporte oficial Odoo
- ✅ Correção de discrepâncias incluída
- ✅ Mais seguro

**Limitações:**
- ⏱️ Tempo de processamento (pode demorar dias/semanas)
- 📦 Dependente da fila do Odoo

#### 2️⃣ Community Edition (COMPLEXO!)

**Opção A: OpenUpgrade (OCA)**

```bash
# Migração v15 → v16
git clone https://github.com/OCA/OpenUpgrade.git
cd OpenUpgrade
git checkout 16.0
# Executar scripts de migração

# Migração v16 → v17
git checkout 17.0
# Executar scripts de migração
```

**⚠️ ATENÇÃO:**
- OpenUpgrade v17 pode ainda não estar pronto
- Comunidade recomenda NÃO migrar para v17 antes do lançamento v18
- Requer modificações manuais no banco
- Testar EXTENSIVAMENTE antes

**Opção B: Custom Scripts (Dados Estáticos)**

Para dados simples (clientes, produtos, categorias):
```python
# Script Python customizado para migração
# Exportar de v15
# Transformar dados
# Importar em v17
```

**Custos Estimados:**
- **Mínimo:** 50 horas de trabalho
- **Lead time:** 1 mês
- **Custo:** Varia com customizações e tamanho DB

---

## 💥 BREAKING CHANGES - Python/ORM

### 1. `name_get()` DEPRECADO ❌

**Versão:** v17.0
**Status:** Deprecado (ainda funciona, mas não recomendado)

**ANTES (v15):**
```python
def name_get(self):
    result = []
    for record in self:
        name = f"[{record.code}] {record.name}"
        result.append((record.id, name))
    return result
```

**DEPOIS (v17):**
```python
# Usar display_name field diretamente
display_name = fields.Char(
    compute='_compute_display_name',
    store=True  # Opcional, mas recomendado
)

@api.depends('code', 'name')
def _compute_display_name(self):
    for record in self:
        record.display_name = f"[{record.code}] {record.name}"
```

**Por que mudou:**
- `display_name` agora é base
- `name_get` chama `display_name` internamente (invertido!)
- Performance melhorada com computed field + store

**Migração:**
```python
# Se tiver name_get customizado:
1. Converter para _compute_display_name
2. Testar equivalência
3. Remover name_get() do código
```

---

### 2. Field Attributes REMOVIDOS ❌

**Removidos em v17:**
- `deprecated` (atributo de campo)
- `_sequence` (atributo de modelo)
- `column_format` (atributo de campo)

**Causa:** Funcionalidades não utilizadas, ruído desnecessário

**Impacto:**
- ✅ ORM mais limpo
- ✅ Menos overhead
- ⚠️ Se usava esses atributos, remover do código

---

### 3. Access Control API - MUDOU (v18, mas prepare-se!)

**v15-17:**
```python
# Filtrar por access rules
filtered = records._filter_access_rule('read')
filtered = records._filter_access_rule_python('write')
```

**v18+ (futuro):**
```python
# Novo método unificado
filtered = records._filter_access(mode='read')
filtered = records._filter_access(mode='write')
```

**Ação:** Preparar código para futuro, mas ainda funciona em v17

---

## ⚡ MELHORIAS DE PERFORMANCE - ORM

### 1. `search_fetch()` e `fetch()` - NOVO! ✨

**Versão:** v17.4
**Impacto:** 🔥 ENORME - Reduz queries drasticamente

**Problema Antigo (v15):**
```python
# search() + read() = 2 queries
leads = self.env['crm.lead'].search([('state', '=', 'new')])
data = leads.read(['name', 'partner_id', 'expected_revenue'])
# Query 1: SELECT id FROM crm_lead WHERE state='new'
# Query 2: SELECT id, name, partner_id, expected_revenue FROM crm_lead WHERE id IN (...)
```

**Solução Nova (v17.4+):**
```python
# search_fetch() = 1 query só!
data = self.env['crm.lead'].search_fetch(
    [('state', '=', 'new')],
    ['name', 'partner_id', 'expected_revenue']
)
# Query única: SELECT id, name, partner_id, expected_revenue
#              FROM crm_lead WHERE state='new'
```

**Ganho de Performance:**
- ✅ -50% de queries
- ✅ -30% de tempo de execução
- ✅ Menos overhead de comunicação PostgreSQL

**Quando usar:**
- Listagens
- Reports
- Exports
- APIs que retornam dados

**Método `fetch()`:**
```python
# Fetch específico em recordset existente
leads = self.env['crm.lead'].browse([1, 2, 3])
data = leads.fetch(['name', 'email'])  # Fetch otimizado
```

---

### 2. Prefetch Melhorado

**v17 otimizou ainda mais o prefetch automático:**

```python
# Odoo prefetcha automaticamente campos simples
for lead in leads:  # Odoo carrega tudo de uma vez!
    print(lead.name)           # Já em cache
    print(lead.partner_id)     # Já em cache
    print(lead.expected_revenue)  # Já em cache
```

**Campos prefetchados:**
- boolean, integer, float, char, text
- date, datetime, selection
- many2one (ID do relacionamento)

**NOT prefetchados (lazy load):**
- one2many, many2many (requer query separada)
- Binary fields (imagens)
- Html fields muito grandes

---

## 🎨 BREAKING CHANGES - JavaScript/OWL

### 1. OWL Framework - OBRIGATÓRIO

**v15:** JavaScript legado (Widget-based)
**v17:** OWL 2.0 obrigatório para novos módulos

**Mudanças Críticas:**

#### Widget → Component

**ANTES (v15):**
```javascript
odoo.define('module.Widget', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');

    var MyWidget = AbstractField.extend({
        events: {
            'click .button': '_onClick',
        },
        _onClick: function() {
            // Handler
        }
    });

    return MyWidget;
});
```

**DEPOIS (v17):**
```javascript
/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

class MyComponent extends Component {
    static template = "module.MyComponent";

    onClick() {
        // Handler usando arrow function
    }
}

registry.category("fields").add("my_component", MyComponent);
```

**Principais Diferenças:**
- ✅ ES6 Classes (não extend)
- ✅ Templates XML separados
- ✅ Hooks (useState, onMounted, etc)
- ✅ Reactivity automática
- ✅ Virtual DOM (performance!)

---

### 2. OWL 2.0 Breaking Changes

**Store System REMOVIDO ❌**

**v15 (OWL 1.x):**
```javascript
// Store para estado global
const store = new owl.Store({...});
```

**v17 (OWL 2.0):**
```javascript
// Usar services ao invés de Store
import { useService } from "@web/core/utils/hooks";

class MyComponent extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
    }
}
```

**`t-raw` REMOVIDO ❌**

**v15:**
```xml
<t t-raw="unsafeHTML"/>  <!-- Perigoso! -->
```

**v17:**
```xml
<t t-out="safeHTML"/>  <!-- Escapado automaticamente -->
```

**Rendering NÃO É MAIS "DEEP"**

**v15:** Componente rerenderiza todos filhos sempre
**v17:** Apenas rerenderiza se props mudaram (shallow comparison)

```javascript
// v17: Precisa usar reactive() para objetos
import { reactive } from "@odoo/owl";

setup() {
    this.state = reactive({ count: 0 });
}
```

---

### 3. Tutorials JavaScript - ATUALIZADOS

Odoo 17 tem tutorial completo de OWL no módulo `awesome_owl`:

```bash
# Estudar em:
odoo-bin scaffold awesome_owl_tutorial ./addons
# Seguir tutorial oficial docs
```

**Tópicos cobertos:**
- Owl Components básicos
- Props e State
- Hooks (useState, onMounted, etc)
- Services
- RPC calls
- Reactivity

---

## 📊 ACCOUNTING CHANGES

### 1. Outstanding & Suspense Accounts - MUDOU (v14+)

**Desde v14 (continua v17):**

Contas automáticas criadas:
- **Outstanding Account:** Pagamentos não reconciliados
- **Bank Suspense Account:** Transações bancárias pendentes

**Comportamento:**
```
Payment criado → Outstanding Account (temporário)
↓
Bank statement importado → Bank Suspense
↓
Reconciliation → Move para conta definitiva
```

**IMPORTANTE:**
- Não editar journal de moves posted
- Não editar moves com sequence number
- Automação de journal entries (v17 novo!)

---

### 2. Automatic Journal Entries - NOVO! ✨

**Odoo 17 Feature:**

```python
# Criar regras para journal entries automáticos
# Reduz entry manual
# Minimiza erros
```

**Benefícios:**
- ✅ Menos trabalho manual
- ✅ Consistência
- ✅ Menos erros

---

## 🔧 MÓDULOS CUSTOMIZADOS

### Compatibilidade

**REGRA CRÍTICA:**

> "Se mudança em v17 quebrar customização, é responsabilidade do
> mantenedor do módulo custom torná-lo compatível!"

**Checklist de Compatibilidade:**

```
[ ] Substituir name_get() por display_name
[ ] Remover atributos deprecated
[ ] Migrar JavaScript para OWL 2.0
[ ] Testar access control
[ ] Atualizar depends no manifest
[ ] Remover Store (OWL)
[ ] Substituir t-raw por t-out
[ ] Verificar computed fields com store
```

---

### Manifest Changes

**v15:**
```python
{
    'name': 'My Module',
    'version': '15.0.1.0.0',
    'depends': ['base', 'web'],
    'data': [...],
}
```

**v17:**
```python
{
    'name': 'My Module',
    'version': '17.0.1.0.0',  # Atualizar versão!
    'depends': ['base', 'web'],
    'data': [...],
    'assets': {  # Assets separados (v17+)
        'web.assets_backend': [
            'module/static/src/components/**/*',
        ],
    },
}
```

**Assets Structure - MUDOU:**

```
v15: /static/src/js/
v17: /static/src/components/  (OWL components)
     /static/src/services/    (Services)
     /static/src/models/      (Models)
```

---

## 🧪 TESTING & VALIDATION

### Antes de Migrar

**Backup Completo:**
```bash
# Database
sudo -u postgres pg_dump -Fc DATABASE > backup_pre_migration.dump

# Filestore
tar -czf filestore_backup.tar.gz /odoo/filestore/

# Custom addons
tar -czf custom_addons_backup.tar.gz /odoo/custom/
```

**Ambiente de Teste:**
1. Criar servidor staging com v17
2. Restaurar backup v15
3. Executar migração (upgrade service ou OpenUpgrade)
4. Testar TODAS as funcionalidades
5. Verificar todos os módulos custom
6. Performance testing (queries lentas?)
7. Security audit
8. User acceptance testing (1 mês mínimo!)

---

### Após Migração

**Validações Obrigatórias:**

```python
# 1. Verificar integridade de dados
SELECT COUNT(*) FROM ir_module_module WHERE state = 'to upgrade';
# Deve ser 0

# 2. Verificar errors nos logs
grep -i "error\|warning" /var/log/odoo/odoo-server.log

# 3. Verificar scheduled actions
# Settings → Technical → Automation → Scheduled Actions
# Todos devem estar funcionais

# 4. Verificar cron jobs
SELECT * FROM ir_cron WHERE active = True;

# 5. Testar workflows críticos:
#    - Criar invoice
#    - Criar sale order
#    - Processar payment
#    - Enviar email
#    - Relatórios

# 6. Performance baseline
\timing
SELECT COUNT(*) FROM account_move;
SELECT COUNT(*) FROM res_partner;
# Comparar com v15
```

---

## 📚 RECURSOS DE APRENDIZADO

### Documentação Oficial

1. **Upgrade Guide:** https://www.odoo.com/documentation/17.0/administration/upgrade.html
2. **ORM API:** https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html
3. **OWL Framework:** https://github.com/odoo/owl
4. **JavaScript Tutorial:** https://www.odoo.com/documentation/17.0/developer/tutorials/

### Comunidade

1. **OpenUpgrade:** https://github.com/OCA/OpenUpgrade
2. **OCA Guidelines:** https://github.com/OCA/odoo-community.org
3. **Odoo Forums:** https://www.odoo.com/forum/help-1
4. **Odoo Experience 2023:** "What changed in the ORM for Odoo 17"

---

## ⚠️ RISCOS E MITIGAÇÕES

### Riscos Conhecidos

1. **Módulos Third-Party Incompatíveis**
   - **Risco:** Alto
   - **Mitigação:** Verificar com vendors ANTES de migrar
   - **Alternativa:** Substituir por módulos compatíveis

2. **Custom Code Quebrado**
   - **Risco:** Médio-Alto
   - **Mitigação:** Refatorar seguindo checklist acima
   - **Custo:** 50-200 horas dependendo complexidade

3. **Performance Degradada**
   - **Risco:** Baixo (v17 é mais rápido!)
   - **Mitigação:** Usar search_fetch(), otimizar computed fields
   - **Benefício:** Geralmente melhora vs v15

4. **Downtime Prolongado**
   - **Risco:** Médio
   - **Mitigação:** Testar migração em staging primeiro
   - **Planejar:** Janela de manutenção adequada

5. **Data Loss**
   - **Risco:** Baixo (se feito corretamente)
   - **Mitigação:** BACKUPS MÚLTIPLOS!
   - **Validação:** Contar records antes/depois

---

## 🎯 TIMELINE RECOMENDADO

### Fase 1: Preparação (2-4 semanas)
- [ ] Backup completo
- [ ] Inventário de módulos instalados
- [ ] Verificar compatibilidade third-party
- [ ] Setup staging environment
- [ ] Estimar custos de refatoração

### Fase 2: Migração Staging (2-4 semanas)
- [ ] Executar upgrade (service ou OpenUpgrade)
- [ ] Resolver erros de migração
- [ ] Refatorar código custom
- [ ] Testes funcionais
- [ ] Performance testing

### Fase 3: Validação (4-8 semanas)
- [ ] User acceptance testing
- [ ] Training usuários
- [ ] Ajustes finais
- [ ] Documentation
- [ ] Rollback plan

### Fase 4: Produção (1 semana)
- [ ] Comunicação com usuários
- [ ] Backup final
- [ ] Migração produção
- [ ] Validação pós-migração
- [ ] Monitoramento intensivo (2 semanas)

**TOTAL:** 3-5 meses para migração segura

---

## 💡 QUICK WINS - Aproveitar Features v17

### 1. Usar `search_fetch()` Imediatamente

```python
# Refatorar todas as ocorrências de:
records = self.search([...])
data = records.read([...])

# Para:
data = self.search_fetch([...], [...])
```

**Impacto:** -30% tempo de listagens

---

### 2. Migrar Computed Fields para `store=True`

```python
# Se campo é muito acessado:
@api.depends('partner_id.phone')
def _compute_partner_phone(self):
    for record in self:
        record.partner_phone = record.partner_id.phone

partner_phone = fields.Char(
    compute='_compute_partner_phone',
    store=True  # ← ADICIONAR se campo é lido frequentemente
)
```

**Benefício:** Queries mais rápidas, menos recomputes

---

### 3. Atualizar JavaScript para OWL

**ROI:** Alto se você tem muito JS custom

- Performance melhorada
- Código mais moderno
- Facilita manutenção futura
- Aproveita reactivity

---

## 🔍 DIFERENÇAS v15 vs v17 - RESUMO

| Aspecto | v15 | v17 |
|---------|-----|-----|
| **Suporte** | ❌ Acabou Out/2024 | ✅ Até ~Out/2026 |
| **Python** | 3.8+ | 3.10+ |
| **PostgreSQL** | 12+ | 13+ |
| **JavaScript** | Widget-based | OWL 2.0 |
| **`name_get`** | ✅ Método principal | ⚠️ Deprecado |
| **ORM Performance** | Base | ✅ +30% com search_fetch |
| **Accounting** | Básico | ✅ Auto journal entries |
| **UI** | Standard | ✅ Modernizada |
| **Migração** | Para v16 | De v16 |

---

## 📋 CHECKLIST FINAL

### Antes de Decidir Migrar

```
[ ] v15 ainda atende necessidades? (considerar EOL!)
[ ] Budget aprovado? (50-200h + custos infraestrutura)
[ ] Timeline realista? (3-5 meses)
[ ] Equipe treinada em v17?
[ ] Módulos third-party compatíveis?
[ ] Staging environment disponível?
[ ] Backup strategy definida?
[ ] Rollback plan documentado?
[ ] Usuários avisados e treinados?
```

### Se SIM para todos acima

```
[ ] Executar migração staging
[ ] Testar 1 mês mínimo
[ ] Validar TODAS funcionalidades
[ ] Treinar usuários
[ ] Documentar mudanças
[ ] Planejar janela de manutenção
[ ] GO! 🚀
```

---

## 🎓 LIÇÕES APRENDIDAS (Comunidade)

1. **NUNCA** migre diretamente v15 → v17 (vai dar erro!)
2. **SEMPRE** teste em staging primeiro (3-4 semanas mínimo)
3. **Aguarde 3 meses** após release v17 antes de migrar
4. **Verifique módulos** third-party ANTES (alguns nunca migram!)
5. **OpenUpgrade** é complexo - Enterprise upgrade service é mais seguro
6. **Refatoração custom code** leva MUITO mais tempo que estimado
7. **Performance geralmente MELHORA** (search_fetch é ouro!)
8. **OWL migration** é trabalhosa mas vale a pena
9. **Users resistem mudanças** - treinamento é crítico
10. **Backup TUDO** - melhor sobrar que faltar!

---

**Criado:** 2025-11-17
**Sprint:** 4 - Auto-Educação Odoo
**Próxima atualização:** Ao encontrar novos breaking changes
**Fonte:** Docs Oficial + GitHub + Comunidade + Odoo Experience 2023

**Próximo:** [Odoo 18 - What's New](./whats-new-18.md)
