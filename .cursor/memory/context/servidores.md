# 🖥️ Servidores do Projeto - Informações Completas

> **Última atualização:** 2025-11-17

---

## 📊 RESUMO DOS SERVIDORES

| # | Nome | Tipo | Status | Acesso |
|---|------|------|--------|--------|
| 1 | **odoo-sr-tensting** | Testing/Development | ✅ Ativo | gcloud SSH |
| 2 | **odoo-rc** | Produção | ✅ Ativo | SSH tradicional |

---

## 🖥️ SERVIDOR 1: odoo-sr-tensting (TESTING)

### Informações Gerais
- **Nome:** odoo-sr-tensting
- **Tipo:** Testing/Development
- **Localização:** `/Users/andersongoliveira/testing_odoo_15_sr`
- **Cloud Provider:** Google Cloud Platform
- **Sistema Operacional:** Ubuntu 20.04 LTS
- **Status:** ✅ Operacional

### Especificações Técnicas
- **vCPUs:** 2
- **Memória RAM:** 4 GB
- **Disco:** 300 GB SSD (168 GB usado, 124 GB livre)
- **Região:** South America East 1-b

### Rede
- **IP Externo:** 35.199.92.1 (Ephemeral)
- **IP Interno:** 10.158.0.5
- **Projeto GCP:** webserver-258516
- **Zona:** southamerica-east1-b
- **Portas Abertas:** 80 (HTTP), 443 (HTTPS)

### Acesso SSH
```bash
# Método ÚNICO (OS Login habilitado)
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b

# Executar comando remoto
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="comando"

# Copiar arquivo para servidor
gcloud compute scp arquivo.txt odoo-sr-tensting:~/ --zone=southamerica-east1-b
```

**Observações Importantes:**
- ⚠️ OS Login habilitado - SSH tradicional NÃO funciona
- ⚠️ IP externo é Ephemeral (pode mudar ao reiniciar)
- ✅ Autenticação via Google Cloud SDK
- 👤 Usuário no servidor: `admin_iurd_mx`
- 📧 Conta GCP: `admin@iurd.mx`

### Serviços Rodando
| Serviço | Porta | Status |
|---------|-------|--------|
| Odoo 15 | 8069 | ✅ Ativo |
| Longpolling | 8072 | ✅ Ativo |
| PostgreSQL 12 | 5432 | ✅ Ativo |
| Nginx | 80, 443 | ✅ Ativo |

### Odoo
- **Versão:** 15.0
- **Database:** (verificar nome)
- **Admin Password:** `HI5Rdi5UikL9jjLy`
- **Workers:** 9
- **Módulos Custom:** chatroom_sms_advanced

### Diretórios Importantes
```
/odoo/                      - Instalação principal
/odoo/odoo-server/          - Código fonte
/odoo/custom/               - Módulos customizados
/odoo/filestore/            - Arquivos/anexos
/odoo/backups/              - Backups automáticos
/etc/odoo-server.conf       - Configuração
/var/log/odoo/              - Logs
```

### Comandos Úteis
```bash
# Status serviços
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo systemctl status odoo postgresql nginx"

# Ver logs Odoo
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo tail -f /var/log/odoo/odoo-server.log"

# Restart Odoo
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo systemctl restart odoo"

# PostgreSQL
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo -u postgres psql DATABASE"
```

### Backup
- **Frequência:** Diária (12:00 AM - 1:00 AM)
- **Localização:** `/odoo/backups/`

---

## 🖥️ SERVIDOR 2: odoo-rc (PRODUÇÃO)

### Informações Gerais
- **Nome:** odoo-rc
- **Tipo:** Produção (RealCred)
- **Localização:** `/Users/andersongoliveira/odoo_15_sr`
- **Cloud Provider:** Google Cloud Platform
- **Sistema Operacional:** Ubuntu 20.04.6 LTS
- **Status:** ✅ Operacional
- **Uptime:** Desde 24/Ago/2025

### Especificações Técnicas
- **vCPUs:** (não especificado)
- **Memória RAM:** 12 GB (3.9 GB usada - 33%)
- **Disco:** 291 GB (156 GB usado - 54%)
- **Database Size:** 10 GB (realcred)

### Rede
- **IP Externo:** 35.199.79.229
- **Domínio:** odoo.semprereal.com
- **SSL/TLS:** ✅ Let's Encrypt (renovado 09/Nov/2025)
- **Portas:** 80 (HTTP), 443 (HTTPS)

### Acesso SSH
```bash
# Método tradicional
ssh andlee21@35.199.79.229

# Alias (se configurado)
ssh odoo-rc
```

**Observações Importantes:**
- ✅ SSH tradicional funciona
- 👤 Usuário: `andlee21`
- 🔑 Chave SSH: `~/.ssh/id_ed25519`

### Serviços Rodando
| Serviço | Porta | Status | Saúde |
|---------|-------|--------|-------|
| Odoo 15 | 8069 (local) | ✅ Running | 🟢 OK |
| Longpolling | 8072 (local) | ✅ Running | 🟢 OK |
| PostgreSQL 12 | 5432 | ✅ Running | 🟢 OK |
| Nginx | 80, 443 | ✅ Running | 🟢 OK |
| SSL/TLS | 443 | ✅ Active | 🟡 Certbot erro |
| Docker | - | ✅ Running | 🟢 OK |

### Odoo
- **Versão:** 15.0
- **Database:** realcred (10 GB, 946 tabelas)
- **Admin Password:** `HI5Rdi5UikL9jjLy`
- **Workers:** 9 + 1 gevent
- **Conexões PostgreSQL:** ~65 ativas
- **Logs:** `/var/log/odoo/odoo-server.log`

### PostgreSQL
- **Versão:** 12
- **Database:** realcred
- **Conexões Max:** 200 (65 ativas)
- **Shared Buffers:** 4 GB
- **Owner:** odoo (superuser)

### Nginx
- **Domínio:** odoo.semprereal.com
- **SSL:** Let's Encrypt
- **Proxy:** → localhost:8069
- **Longpolling:** → localhost:8072
- **Cache:** Habilitado

### Módulos Customizados (373 MB total)
1. **addons_custom** (195 MB) - 23 módulos
2. **hr_attendance_pro** (65 MB) - RH + Ponto + Face recognition
3. **l10n_br_base** (39 MB) - Fiscal Brasil
4. **social** (33 MB) - Email/comunicação
5. **whatsapp-connector** (17 MB) - 30+ módulos WhatsApp
6. **om_account_accountant** (15 MB) - Contabilidade
7. **helpdesk** (7.1 MB) - Helpdesk completo

### Funcionalidades Principais
- ✅ CRM + Telefonia (3CX)
- ✅ WhatsApp integrado (30+ módulos)
- ✅ Helpdesk completo
- ✅ RH + Ponto eletrônico + Face recognition
- ✅ Fiscal Brasil (NFe, NFse, pagamentos)
- ✅ Dashboard Ninja
- ✅ DMS (gestão documentos)
- ✅ Backup automático

### Diretórios Importantes
```
/odoo/                      - Instalação principal
/odoo/odoo-server/          - Código fonte
/odoo/custom/               - Módulos customizados (373 MB)
/odoo/filestore/            - Arquivos (sessions: 5.7 GB!)
/odoo/backups/              - Backups
/etc/odoo-server.conf       - Configuração
/var/log/odoo/              - Logs
```

### Comandos Úteis
```bash
# Status geral
sudo systemctl status odoo-server postgresql@12-main nginx

# Restart all (ordem importante!)
sudo systemctl restart postgresql@12-main && sleep 5 && \
sudo systemctl restart odoo-server && \
sudo systemctl restart nginx

# Ver logs
sudo tail -f /var/log/odoo/odoo-server.log

# Backup rápido
sudo -u postgres pg_dump -Fc realcred > ~/backup_$(date +%Y%m%d).dump

# PostgreSQL
sudo -u postgres psql realcred
```

### 🚨 Problemas Identificados

#### 🔴 Críticos
1. **Certbot Quebrado**
   - Erro: `'_RSAPublicKey' object has no attribute 'verifier'`
   - Renovação automática SSL pode falhar
   - **Ação:** Atualizar certbot URGENTE

2. **Replicação PostgreSQL Aberta**
   - Config aberto para 0.0.0.0/0
   - Risco de segurança
   - **Ação:** Restringir IPs

#### 🟡 Importantes
3. **Sessions 5.7 GB**
   - `/odoo/filestore/sessions/` muito grande
   - **Ação:** Limpar periodicamente

4. **Swap Desabilitado**
   - Risco de OOM em picos
   - **Ação:** Adicionar 4-8 GB swap

5. **Tabelas Grandes**
   - ir_attachment: 3.6 GB
   - mail_message: 2.3 GB
   - **Ação:** Arquivar dados antigos

### Backup
```bash
# Database (10 GB)
sudo -u postgres pg_dump -Fc realcred > backup.dump

# Filestore + Custom
tar -czf backup.tar.gz /odoo/filestore/ /odoo/custom/

# Configs
tar -czf configs.tar.gz /etc/odoo-server.conf /etc/nginx/ /etc/postgresql/
```

**Frequência:** Backup automático diário

### Acesso Web
- **URL:** https://odoo.semprereal.com
- **HTTP:** http://35.199.79.229
- **HTTPS:** https://35.199.79.229

---

## 📊 COMPARAÇÃO DOS SERVIDORES

| Aspecto | odoo-sr-tensting (Testing) | odoo-rc (Produção) |
|---------|----------------------------|---------------------|
| **Ambiente** | Testing/Development | Produção |
| **RAM** | 4 GB | 12 GB |
| **Disco** | 300 GB (168 GB usado) | 291 GB (156 GB usado) |
| **IP** | 35.199.92.1 (Ephemeral) | 35.199.79.229 |
| **Acesso SSH** | gcloud CLI (OS Login) | SSH tradicional |
| **Database** | (verificar) | realcred (10 GB) |
| **Workers** | 9 | 9 + 1 gevent |
| **Domínio** | ❌ Não | ✅ odoo.semprereal.com |
| **SSL** | ❌ Não configurado | ✅ Let's Encrypt |
| **Módulos Custom** | chatroom_sms_advanced | 7 pacotes (373 MB) |
| **Finalidade** | Testes SMS/CRM | Produção RealCred |
| **Backup** | Diário (automático) | Diário (automático) |

---

## 🔑 CREDENCIAIS (PROTEGER!)

### odoo-sr-tensting
- **SSH:** Via gcloud (admin_iurd_mx)
- **Conta GCP:** admin@iurd.mx
- **Odoo Admin:** HI5Rdi5UikL9jjLy

### odoo-rc
- **SSH:** andlee21@35.199.79.229
- **Odoo Admin:** HI5Rdi5UikL9jjLy
- **Database:** realcred
- **PostgreSQL Users:** postgres, odoo (superuser)

---

## 📁 DOCUMENTAÇÃO ADICIONAL

### Servidor Testing (odoo-sr-tensting)
- Localização: `./servidor-testing-odoo/`
- Arquivos: CONEXAO_SSH.md, ACESSOS_CREDENCIAIS.md, etc.

### Servidor Produção (odoo-rc)
- Localização: `/Users/andersongoliveira/odoo_15_sr/server_documentation/`
- Arquivos: 00_EXECUTIVE_SUMMARY.md até 24_CONTACT_CENTER_SMS_IMPLEMENTATION.md

---

## ⚠️ OBSERVAÇÕES IMPORTANTES

### odoo-sr-tensting (Testing)
1. OS Login habilitado - SEMPRE usar gcloud
2. IP Ephemeral - pode mudar
3. Menos recursos (4 GB RAM)
4. Foco em testes SMS e CRM

### odoo-rc (Produção)
1. Servidor principal RealCred
2. Mais recursos (12 GB RAM)
3. Certbot precisa correção urgente
4. Limpar sessions regularmente (5.7 GB!)
5. Configurar swap (4-8 GB)
6. Restringir PostgreSQL replication

---

## 🚀 ACESSO RÁPIDO

### Testing
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b
```

### Produção
```bash
ssh odoo-rc
# ou
ssh andlee21@35.199.79.229
```

### Web
- **Testing:** http://35.199.92.1
- **Produção:** https://odoo.semprereal.com

---

**Última atualização:** 2025-11-17
**Total de servidores:** 2
**Status:** ✅ Ambos operacionais
**Próxima revisão:** Quando houver mudanças
