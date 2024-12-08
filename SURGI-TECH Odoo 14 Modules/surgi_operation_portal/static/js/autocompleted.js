odoo.define('surgi_operation_portal.SurgeonWidget', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');

publicWidget.registry.SurgeonWidget = publicWidget.Widget.extend({
    selector: '.surgeon-auto-widget',
    events: {
        'input .surgeon-input': '_onInput',
    },
    start: function () {
        this._super.apply(this, arguments);
    },
    _onInput: function (e) {
        var self = this;
        var query = $(e.currentTarget).val();
        var hospital_id = $('#hospital_id').val();  // Get the selected hospital_id
        console.log('Selected Hospital ID:', hospital_id);  // Debug log to check the value
        this._rpc({
            route: '/search_surgeons',
            params: {query: query, hospital_id: hospital_id}  // Pass the hospital_id
        }).then(function (data) {
            self._populateOptions(data);
        });
    },
    _populateOptions: function (data) {
        var dropdown = $('#custom_surgeon_dropdown');
        dropdown.empty();
        for (var i = 0; i < data.length; i++) {
            dropdown.append('<div class="custom-surgeon-option" data-id="' + data[i].id + '">' + data[i].name + '</div>');
        }
        dropdown.show();
        $('.custom-surgeon-option').click(function () {
            var selectedId = $(this).attr('data-id');
            var selectedName = $(this).text();
            $('#surgeon_input').val(selectedName);
            $('#surgeon_id').val(selectedId);  // Update the hidden input field
            dropdown.hide();
        });
    },
});

    publicWidget.registry.PatientWidget = publicWidget.Widget.extend({
        selector: '.patient-auto-widget',
        events: {
            'input .patient-input': '_onInput',
        },

        start: function () {
            this._super.apply(this, arguments);
        },

        _onInput: function (e) {
            var self = this;
            var query = $(e.currentTarget).val();

            this._rpc({
                route: '/search_patients',
                params: {query: query}
            }).then(function (data) {
                self._populateOptions(data);
            });
        },

        _populateOptions: function (data) {
            var dropdown = $('#custom_patient_dropdown');
            dropdown.empty();

            for (var i = 0; i < data.length; i++) {
                dropdown.append('<div class="custom-patient-option" data-id="' + data[i].id + '">' + data[i].name + '</div>');
            }

            dropdown.show();

            $('.custom-patient-option').click(function () {
                var selectedId = $(this).attr('data-id');
                var selectedName = $(this).text();

                $('#patient_input').val(selectedName);
                $('#patient_id').val(selectedId); // Update the hidden field
                dropdown.hide();
            });
        },
    });

publicWidget.registry.HospitalWidget = publicWidget.Widget.extend({
    selector: '.hospital-auto-widget',
    events: {
        'input .hospital-input': '_onInput',
        'change #payment_methods': '_onPaymentMethodChange',  // Add event for payment method change
    },

    start: function () {
        this._super.apply(this, arguments);
    },

    _onInput: function (e) {
        var self = this;
        var query = $(e.currentTarget).val();
        var paymentMethod = $('#payment_methods').val();

        // Set `include_activation` based on selected payment method
        var includeActivation = !(paymentMethod === 'cash' || paymentMethod === 'hospitalcash');
        console.log('includeActivation')
        console.log(includeActivation)
        this._rpc({
            route: '/search_hospitals',
            params: {
                query: query,
                include_activation: includeActivation
            }
        }).then(function (data) {
            self._populateOptions(data);
        });
    },

    _onPaymentMethodChange: function () {
        var paymentMethod = $('#payment_methods').val();
        if (paymentMethod === 'cash' || paymentMethod === 'hospitalcash') {
            $('#hospital_id').val(''); // Clear hospital_id if payment method is cash or hospital cash
        }
        // Trigger a search to update the hospital list based on new payment method
        $('#hospital_input').trigger('input');
    },

    _populateOptions: function (data) {
        var dropdown = $('#custom_hospital_dropdown');
        dropdown.empty();

        for (var i = 0; i < data.length; i++) {
            dropdown.append('<div class="custom-hospital-option" data-id="' + data[i].id + '">' + data[i].name + '</div>');
        }

        dropdown.show();

        $('.custom-hospital-option').click(function () {
            var selectedId = $(this).attr('data-id');
            var selectedName = $(this).text();

            $('#hospital_input').val(selectedName);
            $('#hospital_id').val(selectedId); // Update the hidden field
            // Reset the surgeon selection
            $('#surgeon_input').val('');  // Clear surgeon input field
            $('#surgeon_id').val('');  // Clear hidden surgeon_id field

            dropdown.hide();
        });
    },
});


    publicWidget.registry.WebsiteMedicalAppointmentWidget = publicWidget.Widget.extend({
        selector: '#new_medical_addition_portal',
        events: {
            'click .o_website_links_edit_codes': '_addNewRow',
            'click .remove': '_removeRow',
        },

        start: function () {
            this._super.apply(this, arguments);
        },

        _addNewRow: function () {
            var self = this;
            var table = $("#invoice");
            var rowCount = table.find("tbody tr").length + 1;
            var newRow = $(`<tr>
            <td>
                <div class="form-group surgeon-auto-widget">
                    <input type="text" class="form-control product-search" name="product_search${rowCount}" autocomplete="off" required="required"/>
                    <input type="hidden" name="op_add_product_id${rowCount}" class="product-id"/>
                    <div class="custom-dropdown custom-surgeon-dropdown"></div>
                </div>
            </td>
            <td>
                <input type="number" min="1" value="1" name="quantity${rowCount}" class="form-control"/>
            </td>
            <td>
                <button class="btn btn-danger remove">
                    <i class="fa fa-times" aria-hidden="true"></i>
                </button>
            </td>
        </tr>`);
            table.find("tbody").append(newRow);
            self._initializeLiveSearch(newRow.find('.product-search'));
        },

        _initializeLiveSearch: function (searchElement) {
            var self = this;
            searchElement.on('input', function () {
                var searchInput = $(this);
                var searchTerm = searchInput.val();
                var resultsContainer = searchInput.siblings('.custom-surgeon-dropdown');

                if (searchTerm.length < 1) {
                    resultsContainer.empty().hide();
                    return;
                }

                ajax.jsonRpc('/odoo/rpc/for/get_products', 'call', {
                    'search_term': searchTerm
                }).then(function (data) {
                    self._populateProductOptions(data, resultsContainer, searchInput);
                });
            });
        },

        _populateProductOptions: function (data, dropdown, searchInput) {
            dropdown.empty();
            data.forEach(function (item) {
                var resultItem = $('<div class="custom-surgeon-option" data-id="' + item.id + '">' + item.display_name + '</div>');
                resultItem.on('click', function () {
                    searchInput.val(item.display_name);
                    searchInput.siblings('.product-id').val(item.id);
                    dropdown.hide();
                });
                dropdown.append(resultItem);
            });
            if (data.length > 0) {
                dropdown.show();
            } else {
                dropdown.hide();
            }
        },

        _removeRow: function (e) {
            $(e.currentTarget).closest('tr').remove();
        },
    });

    publicWidget.registry.MoreProductWidget = publicWidget.Widget.extend({
        selector: '#add-items',
        events: {
            'click .addMoreProduct': '_addMoreProductRow',
            'click .remove': '_removeRow',
        },

        start: function () {
            this._super.apply(this, arguments);
        },

        _addMoreProductRow: function () {
            var table = $("#more_product");
            var rowCount = table.find("tbody tr").length + 1;
            var newRow = $(`<tr>
        <td>
            <div class="form-group product-auto-widget">
                <input type="text" class="form-control product-search" name="product_search${rowCount}" autocomplete="off" required="required"/>
                <input type="hidden" name="op_add_more_product_id${rowCount}" class="product-id"/>
                <div class="custom-dropdown custom-surgeon-dropdown"></div>
            </div>
        </td>
        <td>
            <input type="checkbox" name="internal${rowCount}" class="checkbox" value="on"/>
        </td>
        <td>
            <input type="checkbox" name="external${rowCount}" class="checkbox" value="on"/>
        </td>
        <td>
            <input type="checkbox" name="empties${rowCount}" class="checkbox" value="on"/>
        </td>
        <td>
            <button class="btn btn-danger remove">
                <i class="fa fa-times" aria-hidden="true"></i>
            </button>
        </td>
    </tr>`);
            table.find("tbody").append(newRow);
            this._initializeLiveSearch(newRow.find('.product-search'));
        },

        _initializeLiveSearch: function (searchElement) {
            var self = this;
            searchElement.on('input', function () {
                var searchInput = $(this);
                var searchTerm = searchInput.val();
                var resultsContainer = searchInput.siblings('.custom-surgeon-dropdown');

                if (searchTerm.length < 1) {
                    resultsContainer.empty().hide();
                    return;
                }

                ajax.jsonRpc('/odoo/rpc/for/get_products', 'call', {
                    'search_term': searchTerm
                }).then(function (data) {
                    self._populateProductOptions(data, resultsContainer, searchInput);
                });
            });
        },

        _populateProductOptions: function (data, dropdown, searchInput) {
            dropdown.empty();
            data.forEach(function (item) {
                var resultItem = $('<div class="custom-surgeon-option" data-id="' + item.id + '">' + item.display_name + '</div>');
                resultItem.on('click', function () {
                    searchInput.val(item.display_name);
                    searchInput.siblings('.product-id').val(item.id);
                    dropdown.hide();
                });
                dropdown.append(resultItem);
            });
            if (data.length > 0) {
                dropdown.show();
            } else {
                dropdown.hide();
            }
        },

        _removeRow: function (e) {
            $(e.currentTarget).closest('tr').remove();
        },
    });

});