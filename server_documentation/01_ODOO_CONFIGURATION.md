# Configuração do Odoo - odoo-rc

**Data da documentação:** 2025-11-15
**Servidor:** odoo-rc (35.199.79.229)
**Domínio:** odoo.semprereal.com

---

## Versão do Odoo

- **Versão:** 15.0
- **Release Info:** (15, 0, 0, FINAL, 0, '')
- **Série:** 15.0
- **Python:** 3.8.10

---

## Configuração Principal (/etc/odoo-server.conf)

```ini
[options]
; This is the password that allows database operations:
admin_passwd = HI5Rdi5UikL9jjLy
http_port = 8069
logfile = /var/log/odoo/odoo-server.log
addons_path=/odoo/odoo-server/addons,/odoo/custom/addons_custom ,/odoo/custom/helpdesk ,  /odoo/custom/l10n_br_base , /odoo/custom/social , /odoo/custom/addons-whatsapp-connector, /odoo/custom/om_account_accountant, /odoo/custom/hr_attendance_pro
proxy_mode = True

csv_internal_sep = ,
data_dir = /odoo/filestore

dbfilter = realcred
demo = {}
email_from = False
log_level = info

max_cron_threads = 5
bantime = 900
maxretry = 5
limit_time_real_cron = 600

list_db = False
log_db = True
log_db_level = info
log_handler = :WARNING
longpolling_port = 8072
workers = 9

limit_memory_hard = 6442450944
limit_memory_soft = 8589934592
limit_time_cpu = 60
limit_time_real = 120
limit_request = 2048

netrpc = True
netrpc_interface = 127.0.0.1

http_enable = True
http_interface = 127.0.0.1
```

---

## Parâmetros Importantes

### Segurança
- **admin_passwd:** HI5Rdi5UikL9jjLy (CRÍTICO - Proteger!)
- **list_db:** False (databases não são listadas publicamente)
- **dbfilter:** realcred (apenas este BD é acessível)

### Performance
- **workers:** 9 workers (multi-processo)
- **limit_memory_hard:** 6 GB por worker
- **limit_memory_soft:** 8 GB por worker
- **limit_time_cpu:** 60s
- **limit_time_real:** 120s
- **limit_request:** 2048 requisições por worker

### Portas
- **http_port:** 8069 (interface: 127.0.0.1 - apenas local)
- **longpolling_port:** 8072 (para notificações em tempo real)

### Cron
- **max_cron_threads:** 5 threads
- **limit_time_real_cron:** 600s (10 min timeout)

### Addons Path
1. `/odoo/odoo-server/addons` (addons padrão)
2. `/odoo/custom/addons_custom`
3. `/odoo/custom/helpdesk`
4. `/odoo/custom/l10n_br_base`
5. `/odoo/custom/social`
6. `/odoo/custom/addons-whatsapp-connector`
7. `/odoo/custom/om_account_accountant`
8. `/odoo/custom/hr_attendance_pro`

---

## Serviço Systemd

**Status:** Active (running) desde 24/Ago/2025
**Service:** odoo-server.service
**Init Script:** /etc/init.d/odoo-server

### Processos Ativos
- 1 processo principal (PID 577)
- 1 processo gevent (PID 726) - longpolling
- 14 workers (PIDs: 2356992, 2396983, 2397172, 2397521, 2397546, 2397733, 2397740, 2397773, 2401673, 2409834, 2430162, 2433920, 2463359, 2478527)
- **Memória total:** ~3.0 GB

### Comandos Úteis
```bash
# Status do serviço
sudo systemctl status odoo-server

# Restart
sudo systemctl restart odoo-server

# Logs
sudo tail -f /var/log/odoo/odoo-server.log

# Stop
sudo systemctl stop odoo-server

# Start
sudo systemctl start odoo-server
```

---

## Estrutura de Diretórios

### /odoo/odoo-server/
```
drwxr-xr-x  10 odoo odoo 4.0K Jul 14 21:16 .
drwxr-xr-x   9 odoo odoo 4.0K Oct 12  2024 ..
drwxr-xr-x   8 odoo odoo 4.0K Oct  4  2023 .git
drwxr-xr-x   2 odoo odoo 4.0K May 22  2023 .github
drwxr-xr-x 433 odoo odoo  20K Oct  4  2023 addons (433 módulos padrão)
drwxr-xr-x   3 odoo odoo 4.0K Jul 21 05:21 debian
drwxr-xr-x   3 odoo odoo 4.0K May 22  2023 doc
drwxr-xr-x  12 odoo odoo 4.0K Oct  4  2023 odoo
-rwxr-xr-x   1 odoo odoo  180 May 22  2023 odoo-bin
-rwxr-xr-x   1 odoo odoo   89 Jun 12  2024 start.sh
```

### /odoo/filestore/
```
drwxrwxr-x 5 odoo odoo    4096 May 22  2023 .
drwx------ 3 odoo odoo    4096 May 22  2023 addons
drwxrwxr-x 3 odoo odoo    4096 May 22  2023 filestore
drwx------ 2 odoo odoo 5976064 Nov 15 15:09 sessions (5.7 GB!)
```

**IMPORTANTE:** O diretório `sessions` está com 5.7 GB - considerar limpeza periódica

---

## Logs

**Arquivo principal:** `/var/log/odoo/odoo-server.log`
**Nível de log:** info
**Log DB:** Habilitado (log_db = True)
**Log DB Level:** info

---

## Backup Crítico

### Arquivos Essenciais para Backup
1. **Configuração:** `/etc/odoo-server.conf`
2. **Módulos Custom:** `/odoo/custom/`
3. **Filestore:** `/odoo/filestore/filestore/`
4. **Banco de Dados:** PostgreSQL database `realcred`

### Comando de Backup do BD
```bash
sudo -u postgres pg_dump realcred > realcred_backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## Troubleshooting

### Odoo não inicia
1. Verificar logs: `sudo tail -f /var/log/odoo/odoo-server.log`
2. Verificar PostgreSQL: `sudo systemctl status postgresql@12-main`
3. Verificar permissões: owner deve ser `odoo:odoo`

### Erro de memória
- Verificar workers: pode reduzir de 9 para 6
- Verificar limit_memory_hard e limit_memory_soft

### Workers não respondem
```bash
sudo systemctl restart odoo-server
```

### Sessões acumuladas
```bash
# Limpar sessões antigas (cuidado!)
sudo find /odoo/filestore/sessions -type f -mtime +7 -delete
```
