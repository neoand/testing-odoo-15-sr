#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para instalar contact_center_sms via XML-RPC
"""
import xmlrpc.client

# Conexão Odoo
url = 'https://odoo.semprereal.com'
db = 'realcred'
username = 'anderson@semprereal.com'
password = '********'  # Usuário precisa fornecer

print(f"Conectando ao Odoo: {url}")
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
version = common.version()
print(f"Odoo versão: {version['server_version']}")

# Autenticação
print(f"\nAutenticando como {username}...")
uid = common.authenticate(db, username, password, {})
if not uid:
    print("ERRO: Falha na autenticação!")
    print("Por favor, execute o script manualmente com sua senha:")
    print("python3 install_contact_center_sms.py")
    exit(1)

print(f"Autenticado! UID: {uid}")

# Conexão models
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Busca módulo contact_center_sms
print("\nBuscando módulo contact_center_sms...")
module_ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search', [
    [('name', '=', 'contact_center_sms')]
])

if not module_ids:
    print("ERRO: Módulo contact_center_sms não encontrado!")
    print("Tentando atualizar lista de apps primeiro...")

    # Atualiza lista
    models.execute_kw(db, uid, password, 'ir.module.module', 'update_list', [[]])
    print("Lista de apps atualizada!")

    # Busca novamente
    module_ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search', [
        [('name', '=', 'contact_center_sms')]
    ])

    if not module_ids:
        print("ERRO: Módulo ainda não encontrado após atualizar lista!")
        exit(1)

module_id = module_ids[0]
print(f"Módulo encontrado! ID: {module_id}")

# Verifica estado atual
module_data = models.execute_kw(db, uid, password, 'ir.module.module', 'read', [
    [module_id], ['name', 'state', 'shortdesc']
])
print(f"\nEstado atual: {module_data[0]['state']}")
print(f"Descrição: {module_data[0]['shortdesc']}")

if module_data[0]['state'] == 'installed':
    print("\n✅ Módulo JÁ INSTALADO!")
    print("Para atualizar, execute:")
    print(f"  Odoo web > Apps > Contact Center SMS Integration > Upgrade")
else:
    # Instala módulo
    print("\nInstalando contact_center_sms...")
    try:
        models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [[module_id]])
        print("\n✅ MÓDULO INSTALADO COM SUCESSO!")
    except Exception as e:
        print(f"\n❌ ERRO ao instalar: {e}")
        print("\nTente instalar manualmente via web:")
        print("  Odoo web > Apps > Search 'contact_center_sms' > Install")
