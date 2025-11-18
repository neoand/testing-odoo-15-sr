# 🏗️ Infrastructure & Operations - Mastery Guide

> **Odoo DevOps Complete** - Testing, Docker, Nginx, Security, CI/CD, Monitoring
>
> **Última atualização:** 2025-11-17
> **Aplicação:** Odoo 15-18, Production environments
> **Status:** ✅ Conhecimento Consolidado

---

## 📚 Índice

1. [Testing Framework](#testing-framework)
2. [Docker & Kubernetes](#docker--kubernetes)
3. [Nginx Reverse Proxy](#nginx-reverse-proxy)
4. [Security (OWASP)](#security-owasp)
5. [CI/CD Pipelines](#cicd-pipelines)
6. [Monitoring & APM](#monitoring--apm)

---

## 🧪 Testing Framework

### Testing Pyramid para Odoo

```
        /\
       /  \      E2E Tests (Tours)         - 10%
      /____\
     /      \    Integration Tests         - 30%
    /________\
   /          \  Unit Tests                - 60%
  /__________  \
```

### 1. Python Unit Tests

```python
# tests/test_crm_lead.py
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestCrmLead(TransactionCase):

    def setUp(self):
        super(TestCrmLead, self).setUp()
        self.Lead = self.env['crm.lead']
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@example.com'
        })

    def test_create_lead(self):
        """Test basic lead creation."""
        lead = self.Lead.create({
            'name': 'Test Lead',
            'partner_id': self.partner.id,
            'expected_revenue': 1000.0
        })
        self.assertTrue(lead)
        self.assertEqual(lead.name, 'Test Lead')
        self.assertEqual(lead.partner_id, self.partner)

    def test_lead_validation(self):
        """Test lead validation constraints."""
        with self.assertRaises(ValidationError):
            self.Lead.create({
                'name': False,  # Required field
                'expected_revenue': -100  # Invalid negative
            })

    def test_computed_field(self):
        """Test computed field calculation."""
        lead = self.Lead.create({
            'name': 'Test Lead',
            'probability': 50,
            'expected_revenue': 1000.0
        })
        # Test computed field
        self.assertEqual(lead.prorated_revenue, 500.0)

    def test_onchange_partner(self):
        """Test onchange method."""
        lead = self.Lead.new({
            'name': 'Test Lead',
            'partner_id': self.partner.id
        })
        lead._onchange_partner_id()
        self.assertEqual(lead.email_from, self.partner.email)

    def tearDown(self):
        # Cleanup if needed
        super(TestCrmLead, self).tearDown()
```

### Test Classes Disponíveis

```python
from odoo.tests.common import (
    TransactionCase,       # ← Mais usado - Rollback após cada test
    SingleTransactionCase, # Single transaction para todos tests
    SavepointCase,        # Savepoint após cada test
    HttpCase,             # Para testes HTTP/Controllers
    tagged              # Decorator para tags
)

# Usar tags para organizar tests
@tagged('post_install', '-at_install', 'crm')
class TestCrmAdvanced(TransactionCase):
    pass
```

### Running Tests

```bash
# Executar todos tests do módulo
odoo-bin -c odoo.conf -d test_db -u crm_custom --test-enable --stop-after-init

# Executar tests específicos
odoo-bin -c odoo.conf -d test_db -u crm_custom --test-enable --test-tags /crm

# Executar apenas post_install tests
odoo-bin -c odoo.conf -d test_db -u crm_custom --test-enable --test-tags post_install

# Com coverage
coverage run --source=addons/crm_custom odoo-bin ...
coverage report
coverage html  # HTML report em htmlcov/
```

### 2. JavaScript Tests (QUnit)

```javascript
// static/tests/my_component_tests.js
odoo.define('my_module.tests', function (require) {
    "use strict";

    const { createComponent } = require('web.test_utils');
    const MyComponent = require('my_module.MyComponent');

    QUnit.module('MyComponent');

    QUnit.test('component renders correctly', async function (assert) {
        assert.expect(2);

        const component = await createComponent(MyComponent, {
            props: { title: 'Test Title' }
        });

        assert.containsOnce(component, '.my-component');
        assert.strictEqual(
            component.el.querySelector('.title').textContent,
            'Test Title'
        );

        component.destroy();
    });

    QUnit.test('click event works', async function (assert) {
        assert.expect(1);

        const component = await createComponent(MyComponent);

        await testUtils.dom.click(component.el.querySelector('.btn-increment'));

        assert.strictEqual(component.state.count, 1);

        component.destroy();
    });
});
```

```xml
<!-- In manifest -->
'assets': {
    'web.qunit_suite_tests': [
        'my_module/static/tests/**/*',
    ],
}
```

### 3. Integration Tests (Tours)

```javascript
// static/tests/tours/crm_tour.js
odoo.define('crm_custom.tour', function (require) {
    "use strict";

    var tour = require('web_tour.tour');

    tour.register('crm_create_lead_tour', {
        test: true,
        url: '/web',
    }, [
        // Step 1: Open CRM menu
        {
            trigger: '.o_app[data-menu-xmlid="crm.crm_menu_root"]',
            content: 'Open CRM app',
            run: 'click',
        },
        // Step 2: Click Create
        {
            trigger: '.o_list_button_add',
            content: 'Create new lead',
            run: 'click',
        },
        // Step 3: Fill form
        {
            trigger: 'input[name="name"]',
            content: 'Enter lead name',
            run: 'text Test Lead from Tour',
        },
        {
            trigger: 'input[name="expected_revenue"]',
            content: 'Enter revenue',
            run: 'text 5000',
        },
        // Step 4: Save
        {
            trigger: '.o_form_button_save',
            content: 'Save lead',
            run: 'click',
        },
        // Step 5: Verify
        {
            trigger: '.o_form_readonly .o_field_widget[name="name"]',
            content: 'Verify lead created',
            run: function () {
                console.log('Lead created successfully!');
            },
        },
    ]);
});
```

```python
# tests/test_tours.py
from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestCrmTours(HttpCase):

    def test_crm_create_lead(self):
        """Test CRM lead creation tour."""
        self.start_tour('/web', 'crm_create_lead_tour', login='admin')
```

### Test Best Practices

**✅ DO:**
- Write tests for business logic
- Test validation constraints
- Test computed fields
- Test access rights
- Use descriptive test names
- Keep tests independent
- Mock external APIs

**❌ DON'T:**
- Test Odoo core functionality
- Write tests that depend on others
- Hardcode IDs (use xmlids)
- Skip tearDown cleanup
- Test UI only (prefer unit tests)

---

## 🐳 Docker & Kubernetes

### Docker Compose for Odoo

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:12
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - odoo-db-data:/var/lib/postgresql/data/pgdata
    networks:
      - odoo-network
    restart: always

  odoo:
    image: odoo:15.0
    depends_on:
      - db
    ports:
      - "8069:8069"
      - "8072:8072"  # Longpolling
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    volumes:
      - ./addons:/mnt/extra-addons
      - odoo-data:/var/lib/odoo
      - ./etc:/etc/odoo
    networks:
      - odoo-network
    restart: always
    command: --dev=all  # Development mode

  nginx:
    image: nginx:alpine
    depends_on:
      - odoo
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - odoo-network
    restart: always

volumes:
  odoo-db-data:
  odoo-data:

networks:
  odoo-network:
    driver: bridge
```

### Custom Dockerfile

```dockerfile
# Dockerfile
FROM odoo:15.0

USER root

# Install additional Python packages
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# Copy custom addons
COPY ./addons /mnt/extra-addons

# Copy configuration
COPY ./etc/odoo.conf /etc/odoo/

# Set permissions
RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo

EXPOSE 8069 8072

CMD ["odoo"]
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: odoo
  labels:
    app: odoo
spec:
  replicas: 3  # High availability
  selector:
    matchLabels:
      app: odoo
  template:
    metadata:
      labels:
        app: odoo
    spec:
      containers:
      - name: odoo
        image: odoo:15.0
        ports:
        - containerPort: 8069
        - containerPort: 8072
        env:
        - name: HOST
          value: postgres-service
        - name: USER
          valueFrom:
            secretKeyRef:
              name: odoo-secrets
              key: db-user
        - name: PASSWORD
          valueFrom:
            secretKeyRef:
              name: odoo-secrets
              key: db-password
        volumeMounts:
        - name: odoo-data
          mountPath: /var/lib/odoo
        - name: addons
          mountPath: /mnt/extra-addons
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /web/health
            port: 8069
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /web/health
            port: 8069
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: odoo-data
        persistentVolumeClaim:
          claimName: odoo-pvc
      - name: addons
        persistentVolumeClaim:
          claimName: addons-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: odoo-service
spec:
  selector:
    app: odoo
  ports:
  - name: http
    port: 80
    targetPort: 8069
  - name: longpolling
    port: 8072
    targetPort: 8072
  type: LoadBalancer
```

### Persistent Volumes

```yaml
# k8s/pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: odoo-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: fast-ssd
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: fast-ssd
```

### Docker Best Practices

**✅ DO:**
- Use official Odoo images as base
- Multi-stage builds for smaller images
- `.dockerignore` to exclude unnecessary files
- Health checks for containers
- Resource limits (CPU/memory)
- Secrets management (not in env vars)
- Persistent volumes for data
- Regular security scans

**❌ DON'T:**
- Run as root user
- Store credentials in Dockerfile
- Use `latest` tag (pin versions)
- Install unnecessary packages
- Ignore log aggregation

---

## 🌐 Nginx Reverse Proxy

### Nginx Configuration for Odoo

```nginx
# /etc/nginx/sites-available/odoo.conf
upstream odoo {
    server 127.0.0.1:8069;
}

upstream odoochat {
    server 127.0.0.1:8072;
}

# Redirect HTTP → HTTPS
server {
    listen 80;
    server_name odoo.example.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name odoo.example.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/odoo.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/odoo.example.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;

    # HSTS (Strict Transport Security)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Logs
    access_log /var/log/nginx/odoo.access.log;
    error_log /var/log/nginx/odoo.error.log;

    # Proxy Settings
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    # File Upload Limit
    client_max_body_size 100M;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    # Static Files Caching
    location ~* /web/static/ {
        proxy_cache_valid 200 60m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
    }

    # Longpolling (Chat/Notifications)
    location /longpolling {
        proxy_pass http://odoochat;
    }

    # Main Proxy
    location / {
        proxy_redirect off;
        proxy_pass http://odoo;
    }

    # Certbot Challenge
    location ~ /.well-known/acme-challenge {
        allow all;
        root /var/www/certbot;
    }
}
```

### Let's Encrypt SSL (Certbot)

```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d odoo.example.com

# Auto-renewal (crontab)
sudo crontab -e
# Add:
0 3 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

### Nginx Performance Tuning

```nginx
# /etc/nginx/nginx.conf
user www-data;
worker_processes auto;  # Auto-detect CPU cores
pid /run/nginx.pid;

events {
    worker_connections 4096;  # Increased from default 1024
    use epoll;  # Efficient on Linux
    multi_accept on;
}

http {
    ##
    # Basic Settings
    ##
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;  # Hide Nginx version

    ##
    # Buffer Settings
    ##
    client_body_buffer_size 128k;
    client_max_body_size 100M;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 16k;
    output_buffers 1 32k;
    postpone_output 1460;

    ##
    # Timeouts
    ##
    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;

    ##
    # Logging
    ##
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    ##
    # Gzip Settings
    ##
    gzip on;
    gzip_disable "msie6";
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;
    gzip_min_length 256;
    gzip_types
        application/atom+xml
        application/javascript
        application/json
        application/ld+json
        application/manifest+json
        application/rss+xml
        application/vnd.geo+json
        application/vnd.ms-fontobject
        application/x-font-ttf
        application/x-web-app-manifest+json
        application/xhtml+xml
        application/xml
        font/opentype
        image/bmp
        image/svg+xml
        image/x-icon
        text/cache-manifest
        text/css
        text/plain
        text/vcard
        text/vnd.rim.location.xloc
        text/vtt
        text/x-component
        text/x-cross-domain-policy;

    ##
    # Virtual Host Configs
    ##
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

---

## 🔒 Security (OWASP)

### OWASP Top 10 para Odoo

#### 1. SQL Injection Protection

```python
# ❌ VULNERABLE: String formatting
query = f"SELECT * FROM res_partner WHERE name = '{user_input}'"
self.env.cr.execute(query)  # SQL INJECTION!

# ✅ SAFE: Parameterized queries
query = "SELECT * FROM res_partner WHERE name = %s"
self.env.cr.execute(query, (user_input,))  # Safe!

# ✅ BEST: Use ORM
partners = self.env['res.partner'].search([('name', '=', user_input)])
```

#### 2. XSS (Cross-Site Scripting) Protection

```xml
<!-- ❌ VULNERABLE: t-raw with user input -->
<div t-raw="partner.description"/>  <!-- XSS if description = "<script>alert('XSS')</script>" -->

<!-- ✅ SAFE: t-esc (escapes HTML) -->
<div t-esc="partner.description"/>  <!-- Renders as text, not HTML -->

<!-- ✅ SAFE: Sanitize HTML in Python -->
<div t-raw="partner.sanitized_description"/>
```

```python
from odoo import tools

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sanitized_description = fields.Html(
        compute='_compute_sanitized_description'
    )

    @api.depends('description')
    def _compute_sanitized_description(self):
        for partner in self:
            partner.sanitized_description = tools.html_sanitize(
                partner.description,
                strip_classes=True,
                strip_style=True
            )
```

#### 3. CSRF Protection

```python
# Odoo tem proteção CSRF built-in para rotas web
from odoo import http

class MyController(http.Controller):

    @http.route('/my/route', type='http', auth='user', csrf=True)
    def my_route(self, **kwargs):
        # csrf=True (default) → CSRF token validado automaticamente
        return "Safe!"

    @http.route('/public/api', type='json', auth='none', csrf=False)
    def public_api(self, **kwargs):
        # csrf=False → Use APENAS para APIs públicas sem autenticação
        return {"status": "ok"}
```

#### 4. Authentication & Authorization

```python
# Access Rights (ir.model.access.csv)
# id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_crm_lead_user,crm.lead.user,model_crm_lead,sales_team.group_sale_salesman,1,1,1,0

# Record Rules
<record id="crm_lead_rule_own" model="ir.rule">
    <field name="name">Own Leads Only</field>
    <field name="model_id" ref="crm.model_crm_lead"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
</record>

# Field-level security
<field name="salary" groups="hr.group_hr_manager"/>
```

#### 5. Password Security

```python
from odoo import models, fields
from passlib.context import CryptContext

# Odoo usa passlib para hash de senhas
pwd_context = CryptContext(schemes=['pbkdf2_sha512'])

class ResUsers(models.Model):
    _inherit = 'res.users'

    # NUNCA armazenar senha em plain text
    # Odoo faz hash automaticamente
    password = fields.Char(string='Password', invisible=True, copy=False)

    @api.model
    def create(self, vals):
        # Password é hasheado automaticamente pelo Odoo
        user = super(ResUsers, self).create(vals)
        return user
```

#### 6. Sensitive Data Exposure

```python
# ❌ BAD: Expor dados sensíveis em logs
_logger.info(f"User password: {password}")  # NUNCA!
_logger.info(f"Credit card: {card_number}")  # NUNCA!

# ✅ GOOD: Log apenas informações não-sensíveis
_logger.info(f"User login: {username}")
_logger.info(f"Payment method: {payment_type}")

# ❌ BAD: Retornar senha em API
@http.route('/api/user', type='json', auth='user')
def get_user(self):
    user = request.env.user
    return {
        'name': user.name,
        'password': user.password  # NUNCA!
    }

# ✅ GOOD: Excluir campos sensíveis
@http.route('/api/user', type='json', auth='user')
def get_user(self):
    user = request.env.user
    return {
        'name': user.name,
        'email': user.email
        # password excluded!
    }
```

#### 7. Security Headers

Ver Nginx configuration acima com headers:
- `X-Frame-Options: SAMEORIGIN` (previne clickjacking)
- `X-Content-Type-Options: nosniff` (previne MIME sniffing)
- `X-XSS-Protection: 1; mode=block` (XSS filter do browser)
- `Strict-Transport-Security` (força HTTPS)

#### 8. File Upload Validation

```python
from odoo import models, fields, api, exceptions
import magic  # python-magic library

class DocumentUpload(models.Model):
    _name = 'document.upload'

    file = fields.Binary(string='File', required=True)
    filename = fields.Char(string='Filename')

    @api.constrains('file', 'filename')
    def _check_file_security(self):
        for record in self:
            # Validate file extension
            allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.doc', '.docx']
            ext = os.path.splitext(record.filename)[1].lower()
            if ext not in allowed_extensions:
                raise exceptions.ValidationError(
                    f"File type {ext} not allowed. Allowed: {', '.join(allowed_extensions)}"
                )

            # Validate MIME type (não confiar apenas na extensão!)
            file_data = base64.b64decode(record.file)
            mime = magic.from_buffer(file_data, mime=True)
            allowed_mimes = ['application/pdf', 'image/png', 'image/jpeg']
            if mime not in allowed_mimes:
                raise exceptions.ValidationError(
                    f"File content type {mime} not allowed"
                )

            # Validate file size (max 10MB)
            if len(file_data) > 10 * 1024 * 1024:
                raise exceptions.ValidationError("File size exceeds 10MB limit")
```

### Security Scanning Tools

```bash
# 1. OWASP ZAP (Zed Attack Proxy)
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://odoo.example.com

# 2. Safety (Python dependency check)
pip install safety
safety check

# 3. Bandit (Python security linter)
pip install bandit
bandit -r addons/my_module/

# 4. npm audit (JavaScript dependencies)
npm audit
npm audit fix
```

---

## 🚀 CI/CD Pipelines

### GitHub Actions

```yaml
# .github/workflows/odoo-ci.yml
name: Odoo CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:12
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: odoo
          POSTGRES_PASSWORD: odoo
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install Odoo dependencies
      run: |
        pip install -r requirements.txt
        pip install coverage flake8

    - name: Lint with flake8
      run: |
        flake8 addons/my_module/ --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 addons/my_module/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

    - name: Run Odoo tests
      run: |
        odoo-bin -c odoo.conf -d test_db -i my_module --test-enable --stop-after-init --log-level=test
      env:
        PGHOST: localhost
        PGPORT: 5432
        PGUSER: odoo
        PGPASSWORD: odoo

    - name: Coverage report
      run: |
        coverage run --source=addons/my_module odoo-bin -c odoo.conf -d test_db -u my_module --test-enable --stop-after-init
        coverage report
        coverage xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Build Docker image
      run: docker build -t odoo-custom:${{ github.sha }} .

    - name: Push to Docker Hub
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker tag odoo-custom:${{ github.sha }} mycompany/odoo:latest
        docker push mycompany/odoo:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - name: Deploy to production
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.PRODUCTION_HOST }}
        username: ${{ secrets.PRODUCTION_USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /opt/odoo
          docker-compose pull
          docker-compose up -d
          docker-compose exec odoo odoo-bin -d production -u my_module --stop-after-init
```

### GitLab CI/CD

```yaml
# .gitlab-ci.yml
stages:
  - lint
  - test
  - build
  - deploy

variables:
  POSTGRES_DB: test_db
  POSTGRES_USER: odoo
  POSTGRES_PASSWORD: odoo

lint:
  stage: lint
  image: python:3.9
  script:
    - pip install flake8
    - flake8 addons/my_module/ --max-line-length=127

test:
  stage: test
  image: odoo:15.0
  services:
    - postgres:12
  script:
    - pip install -r requirements.txt
    - odoo-bin -d test_db -i my_module --test-enable --stop-after-init
  coverage: '/TOTAL.*\s+(\d+%)$/'

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - main

deploy:production:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
  script:
    - ssh user@production-server 'cd /opt/odoo && docker-compose pull && docker-compose up -d'
  only:
    - main
  when: manual
```

---

## 📊 Monitoring & APM

### Prometheus + Grafana Setup

```yaml
# docker-compose-monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    networks:
      - monitoring
    depends_on:
      - prometheus

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    networks:
      - monitoring

  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    environment:
      DATA_SOURCE_NAME: "postgresql://odoo:odoo@db:5432/postgres?sslmode=disable"
    ports:
      - "9187:9187"
    networks:
      - monitoring

volumes:
  prometheus-data:
  grafana-data:

networks:
  monitoring:
```

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'odoo'
    static_configs:
      - targets: ['odoo:8069']
    metrics_path: /metrics  # Requires custom Odoo metrics endpoint
```

### Custom Odoo Metrics Exporter

```python
# addons/my_module/controllers/metrics.py
from odoo import http
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
import time

# Define metrics
request_count = Counter(
    'odoo_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'odoo_http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

class MetricsController(http.Controller):

    @http.route('/metrics', type='http', auth='none', csrf=False)
    def metrics(self):
        """Prometheus metrics endpoint."""
        return generate_latest(REGISTRY)

# Middleware to track requests
original_dispatch = http.Root.dispatch

def dispatch_with_metrics(self, endpoint, args):
    start_time = time.time()
    method = http.request.httprequest.method

    try:
        result = original_dispatch(self, endpoint, args)
        status = 200
        return result
    except Exception as e:
        status = 500
        raise
    finally:
        duration = time.time() - start_time
        request_count.labels(method=method, endpoint=endpoint.routing['route'], status=status).inc()
        request_duration.labels(method=method, endpoint=endpoint.routing['route']).observe(duration)

http.Root.dispatch = dispatch_with_metrics
```

### OpenTelemetry (2025 Standard)

```python
# addons/my_module/models/__init__.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Export to collector
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Use in code
class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_process_leads(self):
        with tracer.start_as_current_span("process_leads") as span:
            span.set_attribute("lead_count", len(self))

            for lead in self:
                with tracer.start_as_current_span("process_single_lead") as child_span:
                    child_span.set_attribute("lead_id", lead.id)
                    child_span.set_attribute("lead_name", lead.name)

                    # Business logic
                    self._process_lead(lead)
```

### Key Metrics to Monitor

**Odoo-Specific:**
- HTTP request rate and duration
- Database query count and duration
- Active users count
- Queue job lag (if using job queue)
- Module-specific metrics (SMS sent, leads created, etc.)

**Infrastructure:**
- CPU usage
- Memory usage
- Disk I/O
- Network I/O
- PostgreSQL connections
- PostgreSQL slow queries

**Business:**
- Revenue per day
- Orders created
- Conversion rate
- Average order value

---

## 📚 Recursos

### Documentação Oficial
- **Odoo Testing:** https://www.odoo.com/documentation/15.0/developer/reference/backend/testing.html
- **Docker:** https://docs.docker.com/
- **Kubernetes:** https://kubernetes.io/docs/
- **Nginx:** https://nginx.org/en/docs/
- **OWASP:** https://owasp.org/www-project-top-ten/
- **Prometheus:** https://prometheus.io/docs/
- **Grafana:** https://grafana.com/docs/

### Ferramentas
- **Certbot:** https://certbot.eff.org/
- **OWASP ZAP:** https://www.zaproxy.org/
- **GitHub Actions:** https://github.com/features/actions
- **GitLab CI:** https://docs.gitlab.com/ee/ci/
- **OpenTelemetry:** https://opentelemetry.io/

---

## 💡 Conclusão

**Infraestrutura completa para produção:**

**Testing:**
- ✅ Unit tests (60%) - Python TransactionCase
- ✅ Integration tests (30%) - Tours
- ✅ E2E tests (10%) - Full user flows

**Deployment:**
- ✅ Docker para desenvolvimento
- ✅ Kubernetes para produção em escala
- ✅ Nginx reverse proxy com SSL

**Security:**
- ✅ OWASP Top 10 protections
- ✅ SQL injection prevention (ORM + parameterization)
- ✅ XSS prevention (t-esc, html_sanitize)
- ✅ CSRF protection (built-in Odoo)

**CI/CD:**
- ✅ Automated testing on every commit
- ✅ Docker build and push
- ✅ Automated deployment
- ✅ Zero-downtime deployments

**Monitoring:**
- ✅ Prometheus metrics collection
- ✅ Grafana dashboards
- ✅ OpenTelemetry distributed tracing
- ✅ Real-time alerts

---

**Criado:** 2025-11-17
**Fontes:** 95+ artigos, docs oficiais, melhores práticas 2025
**Status:** ✅ Conhecimento Consolidado
**Aplicação:** Imediata - produção Odoo 15+
