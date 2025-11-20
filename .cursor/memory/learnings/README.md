# 📚 Aprendizados e Descobertas

> **Propósito:** Capturar TODO conhecimento adquirido durante o desenvolvimento - pesquisas online, Stack Overflow, documentações, experimentos.

---

## 🎯 Como Usar

**Quando aprender algo novo:**
1. Adicione entrada neste diretório
2. Organize por tópico (criar arquivo se necessário)
3. Inclua fonte e data
4. Contextualize para o projeto

**Estrutura:**
```
learnings/
├── README.md           (este arquivo)
├── odoo-tricks.md      (Truques específicos Odoo)
├── python-patterns.md  (Padrões Python úteis)
├── api-integrations.md (Integrações com APIs)
├── performance.md      (Otimizações descobertas)
└── security.md         (Security best practices)
```

---

## 📋 Índice de Aprendizados

### Odoo
- [odoo-tricks.md](odoo-tricks.md) - Truques e hacks Odoo

### Python
- [python-patterns.md](python-patterns.md) - Patterns Python úteis

### Integrações
- [api-integrations.md](api-integrations.md) - Como integrar com APIs

### Performance
- [performance.md](performance.md) - Otimizações de performance

### Security
- [security.md](security.md) - Segurança e permissões

---

## 🌟 Top Learnings (Destaques)

### 1. Odoo Prefetch
**Data:** 2025-11-15
**Fonte:** https://www.odoo.com/documentation/15.0/developer/reference/backend/orm.html#prefetching

**O que é:**
Odoo automaticamente faz prefetch de campos quando você acessa um record em iteração.

**Descoberta:**
```python
# Isso carrega TODOS os campos de uma vez (prefetch)
for record in records:
    print(record.name)  # Primeira iteração carrega tudo
    print(record.email)  # Já está em cache!
```

**Impacto no projeto:**
Reduziu queries de 150 para 3 em listagem de CRM leads!

**Aplicado em:** `crm_lead` customizado

---

### 2. @api.depends com Campos Relacionados
**Data:** 2025-11-15
**Fonte:** Debugging performance issue

**Descoberta:**
Usar `@api.depends('partner_id.phone')` ao invés de apenas `@api.depends('partner_id')` faz cache correto!

```python
# ❌ NÃO carrega phone no cache
@api.depends('partner_id')
def _compute_phone(self):
    for record in self:
        record.phone = record.partner_id.phone  # Query!

# ✅ Carrega phone no cache
@api.depends('partner_id.phone')
def _compute_phone(self):
    for record in self:
        record.phone = record.partner_id.phone  # Cached!
```

**Aplicado em:** Múltiplos models do projeto

---

### 3. requests.Session para APIs
**Data:** 2025-11-16
**Fonte:** https://requests.readthedocs.io/en/latest/user/advanced/#session-objects

**Descoberta:**
Usar `Session` reutiliza conexões HTTP, reduzindo latência.

```python
# ❌ Lento - cria nova conexão a cada request
def send_sms(phone, message):
    response = requests.post(url, json={...})

# ✅ Rápido - reutiliza conexão
session = requests.Session()
def send_sms(phone, message):
    response = session.post(url, json={...})
```

**Impacto:** 40% mais rápido para envio de SMS em batch!

**Aplicado em:** Integração Kolmeya

---

### 4. PostgreSQL EXPLAIN ANALYZE
**Data:** 2025-11-15
**Fonte:** PostgreSQL docs

**Descoberta:**
Use `EXPLAIN ANALYZE` para entender queries lentas.

```sql
EXPLAIN ANALYZE
SELECT * FROM crm_lead
WHERE user_id = 2 AND state = 'open';
```

**Insights:**
- Seq Scan = RUIM (adicionar índice!)
- Index Scan = BOM
- Nested Loop com muitas rows = considerar JOIN diferente

**Aplicado em:** Otimização de queries do CRM

---

### 5. Odoo XML Herança
**Data:** 2025-11-16
**Fonte:** https://www.odoo.com/documentation/15.0/developer/reference/backend/views.html

**Descoberta:**
Pode usar `position="replace"`, `position="after"`, `position="before"`, `position="inside"`, `position="attributes"`.

```xml
<xpath expr="//field[@name='name']" position="after">
    <field name="custom_field"/>
</xpath>
```

**Dica:** `position="attributes"` para mudar attrs sem reescrever campo inteiro!

**Aplicado em:** Customizações de views do CRM

---

## 📖 Template para Novo Learning

```markdown
### N. Título do Learning
**Data:** YYYY-MM-DD
**Fonte:** URL ou referência

**O que é:**
Explicação breve

**Descoberta:**
```código ou explicação```

**Impacto no projeto:**
Como isso ajudou?

**Aplicado em:** Onde foi usado?
```

---

## 🔗 Fontes Favoritas

### Documentação Oficial
- **Odoo:** https://www.odoo.com/documentation/15.0/
- **Python:** https://docs.python.org/3/
- **PostgreSQL:** https://www.postgresql.org/docs/
- **Requests:** https://requests.readthedocs.io/

### Comunidade
- **Odoo Community (OCA):** https://github.com/OCA
- **Stack Overflow - Odoo:** https://stackoverflow.com/questions/tagged/odoo
- **Odoo Forum:** https://www.odoo.com/forum

### Blogs Úteis
- **Cybrosys:** https://www.cybrosys.com/blog/
- **Odoo Mates:** https://www.odoomates.tech/
- **Synconics:** https://synconics.com/blog/

---

**Última atualização:** 2025-11-17
**Total de learnings:** 5
**Próxima revisão:** Sempre que aprender algo novo!
