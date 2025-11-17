# Detalhes Técnicos do Servidor

## Informações da Instância

### Identificação
- **Nome:** `odoo-sr-tensting`
- **Instance ID:** `6970162141243819062`
- **Status:** Running
- **Criação:** 17 de Novembro de 2025, 13:43:21 UTC-06:00
- **Localização:** `southamerica-east1-b` (São Paulo, Brasil)

### Configuração de Hardware

**Machine Type:** `e2-medium`
- **vCPUs:** 2
- **Memória:** 4 GB
- **CPU Platform:** Intel Broadwell
- **Arquitetura:** x86/64

### Armazenamento

**Boot Disk:**
- **Nome:** `rc-20-jul-25`
- **Tamanho:** 300 GB
- **Tipo:** SSD persistent disk
- **Uso Atual:** 168 GB (58%)
- **Disponível:** 124 GB
- **Proteção:** Backup automático diário (12:00 AM - 1:00 AM)

**Backup:**
- **Plano:** `default-compute-instance-plan-southamerica-east1`
- **Vault:** `default-vault-southamerica-east1`
- **Frequência:** Diário
- **Estado:** Ativo

### Sistema Operacional

- **Distribuição:** Ubuntu 20.04 LTS
- **Kernel:** Linux 5.15.0-1083-gcp
- **Arquitetura:** x86_64 GNU/Linux

### Recursos do Sistema (Última Verificação)

**Memória:**
- **Total:** 3.8 GB
- **Usado:** 1.2 GB
- **Livre:** 1.4 GB
- **Buffer/Cache:** 1.2 GB
- **Disponível:** 2.2 GB
- **Swap:** 0 GB (desabilitado)

**Disco:**
- **Total:** 291 GB
- **Usado:** 168 GB (58%)
- **Disponível:** 124 GB

**Carga do Sistema:**
- **1 minuto:** 0.20
- **5 minutos:** 0.17
- **15 minutos:** 0.11

### Rede

**Interface de Rede (nic0):**
- **Rede:** `default`
- **Subnet:** `default`
- **IP Interno:** `10.158.0.5`
- **IP Externo:** `35.199.92.1` (Ephemeral)
- **Network Tier:** Premium
- **IP Forwarding:** Desabilitado

**Firewalls:**
- **HTTP traffic:** Habilitado
- **HTTPS traffic:** Habilitado
- **Network Tags:** `http-server`, `https-server`

### Segurança

**Shielded VM:**
- **Secure Boot:** Desabilitado
- **vTPM:** Habilitado
- **Integrity Monitoring:** Habilitado

**SSH Keys:**
- **Usuário:** `andlee21`
- **Chave:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIZjj/qq4G2XeocH5DmyoAl3UcHHUMgxcxzQhZVYmx3t andlee21@hotmail.com`
- **Block project-wide SSH keys:** Desabilitado

**OS Login:**
- **Status:** Habilitado (`enable-oslogin: true`)

### Configurações de Gerenciamento

**Service Account:**
- **Email:** `744444505452-compute@developer.gserviceaccount.com`
- **Cloud API access scopes:** Allow default access

**Availability Policies:**
- **VM provisioning model:** Standard
- **Preemptibility:** Off
- **Automatic restart:** On
- **On host maintenance:** Migrate VM instance

**Metadata:**
- `enable-osconfig: TRUE`
- `enable-oslogin: true`

### Deletion Protection
- **Status:** Desabilitado

