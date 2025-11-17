odoo.define('whatsapp_connector_helpdesk.conversation', function(require) {
"use strict";

var Conversation = require('whatsapp_connector.conversation');

/**
 * @class
 * @name Conversation
 * @extends Conversation
 */
Conversation.include({
    /**
     * @override
     * @see Conversation.init
     */
    init: function(parent, options) {
        this._super.apply(this, arguments);

        this.ticket_id = this.options.ticket_id || [false, ''];
    },

});

});
