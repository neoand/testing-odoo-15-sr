odoo.define('whatsapp_connector_split_new_chat.init_conversation', function(require) {
"use strict";

var InitConversation = require('whatsapp_connector.chat_classes').InitConversation;
var session = require('web.session');

InitConversation.include({
    
    /**
     * @override
     * @see InitConversation.selectConversation
     * @returns {Promise}
     */
    selectConversation: function(event) {
        let conversation_id = $(event.currentTarget).data('id');
        return this._super(event).then(() => {
            let conv = this.parent.conversations.find(x => x.id == conversation_id);
            if (conv && this.parent.conv_filter == 'mines') {
                if (!conv.agent_id || conv.agent_id[0] != session.uid) {
                    let not_shown = !conv.el;
                    return this.parent.doToggleConvFilter().then(() => {
                        if (not_shown) {
                            return this.parent.selectConversation({ currentTarget: conv.el });
                        }
                    });
                }
            }
        })
    },
});

});