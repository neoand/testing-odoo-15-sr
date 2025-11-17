odoo.define('attendance_reason.my_attendances', function (require) {
    "use strict";

    var MyAttendances = require('hr_attendance.my_attendances');
    var MyAttendances= MyAttendances.include({
        events: _.extend({}, MyAttendances.prototype.events, {
            'change #oe_attendance_reasons': 'OnChangeReason',
        }),

        willStart: function () {
            var self = this;
            var superDef = this._super.apply(this, arguments);            
            var def = this._rpc({
                    model: 'hr.attendance.reasons',
                    method: 'search_read',
                    args: [[], ['id','name', 'attendance_state']],
                }).then(function (reasons) {
                    self.reasons = reasons;
                });            
            return Promise.all([superDef, def]);
        },

        OnChangeReason:  function(){
            var self = this;
            var inputReason = this.$('#oe_attendance_reasons')[0];
            if (inputReason.value !== '') {                    
                self.attendance_reason = inputReason.value;
            }
        },

        update_attendance: function () {
            var self = this;
            this._rpc({
                    model: 'hr.employee',
                    method: 'attendance_manual',
                    args: [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances'],
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
        },
    });

});