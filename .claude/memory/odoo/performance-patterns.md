# ⚡ Odoo Performance Patterns - Guia Definitivo

> **Objetivo:** Maximizar performance em TODAS as versões Odoo
> **Fontes:** v15/17/18 analysis + GitHub + Comunidade + Experiência
> **Data:** 2025-11-17
> **Status:** Conhecimento permanente

---

## 🎯 PRINCÍPIOS FUNDAMENTAIS

### A Regra de Ouro

> **"O ORM do Odoo é LENTO. PostgreSQL é RÁPIDO. A chave é fazer o ORM
> trabalhar SMART, não HARD."**

### Performance Hierarchy

```
1. Zero queries (cache) ⚡⚡⚡⚡⚡ FASTEST
2. One optimized query ⚡⚡⚡⚡ FAST
3. Few queries (bulk) ⚡⚡⚡ OK
4. Many queries (N+1) ⚡ SLOW
5. Python loops com ORM ☠️ VERY SLOW
```

---

## 🔥 PROBLEMA #1: N+1 QUERIES (O MAIOR VILÃO!)

### O Que É N+1?

```python
# ❌ EXEMPLO CLÁSSICO DE N+1
leads = self.env['crm.lead'].search([('state', '=', 'new')])  # Query 1
for lead in leads:  # Iterating 100 leads
    partner_name = lead.partner_id.name  # Query 2, 3, 4... 101!
    # TOTAL: 101 queries! 😱
```

**Por que acontece:**
- Odoo carrega `partner_id` como ID apenas (lazy load)
- Acessar `.name` força query para res.partner
- Cada iteração = nova query!

**Performance:**
```
100 leads com N+1: ~3-5 seconds
100 leads otimizado: ~0.1 seconds
= 30-50x SLOWER! 💀
```

---

### SOLUÇÃO #1: @api.depends CORRETO

```python
# ❌ ERRADO - Causa N+1
@api.depends('partner_id')  # Genérico demais!
def _compute_partner_name(self):
    for record in self:
        record.partner_name = record.partner_id.name  # N+1!

# ✅ CORRETO - Zero N+1
@api.depends('partner_id.name')  # Campo COMPLETO!
def _compute_partner_name(self):
    for record in self:
        record.partner_name = record.partner_id.name  # Cached! ⚡
```

**Por que funciona:**
- `@api.depends('partner_id.name')` → Odoo prefetcha partner.name
- Uma query carrega TODOS os partners de uma vez
- Loop acessa cache, não database!

**Regra:**
```python
# SEMPRE especificar campo completo em depends de relacionamentos!
@api.depends('field_id.subfield')  # ✅
@api.depends('field_id')           # ❌
```

---

### SOLUÇÃO #2: mapped() Antes de Loop

```python
# ❌ ERRADO
for lead in leads:
    print(lead.partner_id.phone)  # N+1!

# ✅ CORRETO - Opção 1: mapped
leads.mapped('partner_id.phone')  # Prefetch tudo!
for lead in leads:
    print(lead.partner_id.phone)  # Cache! ⚡

# ✅ CORRETO - Opção 2: Acessar diretamente
partner_phones = leads.mapped('partner_id.phone')
for phone in partner_phones:
    print(phone)
```

**Quando usar:**
- Loop que acessa campos relacionados
- Qualquer iteração com many2one/one2many

---

### SOLUÇÃO #3: read() ao Invés de Browse

```python
# ❌ LENTO - Carrega objetos completos
leads = self.env['crm.lead'].browse(lead_ids)
for lead in leads:
    data.append({
        'name': lead.name,
        'phone': lead.phone,
    })

# ✅ RÁPIDO - Carrega apenas campos necessários
leads_data = self.env['crm.lead'].browse(lead_ids).read(['name', 'phone'])
for lead in leads_data:  # lead é dict, não recordset!
    data.append({
        'name': lead['name'],
        'phone': lead['phone'],
    })
```

**Benefício:**
- read() carrega apenas campos especificados
- Retorna dicts (mais leves que recordsets)
- -40% overhead de ORM

---

### SOLUÇÃO #4: search_fetch() (v17.4+) - GAME CHANGER! 🚀

```python
# ❌ ANTES (v15-17.3) - 2 queries
leads = self.env['crm.lead'].search([('state', '=', 'new')])
data = leads.read(['name', 'partner_id', 'expected_revenue'])
# Query 1: SELECT id FROM crm_lead WHERE state='new'
# Query 2: SELECT id,name,partner_id,expected_revenue FROM crm_lead WHERE id IN (...)

# ✅ DEPOIS (v17.4+) - 1 query!
data = self.env['crm.lead'].search_fetch(
    [('state', '=', 'new')],
    ['name', 'partner_id', 'expected_revenue']
)
# Query única: SELECT id,name,partner_id,expected_revenue FROM crm_lead WHERE state='new'
```

**Impacto:**
- -50% queries
- -30% tempo de execução
- Disponível v17.4+ (use SEMPRE!)

**Comparação:**

| Método | Queries | Tempo (1000 records) |
|--------|---------|----------------------|
| search + browse + access | 1 + N | ~5s |
| search + read | 2 | ~1.2s |
| search_fetch | 1 | ~0.8s ⚡ |

---

### SOLUÇÃO #5: read_group() para Agregações

```python
# ❌ LENTO - ORM + Python aggregation
totals = {}
for partner in partners:
    total = sum(partner.invoice_ids.mapped('amount_total'))  # N+1!
    totals[partner.id] = total

# ✅ RÁPIDO - SQL aggregation
data = self.env['account.move'].read_group(
    domain=[('partner_id', 'in', partner_ids), ('move_type', '=', 'out_invoice')],
    fields=['partner_id', 'amount_total:sum'],
    groupby=['partner_id']
)
# Retorna: [{'partner_id': (1, 'Partner A'), 'amount_total': 50000, ...}, ...]
```

**Quando usar:**
- COUNT, SUM, AVG, MIN, MAX
- GROUP BY queries
- Dashboards/Reports

**Performance:**
```
1000 partners com invoices (ORM): ~30s
1000 partners com invoices (read_group): ~0.5s
= 60x FASTER! 🚀
```

---

## 🔥 PROBLEMA #2: COMPUTED FIELDS SEM STORE

### O Dilema

**Computed field SEM store:**
- ✅ Sempre atualizado (nenhum stale data)
- ✅ Não ocupa espaço DB
- ❌ Calculado a CADA acesso (lento!)
- ❌ Não indexável
- ❌ Não searchable (sem search method)

**Computed field COM store:**
- ✅ Muito rápido (leitura direta DB)
- ✅ Indexável (pode criar index!)
- ✅ Searchable automaticamente
- ❌ Ocupa espaço DB
- ❌ Pode ficar stale se depends errado
- ❌ Recompute pode ser caro

---

### Quando Usar store=True

**✅ USE store=True SE:**

1. **Campo muito acessado:**
```python
# Exemplo: partner_name em crm.lead (mostrado em tree view)
partner_name = fields.Char(
    compute='_compute_partner_name',
    store=True,  # ✅ Tree view acessa 100x/dia!
    index=True   # ✅ Bonus: indexável!
)
```

2. **Campo usado em search/filter:**
```python
# Exemplo: total_amount usado em filtros
@api.depends('line_ids.price_total')
def _compute_amount_total(self):
    for record in self:
        record.amount_total = sum(record.line_ids.mapped('price_total'))

amount_total = fields.Float(
    compute='_compute_amount_total',
    store=True  # ✅ Permite filtrar "total > 1000" sem search method!
)
```

3. **Campo em reports/dashboards:**
```python
# read_group() requer store=True (ou funciona muito lento)
margin = fields.Float(
    compute='_compute_margin',
    store=True  # ✅ Dashboard usa read_group!
)
```

4. **Cálculo caro mas mudanças raras:**
```python
# Exemplo: Análise complexa de texto
sentiment_score = fields.Float(
    compute='_compute_sentiment',  # NLP analysis (caro!)
    store=True  # ✅ Só recomputa quando description muda
)

@api.depends('description')  # Muda raramente
def _compute_sentiment(self):
    for record in self:
        record.sentiment_score = analyze_sentiment(record.description)
```

---

**❌ NÃO USE store=True SE:**

1. **Depende de muitos records de outro model:**
```python
# ⚠️ PERIGOSO!
@api.depends('partner_id.invoice_ids.amount_total')
def _compute_partner_total(self):
    for record in self:
        record.partner_total = sum(record.partner_id.invoice_ids.mapped('amount_total'))

# Problema: Cada invoice criada → recomputa TODOS os leads do partner!
# Se partner tem 1000 leads → 1000 recomputes!
```

**Alternativa:**
```python
# Sem store, ou calcular apenas quando acessado via property
def _get_partner_total(self):
    self.ensure_one()
    return sum(self.partner_id.invoice_ids.mapped('amount_total'))
```

2. **Cálculo extremamente rápido:**
```python
# Sem necessidade de store
full_name = fields.Char(compute='_compute_full_name')

@api.depends('first_name', 'last_name')
def _compute_full_name(self):
    for record in self:
        record.full_name = f"{record.first_name} {record.last_name}"
        # Cálculo trivial, sem store OK
```

---

### Impacto de store=True

**Benchmark (1000 records):**

| Operação | Sem Store | Com Store | Diff |
|----------|-----------|-----------|------|
| Tree view load | 8.5s | 0.3s | **28x faster!** ⚡ |
| Search domain | ERROR | 0.1s | **Possível!** |
| read_group | 12s | 0.2s | **60x faster!** 🚀 |
| Single access | 0.001s | 0.0005s | 2x faster |

**Tradeoff:**

| Aspecto | Sem Store | Com Store |
|---------|-----------|-----------|
| **Read Speed** | Slow | ⚡ Fast |
| **Write Speed** | ⚡ Fast | Slow (recompute) |
| **DB Size** | Small | Larger |
| **Freshness** | Always | Depends |

---

## 🔥 PROBLEMA #3: ORM OVERHEAD (Quando usar SQL direto)

### Quando ORM é MUITO Lento

**ORM overhead inclui:**
1. Access rights check (per record!)
2. Record rules evaluation
3. Computed fields trigger
4. write() triggers (onchange, constraints, etc)
5. Chatter/tracking updates
6. Object instantiation

**Resultado:**
```
Bulk update 10,000 records:
  ORM: ~45 seconds
  SQL: ~0.8 seconds
= 56x SLOWER! 💀
```

---

### QUANDO Usar SQL Direto

**✅ USE SQL SE:**

1. **Bulk Updates (>1000 records):**
```python
# ❌ ORM LENTO
partners = self.env['res.partner'].search([('country_id', '=', False)])
partners.write({'active': False})
# 10,000 partners = ~30s

# ✅ SQL RÁPIDO
self.env.cr.execute("""
    UPDATE res_partner
    SET active = FALSE
    WHERE country_id IS NULL
""")
self.env['res.partner'].invalidate_cache()  # CRÍTICO!
# 10,000 partners = ~0.5s ⚡
```

2. **Complex Queries (joins, aggregations):**
```python
# ❌ ORM - Múltiplas queries + Python processing
# Muito lento!

# ✅ SQL - Uma query otimizada
self.env.cr.execute("""
    SELECT
        p.id,
        p.name,
        COUNT(DISTINCT so.id) as order_count,
        SUM(sol.price_total) as total_revenue,
        AVG(sol.margin) as avg_margin
    FROM res_partner p
    LEFT JOIN sale_order so ON so.partner_id = p.id
    LEFT JOIN sale_order_line sol ON sol.order_id = so.id
    WHERE so.date_order >= %s
    GROUP BY p.id, p.name
    HAVING SUM(sol.price_total) > %s
    ORDER BY total_revenue DESC
    LIMIT 10
""", (start_date, min_revenue))

results = self.env.cr.dictfetchall()
```

3. **Mass Data Import:**
```python
# ✅ SQL COPY para imports massivos
with open('/tmp/partners.csv') as f:
    self.env.cr.copy_expert("""
        COPY res_partner (name, email, phone)
        FROM STDIN WITH CSV HEADER
    """, f)

# Faster que create() em loop (100x+!)
```

---

### CUIDADOS ao Usar SQL Direto

**❌ NUNCA:**

1. **Esquecer de invalidar cache:**
```python
self.env.cr.execute("UPDATE res_partner SET active=FALSE WHERE id=1")
# ❌ Cache ainda tem active=True!

# ✅ SEMPRE invalidar
self.env.cr.execute("UPDATE res_partner SET active=FALSE WHERE id=1")
self.env['res.partner'].invalidate_cache()  # ou invalidate_cache(['active'])
```

2. **SQL Injection (CRÍTICO!):**
```python
# ❌ VULNERABILITY!
user_input = request.params['name']
self.env.cr.execute(f"SELECT * FROM res_partner WHERE name = '{user_input}'")
# Exploitable: user_input = "' OR '1'='1"

# ✅ SAFE - Use %s placeholder
self.env.cr.execute(
    "SELECT * FROM res_partner WHERE name = %s",
    (user_input,)  # Tupla! Mesmo para 1 param
)
```

3. **Bypass Security (access rights/record rules):**
```python
# SQL bypassa TUDO! Use com cuidado
# Se precisa de segurança, use ORM com sudo()
```

4. **Commit manual (geralmente errado):**
```python
# ❌ RARAMENTE necessário
self.env.cr.commit()

# Odoo gerencia transactions automaticamente!
# Só commitar manualmente em casos MUITO específicos
```

---

### Quando NÃO Usar SQL

**❌ NÃO USE SQL para:**

1. **Operações normais CRUD**
```python
# Use ORM - mais seguro e manutenível
partner = self.env['res.partner'].create({'name': 'Test'})
partner.write({'email': 'test@example.com'})
```

2. **Quando security importa**
```python
# ORM respeita access rights e record rules
# SQL bypassa TUDO!
```

3. **Quando triggers/hooks são necessários**
```python
# ORM dispara:
# - @api.constrains
# - compute fields
# - onchange
# - tracking/chatter

# SQL dispara: NADA!
```

---

## 🔥 PROBLEMA #4: POSTGRESQL NÃO OTIMIZADO

### Configurações Essenciais

**postgresql.conf - SEMPRE ajustar:**

```ini
# MEMÓRIA (ajustar para seu servidor!)
# Regra: 25-40% da RAM disponível
shared_buffers = 4GB          # Se servidor tem 16GB RAM
effective_cache_size = 12GB   # ~75% RAM (PostgreSQL + OS cache)
work_mem = 50MB              # Por query worker
maintenance_work_mem = 1GB   # Para VACUUM, CREATE INDEX

# CONEXÕES
max_connections = 200        # Odoo workers * 2 + buffer
```

**Performance Tuning:**

```ini
# PLANNER
random_page_cost = 1.1       # SSD (default 4.0 é para HDD!)
effective_io_concurrency = 200  # SSD concurrent I/O

# QUERY EXECUTION
max_parallel_workers_per_gather = 4
max_worker_processes = 8

# LOGGING (essencial para debug!)
log_min_duration_statement = 1000  # Log queries > 1s
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

---

### Índices Críticos

**Criar índices para:**

1. **Campos em WHERE frequentes:**
```sql
-- Se filtra por state frequentemente:
CREATE INDEX idx_crm_lead_state ON crm_lead(state);

-- Se filtra por date range:
CREATE INDEX idx_sale_order_date ON sale_order(date_order);

-- Partial index (mais eficiente):
CREATE INDEX idx_so_confirmed ON sale_order(date_order)
WHERE state IN ('sale', 'done');
```

2. **Campos em JOIN:**
```sql
-- Foreign keys (Odoo NÃO cria automaticamente para todos!)
CREATE INDEX idx_sol_order_id ON sale_order_line(order_id);
```

3. **Campos em GROUP BY / ORDER BY:**
```sql
-- Se agrupa/ordena por partner:
CREATE INDEX idx_invoice_partner ON account_move(partner_id, invoice_date);
```

4. **Campos de busca (name, ref, etc):**
```sql
-- Índice trigram para LIKE '%text%'
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_partner_name_trgm ON res_partner
USING gin(name gin_trgm_ops);

-- Agora busca ILIKE '%nome%' é rápida! ⚡
```

---

### Monitoramento de Performance

**1. Slow Query Log:**

```sql
-- Ver queries mais lentas
SELECT
    calls,
    total_exec_time,
    mean_exec_time,
    query
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Requer: shared_preload_libraries = 'pg_stat_statements'
```

**2. Identificar Missing Indexes:**

```sql
-- Tables com muitos seq scans (precisam index!)
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / seq_scan as avg_seq_tup
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 10;
```

**3. Index Usage:**

```sql
-- Índices não usados (podem ser removidos)
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
    AND indexrelname NOT LIKE '%_pkey';
```

---

### VACUUM e ANALYZE

**CRÍTICO para performance:**

```sql
-- Configurar autovacuum (postgresql.conf)
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 20s  # Check a cada 20s

-- Manual vacuum (após bulk operations)
VACUUM ANALYZE res_partner;
VACUUM ANALYZE account_move;

-- VACUUM FULL (locks table! Fazer fora do horário)
VACUUM FULL res_partner;  # Recupera espaço em disco
```

**Por que importa:**
- PostgreSQL não deleta rows fisicamente (MVCC)
- VACUUM limpa dead tuples
- ANALYZE atualiza statistics do planner
- Sem VACUUM: queries ficam lentas com tempo!

---

## 🔥 PROBLEMA #5: PYTHON INEFICIENTE

### Patterns Ineficientes

**❌ EVITAR:**

1. **Loops desnecessários:**
```python
# ❌ LENTO
total = 0
for line in order.order_line:
    total += line.price_total

# ✅ RÁPIDO
total = sum(order.order_line.mapped('price_total'))
```

2. **Concatenação em loop:**
```python
# ❌ LENTO (strings são immutable!)
result = ""
for item in items:
    result += item + "\n"

# ✅ RÁPIDO
result = "\n".join(items)
```

3. **Criar/deletar em loop:**
```python
# ❌ LENTO - N creates
for data in import_data:
    self.env['res.partner'].create(data)

# ✅ RÁPIDO - Batch create
self.env['res.partner'].create(import_data)  # Lista!
```

4. **Multiple searches:**
```python
# ❌ LENTO
partner_a = self.env['res.partner'].search([('id', '=', 1)])
partner_b = self.env['res.partner'].search([('id', '=', 2)])
partner_c = self.env['res.partner'].search([('id', '=', 3)])

# ✅ RÁPIDO
partners = self.env['res.partner'].browse([1, 2, 3])
```

---

### List Comprehensions vs Loops

```python
# ❌ LENTO
result = []
for item in items:
    if item.active:
        result.append(item.name.upper())

# ✅ RÁPIDO
result = [item.name.upper() for item in items if item.active]

# ⚡ MAIS RÁPIDO (Odoo specific)
result = items.filtered(lambda r: r.active).mapped(lambda r: r.name.upper())
```

---

## 📊 PERFORMANCE CHECKLIST

### Desenvolvimento

```
[ ] Computed fields com @api.depends completo?
[ ] store=True em campos acessados frequentemente?
[ ] Usando mapped() antes de loops?
[ ] Bulk operations ao invés de loops?
[ ] SQL direto para bulk updates (>1000)?
[ ] Invalidate cache após SQL direto?
[ ] Queries parametrizadas (%s) - NUNCA f-string?
```

### Database

```
[ ] shared_buffers = 25-40% RAM?
[ ] random_page_cost = 1.1 (se SSD)?
[ ] Índices em campos WHERE/JOIN/GROUP BY?
[ ] Slow query log habilitado?
[ ] VACUUM ANALYZE rodando regularmente?
[ ] pg_stat_statements habilitado?
```

### Produção

```
[ ] Odoo workers adequados (2*CPU cores + 1)?
[ ] PostgreSQL max_connections adequado?
[ ] Monitoring de queries lentas?
[ ] Alerta para queries >5s?
[ ] DB backup não interferindo com performance?
[ ] Filestore em SSD?
```

---

## 🎯 QUICK WINS IMEDIATOS

### Top 5 Mudanças com Maior ROI

**1. Fix N+1 Queries (ROI: 🚀🚀🚀🚀🚀)**
```
Esforço: 1-2 dias
Impacto: 10-50x faster listagens
Prioridade: CRÍTICA!
```

**2. Add Indexes (ROI: 🚀🚀🚀🚀)**
```
Esforço: 2-4 horas
Impacto: 5-20x faster queries
Prioridade: ALTA
```

**3. shared_buffers Tuning (ROI: 🚀🚀🚀)**
```
Esforço: 15 minutos
Impacto: 2-5x faster overall
Prioridade: ALTA
```

**4. store=True em Campos Chave (ROI: 🚀🚀🚀)**
```
Esforço: 1 dia
Impacto: 20-100x faster tree views
Prioridade: ALTA
```

**5. Migrate para v18 (ROI: 🚀🚀🚀🚀🚀)**
```
Esforço: 1-3 meses
Impacto: 3.7x faster tudo!
Prioridade: ALTA (se em v15/16)
```

---

## 📚 FERRAMENTAS DE PROFILING

### 1. Odoo Profiler (Built-in)

```python
# Em config
odoo-bin --log-level=debug --log-sql

# Logs mostram todas queries executadas
```

### 2. Python cProfile

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Código a profiler
result = self.my_slow_method()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

### 3. PostgreSQL EXPLAIN

```sql
EXPLAIN ANALYZE
SELECT *
FROM res_partner
WHERE name ILIKE '%odoo%';

-- Mostra:
-- - Seq Scan vs Index Scan
-- - Tempo de execução
-- - Rows estimadas vs reais
-- - Bottlenecks
```

### 4. pgBadger (Log Analysis)

```bash
# Gera relatório HTML de slow queries
pgbadger /var/log/postgresql/postgresql-*.log -o report.html
```

---

## 🎓 LIÇÕES APRENDIDAS

1. **N+1 é o problema #1** - Resolver isso é 80% da otimização
2. **ORM tem custo** - SQL direto para bulk é OK
3. **Índices são ouro** - Mas não crie demais (slow writes)
4. **store=True é tradeoff** - Rápido read, slow write
5. **PostgreSQL tuning é essencial** - Default configs são ruins
6. **search_fetch() v17.4+ é revolucionário** - Use sempre!
7. **v18 é 3.7x faster** - Migração vale muito a pena
8. **Profiling antes de otimizar** - Não adivinhe, meça!
9. **Computed fields com store** - Maioria precisa!
10. **Invalidate cache após SQL** - NUNCA esqueça!

---

**Criado:** 2025-11-17
**Sprint:** 4 - Auto-Educação Odoo
**Aplicável:** v15, v16, v17, v18 (todos!)
**Próxima revisão:** Quando descobrir novos patterns

**Ver também:**
- [Common Errors v15](./common-errors-15.md)
- [Breaking Changes v17](./breaking-changes-17.md)
- [What's New v18](./whats-new-18.md)
- [Security Best Practices](./security-best-practices.md)
