odoo.define('portal_leave_knk.button', function (require) {
    'use strict';
    // debugger;

    const publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    var time = require('web.time');
    const session = require('web.session');


    publicWidget.registry.RemoveLeave = publicWidget.Widget.extend({
        selector: '.delete_button',
        events: {
            click: '_onClick'
        },

        start: function () {
            var def = this._super.apply(this, arguments);
        },

        _onClick: function (event) {
            var self = this;
            this._rpc({
                model: 'hr.leave',
                method: 'unlink',
                args: [parseInt(self.target.id)]
            })
                .then(function (action) {
                    window.location.reload(true)
                });
        }
    });

    publicWidget.registry.CustomCheckboxes = publicWidget.Widget.extend({
        selector: '.custom-hours',
        events: {
            'change #half_day_input_id': '_onHalfDayChange',
            'change #unit_hours_input_id': '_onUnitHoursChange',
        },
        start: function () {
            this._super.apply(this, arguments);
            this._checkFromDuration($('#half_day_input_id'));
            this._checkCustomHours($('#unit_hours_input_id'));
        },
        _checkFromDuration: function ($element) {
            var $challenges_details = $('#from_period_div');
            var $challenges_input = $challenges_details.find('#select_from_period');
            if ($element.prop('checked')) {
                $challenges_details.show();
                $challenges_input.attr('required', 'required');
            } else {
                $challenges_details.hide();
                $challenges_input.removeAttr('required');
                $challenges_input.val('');
            }
        },
        _checkCustomHours: function ($element) {
            var $challenges_details = $('.custom_hour_divs');
            var $challenges_input = $challenges_details.find('.select_period_select');
            if ($element.prop('checked')) {
                $challenges_details.show();
                $challenges_input.attr('required', 'required');
            } else {
                $challenges_details.hide();
                $challenges_input.removeAttr('required');
                $challenges_input.val('');
            }
        },
        _onHalfDayChange: function (event) {
            $("#unit_hours_input_id").prop("checked", false);
            $('.custom_hour_divs').hide();
            $('.select_period_select').removeAttr('required');
            $('.select_period_select').val('');
            this._checkFromDuration($(event.target));
        },
        _onUnitHoursChange: function (event) {
            $("#half_day_input_id").prop("checked", false);
            $('#from_period_div').hide();
            $('#select_from_period').removeAttr('required');
            $('#select_from_period').val('');
            this._checkCustomHours($(event.target));
        },

    });

    publicWidget.registry.TimeOffTypeHandler = publicWidget.Widget.extend({
        selector: '#leave_form',  // Replace with the actual selector
        events: {
            'change .time_off_type_select': '_onTimeOffTypeChange'
        },
        _onTimeOffTypeChange: function (event) {
            console.log('leave')
            console.log('leave')
            console.log('leave')
            console.log('leave')
            var self = this;
            rpc.query({
                model: 'hr.leave.type',
                method: 'search_read',
                args: [[['id', '=', $(event.target).val()]], ['id', 'request_unit']],
            }).then(function (rec) {
                if (rec && rec[0]) {
                    if (rec[0].request_unit == 'hour') {
                        $('.half_day_option').show();
                        $('.custom-hours').show();
                        $('.custom_hrs_option').show();
                    } else if (rec[0].request_unit == 'half_day') {
                        $('.half_day_option').show();
                        $('.custom_hrs_option').hide();
                    } else {
                        $('.half_day_option').hide();
                        $('.custom_hrs_option').hide();
                        $('.custom-hours').hide();
                    }
                }
            });
        }
    });




    publicWidget.registry.EmpPortalTimeOff = publicWidget.Widget.extend({
        selector: '.new_timeoff_form',
        events: {
            'click .new_timeoff_confirm': '_onNewTimeOffConfirm',
            'click .edit_timeoff_confirm': '_onEditTimeOffConfirm',
            'click .o_hr_attendance_sign_in_out_icon': 'update_attendance',
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
        async update_attendance() {


            var self = this;
            console.log(this.getSession())
            const result = await this._rpc({
                model: 'hr.employee.public',
                method: 'search_read',
                args: [[['user_id', '=', this.getSession().user_id]], ['id', 'name']],
            });

            console.log(result[0]['id'])
            this._rpc({
                model: 'hr.employee',
                method: 'attendance_manual',
                args: [[result[0]['id']], 'hr_attendance.hr_attendance_action_my_attendances'],
            })
                .then(function (result) {
                    window.location.href = "/my/employee/data";
                });
        },
        _buttonExec: function ($btn, callback) {
            // TODO remove once the automatic system which does this lands in master
            $btn.prop('disabled', true);
            return callback.call(this).guardedCatch(function () {
                $btn.prop('disabled', false);
            });
        },
        /**
         * @private
         * @returns {Promise}
         */
        _createTimeOff: function () {

            return this._rpc({
                model: 'hr.leave',
                method: 'create_timeoff_portal',
                args: [{
                    description: $('.new_timeoff_form .name').val(),
                    leave_location: $('.new_timeoff_form .leave_location').val(),
                    timeoff_type: $('.new_timeoff_form .holiday_status_id').val(),
                    from: this._parse_date($('.new_timeoff_form #leave_date_from_bt').val()),
                    to: this._parse_date($('.new_timeoff_form #leave_date_to_bt').val()),
                    half_day: $('.new_timeoff_form .request_unit_half').prop("checked"),
                    custom_hours: $('.new_timeoff_form .request_unit_hours').prop("checked"),
                    request_hour_from: $('.new_timeoff_form .request_hour_from').val(),
                    request_hour_to: $('.new_timeoff_form .request_hour_to').val(),
                    lesson_plan_link: $('.new_timeoff_form .lesson_plan_link').val(),
                    request_date_from_period: $('.new_timeoff_form .request_date_from_period').val(),
                    attachment_2: $('.new_timeoff_form .base64_file').val(),
                    file_name2: $('.new_timeoff_form .file_name2').val(),
                }],
            }).then(function (response) {
                if (response.errors) {
                    toastr.error('Something went wrong ' + response.errors + ' , try again.')
                    return Promise.reject(response);
                } else {
                    window.location = '/my/leave/' + response.id;
                }
            });
        },
        /**
         * @private
         * @returns {Promise}
         */
        _editTimeOffRequest: function () {

            return this._rpc({
                model: 'hr.leave',
                method: 'update_timeoff_portal',
                args: [[parseInt($('.edit_timeoff_form .timeoff_id').val())], {
                    timeoffID: parseInt($('.edit_timeoff_form .timeoff_id').val()),
                    description: $('.edit_timeoff_form .name').val(),
                    leave_location: $('.edit_timeoff_form .leave_location').val(),
                    timeoff_type: $('.edit_timeoff_form .holiday_status_id').val(),
                    from: this._parse_date($('.edit_timeoff_form .request_date_from').val()),
                    to: this._parse_date($('.edit_timeoff_form .request_date_to').val()),
                    half_day: $('.edit_timeoff_form .request_unit_half').prop("checked"),
                    custom_hours: $('.edit_timeoff_form .request_unit_hours').prop("checked"),
                    request_hour_from: $('.edit_timeoff_form .request_hour_from').val(),
                    lesson_plan_link: $('.edit_timeoff_form .lesson_plan_link').val(),
                    request_hour_to: $('.edit_timeoff_form .request_hour_to').val(),
                    request_date_from_period: $('.edit_timeoff_form .request_date_from_period').val(),
                }],
            }).then(function (response) {

                if (response.errors) {

                    toastr.error('Something went wrong ' + response.errors + ' , try again.')
                    return Promise.reject(response);
                } else {

                    window.location.reload();
                }

            });
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {Event} ev
         */
        _onNewTimeOffConfirm: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            if ($("#leave_form").valid()) {
                console.log($(ev.currentTarget))
                this._buttonExec($(ev.currentTarget), this._createTimeOff);
            } else {
                toastr.warning('Please fill the mandatory fields.')
            }

        },
        /**
         * @private
         * @param {Event} ev
         */
        _onEditTimeOffConfirm: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            if ($("#leave_form").valid()) {
                this._buttonExec($(ev.currentTarget), this._editTimeOffRequest);
            } else {
                toastr.warning('Please fill the mandatory fields.')
            }

        },

        _parse_date: function (value) {
            console.log(value);
            var date = moment(value, "YYYY-MM-DD", true);
            if (date.isValid()) {
                return time.date_to_str(date.toDate());
            } else {
                return false;
            }
        },
    });


})
;


$(document).ready(function () {
    $.validator.addMethod("greaterThann", function (value, element, params) {
        if ($(params[0]).val() != '') {
            if (!/Invalid|NaN/.test(new Date(value))) {
                return new Date(value) > new Date($(params[0]).val());
            }
            return isNaN(value) && isNaN($(params[0]).val()) || (Number(value) > Number($(params[0]).val()));
        }
        ;
        return true;
    }, 'Must be greater than {1}.');
    $.validator.addMethod('greaterThan', function (value, element) {

        var dateFrom = $(".request_date_from").val();
        var dateTo = $('.request_date_to').val();
        return dateTo >= dateFrom;

    });
    $("#leave_form").validate({
        rules: {
            request_date_to: {greaterThan: "#request_date_from"}
        }
    });
    $("#bt_valid_form").validate({
        rules: {
            date_to: {
                greaterThann: [".date_from", "Date From"]
            }
        }
    });

});
leave_date_from_bt = flatpickr("#leave_date_from_bt", {
    enableTime: false,
    dateFormat: "Y-m-d",
    onChange: function (selectedDates, dateStr, instance) {
        leave_date_to_bt.set('minDate', selectedDates[0]);
    }
});
leave_date_from_bt = flatpickr("#new_date", {
    enableTime: false,
    dateFormat: "Y-m-d",
});
leave_date_to_bt = flatpickr("#leave_date_to_bt", {});

