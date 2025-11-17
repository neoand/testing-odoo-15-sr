odoo.define('whatsapp_connector_message_option.toolbox', function(require) {
"use strict";
    
var Toolbox = require('whatsapp_connector.toolbox')
var Message = require('whatsapp_connector.message');

/**
 * @class
 * @name Toolbox
 * @extends Toolbox
 */
Toolbox.include({
    events: _.extend({}, Toolbox.prototype.events, {
        'click .o_chat_toolbox_close_message': 'setQuoteMessage'
    }),

    /**
     * @override
     */
    init: function(parent, options) {
        this._super(parent, options);
        this.quoteMessage = options.quoteMessage || null
    },

   /**
     * @param {Event} [event] Evento
     *
     * @returns {Promise<Message>}
     */
    sendMessage: async function(event) {
        return this._super(event).then(msg => {
            if (msg) {
                this.setQuoteMessage(null)
            }
            return msg
        })
    },
    
    /**
     * Se coloca el mensaje cita
     * @override
     * @param {Object} options diccionario para crear un mensaje
     * @returns {Object} diccionario para crear un mensaje
     */
    sendMessageHook: function(options) {
        options = this._super(options)
        if (this.quoteMessage) {
            options.quote_id = this.quoteMessage.export_to_json()
        }
        return options
    },

    /**
     * Para cerrar el mensaje cita con escape
     *
     * @param {Event} event Evento
     */
    onKeydown: function(event) {
        this._super(event)
        if(event.which === 27) {
            this.setQuoteMessage(null);
        }
    },
    
    /**
     * Se setea el mensaje que se va a citar.
     * @param {Object} msg mesanje a citar
     */
    setQuoteMessage: function (msg) {
        if (this.quoteMessage) {
            this.quoteMessage.destroy()
        }
        this.quoteMessage = null
        if (msg && msg instanceof Message) {
            let data = msg.export_to_json()
            if (data.quote_id) {
                delete (data.quote_id)
            } 
            this.quoteMessage = new Message(this.parent.selected_conversation, data)
            this.quoteMessage.appendTo(this.$('.o_chat_toolbox_message_quote_content'))
            this.$input.focus();
            this.$('.o_chat_toolbox_close_message').removeClass('o_hidden')
        } else {
            this.$('.o_chat_toolbox_close_message').addClass('o_hidden')
        }
    } 
})

return Toolbox
})
