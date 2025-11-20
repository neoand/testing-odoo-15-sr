#!/bin/bash
# Script: odoo-logs.sh
# Description: View Odoo logs from testing or production server
# Usage: ./odoo-logs.sh [testing|production] [lines|follow]
# Author: Claude
# Created: 2025-11-17

set -e

SERVER=${1:-production}
MODE=${2:-lines}  # lines or follow
LINES=${3:-100}   # Default 100 lines

if [ "$SERVER" = "testing" ]; then
    if [ "$MODE" = "follow" ]; then
        echo "📋 Following logs on TESTING server (Ctrl+C to stop)..."
        gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo tail -f /var/log/odoo/odoo-server.log"
    else
        echo "📋 Last $LINES lines from TESTING server..."
        gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo tail -n $LINES /var/log/odoo/odoo-server.log"
    fi
elif [ "$SERVER" = "production" ]; then
    if [ "$MODE" = "follow" ]; then
        echo "📋 Following logs on PRODUCTION server (Ctrl+C to stop)..."
        ssh odoo-rc "sudo tail -f /var/log/odoo/odoo-server.log"
    else
        echo "📋 Last $LINES lines from PRODUCTION server..."
        ssh odoo-rc "sudo tail -n $LINES /var/log/odoo/odoo-server.log"
    fi
else
    echo "❌ Error: Invalid server"
    echo "Usage: $0 [testing|production] [lines|follow] [number_of_lines]"
    echo "Examples:"
    echo "  $0 production lines 200    # Last 200 lines from production"
    echo "  $0 testing follow          # Follow logs on testing"
    exit 1
fi
