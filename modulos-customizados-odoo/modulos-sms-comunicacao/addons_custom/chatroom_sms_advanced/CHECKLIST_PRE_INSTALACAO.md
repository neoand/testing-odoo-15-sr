# Checklist Pré-Instalação - chatroom_sms_advanced

**Data:** 16/11/2025
**Versão:** 15.0.2.0.0

---

## ✅ VERIFICAÇÕES OBRIGATÓRIAS

### 1. Dependências Instaladas

```bash
# No servidor Odoo, verificar se os módulos base estão instalados:
ssh odoo-rc
cd /odoo

# Verificar sms_base_sr
ls -la /odoo/custom/addons_custom/sms_base_sr/

# Verificar sms_kolmeya
ls -la /odoo/custom/addons_custom/sms_kolmeya/

# Verificar contact_center_sms
ls -la /odoo/custom/addons_custom/contact_center_sms/
```

**Ação:** Se algum não existir, PARE e instale primeiro!

---

### 2. Estrutura de Arquivos

```bash
# Verificar se todos arquivos foram criados:
cd /Users/andersongoliveira/odoo_15_sr/chatroom_sms_advanced/

# Contar arquivos Python
find . -name "*.py" | wc -l
# Deve mostrar: 9 arquivos

# Contar arquivos XML
find . -name "*.xml" | wc -l
# Deve mostrar: 12 arquivos

# Verificar estrutura
tree -L 2
```

**Resultado esperado:**
```
chatroom_sms_advanced/
├── __init__.py
├── __manifest__.py
├── README.md
├── ARQUIVOS_CRIADOS.md
├── CHECKLIST_PRE_INSTALACAO.md
├── models/      (7 arquivos)
├── wizard/      (3 arquivos)
├── views/       (7 arquivos)
├── security/    (2 arquivos)
├── data/        (2 arquivos)
└── static/      (css, js)
```

---

### 3. Validação de Sintaxe Python

```bash
# Validar sintaxe de todos arquivos Python
cd /Users/andersongoliveira/odoo_15_sr/chatroom_sms_advanced/

# Verificar models
python3 -m py_compile models/*.py
# Se houver erro, corrigir antes de continuar!

# Verificar wizard
python3 -m py_compile wizard/*.py
```

**✅ Sem erros = OK**
**❌ Com erros = CORRIGIR ANTES DE INSTALAR**

---

### 4. Validação de XML

```bash
# Validar todos XML
cd /Users/andersongoliveira/odoo_15_sr/chatroom_sms_advanced/

# Verificar views
xmllint --noout views/*.xml
# Deve retornar vazio (sem erros)

# Verificar wizard
xmllint --noout wizard/*.xml

# Verificar security
xmllint --noout security/*.xml

# Verificar data
xmllint --noout data/*.xml
```

**✅ Sem erros = OK**
**❌ Erros de sintaxe XML = CORRIGIR**

---

### 5. Verificar __manifest__.py

```python
# Abrir e verificar manualmente:
cat __manifest__.py

# Verificar:
# ✅ name: 'ChatRoom SMS Advanced'
# ✅ version: '15.0.2.0.0'
# ✅ depends: ['sms_base_sr', 'sms_kolmeya', 'contact_center_sms']
# ✅ data: lista completa de arquivos XML
# ✅ installable: True
```

---

### 6. Verificar security/ir.model.access.csv

```bash
# Verificar formato CSV
cat security/ir.model.access.csv

# Deve ter 11 linhas (1 header + 10 acessos):
# - sms.scheduled (user + manager)
# - sms.campaign (user + manager)
# - sms.blacklist (user + manager)
# - sms.dashboard (user + manager)
# - sms.bulk.send (user + manager)
```

**Verificar:**
- ✅ Sem espaços extras
- ✅ IDs únicos
- ✅ Todos modelos cobertos

---

## 🔄 PROCESSO DE INSTALAÇÃO

### Passo 1: Backup

```bash
# Backup do banco de dados
ssh odoo-rc
sudo -u postgres pg_dump odoo_15 > /tmp/odoo_15_backup_$(date +%Y%m%d_%H%M%S).sql

# Backup do módulo atual (se existir)
cd /odoo/custom/addons_custom/
[ -d chatroom_sms_advanced ] && sudo cp -r chatroom_sms_advanced chatroom_sms_advanced.BACKUP_$(date +%Y%m%d)
```

---

### Passo 2: Upload do Módulo

```bash
# Do seu Mac, enviar módulo para servidor:
cd /Users/andersongoliveira/odoo_15_sr/

# Rsync (preserva permissões)
rsync -avz --progress chatroom_sms_advanced/ odoo-rc:/tmp/chatroom_sms_advanced/

# No servidor, mover para addons_custom
ssh odoo-rc
sudo rm -rf /odoo/custom/addons_custom/chatroom_sms_advanced
sudo mv /tmp/chatroom_sms_advanced /odoo/custom/addons_custom/
sudo chown -R odoo:odoo /odoo/custom/addons_custom/chatroom_sms_advanced
```

---

### Passo 3: Atualizar Lista de Apps

```bash
ssh odoo-rc
cd /odoo

# Atualizar lista (não instala ainda)
sudo -u odoo ./odoo-bin -c odoo.conf -d odoo_15 --stop-after-init --log-level=warn
```

**Verificar logs:**
- ✅ Sem erros de import
- ✅ Módulo aparece na lista
- ❌ Erros = CORRIGIR antes de instalar

---

### Passo 4: Instalação (CUIDADO!)

```bash
# Instalar módulo
ssh odoo-rc
cd /odoo

# Modo 1: Via linha de comando
sudo -u odoo ./odoo-bin -c odoo.conf -d odoo_15 -i chatroom_sms_advanced --stop-after-init --log-level=info

# Modo 2: Via interface (RECOMENDADO)
# 1. Apps > Update Apps List
# 2. Remove "Apps" filter
# 3. Search "SMS Advanced"
# 4. Click Install
```

**Verificar logs durante instalação:**
```bash
# Em outro terminal, monitorar logs
ssh odoo-rc
tail -f /var/log/odoo/odoo.log | grep -i "chatroom_sms"
```

---

### Passo 5: Verificação Pós-Instalação

```bash
# 1. Verificar se instalou sem erros
ssh odoo-rc
psql -U odoo odoo_15 -c "SELECT name, state FROM ir_module_module WHERE name = 'chatroom_sms_advanced';"

# Deve mostrar:
#          name          | state
# -----------------------+-----------
# chatroom_sms_advanced | installed

# 2. Verificar se modelos foram criados
psql -U odoo odoo_15 -c "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'sms_%' ORDER BY table_name;"

# Deve incluir:
# - sms_scheduled
# - sms_campaign
# - sms_blacklist
# - sms_dashboard (view)

# 3. Verificar se crons foram criados
psql -U odoo odoo_15 -c "SELECT name, active, interval_type, interval_number FROM ir_cron WHERE name LIKE '%SMS%';"

# Deve mostrar 3 crons:
# - Process Scheduled SMS (5 minutes)
# - Check Provider Balance (6 hours)
# - Sync Blacklist (1 hour)
```

---

## 🧪 TESTES PÓS-INSTALAÇÃO

### Teste 1: Acessar Menus

1. Login no Odoo
2. Ir em: **SMS Advanced** (menu principal)
3. Verificar submenus:
   - ✅ Dashboard
   - ✅ Campaigns
   - ✅ Scheduled SMS
   - ✅ Send Bulk SMS
   - ✅ Configuration > Blacklist (se manager)

**Status:** ___________

---

### Teste 2: Dashboard

1. Menu: SMS Advanced > Dashboard
2. Verificar views disponíveis:
   - ✅ Graph
   - ✅ Pivot
   - ✅ Kanban
   - ✅ Tree

**Status:** ___________

---

### Teste 3: Criar Campanha

1. Menu: SMS Advanced > Campaigns > Create
2. Preencher:
   - Name: "Teste Instalação"
   - Provider: (selecionar)
   - Template: (selecionar)
   - Recipients: (adicionar 1 contato)
3. Salvar

**Status:** ___________

---

### Teste 4: Agendar SMS

1. Menu: SMS Advanced > Scheduled SMS > Create
2. Preencher:
   - Name: "Teste Agendamento"
   - Schedule Type: Once
   - Date: Amanhã
   - Time: 10:00
3. Salvar
4. Botão: Activate

**Status:** ___________

---

### Teste 5: Envio em Massa (SEM ENVIAR!)

1. Contacts > Selecionar 2-3 contatos
2. Action > Send Bulk SMS
3. Preencher wizard:
   - Template ou mensagem
   - Verificar estimativa de custo
4. Preview (não enviar ainda!)

**Status:** ___________

---

### Teste 6: Blacklist

1. Menu: SMS Advanced > Configuration > Blacklist
2. Create
3. Preencher:
   - Phone: +5511999999999
   - Reason: Manual
4. Salvar
5. Verificar se synced_kolmeya = False

**Status:** ___________

---

### Teste 7: Extend Views

1. Ir em qualquer SMS existente (de sms_base_sr)
2. Verificar se aparecem novos campos:
   - ✅ Campaign
   - ✅ Scheduled Task
   - ✅ Cost
3. Verificar botões:
   - ✅ Add to Blacklist

**Status:** ___________

---

### Teste 8: Provider Settings

1. Settings > Technical > SMS > Providers
2. Abrir provider existente
3. Verificar novas abas:
   - ✅ Advanced Settings
   - ✅ Statistics
4. Verificar campos:
   - ✅ Balance Warning
   - ✅ DND Settings

**Status:** ___________

---

## ⚠️ TROUBLESHOOTING

### Erro: "Module not found"

**Causa:** Dependências não instaladas
**Solução:**
```bash
# Instalar dependências primeiro
Apps > Search "sms_base_sr" > Install
Apps > Search "sms_kolmeya" > Install
Apps > Search "contact_center_sms" > Install
# Depois instalar chatroom_sms_advanced
```

---

### Erro: "Table already exists"

**Causa:** Versão antiga do módulo ainda está no BD
**Solução:**
```bash
# Desinstalar versão antiga primeiro
Apps > Search "chatroom_sms_advanced" > Uninstall
# Atualizar código
# Instalar novamente
```

---

### Erro: "Field 'campaign_id' does not exist"

**Causa:** Modelo sms.message não foi estendido corretamente
**Solução:**
```bash
# Atualizar módulo
Apps > Search "chatroom_sms_advanced" > Upgrade
# Ou via CLI:
sudo -u odoo ./odoo-bin -c odoo.conf -d odoo_15 -u chatroom_sms_advanced --stop-after-init
```

---

### Erro: "View não encontrada"

**Causa:** Referência errada no inherit_id
**Solução:**
1. Verificar se sms_base_sr tem a view referenciada
2. Ajustar ref="sms_base_sr.view_sms_message_form" no XML
3. Atualizar módulo

---

### Cron não executa

**Causa:** Cron desativado ou erro no método
**Solução:**
```sql
-- Verificar cron
SELECT id, name, active, nextcall FROM ir_cron WHERE name LIKE '%SMS%';

-- Ativar se necessário
UPDATE ir_cron SET active = true WHERE name LIKE '%SMS Advanced%';

-- Executar manualmente para testar
-- Via Python shell
env['sms.scheduled'].cron_process_scheduled_sms()
```

---

## 📋 CHECKLIST FINAL

Antes de considerar a instalação completa, verificar:

- [ ] Todos os 3 módulos de dependência estão instalados
- [ ] chatroom_sms_advanced aparece como "installed"
- [ ] Menus aparecem corretamente
- [ ] Dashboard carrega sem erros
- [ ] Consegue criar campanha
- [ ] Consegue criar agendamento
- [ ] Wizard de envio em massa abre
- [ ] Blacklist funciona
- [ ] Views estendidas mostram novos campos
- [ ] 3 crons foram criados e estão ativos
- [ ] Sem erros no log do Odoo
- [ ] Security groups foram criados

**Status Final:** ___________

**Data de Instalação:** ___________

**Instalado por:** ___________

---

## 📞 SUPORTE

**Problemas durante instalação:**
- Verificar logs: `/var/log/odoo/odoo.log`
- Executar em modo debug: `--log-level=debug`
- Consultar: RESUMO_EXECUTIVO_SMS.md
- Consultar: PLANO_ACAO_REFATORACAO.md

**Desenvolvedor:** Anderson Oliveira
**Data:** 16/11/2025

---

**IMPORTANTE:** NÃO instalar em produção antes de testar em ambiente de staging!
