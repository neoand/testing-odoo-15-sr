odoo.define('whatsapp_connector_message_option.message', function(require) {
"use strict";
    
var Message = require('whatsapp_connector.message')

/**
 * @class
 * @name Message
 * @extends Message
 */
Message.include({
    events: _.extend({}, Message.prototype.events, {
        'click div.acrux_chat_message_quote': 'clickQuoteMessage',
    }),

    /**
     * @override
     * @see Widget.init
     */
    init: function(parent, options) {
        let current = parent
        
        while(current && !this.conversation) {
            if (current instanceof Message) {
                current = current.parent
            } else {
                this.conversation = current
            }
        }
        this._super.apply(this, arguments);
    },
    
    /**
     * @override
     */
    update: function(options) {
        this._super(options)
        this.date_delete = options.date_delete || false;
        this.convertDate('date_delete')
        if (options.quote_id) {
            if (options.quote_id instanceof Message) {
                this.quote_id = options.quote_id
            } else {
                this.quote_id = new Message(this, options.quote_id)
            }
        } else {
            this.quote_id = null
        } 
    },
    
    /**
     * @override
     * @returns {Promise} Para indicar que termino
     */
    _initRender: function() {
        return this._super().then(() => {
            if (this.quote_id) {
                return this.quote_id.appendTo(this.$('div.acrux_chat_message_quote')).then(() => {
                    if (this.quote_id.res_model_obj && this.quote_id.isAttachmentComponent()) {
                        let comp = null
                        if (this.quote_id.res_model_obj.attachmentImage) {
                            comp = this.quote_id.res_model_obj.attachmentImage
                            this.quote_id.el.querySelector('.o_AttachmentImage_imageOverlay').dataset['is_quote'] = true
                        }
                        if (this.quote_id.res_model_obj.attachmentCard) {
                            comp = this.quote_id.res_model_obj.attachmentCard
                            this.quote_id.el.querySelector('.o_AttachmentCard_image').dataset['is_quote'] = true
                        }
                        if (comp) {
                            const onClickImage = comp.onClickImage
                            comp.onClickImage = (ev) => {
                                if (!(ev.target.dataset.is_quote)) {
                                    onClickImage.apply(comp, arguments)
                                }
                            }
                        }
                    }
                })
            }
        })
    },
    
    /**
     * Retorna una lista de las classes CSS para aplicarlas al contendio del mensaje
     * @returns {Array<String>}
     */
    message_css_class_list: function() {
        let out = this._super()
        if (this.date_delete) {
            out.push('o_chat_msg_deleted')
        }
        return out
    },
    
    /**
     * @override
     * @returns {Object}
     */
    export_to_json: function() {
        let out = this._super()
        out.date_delete = this.date_delete
        if (this.quote_id) {
            out.quote_id = this.quote_id.export_to_json()
        }
        return out
    },

    /**
     * @override 
     * @returns {Object}
     */
    export_to_vals: function() {
        let out = this._super()
        if (out.quote_id) {
            out.quote_id = out.quote_id.id;
        }
        return out;
    },

    /**
     * Ataja el evento cuando le dan click a un mensaje citado
     * @param {Event} ev evento
     */
    clickQuoteMessage: function(ev) {
        ev.stopPropagation()
        const msg = this.conversation.messages.find(msg => msg.id === this.quote_id.id)
        if (msg) {
            msg.el.scrollIntoView({block: 'nearest', inline: 'start' })
            setTimeout(() => msg.el.classList.add('active_quote'), 400)
            setTimeout(() => msg.el.classList.remove('active_quote'), 800)
            setTimeout(() => msg.el.classList.add('active_quote'), 1200)
            setTimeout(() => msg.el.classList.remove('active_quote'), 1600)
        } else {
            this.conversation.messages[0].el.scrollIntoView({block: 'nearest', inline: 'start' })
        }
    },
    
    /**
     * Permite activar o desactivar la opcion de responder mensaje
     * @returns {Boolean}
     */
    canBeAnswered: function() {
        return this._super() && !this.date_delete        
    },

    /**
     * Permite activar o desactivar la opcion de borrar mensaje
     * @returns {Boolean}
     */    
    canBeDeleted: function() {
        return this._super() && this.from_me && !this.date_delete
    },
    
})

return Message

})
