# -*- coding: utf-8 -*-
"""
SMS Core Unified Manifest
CONTEÚDO para __manifest__.py
"""

{
    'name': 'SMS Core Unified',
    'version': '1.0.0',
    'category': 'Communication',
    'summary': 'Unified SMS Messaging System - Resolves action_send() conflicts',
    'description': """
SMS Core Unified - Sistema Unificado de SMS
=========================================

Módulo CRÍTICO que resolve o conflito do método action_send() entre:
- sms_base_sr
- chatroom_sms_advanced

FUNCIONALIDADES:
✅ Modelo SMS Message unificado
✅ Envio via providers configurados
✅ Verificação de blacklist
✅ Cálculo automático de custo
✅ Interface completa para gestão de SMS
✅ Integração com chatter e atividades

BENEFÍCIOS:
❌ FIM dos conflitos de override
✅ Single source of truth para SMS
✅ Performance otimizada
✅ Compatibilidade com módulos existentes
    """,
    'author': 'Anderson Oliveira + Claude',
    'website': 'https://github.com/neoand',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'contacts',
        'sales_team',  # Para access rights
    ],
    'data': [
        # Security
        'security/sms_security.xml',

        # Views
        'views/sms_message_views.xml',

        # Menus
        'views/sms_menu.xml',

        # Data (providers padrão, templates, etc)
        'data/sms_data.xml',
    ],
    'demo': [
        'demo/sms_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'images': [
        'static/description/main.png',
    ],
    'price': 0.00,
    'currency': 'BRL',
    'live_test_url': 'http://35.199.92.1:8069',
    'support': 'anderson.goliveira@gmail.com',
}