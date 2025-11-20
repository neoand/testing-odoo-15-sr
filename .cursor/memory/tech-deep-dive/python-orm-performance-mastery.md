# 🐍 Python/Odoo ORM Performance - Mastery Guide

> **Odoo ORM Optimization** - Técnicas avançadas de performance para Python e ORM do Odoo
>
> **Última atualização:** 2025-11-17
> **Versão Odoo:** 15.0+ (aplicável até 18.0)
> **Status:** ✅ Conhecimento Consolidado

---

## 📚 Índice

1. [ORM Fundamentals](#orm-fundamentals)
2. [N+1 Query Problem](#n1-query-problem)
3. [search_fetch() Optimization](#search_fetch-optimization)
4. [Computed Fields Performance](#computed-fields-performance)
5. [Prefetching Mechanism](#prefetching-mechanism)
6. [SQL Direct Queries](#sql-direct-queries)
7. [Batch Operations](#batch-operations)
8. [Caching Strategies](#caching-strategies)
9. [Best Practices](#best-practices)

---

## 🎯 ORM Fundamentals

### ORM Architecture

```python
# Odoo ORM Layers
┌─────────────────────────────────┐
│   Python Business Logic         │
├─────────────────────────────────┤
│   Odoo ORM (models.py)          │  ← Active Record Pattern
├─────────────────────────────────┤
│   psycopg2 (PostgreSQL driver)  │
├─────────────────────────────────┤
│   PostgreSQL Database           │
└─────────────────────────────────┘
```

### Basic ORM Operations

```python
# Environment and Context
env = self.env  # Current environment
model = env['res.partner']  # Get model

# CRUD Operations
record = model.create({'name': 'John'})  # INSERT
records = model.search([('name', '=', 'John')])  # SELECT WHERE
record.write({'email': 'john@example.com'})  # UPDATE
record.unlink()  # DELETE

# Search variations
all_partners = model.search([])  # All records
active_partners = model.search([('active', '=', True)])
limited = model.search([], limit=10)
ordered = model.search([], order='name ASC')
count = model.search_count([('is_company', '=', True)])

# Read operations
data = records.read(['name', 'email'])  # SELECT specific fields
ids = records.ids  # List of IDs
names = records.mapped('name')  # Extract field values
```

---

## ⚠️ N+1 Query Problem

### The Problem

```python
# ❌ RUIM: N+1 queries (1 query + N queries)
leads = self.env['crm.lead'].search([('state', '=', 'new')])  # 1 query
for lead in leads:  # N iterations
    partner_name = lead.partner_id.name  # N queries! (1 per lead)
    partner_phone = lead.partner_id.phone  # N more queries!
    print(f"{partner_name}: {partner_phone}")

# Result: 1 + 100*2 = 201 queries for 100 leads!
```

**Performance Impact:**
- 100 leads = 201 queries
- Each query ~5ms = 1000ms (1 second)
- Database connection overhead
- Network latency

### Solution 1: Proper @api.depends

```python
from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # ❌ RUIM: Depends sem campo específico
    partner_phone = fields.Char(compute='_compute_partner_phone')

    @api.depends('partner_id')  # ← Não especifica qual campo!
    def _compute_partner_phone(self):
        for record in self:
            record.partner_phone = record.partner_id.phone  # N+1!

    # ✅ BOM: Depends com campo completo
    partner_phone = fields.Char(compute='_compute_partner_phone')

    @api.depends('partner_id.phone')  # ← Especifica campo exato!
    def _compute_partner_phone(self):
        for record in self:
            record.partner_phone = record.partner_id.phone  # Cached! 1 query

    # ✅ MELHOR: Store para campos muito acessados
    partner_phone = fields.Char(
        compute='_compute_partner_phone',
        store=True  # ← Salvo no banco! 0 queries ao ler
    )

    @api.depends('partner_id.phone')
    def _compute_partner_phone(self):
        for record in self:
            record.partner_phone = record.partner_id.phone
```

**Performance:**
- Sem store: 100 leads = 2 queries (1 lead + 1 partners batch)
- Com store: 100 leads = 1 query (direto do banco)
- **Melhoria: 100x mais rápido!**

### Solution 2: Prefetch with mapped()

```python
# ❌ RUIM: Iterar sem prefetch
for lead in leads:
    print(lead.partner_id.name)  # N queries

# ✅ BOM: Prefetch com mapped()
partners = leads.mapped('partner_id')  # 1 query - fetch all partners
for lead in leads:
    print(lead.partner_id.name)  # 0 additional queries (cached)

# ✅ MELHOR: Processar valores diretamente
partner_names = leads.mapped('partner_id.name')  # 1 query
for name in partner_names:
    print(name)
```

### Solution 3: Use read()

```python
# ✅ BOM: read() é otimizado
data = leads.read(['name', 'partner_id', 'stage_id'])
# Returns: [{'id': 1, 'name': 'Lead 1', 'partner_id': (5, 'John'), 'stage_id': (2, 'New')}, ...]

# Process data without additional queries
for item in data:
    print(f"{item['name']} - Partner: {item['partner_id'][1]}")
```

---

## 🚀 search_fetch() Optimization

### Odoo 17.4+ Only

```python
# ❌ ANTES (Odoo ≤17.3): 2 queries
leads = self.env['crm.lead'].search([('state', '=', 'new')])  # Query 1
data = leads.read(['name', 'partner_id', 'expected_revenue'])  # Query 2

# ✅ DEPOIS (Odoo 17.4+): 1 query
data = self.env['crm.lead'].search_fetch(
    [('state', '=', 'new')],  # Domain
    ['name', 'partner_id', 'expected_revenue']  # Fields
)

# Retorna lista de dicionários (mesmo que read())
# Performance: 30% mais rápido!
```

**Benefícios:**
- ✅ 1 query ao invés de 2
- ✅ Menos overhead de processamento
- ✅ 30% redução de tempo
- ✅ Compatível com limit, offset, order

**Limitação:**
- ⚠️ Disponível APENAS em Odoo 17.4+
- ⚠️ Nosso projeto (Odoo 15) NÃO tem search_fetch()

---

## 💾 Computed Fields Performance

### Store vs Non-Store

```python
class ProductProduct(models.Model):
    _inherit = 'product.product'

    # ❌ RUIM: Sem store, calculado sempre
    total_stock = fields.Float(
        compute='_compute_total_stock'
    )

    @api.depends('stock_quant_ids.quantity')
    def _compute_total_stock(self):
        for product in self:
            # Query pesada a cada acesso!
            product.total_stock = sum(product.stock_quant_ids.mapped('quantity'))

    # ✅ BOM: Com store, calculado 1x
    total_stock = fields.Float(
        compute='_compute_total_stock',
        store=True  # ← Salvo no banco
    )

    @api.depends('stock_quant_ids.quantity')
    def _compute_total_stock(self):
        for product in self:
            # Executa apenas quando dependências mudam
            product.total_stock = sum(product.stock_quant_ids.mapped('quantity'))
```

**Quando usar store=True:**
- ✅ Campo acessado frequentemente (listagens, relatórios)
- ✅ Cálculo custoso (queries, loops, agregações)
- ✅ Dependências não mudam com frequência
- ✅ Espaço em disco não é problema

**Quando NÃO usar store:**
- ❌ Campo raramente acessado
- ❌ Cálculo trivial (concatenação strings)
- ❌ Dependências mudam constantemente
- ❌ Dados sensíveis ao tempo (datetime.now())

**Performance Impact:**
| Scenario | Without store | With store | Improvement |
|----------|---------------|------------|-------------|
| List 100 products | 100 queries | 0 queries | ∞ |
| Read 1 product | 1 query | 0 queries | - |
| Report 1000+ | 1000+ queries | 0 queries | **100x faster** |

---

## 🔄 Prefetching Mechanism

### How Prefetching Works

```python
# Odoo ORM Prefetch Automático
leads = self.env['crm.lead'].search([], limit=100)

# Primeiro acesso a um campo
first_lead = leads[0]
name = first_lead.name  # ← Trigger: ORM fetches 'name' for ALL 100 leads!

# Acessos subsequentes
for lead in leads:
    print(lead.name)  # 0 queries - all cached!
```

**Prefetch Size:** Default 1000 records

### Controlling Prefetch

```python
# Disable prefetch (raramente necessário)
leads = self.env['crm.lead'].with_context(prefetch_fields=False).search([])

# Custom prefetch size
leads = self.env['crm.lead'].with_context(prefetch={'limit': 500}).search([])
```

### Prefetch with Related Fields

```python
# ✅ BOM: Prefetch de campos relacionados
leads = self.env['crm.lead'].search([])

# Trigger prefetch de partners
_ = leads.mapped('partner_id')

# Agora todos os acessos são cached
for lead in leads:
    print(lead.partner_id.name)  # 0 queries
    print(lead.partner_id.email)  # 0 queries
```

---

## 💻 SQL Direct Queries

### When to Use SQL

Use SQL direto quando:
- ✅ Agregações complexas (SUM, AVG, GROUP BY)
- ✅ Joins complexos (3+ tabelas)
- ✅ Performance crítica (relatórios, dashboards)
- ✅ Bulk operations (milhares de registros)

**NÃO use SQL para:**
- ❌ CRUD simples (use ORM)
- ❌ Quando ORM é suficiente
- ❌ Lógica de negócio complexa

### SQL Queries Safely

```python
from odoo import models, api

class ReportSales(models.Model):
    _name = 'report.sales'

    def get_sales_statistics(self, date_from, date_to):
        """Estatísticas de vendas por vendedor."""

        # ✅ SEGURO: Use %s para parâmetros
        query = """
            SELECT
                ru.name as seller_name,
                COUNT(so.id) as order_count,
                SUM(so.amount_total) as total_amount,
                AVG(so.amount_total) as avg_amount
            FROM sale_order so
            JOIN res_users ru ON so.user_id = ru.id
            WHERE so.state = 'sale'
              AND so.date_order >= %s
              AND so.date_order <= %s
            GROUP BY ru.id, ru.name
            ORDER BY total_amount DESC
        """

        # Execute com parâmetros
        self.env.cr.execute(query, (date_from, date_to))

        # Fetch results
        results = self.env.cr.dictfetchall()
        # Returns: [{'seller_name': 'John', 'order_count': 10, 'total_amount': 5000, ...}, ...]

        return results

    def bulk_update_prices(self, product_ids, discount_percent):
        """Atualização em massa de preços."""

        # ❌ NUNCA: String formatting (SQL INJECTION!)
        # query = f"UPDATE product_product SET list_price = list_price * {discount_percent} WHERE id IN {tuple(product_ids)}"

        # ✅ SEGURO: Parâmetros
        query = """
            UPDATE product_product
            SET list_price = list_price * %s
            WHERE id = ANY(%s)
        """
        self.env.cr.execute(query, (discount_percent, product_ids))

        # ⚠️ IMPORTANTE: Invalidar cache!
        self.env['product.product'].invalidate_cache(['list_price'], product_ids)
```

### SQL Performance Tips

```python
# 1. Use EXPLAIN ANALYZE para debug
self.env.cr.execute("EXPLAIN ANALYZE SELECT ...")
plan = self.env.cr.fetchall()
print(plan)

# 2. Use índices apropriados (ver postgresql-mastery.md)

# 3. Limit results
query = "SELECT * FROM sale_order LIMIT 1000"  # Sempre use LIMIT!

# 4. Use prepared statements (psycopg2 faz automaticamente com %s)
```

---

## 📦 Batch Operations

### create_multi (Odoo 13+)

```python
# ❌ RUIM: Criar 1 por 1
for i in range(1000):
    self.env['product.product'].create({'name': f'Product {i}'})
# Result: 1000 queries

# ✅ BOM: Batch create
vals_list = [{'name': f'Product {i}'} for i in range(1000)]
self.env['product.product'].create(vals_list)
# Result: 1 query (com múltiplos INSERTs)
# Performance: 100x mais rápido!
```

### Batch Write

```python
# ❌ RUIM: Write 1 por 1
for product in products:
    product.write({'list_price': product.list_price * 1.1})
# Result: N queries

# ✅ BOM: Batch write
products.write({'list_price': sql.SQL('list_price * 1.1')})
# Result: 1 query
```

### Batch Unlink

```python
# ❌ RUIM: Delete 1 por 1
for partner in old_partners:
    partner.unlink()

# ✅ BOM: Batch delete
old_partners.unlink()
# Result: 1 query (DELETE WHERE id IN (...))
```

---

## 💾 Caching Strategies

### ORM Cache

```python
# Cache é automático para campos já acessados
lead = self.env['crm.lead'].browse(123)
name = lead.name  # Query executada
name_again = lead.name  # Cache! 0 queries

# Invalidar cache manualmente
lead.invalidate_cache(['name'])
name_fresh = lead.name  # Query executada novamente
```

### @tools.ormcache Decorator

```python
from odoo import models, tools

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @tools.ormcache('product_id')
    def get_stock_info(self, product_id):
        """Cached function - chamadas repetidas retornam cache."""
        product = self.browse(product_id)
        return {
            'qty': sum(product.stock_quant_ids.mapped('quantity')),
            'value': product.standard_price * qty
        }

    # Limpar cache quando necessário
    def write(self, vals):
        result = super().write(vals)
        if 'standard_price' in vals:
            self.get_stock_info.clear_cache(self)
        return result
```

### Redis/Memcached (Externo)

```python
# Para caching avançado (não nativo do Odoo)
import redis

class MyModel(models.Model):
    _name = 'my.model'

    def get_expensive_data(self):
        cache_key = f'expensive_data_{self.id}'

        # Check Redis first
        redis_client = redis.Redis(host='localhost', port=6379)
        cached = redis_client.get(cache_key)

        if cached:
            return json.loads(cached)

        # Compute data
        data = self._compute_expensive_data()

        # Cache for 1 hour
        redis_client.setex(cache_key, 3600, json.dumps(data))

        return data
```

---

## 🎯 Best Practices

### 1. Sempre Especificar Campos

```python
# ❌ RUIM: Fetch todos os campos
partners = self.env['res.partner'].search([])
data = partners.read()  # Fetch ALL fields (100+ fields!)

# ✅ BOM: Fetch apenas necessários
data = partners.read(['name', 'email', 'phone'])  # 3 fields only
```

### 2. Use Domain Filters

```python
# ❌ RUIM: Fetch all e filtrar em Python
all_leads = self.env['crm.lead'].search([])
new_leads = [l for l in all_leads if l.state == 'new']  # Filter in Python!

# ✅ BOM: Filtrar no banco
new_leads = self.env['crm.lead'].search([('state', '=', 'new')])  # WHERE clause
```

### 3. Limit Large Datasets

```python
# ❌ RUIM: Fetch milhões de registros
all_logs = self.env['mail.message'].search([])  # OOM risk!

# ✅ BOM: Use limit e pagination
page_size = 1000
offset = 0
while True:
    logs = self.env['mail.message'].search([], limit=page_size, offset=offset)
    if not logs:
        break
    process(logs)
    offset += page_size
```

### 4. Avoid Computed Fields in Loops

```python
# ❌ RUIM: Acessar computed em loop
for product in products:
    if product.qty_available > 0:  # Computed field - expensive!
        available_products.append(product)

# ✅ BOM: Filter no banco com SQL ou stored computed
available_products = products.filtered(lambda p: p.qty_available > 0)
# Melhor ainda: Use domain search se campo é stored
```

### 5. Use sudo() Wisely

```python
# ⚠️ CUIDADO: sudo() bypassa permissões
partner = self.env['res.partner'].sudo().search([])  # Admin access!

# ✅ BOM: Use apenas quando necessário e validado
if self.env.user.has_group('base.group_system'):
    partner = self.env['res.partner'].sudo().create(vals)
```

---

## 📊 Performance Checklist

**Antes de Fazer Deploy:**

- [ ] Todos campos computed frequentes têm `store=True`
- [ ] N+1 queries eliminados (verificar com pg_stat_statements)
- [ ] @api.depends especifica campos completos (ex: 'partner_id.name')
- [ ] Bulk operations usam create/write em batch
- [ ] SQL queries usam %s para parâmetros (NUNCA f-strings!)
- [ ] Large datasets têm limit/pagination
- [ ] Computed fields não são chamados em loops
- [ ] Cache invalidado quando necessário
- [ ] PostgreSQL indexes apropriados (ver postgresql-mastery.md)
- [ ] Tests de performance executados

---

## 🔧 Debugging Performance

### Enable SQL Logging

```python
# In odoo.conf or command line
# --log-sql
# --log-level=debug_sql

# Logs mostrarão todas as queries executadas
```

### pg_stat_statements

```sql
-- Habilitar no PostgreSQL
CREATE EXTENSION pg_stat_statements;

-- Ver queries mais lentas
SELECT
    calls,
    mean_exec_time,
    query
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Reset stats
SELECT pg_stat_statements_reset();
```

### Python Profiling

```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()

    # Code to profile
    result = self.expensive_operation()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumtime')
    stats.print_stats(20)  # Top 20 slowest functions

    return result
```

---

## 📚 Recursos

### Documentação Oficial
- **Odoo ORM:** https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html
- **Performance Guidelines:** https://www.odoo.com/documentation/17.0/developer/howtos/rdtraining/14_other_module_techniques.html#performance

### Ferramentas
- **pg_stat_statements:** PostgreSQL query statistics
- **Odoo Profiler:** Built-in profiler (enable with --dev=all)
- **Python cProfile:** Standard library profiling
- **py-spy:** Sampling profiler (no code changes needed)

---

## 💡 Conclusão

**Otimizações essenciais:**
1. ✅ Eliminate N+1 queries (@api.depends completo)
2. ✅ Store computed fields frequentes (20-100x faster)
3. ✅ Use batch operations (100x faster)
4. ✅ Prefetch com mapped() (evita queries extras)
5. ✅ SQL direto para agregações complexas

**Para nosso projeto (Odoo 15):**
- ⚠️ search_fetch() NÃO disponível (Odoo 17.4+ only)
- ✅ Todas outras técnicas aplicáveis
- 📊 Foco em N+1 elimination e stored computed fields

---

**Criado:** 2025-11-17
**Fontes:** Odoo docs, OCA guidelines, experiência prática
**Status:** ✅ Conhecimento Consolidado
**Aplicação:** Imediata - Odoo 15 projeto atual
