# -*- coding: utf-8 -*-
{
    'name': 'SMS Kolmeya Provider',
    'version': '15.0.1.0.0',
    'category': 'Marketing/SMS',
    'summary': 'Kolmeya SMS Gateway Integration',
    'description': '''
Kolmeya SMS Provider for SempreReal
====================================

Kolmeya-specific implementation of SMS provider:
- KolmeyaAPI wrapper class
- Provider configuration model
- Webhook handlers for replies and delivery status
- JWT authentication for webhooks
- Rate limiting protection
- Batch sending (up to 1000 messages)

Requires sms_base_sr module.
    ''',
    'author': 'SempreReal',
    'website': 'https://www.semprereal.com',
    'depends': ['sms_base_sr'],
    'external_dependencies': {
        'python': ['PyJWT'],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/sms_provider_data.xml',
        'views/sms_provider_kolmeya_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
