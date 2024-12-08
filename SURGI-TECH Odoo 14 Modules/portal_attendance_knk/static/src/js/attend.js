odoo.define('portal_attendance.attendance', function (require) {
    "use strict";
  var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');

    publicWidget.registry.PortalAttendance = publicWidget.Widget.extend({
        selector: '#portal_attendance',
        events: {
            'click .update_attendance': '_updateAttendance',
        },

        start: function () {
            var self = this;

            var defEmployee = rpc.query({
                model: 'hr.employee',
                method: 'search_read',
                args: [[['user_id', '=', this.getSession().uid]], ['attendance_state', 'name', 'hours_today', 'allow_check_in_description', 'allow_check_in_task']],
            })
            .then(function (res) {
                self.employee = res.length && res[0];
            });

            var defTasks = rpc.query({
                model: 'project.task',
                method: 'search_read',
                args: [[['user_id', '=', this.getSession().uid]], ['id', 'name']],
            })
            .then(function (tasks) {
                self.tasks = tasks;
            });

            return Promise.all([defEmployee, defTasks, this._super.apply(this, arguments)]);
        },

        _updateAttendance: function () {
            var self = this;
            var context = {};

            if (self.employee) {
                if (self.employee.allow_check_in_description) {
                    context['default_task_description'] = $('input#task_description').val();
                    if (!context['default_task_description'] && self.employee.attendance_state === 'checked_out') {
                        window.alert('Please Add Task Description');
                        return;
                    }
                }
                if (self.employee.allow_check_in_task) {
                    context['default_task_id'] = parseInt($('select.task_select').val()) || false;
                    if (!context['default_task_id'] && self.employee.attendance_state === 'checked_out') {
                        window.alert('Please select attendance task');
                        return;
                    }
                }
            }

            navigator.geolocation.getCurrentPosition(function (position) {
                self.lat = position.coords.latitude;
                self.long = position.coords.longitude;

                rpc.query({
                    model: 'hr.employee',
                    method: 'attendance_manual',
                    args: [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances', self.lat, self.long],
                    context: context,
                })
                .then(function (result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                    }
                });
            });
        },
    });
});
