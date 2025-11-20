#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para melhorar views com interface moderna e responsiva
FASE 1 - Funcionalidade 10
"""

import re

# 1. MELHORAR sms_message_views.xml
message_views_file = '/tmp/sms_message_views_current.xml'
with open(message_views_file, 'r') as f:
    message_views_content = f.read()

# Adicionar campos de segmentos e melhorar form view
form_view_improvements = """
                <field name="segment_count" widget="integer"/>
                <field name="estimated_cost" widget="monetary" options="{'currency_field': 'currency_id'}"/>
                <field name="actual_cost" widget="monetary" options="{'currency_field': 'currency_id'}"/>
"""

# Adicionar botão de check status
status_button = """
                <button name="action_check_status" string="Check Status" type="object" 
                        class="oe_highlight" icon="fa-refresh"
                        attrs="{'invisible': [('state', 'in', ['draft', 'canceled']), ('external_id', '=', False)]}"/>
"""

# Verificar se campos de segmentos já estão na view
if 'segment_count' not in message_views_content:
    # Adicionar campos após cost
    message_views_content = message_views_content.replace(
        '<field name="cost"',
        form_view_improvements + '                <field name="cost"'
    )
    print("✅ Campos de segmentos adicionados na view de mensagem")

# Adicionar botão de check status
if 'action_check_status' not in message_views_content:
    # Adicionar botão no header ou após statusbar
    pattern = r'(<header>.*?</header>)'
    if re.search(pattern, message_views_content, re.DOTALL):
        replacement = r'\1' + status_button
        message_views_content = re.sub(pattern, replacement, message_views_content, flags=re.DOTALL)
        print("✅ Botão de check status adicionado")
    else:
        # Adicionar após statusbar
        pattern = r'(<field name="state" widget="statusbar".*?/>)'
        replacement = r'\1' + status_button
        message_views_content = re.sub(pattern, replacement, message_views_content, flags=re.DOTALL)
        print("✅ Botão de check status adicionado após statusbar")

# Melhorar tree view para mostrar segmentos
tree_view_improvements = """
                <field name="segment_count" optional="show"/>
                <field name="estimated_cost" widget="monetary" optional="show"/>
"""

if 'segment_count' not in message_views_content or 'tree' in message_views_content:
    # Adicionar campos na tree view
    pattern = r'(<tree.*?<field name="cost".*?/>)'
    if re.search(pattern, message_views_content, re.DOTALL):
        replacement = r'\1' + tree_view_improvements
        message_views_content = re.sub(pattern, replacement, message_views_content, flags=re.DOTALL)
        print("✅ Campos de segmentos adicionados na tree view")

# Salvar views modificadas
with open('/tmp/sms_message_views_improved.xml', 'w') as f:
    f.write(message_views_content)

# 2. MELHORAR sms_provider_views.xml
provider_views_file = '/tmp/sms_provider_views_current.xml'
with open(provider_views_file, 'r') as f:
    provider_views_content = f.read()

# Adicionar botões de webhook
webhook_buttons = """
                <button name="action_configure_webhook" string="Configure Webhook" type="object" 
                        class="oe_highlight" icon="fa-link"
                        attrs="{'invisible': [('provider_type', '!=', 'kolmeya')]}"/>
                <button name="action_validate_webhook" string="Validate Webhook" type="object" 
                        class="btn-secondary" icon="fa-check"
                        attrs="{'invisible': [('provider_type', '!=', 'kolmeya')]}"/>
"""

# Adicionar campo cost_per_segment
cost_field = """
                <field name="cost_per_segment" widget="monetary" options="{'currency_field': 'currency_id'}"/>
"""

if 'action_configure_webhook' not in provider_views_content:
    # Adicionar botões após action_test_connection
    pattern = r'(<button name="action_test_connection".*?/>)'
    if re.search(pattern, provider_views_content, re.DOTALL):
        replacement = r'\1' + webhook_buttons
        provider_views_content = re.sub(pattern, replacement, provider_views_content, flags=re.DOTALL)
        print("✅ Botões de webhook adicionados na view de provider")

if 'cost_per_segment' not in provider_views_content:
    # Adicionar campo após balance
    pattern = r'(<field name="balance".*?/>)'
    if re.search(pattern, provider_views_content, re.DOTALL):
        replacement = r'\1' + cost_field
        provider_views_content = re.sub(pattern, replacement, provider_views_content, flags=re.DOTALL)
        print("✅ Campo cost_per_segment adicionado na view de provider")

# Salvar views modificadas
with open('/tmp/sms_provider_views_improved.xml', 'w') as f:
    f.write(provider_views_content)

print("\n✅ Arquivos modificados criados:")
print("   - /tmp/sms_message_views_improved.xml")
print("   - /tmp/sms_provider_views_improved.xml")

