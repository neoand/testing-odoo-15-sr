odoo.define('whatsapp_connector_product_option.acrux_chat', function(require) {
"use strict";

var AcruxChatAction = require('whatsapp_connector.acrux_chat').AcruxChatAction;

/**
 * @class
 * @name AcruxChatAction
 * @extends AcruxChatAction
 */
AcruxChatAction.include({

    /**
     * @override
     * @see AcruxChatAction.getRequiredViews
     * @returns {Promise}
     */
    getRequiredViews: function() {
        return this._super().then(() => {
            return this._rpc({
                model: this.model,
                method: 'check_object_reference',
                args: ['', 'acrux_chat_message_wizard_form'],
                context: this.context
            }).then(result => {
                this.message_wizard_view_id = result[1];
            });
        });
    },

});

});
