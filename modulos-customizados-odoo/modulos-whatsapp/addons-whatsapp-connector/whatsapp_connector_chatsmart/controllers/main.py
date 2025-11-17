# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.whatsapp_connector.controllers.main import WebhookController


class WebhookControllerApichat(http.Controller):

    @http.route('/chatsmart/whatsapp_connector/<string:connector_uuid>',
                auth='public', type='json', methods=['POST'])
    def chatroom_apichat_webhook(self, connector_uuid, **post):
        ''' Keeping URLs secret. '''
        controller = WebhookController()
        return controller.acrux_webhook(connector_uuid, **post)
