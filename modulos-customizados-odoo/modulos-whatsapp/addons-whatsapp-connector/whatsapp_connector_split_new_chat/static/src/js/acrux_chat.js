odoo.define('whatsapp_connector_split_new_chat.acrux_chat', function(require) {
"use strict";

var AcruxChatAction = require('whatsapp_connector.acrux_chat').AcruxChatAction;
var session = require('web.session');


AcruxChatAction.include({
    events: _.extend({}, AcruxChatAction.prototype.events, {
        'click label#chat_filter_my': 'toggleConvFilter',
        'click label#chat_filter_all': 'toggleConvFilter',
    }),

    /**
     * @override
     */
    init: function (parent, options) {
        this._super.apply(this, arguments);
        this.conv_filter = 'mines';
    },
    
    /**
     * Intercambia el filtro de las conversaciones
     *
     *  @param {Event} event
     *  @returns {Promise}
     */
    toggleConvFilter: function(event) {
        let out, flag = false;
        if ($(event.target).attr('id') == 'chat_filter_my') {
            flag = this.conv_filter != 'mines';
        } else {
            flag = this.conv_filter != 'all';
        }
        if (flag) {
            out = this.doToggleConvFilter();
        } else {
            out = Promise.resolve();
        }
        return out;
    },
    
    /**
     * Hace el intercambio del filtro de las conversaciones.
     *
     * @returns {Promise}
     */
    doToggleConvFilter: function() {
        let defs = [];
        if (this.conv_filter == 'mines') {
            this.conv_filter = 'all';
        } else {
            this.conv_filter = 'mines';
        }
        this.$('label#chat_filter_my').toggleClass('active');
        this.$('label#chat_filter_all').toggleClass('active');
        this.$new_chats.html('');
        this.getNewConversation().forEach(x => defs.push(this.renderNewConversation(x)));
        return Promise.all(defs); 
    },

    /**
     * Returna la lista de mensajes nuevos
     *
     * @returns {Array<Conversation>}
     */
    getNewConversation: function() {
        let filter = x => {
            let flag = false;
            if (this.conv_filter == 'mines') {
                flag = x.agent_id && x.agent_id[0] == session.uid;
            } else {
                flag = true;
            }
            return flag;
        }
        let tmp_arr = this.getCurrentConversation();
        return this.conversations.filter(x => !tmp_arr.includes(x) && filter(x));
    },

    /**
     * @override
     * @returns {Promise}
     */    
    renderNewConversation: function(conv) {
        let out, render = false;
        if (this.conv_filter == 'mines') {
            render = conv.agent_id && conv.agent_id[0] == session.uid;
        } else {
            render = true;
        }
        if (render) { 
            out = conv.appendTo(this.$new_chats);
        } else {
            out = Promise.resolve();
        }
        return out;
    },
});

});
