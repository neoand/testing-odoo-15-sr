odoo.define('whatsapp_connector_audio_record.toolbox', function(require) {
"use strict";
    
var Toolbox = require('whatsapp_connector.toolbox')
var AudioRecorder = require('whatsapp_connector_audio_record.audio_recorder')

/**
 * @class
 * @name Toolbox
 * @extends Toolbox
 */
Toolbox.include({

    /**
     * @override
     * @see Widget.init
     */
    init: function(parent, options) {
        this._super.apply(this, arguments)

        this.audioRecorder = new AudioRecorder(this, {context: this.context})
    },

    /**
     * @override
     * @see Widget.start
     */
    start: function() {
        return this._super().then(() => {
            return this.audioRecorder.appendTo(this.$audio_recorder_button)
        })
    },

    /**
     * Hace trabajos de render
     *
     * @private
     * @override
     * @returns {Promise} Para indicar que termino
     */
    _initRender: function() {
        return this._super().then(result => {
            this.$audio_recorder_button = this.$('.acrux_audio_recorder_container')
            this.$other_inputs = this.$other_inputs.add(this.$audio_recorder_button)
            return result;
        })
    },

    /**
     * Revisa la visibilidad de los componentes.
     * @override
     */
    check_component_visibility: function() {
        this._super()
        if (this.parent.selected_conversation.allow_record_audio) {
            this.$audio_recorder_button.removeClass('o_hidden');
        } else {
            this.$audio_recorder_button.addClass('o_hidden');
        }
    },

   /**
     * @param {Event} [event] Evento
     *
     * @returns {Promise<Message>}
     */
    sendMessage: async function(event) {
        const _super = this._super
        /** @type {Blob} */
        const audio = await this.audioRecorder.stopRecording()
        if (audio) {
            const file = new File([audio], 'audio.oga', {type: 'audio/ogg'});
            await this.component.uploadFile({target: { files: [file] }})
        }
        return _super.apply(this, arguments)
    },

    /**
     * Oculta todo lo necesario de toolbox para grabar audios.
     */
    onAudioRecorderStart: function() {
        this.$emoji_btn.addClass('o_hidden')
        this.$toolbox_container.addClass('o_hidden')
        this.$write_done_btn.addClass('o_hidden')
        this.$attachment_button.addClass('o_hidden')
        if (this.component && this.component.attachment.value) {
            this.component._onAttachmentRemoved({})  // borrar adjuntos
        }
    },

    /**
     * Muestra todo lo que se oculto para poder grabar audio.
     */
    onAudioRecorderStop: function() {
        this.$emoji_btn.removeClass('o_hidden')
        this.$toolbox_container.removeClass('o_hidden')
        this.$write_done_btn.removeClass('o_hidden')
        this.$attachment_button.removeClass('o_hidden')        
    }

})

return Toolbox
})
