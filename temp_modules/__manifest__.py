# -*- coding: utf-8 -*-
{
    'name': 'SMS Base - SempreReal',
    'version': '15.0.1.0.1',
    'category': 'Marketing/SMS',
    'summary': 'Core SMS with Templates and Wizard',
    'description': '''
SMS Base Module for SempreReal - Features: SMS messages, templates, wizard, provider abstraction
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
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
