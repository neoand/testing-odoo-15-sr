odoo.define('whatsapp_connector_tags.conversation', function(require) {
"use strict";

var config = require('web.config');
var Conversation = require('whatsapp_connector.conversation');
var core = require('web.core');
var _t = core._t;

/**
 *
 * @class
 * @name Conversation
 * @extends whatsapp.Conversation
 */
Conversation.include({
    events: _.extend({}, Conversation.prototype.events, {
        'mouseenter': '_onMouseEnter',
        'mouseleave': '_onMouseLeave',
    }),

    /**
     * @override
     * @see Widget.start
     */
    start: function() {
        return this._super().then(() => {
            if (this.note) {
                this.$el.popover({
                    trigger: 'manual',
                    animation: true,
                    html: true,
                    title: function () {
                        return _t("Note");
                    },
                    container: 'body',
                    placement: 'left',
                    template: '<div class="popover acrux-note-popover" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'
                }).on('inserted.bs.popover', () => {
                    if (!config.device.isMobile) {
                        setTimeout(() => this.fix_popover_position(), 50);
                    }
                });
            }
        });
    },

    /**
     * @override
     * @see Conversation.update
     */
    update: function(options) {
        this._super.apply(this, arguments);
        this.tag_ids = options.tag_ids || false;
        this.note = options.note || false;
    },

    /**
     * corrige la posicion del popover
     */
    fix_popover_position: function() {
        let popover = $('.acrux-note-popover');
        if (popover.length) {
            let data = this.$el[0].getBoundingClientRect();
            let left = data.left;
            let width = data.width;
            let transform = popover.css('transform')
            if (transform) {
                let matrix = transform.replace(/[^0-9\-.,]/g, '').split(',');
                let x = matrix[12] || matrix[4];
                x = isNaN(x) ? 0 : (x < 0) ? Math.abs(x) : x * -1;
                popover.css('left', left + width + x);
            }
        }
    },
 
     /**
     * @private
     * @param {Event} ev
     */
    _onMouseEnter: function (ev) {
        if (this.note) {
            clearTimeout(this.note_timeout);
            this.note_timeout = setTimeout(() => {
                if (!this.$el.is(':hover') || $('.acrux-note-popover:visible').length) {
                    return;
                }
                this.$el.data("bs.popover").config.content = '<h5>' + this.note + '</h5>';
                this.$el.popover("show");
                $('.acrux-note-popover').on('mouseleave', () => {
                    this.$el.trigger('mouseleave');
                });
            }, 500);
        }
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onMouseLeave: function (ev) {
        if (this.note) {
            if ($('.acrux-note-popover:hover').length) {
                return;
            }
            if (!this.$el.is(':hover')) {
               this.$el.popover('hide');
            }
        }
    },
 
});

return Conversation;
});
