# 🎨 Padrões e Boas Práticas Descobertas

> **Propósito:** Documentar padrões de código, soluções elegantes e boas práticas específicas deste projeto.

---

## 🏗️ Padrões Arquiteturais

### 1. Estrutura de Módulo Odoo

```
module_name/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── model_name.py
├── views/
│   ├── menu.xml
│   └── model_views.xml
├── security/
│   ├── security_groups.xml
│   ├── ir.model.access.csv
│   └── record_rules.xml
├── data/
│   └── data.xml
├── wizard/
│   ├── __init__.py
│   └── wizard_name.py
├── static/
│   ├── src/
│   │   ├── js/
│   │   ├── scss/
│   │   └── xml/
│   └── description/
│       ├── icon.png
│       └── index.html
└── tests/
    ├── __init__.py
    └── test_model.py
```

**Por que assim:**
- Organização clara
- Fácil navegação
- Padrão Odoo oficial
- Compatível com OCA

---

## 💻 Padrões de Código Python

### 1. Model Base Template

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class ModelName(models.Model):
    """Docstring descrevendo o modelo."""

    _name = 'module.model'
    _description = 'Descrição do Modelo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # ====== CAMPOS ======

    name = fields.Char(
        string='Nome',
        required=True,
        tracking=True,
        index=True,
        help='Nome principal'
    )

    active = fields.Boolean(
        string='Ativo',
        default=True
    )

    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('done', 'Concluído'),
    ], string='Status', default='draft', tracking=True)

    # ====== CONSTRAINTS ======

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Nome deve ser único!'),
    ]

    @api.constrains('field')
    def _check_field(self):
        for record in self:
            if not record.field:
                raise ValidationError(_('Validação falhou!'))

    # ====== COMPUTE ======

    @api.depends('field')
    def _compute_something(self):
        for record in self:
            record.computed_field = record.field * 2

    # ====== ONCHANGE ======

    @api.onchange('field')
    def _onchange_field(self):
        if self.field:
            self.other_field = self.field

    # ====== CRUD OVERRIDES ======

    @api.model
    def create(self, vals):
        # Lógica antes
        record = super(ModelName, self).create(vals)
        # Lógica depois
        return record

    def write(self, vals):
        # Lógica antes
        result = super(ModelName, self).write(vals)
        # Lógica depois
        return result

    def unlink(self):
        # Validações
        if self.filtered(lambda r: r.state != 'draft'):
            raise UserError(_('Não pode deletar registro confirmado!'))
        return super(ModelName, self).unlink()

    # ====== ACTIONS ======

    def action_confirm(self):
        """Confirma o registro."""
        self.ensure_one()
        self.write({'state': 'done'})
        self.message_post(body=_('Registro confirmado'))
        return True

    # ====== HELPERS ======

    def _helper_method(self):
        """Método auxiliar privado."""
        self.ensure_one()
        # Lógica
        pass
```

**Padrão:**
- Seções claramente demarcadas
- Ordem lógica (campos → constraints → compute → actions)
- Docstrings em português
- Logging adequado
- Type hints quando possível

---

### 2. Tratamento de Exceptions

```python
def send_sms(self):
    """Envia SMS com tratamento robusto de erros."""
    try:
        response = requests.post(
            url,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        _logger.error('Timeout sending SMS to %s', self.phone)
        raise UserError(_(
            'O serviço de SMS não respondeu a tempo. '
            'Por favor, tente novamente em alguns minutos.'
        ))

    except requests.exceptions.HTTPError as e:
        _logger.error('HTTP error sending SMS: %s', e)
        if e.response.status_code == 401:
            raise UserError(_('Credenciais inválidas. Contate o administrador.'))
        elif e.response.status_code == 429:
            raise UserError(_('Limite de SMS excedido. Aguarde antes de tentar novamente.'))
        else:
            raise UserError(_('Erro ao enviar SMS: %s') % str(e))

    except requests.exceptions.RequestException as e:
        _logger.exception('Unexpected error sending SMS')
        raise UserError(_('Erro inesperado: %s') % str(e))
```

**Padrão:**
- Exceptions específicas primeiro
- Logging adequado por severidade
- Mensagens amigáveis para usuário
- Informação técnica nos logs

---

### 3. Otimização de Performance

```python
# ❌ RUIM - N+1 queries
def bad_method(self):
    for record in self:
        partner_name = record.partner_id.name  # Query a cada iteração!
        print(partner_name)

# ✅ BOM - Single query
def good_method(self):
    # Opção 1: depends correto
    @api.depends('partner_id.name')
    def _compute_partner_name(self):
        for record in self:
            record.partner_name = record.partner_id.name  # Cached!

    # Opção 2: mapped
    partners = self.mapped('partner_id')  # Uma query só
    for partner in partners:
        print(partner.name)

    # Opção 3: read
    data = self.read(['partner_id'])  # Query otimizada
```

**Padrão:**
- Sempre usar `@api.depends` com campos relacionados completos
- Preferir `mapped()` a loops
- Usar `read()` quando só precisa de alguns campos
- Profile com pg_stat_statements

---

## 🎯 Padrões de Views XML

### 1. Form View Completa

```xml
<record id="view_model_form" model="ir.ui.view">
    <field name="name">model.model.form</field>
    <field name="model">module.model</field>
    <field name="arch" type="xml">
        <form string="Título">
            <!-- Header com ações e statusbar -->
            <header>
                <button name="action_confirm"
                        string="Confirmar"
                        type="object"
                        class="oe_highlight"
                        attrs="{'invisible': [('state', '!=', 'draft')]}"/>
                <field name="state" widget="statusbar"/>
            </header>

            <sheet>
                <!-- Button box -->
                <div class="oe_button_box" name="button_box">
                    <button name="toggle_active" type="object"
                            class="oe_stat_button" icon="fa-archive">
                        <field name="active" widget="boolean_button"/>
                    </button>
                </div>

                <!-- Título -->
                <div class="oe_title">
                    <h1><field name="name" placeholder="Nome..."/></h1>
                </div>

                <!-- Grupos -->
                <group>
                    <group name="left">
                        <field name="field1"/>
                        <field name="field2"/>
                    </group>
                    <group name="right">
                        <field name="field3"/>
                        <field name="field4"/>
                    </group>
                </group>

                <!-- Notebook -->
                <notebook>
                    <page string="Info" name="info">
                        <field name="description"/>
                    </page>
                </notebook>
            </sheet>

            <!-- Chatter -->
            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="activity_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

**Padrão:**
- Estrutura consistente: header → sheet → chatter
- Names em elementos para facilitar herança
- Button box para ações rápidas
- Groups de 2 colunas
- Notebook para conteúdo extenso

---

### 2. Tree View com Decorations

```xml
<record id="view_model_tree" model="ir.ui.view">
    <field name="name">model.model.tree</field>
    <field name="model">module.model</field>
    <field name="arch" type="xml">
        <tree string="Lista"
              decoration-muted="active == False"
              decoration-success="state == 'done'"
              decoration-danger="state == 'cancel'"
              decoration-info="state == 'draft'">
            <field name="name"/>
            <field name="partner_id"/>
            <field name="state"/>
            <field name="active" invisible="1"/>
        </tree>
    </field>
</record>
```

**Padrão:**
- Decorations para feedback visual
- Campos importantes visíveis
- Campos auxiliares com invisible="1"
- String descritivo

---

## 🔒 Padrões de Security

### 0. Record Rules - Padrão Correto ⭐ CRÍTICO

**Erro Comum que Bloqueia Tudo:**
```xml
<!-- ❌ ERRADO - Bloqueia TUDO -->
<record id="rule_name" model="ir.rule">
    <field name="name">Rule Name</field>
    <field name="model_id" ref="model_name"/>
    <field name="perm_read" eval="False"/>  <!-- BLOQUEIA - domain nunca é consultado! -->
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

**Padrão Correto:**
```xml
<!-- ✅ CORRETO - Permite + Filtra com domain -->
<record id="rule_name" model="ir.rule">
    <field name="name">Rule Description - Group Name Access</field>
    <field name="model_id" ref="model_name"/>
    <field name="perm_read" eval="True"/>      <!-- PERMITE leitura -->
    <field name="perm_write" eval="False"/>    <!-- Bloqueia escrita -->
    <field name="perm_create" eval="False"/>   <!-- Bloqueia criação -->
    <field name="perm_unlink" eval="False"/>   <!-- Bloqueia deleção -->
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

**Regra de Ouro:**
- Record rules SEMPRE têm `perm_read=True`
- O `domain_force` é que filtra quem vê o quê
- NUNCA use `perm_read=False` em rules com domain_force
- Bloqueie escrita/criação/deleção conforme necessário

**Por quê?**
```
Fluxo de Segurança Odoo:
1. Verifica access rights (ir.model.access.csv) → perm_read=1?
2. Verifica record rules (ir.rule)
   - Se perm_read=False → ❌ BLOQUEIA (domain não é consultado!)
   - Se perm_read=True → Aplica domain_force para filtrar (SQL WHERE)
   - Domain controla quem vê cada registro
```

**Exemplo Real:**
```xml
<!-- Domain: usuário vê APENAS seus próprios leads -->
<field name="domain_force">[('user_id', '=', user.id)]</field>

<!-- Sem perm_read=True, o domain nunca é executado! -->
<!-- Resultado: nada é visível para ninguém -->
```

---

### 1. Security Completo

```
security/
├── security_groups.xml    # Grupos
├── ir.model.access.csv    # Access rights
└── record_rules.xml       # Record rules
```

**security_groups.xml:**
```xml
<record id="group_custom_user" model="res.groups">
    <field name="name">Custom User</field>
    <field name="category_id" ref="base.module_category_custom"/>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
</record>
```

**ir.model.access.csv:**
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,model.user,model_module_model,base.group_user,1,1,1,0
access_model_manager,model.manager,model_module_model,base.group_system,1,1,1,1
```

**record_rules.xml (CORRETO):**
```xml
<record id="model_rule_own" model="ir.rule">
    <field name="name">Ver apenas próprios registros</field>
    <field name="model_id" ref="model_module_model"/>
    <field name="perm_read" eval="True"/>      <!-- ✅ Permite -->
    <field name="perm_write" eval="False"/>    <!-- Bloqueia -->
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

---

## 🧪 Padrões de Testes

```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestModel(TransactionCase):

    def setUp(self):
        super(TestModel, self).setUp()
        self.Model = self.env['module.model']
        self.record = self.Model.create({'name': 'Test'})

    def test_create(self):
        """Testa criação de registro."""
        record = self.Model.create({'name': 'Test 2'})
        self.assertTrue(record)
        self.assertEqual(record.name, 'Test 2')

    def test_constraint(self):
        """Testa constraint de validação."""
        with self.assertRaises(ValidationError):
            self.Model.create({'name': False})

    def test_compute(self):
        """Testa campo computado."""
        self.record.field = 10
        self.assertEqual(self.record.computed_field, 20)
```

---

## 📊 Padrões SQL

### Queries Complexas

```python
def _get_statistics(self):
    """Usa SQL direto quando ORM é insuficiente."""
    self.env.cr.execute("""
        SELECT
            user_id,
            COUNT(*) as count,
            SUM(amount) as total
        FROM crm_lead
        WHERE state = 'done'
        GROUP BY user_id
        ORDER BY total DESC
    """)
    return self.env.cr.dictfetchall()
```

**Quando usar SQL direto:**
- Agregações complexas
- Performance crítica
- Reports
- Bulk operations

**Cuidados:**
- SEMPRE sanitize inputs com `%s`
- NUNCA use string formatting
- Commit manual se necessário
- Documentar query

---

## 🎯 Anti-Patterns (Evitar!)

### ❌ Não Fazer

```python
# 1. String formatting em queries (SQL INJECTION!)
self.env.cr.execute(f"SELECT * FROM table WHERE id = {user_input}")

# 2. Commit desnecessário
self.env.cr.commit()  # Odoo gerencia isso!

# 3. Browse sem necessidade
for id in ids:
    record = self.browse(id)  # Lento!

# 4. Search sem limit
all_records = self.env['huge.model'].search([])  # OOM!

# 5. Compute sem store para campos muito usados
@api.depends('partner_id')
def _compute_partner_name(self):  # Calculado sempre!
    ...
```

### ✅ Fazer

```python
# 1. Use %s para parâmetros
self.env.cr.execute("SELECT * FROM table WHERE id = %s", (user_input,))

# 2. Deixe Odoo gerenciar transactions

# 3. Browse de uma vez
records = self.browse(ids)

# 4. Use limit
records = self.env['huge.model'].search([], limit=1000)

# 5. Store quando fizer sentido
@api.depends('partner_id.name')
def _compute_partner_name(self):
    ...
partner_name = fields.Char(compute='_compute_partner_name', store=True)
```

---

## 🌐 Padrões de Troubleshooting de Rede

### 1. Serviço Não Acessível Externamente - Checklist Sistemático

**Problema:** Serviço (Odoo, Nginx, etc.) roda mas não aceita conexões externas

**Checklist em Ordem (camada por camada):**

```bash
# ====== CAMADA 1: Processo Rodando? ======
ps aux | grep PROCESSO | grep -v grep
# ✅ Se vazio: processo parado - iniciar
# ✅ Se mostra: processo rodando - ir para camada 2

# ====== CAMADA 2: Porta Escutando? ======
sudo ss -tlnp | grep PORTA
# ✅ Se vazio: processo não escuta nessa porta - verificar config
# ✅ Se mostra: porta escutando - ir para camada 3

# ====== CAMADA 3: Interface Correta? ======
sudo ss -tlnp | grep PORTA | grep -E '0.0.0.0|127.0.0.1'
# ✅ 0.0.0.0:PORTA → Aceita externo ✅
# ❌ 127.0.0.1:PORTA → Apenas localhost ❌
# Se 127.0.0.1 e precisa externo: mudar config (http_interface, etc)

# ====== CAMADA 4: Teste Interno ======
curl -I http://localhost:PORTA
# ✅ Se responde: serviço OK internamente - ir para camada 5
# ❌ Se falha: problema na aplicação - verificar logs

# ====== CAMADA 5: Firewall Local (iptables) ======
sudo iptables -L -n | grep PORTA
# Verificar se há regra DROP/REJECT bloqueando porta

# ====== CAMADA 6: Firewall Cloud (GCP/AWS/Azure) ======
# GCP:
gcloud compute firewall-rules list --filter="tcp:PORTA"
# ✅ Se vazio: sem regra - criar regra
# ✅ Se mostra: regra existe - verificar target-tags

# ====== CAMADA 7: Teste Externo ======
curl -I http://IP_EXTERNO:PORTA
# ✅ Se responde: TUDO OK! ✅
# ❌ Se falha: voltar camadas 5-6
```

**Pattern Geral:**
```
Processo → Porta → Interface → Teste Interno → Firewall Local → Firewall Cloud → Teste Externo
```

**Ferramentas Chave:**
- `ps aux` - verificar processo
- `ss -tlnp` / `netstat -tlnp` - verificar porta e interface
- `curl -I` - testar conectividade HTTP
- `iptables -L` - firewall local
- `gcloud compute firewall-rules` - firewall cloud (GCP)

---

### 2. Odoo http_interface - Quando Usar Cada Opção

**Configuração:** `/etc/odoo-server.conf` → `http_interface`

**Opção 1: http_interface = 127.0.0.1** (Apenas Localhost)
```
Odoo escuta: 127.0.0.1:8069
Aceita conexões de: APENAS localhost
Uso: Quando Nginx/Apache faz reverse proxy
```

**Fluxo:**
```
Internet → Nginx (443) → localhost:8069 (Odoo) ✅
Internet → 8069 (Odoo) ❌ Bloqueado
```

**Quando usar:**
- ✅ Produção com reverse proxy (Nginx/Apache)
- ✅ SSL/HTTPS via Nginx
- ✅ Load balancing
- ✅ Cache estático
- ✅ **Segurança:** Odoo não exposto diretamente

**Opção 2: http_interface = 0.0.0.0** (Todas Interfaces)
```
Odoo escuta: 0.0.0.0:8069
Aceita conexões de: localhost + rede externa
Uso: Acesso direto ou testing
```

**Fluxo:**
```
Internet → 8069 (Odoo) ✅ Direto
localhost → 8069 (Odoo) ✅ Também funciona
```

**Quando usar:**
- ✅ Ambiente de testing/development
- ✅ Prototipagem rápida
- ✅ Quando não há reverse proxy
- ⚠️ **Atenção:** Odoo exposto diretamente (usar firewall!)

**Opção 3: http_interface = IP_ESPECÍFICO** (Uma Interface)
```
Odoo escuta: 10.0.0.5:8069
Aceita conexões de: Apenas rede do IP específico
Uso: Casos avançados (multi-network)
```

**Decisão Rápida:**
```
Tem Nginx/Apache? → 127.0.0.1 (localhost)
Acesso direto? → 0.0.0.0 (todas interfaces)
Multi-network? → IP específico
```

**CRÍTICO:** Após mudar `http_interface`, SEMPRE:
```bash
sudo pkill -9 -f 'odoo-bin'  # Matar processos antigos
sudo -u odoo python3 ./odoo-bin -c /etc/odoo-server.conf &
sudo ss -tlnp | grep 8069  # Validar nova interface
```

---

### 3. GCP Firewall - Pattern de Criação

**Estrutura de Comando:**
```bash
gcloud compute firewall-rules create RULE_NAME \
  --project=PROJECT_ID \           # Projeto GCP
  --direction=INGRESS \            # Entrada (INGRESS) ou Saída (EGRESS)
  --priority=1000 \                # 0-65535 (menor = maior prioridade)
  --network=default \              # Rede (geralmente 'default')
  --action=ALLOW \                 # ALLOW ou DENY
  --rules=tcp:PORTA \              # tcp:80, udp:53, etc
  --source-ranges=0.0.0.0/0 \      # 0.0.0.0/0 = qualquer IP
  --target-tags=TAG \              # Tag da instância alvo
  --description="Description"
```

**Exemplo Real:**
```bash
gcloud compute firewall-rules create allow-odoo-8069 \
  --project=webserver-258516 \
  --direction=INGRESS \
  --priority=1000 \
  --network=default \
  --action=ALLOW \
  --rules=tcp:8069 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=http-server \
  --description="Allow Odoo direct access on port 8069"
```

**Validação:**
```bash
# 1. Verificar regra criada
gcloud compute firewall-rules list --filter="name=allow-odoo-8069"

# 2. Verificar se instância tem a tag
gcloud compute instances describe INSTANCE \
  --zone=ZONE \
  --format="value(tags.items)"
# Output deve conter: http-server
```

**Pattern Comum - Portas Web:**
```bash
# HTTP (80)
--rules=tcp:80 --target-tags=http-server

# HTTPS (443)
--rules=tcp:443 --target-tags=https-server

# Odoo direto (8069)
--rules=tcp:8069 --target-tags=http-server

# Odoo longpolling (8072)
--rules=tcp:8072 --target-tags=http-server

# PostgreSQL (5432) - CUIDADO: restringir source-ranges!
--rules=tcp:5432 --source-ranges=10.0.0.0/8

# SSH (22) - Geralmente já existe regra default
--rules=tcp:22
```

**Segurança - source-ranges:**
```bash
# ⚠️ PÚBLICO (todos IPs):
--source-ranges=0.0.0.0/0

# ✅ RESTRITO (apenas escritório):
--source-ranges=203.0.113.0/24

# ✅ MÚLTIPLOS RANGES:
--source-ranges=203.0.113.0/24,198.51.100.0/24

# ✅ REDE INTERNA:
--source-ranges=10.0.0.0/8
```

---

## 🛠️ Pattern Cheatsheet - Comandos Rápidos

### Odoo Troubleshooting One-Liner

```bash
# Diagnóstico completo de acessibilidade
echo "1. Processo:" && ps aux | grep odoo-bin | grep -v grep | wc -l && \
echo "2. Porta:" && sudo ss -tlnp | grep 8069 && \
echo "3. Config:" && sudo grep http_interface /etc/odoo-server.conf && \
echo "4. Teste:" && curl -I http://localhost:8069
```

### GCP Firewall One-Liner

```bash
# Verificar completo para uma porta
gcloud compute firewall-rules list --filter="tcp:8069" --format="table(name,allowed,targetTags)" && \
gcloud compute instances describe odoo-sr-tensting --zone=southamerica-east1-b --format="value(tags.items)"
```

---

## 🧠 RAG (Retrieval-Augmented Generation) Patterns

### 1. MCP Server para Auto-Invocação

**Pattern:** RAG como MCP tool que Claude invoca automaticamente

```python
# Estrutura MCP Server
#!/usr/bin/env python3
import sys
import json

def handle_request(request):
    """Processa requisição MCP"""
    method = request.get('method', '')
    params = request.get('params', {})

    if method == 'search_knowledge':
        return search_knowledge(params)
    # Outros métodos...

if __name__ == "__main__":
    # Loop MCP stdin/stdout
    for line in sys.stdin:
        request = json.loads(line.strip())
        response = handle_request(request)
        print(json.dumps(response))
        sys.stdout.flush()
```

**Configuração (.mcp.json):**
```json
{
  "mcpServers": {
    "knowledge": {
      "type": "stdio",
      "command": "python3.11",
      "args": ["/absolute/path/to/mcp_server.py"],
      "env": {}
    }
  }
}
```

**Por que esse pattern:**
- ✅ Claude invoca automaticamente quando precisa de contexto
- ✅ Zero overhead - processo spawn sob demanda
- ✅ stdio protocol = simples e robusto
- ✅ Stateless - cada request independente

---

### 2. Session Memory com Embeddings

**Pattern:** Salvar resumos de sessões com embeddings para busca semântica

```python
def save_session(summary, tasks_completed, learnings):
    """
    Salva sessão atual com embedding para futuras buscas
    """
    # Criar texto completo
    full_content = f"""
    Summary: {summary}
    Tasks: {tasks}
    Learnings: {learnings}
    """

    # Gerar embedding
    embedding = model.encode(full_content).tolist()

    # Salvar em ChromaDB
    session_collection.add(
        ids=[session_id],
        embeddings=[embedding],
        documents=[full_content],
        metadatas=[{...}]
    )

    # Logging permanente (JSONL)
    with open(log_file, 'a') as f:
        f.write(json.dumps(session_data) + '\n')

def search_similar_sessions(query, n_results=5):
    """Busca sessões similares semanticamente"""
    query_embedding = model.encode(query).tolist()
    results = session_collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results
```

**Por que esse pattern:**
- ✅ Continuidade entre sessões
- ✅ Semantic search > keyword search
- ✅ JSONL backup = durável
- ✅ Injeta contexto automaticamente

---

### 3. Path Calculation em Scripts Python

**Pattern:** Calcular PROJECT_ROOT a partir de localização do script

```python
from pathlib import Path

# Script location: PROJECT_ROOT/.claude/scripts/python/script.py
script_path = Path(__file__).resolve()

# Calcular PROJECT_ROOT
# script.py → python/ → scripts/ → .claude/ → PROJECT_ROOT
PROJECT_ROOT = script_path.parent.parent.parent.parent

# Construir paths relativos
VECTORDB_PATH = str(PROJECT_ROOT / ".claude" / "vectordb")
MEMORY_PATH = str(PROJECT_ROOT / ".claude" / "memory")

# SEMPRE documentar estrutura esperada no comentário!
```

**Por que esse pattern:**
- ✅ Portable - funciona em qualquer máquina
- ✅ Não depende de $PWD
- ✅ Robusto contra mudanças de working directory
- ⚠️ Requires estrutura de diretórios consistente

**Erros comuns:**
```python
# ❌ ERRADO - 3x parent (falta 1)
PROJECT_ROOT = script_path.parent.parent.parent

# ❌ ERRADO - hardcoded path
PROJECT_ROOT = "/Users/user/project"

# ❌ ERRADO - relative path
PROJECT_ROOT = "../../../"

# ✅ CORRETO
PROJECT_ROOT = script_path.parent.parent.parent.parent
```

---

### 4. Query Caching com LRU + TTL

**Pattern:** Cache embeddings de queries com expiração

```python
class QueryCache:
    def __init__(self, max_size=1000, ttl_hours=24):
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
        self.cache = {}  # {hash: (embedding, timestamp)}

    def get(self, query):
        query_hash = hashlib.md5(query.encode()).hexdigest()[:12]
        if query_hash in self.cache:
            embedding, timestamp = self.cache[query_hash]
            if datetime.now() - timestamp < self.ttl:
                return embedding  # Cache HIT!
        return None

    def put(self, query, embedding):
        query_hash = hashlib.md5(query.encode()).hexdigest()[:12]

        # LRU eviction
        if len(self.cache) >= self.max_size:
            oldest = min(self.cache.items(), key=lambda x: x[1][1])
            del self.cache[oldest[0]]

        self.cache[query_hash] = (embedding, datetime.now())
```

**Por que esse pattern:**
- ✅ 10-100x speedup para queries repetidas
- ✅ LRU = memory bounded
- ✅ TTL = freshness garantido
- ✅ Hash de query = chave consistente

---

### 5. Batch Processing com Pré-Sorting

**Pattern:** Ordenar textos por comprimento antes de batching

```python
def index_in_batches(chunks, batch_size=256):
    """Processa chunks em batches otimizados"""
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]

        # Pré-sort por comprimento (CRÍTICO!)
        batch_sorted = sorted(batch, key=lambda x: len(x['content']))

        # Encode batch
        texts = [chunk['content'] for chunk in batch_sorted]
        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            convert_to_tensor=True,
            precision='float16'  # Mixed-precision
        )

        # Add to ChromaDB...
```

**Por que pré-sorting:**
Sentence transformers fazem padding para o maior texto do batch.

```
# ❌ SEM pre-sorting:
Batch: [50 tokens, 500 tokens, 100 tokens]
Padding: Todos para 500 tokens → 90% desperdício!

# ✅ COM pre-sorting:
Batch: [50, 100, 120, 150, ...] tokens
Padding: Todos para 150 tokens → 10% desperdício!
```

**Ganho:** 15-30% redução de cálculos desperdiçados

---

### 6. HNSW Parameters Tuning

**Pattern:** Configurar HNSW baseado em caso de uso

```python
# ⚠️ HNSW params NÃO PODEM SER ALTERADOS após criação!
# Sempre definir na criação da collection

collection = client.get_or_create_collection(
    name="project_knowledge",
    metadata={
        # Base de conhecimento média (~100-500 docs)
        # Queries frequentes (alta taxa de busca)
        # Precisão > velocidade extrema

        "hnsw:space": "cosine",
        "hnsw:M": 32,                    # ↑ = melhor recall, mais memória
        "hnsw:construction_ef": 200,      # ↑ = melhor qualidade, indexação lenta
        "hnsw:search_ef": 100,            # ↑ = melhor recall, busca lenta
        "hnsw:num_threads": 8,
        "hnsw:batch_size": 1000,
        "hnsw:sync_threshold": 500
    }
)
```

**Guia de valores:**

| Caso de Uso | M | construction_ef | search_ef |
|-------------|---|-----------------|-----------|
| Small DB, velocidade crítica | 16 | 100 | 10 |
| Medium DB, balanced | 32 | 200 | 100 |
| Large DB, precisão crítica | 64 | 400 | 200 |

**Trade-offs:**
- ↑ M = Melhor recall, mais memória, busca levemente mais lenta
- ↑ construction_ef = Melhor qualidade de grafo, indexação MUITO mais lenta
- ↑ search_ef = Melhor recall, busca mais lenta

---

## 🎯 Quick Reference RAG

**Otimizações CRÍTICAS (300-500% ganho):**
1. Mixed-Precision (FP16) → 2x velocidade
2. Batch Processing → 3-5x velocidade
3. Pré-Sorting → 15-30% economia
4. Query Caching → 10-100x (cache hits)
5. HNSW Tuning → 20-40% busca + 30% precisão
6. Keep Data on GPU → 30-50% latência
7. Reranking Batch → 50-100% reranking
8. Monitoring → Visibilidade total

**Documentação Completa:**
- `.claude/memory/learnings/rag-optimizations-2025.md` (27 otimizações)
- `.claude/memory/decisions/ADR-009-ADVANCED-RAG.md` (decisão arquitetural)

---

---

## 🦎 Padrões de Integração com Plataformas Externas

### Pang olin Platform Integration Pattern

**Quando usar:**
- Integrar com API externa
- Documentar plataforma nova
- Tornar-se especialista em tecnologia

**Pattern:**
```bash
1. Explorar documentação local (se houver)
   - Ler todos .md files do projeto
   - Identificar arquitetura e stack

2. Acessar API e testar endpoints
   - WebFetch para homepage
   - Web Search para GitHub e docs oficiais

3. Documentar completamente
   - Criar guia em .claude/memory/learnings/
   - Mínimo 100KB de conteúdo estruturado
   - Incluir: arquitetura, API, comandos, troubleshooting

4. Atualizar RAG
   - Reindexar knowledge base
   - Testar busca semântica

5. Criar ADR
   - Documentar decisão de integração
   - Registrar credenciais e acessos

6. Persistir
   - Commit com mensagem detalhada
   - Push para GitHub
```

**Exemplo (Pangolin):**
```
✅ Documentação local: /Users/andersongoliveira/neo_pangolin/ (explorado)
✅ API access: https://pangolin.keyanders.me (testado)
✅ Web research: GitHub fosrl/pangolin (pesquisado)
✅ Guia criado: 125KB, 3500 linhas
✅ RAG atualizado: 15 chunks Pangolin
✅ ADR-010: Pangolin Integration (criado)
✅ Resultado: Claude = especialista Pangolin
```

**Benefícios:**
- ✅ Conhecimento permanente (nunca esquece)
- ✅ Capacitação imediata (pode operar/desenvolver)
- ✅ Replicável para outras plataformas
- ✅ RAG-powered (busca semântica)

---

**Última atualização:** 2025-11-18
**Contribuir:** Adicione novos padrões conforme descobertos!
