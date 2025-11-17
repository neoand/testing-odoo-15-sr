# Índice Rápido - Servidor Testing Odoo

## 🚀 Conexão Rápida

```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b
```

## 📋 Informações Essenciais

| Item | Valor |
|------|-------|
| **Nome da Instância** | `odoo-sr-tensting` |
| **Projeto GCP** | `webserver-258516` |
| **Zona** | `southamerica-east1-b` |
| **IP Externo** | `35.199.92.1` |
| **IP Interno** | `10.158.0.5` |
| **Sistema** | Ubuntu 20.04 LTS |
| **Usuário SSH** | `admin_iurd_mx` |

## 🔑 Acessos

- **SSH:** Via `gcloud compute ssh` (OS Login habilitado)
- **Odoo Web:** `http://35.199.92.1` ou `https://35.199.92.1`
- **Odoo Admin Password:** `HI5Rdi5UikL9jjLy` (ver ODOO_CONFIGURACAO.md)
- **Banco de Dados:** `realcred` (PostgreSQL 12)

## 📁 Documentação Completa

### Conexão e Acesso
- **[CONEXAO_SSH.md](./CONEXAO_SSH.md)** - Como conectar
- **[ACESSOS_CREDENCIAIS.md](./ACESSOS_CREDENCIAIS.md)** - Credenciais e acessos

### Configuração Técnica
- **[DETALHES_TECNICOS.md](./DETALHES_TECNICOS.md)** - Hardware e specs
- **[CONFIGURACAO_GCP.md](./CONFIGURACAO_GCP.md)** - Configuração GCP
- **[ODOO_CONFIGURACAO.md](./ODOO_CONFIGURACAO.md)** - Configuração Odoo

### Operação
- **[COMANDOS_UTEIS.md](./COMANDOS_UTEIS.md)** - Comandos de gerenciamento
- **[ESTRUTURA_SISTEMA.md](./ESTRUTURA_SISTEMA.md)** - Estrutura e serviços

## 🛠️ Comandos Mais Usados

### Status do Servidor
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="uptime && free -h && df -h /"
```

### Status do Odoo
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="ps aux | grep odoo | grep -v grep"
```

### Logs do Odoo
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo tail -f /var/log/odoo/odoo-server.log"
```

### Reiniciar Instância
```bash
gcloud compute instances reset odoo-sr-tensting --zone=southamerica-east1-b
```

## 📊 Recursos do Sistema

- **vCPUs:** 2
- **Memória:** 4 GB (3.8 GB disponível)
- **Disco:** 300 GB SSD (168 GB usado, 124 GB livre)
- **Workers Odoo:** 9
- **Banco de Dados:** PostgreSQL 12

## 🔍 Verificações Rápidas

### Serviços em Execução
- ✅ Odoo (porta 8069/8072)
- ✅ PostgreSQL (porta 5432)
- ✅ Nginx (portas 80/443)
- ✅ SSH (porta 22)

### Diretórios Importantes
- `/odoo/` - Instalação do Odoo
- `/odoo/odoo-server/` - Código fonte
- `/odoo/custom/` - Módulos customizados
- `/odoo/filestore/` - Arquivos do Odoo
- `/odoo/backups/` - Backups
- `/etc/odoo-server.conf` - Configuração

## ⚠️ Importante

1. **OS Login está habilitado** - Use `gcloud compute ssh` ao invés de SSH tradicional
2. **Senha Admin do Odoo** - Mantenha segura (ver ODOO_CONFIGURACAO.md)
3. **Backups automáticos** - Diários entre 12:00 AM e 1:00 AM
4. **IP Externo é Ephemeral** - Pode mudar se a instância for reiniciada

## 📞 Suporte

Para mais detalhes, consulte os arquivos de documentação específicos listados acima.

