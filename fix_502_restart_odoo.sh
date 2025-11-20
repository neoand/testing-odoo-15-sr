#!/bin/bash
# Script para corrigir erro 502 - Reiniciar Odoo corretamente
# Odoo 15 - RealCred Testing

echo "🔧 CORREÇÃO ERRO 502 - REINICIANDO ODOO"
echo "========================================"
echo ""

SERVER="odoo-sr-tensting"
ZONE="southamerica-east1-b"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "📡 Conectando ao servidor: $SERVER"
echo ""

# 1. Parar Odoo
echo "1️⃣ Parando Odoo Server..."
gcloud compute ssh $SERVER --zone=$ZONE --command="sudo systemctl stop odoo-server" 2>&1

# 2. Matar processos órfãos
echo ""
echo "2️⃣ Limpando processos órfãos..."
gcloud compute ssh $SERVER --zone=$ZONE --command="sudo pkill -9 -f odoo-bin || true" 2>&1

# 3. Aguardar 3 segundos
echo ""
echo "3️⃣ Aguardando 3 segundos..."
sleep 3

# 4. Verificar configuração
echo ""
echo "4️⃣ Verificando configuração do Odoo..."
gcloud compute ssh $SERVER --zone=$ZONE --command="sudo grep -E '^(workers|xmlrpc_port|http_port)' /etc/odoo-server.conf | head -5" 2>&1

# 5. Iniciar Odoo
echo ""
echo "5️⃣ Iniciando Odoo Server..."
gcloud compute ssh $SERVER --zone=$ZONE --command="sudo systemctl start odoo-server" 2>&1

# 6. Aguardar inicialização
echo ""
echo "6️⃣ Aguardando inicialização (10 segundos)..."
sleep 10

# 7. Verificar status
echo ""
echo "7️⃣ Verificando status do Odoo..."
gcloud compute ssh $SERVER --zone=$ZONE --command="sudo systemctl status odoo-server --no-pager | head -15" 2>&1

# 8. Verificar se está escutando na porta
echo ""
echo "8️⃣ Verificando se está escutando na porta 8069..."
gcloud compute ssh $SERVER --zone=$ZONE --command="sudo ss -tlnp | grep 8069" 2>&1

# 9. Verificar últimos logs
echo ""
echo "9️⃣ Verificando últimos logs (últimas 10 linhas)..."
gcloud compute ssh $SERVER --zone=$ZONE --command="sudo tail -10 /var/log/odoo/odoo-server.log" 2>&1

# 10. Testar conexão
echo ""
echo "🔟 Testando conexão HTTP local..."
gcloud compute ssh $SERVER --zone=$ZONE --command="curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8069/web/login || echo 'Falha na conexão'" 2>&1

echo ""
echo "========================================"
echo "✅ Processo de reinicialização completo!"
echo ""
echo "💡 Se ainda houver erro 502:"
echo "   1. Verifique os logs: sudo tail -f /var/log/odoo/odoo-server.log"
echo "   2. Verifique o Nginx: sudo systemctl restart nginx"
echo "   3. Verifique o banco de dados: sudo -u postgres psql -c 'SELECT count(*) FROM pg_stat_activity;'"

