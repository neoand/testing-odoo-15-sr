odoo.define('whatsapp_connector_product_option.product_search', function(require) {
"use strict";

var ProductSearch = require('whatsapp_connector.product_search');

/**
 *
 * @class
 * @name ProductSearch
 * @extends whatsapp.ProductSearch
 */
ProductSearch.include({
    events: _.extend({}, ProductSearch.prototype.events, {
        'click .acrux_open_send_wizard': 'productOptions',
    }),

    /**
     * @override
     * @param {String} product el producto a procesar
     * @param {Event} event el evento que se ejecutó
     * @return {Promise}
     */
    doProductOption: function(product, event) {
        let out
        if (event.target.classList.contains('acrux_open_send_wizard')) {
            out = this.do_action(this.getProductOptionAction(product.id))
        } else {
            out = this._super(product, event)
        }
        return out
    },
    
    /**
     * Construye el diccionario para llamar a la acción del wizard del producto
     *
     * @param {Integer} product_id Id del producto a enviar
     * @returns {Object}
     */
    getProductOptionAction: function(product_id) {
        let context = this.context;
        context = _.extend({
            default_conversation_id: this.parent.selected_conversation.id,
            active_model: 'product.product',
            active_id: product_id,
            default_invisible_top: true
        }, context);
        return {
            name: 'Send ChatRoom Message',
            type: 'ir.actions.act_window',
            view_type: 'form',
            view_mode: 'form',
            res_model: 'acrux.chat.message.wizard',
            views: [[this.parent.message_wizard_view_id, 'form']],
            target: 'new',
            context: context,
        };
    },
});

return ProductSearch;
});
