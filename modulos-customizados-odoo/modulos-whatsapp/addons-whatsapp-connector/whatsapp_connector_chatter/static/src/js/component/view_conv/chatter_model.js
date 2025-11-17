/** @odoo-module **/
require("@mail/models/chatter/chatter");

import { registry } from "@mail/model/model_core";

var factoryBak = registry["mail.chatter"].factory;

registry["mail.chatter"].factory = dependencies => {
    let outClass = factoryBak(dependencies);
    class Chatter extends outClass {
        create(vals) {
            let data = {};
            return Object.assign(data, vals), data.originalState && delete data.originalState, 
            super.create(data);
        }
        update(vals) {
            let data = {};
            return Object.assign(data, vals), data.originalState && delete data.originalState, 
            super.update(data);
        }
        onClickLogNote() {
            super.onClickLogNote(), this.componentChatterTopbar && this.componentChatterTopbar.__owl__.parent.hideWhatsappTalk();
        }
        onClickSendMessage(ev) {
            super.onClickSendMessage(ev), this.componentChatterTopbar && this.componentChatterTopbar.__owl__.parent.hideWhatsappTalk();
        }
        _onClickWhatsappTalk() {
            if (this.componentChatterTopbar) return this.componentChatterTopbar.__owl__.parent._onClickWhatsappTalk();
        }
    }
    return Object.assign(Chatter, outClass), Chatter;
};