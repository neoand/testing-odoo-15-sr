# 🐛 Erros Comuns Odoo 15 - Soluções Validadas

> **Fonte:** Análise de GitHub Issues + Stack Overflow + Documentação Oficial
> **Data:** 2025-11-17
> **Status:** Conhecimento permanente

---

## 🚨 CRÍTICO: Odoo 15 Não Tem Mais Suporte!

**⚠️ IMPORTANTE:** Odoo Enterprise 15.0 perdeu suporte oficial em **Outubro/2024**
- Não recebe mais security patches
- Vulnerabilidades não serão corrigidas
- **Ação recomendada:** Planejar migração para versão suportada

---

## 1️⃣ Erros de Instalação/Setup

### Bug #80567: Erro ao Criar Database

**Sintoma:**
- Erro durante criação de database no Odoo 15
- Processo falha no meio da instalação

**Solução:**
```bash
# Verificar logs PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log

# Comum: permissões incorretas
sudo chown -R postgres:postgres /var/lib/postgresql/
sudo systemctl restart postgresql

# Verificar encoding
sudo -u postgres psql -c "SHOW server_encoding;"
# Deve ser UTF8
```

**Prevenção:**
- ✅ Sempre criar database com encoding UTF8
- ✅ Verificar permissões PostgreSQL antes
- ✅ Testar conexão com psql primeiro

---

### Bug #78294: Erro ao Atualizar Community → Enterprise

**Sintoma:**
```
TypeError: Cannot read properties of undefined
```
Ocorre ao clicar no menu home após instalar "web enterprise"

**Solução:**
```bash
# 1. Limpar cache de assets
./odoo-bin --addons-path=... -d DATABASE --stop-after-init

# 2. Atualizar módulo web
./odoo-bin -d DATABASE -u web --stop-after-init

# 3. Restart completo
sudo systemctl restart odoo
```

**Prevenção:**
- ✅ Sempre fazer backup antes de upgrade
- ✅ Testar em ambiente de staging primeiro
- ✅ Limpar cache após mudanças de edição

---

### Bug #70574: Template 'website.new_content_loader' Not Found

**Sintoma:**
```
QWeb2 Error: Template 'website.new_content_loader' not found
```

**Causa Raiz:**
Módulo website instalado incorretamente ou assets não compilados

**Solução:**
```bash
# 1. Reinstalar módulo website
./odoo-bin -d DATABASE -u website --stop-after-init

# 2. Rebuild assets
./odoo-bin -d DATABASE --stop-after-init --no-http

# 3. Se persistir, dropar e recriar
./odoo-bin -d DATABASE -i website --stop-after-init
```

**Prevenção:**
- ✅ Verificar se módulo website está na lista de addons-path
- ✅ Não modificar templates core sem herança

---

## 2️⃣ Erros de Accounting (CRÍTICO!)

### Bug #91873: Concurrency Errors em account.move (v14+)

**Sintoma:**
```
TransactionRollbackError: could not serialize access due to concurrent update
```

**Contexto:**
Aumentou **consideravelmente** desde Odoo v14.0+, afetando:
- Transações ecommerce
- Invoices criados por múltiplos usuários
- Subscriptions

**Causa Raiz:**
Lock otimista muito agressivo em `account.move`

**Solução Workaround:**
```python
# Em models que criam/atualizam invoices
from odoo.exceptions import UserError
import time

MAX_RETRIES = 3
for attempt in range(MAX_RETRIES):
    try:
        with self.env.cr.savepoint():
            # Operação que falha
            invoice.write({'state': 'posted'})
            break
    except psycopg2.extensions.TransactionRollbackError:
        if attempt == MAX_RETRIES - 1:
            raise UserError(_('Sistema ocupado, tente novamente.'))
        time.sleep(0.5 * (attempt + 1))  # Backoff exponencial
```

**Solução Permanente:**
- Upgrade para versão mais recente (fix oficial)
- Ou aplicar patch da comunidade (verificar OCA)

**Prevenção:**
- ⚠️ Evitar múltiplos usuários editando mesma invoice
- ✅ Implementar retry com backoff
- ✅ Monitorar logs para detect

ar frequência

---

## 3️⃣ Erros de Manufacturing (MRP)

### Bug: Componentes de Kit Não Atualizados

**Sintoma:**
Ao usar botão "Update BOM", quantidades de componentes não atualizam corretamente para kits

**Solução:**
```python
# Foi corrigido em PRs #203029, #203021, #203017
# Atualizar para versão com patch ou aplicar manualmente

# Workaround: forçar recompute
manufacturing_order.move_raw_ids._compute_product_qty()
manufacturing_order.move_finished_ids._compute_product_qty()
```

---

## 4️⃣ Performance Issues - N+1 Queries

### Problema #1: N+1 Query Pattern

**Sintoma:**
Listagens muito lentas (>5s) com muitos records

**Causa Raiz:**
```python
# ❌ ERRO CLÁSSICO - N+1 queries
for partner in partners:
    print(partner.invoice_ids)  # Query a cada iteração!
```

**Solução:**
```python
# ✅ CORRETO - Prefetch automático
# Opção 1: @api.depends correto
@api.depends('partner_id.invoice_ids')
def _compute_invoice_count(self):
    for record in self:
        record.invoice_count = len(record.partner_id.invoice_ids)

# Opção 2: Usar mapped() para prefetch
partners.mapped('invoice_ids')  # Carrega tudo de uma vez
for partner in partners:
    print(partner.invoice_ids)  # Já está em cache!

# Opção 3: read_group para agregações
data = self.env['account.move'].read_group(
    [('partner_id', 'in', partner_ids)],
    ['partner_id', 'amount_total:sum'],
    ['partner_id']
)
```

**Best Practices:**
- ✅ SEMPRE usar `@api.depends()` com campos relacionados **completos**
- ✅ Usar `mapped()` antes de loops
- ✅ Usar `read_group()` para agregações
- ✅ Considerar `store=True` em computed fields muito acessados

---

### Problema #2: ORM Muito Lento

**Sintoma:**
Operações bulk muito lentas mesmo sem N+1

**Causa:**
ORM é **várias magnitudes mais lento** que SQL direto devido a:
- Verificação de access rights
- Verificação de record rules
- Recompute de campos dependentes
- Triggers de write()

**Solução:**
```python
# Para operações bulk críticas, usar SQL direto
self.env.cr.execute("""
    UPDATE res_partner
    SET active = FALSE
    WHERE create_date < %s
""", (cutoff_date,))

# IMPORTANTE: Invalidar cache depois!
self.env['res.partner'].invalidate_cache()
```

**Quando usar:**
- ✅ Bulk updates (>1000 records)
- ✅ Relatórios complexos
- ✅ Imports massivos
- ❌ NUNCA em operações normais de CRUD

---

### Problema #3: PostgreSQL Não Otimizado

**Sintoma:**
Queries lentas mesmo otimizadas

**Solução:**
```sql
-- Ajustar shared_buffers (25-40% da RAM)
-- Em postgresql.conf
shared_buffers = 4GB  # Se servidor tem 16GB RAM

-- Habilitar query logging
log_min_duration_statement = 1000  # Log queries >1s

-- Criar índices faltantes
CREATE INDEX idx_partner_vat ON res_partner(vat);
CREATE INDEX idx_invoice_date ON account_move(invoice_date) WHERE move_type IN ('out_invoice', 'out_refund');
```

**Monitoramento:**
```sql
-- Ver queries lentas
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## 5️⃣ Security Issues

### ⚠️ Vulnerabilidades JavaScript Libraries

**Problema:**
jQuery e underscore.js usados pelo Odoo 15 têm vulnerabilidades conhecidas

**Status:**
Patches aplicados no código Odoo, mas bibliotecas ainda antigas

**Mitigação:**
- ✅ Não expor Odoo diretamente (usar nginx/apache na frente)
- ✅ CSP headers configurados
- ✅ Atualizar para versão suportada ASAP

---

### SQL Injection Prevention

**❌ NUNCA FAZER:**
```python
# SQL INJECTION VULNERABILITY!
self.env.cr.execute(f"SELECT * FROM res_partner WHERE name = '{user_input}'")
self.env.cr.execute("SELECT * FROM res_partner WHERE id = " + str(user_id))
```

**✅ SEMPRE FAZER:**
```python
# SEGURO - Usar %s com tupla
self.env.cr.execute("SELECT * FROM res_partner WHERE name = %s", (user_input,))
self.env.cr.execute("SELECT * FROM res_partner WHERE id = %s", (user_id,))
```

---

### XSS Prevention

**Odoo tem proteção automática via QWeb:**
```xml
<!-- Escapado automaticamente -->
<span t-field="partner.name"/>
<span t-esc="partner.name"/>

<!-- NÃO escapado (PERIGO!) -->
<span t-raw="partner.description"/>  <!-- Só usar se já sanitizado! -->
```

**Em Python:**
```python
from markupsafe import Markup, escape

# ❌ PERIGOSO
description_html = f"<p>{user_input}</p>"

# ✅ SEGURO
description_html = Markup("<p>%s</p>") % escape(user_input)
```

---

## 📊 Checklist de Prevenção Geral

### Antes de Desenvolver
```
[ ] Li os erros comuns desta lista?
[ ] Vou evitar N+1 queries? (@api.depends correto)
[ ] Vou usar %s para SQL queries?
[ ] Vou escapar HTML user input?
[ ] Tenho índices nos campos buscados?
```

### Antes de Deploy
```
[ ] Testei com >1000 records?
[ ] Verifiquei logs de queries lentas?
[ ] Rodei security audit?
[ ] Backup está OK?
[ ] Rollback plan existe?
```

---

## 🎓 Lições Aprendidas

1. **N+1 queries é o problema #1 de performance**
   - SEMPRE especificar campo completo em @api.depends
   - Usar mapped() antes de loops

2. **Concurrency em accounting é real**
   - Implementar retry com backoff
   - Considerar row-level locking

3. **Security matters**
   - Odoo 15 sem suporte = risco
   - Planejar upgrade urgente

4. **PostgreSQL tuning é essencial**
   - shared_buffers = 25-40% RAM
   - Índices em campos buscados

5. **ORM tem custo**
   - Para bulk: considerar SQL direto
   - Sempre invalidar cache depois

---

**Última atualização:** 2025-11-17
**Próxima revisão:** Ao encontrar novos erros
**Fonte:** Sprint 4 Auto-Educação Profunda
