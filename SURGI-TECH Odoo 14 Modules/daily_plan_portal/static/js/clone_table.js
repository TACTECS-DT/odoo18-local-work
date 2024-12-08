if ($('#daily_plan_form').length) {
    odoo.define('daily_plan_portal.daily_plan', function (require) {
        "use strict";
        var publicWidget = require('web.public.widget');

        publicWidget.registry.FormFunction = publicWidget.Widget.extend({
            selector: '#state_employee',
            events: {
                'change': '_onChangeStateEmployee',
            },

            start: function () {
                this._super.apply(this, arguments);
                this.$operationBlock = $('#operation_block');
                this.operation2_block = $('#operation2_block');
                this.operation3_block = $('#operation3_block');
                this.mission_block = $('#mission_block');
                this.$operationBlock.hide();
                this.operation3_block.hide();
                this.operation2_block.hide();
                this.mission_block.hide();
            },

            _onChangeStateEmployee: function (event) {
                var stateEmployee = $(event.currentTarget).val();
                if (stateEmployee === 'operation') {
                    this.$operationBlock.show();
                    this.operation2_block.show();
                    this.operation3_block.show();
                } else {
                    this.$operationBlock.hide();
                    this.operation2_block.hide();
                    this.operation3_block.hide();
                }
                if (stateEmployee === 'mission') {
                    this.mission_block.show();

                } else {
                    this.mission_block.hide();

                }
            },
        });
        publicWidget.registry.OperationOnchange = publicWidget.Widget.extend({
            selector: '#operation_id',
            events: {
                'change': '_onOperationChange',
            },

            _onOperationChange: function (ev) {
                var self = this;
                var operationId = $(ev.target).val();

                this._rpc({
                    model: 'operation.operation',
                    method: 'search_read',
                    domain: [['id', '=', parseInt(operationId)]],
                    fields: ['operation_type', 'hospital_id', 'surgeon_id'],
                }).then(function (operation) {
                    console.log(operation)
                    // Assuming the first operation is the one we want.
                    operation = operation[0];

                    // Remove existing options
                    $('#operation_type').find('option').remove();
                    $('#surgeon').find('option').remove();
                    $('#hospital_id').find('option').remove();

                    // Check if fields exist and append new options
                    if (operation.operation_type) {
                        var option = new Option(operation.operation_type[1], operation.operation_type[0]);
                        $(option).attr('selected', 'selected');
                        $('#operation_type').append(option);
                    }
                    if (operation.surgeon_id) {
                        var option = new Option(operation.surgeon_id[1], operation.surgeon_id[0]);
                        $(option).attr('selected', 'selected');
                        $('#surgeon').append(option);
                    }
                    if (operation.hospital_id) {
                        var option = new Option(operation.hospital_id[1], operation.hospital_id[0]);
                        $(option).attr('selected', 'selected');
                        $('#hospital_id').append(option);
                    }
                });
            },
        });


    });
}