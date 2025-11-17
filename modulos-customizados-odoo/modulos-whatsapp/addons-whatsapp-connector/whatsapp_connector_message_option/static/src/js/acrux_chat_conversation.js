odoo.define('whatsapp_connector_message_option.conversation', function(require) {
"use strict";

var Conversation = require('whatsapp_connector.conversation');

/**
 * @class
 * @name Conversation
 * @extends whatsapp.Conversation
 */
Conversation.include({
    /**
     * Actualiza los datos de los mensajes
     *
     * @param {Array<Object>} messages Mensajes a actualizar
     * @returns {void}
     */
    updateMessages: function(messages) {
        this._super(messages)
        if (messages && this.messages && this.messages.length) {
            let show = (this.parent.selected_conversation &&
                this.parent.selected_conversation.id == this.id);
            let quoted = this.messages.filter(msg => msg.quote_id).map(msg => msg.quote_id)
            if (quoted.length) {
                messages.forEach(r => {
                    let msg = quoted.find(x => x.id == r.id);
                    if (msg) {
                        msg.update(r)
                        if (show) {
                            msg.replace();
                        }
                    }
                })
            }
        }
    },
})

return Conversation
})
