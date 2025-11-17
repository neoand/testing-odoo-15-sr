# Documentação Completa do Servidor odoo-rc

**Servidor:** odoo-rc (35.199.79.229)
**Domínio:** odoo.semprereal.com
**Sistema:** Ubuntu 20.04.6 LTS
**Data da documentação:** 2025-11-15

---

## 📋 Índice da Documentação

### Configuração e Infraestrutura
1. **[00_EXECUTIVE_SUMMARY.md](00_EXECUTIVE_SUMMARY.md)** - Sumário executivo do servidor
2. **[01_ODOO_CONFIGURATION.md](01_ODOO_CONFIGURATION.md)** - Configurações do Odoo
3. **[02_CUSTOM_MODULES.md](02_CUSTOM_MODULES.md)** - Módulos customizados
4. **[03_POSTGRESQL.md](03_POSTGRESQL.md)** - PostgreSQL e bancos de dados
5. **[04_NGINX.md](04_NGINX.md)** - Nginx e configurações SSL
6. **[05_SYSTEM_SERVICES.md](05_SYSTEM_SERVICES.md)** - Sistema, serviços e dependências

### Otimizações e Performance
7. **[06_POSTGRESQL_OPTIMIZATION_PLAN.md](06_POSTGRESQL_OPTIMIZATION_PLAN.md)** - Plano de otimização PostgreSQL
8. **[07_OPTIMIZATION_RESULTS.md](07_OPTIMIZATION_RESULTS.md)** - Resultados Fase 1
9. **[08_PHASE2_RESULTS.md](08_PHASE2_RESULTS.md)** - Resultados Fase 2
10. **[09_COMPLETE_OPTIMIZATION_RESULTS.md](09_COMPLETE_OPTIMIZATION_RESULTS.md)** - Resultados completos (3 fases)

### Data Cleanup
11. **[10_DATA_CLEANUP_STRATEGY.md](10_DATA_CLEANUP_STRATEGY.md)** - Estratégia de limpeza de dados
12. **[11_DATA_CLEANUP_FINAL_RESULTS.md](11_DATA_CLEANUP_FINAL_RESULTS.md)** - Resultados da limpeza (201K registros deletados)

### Integrações
13. **[12_KOLMEYA_SMS_INTEGRATION.md](12_KOLMEYA_SMS_INTEGRATION.md)** - Integração Kolmeya SMS (credenciais, API, plano)
14. **[13_KOLMEYA_SEMPREREAL_IMPLEMENTATION.md](13_KOLMEYA_SEMPREREAL_IMPLEMENTATION.md)** - Implementação focada em SempreReal (casos de uso, modelos)
15. **[14_KOLMEYA_SMS_TEST_RESULTS.md](14_KOLMEYA_SMS_TEST_RESULTS.md)** - Resultados dos testes reais de SMS
16. **[15_KOLMEYA_API_COMPLETE_DISCOVERY.md](15_KOLMEYA_API_COMPLETE_DISCOVERY.md)** - Descoberta completa da API Kolmeya (15 endpoints testados)
17. **[16_KOLMEYA_ARCHITECTURE_RECOMMENDATIONS.md](16_KOLMEYA_ARCHITECTURE_RECOMMENDATIONS.md)** - Recomendações de arquitetura (baseadas em OCA e best practices)

### Backups
18. **[17_BACKUP_PRE_SMS_IMPLEMENTATION.md](17_BACKUP_PRE_SMS_IMPLEMENTATION.md)** - Backup completo pré-implementação SMS (1.1 GB, 2025-11-15)

---

## 🚨 Informações Críticas

### Credenciais e Senhas

**⚠️ PROTEGER ESTAS INFORMAÇÕES!**

#### Odoo e Database
- **Odoo Admin Password:** `HI5Rdi5UikL9jjLy`
- **Database:** `realcred` (owner: odoo)
- **PostgreSQL Users:** postgres, odoo (superuser), replicador

#### Kolmeya SMS API
- **URL:** https://kolmeya.com.br/
- **Usuário:** SUPERVISAO@REALCREDEMPRESTIMO.COM.BR
- **Senha:** Anca741@
- **API Token:** Bearer 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY
- **Docs:** https://kolmeya.com.br/docs/api/

### Serviços Principais

| Serviço | Porta | Status | Auto-start |
|---------|-------|--------|------------|
| Odoo | 8069 (local) | ✅ Running | Sim |
| Odoo Longpolling | 8072 (local) | ✅ Running | Sim |
| Nginx | 80, 443 | ✅ Running | Sim |
| PostgreSQL 12-main | 5432 | ✅ Running | Sim |

### Acesso SSH

```bash
# Configurado em ~/.ssh/config
Host odoo-rc
    HostName 35.199.79.229
    User andlee21
    IdentityFile ~/.ssh/id_ed25519
```

**Conectar:**
```bash
ssh odoo-rc
```

---

## 🆘 Recuperação de Desastres

### Cenário 1: Servidor Parou Completamente

```bash
# 1. Conectar ao servidor
ssh odoo-rc

# 2. Verificar status dos serviços
sudo systemctl status postgresql@12-main
sudo systemctl status odoo-server
sudo systemctl status nginx

# 3. Iniciar serviços na ordem correta
sudo systemctl start postgresql@12-main
sleep 5
sudo systemctl start odoo-server
sudo systemctl start nginx

# 4. Verificar logs para erros
sudo tail -f /var/log/odoo/odoo-server.log
sudo tail -f /var/log/nginx/error.log
```

### Cenário 2: Odoo Não Responde (502 Bad Gateway)

```bash
# 1. Verificar se Odoo está rodando
sudo systemctl status odoo-server

# 2. Verificar porta 8069
sudo ss -tlnp | grep 8069

# 3. Se não está rodando, iniciar
sudo systemctl restart odoo-server

# 4. Se está travado, forçar restart
sudo systemctl stop odoo-server
sudo pkill -9 -f odoo-bin
sudo systemctl start odoo-server

# 5. Monitorar logs
sudo tail -f /var/log/odoo/odoo-server.log
```

### Cenário 3: Banco de Dados Corrompido

```bash
# 1. Parar Odoo
sudo systemctl stop odoo-server

# 2. Conectar ao PostgreSQL
sudo -u postgres psql realcred

# 3. Verificar integridade
VACUUM VERBOSE;
REINDEX DATABASE realcred;

# 4. Se houver corrupção, restaurar do backup
sudo -u postgres pg_restore -d realcred /path/to/backup.dump

# 5. Reiniciar Odoo
sudo systemctl start odoo-server
```

### Cenário 4: Disco Cheio

```bash
# 1. Verificar uso
df -h
du -sh /odoo/* | sort -rh

# 2. Limpar sessions (5.7 GB!)
sudo rm -rf /odoo/filestore/sessions/*

# 3. Limpar logs antigos
sudo journalctl --vacuum-time=7d
sudo find /var/log -name "*.log" -mtime +30 -delete

# 4. Limpar cache apt
sudo apt clean
sudo apt autoremove

# 5. Vacuum PostgreSQL para recuperar espaço
sudo -u postgres psql realcred -c "VACUUM FULL VERBOSE;"
```

### Cenário 5: SSL Expirado

```bash
# 1. Verificar certificados
sudo certbot certificates

# 2. Renovar (se certbot funcionar)
sudo certbot renew --force-renewal

# 3. Se certbot quebrado, reinstalar
sudo apt remove certbot python3-certbot-nginx
sudo apt install certbot python3-certbot-nginx

# 4. Obter novo certificado
sudo certbot --nginx -d odoo.semprereal.com

# 5. Reload nginx
sudo systemctl reload nginx
```

---

## 💾 Backup e Restore

### Backup Completo

```bash
# 1. Criar diretório de backup
mkdir -p ~/backups/$(date +%Y%m%d)
cd ~/backups/$(date +%Y%m%d)

# 2. Backup PostgreSQL
sudo -u postgres pg_dump -Fc realcred > realcred_$(date +%Y%m%d_%H%M%S).dump

# 3. Backup filestore
sudo tar -czf filestore_$(date +%Y%m%d).tar.gz /odoo/filestore/

# 4. Backup módulos custom
sudo tar -czf custom_$(date +%Y%m%d).tar.gz /odoo/custom/

# 5. Backup configurações
sudo tar -czf configs_$(date +%Y%m%d).tar.gz \
    /etc/odoo-server.conf \
    /etc/nginx/ \
    /etc/postgresql/ \
    /etc/letsencrypt/

# 6. Download para local (do seu Mac)
scp -r odoo-rc:~/backups/$(date +%Y%m%d) ~/odoo_backups/
```

### Restore Completo

```bash
# 1. Parar serviços
sudo systemctl stop odoo-server
sudo systemctl stop nginx

# 2. Restaurar database
sudo -u postgres dropdb realcred
sudo -u postgres createdb -O odoo realcred
sudo -u postgres pg_restore -d realcred realcred_backup.dump

# 3. Restaurar filestore
sudo rm -rf /odoo/filestore/*
sudo tar -xzf filestore_backup.tar.gz -C /
sudo chown -R odoo:odoo /odoo/filestore

# 4. Restaurar módulos custom
sudo rm -rf /odoo/custom/*
sudo tar -xzf custom_backup.tar.gz -C /
sudo chown -R odoo:odoo /odoo/custom

# 5. Restaurar configurações
sudo tar -xzf configs_backup.tar.gz -C /

# 6. Reiniciar serviços
sudo systemctl start postgresql@12-main
sleep 5
sudo systemctl start odoo-server
sudo systemctl start nginx

# 7. Verificar
curl https://odoo.semprereal.com
```

---

## ⚡ Comandos Rápidos

### Status Geral

```bash
# Ver todos os serviços principais
sudo systemctl status odoo-server postgresql@12-main nginx

# Ver uso de recursos
free -h && df -h

# Ver processos principais
ps aux | grep -E 'odoo|postgres|nginx' | grep -v grep
```

### Restart Completo

```bash
# Ordem correta de restart
sudo systemctl restart postgresql@12-main && \
sleep 5 && \
sudo systemctl restart odoo-server && \
sudo systemctl restart nginx && \
echo "✅ All services restarted"
```

### Ver Logs em Tempo Real

```bash
# Odoo
sudo tail -f /var/log/odoo/odoo-server.log

# Nginx access
sudo tail -f /var/log/nginx/odoo-semprereal-access.log

# Nginx error
sudo tail -f /var/log/nginx/odoo-semprereal-error.log

# PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-12-main.log

# Sistema
sudo journalctl -f
```

### Verificar Conectividade

```bash
# Testar Odoo local
curl http://127.0.0.1:8069

# Testar Nginx local
curl http://127.0.0.1:80

# Testar HTTPS
curl https://odoo.semprereal.com

# Testar PostgreSQL
sudo -u postgres psql -c "SELECT version();"
```

---

## 🔍 Troubleshooting Comum

### Problema: Erro 502 Bad Gateway

**Causa:** Odoo não está respondendo

**Solução:**
```bash
sudo systemctl restart odoo-server
sudo tail -f /var/log/odoo/odoo-server.log
```

### Problema: Slow Performance

**Causa:** Memória/CPU/Disco

**Solução:**
```bash
# Verificar recursos
top
free -h
df -h

# Reduzir workers Odoo (se necessário)
sudo nano /etc/odoo-server.conf
# workers = 9 -> workers = 6
sudo systemctl restart odoo-server

# Limpar cache
sudo -u postgres psql realcred -c "VACUUM ANALYZE;"
```

### Problema: SSL Warning/Error

**Causa:** Certificado expirado ou certbot quebrado

**Solução:**
```bash
# Renovar certificado
sudo certbot renew

# Se falhar, ver seção "Cenário 5: SSL Expirado"
```

### Problema: Database Connection Error

**Causa:** PostgreSQL não está rodando ou conexão falhou

**Solução:**
```bash
sudo systemctl status postgresql@12-main
sudo systemctl restart postgresql@12-main

# Verificar conexões
sudo -u postgres psql -c "\conninfo"
```

### Problema: Upload Falha

**Causa:** Limite de tamanho

**Solução:**
```bash
# Nginx já está com client_max_body_size 0 (ilimitado)
# Verificar Odoo
grep -i "limit_memory" /etc/odoo-server.conf
```

---

## 📊 Monitoramento

### Métricas Importantes

```bash
# Conexões PostgreSQL
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Workers Odoo ativos
ps aux | grep odoo-bin | wc -l

# Uso de disco por tabela (top 10)
sudo -u postgres psql realcred -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;"

# Tamanho do database
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('realcred'));"
```

### Alertas Recomendados

- ⚠️ Disco > 80% usado
- ⚠️ Memória > 90% usada
- ⚠️ CPU > 80% por 5+ minutos
- ⚠️ PostgreSQL > 180 conexões
- ⚠️ SSL expira em < 30 dias
- ⚠️ Serviços críticos down

---

## ⚠️ Problemas Conhecidos

### 1. Certbot Quebrado
**Status:** ⚠️ CRÍTICO
**Erro:** `'_RSAPublicKey' object has no attribute 'verifier'`
**Impacto:** Renovação automática SSL pode falhar
**Ação:** Atualizar certbot antes da expiração do certificado

### 2. Sessions 5.7 GB
**Status:** ⚠️ ATENÇÃO
**Local:** `/odoo/filestore/sessions/`
**Impacto:** Desperdício de disco
**Ação:** Limpar sessions antigas periodicamente

### 3. Swap Desabilitado
**Status:** ⚠️ ATENÇÃO
**Impacto:** Pode causar OOM em picos de memória
**Ação:** Considerar adicionar 4-8 GB swap

### 4. Tabelas Grandes
**Status:** ℹ️ INFO
**Tabelas:** ir_attachment (3.6GB), mail_message (2.3GB)
**Impacto:** Crescimento do database
**Ação:** Arquivar dados antigos

### 5. Replicação PostgreSQL Aberta
**Status:** 🔴 SEGURANÇA
**Config:** `host replication replicador 0.0.0.0/0 md5`
**Impacto:** Qualquer IP pode tentar replicar
**Ação:** Restringir IPs no pg_hba.conf

### 6. TLS 1.0/1.1 Habilitado
**Status:** ℹ️ INFO
**Impacto:** Protocolos deprecados
**Ação:** Desabilitar, manter apenas TLS 1.2/1.3

---

## 📞 Contatos e Recursos

### Documentação Oficial
- **Odoo 15:** https://www.odoo.com/documentation/15.0/
- **PostgreSQL 12:** https://www.postgresql.org/docs/12/
- **Nginx:** https://nginx.org/en/docs/

### Logs Importantes
```
/var/log/odoo/odoo-server.log
/var/log/nginx/odoo-semprereal-access.log
/var/log/nginx/odoo-semprereal-error.log
/var/log/postgresql/postgresql-12-main.log
/var/log/syslog
```

### Arquivos de Configuração
```
/etc/odoo-server.conf
/etc/nginx/sites-available/odoo.semprereal.com
/etc/postgresql/12/main/postgresql.conf
/etc/postgresql/12/main/pg_hba.conf
```

---

## 🔄 Manutenção Programada

### Diária (Automática)
- ✅ Backup automático (auto_backup_odoo)
- ✅ Autovacuum PostgreSQL
- ✅ Unattended security updates

### Semanal (Manual)
- [ ] Verificar espaço em disco
- [ ] Revisar logs de erro
- [ ] Limpar sessions antigas
- [ ] Verificar certificado SSL

### Mensal (Manual)
- [ ] Backup completo manual
- [ ] VACUUM FULL PostgreSQL (se necessário)
- [ ] Reindex database
- [ ] Atualizar dependências Python
- [ ] Revisar uso de recursos
- [ ] Testar restore de backup

### Trimestral (Manual)
- [ ] Arquivar dados antigos
- [ ] Revisar módulos instalados
- [ ] Atualizar documentação
- [ ] Testar disaster recovery

---

## 📝 Histórico de Mudanças

### 2025-11-15
- ✅ Documentação completa criada
- ✅ SSH configurado para acesso remoto (andlee21@...)
- ℹ️ Identificado problema certbot
- ℹ️ Identificado sessions 5.7 GB

---

## 🎯 Próximos Passos Recomendados

1. **Urgente:**
   - [ ] Resolver problema certbot
   - [ ] Limpar sessions antigas (5.7 GB)
   - [ ] Restringir replicação PostgreSQL

2. **Importante:**
   - [ ] Configurar swap (4-8 GB)
   - [ ] Configurar monitoramento automático
   - [ ] Desabilitar TLS 1.0/1.1
   - [ ] Configurar rate limiting Nginx

3. **Desejável:**
   - [ ] Arquivar ir_attachment antigos
   - [ ] Arquivar mail_message antigos
   - [ ] Configurar HSTS
   - [ ] Implementar fail2ban

---

## 💡 Notas Finais

Esta documentação foi gerada automaticamente em 2025-11-15 e reflete o estado atual do servidor **odoo-rc**.

**Mantenha esta documentação atualizada** sempre que fizer mudanças significativas no servidor.

**Em caso de emergência**, siga os procedimentos na seção "Recuperação de Desastres" acima.

**Para qualquer dúvida**, consulte os arquivos de documentação detalhada listados no índice.

---

**Documentação gerada por:** Claude Code
**Data:** 2025-11-15
**Versão:** 1.0
