/** @odoo-module **/
import { registerMessagingComponent, unregisterMessagingComponent } from "@mail/utils/messaging_component";

import { Chatter as ChatterBase } from "@mail/components/chatter/chatter";

import { clear } from "@mail/model/model_field_command";

const WhatsappChatter = require("whatsapp_connector_chatter.Chatter"), {useState: useState} = owl.hooks, {useRef: useRef} = owl.hooks;

export class Chatter extends ChatterBase {
    constructor(...args) {
        super(...args);
        let state = this.state || {};
        Object.assign(state, {
            isWhatsappTalkVisible: !1,
            hasChatroomChatterGroup: !1
        }), this.state = useState(state), this._whatsappConversationRef = useRef("whatsappConversationRef"), 
        this.widgetComponents || (this.widgetComponents = {}), Object.assign(this.widgetComponents, {
            WhatsappChatter: WhatsappChatter
        });
    }
    async willStart() {
        await super.willStart(), this.state.hasChatroomChatterGroup = await this.env.session.user_has_group("whatsapp_connector_chatter.group_chat_in_chatter");
    }
    showWhatsappTalk() {
        this.state.isWhatsappTalkVisible = !0;
    }
    hideWhatsappTalk() {
        this.state.isWhatsappTalkVisible = !1;
    }
    async _onClickWhatsappTalk() {
        this.state.isWhatsappTalkVisible ? this.state.isWhatsappTalkVisible = !1 : this._whatsappConversationRef.comp && (await this._whatsappConversationRef.comp.queryConversations(), 
        this.state.isWhatsappTalkVisible = !0, this.chatter.update({
            composerView: clear()
        }));
    }
}

Object.assign(Chatter.props, {
    originalState: Object,
    isChatroomInstalled: Boolean,
    isInAcruxChatRoom: Boolean
}), unregisterMessagingComponent(ChatterBase), registerMessagingComponent(Chatter);