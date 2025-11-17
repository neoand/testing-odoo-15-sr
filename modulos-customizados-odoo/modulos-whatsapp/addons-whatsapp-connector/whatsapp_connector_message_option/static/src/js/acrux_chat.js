odoo.define('whatsapp_connector_message_option.acrux_chat', function(require) {
"use strict";

var AcruxChatAction = require('whatsapp_connector.acrux_chat').AcruxChatAction
var Dialog = require('web.Dialog');
var core = require('web.core');
var _t = core._t;


/**
 * @class
 * @name AcruxChatAction
 * @extends AcruxChatAction
 */
AcruxChatAction.include({
    events: _.extend({}, AcruxChatAction.prototype.events, {
        'click span.o_chat_message_options': 'showMessageOption',
        'click span#option_delete_message': 'deleteMessageDialog',
        'click span#option_answer_message': 'answerMessage',
    }),

    /**
     * @override
     * @returns {Promise}
     */
    changeStatusView: function() {
        return this._super().then(() => this.toolbox.setQuoteMessage(null))
    },

    /**
     * @override
     * @param {Event} event
     * @returns {Promise}
     */
    selectConversation: function(event) {
        let conv_bak = this.selected_conversation
        
        return this._super(event).then(() => {
            if (this.selected_conversation != conv_bak) {
                this.toolbox.setQuoteMessage(null);
            }
        })
    },

    /**
     * Agrega las opciones del mensaje al popover
     * @override
     * @returns {String}
     */
    popoverOptions: function() {
        let out
        if (this.popoverOption && this.popoverOption.option === 'message_menu') {
            const msgId = parseInt(this.popoverOption.event.currentTarget.dataset.id)
            const msg = this.selected_conversation.messages.find(msg => msg.id === msgId)
            const answerLabel = _t('Answer')
            const deleteLabel = _t('Delete')
            const deleteOption = `<span id="option_delete_message">${deleteLabel}</span>`
            const answerOption = `<span id="option_answer_message">${answerLabel}</span>`
            if (this.selected_conversation.isMine()) {
                out = `
                  <div id="menu_message_option" class="dropdown-content">
                    ${msg && msg.canBeAnswered() ? answerOption : ''}
                    ${msg && msg.canBeDeleted() ? deleteOption : ''}
                  </div>
                `
            } else {
                out = ''
            }
        } else {
            out = this._super()
        }
        return out
    },

    /**
     * Muestra el menú de opciones del los mensajes
     * @param {Event} event
     */
    showMessageOption: function(event) {
        event.stopPropagation()
        this.popoverOption = {
            option: 'message_menu',
            event: event, 
        }
        this.$el.popover("show")
    },

    /**
     * Muestra un dialogo para confirmar eliminar
     */
    deleteMessageDialog: function() {
        this.$el.popover("hide")
        if (this.popoverOption && this.selected_conversation) { 
            const msgId = parseInt(this.popoverOption.event.currentTarget.dataset.id)
            const msg = this.selected_conversation.messages.find(msg => msg.id === msgId)
            if (msg) {
                let buttons = [{
                    text: _t('Delete for me'),
                    classes: 'btn-primary',
                    close: true,
                    click: () => { this.deleteMessage(msgId, true) },
                }]
                if (msg.from_me) {
                    /** tiene maximo una hora para borrar un mesanje */
                    let allowDeleteAll = true
                    const now = moment()
                    if (now.diff(msg.date_message, "days") > 0) {
                        allowDeleteAll = false
                    } else if (now.diff(msg.date_message, "minutes") > 59) {
                        allowDeleteAll = false
                    }
                    if (allowDeleteAll) {
                        buttons.push({
                            text: _t('Delete for all'),
                            classes: 'btn-primary',
                            close: true,
                            click: () => { this.deleteMessage(msgId, false) },
                        })
                    }
                }
                buttons.push({ text: _t('Cancel'), close: true })
                Dialog.confirm(this, _t('Do you want delete this message?'),
                    {buttons: buttons})
            }
        }
    },

    /**
     * Borra un mensaje
     * @param {String} msgId id del mensaje a eliminar
     * @param {Boolean} forMe solo borrar para mi?
     * @return {Promise}
     */
    deleteMessage: function(msgId, forMe) {
        return this._rpc({
            model: this.model,
            method: 'delete_message',
            args: [[this.selected_conversation.id], msgId, forMe],
            context: this.context
        }).then(msgData => {
            this.selected_conversation.updateMessages(msgData)
        })
    },

    /**
     * Setea un mensaje como para responder
     * @param {Event} event
     */
    answerMessage: function() {
        this.$el.popover("hide")
        if (this.popoverOption && this.selected_conversation) { 
            const msgId = parseInt(this.popoverOption.event.currentTarget.dataset.id)
            const msg = this.selected_conversation.messages.find(msg => msg.id === msgId)
            if (msg) {
                this.toolbox.setQuoteMessage(msg)
            }
        }
    },

    /**
     * @override
     */
    removeSelectedConversation: function() {
        this._super()
        this.toolbox.setQuoteMessage(null)
    },

});

});
