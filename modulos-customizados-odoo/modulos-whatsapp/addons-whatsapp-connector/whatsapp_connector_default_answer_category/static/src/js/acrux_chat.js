odoo.define('whatsapp_connector_default_answer_category.acrux_chat', function(require) {
"use strict";

const AcruxChatAction = require('whatsapp_connector.acrux_chat').AcruxChatAction
const core = require('web.core');

const _t = core._t;

/**
 * @class
 * @name AcruxChatAction
 * @extends whatsapp.AcruxChatAction
 */
AcruxChatAction.include({

    /**
     * Consulta al servidor todas las respuestas predeterminadas
     *
     * @returns {Promise}
     */
    getDefaultAnswers: function() {
        return this._super().then(() => {
            return this._rpc({
                model: 'acrux.chat.default.answer.category',
                method: 'search_read',
                args: [[], ['id', 'name', 'sequence']],
                context: this.context
            }).then(result => {
                this.category_ids = {}
                this.category_ids[0] = {
                    id: 0,
                    name: _t('No Category'),
                    sequence: 10000,
                    answers: []
                }
                for (const category of result) {
                    this.category_ids[category.id] = category
                    category.answers = []
                }
                for (const answer of this.default_answers) {
                    this.category_ids[answer.category_id[0]].answers.push(answer)
                }
                this.category_list = []
                for (const category of result) {
                    if (category.answers.length) {
                        this.category_list.push(category)
                    }
                }
                if (this.category_ids[0].answers.length) {
                    this.category_list.push(this.category_ids[0])
                }
            })
        })
    },

    /**
     * Muestra las respuestas predeterminadas
     * @returns {Promise}
     */
    showDefaultAnswers: async function() {
        const $target = this.$('div.default_table_answers')
        const $ul = $('<ul class="nav nav-tabs">')
        const $header = $('<div class="o_notebook_headers">')
        const $container = $('<div class="o_notebook" data-name="default_answer_category" style="padding-top: 1em;">')
        const $content = $('<div class="tab-content">')
        let extraClass = ' active'
        
        for await (const category of this.category_list) {
            const $el = $(`
<li class="nav-item">
    <a data-toggle="tab"
        disable_anchor="true" href="#answer_categ_${category.id}"
        class="nav-link${extraClass}" role="tab" aria-selected="true">
        ${category.name}
    </a>
</li>
            `)
            const $elContent = $(`<div class="tab-pane${extraClass}" id="answer_categ_${category.id}" >`)
            await this._showDefaultAnswers(category.answers, $elContent)
            $el.appendTo($ul)
            $elContent.appendTo($content)
            extraClass = ''
        }
        $ul.appendTo($header)
        $header.appendTo($container)
        $content.appendTo($container)
        $container.appendTo($target)
    }

})

return AcruxChatAction

})
