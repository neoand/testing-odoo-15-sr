odoo.define('whatsapp_connector_audio_record.audio_recorder', function(require) {
"use strict";

var Widget = require('web.Widget');
var AudioPlayer = require('whatsapp_connector.audio_player')
var core = require('web.core')

var _t = core._t


/**
 * Es la grabadora de audios de chatroom
 *
 * @class
 * @name Message
 * @extends web.Widget
 */
var AudioRecorder = Widget.extend({
    jsLibs: [
        '/whatsapp_connector_audio_record/static/src/js/lib/OpusMediaRecorder.umd.js',
        '/whatsapp_connector_audio_record/static/src/js/lib/encoderWorker.umd.js',
    ],
    template: 'acrux_audio_recorder',
    events: {
        'click .o_chat_button_audio_record': 'startRecording',
        'click .o_chat_button_audio_cancel': 'cancelRecording',
        'click .o_chat_button_audio_pause': 'pauseRecording',
    },
    
    /**
     * @override
     * @see Widget.init
     */
    init: function(parent, options) {
        this._super.apply(this, arguments)

        this.parent = parent
        this.options = _.extend({}, options)
        this.context = _.extend({}, this.parent.context || {}, this.options.context)
        
        this.audioPlayer = new AudioPlayer(this, {context: this.context})
        this.calculateTime = AudioPlayer.prototype.calculateTime.bind(this)
        this.duration = 0
        this.startDate = new Date()
        this.cancelRecording()
    },

    /**
     * @override
     * @see Widget.destroy
     */
    destroy: function() {
        this.cancelRecording()
        this._super.apply(this, arguments)
    },

    /**
     * @override
     * @see Widget.willStart
     */
    willStart: function() {
        return this._super()
    },

    /**
     * @override
     * @see Widget.start
     */
    start: function() {
        return this._super()
        .then(() => this._initRender())
        .then(() => this.audioPlayer.appendTo(this.$audio_player))
    },

    /**
     * Hace trabajos de render
     *
     * @private
     * @returns {Promise} Para indicar que termino
     */
    _initRender: function() {
        this.$cancel_btn = this.$('.o_chat_button_audio_cancel')
        this.$recorder_btn = this.$('.o_chat_button_audio_record')
        this.$pause_btn = this.$('.o_chat_button_audio_pause')
        this.$audio_player = this.$('.audio_player')
        this.$recording_elapsed_time = this.$('.recording_elapsed_time')
        this.$red_recording_dot = this.$('.red_recording_dot')
        this.$elapsed_time = this.$('.elapsed_time')
    },

    /**
     * Botton grabar.
     * @returns {Promise}
     */
    startRecording: async function() {
        navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
        if (navigator.getUserMedia) {
            try {
                if (this.mediaRecorder) {  // esta pausado entonces remotar
                    this.mediaRecorder.resume() 
                } else {  // se va a comenzar grabar
                    await this.beginRecording()
                }
                this.renderRecording()
            } catch (error) {
                let msj = error
                if (error instanceof DOMException) {
                    if (error.name === 'NotFoundError') {
                        msj = {message: _t('Microphone not found.')}
                    } else if (error.name === 'NotAllowedError') {
                        msj = {message: _t('Microphone permission not granted.')}
                    }
                }
                this.call('crash_manager', 'show_warning', msj)
                this.cancelRecording()
            }
        } else {
            this.call('crash_manager', 'show_warning', _t('Recording audio not supported.'))
        }
    },

    /**
     * Solicita los permisos para grabar y comienza a grabar.
     * @returns {Promise}
     */
    beginRecording: async function() {
        // solicitar stream / permisos
        const constrain = navigator.mediaDevices.getSupportedConstraints()
        let audioConstrain = {}
        if (constrain.channelCount) {
            audioConstrain.channelCount = 1
        } else {
            audioConstrain = true
        }
        const audioStream = await navigator.mediaDevices.getUserMedia({video: false, audio: audioConstrain})
        this.parent.onAudioRecorderStart()  // ocultar los botos
        this.streamBeingCaptured = audioStream
        const options = {mimeType: this.getMimeType(), audioBitsPerSecond: 30480}
        if (!window.MediaRecorder || !window.MediaRecorder.isTypeSupported(this.getMimeType())) {  // Check if MediaRecorder available.
            const workerOptions = {
                OggOpusEncoderWasmPath: `${window.location.origin}/whatsapp_connector_audio_record/static/src/js/lib/OggOpusEncoder.wasm`,
                WebMOpusEncoderWasmPath: `${window.location.origin}/whatsapp_connector_audio_record/static/src/js/lib/WebMOpusEncoder.wasm`
            }
            this.mediaRecorder = new window.OpusMediaRecorder(audioStream, options, workerOptions)  // la clase que graba
        } else {  
            this.mediaRecorder = new MediaRecorder(audioStream, options)  // la clase que graba
        }
        this.audioBlobs = []
        // cada vez que graba algo, se guarda
        this.mediaRecorder.addEventListener('dataavailable', event => {
            this.audioBlobs.push(event.data)
            if (this.pausePromiseResolve) {  // para el caso de pausa
                this.pausePromiseResolve()
            }
        })
        this.mediaRecorder.start()  // comenzar a grabar
        this.duration = 0
        this.$elapsed_time.text(this.calculateTime(this.duration))
    },

    /**
     * Hace los cambios visuales necesarios para grabar
     */
    renderRecording: function() {
        this.startDate = new Date()
        this.elapsedTimeTimer = setInterval(() => {
            const time = this.computeElapsedTime()
            this.$elapsed_time.text(this.calculateTime(this.duration + time))
        }, 1000)
        this.$audio_player.addClass('o_hidden')
        this.$recorder_btn.addClass('o_hidden')
        
        this.$cancel_btn.removeClass('o_hidden')
        this.$pause_btn.removeClass('o_hidden')
        this.$recording_elapsed_time.removeClass('o_hidden')
        this.$red_recording_dot.removeClass('o_hidden')
        this.$elapsed_time.removeClass('o_hidden')
    },

    /**
     * Devuelve el formato en que se grabará el audio
     * @returns {String}
     */
    getMimeType: function() {
        return 'audio/ogg;codecs=opus'
    },

    /**
     * Se retorna lo que se va actualmente grabado.
     * @returns {Promise<Blob>}
     */
    getBoldAudio: async function() {
        const mimeType = this.getMimeType()
        const data = new Blob(this.audioBlobs, { type: mimeType })
        return data
    },

    /**
     * Detiene la grabacion y retorna un bold con dicha grabacion.
     * @returns {Promise<Bold>}
     */
    stopRecording: async function() {
        return new Promise(resolve => {
            if (this.mediaRecorder) {
                this.mediaRecorder.addEventListener('stop', async () => {
                    const audioBlob = await this.getBoldAudio()
                    resolve(audioBlob)
                })
               this.cancelRecording()
            } else {
                resolve(null)
            }
        })
    },

    /**
     * Pausa la grabacion
     * @returns {Promise} 
     */
    pauseRecording: async function() {
        clearInterval(this.elapsedTimeTimer)
        this.duration += this.computeElapsedTime()
        const prom = new Promise(res => this.pausePromiseResolve = res)
        this.mediaRecorder.pause()
        this.mediaRecorder.requestData()
        await prom  // esta promesa permite reproducir lo que se grabo
        this.$pause_btn.addClass('o_hidden')
        this.$red_recording_dot.addClass('o_hidden')
        this.$recorder_btn.removeClass('o_hidden')

        const audio = await this.getBoldAudio()
        const audioURL = window.URL.createObjectURL(audio);
        this.$audio_player.removeClass('o_hidden')
        this.audioPlayer.setAudio(audioURL)
        this.audioPlayer.replace()
    },

    /**
     * Cancela la grabación.
     */
    cancelRecording: function() {
        clearInterval(this.elapsedTimeTimer)
        this.stopStream()
        if (this.mediaRecorder) {
            this.mediaRecorder.stop()
        }
        this.mediaRecorder = null
        this.streamBeingCaptured = null
        if (this.$el) {
            this.$audio_player.addClass('o_hidden')
            
            this.$cancel_btn.addClass('o_hidden')
            this.$pause_btn.addClass('o_hidden')
            this.$recording_elapsed_time.addClass('o_hidden')
            this.$red_recording_dot.addClass('o_hidden')
            this.$elapsed_time.addClass('o_hidden')
            
            this.$recorder_btn.removeClass('o_hidden')
            this.parent.onAudioRecorderStop()
        }
    },

    /**
     * Detiene el stream
     */
    stopStream: function () {
        if (this.streamBeingCaptured) {
            const tracks = this.streamBeingCaptured.getTracks()
            tracks.forEach(track => track.stop()); 
        }
    },

    /**
     * Calcula el tiempo que duar el audio.
     */
    computeElapsedTime: function() {
        let endTime = new Date();  //record end time
        let timeDiff = endTime - this.startDate;  //time difference in ms
    
        timeDiff = timeDiff / 1000;  //convert time difference from ms to seconds
        return timeDiff
    }
})

return AudioRecorder
})
    
    