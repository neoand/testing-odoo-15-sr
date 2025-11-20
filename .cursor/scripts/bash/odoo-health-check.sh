#!/bin/bash
# Script: odoo-health-check.sh
# Description: Complete health check of Odoo server (services, resources, database)
# Usage: ./odoo-health-check.sh [testing|production]
# Author: Claude
# Created: 2025-11-17

set -e

SERVER=${1:-production}

echo "🏥 Running Health Check..."
echo "================================"

if [ "$SERVER" = "testing" ]; then
    SSH_CMD="gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command"
    echo "🖥️  Server: TESTING (odoo-sr-tensting)"
elif [ "$SERVER" = "production" ]; then
    SSH_CMD="ssh odoo-rc"
    echo "🖥️  Server: PRODUCTION (odoo-rc)"
else
    echo "❌ Error: Invalid server"
    exit 1
fi

echo ""
echo "1️⃣  System Resources"
echo "-------------------"
$SSH_CMD "echo 'RAM Usage:' && free -h | grep Mem && echo '' && echo 'Disk Usage:' && df -h / | tail -n 1 && echo '' && echo 'Uptime:' && uptime"

echo ""
echo "2️⃣  Service Status"
echo "----------------"
if [ "$SERVER" = "production" ]; then
    $SSH_CMD "sudo systemctl is-active odoo-server && echo '✅ Odoo: Running' || echo '❌ Odoo: Down'"
    $SSH_CMD "sudo systemctl is-active postgresql@12-main && echo '✅ PostgreSQL: Running' || echo '❌ PostgreSQL: Down'"
    $SSH_CMD "sudo systemctl is-active nginx && echo '✅ Nginx: Running' || echo '❌ Nginx: Down'"
else
    $SSH_CMD "sudo systemctl is-active odoo && echo '✅ Odoo: Running' || echo '❌ Odoo: Down'"
    $SSH_CMD "sudo systemctl is-active postgresql && echo '✅ PostgreSQL: Running' || echo '❌ PostgreSQL: Down'"
fi

echo ""
echo "3️⃣  Odoo Workers"
echo "---------------"
$SSH_CMD "ps aux | grep -E 'odoo.*--workers' | grep -v grep | wc -l | xargs echo 'Active Odoo processes:'"

echo ""
echo "4️⃣  Database Connections"
echo "----------------------"
$SSH_CMD "sudo -u postgres psql -t -c 'SELECT count(*) FROM pg_stat_activity;' | xargs echo 'Active DB connections:'"

echo ""
echo "5️⃣  Recent Errors in Logs (last 50 lines)"
echo "----------------------------------------"
$SSH_CMD "sudo tail -n 50 /var/log/odoo/odoo-server.log | grep -i error | tail -n 5 || echo 'No recent errors found'"

echo ""
echo "================================"
echo "✅ Health check complete!"
