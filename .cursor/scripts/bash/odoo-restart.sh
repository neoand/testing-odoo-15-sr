#!/bin/bash
# Script: odoo-restart.sh
# Description: Restart Odoo service on testing or production server
# Usage: ./odoo-restart.sh [testing|production]
# Author: Claude
# Created: 2025-11-17

set -e  # Exit on error

SERVER=${1:-production}  # Default to production

if [ "$SERVER" = "testing" ]; then
    echo "🔄 Restarting Odoo on TESTING server (odoo-sr-tensting)..."
    gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo systemctl restart odoo && sudo systemctl status odoo --no-pager"
    echo "✅ Odoo restarted on testing server"
elif [ "$SERVER" = "production" ]; then
    echo "🔄 Restarting Odoo on PRODUCTION server (odoo-rc)..."
    ssh odoo-rc "sudo systemctl restart odoo-server && sudo systemctl status odoo-server --no-pager"
    echo "✅ Odoo restarted on production server"
else
    echo "❌ Error: Invalid server. Use 'testing' or 'production'"
    echo "Usage: $0 [testing|production]"
    exit 1
fi
