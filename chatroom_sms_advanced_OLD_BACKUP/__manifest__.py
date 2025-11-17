# -*- coding: utf-8 -*-
{
    'name': 'ChatRoom SMS Advanced - The Best SMS Module Ever',
    'version': '15.0.1.0.0',
    'category': 'Chatroom/SMS',
    'summary': 'O módulo de SMS mais completo do planeta para Odoo 15',
    'description': """
        ChatRoom SMS Advanced
        =====================

        O módulo de SMS mais completo e profissional para Odoo 15!

        Funcionalidades:
        ----------------
        PRIORIDADE 1 - ESSENCIAL:
        * Webhooks automáticos de status (entregue/falhou/respondeu)
        * Consulta automática de saldo com alertas
        * Sistema completo de blacklist e "Não Perturbe"

        PRIORIDADE 2 - GESTÃO:
        * Log completo de TODOS os SMS enviados
        * Envio em lote (até 1000 mensagens por vez)
        * Dashboard visual com estatísticas e gráficos

        PRIORIDADE 3 - PRODUTIVIDADE:
        * Sistema de templates de mensagens
        * Agendamento de envios
        * Rastreamento de links curtos
        * Autenticação 2FA via SMS

        EXTRAS:
        * Relatórios avançados por período
        * Centros de custo
        * Analytics completo
        * API REST para integração externa

        Compatível com API Kolmeya SMS

        Desenvolvido por: Claude AI + Anderson Oliveira
        Data: 16/11/2025
    """,
    'author': 'Realcred - Anderson Oliveira',
    'website': 'https://realcred.com.br',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'chatroom',  # Módulo chatroom base
    ],
    'data': [
        # Security
        'security/sms_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/cron_sms_balance.xml',
        'data/cron_sms_scheduled.xml',
        'data/config_parameters.xml',
        'data/sms_templates_default.xml',

        # Views - Config
        'views/chatroom_sms_api_views.xml',
        'views/chatroom_sms_segment_views.xml',

        # Views - Operations
        'views/chatroom_conversation_views.xml',
        'views/chatroom_room_views.xml',
        'views/chatroom_sms_log_views.xml',
        'views/chatroom_sms_template_views.xml',
        'views/chatroom_sms_scheduled_views.xml',

        # Views - Reports
        'views/chatroom_sms_dashboard_views.xml',
        'views/chatroom_sms_report_views.xml',

        # Wizards
        'wizard/chatroom_send_bulk_sms_views.xml',
        'wizard/chatroom_sms_test_views.xml',

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
