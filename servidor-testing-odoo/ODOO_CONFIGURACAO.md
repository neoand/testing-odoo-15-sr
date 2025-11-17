# Configuração do Odoo

## Informações Gerais

**Status:** ✅ Rodando e Ativo

**Versão:** (verificar com `odoo-bin --version`)

**Banco de Dados:** `realcred`

**Diretório de Instalação:** `/odoo/odoo-server/`

## Configuração do Servidor

### Arquivo de Configuração
- **Localização:** `/etc/odoo-server.conf`
- **Usuário:** `odoo`

### Parâmetros Principais

**Banco de Dados:**
```ini
dbfilter = realcred
list_db = False
log_db = True
log_db_level = info
```

**Senha de Administração:**
```ini
admin_passwd = HI5Rdi5UikL9jjLy
```
⚠️ **IMPORTANTE:** Esta é a senha master do Odoo. Mantenha segura!

**Portas:**
```ini
http_port = 8069
longpolling_port = 8072
```

**Rede:**
```ini
http_enable = True
http_interface = 127.0.0.1
netrpc = True
netrpc_interface = 127.0.0.1
proxy_mode = True
```

**Workers:**
```ini
workers = 9
max_cron_threads = 5
```

**Limites de Recursos:**
```ini
limit_memory_hard = 6442450944    # 6 GB
limit_memory_soft = 8589934592     # 8 GB
limit_time_cpu = 60                # 60 segundos
limit_time_real = 120              # 120 segundos
limit_request = 2048               # 2048 requisições
limit_time_real_cron = 600         # 600 segundos para cron
```

**Segurança:**
```ini
bantime = 900      # 15 minutos de banimento
maxretry = 5       # 5 tentativas antes de banir
```

**Logs:**
```ini
logfile = /var/log/odoo/odoo-server.log
log_level = info
log_handler = :WARNING
```

**Diretórios:**
```ini
data_dir = /odoo/filestore
addons_path = /odoo/odoo-server/addons,/odoo/custom/addons_custom,/odoo/custom/helpdesk,/odoo/custom/l10n_br_base,/odoo/custom/social,/odoo/custom/addons-whatsapp-connector,/odoo/custom/om_account_accountant,/odoo/custom/hr_attendance_pro
```

**Outros:**
```ini
csv_internal_sep = ,
demo = {}
email_from = False
```

## Estrutura de Módulos

### Caminhos de Addons

1. **Módulos Core:**
   - `/odoo/odoo-server/addons`

2. **Módulos Customizados:**
   - `/odoo/custom/addons_custom`
   - `/odoo/custom/helpdesk`
   - `/odoo/custom/l10n_br_base` (Localização Brasil)
   - `/odoo/custom/social`
   - `/odoo/custom/addons-whatsapp-connector`
   - `/odoo/custom/om_account_accountant`
   - `/odoo/custom/hr_attendance_pro`

### Módulo Específico
- `/odoo/iurd-cm-mx/` - Módulo customizado específico

## Processos em Execução

### Processo Principal
- **PID:** 584
- **Comando:** `python3 /odoo/odoo-server/odoo-bin -c /etc/odoo-server.conf`

### Workers HTTP
- **Quantidade:** 9 workers
- **PIDs:** 1138, 1139, 1140, 1141, 1143, 1145, 1148, 1149, 1151
- **Porta:** 8069 (localhost)

### Worker Gevent (Longpolling)
- **PID:** 1155
- **Comando:** `/bin/python3 /odoo/odoo-server/odoo-bin gevent -c /etc/odoo-server.conf`
- **Porta:** 8072 (localhost)

### Workers Adicionais
- **PIDs:** 1159, 1162, 1182, 1184, 1186
- **Função:** Processamento de requisições e tarefas em background

## Acesso ao Odoo

### Via Web
- **URL Externa:** `http://35.199.92.1` ou `https://35.199.92.1`
- **URL Interna:** `http://localhost:8069` (apenas no servidor)
- **Proxy:** Nginx faz proxy reverso para o Odoo

### Via Linha de Comando

**Conectar ao Odoo Shell:**
```bash
sudo -u odoo /odoo/odoo-server/odoo-bin shell -c /etc/odoo-server.conf -d realcred
```

**Executar comando específico:**
```bash
sudo -u odoo /odoo/odoo-server/odoo-bin -c /etc/odoo-server.conf -d realcred --stop-after-init
```

## Banco de Dados

### Informações
- **Nome do Banco:** `realcred`
- **Usuário:** `odoo`
- **Host:** `localhost`
- **Porta:** `5432` (PostgreSQL)

### Conexão
```bash
# Conectar ao banco
sudo -u postgres psql -d realcred

# Ou como usuário odoo
psql -U odoo -d realcred
```

### Backup do Banco
```bash
# Backup manual
sudo -u postgres pg_dump realcred > /odoo/backups/realcred_$(date +%Y%m%d_%H%M%S).sql
```

## Logs

### Localização
- **Arquivo Principal:** `/var/log/odoo/odoo-server.log`
- **Nível de Log:** `info`
- **Handler:** `:WARNING` (warnings e acima)

### Visualizar Logs
```bash
# Logs em tempo real
sudo tail -f /var/log/odoo/odoo-server.log

# Últimas 100 linhas
sudo tail -n 100 /var/log/odoo/odoo-server.log

# Logs via journalctl (se configurado como serviço)
sudo journalctl -u odoo -f
```

## Gerenciamento

### Reiniciar Odoo
```bash
# Se tiver serviço systemd
sudo systemctl restart odoo

# Ou matar processos e reiniciar
sudo pkill -f odoo-bin
sudo -u odoo /odoo/odoo-server/odoo-bin -c /etc/odoo-server.conf
```

### Parar Odoo
```bash
# Via systemd
sudo systemctl stop odoo

# Ou matar processos
sudo pkill -f odoo-bin
```

### Iniciar Odoo
```bash
# Via systemd
sudo systemctl start odoo

# Ou manualmente
sudo -u odoo /odoo/odoo-server/odoo-bin -c /etc/odoo-server.conf
```

### Atualizar Módulos
```bash
sudo -u odoo /odoo/odoo-server/odoo-bin -c /etc/odoo-server.conf -d realcred -u nome_modulo --stop-after-init
```

### Atualizar Todos os Módulos
```bash
sudo -u odoo /odoo/odoo-server/odoo-bin -c /etc/odoo-server.conf -d realcred -u all --stop-after-init
```

## Monitoramento

### Verificar Status
```bash
# Processos rodando
ps aux | grep odoo | grep -v grep

# Portas em uso
sudo ss -tulpn | grep -E "(8069|8072)"

# Uso de memória
ps aux | grep odoo | awk '{sum+=$6} END {print "Memória total: " sum/1024 " MB"}'
```

### Verificar Performance
```bash
# Carga do sistema
top -bn1 | grep -i odoo

# Conexões ao banco
sudo -u postgres psql -d realcred -c "SELECT count(*) FROM pg_stat_activity WHERE datname='realcred';"
```

## Troubleshooting

### Odoo não inicia
1. Verificar logs: `sudo tail -f /var/log/odoo/odoo-server.log`
2. Verificar permissões: `ls -la /odoo/`
3. Verificar banco de dados: `sudo systemctl status postgresql`
4. Verificar espaço em disco: `df -h`

### Erro de conexão ao banco
1. Verificar se PostgreSQL está rodando: `sudo systemctl status postgresql`
2. Testar conexão: `sudo -u postgres psql -d realcred`
3. Verificar configuração em `/etc/odoo-server.conf`

### Performance lenta
1. Verificar uso de memória: `free -h`
2. Verificar número de workers: `ps aux | grep odoo | wc -l`
3. Verificar logs de erro: `sudo grep ERROR /var/log/odoo/odoo-server.log`

### Módulos não aparecem
1. Verificar caminhos em `addons_path` no arquivo de configuração
2. Verificar permissões dos diretórios: `ls -la /odoo/custom/`
3. Atualizar lista de módulos: `sudo -u odoo /odoo/odoo-server/odoo-bin -c /etc/odoo-server.conf -d realcred --update=all --stop-after-init`

