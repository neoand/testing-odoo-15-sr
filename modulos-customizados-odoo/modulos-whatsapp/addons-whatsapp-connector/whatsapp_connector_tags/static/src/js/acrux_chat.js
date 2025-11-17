odoo.define('whatsapp_connector_tags.acrux_chat', function(require) {
"use strict";

var AcruxChatAction = require('whatsapp_connector.acrux_chat').AcruxChatAction


/**
 * @class
 * @name AcruxChatAction
 * @extends AcruxChatAction
 */
AcruxChatAction.include({

    /**
     * @override
     */
    destroy: function() {
        // por si acaso que se queda el popup con la descripcion
        // se elimina 
        $('.acrux-note-popover').remove()
        return this._super.apply(this, arguments);
    },

})

return AcruxChatAction
})
