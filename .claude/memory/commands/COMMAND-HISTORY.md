# 💻 Histórico de Comandos - Aprendizado Automático

> **Propósito:** Registrar AUTOMATICAMENTE todo comando executado, erros encontrados e soluções aplicadas para NUNCA repetir o mesmo erro.

---

## 🎯 Como Funciona

**Sistema de Aprendizado:**
1. **Comando executado** → Registro automático
2. **Erro encontrado** → Solução documentada
3. **Sucesso confirmado** → Pattern salvo
4. **Próxima vez** → Claude usa conhecimento prévio

**Resultado:**
- ✅ Nunca mais "ah, precisa sudo!"
- ✅ Comandos corretos na primeira vez
- ✅ Aprendizado incremental
- ✅ Zero tempo perdido

---

## 📋 Comandos SSH/Servidor

### systemctl (Controle de Serviços)

```bash
# ❌ NUNCA funciona sem sudo
systemctl restart odoo

# ✅ SEMPRE usar sudo
sudo systemctl restart odoo
sudo systemctl status odoo
sudo systemctl stop odoo
sudo systemctl start odoo
```

**Regra aprendida:** `systemctl` SEMPRE requer `sudo`
**Data:** 2025-11-17
**Contexto:** Controle de serviços do sistema

---

### Logs do Odoo

```bash
# ✅ Não precisa sudo para ler
tail -f /var/log/odoo/odoo-server.log

# ⚠️ Se acesso negado, usar:
sudo tail -f /var/log/odoo/odoo-server.log

# ✅ Grep em logs
sudo grep "ERROR" /var/log/odoo/odoo-server.log

# ✅ Ver últimas 100 linhas
sudo tail -n 100 /var/log/odoo/odoo-server.log
```

**Regra aprendida:** Logs podem precisar sudo dependendo de permissões
**Data:** 2025-11-17

---

### PostgreSQL

```bash
# ✅ Sempre como usuário postgres
sudo -u postgres psql DATABASE_NAME

# ✅ Listar databases
sudo -u postgres psql -l

# ✅ Executar query
sudo -u postgres psql DATABASE_NAME -c "SELECT * FROM res_users LIMIT 5;"

# ✅ Backup
sudo -u postgres pg_dump DATABASE_NAME > backup.sql

# ✅ Restore
sudo -u postgres psql DATABASE_NAME < backup.sql
```

**Regra aprendida:** PostgreSQL SEMPRE como `-u postgres`
**Data:** 2025-11-17

---

### Odoo CLI

```bash
# ✅ Localização comum do odoo-bin
/usr/bin/odoo
# ou
/opt/odoo/odoo-bin
# ou
python3 odoo-bin

# ✅ Update module
sudo -u odoo /usr/bin/odoo -c /etc/odoo/odoo.conf -d DATABASE -u MODULE --stop-after-init

# ✅ Install module
sudo -u odoo /usr/bin/odoo -c /etc/odoo/odoo.conf -d DATABASE -i MODULE --stop-after-init

# ✅ Run tests
sudo -u odoo /usr/bin/odoo -c /etc/odoo/odoo.conf -d DATABASE -u MODULE --test-enable --stop-after-init

# ✅ Shell mode
sudo -u odoo /usr/bin/odoo -c /etc/odoo/odoo.conf -d DATABASE --shell-interface=ipython
```

**Regra aprendida:** odoo-bin geralmente roda como usuário `odoo`
**Data:** 2025-11-17

---

### Permissões de Arquivo

```bash
# ✅ Mudar owner para odoo
sudo chown -R odoo:odoo /path/to/module

# ✅ Permissões corretas para módulos
sudo chmod -R 755 /path/to/module

# ✅ Verificar permissões
ls -la /path/to/module
```

**Regra aprendida:** Módulos Odoo devem pertencer ao usuário `odoo`
**Data:** 2025-11-17

---

### Arquivos de Configuração

```bash
# ⚠️ Sempre usar sudo para editar configs do sistema
sudo nano /etc/odoo/odoo.conf
sudo nano /etc/systemd/system/odoo.service

# ✅ Reload systemd após mudanças
sudo systemctl daemon-reload
```

**Regra aprendida:** Configs em `/etc/` SEMPRE precisam sudo
**Data:** 2025-11-17

---

## 🐛 Erros Comuns e Soluções AUTO-APRENDIDAS

### Erro: "Permission denied"

**Sintoma:**
```
bash: /var/log/odoo/odoo-server.log: Permission denied
```

**Solução automática:**
```bash
# Claude deve AUTOMATICAMENTE tentar:
sudo [comando original]
```

**Pattern salvo:** Quando vir "Permission denied" → retry com sudo

---

### Erro: "Failed to restart odoo.service"

**Sintoma:**
```
Failed to restart odoo.service: Access denied
```

**Solução automática:**
```bash
sudo systemctl restart odoo
```

**Pattern salvo:** systemctl SEMPRE precisa sudo

---

### Erro: "FATAL: role 'user' does not exist"

**Sintoma:**
```
psql: FATAL: role "anderson" does not exist
```

**Solução automática:**
```bash
# Usar -u postgres
sudo -u postgres psql DATABASE
```

**Pattern salvo:** psql SEMPRE como postgres user

---

### Erro: "Module not found" no Odoo

**Sintoma:**
```
Module MODULE not found
```

**Solução automática:**
1. Verificar se módulo está em addons-path
2. Verificar permissões (odoo:odoo)
3. Verificar __init__.py
4. Restart Odoo

**Commands:**
```bash
# 1. Verificar localização
ls -la /path/to/module

# 2. Corrigir permissões
sudo chown -R odoo:odoo /path/to/module

# 3. Verificar __init__.py
cat /path/to/module/__init__.py

# 4. Restart
sudo systemctl restart odoo
```

**Pattern salvo:** Checklist completo para módulo não encontrado

---

## 🧠 Regras de Aprendizado Automático

### 1. Comando Falhou → Aprender

**Protocolo:**
```
Comando executado: X
Erro obtido: Y
Solução aplicada: Z
→ SALVAR: "Sempre que X, fazer Z"
```

**Exemplo:**
```
Comando: systemctl restart odoo
Erro: Permission denied
Solução: sudo systemctl restart odoo
→ SALVO: systemctl SEMPRE precisa sudo
```

### 2. Pesquisa Feita → Documentar

**Protocolo:**
```
Dúvida: X
Pesquisa: Y (URL)
Resposta encontrada: Z
→ SALVAR em learnings/
```

**Exemplo:**
```
Dúvida: Como atualizar módulo Odoo?
Pesquisa: Odoo docs
Resposta: odoo-bin -u MODULE
→ SALVO: padrão de update
```

### 3. Padrão Descoberto → Registrar

**Protocolo:**
```
Ação repetida 2+ vezes: X
Pattern identificado: Y
→ SALVAR em patterns/
```

**Exemplo:**
```
Ação: Criar módulo Odoo
Pattern: Sempre mesma estrutura
→ SALVO: Template de módulo
```

---

## 📊 Estatísticas de Aprendizado

**Comandos registrados:** 15+
**Erros documentados:** 4
**Patterns salvos:** 4
**Taxa de acerto (esperada):** 95%+

**Meta:** 100% comandos corretos na primeira tentativa!

---

## 🔄 Auto-Atualização

Este arquivo é atualizado AUTOMATICAMENTE quando:
- ✅ Novo comando é executado com sucesso após falha
- ✅ Novo erro é encontrado e resolvido
- ✅ Novo pattern é identificado
- ✅ Nova regra é aprendida

**Frequência:** A cada sessão de trabalho
**Responsável:** Claude (automático) + Anderson (revisão)

---

## 📝 Template de Nova Entrada

```markdown
### Comando/Erro: [Nome]

```bash
# Comando correto
sudo comando args
```

**Regra aprendida:** [Descrição]
**Data:** YYYY-MM-DD
**Contexto:** [Quando usar]
**Trigger:** [O que indica que precisa deste comando]
```

---

**Última atualização:** 2025-11-17
**Próxima atualização:** Automática a cada novo aprendizado
**Objetivo:** Claude cada vez mais inteligente, zero tempo perdido!
