odoo.define('hr_evaluation_portal.evaluation_portal', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;

    publicWidget.registry.EvaluationWidget = publicWidget.Widget.extend({
        selector: '#evaluation_form', events: {
            'click .submit_evaluation': '_onSubmitEvaluation',
        },

        _editEvaluation: function () {
            console.log('_editEvaluation', $('.evaluation_form .evaluation_id').val())
            var coreCompetencies = [];
            $('.self_core_competencies').each(function () {
                var input = $(this);
                var id = input.data('id'); // Retrieve the ID
                var value = input.val(); // Retrieve the input value

                // Construct the object for this row
                coreCompetencies.push({
                    id: id, employee_self_assessment: parseFloat(value) / 100
                });
            });
            var functionComp = [];
            $('.self_function_comp').each(function () {
                var input = $(this);
                var id = input.data('id'); // Retrieve the ID
                var value = input.val(); // Retrieve the input value

                // Construct the object for this row
                functionComp.push({
                    id: id, employee_self_assessment: parseFloat(value) / 100
                });
            });
            var employeeKpi = [];
            $('.self_employee_kpi').each(function () {
                var input = $(this);
                var id = input.data('id'); // Retrieve the ID
                var value = input.val(); // Retrieve the input value

                // Construct the object for this row
                employeeKpi.push({
                    id: id, employee_self_assessment: parseFloat(value) / 100
                });
            });
            console.log('coreCompetencies', coreCompetencies)
            console.log('functionComp', functionComp)
            console.log('employeeKpi', employeeKpi)
            return this._rpc({
                model: 'evaluation.evaluation', // Adjust to your model name
                method: 'edit_self_evaluation_portal_record', args: [{
                    evaluation_id: $('.evaluation_form .evaluation_id').val(),
                    core_competencies: coreCompetencies,
                    function_comp: functionComp,
                    employee_kpi: employeeKpi,

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

        _onSubmitEvaluation: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            if ($("#evaluation_form").valid()) {
                this._buttonExec($(ev.currentTarget), this._editEvaluation);
            } else {
                toastr.warning('Please fill the mandatory fields.');
            }
        },

        _buttonExec: function ($btn, callback) {
            $btn.prop('disabled', true);
            return callback.call(this).guardedCatch(function () {
                $btn.prop('disabled', false);
            });
        },
    });
});
