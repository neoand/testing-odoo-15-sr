# Backup Pre-SMS Implementation

**Data:** 2025-11-15 15:34
**Localização Servidor:** `/home/andlee21/backups/pre_sms_implementation_20251115_153111/`
**Tamanho Total:** 1.1 GB
**Status:** ✅ COMPLETO

---

## 📦 Conteúdo do Backup

### ✅ Arquivos Incluídos

| Arquivo | Tamanho | Descrição |
|---------|---------|-----------|
| `realcred_database.dump` | 558 MB | PostgreSQL dump completo (formato custom -Fc) |
| `custom_modules.tar.gz` | 499 MB | Todos os módulos custom (8072 arquivos) |
| `odoo-server.conf` | 994 bytes | Configuração do Odoo |
| `README_BACKUP.md` | 2 KB | Documentação do backup |

**Total:** ~1.1 GB

### ❌ NÃO Incluído

- **Filestore** (`/odoo/filestore/` - 73 GB)
  - Muito grande para backup rápido
  - Não será modificado pela implementação SMS
  - Permanece intacto no servidor

---

## 🔄 Como Fazer Rollback Completo

Se algo der errado e você precisar voltar **EXATAMENTE** ao estado anterior:

```bash
# 1. Conectar ao servidor
ssh odoo-rc

# 2. Ir para diretório de backup
cd /home/andlee21/backups/pre_sms_implementation_20251115_153111/

# 3. Parar Odoo
sudo systemctl stop odoo-server

# 4. Restaurar Database
sudo -u postgres dropdb realcred
sudo -u postgres createdb -O odoo realcred
sudo -u postgres pg_restore -d realcred realcred_database.dump

# 5. Restaurar Módulos Custom (ATENÇÃO: sobrescreve tudo!)
sudo rm -rf /odoo/custom/*
sudo tar -xzf custom_modules.tar.gz -C /odoo/
sudo chown -R odoo:odoo /odoo/custom/

# 6. Restaurar Configuração
sudo cp odoo-server.conf /etc/odoo-server.conf

# 7. Reiniciar Odoo
sudo systemctl start odoo-server

# 8. Verificar logs
sudo tail -f /var/log/odoo/odoo-server.log
```

**Tempo estimado de restore:** ~5 minutos

---

## 🧪 Verificação de Integridade

### Database Dump
```bash
ssh odoo-rc "file ~/backups/pre_sms_implementation_20251115_153111/realcred_database.dump"
# Output: PostgreSQL custom database dump - v1.14-0 ✅
```

### Custom Modules
```bash
ssh odoo-rc "tar -tzf ~/backups/pre_sms_implementation_20251115_153111/custom_modules.tar.gz | wc -l"
# Output: 8072 arquivos ✅
```

### Módulos Importantes Incluídos
- `contacts_realcred/` (módulo principal SempreReal)
- `l10n_br_*` (localização brasileira)
- `addons_custom/` (todos customizados)
- `addons_oca/` (módulos OCA instalados)

---

## 📊 Estatísticas do Backup

```
Tempo de Execução: ~2 minutos
Método Database: pg_dump -Fc (compressed custom format)
Método Módulos: tar -czf (gzip compression)
Compressão Database: ~30% (de ~800MB para 558MB)
Compressão Módulos: ~40% (de ~800MB para 499MB)
```

---

## ⚠️ Segurança

**ESTE BACKUP CONTÉM INFORMAÇÕES SENSÍVEIS:**

- ✅ Database completo com dados de clientes
- ✅ Credenciais Kolmeya API (Bearer token)
- ✅ Configurações do sistema
- ✅ Código-fonte customizado

**PROTEGER ESTE DIRETÓRIO!**

**Recomendações:**
- NÃO compartilhar publicamente
- NÃO commitar no Git
- Manter apenas no servidor seguro
- Deletar após confirmação de sucesso (30 dias)

---

## 🎯 Propósito

Este backup foi criado antes de implementar a **integração completa com Kolmeya SMS**, que inclui:

1. Criação de 3 novos módulos:
   - `sms_base_sr` (core abstraction)
   - `sms_kolmeya` (provider específico)
   - `contacts_realcred_sms` (business logic)

2. Modificações em módulos existentes:
   - `contacts_realcred` (adicionar envio SMS real)

3. Novas dependências:
   - OCA `queue_job`
   - Python `PyJWT`

4. Novos modelos de database:
   - `sms.message`
   - `sms.template`
   - `sms.provider`

**Risco:** Médio (modificações em código existente + novos módulos)

**Estratégia de Rollback:** Backup completo permite voltar em < 5 minutos

---

## 📝 Checklist de Restore

Se precisar fazer rollback, siga esta ordem:

- [ ] 1. Parar Odoo server
- [ ] 2. Restaurar database
- [ ] 3. Restaurar módulos custom
- [ ] 4. Restaurar configuração
- [ ] 5. Verificar permissões (chown odoo:odoo)
- [ ] 6. Reiniciar Odoo
- [ ] 7. Verificar logs (sem erros)
- [ ] 8. Testar login no Odoo
- [ ] 9. Verificar módulo contacts_realcred funcional
- [ ] 10. Confirmar que campanhas estão visíveis

---

## 🗂️ Localização dos Arquivos

**Servidor:**
```
/home/andlee21/backups/pre_sms_implementation_20251115_153111/
├── README_BACKUP.md
├── realcred_database.dump
├── custom_modules.tar.gz
└── odoo-server.conf
```

**Espaço em Disco:**
```bash
# Verificar espaço disponível
df -h /home

# Ver tamanho do backup
du -sh /home/andlee21/backups/pre_sms_implementation_20251115_153111/
```

---

## 💾 Download Local (Opcional)

Se quiser ter cópia local no seu Mac:

```bash
# Do seu Mac, executar:
mkdir -p ~/odoo_backups/
scp -r odoo-rc:~/backups/pre_sms_implementation_20251115_153111/ ~/odoo_backups/

# Verificar
ls -lh ~/odoo_backups/pre_sms_implementation_20251115_153111/
```

**Nota:** Download de 1.1GB pode demorar ~10-15 minutos dependendo da conexão.

---

## 🔍 Troubleshooting

### Problema: "Permission denied" durante restore

**Solução:**
```bash
# Dar permissão de leitura
sudo chmod -R 644 ~/backups/pre_sms_implementation_20251115_153111/*
sudo chmod 755 ~/backups/pre_sms_implementation_20251115_153111/
```

### Problema: "Database already exists" durante restore

**Solução:**
```bash
# Forçar drop e recriação
sudo -u postgres psql -c "DROP DATABASE IF EXISTS realcred;"
sudo -u postgres psql -c "CREATE DATABASE realcred OWNER odoo;"
sudo -u postgres pg_restore -d realcred realcred_database.dump
```

### Problema: Módulos não carregam após restore

**Solução:**
```bash
# Verificar permissões
sudo chown -R odoo:odoo /odoo/custom/
sudo chmod -R 755 /odoo/custom/

# Reiniciar Odoo
sudo systemctl restart odoo-server

# Update base module
cd /odoo/odoo-server
sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d realcred --stop-after-init --update=base
```

---

## 📅 Histórico de Backups

| Data | Tipo | Tamanho | Motivo |
|------|------|---------|--------|
| 2025-11-15 15:34 | Completo | 1.1 GB | Pre-SMS Implementation |

---

## ✅ Backup Verificado

- ✅ Database dump válido (PostgreSQL v1.14)
- ✅ Tar.gz dos módulos extraível (8072 arquivos)
- ✅ Configuração legível
- ✅ Integridade confirmada
- ✅ Permissões corretas
- ✅ README documentado

**Status:** PRONTO PARA USAR EM CASO DE EMERGÊNCIA

---

**Criado por:** Claude Code
**Data:** 2025-11-15
**Servidor:** odoo-rc (35.199.79.229)
**Database:** realcred (Odoo 15.0)
