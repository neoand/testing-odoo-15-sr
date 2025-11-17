#!/usr/bin/env python3
"""
Kolmeya SMS Monitor - Test
Monitora status das mensagens enviadas
"""

import requests
import time
import json
from datetime import datetime

# Configuration
KOLMEYA_API_URL = "https://kolmeya.com.br/api/v1/sms/status/request"
KOLMEYA_TOKEN = "Bearer 5RshH19JjvN5M6RRCLoMKRkLnFYBrpLZiTXzpsgY"

# Test Job ID
JOB_ID = "bd067220-a777-46b4-91d7-c834c773538d"

# Status mapping
STATUS_MAP = {
    1: "🔄 Tentando enviar",
    2: "📤 Enviado",
    3: "✅ Entregue",
    4: "❌ Não entregue",
    5: "⛔ Rejeitado",
    6: "⏰ Expirado"
}

def check_status(job_id):
    """Check SMS status via Kolmeya API"""
    headers = {
        'Authorization': KOLMEYA_TOKEN,
        'Content-Type': 'application/json'
    }

    payload = {'id': job_id}

    try:
        response = requests.post(
            KOLMEYA_API_URL,
            json=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro: {e}")
        return None

def print_status(data):
    """Print formatted status"""
    if not data:
        return

    print(f"\n{'='*60}")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    print(f"\n📊 Job ID: {data['id']}")
    print(f"Status Geral: {data['status']} (Code: {data['status_code']})")

    print(f"\n📱 Mensagens:")
    for msg in data.get('messages', []):
        status_code = msg['status_code']
        status_text = STATUS_MAP.get(status_code, f"Unknown ({status_code})")

        print(f"\n  → {msg['reference']}")
        print(f"    ID: {msg['id']}")
        print(f"    Status: {status_text}")

def monitor(job_id, interval=10, max_checks=30):
    """Monitor SMS status until delivered or max_checks reached"""
    print(f"🔍 Monitorando Job {job_id}")
    print(f"Verificando a cada {interval} segundos (máximo {max_checks} vezes)")

    for i in range(max_checks):
        data = check_status(job_id)

        if data:
            print_status(data)

            # Check if all messages delivered
            messages = data.get('messages', [])
            all_delivered = all(
                msg['status_code'] == 3
                for msg in messages
            )

            if all_delivered:
                print(f"\n{'='*60}")
                print("✅ TODAS AS MENSAGENS ENTREGUES!")
                print(f"{'='*60}\n")
                return True

            # Check for failures
            failed = [
                msg for msg in messages
                if msg['status_code'] in [4, 5, 6]
            ]

            if failed:
                print(f"\n{'='*60}")
                print(f"⚠️  {len(failed)} MENSAGEM(NS) COM FALHA!")
                print(f"{'='*60}\n")
                for msg in failed:
                    print(f"  ❌ {msg['reference']}: {msg['status']}")
                return False

        # Wait before next check
        if i < max_checks - 1:
            print(f"\n⏳ Aguardando {interval}s... ({i+1}/{max_checks})")
            time.sleep(interval)

    print(f"\n{'='*60}")
    print("⏰ TIMEOUT - Verificações concluídas sem entrega final")
    print(f"{'='*60}\n")
    return False

if __name__ == '__main__':
    print("\n🚀 Kolmeya SMS Monitor - Test")
    print("="*60)

    # Run monitoring
    success = monitor(JOB_ID, interval=10, max_checks=30)

    # Final status
    print("\n📋 RESUMO FINAL:")
    final_data = check_status(JOB_ID)
    if final_data:
        print_status(final_data)

    exit(0 if success else 1)
