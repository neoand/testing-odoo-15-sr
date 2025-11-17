# Comandos Úteis para Gerenciamento do Servidor

## Conexão SSH

### Conectar ao Servidor
```bash
# Método recomendado
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b

# Com caminho completo
/opt/homebrew/bin/gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b
```

### Executar Comando Remoto
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="comando_aqui"
```

## Informações do Sistema

### Status Geral
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="uptime && free -h && df -h /"
```

### Informações Detalhadas
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="
  echo '=== Sistema ===' && uname -a && 
  echo '' && echo '=== Uptime ===' && uptime && 
  echo '' && echo '=== Memória ===' && free -h && 
  echo '' && echo '=== Disco ===' && df -h && 
  echo '' && echo '=== IPs ===' && hostname -I
"
```

### Processos em Execução
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="ps aux | head -20"
```

### Carga do Sistema
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="top -bn1 | head -20"
```

## Transferência de Arquivos

### Copiar Arquivo para o Servidor
```bash
gcloud compute scp arquivo.txt odoo-sr-tensting:~/ --zone=southamerica-east1-b
```

### Copiar Arquivo do Servidor
```bash
gcloud compute scp odoo-sr-tensting:~/arquivo.txt ./ --zone=southamerica-east1-b
```

### Copiar Diretório para o Servidor
```bash
gcloud compute scp --recurse diretorio/ odoo-sr-tensting:~/ --zone=southamerica-east1-b
```

### Copiar Diretório do Servidor
```bash
gcloud compute scp --recurse odoo-sr-tensting:~/diretorio/ ./ --zone=southamerica-east1-b
```

## Gerenciamento de Instância (GCP)

### Ver Status da Instância
```bash
gcloud compute instances describe odoo-sr-tensting \
  --zone=southamerica-east1-b \
  --format="get(status)"
```

### Reiniciar Instância
```bash
gcloud compute instances reset odoo-sr-tensting --zone=southamerica-east1-b
```

### Parar Instância
```bash
gcloud compute instances stop odoo-sr-tensting --zone=southamerica-east1-b
```

### Iniciar Instância
```bash
gcloud compute instances start odoo-sr-tensting --zone=southamerica-east1-b
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

## Verificação de Serviços

### Verificar se Odoo está Rodando
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="
  sudo systemctl status odoo 2>/dev/null || 
  ps aux | grep odoo | grep -v grep || 
  echo 'Odoo não encontrado rodando como serviço'
"
```

### Verificar Portas em Uso
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo netstat -tulpn | grep LISTEN"
```

### Verificar Serviços Systemd
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo systemctl list-units --type=service --state=running"
```

## Logs

### Ver Logs do Sistema
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo journalctl -n 50"
```

### Ver Logs de um Serviço Específico
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo journalctl -u nome_servico -n 50"
```

### Ver Logs em Tempo Real
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo journalctl -f"
```

## Manutenção

### Atualizar Sistema
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="
  sudo apt update && 
  sudo apt list --upgradable
"
```

### Instalar Atualizações
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="
  sudo apt update && 
  sudo apt upgrade -y
"
```

### Limpar Cache de Pacotes
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo apt clean && sudo apt autoclean"
```

### Verificar Espaço em Disco
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="
  df -h && 
  echo '' && 
  echo '=== Top 10 maiores diretórios ===' && 
  sudo du -h --max-depth=1 / 2>/dev/null | sort -hr | head -10
"
```

## Segurança

### Verificar Usuários Logados
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="who && w"
```

### Verificar Tentativas de Login
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo tail -50 /var/log/auth.log"
```

### Verificar Permissões de Arquivos Importantes
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="
  ls -la /etc/passwd /etc/shadow /etc/sudoers 2>/dev/null
"
```

## Backup e Restauração

### Criar Snapshot do Disco
```bash
gcloud compute disks snapshot rc-20-jul-25 \
  --snapshot-names=snapshot-$(date +%Y%m%d-%H%M%S) \
  --zone=southamerica-east1-b
```

### Listar Snapshots
```bash
gcloud compute snapshots list --filter="sourceDisk:rc-20-jul-25"
```

## Monitoramento

### Verificar Uso de Recursos
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="
  echo 'CPU:' && top -bn1 | grep 'Cpu(s)' && 
  echo '' && echo 'Memória:' && free -h && 
  echo '' && echo 'Disco:' && df -h /
"
```

### Verificar Conexões de Rede
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo ss -tulpn"
```

## Atalhos Úteis

### Alias para Conexão Rápida (adicionar ao ~/.zshrc)
```bash
alias odoo-testing='gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b'
```

### Função para Executar Comando Remoto
```bash
odoo-cmd() {
  gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="$1"
}
```

### Função para Copiar Arquivo
```bash
odoo-scp-to() {
  gcloud compute scp "$1" odoo-sr-tensting:"$2" --zone=southamerica-east1-b
}

odoo-scp-from() {
  gcloud compute scp odoo-sr-tensting:"$1" "$2" --zone=southamerica-east1-b
}
```

