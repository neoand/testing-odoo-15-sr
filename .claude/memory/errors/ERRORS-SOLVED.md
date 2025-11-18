# 🐛 Histórico de Erros Resolvidos

> **Propósito:** Documentar TODOS os erros encontrados e suas soluções para nunca cometer o mesmo erro duas vezes.

---

## Como Usar Este Arquivo

**Quando um erro for resolvido:**
1. Adicione entrada no topo (mais recente primeiro)
2. Use template abaixo
3. Seja ESPECÍFICO - detalhes salvam tempo futuro
4. Inclua código/SQL quando relevante

**Template:**
```markdown
### [YYYY-MM-DD] Título Curto do Erro

**Contexto:** Onde/quando aconteceu
**Sintoma:** O que vimos (erro, comportamento)
**Causa Raiz:** Por que aconteceu
**Solução:** Como corrigimos
**Prevenção:** Como evitar no futuro
**Tags:** #tag1 #tag2
```

---

## 📋 Erros Resolvidos

### [2025-11-18] Python Path Calculation Confusion - `.parent.parent.parent`

**Contexto:** Implementando RAG Feedback Loop com scripts em `.claude/scripts/python/`, precisava calcular PROJECT_ROOT para acessar `.claude/vectordb` e `.claude/logs`

**Sintoma:**
- Path duplicado: `/path/to/project/.claude/.claude/vectordb`
- Vector database não encontrada
- Scripts falhando com "No such file or directory"
- Confusion sobre quantos `.parent` usar

**Causa Raiz:**
Falta de clareza sobre a estrutura de diretórios e como calcular PROJECT_ROOT:

```
Structure:
PROJECT_ROOT/
  .claude/
    scripts/
      python/
        script.py  <-- Estamos aqui
    vectordb/      <-- Queremos acessar isto
    logs/          <-- E isto
```

Com script em `.claude/scripts/python/script.py`:
- `Path(__file__)` = `.../PROJECT_ROOT/.claude/scripts/python/script.py`
- `.parent` (1x) = `.../PROJECT_ROOT/.claude/scripts/python`
- `.parent` (2x) = `.../PROJECT_ROOT/.claude/scripts`
- `.parent` (3x) = `.../PROJECT_ROOT/.claude`
- `.parent` (4x) = `.../PROJECT_ROOT`  ← **Correto!**

Inicialmente usei apenas 3 `.parent`, resultando em PROJECT_ROOT = `.../PROJECT_ROOT/.claude`, causando paths duplicados.

**Solução:**
```python
# CORRETO - Para scripts em .claude/scripts/python/
script_path = Path(__file__).resolve()
PROJECT_ROOT = script_path.parent.parent.parent.parent  # 4x parent
VECTORDB_PATH = str(PROJECT_ROOT / ".claude" / "vectordb")
LOGS_PATH = str(PROJECT_ROOT / ".claude" / "logs")

# Debug para verificar:
# print(f"Script: {script_path}")
# print(f"PROJECT_ROOT: {PROJECT_ROOT}")
# print(f"VDB Path: {VECTORDB_PATH}")
```

**Prevenção:**
1. **SEMPRE adicionar comentário explicativo:**
   ```python
   # This script is at: PROJECT_ROOT/.claude/scripts/python/script.py
   # parent.parent.parent.parent gives us PROJECT_ROOT
   PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
   ```

2. **Criar helper function para reutilizar:**
   ```python
   def get_project_root():
       """Returns PROJECT_ROOT from any script in .claude/scripts/python/"""
       return Path(__file__).resolve().parent.parent.parent.parent
   ```

3. **Debug temporariamente quando incerto:**
   ```python
   script = Path(__file__).resolve()
   for i in range(1, 6):
       print(f"parent ({i}x): {script.parents[i-1]}")
   ```

4. **Documentar estrutura de diretórios** no docstring do script

**Tags:** #python #paths #filesystem #rag #debugging

---

### [2025-11-18] Odoo Não Acessível - http_interface Incorreto + Firewall GCP

**Contexto:** Após aplicar otimizações (swap, work_mem, permissions.xml) e restart do Odoo no servidor testing (odoo-sr-tensting), a URL http://35.199.92.1:8069 não estava acessível externamente

**Sintoma:**
- Odoo rodando normalmente (17 workers ativos)
- PostgreSQL funcionando
- Porta 8069 sem conexões externas
- `ss -tlnp | grep 8069` mostrava: `LISTEN 127.0.0.1:8069` (não 0.0.0.0)
- Teste interno (`curl localhost:8069`) funcionava: HTTP 303 ✅
- Teste externo falhava completamente

**Causa Raiz:**
Duas causas independentes que impediam acesso externo:

1. **Config Odoo - http_interface:** `/etc/odoo-server.conf` tinha `http_interface = 127.0.0.1`
   - Odoo configurado para aceitar APENAS conexões de localhost
   - Porta 8069 escutava em 127.0.0.1, não em 0.0.0.0 (todas interfaces)

2. **Firewall GCP:** Sem regra para porta 8069
   - Apenas porta 80 (HTTP) e 1369 tinham regras de firewall
   - Tráfego externo para porta 8069 bloqueado pelo GCP

**Solução:**

**1. Corrigir configuração Odoo:**
```bash
# Backup da config antes de mudar
sudo cp /etc/odoo-server.conf /etc/odoo-server.conf.backup-http-interface

# Alterar http_interface de 127.0.0.1 para 0.0.0.0
sudo sed -i 's/^http_interface = 127.0.0.1/http_interface = 0.0.0.0/' /etc/odoo-server.conf

# Verificar mudança
sudo grep 'http_interface' /etc/odoo-server.conf
# Output: http_interface = 0.0.0.0 ✅

# CRÍTICO: Restart COMPLETO (processos antigos mantinham config antiga)
sudo pkill -9 -f 'odoo-bin'
sleep 3
cd /odoo/odoo-server
sudo -u odoo python3 ./odoo-bin -c /etc/odoo-server.conf &
sleep 15

# Validar que porta agora escuta em 0.0.0.0 (todas interfaces)
sudo ss -tlnp | grep 8069
# Output: LISTEN 0.0.0.0:8069 ✅ (CORRETO!)
```

**2. Criar regra de firewall GCP:**
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

# Verificar que servidor tem a tag correta
gcloud compute instances describe odoo-sr-tensting \
  --zone=southamerica-east1-b \
  --project=webserver-258516 \
  --format="value(tags.items)"
# Output: http-server ✅
```

**Validação Completa:**
```bash
# 1. Teste interno (no servidor)
curl -I http://localhost:8069/web
# Output: HTTP/1.0 303 SEE OTHER
#         Location: http://localhost:8069/web/login ✅

# 2. Teste externo (de qualquer lugar na internet)
curl -I http://35.199.92.1:8069/web
# Output: HTTP/1.0 303 SEE OTHER
#         Location: http://35.199.92.1:8069/web/login
#         Set-Cookie: session_id=... ✅

# 3. Verificar interface de escuta
sudo ss -tlnp | grep 8069
# Output: LISTEN 0.0.0.0:8069 (não 127.0.0.1) ✅

# 4. Verificar firewall GCP
gcloud compute firewall-rules list --filter="name=allow-odoo-8069"
# Output: allow-odoo-8069  default  INGRESS  1000  tcp:8069 ✅
```

**Prevenção - Checklist Completo:**

**Ao configurar Odoo para acesso externo:**
- ✅ SEMPRE verificar `http_interface` em `/etc/odoo-server.conf`
  - **Produção com Nginx:** `http_interface = 127.0.0.1` (reverse proxy interno)
  - **Testing/Acesso direto:** `http_interface = 0.0.0.0` (acesso externo)
- ✅ SEMPRE fazer restart COMPLETO após mudar http_interface
  - `pkill -9 -f odoo-bin` - processos antigos mantêm config antiga!
  - Não basta restart normal
- ✅ SEMPRE validar com `ss -tlnp | grep PORTA` - verificar se é 0.0.0.0 ou 127.0.0.1
- ✅ SEMPRE verificar firewall cloud para portas customizadas (não apenas 80/443)
- ✅ SEMPRE testar interno E externo após mudanças

**Checklist de Troubleshooting - "Odoo Não Acessível":**
```bash
# 1. Odoo está rodando?
ps aux | grep odoo-bin | grep -v grep
# Deve mostrar múltiplos processos

# 2. Porta está escutando?
sudo ss -tlnp | grep 8069
# Deve mostrar LISTEN

# 3. Interface CORRETA?
sudo ss -tlnp | grep 8069 | grep -E '0.0.0.0|127.0.0.1'
# 0.0.0.0 = acesso externo ✅
# 127.0.0.1 = apenas localhost ❌ (se quer acesso externo)

# 4. Config http_interface?
sudo grep 'http_interface' /etc/odoo-server.conf

# 5. Firewall local (iptables)?
sudo iptables -L -n | grep 8069

# 6. Firewall cloud (GCP)?
gcloud compute firewall-rules list --filter="tcp:8069"

# 7. Teste interno?
curl -I http://localhost:8069

# 8. Teste externo?
curl -I http://IP_EXTERNO:8069
```

**Lições Aprendidas:**
1. **http_interface é crítico** - controla de onde Odoo aceita conexões
2. **Restart completo obrigatório** - config só é recarregada ao iniciar processo
3. **Firewall cloud ≠ firewall local** - duas camadas de segurança
4. **ss -tlnp é diagnóstico chave** - mostra exatamente qual interface escuta
5. **Testar sempre interno + externo** - um pode funcionar e outro não

**Impacto após correção:**
- ✅ Odoo acessível externamente em http://35.199.92.1:8069
- ✅ Redirect automático para /web/login funciona
- ✅ Session criada corretamente
- ✅ Servidor testing 100% operacional

**Tags:** #odoo #network #firewall #gcp #http_interface #troubleshooting #critical

---

### [2025-11-17] CRM Record Rules - Vendedores Bloqueados (perm_read=False)

**Contexto:** Módulo crm_products tinha record rules configuradas incorretamente

**Sintoma:**
- Vendedores não conseguiam VER suas próprias oportunidades
- Mensagem "Access Denied" ao abrir CRM
- Gerentes de vendas também bloqueados
- Listagens de leads vazias
- Bug crítico bloqueando uso do CRM

**Arquivo:** `/modulos-customizados-odoo/modulos-sms-comunicacao/addons_custom/crm_products/views/permissions.xml`

**Linhas afetadas:** 8 e 18

**Causa Raiz:**
Record rules com `perm_read="False"` ao invés de `True`. Em Odoo, quando você tem uma record rule restritiva (com domain_force), você DEVE permitir leitura (`perm_read=True`) e deixar o domain_force filtrar quem vê o quê. A estrutura `perm_read=False` bloqueia TODAS leitura independente do domain.

**Padrão Errado:**
```xml
<record id="crm_rule_personal_lead" model="ir.rule">
    <field name="perm_read" eval="False"/>  <!-- ❌ BLOQUEANDO -->
    <field name="domain_force">[...]</field> <!-- Domain nunca é consultado! -->
    <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
</record>
```

**Solução Aplicada:**

1. Mudou `perm_read="False"` → `perm_read="True"` em ambas rules
2. Adicionou explicitamente `perm_write="False"`, `perm_create="False"`, `perm_unlink="False"`
3. Adicionou comentários claros em português
4. Melhorou descrição das rules (adicionou " - Salesman Access" / " - Sales Manager Access")

```xml
<!-- CORRIGIDO -->
<record id="crm_rule_personal_lead" model="ir.rule">
    <field name="name">Personal Leads RC - Salesman Access</field>
    <field ref="model_crm_lead" name="model_id"/>
    <field name="perm_read" eval="True"/>      <!-- ✅ AGORA PERMITE -->
    <field name="perm_write" eval="False"/>    <!-- Bloqueado -->
    <field name="perm_create" eval="False"/>   <!-- Bloqueado -->
    <field name="perm_unlink" eval="False"/>   <!-- Bloqueado -->
    <field name="domain_force">[...]</field>   <!-- Filtra quem vê -->
    <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
</record>
```

**Prevenção:**
- SEMPRE usar padrão: `perm_read=True` (permitir) + `domain_force` (filtrar)
- Record rules RESTRITIVAS não precisam bloquear read - o domain faz isso
- Comparar com padrões já implementados (ex: chatroom_sms_advanced)
- TESTAR com usuários não-admin antes de commitar
- Code review obrigatório para security

**Impacto após correção:**
- ✅ Vendedores conseguem VER suas oportunidades
- ✅ Gerentes conseguem VER equipe
- ✅ Domain force ainda filtra acesso corretamente
- ✅ Sem acesso de escrita/criação/deleção
- ✅ CRM operacional novamente

**Tags:** #security #crm #permissions #record-rules #crítico #resolvido

---

### [2025-11-16] Admin User Locked Out

**Contexto:** Após reorganização de permissões, admin não conseguia acessar

**Sintoma:**
- Erro ao tentar acessar configurações
- "Access Denied" em várias views
- Admin perdeu grupo base.group_system

**Causa Raiz:**
Script de reorganização de permissões removeu inadvertidamente grupos críticos do usuário admin

**Solução:**
```sql
-- Restaurar grupos do admin
INSERT INTO res_groups_users_rel (gid, uid)
SELECT g.id, 2  -- uid 2 = admin
FROM res_groups g
WHERE g.id IN (
    SELECT id FROM res_groups
    WHERE name IN ('Administration / Settings', 'Sales / Manager', 'Technical Features')
)
ON CONFLICT DO NOTHING;
```

**Prevenção:**
- SEMPRE fazer backup antes de mexer em permissões
- NUNCA modificar permissões do uid=2 (admin) sem confirmação explícita
- Criar script de verificação de integridade de permissões

**Tags:** #security #permissions #admin #crítico

---

### [2025-11-16] Vendedores Vendo Oportunidades de Outros

**Contexto:** Após instalação do módulo SMS, vendedores viam todas as oportunidades

**Sintoma:**
- Vendedor A via oportunidades do Vendedor B
- Vazamento de informações sensíveis
- Violação de privacidade

**Causa Raiz:**
Record rules do CRM foram sobrescritas por módulo customizado que não implementou filtros corretos

**Solução:**
```xml
<record id="crm_lead_rule_salesman" model="ir.rule">
    <field name="name">Vendedor vê apenas suas oportunidades</field>
    <field name="model_id" ref="crm.model_crm_lead"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
</record>
```

**Prevenção:**
- Sempre criar record rules para novos modelos
- TESTAR com usuários não-admin
- Code review obrigatório para security-related changes

**Tags:** #security #crm #record-rules #privacidade

---

### [2025-11-16] Fotos de Funcionários Perdidas

**Contexto:** Imagens de res.partner desaparecendo aleatoriamente

**Sintoma:**
- Campo `image_1920` fica NULL
- Acontece em updates do partner
- Não há padrão claro

**Causa Raiz:**
**EM INVESTIGAÇÃO** - Possíveis causas:
1. Override incorreto do método write()
2. Limpeza automática de attachments
3. Módulo third-party interferindo

**Solução:**
Ainda não resolvido completamente. Workaround temporário:
- Backup diário de ir_attachment
- Monitorar logs quando acontecer

**Próximos Passos:**
1. Adicionar logging em res.partner.write()
2. Verificar ir_attachment.gc (garbage collector)
3. Revisar módulos instalados que tocam em res.partner

**Tags:** #bug #res-partner #images #investigating

---

### [2025-11-16] SMS Não Sendo Enviado

**Contexto:** Integração Kolmeya API falhando silenciosamente

**Sintoma:**
- Status "sent" no Odoo
- SMS nunca chega
- Sem erro nos logs

**Causa Raiz:**
Timeout muito curto (5s) causava falha antes da API responder, mas exception não era capturada corretamente

**Solução:**
```python
def send_sms(self, phone, message):
    try:
        response = requests.post(
            KOLMEYA_URL,
            json={'phone': phone, 'message': message},
            timeout=30  # Aumentado de 5 para 30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        _logger.error(f'Timeout sending SMS to {phone}')
        raise UserError(_('SMS service timeout. Try again later.'))
    except requests.exceptions.RequestException as e:
        _logger.error(f'Error sending SMS: {e}')
        raise UserError(_('Failed to send SMS: %s') % str(e))
```

**Prevenção:**
- Usar timeouts adequados (30s para APIs externas)
- SEMPRE capturar exceptions corretamente
- Logar erros de integração
- Mostrar erro para usuário quando falhar

**Tags:** #integration #kolmeya #sms #api #timeout

---

### [2025-11-15] Performance Degradada no CRM

**Contexto:** Listagem de oportunidades levando >10s para carregar

**Sintoma:**
- View tree muito lenta
- Query PostgreSQL executando por segundos
- CPU do servidor em 100%

**Causa Raiz:**
N+1 queries em campo computado `partner_phone` que buscava telefone sem cache

**Solução:**
```python
# ANTES (ruim)
@api.depends('partner_id')
def _compute_partner_phone(self):
    for record in self:
        record.partner_phone = record.partner_id.phone  # N+1!

# DEPOIS (bom)
@api.depends('partner_id.phone')
def _compute_partner_phone(self):
    for record in self:
        record.partner_phone = record.partner_id.phone  # Cached!
```

**Prevenção:**
- Sempre usar `@api.depends()` com campos relacionados completos
- Usar `mapped()` quando iterar sobre múltiplos records
- Profile queries com pg_stat_statements
- Monitorar slow queries

**Tags:** #performance #crm #n+1 #optimization

---

## 🔍 Erros Comuns - Quick Reference

### Permission Denied
1. Verificar ir.model.access.csv
2. Verificar record rules
3. Testar com `sudo()` para isolar problema
4. Verificar grupos do usuário

### Field Not Found
1. Model está registrado no `__init__.py`?
2. Campo existe no modelo Python?
3. Module foi atualizado? (`-u module`)
4. Typo no nome do campo?

### Import Error
1. Módulo está em addons-path?
2. `__init__.py` importa o arquivo?
3. Dependências no manifest?
4. Syntax error no Python?

### View Error
1. XML bem formado?
2. ID único?
3. Model correto no view?
4. Herança (inherit_id) existe?

### API Integration Fails
1. Network connectivity?
2. Timeout adequado?
3. Exception handling correto?
4. Credentials válidos?
5. Rate limiting?

---

## 📊 Estatísticas

**Total de erros documentados:** 6
**Críticos resolvidos:** 3
**Em investigação:** 1
**Prevenção estabelecida:** 6

---

**Última atualização:** 2025-11-17
**Próxima revisão:** Sempre que novo erro for resolvido

---

## 📝 Template para Novo Erro

Copie e cole quando resolver um novo erro:

```markdown
### [YYYY-MM-DD] Título Curto do Erro

**Contexto:**

**Sintoma:**

**Causa Raiz:**

**Solução:**
```código ou descrição```

**Prevenção:**

**Tags:** #tag1 #tag2
```
