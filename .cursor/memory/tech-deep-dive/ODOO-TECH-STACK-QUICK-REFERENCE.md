# ⚡ ODOO TECH STACK - QUICK REFERENCE

> **One-stop reference** para TODAS as tecnologias do ecossistema Odoo
> **Data:** 2025-11-17
> **Uso:** Consulta rápida durante desenvolvimento

---

## 🐘 POSTGRESQL (Database Layer)

### Configuração Essencial (Odoo Produção 16GB RAM)
```ini
shared_buffers = 4GB                    # 25% RAM
effective_cache_size = 12GB             # 75% RAM
work_mem = 50MB                         # Por query
max_connections = 220                    # 100 users * 2 + workers

random_page_cost = 1.1                  # 🔴 CRÍTICO para SSD!
effective_io_concurrency = 200
checkpoint_timeout = 15min
max_wal_size = 4GB

autovacuum = on
autovacuum_naptime = 30s                # Mais agressivo
autovacuum_vacuum_scale_factor = 0.1    # 10% ao invés de 20%
```

**⚠️ NUNCA esquecer:** `random_page_cost = 1.1` (default 4.0 é para HDD!)

### Índices para Odoo
```sql
-- Partial indexes (economizam 50-90% espaço!)
CREATE INDEX idx_lead_active ON crm_lead(user_id, stage_id) WHERE active = true;
CREATE INDEX idx_order_not_cancelled ON sale_order(partner_id, date_order) WHERE state != 'cancel';

-- GIN para full-text search
CREATE INDEX idx_product_desc_gin ON product_template USING GIN (to_tsvector('portuguese', description));

-- mail_message (CRÍTICO!)
CREATE INDEX idx_message_model_res ON mail_message(model, res_id) WHERE model IS NOT NULL;
```

### Backup Diário (Script)
```bash
#!/bin/bash
pg_dump -Fc -f /backup/odoo_$(date +%Y%m%d).dump realcred
aws s3 cp /backup/odoo_$(date +%Y%m%d).dump s3://backups/
find /backup -name "*.dump" -mtime +7 -delete
```

**Cron:** `0 2 * * * /usr/local/bin/odoo-backup.sh`

---

## 🐍 PYTHON/ODOO ORM

### Performance Patterns

#### ❌ N+1 Query (RUIM)
```python
for lead in leads:
    print(lead.partner_id.name)  # Query a cada iteração!
```

#### ✅ Prefetch (BOM)
```python
@api.depends('partner_id.name')
def _compute_partner_name(self):
    for lead in self:
        lead.partner_name = lead.partner_id.name  # Cached!
```

#### ✅ search_fetch() (v17.4+ - 30% FASTER!)
```python
# ANTES (2 queries)
leads = self.env['crm.lead'].search([('state', '=', 'new')])
data = leads.read(['name', 'partner_id'])

# DEPOIS (1 query!)
data = self.env['crm.lead'].search_fetch(
    [('state', '=', 'new')],
    ['name', 'partner_id']
)
```

#### ✅ store=True (20-100x FASTER!)
```python
# Computed field acessado frequentemente
expected_revenue_usd = fields.Float(
    compute='_compute_revenue_usd',
    store=True  # ✅ Cache em DB!
)
```

### Security Best Practices
```python
# ✅ SQL injection safe
self.env.cr.execute("SELECT * FROM res_partner WHERE cpf = %s", (cpf,))

# ❌ SQL injection UNSAFE!
self.env.cr.execute(f"SELECT * FROM res_partner WHERE cpf = '{cpf}'")

# ✅ XSS safe
from odoo.tools import html_sanitize
safe_html = html_sanitize(user_input)

# ✅ sudo() apenas quando REALMENTE necessário
# sudo() here because: Automated process without user context
partner = self.env['res.partner'].sudo().create({...})
```

---

## 🎨 OWL FRONTEND (v17/18)

### Component Básico
```javascript
import { Component, useState, onWillStart, onMounted } from "@odoo/owl";

class MyComponent extends Component {
    static template = "my_module.MyTemplate";

    setup() {
        // Estado reativo
        this.state = useState({
            count: 0,
            items: []
        });

        // Lifecycle hooks
        onWillStart(async () => {
            // Fetch data antes de renderizar
            this.state.items = await this.loadItems();
        });

        onMounted(() => {
            // DOM manipulations
            console.log("Component mounted!");
        });
    }

    async loadItems() {
        const result = await this.env.services.rpc({
            model: 'my.model',
            method: 'search_read',
            args: [[]],
            kwargs: {fields: ['name', 'value']}
        });
        return result;
    }

    increment() {
        this.state.count++;  // Auto re-render!
    }
}
```

### QWeb Template
```xml
<templates>
    <t t-name="my_module.MyTemplate">
        <div class="my-component">
            <h1>Count: <t t-esc="state.count"/></h1>
            <button t-on-click="increment">+1</button>

            <ul>
                <t t-foreach="state.items" t-as="item" t-key="item.id">
                    <li t-esc="item.name"/>
                </t>
            </ul>
        </div>
    </t>
</templates>
```

**⚠️ XSS:** Usar `t-esc` (auto-escape) ao invés de `t-raw`!

---

## 🧪 TESTING

### Python Unit Test
```python
from odoo.tests.common import TransactionCase

class TestCRMLead(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Lead = self.env['crm.lead']
        self.partner = self.env['res.partner'].create({'name': 'Test'})

    def test_create_lead(self):
        lead = self.Lead.create({
            'name': 'Test Lead',
            'partner_id': self.partner.id
        })
        self.assertTrue(lead)
        self.assertEqual(lead.partner_id, self.partner)

    def test_constraint(self):
        with self.assertRaises(ValidationError):
            self.Lead.create({'name': False})
```

### JavaScript QUnit Test
```javascript
QUnit.test("Test component rendering", async function (assert) {
    const { Component, mount } = owl;

    class TestComponent extends Component {
        static template = xml`<div class="test">Hello</div>`;
    }

    const target = getFixture();
    await mount(TestComponent, target);

    assert.strictEqual(target.querySelector('.test').textContent, 'Hello');
});
```

### Tour (Integration Test)
```javascript
/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add('test_crm_lead_creation', {
    test: true,
    url: '/web',
    steps: () => [
        {
            trigger: '.o_app[data-menu-xmlid="crm.crm_menu_root"]',
            content: "Open CRM app",
        },
        {
            trigger: '.o_list_button_add',
            content: "Create new lead",
        },
        {
            trigger: 'input[name="name"]',
            content: "Enter lead name",
            run: 'text Test Lead',
        },
        {
            trigger: '.o_form_button_save',
            content: "Save lead",
        },
    ],
});
```

**Executar:** `odoo-bin --test-tags=test_crm_lead_creation`

---

## 🐳 DOCKER & KUBERNETES

### Docker Compose (Odoo + PostgreSQL)
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: odoo
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
    volumes:
      - pgdata:/var/lib/postgresql/data

  odoo:
    image: odoo:18.0
    depends_on:
      - postgres
    ports:
      - "8069:8069"
      - "8072:8072"
    environment:
      HOST: postgres
      USER: odoo
      PASSWORD: odoo
    volumes:
      - odoo-data:/var/lib/odoo
      - ./addons:/mnt/extra-addons

volumes:
  pgdata:
  odoo-data:
```

### Kubernetes (Helm Chart)
```bash
# Install Bitnami Odoo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install odoo bitnami/odoo \
  --set postgresql.enabled=true \
  --set persistence.enabled=true \
  --set persistence.size=50Gi \
  --set replicaCount=3  # High Availability!
```

### Kubernetes Features para Odoo
- ✅ **Self-healing:** Auto-restart de pods crash
- ✅ **Auto-scaling:** HPA baseado em CPU/memória
- ✅ **Load balancing:** Distribuição de requests
- ✅ **Rolling updates:** Zero-downtime deployment

---

## 🌐 NGINX

### Reverse Proxy para Odoo
```nginx
upstream odoo {
    server 127.0.0.1:8069;
}

upstream odoo_longpolling {
    server 127.0.0.1:8072;
}

server {
    listen 443 ssl http2;
    server_name odoo.example.com;

    ssl_certificate /etc/ssl/certs/odoo.crt;
    ssl_certificate_key /etc/ssl/private/odoo.key;

    # Gzip
    gzip on;
    gzip_types text/css text/javascript application/javascript;

    # Proxy buffers
    proxy_buffer_size 128k;
    proxy_buffers 4 256k;
    proxy_busy_buffers_size 256k;

    # Static files caching
    location ~* /web/static/ {
        proxy_pass http://odoo;
        proxy_cache_valid 200 60m;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Longpolling
    location /longpolling {
        proxy_pass http://odoo_longpolling;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Default
    location / {
        proxy_pass http://odoo;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Performance:**
- ✅ **SSL Termination:** Nginx faz SSL, Odoo não precisa
- ✅ **Static caching:** 60min cache = -80% requests
- ✅ **Gzip:** -70% bandwidth
- ✅ **Load balancer:** Múltiplos backends

---

## 🔐 SECURITY (OWASP)

### Built-in Protections

#### SQL Injection
```python
# ✅ ORM previne automaticamente
partners = self.env['res.partner'].search([('cpf', '=', cpf)])

# ✅ Raw SQL com %s
self.env.cr.execute("SELECT * FROM res_partner WHERE cpf = %s", (cpf,))

# ❌ NUNCA fazer
self.env.cr.execute(f"SELECT * FROM res_partner WHERE cpf = '{cpf}'")
```

#### XSS
```xml
<!-- ✅ Auto-escape -->
<span t-esc="user_input"/>

<!-- ❌ XSS vulnerability! -->
<span t-raw="user_input"/>

<!-- ✅ Se REALMENTE precisa HTML -->
<span t-raw="html_sanitize(user_input)"/>
```

#### CSRF
```python
# ✅ Built-in CSRF protection
# POST requests precisam de token automático
# Odoo web framework injeta token em forms
```

### Security Checklist
```
[ ] Todos .cr.execute() usam %s (não f-strings)
[ ] Todos t-raw têm html_sanitize()
[ ] Passwords com password="True"
[ ] sudo() documentado (por quê?)
[ ] Record rules configuradas
[ ] ir.model.access.csv completo
[ ] SSL habilitado (Nginx)
[ ] Firewall configurado (apenas portas necessárias)
[ ] Backup testado
[ ] Logs de segurança habilitados
```

---

## 🚀 CI/CD

### GitHub Actions (.github/workflows/odoo-ci.yml)
```yaml
name: Odoo CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres

    steps:
    - uses: actions/checkout@v3

    - name: Install Odoo
      run: |
        pip install odoo==15.0
        pip install -r requirements.txt

    - name: Run tests
      run: |
        odoo-bin -d test --test-enable --stop-after-init \
          --log-level=test --addons-path=./addons

    - name: Coverage
      run: |
        coverage run --source=addons odoo-bin -d test --test-enable
        coverage report
```

### GitLab CI (.gitlab-ci.yml)
```yaml
stages:
  - lint
  - test
  - deploy

lint:
  stage: lint
  script:
    - pylint --load-plugins=pylint_odoo addons/

test:
  stage: test
  services:
    - postgres:14
  script:
    - pip install odoo==15.0
    - odoo-bin -d test --test-enable --stop-after-init
  coverage: '/TOTAL.*\s+(\d+%)$/'

deploy_production:
  stage: deploy
  only:
    - main
  script:
    - scp -r addons/ user@server:/odoo/custom/
    - ssh user@server "systemctl restart odoo"
```

---

## 📊 MONITORING

### Prometheus Exporter (Odoo)
```python
# custom_addons/odoo_prometheus/controllers/metrics.py
from prometheus_client import Gauge, Counter, generate_latest

REQUEST_COUNT = Counter('odoo_requests_total', 'Total requests')
ACTIVE_USERS = Gauge('odoo_active_users', 'Active users')

@http.route('/metrics', auth='none', type='http', csrf=False)
def metrics(self):
    # Update metrics
    ACTIVE_USERS.set(len(request.env['res.users'].search([('active', '=', True)])))

    # Return Prometheus format
    return Response(generate_latest(), mimetype='text/plain')
```

### Grafana Dashboard (Query Examples)
```promql
# Requests por segundo
rate(odoo_requests_total[5m])

# Usuários ativos
odoo_active_users

# PostgreSQL queries lentas
rate(postgresql_slow_queries_total[5m])

# CPU usage
rate(process_cpu_seconds_total{job="odoo"}[5m])
```

### OpenTelemetry (2025 Standard)
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://collector:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Usage
tracer = trace.get_tracer(__name__)

def create_lead(self, vals):
    with tracer.start_as_current_span("crm.lead.create"):
        return super().create(vals)
```

---

## 🎯 PERFORMANCE CHECKLIST

### Database
```
[ ] random_page_cost = 1.1 (SSD)
[ ] shared_buffers = 25% RAM
[ ] Índices criados em foreign keys
[ ] Partial indexes para queries frequentes
[ ] Autovacuum configurado
[ ] ANALYZE executado regularmente
```

### Backend
```
[ ] search_fetch() ao invés de search() + read()
[ ] store=True em computed fields frequentes
[ ] N+1 queries eliminados (@api.depends correto)
[ ] sudo() usado com cuidado
[ ] Logs de slow queries habilitados (>1s)
```

### Frontend
```
[ ] useState para estado reativo
[ ] onWillStart para async loading
[ ] t-esc ao invés de t-raw
[ ] Lazy loading de componentes
[ ] Webpack bundle otimizado
```

### Infrastructure
```
[ ] Nginx reverse proxy
[ ] SSL/TLS habilitado
[ ] Gzip compression
[ ] Static files caching (60min+)
[ ] CDN para assets (opcional)
[ ] Load balancer (se >1000 users)
```

### Monitoring
```
[ ] Prometheus + Grafana
[ ] Log aggregation (ELK ou similar)
[ ] Uptime monitoring
[ ] Error tracking (Sentry ou similar)
[ ] Backup automático + teste
```

---

## 🚦 QUICK TROUBLESHOOTING

### Odoo Lento?
1. **Check PostgreSQL queries:**
   ```sql
   SELECT query, calls, mean_exec_time
   FROM pg_stat_statements
   ORDER BY mean_exec_time DESC LIMIT 10;
   ```
2. **Check N+1 queries:** Ver logs Odoo
3. **Check autovacuum:** `SELECT * FROM pg_stat_user_tables WHERE autovacuum_count = 0;`
4. **Check random_page_cost:** `SHOW random_page_cost;` (deve ser 1.1)

### Erro de Permissão?
1. **Check ir.model.access.csv:** Usuário tem acesso ao model?
2. **Check ir.rule:** Record rules estão filtrando?
3. **Check grupos:** `SELECT * FROM res_groups_users_rel WHERE uid = USER_ID;`

### Backup Falhou?
1. **Check espaço em disco:** `df -h`
2. **Check permissões:** `ls -la /backup/`
3. **Test restore:** Sempre testar restore!

---

## 📚 REFERÊNCIAS RÁPIDAS

### Comandos Essenciais
```bash
# PostgreSQL
psql -U odoo -d realcred
\dt                           # List tables
\di                           # List indexes
EXPLAIN ANALYZE SELECT ...;   # Query plan

# Odoo
odoo-bin -d DB -u MODULE --test-enable
odoo-bin -d DB --shell       # Python shell
odoo-bin -d DB --dev=all     # Dev mode

# Docker
docker-compose up -d
docker-compose logs -f odoo
docker-compose exec odoo bash

# Nginx
nginx -t                     # Test config
systemctl reload nginx
tail -f /var/log/nginx/access.log
```

### Logs Importantes
```bash
# Odoo
tail -f /var/log/odoo/odoo-server.log

# PostgreSQL
tail -f /var/log/postgresql/postgresql-15-main.log

# Nginx
tail -f /var/log/nginx/error.log
```

---

**Criado:** 2025-11-17
**Versão:** 1.0
**Uso:** Consulta diária durante desenvolvimento

**⚡ Tip:** Mantenha este arquivo aberto em aba separada!
