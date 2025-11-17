#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para fazer upgrade do contact_center_sms
"""
import xmlrpc.client
import sys

# Conexão Odoo
url = 'https://odoo.semprereal.com'
db = 'realcred'
username = 'anderson@semprereal.com'
password = input("Digite sua senha Odoo: ")

print(f"Conectando ao Odoo: {url}")
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')

try:
    version = common.version()
    print(f"Odoo versão: {version['server_version']}")
except Exception as e:
    print(f"ERRO ao conectar: {e}")
    sys.exit(1)

# Autenticação
print(f"\nAutenticando como {username}...")
try:
    uid = common.authenticate(db, username, password, {})
except Exception as e:
    print(f"ERRO na autenticação: {e}")
    sys.exit(1)

if not uid:
    print("ERRO: Falha na autenticação!")
    sys.exit(1)

print(f"✅ Autenticado! UID: {uid}")

# Conexão models
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Busca módulo
print("\nBuscando módulo contact_center_sms...")
try:
    module_ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search', [
        [('name', '=', 'contact_center_sms')]
    ])
except Exception as e:
    print(f"ERRO ao buscar módulo: {e}")
    sys.exit(1)

if not module_ids:
    print("ERRO: Módulo não encontrado!")
    sys.exit(1)

module_id = module_ids[0]
print(f"✅ Módulo encontrado! ID: {module_id}")

# Verifica estado
try:
    module_data = models.execute_kw(db, uid, password, 'ir.module.module', 'read', [
        [module_id], ['name', 'state', 'shortdesc']
    ])
except Exception as e:
    print(f"ERRO ao ler módulo: {e}")
    sys.exit(1)

print(f"\nEstado atual: {module_data[0]['state']}")

if module_data[0]['state'] == 'to upgrade':
    print("\n🔄 Processando upgrade...")
    try:
        # Executa upgrade imediato
        models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_upgrade', [[module_id]])
        print("\n✅ MÓDULO ATUALIZADO COM SUCESSO!")
        print("\n🎯 Próximo passo: Criar connector SMS no ChatRoom")
        print("   ChatRoom > Configuration > Connectors > Create")
        print("   Type: SMS (Kolmeya)")
    except Exception as e:
        print(f"\n❌ ERRO ao atualizar: {e}")
        print("\nSe o erro persistir, tente pela web interface:")
        print("  Apps > Contact Center SMS Integration > Upgrade")
else:
    print(f"\n⚠️ Módulo está em estado '{module_data[0]['state']}', não 'to upgrade'")
    print("Marque como 'to upgrade' e tente novamente")
