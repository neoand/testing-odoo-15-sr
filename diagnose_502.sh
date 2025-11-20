#!/bin/bash
# Script de Diagnóstico para Erro 502 Bad Gateway
# Odoo 15 - RealCred Testing

echo "🔍 DIAGNÓSTICO ERRO 502 BAD GATEWAY"
echo "===================================="
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Servidor remoto
SERVER="odoo-sr-tensting"
ZONE="southamerica-east1-b"

echo "📡 Conectando ao servidor remoto: $SERVER"
echo ""

# 1. Verificar status do Odoo
echo "1️⃣ Verificando status do Odoo Server..."
gcloud compute ssh $SERVER --zone=$ZONE --command="sudo systemctl status odoo-server --no-pager | head -20" 2>&1

echo ""
echo "2️⃣ Verificando processos Odoo..."
gcloud compute ssh $SERVER --zone=$ZONE --command="ps aux | grep odoo-bin | grep -v grep | head -5" 2>&1

echo ""
echo "3️⃣ Verificando status do Nginx..."
gcloud compute ssh $SERVER --zone=$ZONE --command="sudo systemctl status nginx --no-pager | head -15" 2>&1

echo ""
echo "4️⃣ Verificando última parte do log do Odoo (últimas 30 linhas)..."
gcloud compute ssh $SERVER --zone=$ZONE --command="sudo tail -30 /var/log/odoo/odoo-server.log" 2>&1

echo ""
echo "5️⃣ Verificando erros do Nginx (últimas 20 linhas)..."
gcloud compute ssh $SERVER --zone=$ZONE --command="sudo tail -20 /var/log/nginx/odoo-semprereal-error.log" 2>&1

echo ""
echo "6️⃣ Verificando se Odoo está escutando na porta 8069..."
gcloud compute ssh $SERVER --zone=$ZONE --command="sudo netstat -tlnp | grep 8069 || sudo ss -tlnp | grep 8069" 2>&1

echo ""
echo "7️⃣ Verificando conexões PostgreSQL..."
gcloud compute ssh $SERVER --zone=$ZONE --command="sudo -u postgres psql -c 'SELECT count(*) FROM pg_stat_activity WHERE datname = '\''realcred'\'';'" 2>&1

echo ""
echo "===================================="
echo "✅ Diagnóstico completo!"
echo ""
echo "💡 PRÓXIMOS PASSOS:"
echo "   Se Odoo não estiver rodando:"
echo "   gcloud compute ssh $SERVER --zone=$ZONE --command='sudo systemctl restart odoo-server'"
echo ""
echo "   Se Nginx não estiver rodando:"
echo "   gcloud compute ssh $SERVER --zone=$ZONE --command='sudo systemctl restart nginx'"
echo ""
echo "   Para ver logs em tempo real:"
echo "   gcloud compute ssh $SERVER --zone=$ZONE --command='sudo tail -f /var/log/odoo/odoo-server.log'"

