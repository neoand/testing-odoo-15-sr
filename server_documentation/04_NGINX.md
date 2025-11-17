# Nginx - odoo-rc

**Data da documentação:** 2025-11-15
**Servidor:** odoo-rc (35.199.79.229)
**Versão:** nginx/1.18.0 (Ubuntu)

---

## Status do Serviço

- **Status:** Active (running) desde 24/Ago/2025
- **PID:** 702 (master process)
- **Worker processes:** 4 workers
- **Memória:** 78.1 MB
- **User:** www-data

### Processos
```
702     nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
2466100 nginx: worker process
2466101 nginx: worker process
2466102 nginx: worker process
2466103 nginx: worker process
```

---

## Configuração Principal (/etc/nginx/nginx.conf)

```nginx
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 768;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # SSL Settings
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    # Gzip
    gzip on;

    # Logs
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Virtual Hosts
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

---

## Sites Configurados

### Sites Enabled
- **odoo.semprereal.com** → `/etc/nginx/sites-available/odoo.semprereal.com`

### Certificados SSL (Let's Encrypt)
- **odoo.semprereal.com** - cert12.pem (renovado em 09/Nov/2025)
- **realcredtb.com** - certificado configurado

**⚠️ ATENÇÃO:** Certbot apresenta erros ao verificar certificados. Os certificados estão ativos mas a renovação automática pode falhar!

```
Error: '_RSAPublicKey' object has no attribute 'verifier'
```

---

## Configuração odoo.semprereal.com

### Server Block Principal (HTTPS - Porta 443)

```nginx
server {
    listen 443 ssl;
    server_name odoo.semprereal.com;

    # SSL Certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/odoo.semprereal.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/odoo.semprereal.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Logs
    access_log  /var/log/nginx/odoo-semprereal-access.log;
    error_log   /var/log/nginx/odoo-semprereal-error.log;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";

    # Proxy Headers
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Client-IP $remote_addr;
    proxy_set_header HTTP_X_FORWARDED_HOST $remote_addr;

    # Proxy Buffers
    proxy_buffers 16 64k;
    proxy_buffer_size 128k;

    # Timeouts
    proxy_read_timeout 900s;      # 15 minutos
    proxy_connect_timeout 900s;   # 15 minutos
    proxy_send_timeout 900s;      # 15 minutos

    # Retry logic
    proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;

    # Client settings
    client_header_buffer_size 4k;
    large_client_header_buffers 4 64k;
    client_max_body_size 0;       # Sem limite de upload

    # Gzip Compression
    gzip on;
    gzip_min_length 1100;
    gzip_buffers 4 32k;
    gzip_types text/css text/less text/plain text/xml application/xml
               application/json application/javascript application/pdf
               image/jpeg image/png;
    gzip_vary on;

    # Main location - Odoo on port 8069
    location / {
        proxy_pass http://127.0.0.1:8069;
        proxy_redirect off;
    }

    # Longpolling - Odoo on port 8072
    location /longpolling {
        proxy_pass http://127.0.0.1:8072;
    }

    # Static files caching (images, css, js)
    location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
        expires 2d;
        proxy_pass http://127.0.0.1:8069;
        add_header Cache-Control "public, no-transform";
    }

    # Static data caching (60 minutes)
    location ~ /[a-zA-Z0-9_-]*/static/ {
        proxy_cache_valid 200 302 60m;
        proxy_cache_valid 404 1m;
        proxy_buffering on;
        expires 864000;  # 10 days
        proxy_pass http://127.0.0.1:8069;
    }
}
```

### Server Blocks HTTP→HTTPS Redirect (Porta 80)

```nginx
server {
    listen 80;
    server_name odoo.semprereal.com;

    # Redirect to HTTPS
    if ($host = odoo.semprereal.com) {
        return 301 https://$host$request_uri;
    }

    return 404;
}
```

---

## Funcionalidades Configuradas

### Proxy Reverso
- **Backend Odoo:** http://127.0.0.1:8069
- **Longpolling:** http://127.0.0.1:8072
- **SSL Termination:** Nginx (HTTPS) → Odoo (HTTP local)

### Cache
- **Arquivos estáticos:** 2 dias
- **Static data:** 60 minutos (200/302), 1 minuto (404)
- **Imagens/CSS/JS:** 10 dias

### Segurança
- **HTTPS only:** Redirecionamento automático HTTP→HTTPS
- **X-Frame-Options:** SAMEORIGIN (proteção clickjacking)
- **X-XSS-Protection:** Habilitado
- **SSL/TLS:** TLSv1, TLSv1.1, TLSv1.2, TLSv1.3

### Performance
- **Gzip:** Habilitado para texto, XML, JSON, JS, CSS, PDF, imagens
- **Timeouts:** 15 minutos (para operações longas)
- **Upload:** Sem limite (client_max_body_size 0)
- **Buffers:** 16 x 64k + buffer size 128k

---

## Logs

### Access Logs
- **Geral:** `/var/log/nginx/access.log`
- **Odoo:** `/var/log/nginx/odoo-semprereal-access.log`

### Error Logs
- **Geral:** `/var/log/nginx/error.log`
- **Odoo:** `/var/log/nginx/odoo-semprereal-error.log`

### Ver logs em tempo real
```bash
# Access log Odoo
sudo tail -f /var/log/nginx/odoo-semprereal-access.log

# Error log Odoo
sudo tail -f /var/log/nginx/odoo-semprereal-error.log

# Todos os logs
sudo tail -f /var/log/nginx/*.log
```

---

## SSL/TLS - Let's Encrypt

### Certificados Ativos

**odoo.semprereal.com:**
- **Cert:** `/etc/letsencrypt/live/odoo.semprereal.com/cert.pem` → cert12.pem
- **Chain:** `/etc/letsencrypt/live/odoo.semprereal.com/chain.pem` → chain12.pem
- **Fullchain:** `/etc/letsencrypt/live/odoo.semprereal.com/fullchain.pem` → fullchain12.pem
- **Private Key:** `/etc/letsencrypt/live/odoo.semprereal.com/privkey.pem` → privkey12.pem
- **Última renovação:** 09/Nov/2025

**realcredtb.com:**
- Certificado configurado
- Detalhes em `/etc/letsencrypt/live/realcredtb.com/`

### ⚠️ PROBLEMA CRÍTICO - Renovação Certbot

**Erro identificado:**
```
'_RSAPublicKey' object has no attribute 'verifier'
```

**Impacto:**
- Certificados atuais estão válidos e funcionando
- Renovação automática pode falhar
- Certificados Let's Encrypt expiram em 90 dias

**Ação necessária:**
- Atualizar certbot/python-cryptography
- Testar renovação manual antes da expiração

### Comandos SSL

```bash
# Verificar certificados (ERRO ATUAL!)
sudo certbot certificates

# Renovar manualmente (pode funcionar)
sudo certbot renew --dry-run

# Forçar renovação
sudo certbot renew --force-renewal

# Verificar validade do certificado
echo | openssl s_client -servername odoo.semprereal.com -connect odoo.semprereal.com:443 2>/dev/null | openssl x509 -noout -dates
```

---

## Módulos Nginx Compilados

```
--with-http_ssl_module
--with-http_v2_module              (HTTP/2)
--with-http_realip_module
--with-http_auth_request_module
--with-http_stub_status_module
--with-http_gzip_static_module
--with-http_gunzip_module
--with-http_addition_module
--with-http_sub_module
--with-http_dav_module
--with-http_slice_module
--with-http_xslt_module=dynamic
--with-http_image_filter_module=dynamic
--with-stream=dynamic
--with-stream_ssl_module
--with-mail=dynamic
--with-mail_ssl_module
--with-threads
--with-pcre-jit
--with-debug
--with-compat
```

---

## Comandos Úteis

### Gerenciamento do Serviço

```bash
# Status
sudo systemctl status nginx

# Restart
sudo systemctl restart nginx

# Reload (sem downtime)
sudo systemctl reload nginx

# Stop
sudo systemctl stop nginx

# Start
sudo systemctl start nginx
```

### Testes de Configuração

```bash
# Testar configuração
sudo nginx -t

# Testar e mostrar config
sudo nginx -T

# Ver versão e módulos
nginx -V
```

### Monitoramento

```bash
# Ver worker processes
ps aux | grep nginx

# Conexões ativas
sudo netstat -tlnp | grep :443
sudo ss -tlnp | grep :443

# Logs em tempo real
sudo tail -f /var/log/nginx/odoo-semprereal-access.log
sudo tail -f /var/log/nginx/odoo-semprereal-error.log
```

---

## Troubleshooting

### Nginx não inicia

```bash
# Verificar config
sudo nginx -t

# Ver logs de erro
sudo tail -50 /var/log/nginx/error.log

# Verificar porta em uso
sudo ss -tlnp | grep :80
sudo ss -tlnp | grep :443
```

### Erro 502 Bad Gateway

**Causas comuns:**
1. Odoo não está rodando
2. Odoo não responde na porta 8069/8072
3. Timeout muito curto

**Verificar:**
```bash
# Odoo rodando?
sudo systemctl status odoo-server

# Porta 8069 escutando?
sudo ss -tlnp | grep :8069

# Testar conexão local
curl http://127.0.0.1:8069

# Ver logs Odoo
sudo tail -f /var/log/odoo/odoo-server.log
```

### SSL não funciona

```bash
# Verificar certificados
sudo certbot certificates

# Testar SSL
openssl s_client -connect odoo.semprereal.com:443 -servername odoo.semprereal.com

# Verificar permissões
ls -la /etc/letsencrypt/live/odoo.semprereal.com/
```

### Upload falha

- Verificar `client_max_body_size` (atualmente: 0 = ilimitado)
- Verificar limite no Odoo também

### Performance lenta

1. Verificar cache habilitado
2. Verificar gzip habilitado
3. Ajustar worker_connections
4. Verificar timeouts

---

## Melhorias Recomendadas

### 1. Resolver problema Certbot
```bash
# Atualizar certbot
sudo apt update
sudo apt upgrade certbot python3-certbot-nginx

# Ou reinstalar
sudo apt remove certbot python3-certbot-nginx
sudo apt install certbot python3-certbot-nginx
```

### 2. Configurar renovação automática
```bash
# Adicionar cron job
sudo crontab -e

# Renovar semanalmente
0 3 * * 0 /usr/bin/certbot renew --quiet && /usr/sbin/nginx -s reload
```

### 3. Hardening SSL
```nginx
# Desabilitar TLS 1.0 e 1.1 (deprecated)
ssl_protocols TLSv1.2 TLSv1.3;

# Ciphers seguros
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:...';

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 4. Rate Limiting
```nginx
# Prevenir DDoS
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;

location / {
    limit_req zone=one burst=20 nodelay;
    proxy_pass http://127.0.0.1:8069;
}
```

### 5. Monitoramento
```nginx
# Habilitar status page
location /nginx_status {
    stub_status on;
    access_log off;
    allow 127.0.0.1;
    deny all;
}
```

---

## Atenção - Pontos Críticos

1. **⚠️ Certbot quebrado** - Renovação automática pode falhar!
2. **Timeouts longos** - 15 minutos pode ser excessivo
3. **Upload ilimitado** - client_max_body_size 0 pode causar problemas
4. **TLS 1.0/1.1** - Deprecados, devem ser desabilitados
5. **Sem rate limiting** - Vulnerável a ataques DDoS
6. **Sem HSTS** - Browsers podem tentar HTTP primeiro

---

## Backup

### Arquivos para backup

```bash
# Configurações
/etc/nginx/nginx.conf
/etc/nginx/sites-available/odoo.semprereal.com
/etc/nginx/sites-enabled/

# Certificados SSL
/etc/letsencrypt/

# Comando backup
sudo tar -czf nginx_backup_$(date +%Y%m%d).tar.gz \
    /etc/nginx/ \
    /etc/letsencrypt/
```

### Restore

```bash
# Restaurar configuração
sudo tar -xzf nginx_backup_YYYYMMDD.tar.gz -C /

# Testar
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

---

## Referências

- Nginx docs: https://nginx.org/en/docs/
- SSL Labs test: https://www.ssllabs.com/ssltest/
- Let's Encrypt: https://letsencrypt.org/
- Odoo nginx: https://www.odoo.com/documentation/15.0/administration/install/deploy.html
