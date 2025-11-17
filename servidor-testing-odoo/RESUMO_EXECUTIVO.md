# Resumo Executivo - Servidor Testing Odoo

## 📌 Visão Geral

Servidor de teste do Odoo hospedado no Google Cloud Platform, configurado com OS Login e acesso via Google Cloud SDK.

## 🎯 Informações Principais

**Servidor:**
- Nome: `odoo-sr-tensting`
- Projeto GCP: `webserver-258516`
- Zona: `southamerica-east1-b`
- IP Externo: `35.199.92.1`
- IP Interno: `10.158.0.5`
- Sistema: Ubuntu 20.04 LTS

**Recursos:**
- 2 vCPUs, 4 GB RAM
- 300 GB SSD (168 GB usado, 124 GB livre)
- 9 workers Odoo
- PostgreSQL 12

**Serviços:**
- ✅ Odoo (portas 8069/8072)
- ✅ PostgreSQL (porta 5432)
- ✅ Nginx (portas 80/443)
- ✅ SSH (porta 22)

## 🔐 Acesso

**SSH:**
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b
```

**Odoo Web:**
- URL: `http://35.199.92.1` ou `https://35.199.92.1`
- Admin Password: `HI5Rdi5UikL9jjLy`

**Banco de Dados:**
- Nome: `realcred`
- PostgreSQL 12

## 📚 Documentação

Esta pasta contém documentação completa em formato "AI First" para fácil leitura por LLMs:

1. **README.md** - Visão geral e índice
2. **INDICE_RAPIDO.md** - Referência rápida
3. **CONEXAO_SSH.md** - Como conectar
4. **ACESSOS_CREDENCIAIS.md** - Credenciais
5. **DETALHES_TECNICOS.md** - Especificações técnicas
6. **CONFIGURACAO_GCP.md** - Configuração GCP
7. **ODOO_CONFIGURACAO.md** - Configuração Odoo
8. **ESTRUTURA_SISTEMA.md** - Estrutura e serviços
9. **COMANDOS_UTEIS.md** - Comandos de gerenciamento

## ⚙️ Configuração Odoo

**Diretório:** `/odoo/`

**Configuração:** `/etc/odoo-server.conf`

**Módulos Customizados:**
- `/odoo/custom/addons_custom`
- `/odoo/custom/helpdesk`
- `/odoo/custom/l10n_br_base`
- `/odoo/custom/social`
- `/odoo/custom/addons-whatsapp-connector`
- `/odoo/custom/om_account_accountant`
- `/odoo/custom/hr_attendance_pro`
- `/odoo/iurd-cm-mx/`

## 🔄 Backup

- **Backups Odoo:** `/odoo/backups/`
- **Backups GCP:** Diários (12:00 AM - 1:00 AM)
- **Vault:** `default-vault-southamerica-east1`

## ⚠️ Observações Importantes

1. **OS Login habilitado** - Use `gcloud compute ssh` (não SSH tradicional)
2. **IP Externo é Ephemeral** - Pode mudar ao reiniciar
3. **Senha Admin Odoo** - Manter segura
4. **Backups automáticos** - Configurados e ativos

## 🚀 Próximos Passos

Para começar a trabalhar com o servidor:

1. Leia o **[INDICE_RAPIDO.md](./INDICE_RAPIDO.md)** para referência rápida
2. Consulte **[CONEXAO_SSH.md](./CONEXAO_SSH.md)** para conectar
3. Use **[COMANDOS_UTEIS.md](./COMANDOS_UTEIS.md)** para operações comuns
4. Veja **[ODOO_CONFIGURACAO.md](./ODOO_CONFIGURACAO.md)** para detalhes do Odoo

---

**Última Atualização:** 17 de Novembro de 2025  
**Versão da Documentação:** 1.0

