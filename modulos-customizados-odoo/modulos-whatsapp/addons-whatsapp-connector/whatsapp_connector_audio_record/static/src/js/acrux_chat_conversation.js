odoo.define('whatsapp_connector_audio_record.conversation', function(require) {
"use strict";

var Conversation = require('whatsapp_connector.conversation')

/**
 *
 * @class
 * @name Conversation
 * @extends whatsapp.Conversation
 */
Conversation.include({
    
    /**
     * actualiza los datos de la conversacion
     * @override
     * @param {Object} options Datos de la conversacion
     */
    update: function(options) {
        this._super(options)
        this.allow_record_audio = options.allow_record_audio || false;
    }
 
})

return Conversation
})
