odoo.define('whatsapp_connector_helpdesk.chat_classes', function(require) {
"use strict";

var chat = require('whatsapp_connector.chat_classes');

return _.extend(chat, {
    TicketForm: require('whatsapp_connector_helpdesk.ticket'),
});
});