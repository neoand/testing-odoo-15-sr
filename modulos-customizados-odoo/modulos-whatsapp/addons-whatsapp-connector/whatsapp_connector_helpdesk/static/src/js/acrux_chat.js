odoo.define('whatsapp_connector_helpdesk.acrux_chat', function(require) {
"use strict";

var chat = require('whatsapp_connector_helpdesk.chat_classes');
var AcruxChatAction = require('whatsapp_connector.acrux_chat').AcruxChatAction
var core = require('web.core');

var _t = core._t;
var QWeb = core.qweb;


/**
 * @class
 * @name AcruxChatAction
 * @extends AcruxChatAction
 */
AcruxChatAction.include({
    events: _.extend({}, AcruxChatAction.prototype.events, {
        'click li#tab_ticket': 'tabTicket',
    }),

    /**
     * Hace trabajos de render
     *
     * @private
     * @returns {Promise} Para indicar que termino
     */
    _initRender: function() {
        return this._super().then(() => {
            this.$tab_content_ticket = this.$('div#tab_content_ticket > div.o_group');
        });
    },

    /**
     * Cuando se hace clic en el tab de ticket, se muestra un formulario
     * de helpdeks.ticket
     *
     * @param {Event} _event
     * @param {Object} data
     * @return {Promise}
     */
    tabTicket: function(_event, data) {
        let out = Promise.reject()

        if (this.selected_conversation) {
            if (this.selected_conversation.isMine()) {
                let ticket_id = this.selected_conversation.ticket_id;
                this.saveDestroyWidget('ticket_id_form')
                let options = {
                    context: this.action.context,
                    ticket_id: ticket_id,
                    action_manager: this.action_manager,
                    searchButton: true,
                    title: _t('Helpdesk'),
                }
                this.ticket_id_form = new chat.TicketForm(this, options)
                this.$tab_content_ticket.empty()
                out = this.ticket_id_form.appendTo(this.$tab_content_ticket);
            } else {
                this.$tab_content_ticket.html(QWeb.render('acrux_empty_tab', {notYourConv: true}))
            }
        } else {
            this.$tab_content_ticket.html(QWeb.render('acrux_empty_tab'))
        }
        out.then(() => data && data.resolve && data.resolve())
        out.catch(() => data && data.reject && data.reject())
        return out
    },

    /**
     * @override
     * @see AcruxChatAction.tabsClear
     */
    tabsClear: function() {
        this._super();
        this.saveDestroyWidget('ticket_id_form')
    },
    
    /**
     * @override
     * @see AcruxChatAction._getMaximizeTabs
     */
    _getMaximizeTabs: function() {
        let out = this._super();
        out.push("#tab_content_ticket")
        return out;
    },

    /**
     * Devuelve si el controlador es parte de chatroom, es util para los tabs
     * @param {String} jsId id del controllador
     * @returns {Boolean}
     */
    isChatroomTab: function(jsId) {
        return this._super(jsId) || this._isChatroomTab('ticket_id_form', jsId)
    },
})

});
