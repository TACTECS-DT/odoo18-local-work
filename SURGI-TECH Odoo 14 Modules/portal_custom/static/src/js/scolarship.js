odoo.define('portal_custom.scholarship', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var QWeb = core.qweb;

    function getBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsBinaryString(file);
            reader.onload = () => resolve(window.btoa(reader.result));
            reader.onerror = error => reject(error);
        });
    }

    publicWidget.registry.EmpPortalScholarship = publicWidget.Widget.extend({
        selector: '.new_scholarship_form, .edit_scholarship_form',
        events: {
            'click .new_scholarship_confirm': '_onNewScholarshipConfirm',
            'click .edit_scholarship_confirm': '_onEditScholarshipConfirm',
            'change .attachment_brith': '_onFileChange',
            'change .attachment_grade': '_onFileChange',
            'change .attachment_other': '_onFileChange',
        },

        _onFileChange: function (ev) {
            const input = ev.currentTarget;
            if (input.files.length > 0) {
                const file = input.files[0];
                getBase64(file).then(base64String => {
                    $(input).data('base64', base64String);
                });
            }
        },

        _collectFormData: async function (form) {
            const formData = {
                emp_scholarship_name: form.find('.emp_scholarship_name').val(),
                employee_relation: form.find('.employee_relation').val(),
                bdate: form.find('.bdate').val(),
                school_type: form.find('.school_type').val(),
                school_stage: form.find('.school_stage').val(),
                school_year: form.find('.school_year').val(),
                school_percentage: form.find('.school_percentage').val(),
            };

            const attachmentFields = ['attachment_brith', 'attachment_grade', 'attachment_other'];
            for (const field of attachmentFields) {
                const input = form.find(`.${field}`);
                if (input.data('base64')) {
                    formData[field] = input.data('base64');
                }
            }

            return formData;
        },

        _createScholarship: async function () {
            const form = $('.new_scholarship_form');
            const scholarshipData = await this._collectFormData(form);

            let scholarshipResponse = await rpc.query({
                model: 'emp.scholarship',
                method: 'create_scholarship_record',
                args: [scholarshipData],
            });

            if (scholarshipResponse.errors) {
                toastr.error(`Something went wrong: ${scholarshipResponse.errors}`);
                return;
            }

            window.location = `/my/profile`;
        },

        _editScholarship: async function (ev) {
            const scholarshipId = $(ev.currentTarget).data('id');
            const form = $(`#edit_scholarship_form${scholarshipId}`);
            const scholarshipData = await this._collectFormData(form);
            scholarshipData.scholarship_id = scholarshipId;

            let scholarshipResponse = await rpc.query({
                model: 'emp.scholarship',
                method: 'edit_scholarship_record',
                args: [scholarshipData],
            });

            if (scholarshipResponse.errors) {
                toastr.error(`Something went wrong: ${scholarshipResponse.errors}`);
                return;
            }

            window.location = `/my/profile`;
        },

        _onNewScholarshipConfirm: function (ev) {
            ev.preventDefault();
            this._createScholarship();
        },

        _onEditScholarshipConfirm: function (ev) {
            ev.preventDefault();
            this._editScholarship(ev);
        },
    });
});
