odoo.define('whatsapp_connector_default_answer_category.default_answer', function(require) {
"use strict";
    
const DefaultAnswer = require('whatsapp_connector.default_answer')
const session = require('web.session')

/**
 * @class
 * @name DefaultAnswer
 * @extends DefaultAnswer
 */
DefaultAnswer.include({

    /**
     * @override
     * @see Widget.init
     */
    init: function(parent, options) {
        this._super.apply(this, arguments)

        if (this.options.category_id && this.options.category_id[0]) {
            this.category_id = this.options.category_id
        } else {
            this.category_id = [0, '']
        }
    },

    /**
     * @param {Event} [event]
     * @returns {Promise<void>}
     */
    sendAnswer: async function(event) {
        let out
        if (session.chatroom_edit_default_answer && 'text' === this.ttype) {
            this.parent.toolbox.setInputText(this.text)
        } else {
            out = this._super(event)
        }
        return out
    },

})

return DefaultAnswer
})
