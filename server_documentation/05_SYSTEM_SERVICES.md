# Sistema e Serviços - odoo-rc

**Data da documentação:** 2025-11-15
**Servidor:** odoo-rc (35.199.79.229)

---

## Sistema Operacional

```
OS: Ubuntu 20.04.6 LTS (Focal Fossa)
Kernel: Linux 5.15.0-1083-gcp
Arch: x86_64
Platform: Google Cloud Platform (GCP)
```

---

## Recursos do Sistema

### Memória RAM
```
Total: 12 GB
Used: 3.9 GB (33%)
Free: 276 MB
Shared: 4.1 GB
Buffer/Cache: 7.5 GB
Available: 3.3 GB
Swap: 0 GB (não configurado)
```

**⚠️ ATENÇÃO:** Swap desabilitado - pode causar OOM em picos de memória!

### Disco
```
Filesystem: /dev/root
Size: 291 GB
Used: 156 GB (54%)
Available: 136 GB
```

**Status:** Uso moderado, ainda há espaço disponível.

---

## Serviços Systemd Ativos (Running)

### Aplicações Principais

| Serviço | Descrição | Status |
|---------|-----------|--------|
| **odoo-server.service** | Odoo ERP (9 workers + gevent) | ✅ Active |
| **postgresql@12-main.service** | PostgreSQL 12 Main | ✅ Active |
| **postgresql@12-test.service** | PostgreSQL 12 Test | ✅ Active |
| **nginx.service** | Web Server / Reverse Proxy | ✅ Active |

### Containers e Virtualização

| Serviço | Descrição | Status |
|---------|-----------|--------|
| **docker.service** | Docker Engine | ✅ Active |
| **containerd.service** | Container Runtime | ✅ Active |

### Google Cloud Services

| Serviço | Descrição | Status |
|---------|-----------|--------|
| **google-guest-agent** | GCP Guest Agent | ✅ Active |
| **google-osconfig-agent** | GCP OS Config Agent | ✅ Active |
| **google-cloud-ops-agent-fluent-bit** | GCP Logging Agent | ✅ Active |
| **google-cloud-ops-agent-opentelemetry-collector** | GCP Metrics Agent | ✅ Active |
| **google-cloud-ops-agent-diagnostics** | GCP Diagnostics | ✅ Active |

### Sistema Base

| Serviço | Descrição | Status |
|---------|-----------|--------|
| **ssh.service** | OpenSSH Server | ✅ Active |
| **cron.service** | Cron Daemon | ✅ Active |
| **rsyslog.service** | System Logging | ✅ Active |
| **systemd-networkd** | Network Management | ✅ Active |
| **systemd-resolved** | DNS Resolution | ✅ Active |
| **chrony.service** | NTP Client/Server | ✅ Active |
| **unattended-upgrades** | Auto Security Updates | ✅ Active |

### Outros

| Serviço | Descrição | Status |
|---------|-----------|--------|
| **snapd.service** | Snap Package Manager | ✅ Active |
| **accounts-daemon** | User Accounts Service | ✅ Active |
| **atd.service** | Deferred Execution Scheduler | ✅ Active |
| **polkit.service** | Authorization Manager | ✅ Active |
| **dbus.service** | Message Bus | ✅ Active |

**Total:** 33 serviços ativos

---

## Dependências Python (pip3)

### Total de Pacotes: 100+

### Categorias Principais

#### Fiscal Brasil (erpbrasil)
```
erpbrasil.assinatura  1.6.0      # Assinatura digital
erpbrasil.base        2.3.0      # Base fiscal Brasil
erpbrasil.edoc        2.3.1      # Documentos eletrônicos
erpbrasil.edoc.pdf    1.1.0      # PDFs fiscais
erpbrasil.transmissao 1.0.0      # Transmissão SEFAZ
nfelib                1.3.1      # Nota Fiscal Eletrônica
```

#### Odoo Core
```
Babel            2.9.1       # Internacionalização
lxml             4.6.5       # XML processing
Pillow           9.0.1       # Imagens
passlib          1.7.3       # Hashing senhas
polib            1.1.0       # Traduções .po
Jinja2           2.11.3      # Templates
MarkupSafe       1.1.0       # Safe strings
Werkzeug         (via requirements)
psycopg2         (binary for PostgreSQL)
reportlab        (PDF generation)
```

#### Web & HTTP
```
gevent           20.9.0      # Async networking (longpolling)
greenlet         0.4.17      # Coroutines
requests         (via python3-requests)
urllib3          (via python3-urllib3)
httplib2         0.14.0      # HTTP library
h11              0.14.0      # HTTP/1.1 protocol
beautifulsoup4   4.12.2      # HTML parsing
html2text        2020.1.16   # HTML to text
```

#### Certificados SSL / Segurança
```
certbot          0.40.0      # Let's Encrypt client
certbot-nginx    0.40.0      # Nginx plugin
acme             1.1.0       # ACME protocol
josepy           1.2.0       # JOSE protocol
cryptography     38.0.4      # Crypto primitives
bcrypt           4.0.1       # Password hashing
paramiko         3.1.0       # SSH2
```

#### Cloud Storage
```
boto3            1.26.137    # AWS SDK
botocore         1.29.137    # AWS Core
dropbox          11.36.0     # Dropbox API
pysftp           (SFTP)      # SFTP client
```

#### Localização Brasil
```
brazilcep        6.0.0       # API CEP
phonenumbers     8.13.11     # Phone validation
num2words        0.5.6       # Números por extenso
workalendar      (holidays)  # Calendário/feriados
convertdate      2.4.0       # Conversão datas
lunardate        0.2.0       # Datas lunares
```

#### Comunicação
```
flanker          0.9.11      # Email parsing
dnspython        2.3.0       # DNS toolkit
```

#### Pagamentos
```
ofxparse         0.19        # OFX parsing (banking)
```

#### Testing & Development
```
odoo-test-helper 2.1.0       # Odoo testing
mock             3.0.5       # Mocking
pexpect          4.6.0       # Expect-like
selenium         (browser automation)
freezegun        0.3.15      # Time mocking
```

#### Automação Web
```
selenium         (via requirements)
async-generator  1.10        # Async iteration
outcome          1.2.0       # Trio outcomes
exceptiongroup   1.1.1       # Exception groups
```

#### Utilities
```
Click            7.0         # CLI framework
colorama         0.4.3       # Terminal colors
tqdm             (via requirements)  # Progress bars
simplejson       (via python3-simplejson)
PyYAML           (via python3-yaml)
python-dateutil  (date utilities)
pytz             (timezones)
```

#### Data Processing
```
ebaysdk          2.1.5       # eBay API
isodate          0.6.1       # ISO 8601 dates
jsonpatch        1.22        # JSON patching
jsonpointer      2.0         # JSON pointer
jsonschema       3.2.0       # JSON validation
```

#### Templates & Rendering
```
libsass          0.18.0      # SASS compiler
Genshi           0.7.7       # Template engine
```

#### Diversos
```
decorator        4.4.2       # Decorators
defusedxml       0.7.1       # Safe XML parsing
expiringdict     1.2.2       # Expiring dicts
future           0.18.2      # Python 2/3 compatibility
vobject          (via requirements)  # vCard/iCal
```

---

## Pacotes Sistema (APT)

### Python
```
python3                    3.8.2
python3.8                  3.8.10
python3-dev                3.8.2
python3-pip                20.0.2
python3-venv               3.8.2
python3-setuptools         45.2.0
```

### PostgreSQL
```
postgresql                 12+214ubuntu0.1
postgresql-12              12.22
postgresql-client-12       12.22
postgresql-server-dev-12   12.22
postgresql-common          214ubuntu0.1
```

### Nginx
```
nginx                      1.18.0
nginx-core                 1.18.0
nginx-common               1.18.0
libnginx-mod-http-image-filter
libnginx-mod-http-xslt-filter
libnginx-mod-mail
libnginx-mod-stream
```

### Docker
```
docker-ce                  27.2.1
docker-ce-cli              27.2.1
docker-compose-plugin      2.29.2
docker-buildx-plugin       0.16.2
docker-ce-rootless-extras  27.2.1
containerd                 (via docker)
```

### Git
```
git                        2.25.1
git-man                    2.25.1
```

### Certbot / SSL
```
certbot                    0.40.0 (Python)
python3-certbot            0.40.0
python3-certbot-nginx      0.40.0
python3-acme               1.1.0
```

### Build Tools
```
build-essential            (gcc, g++, make)
libpq-dev                  (PostgreSQL dev)
libsasl2-dev               (SASL)
libldap2-dev               (LDAP)
libssl-dev                 (OpenSSL)
```

---

## Processos Principais

### Por Consumo de Memória

| Processo | Memória | Descrição |
|----------|---------|-----------|
| PostgreSQL | ~6.3 GB | Database (65+ conexões) |
| Odoo | ~3.0 GB | ERP (9 workers + gevent) |
| Nginx | ~78 MB | Web server (4 workers) |
| Docker | Variável | Container engine |
| System | ~1.6 GB | OS + services |

---

## Cron Jobs

### Ver cron jobs ativos
```bash
# Usuário root
sudo crontab -l

# Usuário odoo
sudo -u odoo crontab -l

# Todos os usuários
for user in $(cut -f1 -d: /etc/passwd); do
    echo "=== Cron for $user ==="
    sudo crontab -u $user -l 2>/dev/null
done
```

---

## Comandos Úteis

### Gerenciar Serviços

```bash
# Ver todos os serviços
systemctl list-units --type=service

# Ver serviços ativos
systemctl list-units --type=service --state=running

# Status de serviço específico
sudo systemctl status odoo-server
sudo systemctl status postgresql@12-main
sudo systemctl status nginx

# Restart serviços
sudo systemctl restart odoo-server
sudo systemctl restart postgresql@12-main
sudo systemctl restart nginx

# Habilitar/desabilitar auto-start
sudo systemctl enable odoo-server
sudo systemctl disable nome-servico
```

### Monitorar Recursos

```bash
# Uso de memória
free -h

# Uso de disco
df -h

# Top processos
top
htop (se instalado)

# Processos por memória
ps aux --sort=-%mem | head -20

# Processos por CPU
ps aux --sort=-%cpu | head -20

# Ver I/O disk
iostat -x 1

# Network
netstat -tulpn
ss -tulpn
```

### Ver Logs

```bash
# Logs do sistema
sudo journalctl -xe
sudo journalctl -u odoo-server -f
sudo journalctl -u nginx -f
sudo journalctl -u postgresql@12-main -f

# Rsyslog
sudo tail -f /var/log/syslog
sudo tail -f /var/log/auth.log
```

---

## Docker

### Status
```bash
# Ver containers rodando
sudo docker ps

# Ver todas images
sudo docker images

# Ver uso de disco
sudo docker system df

# Ver networks
sudo docker network ls
```

### Limpar Docker
```bash
# Remover containers parados
sudo docker container prune

# Remover images não usadas
sudo docker image prune -a

# Limpar tudo (cuidado!)
sudo docker system prune -a
```

---

## Troubleshooting

### Sistema lento

1. Verificar memória: `free -h`
2. Verificar CPU: `top`
3. Verificar disco: `df -h` e `iostat`
4. Ver processos: `ps aux --sort=-%mem`

### Disco cheio

```bash
# Ver uso por diretório
du -sh /* 2>/dev/null | sort -rh | head -20

# Limpar logs antigos
sudo journalctl --vacuum-time=7d

# Limpar cache apt
sudo apt clean

# Limpar sessions Odoo
sudo find /odoo/filestore/sessions -type f -mtime +7 -delete
```

### Memória esgotada

1. Verificar: `free -h`
2. Ver processos: `ps aux --sort=-%mem`
3. Considerar reduzir workers Odoo
4. Adicionar swap (se necessário)

### Serviço não inicia

```bash
# Ver status
sudo systemctl status nome-servico

# Ver logs
sudo journalctl -xe -u nome-servico

# Verificar config
sudo nome-servico -t  # Ex: nginx -t
```

---

## Manutenção Regular

### Diária
- Verificar espaço em disco
- Verificar logs de erro

### Semanal
- Limpar sessions antigas
- Verificar backups
- Atualizar certificados SSL (se necessário)

### Mensal
- Limpar logs antigos
- VACUUM PostgreSQL
- Verificar atualizações de segurança
- Revisar uso de recursos

---

## Recomendações

1. **Configurar SWAP** - Adicionar 4-8 GB para evitar OOM
2. **Monitoramento** - Configurar alertas de disco/memória/CPU
3. **Logrotate** - Garantir rotação de logs Odoo/Nginx
4. **Backup automatizado** - Verificar auto_backup_odoo funcionando
5. **Atualizações** - Manter sistema atualizado (unattended-upgrades ativo)
6. **Firewall** - Verificar regras ufw/iptables
7. **Fail2ban** - Considerar instalar para proteção SSH

---

## Comandos de Emergência

### Sistema travado
```bash
# Ver load average
uptime

# Matar processo específico
sudo kill -9 PID

# Matar Odoo (emergência)
sudo systemctl stop odoo-server
sudo pkill -9 -f odoo-bin

# Reiniciar serviços principais
sudo systemctl restart odoo-server nginx postgresql@12-main
```

### Recuperação de espaço urgente
```bash
# Limpar journals
sudo journalctl --vacuum-size=500M

# Limpar sessions Odoo
sudo rm -rf /odoo/filestore/sessions/*

# Limpar cache apt
sudo apt clean
sudo apt autoclean
sudo apt autoremove
```
