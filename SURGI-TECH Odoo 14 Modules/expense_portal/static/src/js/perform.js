odoo.define('expense_portal.perform', function (require) {
    "use strict";
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;

    var ajax = require('web.ajax');

    var sAnimations = require('website.content.snippets.animation');


    publicWidget.registry.RemoveExpence = publicWidget.Widget.extend({
        selector: '.delete_expense_button',
        events: {
            click: '_onClick'
        },

        start: function () {
            var def = this._super.apply(this, arguments);
        },

        _onClick: function (event) {
            var self = this;
            console.log('self.target.id', self.target.id)
            this._rpc({
                model: 'hr.expense',
                method: 'unlink',
                args: [parseInt(self.target.id)]
            })
                .then(function (action) {
                    window.location.reload(true)
                });
        }
    });


    sAnimations.registry.expenses = sAnimations.Class.extend({
        selector: '#expenses',
        read_events: {
            'input #product': '_onChangeproduct',
            'change #quantity': '_onChangeqty',
            'change #unit_price': '_onChangeunit_price',
        },
        init: function () {
            this._super.apply(this, arguments);
        },

        start: function () {
            var def = this._super.apply(this, arguments);
            return def;
        },

        _onChangeproduct: function (ev) {
            var self = this;
            var product_id = ev.currentTarget.value;
            console.log('product_id')
            console.log('product_id', product_id)
            console.log('product_id', product_id)
            this._rpc({
                model: 'product.product',
                method: 'get_product_details',
                args: [parseInt(product_id)],
            }).then(function (res) {
                console.log(res[0])
                $('#unit_price').attr('value', res[0]);
                $('#total').attr('value', res[0] * $('#quantity').val())
            });

            if (product_id) {
                this._rpc({
                    model: 'product.product',
                    method: 'search_read',
                    domain: [['id', '=', parseInt(product_id)]],
                    fields: ['id', 'name', 'property_account_expense_id'],
                }).then(function (result) {
                    console.log('result for property_account_expense_id', result);
                    if (result && result[0]) {
                        var account_id = $('#account_id');
                        account_id.empty();
                        if (result[0].property_account_expense_id) {
                            account_id.append($('<option></option>').attr({
                                'selected': true,
                                'value': result[0].property_account_expense_id[0]
                            }).text(result[0].property_account_expense_id[1]));
                        } else {
                            account_id.append($('<option></option>').attr('value', ""));
                        }
                    }

                });
            } else {
                $('#operations_type').empty();
            }


        },
        _onChangeqty: function (ev) {
            var self = this;
            var qty = ev.currentTarget.value;
            $('#total').attr('value', $('#unit_price').val() * qty)

        },
        _onChangeunit_price: function (ev) {
            var self = this;
            var price = ev.currentTarget.value;
            $('#total').attr('value', $('#quantity').val() * price)

        },


    });
    publicWidget.registry.OperationSelect = publicWidget.Widget.extend({
        selector: '#sales_id',
        events: {
            'input': '_onOperationChange',

        },

        _onOperationChange: function (ev) {
            var operationID = $(ev.currentTarget).val();
            console.log('operationID for service', operationID);

            if (operationID) {
                this._rpc({
                    model: 'operation.operation',
                    method: 'search_read',
                    domain: [['id', '=', parseInt(operationID)]],
                    fields: ['id', 'name', 'state', 'operation_type'],
                }).then(function (result) {
                    console.log('result for service', result);

                    if (result && result[0]) {
                        var operations_type = $('#operations_type');
                        operations_type.empty();
                        if (result[0].operation_type) {
                            operations_type.append($('<option></option>').attr({
                                'selected': true,
                                'value': result[0].operation_type[0]
                            }).text(result[0].operation_type[1]));
                        } else {
                            operations_type.append($('<option></option>').attr('value', ""));
                        }
                    }
                    if (result[0].state) {
                        $('#sales_state').val(result[0].state)
                    } else {
                        $('#sales_state').empty();
                    }

                });
            } else {
                $('#operations_type').empty();
            }
        },
    });

    publicWidget.registry.ProdductWidget = publicWidget.Widget.extend({
        selector: '.product-auto-widget',
        events: {
            'input .product-input': '_onInput',
        },
        start: function () {
            this._super.apply(this, arguments);
        },
        _onInput: function (e) {
            var self = this;
            var query = $(e.currentTarget).val();
            this._rpc({
                route: '/search_exp_products',
                params: {query: query}
            }).then(function (data) {
                self._populateOptions(data);
            });
        },
        _populateOptions: function (data) {
            var dropdown = $('#custom_product_dropdown');
            dropdown.empty();
            for (var i = 0; i < data.length; i++) {
                dropdown.append('<div class="custom-product-option" data-id="' + data[i].id + '">' + data[i].name + '</div>');
            }
            dropdown.show();
            $('.custom-product-option').click(function () {
                var selectedId = $(this).attr('data-id');
                var selectedName = $(this).text();
                $('#product_input').val(selectedName);
                $('#product').val(selectedId);  // Update the hidden input field
                $('#product').trigger('input');
                dropdown.hide();
            });
        },
    });
    publicWidget.registry.AnalyticWidget = publicWidget.Widget.extend({
        selector: '.analytic-auto-widget',
        events: {
            'input .analytic-input': '_onInput',
        },
        start: function () {
            this._super.apply(this, arguments);
        },
        _onInput: function (e) {
            var self = this;
            var query = $(e.currentTarget).val();
            this._rpc({
                route: '/search_analytic_account',
                params: {query: query}
            }).then(function (data) {
                self._populateOptions(data);
            });
        },
        _populateOptions: function (data) {
            var dropdown = $('#custom_analytic_dropdown');
            dropdown.empty();
            for (var i = 0; i < data.length; i++) {
                dropdown.append('<div class="custom-analytic-option" data-id="' + data[i].id + '">' + data[i].name + '</div>');
            }
            dropdown.show();
            $('.custom-analytic-option').click(function () {
                var selectedId = $(this).attr('data-id');
                var selectedName = $(this).text();
                $('#analytic_input').val(selectedName);
                $('#analytic_account').val(selectedId);  // Update the hidden input field
                $('#analytic_account').trigger('input');
                dropdown.hide();
            });
        },
    });
    publicWidget.registry.SurgeonsWidget = publicWidget.Widget.extend({
        selector: '.surgeons-auto-widget',
        events: {
            'input .surgeons-input': '_onInput',
        },
        start: function () {
            this._super.apply(this, arguments);
        },
        _onInput: function (e) {
            var self = this;
            var query = $(e.currentTarget).val();
            this._rpc({
                route: '/search_surgeons',
                params: {query: query}
            }).then(function (data) {
                self._populateOptions(data);
            });
        },
        _populateOptions: function (data) {
            var dropdown = $('#custom_surgeons_dropdown');
            dropdown.empty();
            for (var i = 0; i < data.length; i++) {
                dropdown.append('<div class="custom-surgeons-option" data-id="' + data[i].id + '">' + data[i].name + '</div>');
            }
            dropdown.show();
            $('.custom-surgeons-option').click(function () {
                var selectedId = $(this).attr('data-id');
                var selectedName = $(this).text();
                $('#surgeons_input').val(selectedName);
                $('#partner_surgeons_id').val(selectedId);  // Update the hidden input field
                $('#partner_surgeons_id').trigger('input');
                dropdown.hide();
            });
        },
    });
    publicWidget.registry.OperationsWidget = publicWidget.Widget.extend({
        selector: '.operations-auto-widget',
        events: {
            'input .operations-input': '_onInput',
        },
        start: function () {
            this._super.apply(this, arguments);
        },
        _onInput: function (e) {

            var self = this;
            var query = $(e.currentTarget).val();
            this._rpc({
                route: '/search_exp_operations',
                params: {query: query}
            }).then(function (data) {
                self._populateOptions(data);
            });
        },
        _populateOptions: function (data) {
            var dropdown = $('#custom_operations_dropdown');
            dropdown.empty();
            for (var i = 0; i < data.length; i++) {
                dropdown.append('<div class="custom-operations-option" data-id="' + data[i].id + '">' + data[i].name + '</div>');
            }
            dropdown.show();
            $('.custom-operations-option').click(function () {
                var selectedId = $(this).attr('data-id');
                var selectedName = $(this).text();
                $('#operations_input').val(selectedName);
                $('#sales_id').val(selectedId);  // Update the hidden input field
                $('#sales_id').trigger('input');
                dropdown.hide();
            });
        },
    });


    publicWidget.registry.EmpPortalExpense = publicWidget.Widget.extend({
        selector: '.new_expense_form',
        events: {
            'click .new_expense_confirm': '_onNewExpenseConfirm',
            'click .edit_expense_confirm': '_onEditExpenseConfirm',
        },

        _prepareAttachmentData: function (file, res_id, res_model) {
            return {
                'name': file.name,
                'file': file,
                'res_id': res_id,
                'res_model': res_model,
            };
        },

        _uploadAttachment: async function (file, res_id) {
            var data = this._prepareAttachmentData(file, res_id, 'hr.expense');
            let response = await ajax.post('/attachment/add', data);
            console.log("Server Response:", response);
            return response;
        },

        _createExpense: async function () {
            var analytic_tag_ids = [];
            $('.new_expense_form .analytic_tag_ids option:selected').each(function () {
                analytic_tag_ids.push(parseInt($(this).val()));
            });

            var tax_ids = [];
            $('.new_expense_form .tax_ids option:selected').each(function () {
                tax_ids.push(parseInt($(this).val()));
            });

            const expenseData = {
                description: $('.new_expense_form .description').val(),
                expense_type: $('.new_expense_form .expense_type').val(),
                product: parseInt($('.new_expense_form .product').val()),
                unit_price: parseFloat($('.new_expense_form .unit_price').val()),
                quantity: parseInt($('.new_expense_form .quantity').val()),
                date: $('.new_expense_form .date').val(),
                employee: parseInt($('.new_expense_form .employee').val()),
                sales_id: parseInt($('.new_expense_form .sales_id').val()),
                currency_id: parseInt($('.new_expense_form .currency_id').val()),
                analytic_account: parseInt($('.new_expense_form .analytic_account').val()),
                partner_surgeon_id: parseInt($('.new_expense_form .partner_surgeon_id').val()),
                analytic_tag_ids: analytic_tag_ids,
                tax_ids: tax_ids
            };

            let expenseResponse = await this._rpc({
                model: 'hr.expense',
                method: 'create_expense_record',
                args: [expenseData],
            });

            if (expenseResponse.errors) {
                toastr.error(`Something went wrong: ${expenseResponse.errors}`);
                return;
            }

            let attachmentIds = [];
            const files = $('#attachment_ids')[0].files;
            for (const file of files) {
                let attachmentResponse = await this._uploadAttachment(file, expenseResponse.id);
                attachmentIds.push([4, attachmentResponse.id, 0]);
            }

            // await this._rpc({
            //     model: 'hr.expense',
            //     method: 'write',
            //     args: [[expenseResponse.id], {
            //         'attachment_ids': attachmentIds
            //     }],
            // });

            window.location = `/expense/request/${expenseResponse.id}`;
        },
        _editExpense: async function () {


            const expenseData = {
                description: $('.new_expense_form .description').val(),
                expense_id: $('.new_expense_form .expense_id').val(),
                expense_type: $('.new_expense_form .expense_type').val(),
                product: parseInt($('.new_expense_form .product').val()),
                unit_price: parseFloat($('.new_expense_form .unit_price').val()),
                quantity: parseInt($('.new_expense_form .quantity').val()),
                date: $('.new_expense_form .date').val(),
                employee: parseInt($('.new_expense_form .employee').val()),
                sales_id: parseInt($('.new_expense_form .sales_id').val()),
                currency_id: parseInt($('.new_expense_form .currency_id').val()),
                analytic_account: parseInt($('.new_expense_form .analytic_account').val()),
                partner_surgeon_id: parseInt($('.new_expense_form .partner_surgeon_id').val()),
            };

            let expenseResponse = await this._rpc({
                model: 'hr.expense',
                method: 'edit_expense_record',
                args: [expenseData],
            });

            if (expenseResponse.errors) {
                toastr.error(`Something went wrong: ${expenseResponse.errors}`);
                return;
            }

            let attachmentIds = [];
            const files = $('#attachment_ids')[0].files;
            for (const file of files) {
                let attachmentResponse = await this._uploadAttachment(file, expenseResponse.id);
                attachmentIds.push([4, attachmentResponse.id, 0]);
            }

            // await this._rpc({
            //     model: 'hr.expense',
            //     method: 'write',
            //     args: [[expenseResponse.id], {
            //         'attachment_ids': attachmentIds
            //     }],
            // });

            window.location = `/expense/request/${expenseResponse.id}`;
        },

        _onNewExpenseConfirm: function (ev) {
            ev.preventDefault();
            if ($("#expenses").valid()) {
                this._createExpense();
            } else {
                toastr.warning('Please fill in the mandatory fields.');
            }
        },
        _onEditExpenseConfirm: function (ev) {
            ev.preventDefault();
            if ($("#expenses").valid()) {
                this._editExpense();
            } else {
                toastr.warning('Please fill in the mandatory fields.');
            }
        },

    });


});
