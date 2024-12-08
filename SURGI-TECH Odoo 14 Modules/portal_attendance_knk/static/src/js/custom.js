odoo.define('portal_attendance_knk.custom', function (require) {
    "use strict";
    //var AbstractAction = require('web.AbstractAction');
    //var core = require('web.core');
    // var ajax = require('web.ajax');
    // var MyAttendances = require('hr_attendance.my_attendances');
    // var GreetingMessage = require('hr_attendance.greeting_message')
    //var QWeb = core.qweb;
    //var _t = core._t;
    //var rpc = require('web.rpc');
    // var field_utils = require('web.field_utils');
    //var Dialog = require('web.Dialog');

    var sAnimations = require('website.content.snippets.animation');
$(document).ready(function() {
    $(".o_hr_attendance_sign_in_out").click(function(e) {
        // Remove any existing ripple span
        $(".ripple").remove();

        // Create the ripple span and set the size
        var ripple = $("<span class='ripple'></span>");
        var diameter = Math.max($(this).width(), $(this).height());
        ripple.css({height: diameter, width: diameter});

        // Append the ripple span to the button and animate
        $(this).append(ripple);
        var x = e.pageX - $(this).offset().left - diameter / 2;
        var y = e.pageY - $(this).offset().top - diameter / 2;
        ripple.css({top: y + 'px', left: x + 'px'}).addClass("animate");
    });
});
$(".o_hr_attendance_sign_in_out").click(function() {
    var icon = $(this).find(".o_hr_attendance_sign_in_out_icon");
    icon.addClass("rotating");
    setTimeout(function() {
        icon.removeClass("rotating");
    }, 1000);
});
$(".o_hr_attendance_sign_in_out").click(function() {
    var btn = $(this);
    btn.addClass("scaling");
    setTimeout(function() {
        btn.removeClass("scaling");
    }, 300);
});


    //var field_utils = require('web.field_utils');
    sAnimations.registry.HrAttendances = sAnimations.Class.extend({

        selector: '.portal_attendance_knk',

        events: {
            'click .o_hr_attendance_sign_in_out_icon': '_update_attendance',
        },
        // start: function () {
        //     this._super.apply(this, arguments);
        //     this._updateButton();
        // },
        //
        // _updateButton: function () {
        //     var buttonText = this.employee.attendance_state === 'checked_in' ? 'Check Out' : 'Check In';
        //     var buttonIcon = this.employee.attendance_state === 'checked_in' ? 'fa-sign-out' : 'fa-sign-in';
        //     var buttonClass = this.employee.attendance_state === 'checked_in' ? 'btn-warning' : 'btn-success';
        //
        //     var buttonElement = this.$('.o_hr_attendance_sign_in_out');
        //
        //     buttonElement.removeClass('fa-sign-in fa-sign-out btn-warning btn-success')
        //         .addClass(buttonIcon + ' ' + buttonClass)
        //         .attr('aria-label', buttonText)
        //         .attr('title', buttonText)
        //         .html('<i class="fa ' + buttonIcon + '" aria-hidden="true"></i>');
        // },

        willStart: function () {
            var self = this;
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function (position) {
                    self.lat = position.coords.latitude;
                    self.long = position.coords.longitude;
                });


            }
            var def = this._rpc({
                model: 'hr.employee',
                method: 'search_read',
                args: [[['user_id', '=', this.getSession().uid]], ['attendance_state', 'name', 'hours_today', 'allow_check_in_description', 'allow_check_in_task']],
            })
                .then(function (res) {
                    self.employee = res.length && res[0];
                    if (res.length) {
                        //self.hours_today = field_utils.format.float_time(self.employee.hours_today);
                    }
                    if (res.length && res[0]) {
                        self.employee_attend = res.length && res[0];

                    }
                });
            var prt = this._rpc({
                model: 'project.task',
                method: 'search_read',
//                args: [[['user_id', '=', this.getSession().uid],['date_end', '>=', now],['kanban_state', '=', 'normal']], ['id','name']],
                args: [[['user_id', '=', this.getSession().uid]], ['id', 'name']],
            })
                .then(function (tasks) {
                    if (tasks.length && tasks) {
                        self.tasks = tasks;
                    }
                });

            return Promise.all([prt, def, this._super.apply(this, arguments)]);

        },


        _update_attendance: function (ev, _update_location) {
            var self = this;
            var co_o = [];
            const employee_id = $(ev.currentTarget).data('id');
            console.log(employee_id)
            console.log('------------------')
            console.log('------------------')
            console.log('------------------')
            console.log('------------------')
            console.log('------------------')
            console.log('------------------')
            console.log('------------------')
            console.log('------------------')


            if (navigator.geolocation) {
                var OSName = "Unknown OS";
                if (navigator.appVersion.indexOf("Win") != -1) OSName = "Windows";
                if (navigator.appVersion.indexOf("Mac") != -1) OSName = "MacOS";
                if (navigator.appVersion.indexOf("X11") != -1) OSName = "UNIX";
                if (navigator.appVersion.indexOf("Linux") != -1) OSName = "Linux";
                self.os = OSName;
                var location_timeout = setTimeout("geolocFail()", 10000);
                const options = {
                    enableHighAccuracy: true,
                    timeout: 5000,
                    maximumAge: 0
                };
                navigator.geolocation.getCurrentPosition(function (position) {

                    clearTimeout(location_timeout);
                    self.lat = position.coords.latitude;
                    self.long = position.coords.longitude;
                    var context = {};
                    if (self.employee_attend) {
                        if (self.employee_attend.allow_check_in_description) {

                            context['default_task_description'] = $('input#task_description').val();
                            if (!context['default_task_description'] && self.employee.attendance_state === 'checked_out') {
                                window.alert('Please Add Task Description')
                                return


                            }
                        }
                        if (self.employee_attend.allow_check_in_task) {
                            context['default_task_id'] = parseInt($('select.task_select').val()) || false;
                            if (!context['default_task_id'] && self.employee.attendance_state === 'checked_out') {
                                window.alert('Please select attendance task')
                                return
                            }
                        }
                    }


                }, function (err) {
                    clearTimeout(location_timeout);
                    geolocFail();
                }, options)

            } else {
                geolocFail();
            }

            const options = {
                // enableHighAccuracy: true,
                // timeout: 5000,
                // maximumAge: 0
            };
            self.browser = Object.keys(jQuery.browser)[0];
            this._rpc({
                model: 'hr.employee',
                method: 'attendance_manual',
                args: [[employee_id], 'hr_attendance.hr_attendance_action_my_attendances', self.lat, self.long],
            })
                .then(function (result) {

                    //new Promise(self._update_location(employee_id,result.action.attendance.id));
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                    }

                    $.ajax({
                        url: "/google/address",
                        method: "GET",
                        dataType: 'json',
                        data: {
                            lat: self.lat,
                            long: self.long,
                            emp: employee_id,
                            browser: self.browser,
                            os: self.os,
                            attend: result.action.attendance.id
                        },
                        success: function (data) {
                            window.location.reload();
                            if (data) {

                                self.address = data[0];
                                $('.mylocation').text(self.address);
                                $('.o_hr_attendance_button_dismiss').show();
                            } else {
                                $('.o_hr_attendance_button_dismiss').show();
                            }
                        }
                    });

                    // setTimeout(5000);
                    // delay(5000);

                    //
                });


        },


        _update_location: function (employee_id, id) {

        }


    });
});