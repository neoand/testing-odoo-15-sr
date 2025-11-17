# Configuração do Google Cloud Platform

## Informações do Projeto

### Projeto Principal
- **Project ID:** `webserver-258516`
- **Project Name:** (verificar no console)
- **Location:** `southamerica-east1` (São Paulo, Brasil)

### Zona e Região
- **Zona da Instância:** `southamerica-east1-b`
- **Região:** `southamerica-east1`
- **Localização Física:** São Paulo, Brasil

## Configuração da Instância

### Identificação
- **Nome:** `odoo-sr-tensting`
- **Instance ID:** `6970162141243819062`
- **Descrição:** None
- **Instance Template:** None

### Machine Configuration
- **Machine Type:** `e2-medium`
- **vCPUs:** 2
- **Memória:** 4 GB
- **CPU Platform:** Intel Broadwell
- **Arquitetura:** x86/64

### Boot Disk
- **Nome:** `rc-20-jul-25`
- **Tamanho:** 300 GB
- **Tipo:** SSD persistent disk
- **Licença:** Free
- **Modo:** Read/write
- **Ao deletar instância:** Keep disk

### Networking

**Network Interface (nic0):**
- **Network:** `default`
- **Subnetwork:** `default`
- **NIC Type:** (padrão)
- **IP Interno:** `10.158.0.5`
- **IP Externo:** `35.199.92.1` (Ephemeral)
- **Network Tier:** Premium
- **IP Forwarding:** Off

**Firewall Rules:**
- **HTTP traffic:** On
- **HTTPS traffic:** On
- **Allow Load Balancer Health checks:** Off

**Network Tags:**
- `http-server`
- `https-server`

### Security

**Shielded VM:**
- **Secure Boot:** Off
- **vTPM:** On
- **Integrity Monitoring:** On

**SSH Keys:**
- **Block project-wide SSH keys:** Off
- **Chave configurada:** Ver `ACESSOS_CREDENCIAIS.md`

**OS Login:**
- **Status:** Habilitado (`enable-oslogin: true`)

### Service Account
- **Email:** `744444505452-compute@developer.gserviceaccount.com`
- **Cloud API access scopes:** Allow default access

### Metadata

**Custom Metadata:**
- `enable-osconfig: TRUE`
- `enable-oslogin: true`

### Backup Configuration

**Backup Plan:**
- **Nome:** `default-compute-instance-plan-southamerica-east1`
- **Projeto:** `webserver-258516`
- **Descrição:** Default backup plan created by Backup and DR for southamerica-east1 and resource type Compute Instances

**Backup Vault:**
- **Nome:** `default-vault-southamerica-east1`
- **Location:** `southamerica-east1`

**Backup Schedule:**
- **Frequência:** Diário
- **Horário:** Entre 12:00 AM e 1:00 AM
- **Estado:** Active

### Availability Policies

**VM Provisioning Model:**
- **Tipo:** Standard
- **Max duration:** None
- **Preemptibility:** Off (Recommended)

**On VM Termination:**
- (Não configurado)

**On Host Maintenance:**
- **Ação:** Migrate VM instance (Recommended)
- **Host error timeout:** (padrão)

**Automatic Restart:**
- **Status:** On (Recommended)

### Data Encryption
- **Key ID:** (não configurado)
- **Key name:** (não configurado)
- **CMEK revocation policy:** Do nothing

### Sole-tenancy
- **CPU Overcommit:** Disabled

### Deletion Protection
- **Status:** Disabled

## Comandos GCP Úteis

### Listar Instâncias
```bash
gcloud compute instances list --project=webserver-258516
```

### Descrever Instância
```bash
gcloud compute instances describe odoo-sr-tensting \
  --zone=southamerica-east1-b \
  --project=webserver-258516
```

### Obter IP Externo
```bash
gcloud compute instances describe odoo-sr-tensting \
  --zone=southamerica-east1-b \
  --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
```

### Obter IP Interno
```bash
gcloud compute instances describe odoo-sr-tensting \
  --zone=southamerica-east1-b \
  --format="get(networkInterfaces[0].networkIP)"
```

### Reiniciar Instância
```bash
gcloud compute instances reset odoo-sr-tensting \
  --zone=southamerica-east1-b
```

### Parar Instância
```bash
gcloud compute instances stop odoo-sr-tensting \
  --zone=southamerica-east1-b
```

### Iniciar Instância
```bash
gcloud compute instances start odoo-sr-tensting \
  --zone=southamerica-east1-b
```

### Criar IP Estático (se necessário)
```bash
gcloud compute addresses create odoo-sr-testing-ip \
  --region=southamerica-east1 \
  --project=webserver-258516
```

## Links Úteis

- **Console GCP:** https://console.cloud.google.com/compute/instances?project=webserver-258516
- **Documentação GCP:** https://cloud.google.com/compute/docs
- **Zonas Disponíveis:** https://cloud.google.com/compute/docs/regions-zones

