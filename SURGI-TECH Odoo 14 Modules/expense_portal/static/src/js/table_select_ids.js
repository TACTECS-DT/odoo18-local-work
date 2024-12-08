odoo.define('expense_portal.expense_table', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');


    publicWidget.registry.ExpenseTableCheck = publicWidget.Widget.extend({
        selector: '#expense_table',
        events: {
            'change #select-all-checkbox': '_onSelectAll',
        },
        _onSelectAll: function (ev) {
            var isChecked = $(ev.currentTarget).is(':checked');
            console.log("is checked")
            console.log("is checked")
            console.log("is checked")
            if (isChecked) {
                // Action when the checkbox is checked (select all)
                $('input.record-checkbox').each(function () {
                    $(this).prop('checked', true);
                });
            } else {
                // Action when the checkbox is unchecked (deselect all)
                $('input.record-checkbox').each(function () {
                    $(this).prop('checked', false);
                });
            }
        },

    });
    publicWidget.registry.ExpenseTable = publicWidget.Widget.extend({
        selector: '#submit-selected-expenses',
        events: {
            'click': '_onSubmitSelectedExpenses',
        },

        _onSubmitSelectedExpenses: function (ev) {
            var self = this;
            var selectedExpenseIds = [];
            $('input.record-checkbox:checked').each(function () {
                selectedExpenseIds.push(parseInt($(this).val()));
            });

            if (selectedExpenseIds.length > 0) {
                self._rpc({
                    model: 'hr.expense',
                    method: 'action_submit_expenses_custom',
                    args: [selectedExpenseIds],
                }).then(function (response) {
                    if (response && response.success) {
                        $('#successModal .modal-body .custom-modal-text').text('' + response.name);
                        $('#successModal').modal('show');
                        setTimeout(function () {
                            location.reload();
                        }, 4000);
                    } else {
                        alert('Error: ' + response.message);
                    }
                }).catch(function () {
                    alert('There was an error submitting the selected expenses.');
                });
            } else {
                alert('Please select at least one expense to submit.');
            }
        },

    });

    publicWidget.registry.ProductCategoriesChoices = publicWidget.Widget.extend({
        selector: '.categories-select-wrapper',

        start: function () {
            this._super.apply(this, arguments);
            this._initializeChoices();
        },

        _initializeChoices: function () {
            var productCategIds = document.getElementById('product_categ_ids');
            var tax_ids = document.getElementById('tax_ids');
            var choices = new Choices(productCategIds, {
                removeItemButton: true,
                // position: 'auto',
                shouldSort: false,
                searchFields: ['label'],


            });
            var choices = new Choices(tax_ids, {
                removeItemButton: true,
                // position: 'auto',
                shouldSort: false,
                searchFields: ['label'],


            });
        }
    });

    return publicWidget.registry.ProductCategoriesChoices;
});
