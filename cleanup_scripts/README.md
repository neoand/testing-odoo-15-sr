# Scripts de Limpeza de Dados Antigos - Odoo realcred

**Objetivo:** Deletar dados criados até 31/12/2024
**Potencial de Recuperação:** 65-80 GB

---

## 📋 ORDEM DE EXECUÇÃO

### ⚠️ ANTES DE COMEÇAR

**OBRIGATÓRIO:**
```bash
# 1. Fazer backup completo
sudo -u postgres pg_dump -Fc realcred > ~/backup_before_cleanup_$(date +%Y%m%d).dump
sudo tar -czf ~/filestore_backup_$(date +%Y%m%d).tar.gz /odoo/filestore/

# 2. Verificar backups
ls -lh ~/backup_before_cleanup_*
ls -lh ~/filestore_backup_*
```

**NÃO PROSSIGA SEM BACKUP!**

---

## 🚀 EXECUÇÃO PASSO A PASSO

### Semana 1: TESTE (100 registros)

```bash
# Executar script de teste
ssh odoo-rc
sudo -u postgres psql realcred -f 01_test_cleanup_100_records.sql
```

**Aguardar 24-48h e verificar se Odoo funciona normalmente!**

---

### Semana 2: LIMPEZA EM LOTES (após teste bem-sucedido)

```bash
# Deletar attachments de emails antigos (em lotes de 1000)
ssh odoo-rc
sudo -u postgres psql realcred -f 02_cleanup_mail_attachments_batch.sql

# VACUUM para recuperar espaço
sudo -u postgres psql realcred -c "VACUUM ANALYZE ir_attachment;"
```

**Aguardar 7 dias sem problemas!**

---

### Semana 3: LIMPEZA DO FILESTORE

```bash
# Copiar script para servidor
scp 03_cleanup_filestore_orphans.sh odoo-rc:~/

# Executar
ssh odoo-rc
chmod +x ~/03_cleanup_filestore_orphans.sh
sudo bash ~/03_cleanup_filestore_orphans.sh
```

**Aguardar 30 dias antes de deletar backup!**

---

## 📊 SCRIPTS DISPONÍVEIS

| Script | O que faz | Duração | Downtime | Recuperação |
|--------|-----------|---------|----------|-------------|
| `01_test_cleanup_100_records.sql` | Testa deleção de 100 attachments | 1 min | Não | ~10 MB |
| `02_cleanup_mail_attachments_batch.sql` | Deleta attachments de emails antigos | 10-30 min | Não | ~20 GB |
| `03_cleanup_filestore_orphans.sh` | Limpa arquivos órfãos do filestore | 30-60 min | Não | ~60 GB |

---

## ✅ CHECKLIST DE SEGURANÇA

### Antes
- [ ] Backup do database realizado
- [ ] Backup do filestore realizado
- [ ] Teste de restauração verificado
- [ ] Usuários notificados
- [ ] Executar fora de horário de pico

### Durante
- [ ] Monitorar logs: `sudo tail -f /var/log/odoo/odoo-server.log`
- [ ] Verificar espaço em disco: `df -h`

### Após
- [ ] Testar Odoo funciona normalmente
- [ ] Executar VACUUM
- [ ] Manter backups por 30 dias

---

## 🔍 MONITORAMENTO

### Verificar progresso
```bash
# Attachments restantes
ssh odoo-rc "sudo -u postgres psql realcred -c \"
SELECT COUNT(*) FROM ir_attachment WHERE create_date <= '2024-12-31';
\""

# Espaço do filestore
ssh odoo-rc "sudo du -sh /odoo/filestore/"

# Tamanho do database
ssh odoo-rc "sudo -u postgres psql -c \"
SELECT pg_size_pretty(pg_database_size('realcred'));
\""
```

---

## 🚨 TROUBLESHOOTING

### Erro: "relation deleted_records_log does not exist"
```sql
-- Executar:
CREATE TABLE deleted_records_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    record_id INTEGER,
    record_info JSONB,
    deleted_at TIMESTAMP DEFAULT NOW()
);
```

### Erro: "Permission denied"
- Executar com `sudo -u postgres psql realcred -f script.sql`

### Restaurar backup
```bash
sudo systemctl stop odoo-server
sudo -u postgres dropdb realcred
sudo -u postgres createdb -O odoo realcred
sudo -u postgres pg_restore -d realcred ~/backup_before_cleanup_*.dump
sudo systemctl start odoo-server
```

---

## 📈 RESULTADOS ESPERADOS

### Após Completar Todas as Fases

| Métrica | Antes | Depois | Recuperação |
|---------|-------|--------|-------------|
| Database | 8.8 GB | ~2 GB | **-77%** |
| Filestore | 74 GB | ~14 GB | **-81%** |
| **TOTAL** | **~83 GB** | **~16 GB** | **~67 GB** |

---

## 📞 SUPORTE

**Documentação Completa:** `../server_documentation/10_DATA_CLEANUP_STRATEGY.md`

**Dúvidas comuns:**
- "Posso executar tudo de uma vez?" → **NÃO! Executar incrementalmente.**
- "Precisa parar o Odoo?" → **NÃO, todos os scripts são online.**
- "E se der erro?" → **Restaurar backup imediatamente.**

---

**Criado:** 2025-11-15
**Status:** Pronto para uso
**Abordagem:** Conservadora e segura
