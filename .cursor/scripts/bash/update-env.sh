#!/bin/bash
# Script: update-env.sh
# Description: Update .claude.env persistent state
# Usage: ./update-env.sh KEY VALUE
# Author: Claude
# Created: 2025-11-17

ENV_FILE=".claude.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: $ENV_FILE not found"
    exit 1
fi

if [ $# -ne 2 ]; then
    echo "Usage: $0 KEY VALUE"
    echo "Example: $0 CURRENT_SPRINT 4"
    exit 1
fi

KEY="$1"
VALUE="$2"

# Check if key exists
if grep -q "^${KEY}=" "$ENV_FILE"; then
    # Update existing key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/^${KEY}=.*/${KEY}=${VALUE}/" "$ENV_FILE"
    else
        # Linux
        sed -i "s/^${KEY}=.*/${KEY}=${VALUE}/" "$ENV_FILE"
    fi
    echo "✅ Updated: $KEY=$VALUE"
else
    # Add new key
    echo "${KEY}=${VALUE}" >> "$ENV_FILE"
    echo "✅ Added: $KEY=$VALUE"
fi
