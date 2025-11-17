# -*- coding: utf-8 -*-
{
    'name': 'Contact Center SMS Integration',
    'version': '15.0.1.0.2',
    'category': 'Marketing/SMS',
    'summary': 'Integrate SMS with WhatsApp ChatRoom for Unified Contact Center',
    'description': """
Contact Center SMS Integration
===============================

Integrates SMS (via Kolmeya) with WhatsApp ChatRoom to create a unified
contact center interface.

Features:
---------
* Unified interface for SMS and WhatsApp conversations
* Automatic conversation creation from incoming SMS
* SMS sending through ChatRoom interface
* Webhook integration for delivery status
* Agent assignment and notifications
* Message history and tracking

""",
    'author': 'SempreReal',
    'website': 'https://semprereal.com',
    'license': 'LGPL-3',
    'depends': [
        'whatsapp_connector',
        'sms_base_sr',
        'sms_kolmeya',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/icon.png'],  # ✅ ADICIONADO
    'installable': True,
    'application': True,  # ✅ MUDADO de False para True
    'auto_install': False,
}
