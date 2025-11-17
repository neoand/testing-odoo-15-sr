# -*- coding: utf-8 -*-
{
    'name': 'SMS Base - SempreReal',
    'version': '15.0.1.0.2',
    'category': 'Marketing/SMS',
    'summary': 'Core SMS with Templates and Wizard',
    'description': '''
SMS Base Module for SempreReal
===============================

Features:
---------
* SMS messages management
* SMS templates
* Compose wizard
* Provider abstraction (Kolmeya, etc.)
* Partner integration
* Delivery status tracking

''',
    'author': 'SempreReal',
    'website': 'https://www.semprereal.com',
    'depends': ['base', 'mail', 'contacts'],
    'data': [
        'security/sms_security.xml',
        'security/ir.model.access.csv',
        'views/sms_message_views.xml',
        'views/sms_template_views.xml',
        'views/sms_provider_views.xml',
        'views/sms_compose_views.xml',
        'views/res_partner_views.xml',
        'views/sms_menu.xml',
    ],
    'images': ['static/description/icon.png'],  # ✅ ADICIONADO
    'installable': True,
    'application': True,  # ✅ MUDADO de False para True
    'auto_install': False,
    'license': 'LGPL-3',
}
