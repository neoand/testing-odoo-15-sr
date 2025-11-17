# -*- coding: utf-8 -*-
# =====================================================================================
# License: OPL-1 (Odoo Proprietary License v1.0)
#
# By using or downloading this module, you agree not to make modifications that
# affect sending messages through Acruxlab or avoiding contract a Plan with Acruxlab.
# Support our work and allow us to keep improving this module and the service!
#
# Al utilizar o descargar este módulo, usted se compromete a no realizar modificaciones que
# afecten el envío de mensajes a través de Acruxlab o a evitar contratar un Plan con Acruxlab.
# Apoya nuestro trabajo y permite que sigamos mejorando este módulo y el servicio!
# =====================================================================================
{
    'name': 'Send by apichat.io ChatRoom WhatsApp',
    'summary': 'Send via apichat.io without purchasing a Plan on acruxlab.com. ChatRoom 2.0.',
    'description': 'Send via apichat.io without purchasing a Plan on acruxlab.com. ChatRoom 2.0.',
    'version': '15.0.3',
    'author': 'AcruxLab',
    'live_test_url': 'https://chatroom.acruxlab.com/web/signup',
    'support': 'info@acruxlab.com',
    'price': 500.0,
    'currency': 'USD',
    # 'images': ['static/description/Banner_apichat_direct.gif'],
    'website': 'https://apichat.io',
    'license': 'OPL-1',
    'application': True,
    'installable': True,
    'category': 'Discuss/Sales/CRM',
    'depends': [
        'whatsapp_connector',
    ],
    'data': [
        'views/connector_views.xml'
    ],
    'qweb': [
    ],
    'post_load': '',
    'external_dependencies': {'python': ['vobject']},
}
