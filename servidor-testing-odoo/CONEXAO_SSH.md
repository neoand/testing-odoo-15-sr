# Como Conectar ao Servidor via SSH

## Método Recomendado: Google Cloud SDK (gcloud)

O servidor está configurado com OS Login habilitado, portanto a conexão deve ser feita através do Google Cloud SDK.

### Pré-requisitos

1. **Google Cloud SDK instalado:**
   ```bash
   brew install --cask google-cloud-sdk
   ```

2. **Caminho do gcloud:**
   - Instalado via Homebrew: `/opt/homebrew/bin/gcloud`
   - Para adicionar ao PATH permanentemente, adicione ao `~/.zshrc`:
     ```bash
     export PATH=/opt/homebrew/share/google-cloud-sdk/bin:"$PATH"
     ```

### Configuração Inicial

1. **Definir o projeto GCP:**
   ```bash
   gcloud config set project webserver-258516
   ```

2. **Verificar configuração:**
   ```bash
   gcloud config get-value project
   # Deve retornar: webserver-258516
   ```

### Comando de Conexão

**Comando básico:**
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b
```

**Comando com caminho completo (se gcloud não estiver no PATH):**
```bash
/opt/homebrew/bin/gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b
```

**Executar comando remoto sem abrir shell interativo:**
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="comando_aqui"
```

### Exemplos de Uso

**Verificar status do servidor:**
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="uptime && free -h && df -h /"
```

**Copiar arquivo para o servidor:**
```bash
gcloud compute scp arquivo.txt odoo-sr-tensting:~/ --zone=southamerica-east1-b
```

**Copiar arquivo do servidor:**
```bash
gcloud compute scp odoo-sr-tensting:~/arquivo.txt ./ --zone=southamerica-east1-b
```

## Método Alternativo: SSH Tradicional (NÃO FUNCIONA)

**IMPORTANTE:** O servidor tem OS Login habilitado (`enable-oslogin: true`), portanto conexões SSH tradicionais com chave pública não funcionam diretamente.

Se necessário desabilitar OS Login:
1. Acessar Console do GCP
2. Editar metadados da instância
3. Remover ou definir `enable-oslogin` como `false`

## Autenticação

- **Método:** Google Cloud SDK gerencia autenticação automaticamente
- **Usuário no servidor:** `admin_iurd_mx`
- **Conta GCP:** `admin@iurd.mx`

## Troubleshooting

**Erro: "Permission denied (publickey)"**
- Use `gcloud compute ssh` ao invés de `ssh` tradicional
- Verifique se o projeto está configurado corretamente

**Erro: "Project not found"**
- Execute: `gcloud config set project webserver-258516`
- Verifique permissões da conta GCP

**Erro: "Zone not found"**
- Verifique se a zona está correta: `southamerica-east1-b`
- Liste as zonas disponíveis: `gcloud compute zones list`

