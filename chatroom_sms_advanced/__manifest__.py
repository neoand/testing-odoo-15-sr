# -*- coding: utf-8 -*-
{
    'name': 'ChatRoom SMS Advanced',
    'version': '15.0.2.0.0',
    'category': 'Marketing/SMS',
    'summary': 'Advanced SMS Features - Scheduling, Campaigns, Dashboard',
    'description': '''
ChatRoom SMS Advanced
=====================

Adds advanced features to the existing SMS system:

Features:
---------
PRIORITY 1 - SCHEDULING:
* Schedule SMS (one-time and recurring)
* SMS Campaigns with segments
* Bulk send optimization

PRIORITY 2 - ANALYTICS:
* Visual Dashboard (Kanban, Graph, Pivot)
* Advanced reporting
* Cost center tracking

PRIORITY 3 - MANAGEMENT:
* Blacklist enhancement
* DND (Do Not Disturb) management
* Template variables

This module EXTENDS the existing sms_base_sr and sms_kolmeya modules.
Does NOT duplicate functionality.

Requires:
- sms_base_sr (SMS Core)
- sms_kolmeya (Kolmeya Provider)
- contact_center_sms (ChatRoom Integration)

Desenvolvido por: Claude AI + Anderson Oliveira
Data: 16/11/2025
    ''',
    'author': 'Realcred - Anderson Oliveira',
    'website': 'https://realcred.com.br',
    'license': 'LGPL-3',
    'depends': [
        'sms_base_sr',           # SMS Core - REQUIRED
        'sms_kolmeya',           # Kolmeya Provider - REQUIRED
        'contact_center_sms',    # ChatRoom Integration - REQUIRED
    ],
    'data': [
        # Security
        'security/sms_advanced_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/cron_sms_scheduled.xml',
        'data/sms_campaign_templates.xml',

        # Views - NEW Models
        'views/sms_scheduled_views.xml',
        'views/sms_campaign_views.xml',
        'views/sms_blacklist_views.xml',
        'views/sms_dashboard_views.xml',

        # Views - Extends
        'views/sms_message_advanced_views.xml',
        'views/sms_provider_advanced_views.xml',

        # Wizards
        'wizard/sms_bulk_send_views.xml',

        # Menus
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'chatroom_sms_advanced/static/src/css/sms_dashboard.css',
            'chatroom_sms_advanced/static/src/js/sms_dashboard.js',
        ],
    },
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
