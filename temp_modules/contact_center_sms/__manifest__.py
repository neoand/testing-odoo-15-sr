# -*- coding: utf-8 -*-
{
    'name': 'Contact Center SMS Integration',
    'version': '15.0.1.0.0',
    'category': 'Marketing/SMS',
    'summary': 'Integrate SMS with WhatsApp ChatRoom for Unified Contact Center',
    'description': """
Contact Center Unificado - SMS + WhatsApp
==========================================

Este módulo integra SMS (Kolmeya) com o WhatsApp ChatRoom (AcruxLab),
criando um Contact Center unificado onde agentes podem atender SMS e
WhatsApp na mesma interface.

Funcionalidades:
----------------
* Conversas SMS integradas ao ChatRoom
* Interface única para SMS + WhatsApp
* Mesma fila de atendimento
* Histórico unificado por parceiro
* Templates compartilhados
* Dashboard consolidado

Arquitetura:
------------
* Herda acrux.chat.conversation para SMS
* Adiciona channel_type (sms/whatsapp/instagram)
* Reutiliza features: Kanban, Agents, Templates, Bus
* Aproveita 60% do código ChatRoom existente

Desenvolvido para SempreReal - Novembro 2025
    """,
    'author': 'SempreReal',
    'website': 'https://semprereal.com',
    'license': 'LGPL-3',
    'depends': [
        'whatsapp_connector',  # AcruxLab ChatRoom
        'sms_base_sr',         # Nossa base SMS
        'sms_kolmeya',         # Kolmeya provider
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/conversation_views.xml',
        'views/connector_sms_views.xml',
        'views/message_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
