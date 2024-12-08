odoo.define('hr_attendance_sheet_portal.attendance_portal', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var rpc = require('web.rpc')
    var publicWidget = require('web.public.widget');
    var time = require('web.time');
    var core = require('web.core');
    var _t = core._t;
    const session = require('web.session');
    publicWidget.registry.RequestOvertimeWidget = publicWidget.Widget.extend({
        selector: '.request_overtime_portal_button', // change this to match your HTML button
        events: {
            'click': '_onRequestOvertime',
        },

_onRequestOvertime: function (ev) {
    ev.preventDefault();
    var self = this;
    var sheet_id = $(ev.currentTarget).data('id');
    console.log('request', sheet_id);
    const toast = document.getElementById("toastssss"); // Make sure this ID matches your HTML
    console.log('toast', toast);
    if (!toast) { // Check if toast is null
        console.log('Toast element not found');
        return;
    }
    return this._rpc({
        model: 'attendance.sheet.line',
        method: 'action_req_overtime_portal',
        args: [parseInt(sheet_id)],
    }).then(function (response) {
        console.log('response', response);
        if (response) { // If the response is not true
            console.log('sssssssssssssssssssss');
            toast.textContent = "Overtime Request successfully!"; // Set the success text
            toast.classList.remove("warning"); // Remove the warning class
            toast.classList.add("show");
            setTimeout(function () {
                toast.classList.remove("show");
                window.location.reload();
            }, 3000);
        }
    }).catch(function (error) {
        // Handle the error here
        console.log('Error:', error.message.data['message']);
        toast.textContent = 'Something went wrong: ' + error.message.data['message']; // Set the error text
        toast.classList.add("warning"); // Add the warning class
        toast.classList.add("show");
        setTimeout(function () {
            toast.classList.remove("show");
            toast.classList.remove("warning"); // Optionally, remove the warning class
        }, 9000);
    });
},
    });
});
