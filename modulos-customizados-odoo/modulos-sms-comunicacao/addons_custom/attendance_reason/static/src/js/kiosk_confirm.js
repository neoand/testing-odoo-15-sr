odoo.define('attendance_reason.kiosk_confirm', function (require) {
    "use strict";

    var KioskConfirm = require('hr_attendance.kiosk_confirm');
    var KioskConfirm = KioskConfirm.include({
        events: _.extend({}, KioskConfirm.prototype.events, {
            'change #oe_attendance_reasons': 'OnChangeReason',
            'click .o_hr_attendance_sign_in_out_icon': _.debounce(function () {
                var self = this;
                this._rpc({
                        model: 'hr.employee',
                        method: 'attendance_manual',
                        args: [[this.employee_id], this.next_action],
                    })
                    .then(function(result) {
                        if (result.action) {
                            var action = result.action;
                            self.do_action(action);
                            var employee_id = action.attendance.employee_id[0];
                            var attendance_id = action.attendance['id'];
                            self._rpc({
                                model: 'hr.attendance',
                                method: 'update_reason',
                                args: [[attendance_id],employee_id,self.attendance_reason],
                            });
                        } else if (result.warning) {
                            self.do_warn(result.warning);
                        }
                    });
            }, 200, true),
            'click .o_hr_attendance_pin_pad_button_ok': _.debounce(function() {
                var self = this;
                this.$('.o_hr_attendance_pin_pad_button_ok').attr("disabled", "disabled");
                this._rpc({
                        model: 'hr.employee',
                        method: 'attendance_manual',
                        args: [[this.employee_id], this.next_action, this.$('.o_hr_attendance_PINbox').val()],
                    })
                    .then(function(result) {
                        if (result.action) {
                            var action = result.action;
                            self.do_action(action);
                            var employee_id = action.attendance.employee_id[0];
                            var attendance_id = action.attendance['id'];
                            self._rpc({
                                model: 'hr.attendance',
                                method: 'update_reason',
                                args: [[attendance_id],employee_id,self.attendance_reason],
                            });
                        } else if (result.warning) {
                            self.do_warn(result.warning);
                            self.$('.o_hr_attendance_PINbox').val('');
                            setTimeout( function() { self.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled"); }, 500);
                        }
                    });
            }, 200, true),
        }),

        OnChangeReason:  function(){
            var self = this;
            var inputReason = this.$('#oe_attendance_reasons')[0];
            if (inputReason.value !== '') {                    
                self.attendance_reason = inputReason.value;
            }
        },

        willStart: function () {
            var self = this;
            var superDef = this._super.apply(this, arguments);
            var def = this._rpc({
                model: 'hr.attendance.reasons',
                method: 'search_read',
                args: [[], ['id','name', 'attendance_state']],
                }).then(function (reasons) {                    
                    self.reasons = reasons || false;
                });    
                return Promise.all([superDef, def]);
        },

    });
});