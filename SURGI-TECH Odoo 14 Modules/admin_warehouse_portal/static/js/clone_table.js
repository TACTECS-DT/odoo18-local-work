odoo.define('admin_warehouse_portal.admin_request', function (require) {
    "use strict";

    var core = require('web.core');
    var publicWidget = require('web.public.widget');

    var ProductSelector = publicWidget.Widget.extend({
        selector: '#service', // Listening to changes on table level
        events: {
            'change .ProductCategory_class': '_onCategoryChange',
        },

        _onCategoryChange: function (ev) {
            var self = this;
            var row = $(ev.target).closest('tr');
            var category_id = row.find('.ProductCategory_class').val();

            this._rpc({
                model: 'product.product',
                method: 'search_read',
                domain: [['categ_id', '=', parseInt(category_id)]],
                fields: ['name', 'id'],
            })
                .then(function (data) {
                    var product_selector = row.find('.product_id_class');
                    product_selector.empty();
                    _.each(data, function (product) {
                        product_selector.append(new Option(product.name, product.id));
                    });
                });
        },
    });

    publicWidget.registry.ProductSelector = ProductSelector;

    $(document).ready(function () {
        $('#addService').click(function () {
            // Remove select2 from original select
            $('.add-service:first').find('select').each(function () {
                $(this).select2('destroy');
            });

            // Clone the first row in the service table
            var clonedRow = $('.add-service:first').clone();

            // Clear the inputs of the cloned row
            clonedRow.find('input').val('');
            clonedRow.find('select').val('');

            // Add the cloned row before the last row in the service table
            $('#service tbody.multi tr:last').before(clonedRow);
        });

        $(document).on('click', '.remove', function () {
            $(this).closest('tr').remove();
        });
    });
    $(document).ready(function () {
        // Before form submit
        $('form').on('submit', function () {
            $('.add-service').each(function () {
                var qty = $(this).find('input[name="quantity"]');
                var reason = $(this).find('input[name="reason"]');


                if (!qty.val()) {
                    qty.val(1);
                }

                if (!reason.val()) {
                    reason.val('--');
                }
            });
        });
    });

    return ProductSelector;
});
