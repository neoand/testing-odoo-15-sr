odoo.define('whatsapp_connector_helpdesk.ticket', function(require) {
"use strict";

var FormView = require('whatsapp_connector.form_view');

/**
 * Widget que maneja el formulario del Helpdesk Ticket
 *
 * @class
 * @name ResPartnerForm
 * @extends web.Widget.FormView
 * @see acrux_chat.form_view
 */
var TicketForm = FormView.extend({
    /**
     * @override
     * @see Widget.init
     */
    init: function(parent, options) {
        if (options) {
            options.model = 'helpdesk.ticket';
            options.record = options.ticket_id;
        }
        this._super.apply(this, arguments);

        this.parent = parent;
        _.defaults(this.context, {
            default_partner_id: this.parent.selected_conversation.res_partner_id[0],
        });
    },

    /**
     * @override
     * @see FormView.start
     */
    start: function() {
        return this._super().then(() => this.parent.product_search.minimize());
    },

    /**
     * @override
     * @see FormView.recordUpdated
     * @returns {Promise}
     */
    recordUpdated: function(record) {
        return this._super(record).then(() => {
            if (record && record.data && record.data.id) {
                let ticket_key, partner_key, partner_id, localData;
                ticket_key = this.acrux_form_widget.handle;
                localData = this.acrux_form_widget.model.localData;
                if (ticket_key) {
                    partner_key = localData[ticket_key].data.partner_id;
                }
                if (partner_key) {
                    partner_id = localData[partner_key];
                }
                this.parent.setNewPartner(partner_id);
            }
        });
    },

    /**
     * @override
     * @see FormView.recordChange
     * @returns {Promise}
     */
    recordChange: function(ticket) {
        return Promise.all([
            this._super(ticket),
            this._rpc({
                model: this.parent.model,
                method: 'write',
                args: [[this.parent.selected_conversation.id], {ticket_id: ticket.data.id}]
            }).then(isOk => {
                if (isOk) {
                    let result = [ticket.data.id, ticket.data.name];
                    this.parent.selected_conversation.ticket_id = result;
                    this.record = result;
                }
            })
        ]);
    },

    /**
     * @override
     * @see FormView._getOnSearchChatroomDomain
     * @returns {Array<Array<Object>>}
     */
    _getOnSearchChatroomDomain: function() {
        /** @type {Array} */
        let domain = this._super()
        domain.push(['conversation_id', '=', this.parent.selected_conversation.id])
        if (this.parent.selected_conversation.res_partner_id && this.parent.selected_conversation.res_partner_id[0]) {
            domain.unshift('|')
            domain.push(['partner_id', '=', this.parent.selected_conversation.res_partner_id[0]])
        }
        return domain
    },

})

return TicketForm
})
