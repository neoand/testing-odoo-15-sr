# Acessos e Credenciais

## ⚠️ IMPORTANTE: SEGURANÇA

Este arquivo contém informações sensíveis. Mantenha-o seguro e não compartilhe em repositórios públicos.

## Acesso SSH

### Método Principal: Google Cloud SDK

**Comando de Conexão:**
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b
```

**Usuário no Servidor:**
- **Username:** `admin_iurd_mx`
- **Método de Autenticação:** Gerenciado automaticamente pelo Google Cloud SDK

**Conta Google Cloud:**
- **Email:** `admin@iurd.mx`
- **Projeto:** `webserver-258516`

### Chaves SSH

**Chave Pública (adicionada ao servidor):**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIZjj/qq4G2XeocH5DmyoAl3UcHHUMgxcxzQhZVYmx3t andlee21@hotmail.com
```

**Localização da Chave Privada (Mac):**
- **Caminho:** `~/.ssh/id_ed25519`
- **Fingerprint:** `SHA256:mJFufktYtGbGYchv6wvf5pyKa4i6r9LocAaKTfPQxt8`

**Nota:** A chave privada está na pasta padrão do Mac (`~/.ssh/`), mas não é usada diretamente devido ao OS Login estar habilitado.

## Informações de Rede

### IPs

**IP Externo (Público):**
- **Endereço:** `35.199.92.1`
- **Tipo:** Ephemeral (pode mudar se a instância for reiniciada)
- **Network Tier:** Premium

**IP Interno (Privado):**
- **Endereço:** `10.158.0.5`
- **Rede:** `default`
- **Subnet:** `default`

### Portas e Serviços

**Portas Abertas (Firewall):**
- **HTTP:** 80 (habilitado)
- **HTTPS:** 443 (habilitado)

**Network Tags:**
- `http-server`
- `https-server`

## Acesso ao Google Cloud Platform

### Console Web
- **URL:** https://console.cloud.google.com
- **Projeto:** `webserver-258516`
- **Zona:** `southamerica-east1-b`

### Service Account
- **Email:** `744444505452-compute@developer.gserviceaccount.com`
- **Permissões:** Default access (conforme configuração do projeto)

## Acesso ao Odoo (Se Configurado)

**Nota:** Verificar se o Odoo está instalado e rodando no servidor. Se estiver:

**Possíveis URLs:**
- HTTP: `http://35.199.92.1`
- HTTPS: `https://35.199.92.1`

**Para verificar:**
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo systemctl status odoo || ps aux | grep odoo"
```

## Comandos de Verificação de Acesso

**Testar conexão SSH:**
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="echo 'Conexão OK' && whoami"
```

**Verificar usuário atual:**
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="whoami && id"
```

**Verificar permissões:**
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo -l"
```

## Troubleshooting de Acesso

### Problema: Não consigo conectar via SSH tradicional
**Solução:** Use `gcloud compute ssh` ao invés de `ssh` tradicional, pois OS Login está habilitado.

### Problema: "Permission denied"
**Solução:** 
1. Verifique se está autenticado: `gcloud auth list`
2. Verifique o projeto: `gcloud config get-value project`
3. Verifique permissões no IAM do GCP

### Problema: "Project not found"
**Solução:**
```bash
gcloud config set project webserver-258516
```

### Problema: IP externo mudou
**Solução:** 
1. Verifique o IP atual: `gcloud compute instances describe odoo-sr-tensting --zone=southamerica-east1-b --format="get(networkInterfaces[0].accessConfigs[0].natIP)"`
2. Ou reserve um IP estático se necessário

