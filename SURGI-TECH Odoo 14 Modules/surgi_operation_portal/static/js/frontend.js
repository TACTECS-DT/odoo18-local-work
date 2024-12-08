odoo.define('surgi_operation_portal.edit_operation', function (require) {
    'use strict';
    //debugger;
    var rpc = require('web.rpc')
    const publicWidget = require('web.public.widget');
    var core = require('web.core');
    var session = require('web.session');
    var Widget = require('web.Widget');

    $(document).ready(function () {
        const paymentMethodsSelect = $('#payment_methods');
        const patientNameInput = $('#patient_name');
        const patientNationalIDInput = $('#patient_national_id');
        const patientNationalIDImageInput = $('#patient_national_id_image');

        function updateRequiredAttributes() {
            const isCash = paymentMethodsSelect.val() === 'cash';
            // // Set required attributes based on payment method
            // patientNameInput.prop('required', isCash);
            // patientNationalIDInput.prop('required', isCash);
            // patientNationalIDImageInput.prop('required', isCash);
        }

        // Listen for changes on the payment method select box
        paymentMethodsSelect.change(updateRequiredAttributes);

        // Call the function initially in case the payment method is already set to 'cash' when the page loads
        updateRequiredAttributes();
    });
    publicWidget.registry.MyopSubmitWidget = publicWidget.Widget.extend({
        selector: '#op_new_form',  // This should match the form's ID
        events: {
            'submit': '_onSubmitForm',
        },

        _onSubmitForm: function (event) {
            event.preventDefault();

            var formData = new FormData(event.currentTarget);
            const toast = document.getElementById('toastElement');

            $.ajax({
                url: '/my/operation/new/submit',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {
                    console.log("Success response: ", response);

                    // Parse the JSON string to a JavaScript object
                    var parsedResponse = JSON.parse(response);

                    // Access 'id' property of the parsed object
                    var operationId = parsedResponse.id;
                    console.log("Operation ID: ", operationId);

                    toast.textContent = "Operation successfully created!";
                    toast.classList.remove("warning");
                    toast.classList.add("show");

                    setTimeout(function () {
                        toast.classList.remove("show");
                        window.location = '/my/operation/' + operationId;
                    }, 3000);
                },
                error: function (error) {
                    console.log("Error occurred");
                    toastr.error('Something went wrong: ' + error.responseJSON.message);

                    let errorMsg = "An unknown error occurred.";
                    if (error.responseJSON && error.responseJSON.message) {
                        errorMsg = error.responseJSON.message;
                    }

                    toast.textContent = "Something went wrong: " + errorMsg;
                    toast.classList.add("warning");
                    toast.classList.add("show");

                    setTimeout(function () {
                        toast.classList.remove("show");
                        toast.classList.remove("warning");
                    }, 9000);
                },
            });
        },
    });


    publicWidget.registry.operation_form = publicWidget.Widget.extend({
        selector: '#op_form_ahmed',

        events: {

            'change #operation_type': '_onOperationTypeChange',
            'keydown #sale_order': '_change_sale_order',
            'click .createfreezitem': 'create_freez_items',
            'change #payment_methods': '_onPaymentMethodChange',
        },

        // init: function (parent) {
        //     this._super.apply(this, arguments);

        // },
        start: function () {
            this._super.apply(this, arguments);
            this.$paymentMethodsSelect = this.$('#payment_methods');
            this.$patientNameInput = this.$('#patient_name');
            this.$patientNationalIDInput = this.$('#patient_national_id');
            this.$patientNationalIDImageInput = this.$('#patient_national_id_image');
        this.$surgeonInput = this.$('#surgeon_input');
        this.$doctorPhoneNum = this.$('#DoctorPhoneNum');
            // Initialize the form based on the current payment method.
            this._onPaymentMethodChange();
            console.log("portal op Started");
        },
        _onOperationTypeChange: function () {
            this._update_component();
            this._updateFields();
        },
        _updateFields: function () {
            var self = this;
            var operationTypeId = this.$('#operation_type').val();
            this._rpc({
                route: '/my/operation/get_operation_type',
                params: {operation_type_id: operationTypeId}
            }).then(function (operationType) {
                var isMolnlycke = operationType.is_molnlycke;
                self.$surgeonInput.prop('required', !isMolnlycke);
                self.$doctorPhoneNum.prop('required', !isMolnlycke);
            });
        },

        _onPaymentMethodChange: function () {
            // Check if the payment method is 'cash'
            var isCash = this.$paymentMethodsSelect.val() === 'cash';

            // Set the 'required' property based on whether the payment method is 'cash'
            // this.$patientNameInput.prop('required', isCash);
            // this.$patientNationalIDInput.prop('required', isCash);
            // this.$patientNationalIDImageInput.prop('required', isCash);
        },
        _update_component: function (ev) {
            var self = this;

            this._rpc({
                route: '/my/operation/getcomponent',
                params: {
                    'op_type': $("#operation_type").val()
                }
            }).then(function (result) {
                var msg = result;
                $(".component_divs").empty();

                //  $("#component_ids").empty();
                // $("#component_ids").append(new Option("--Select--",""));
                if (result.length > 0) {
                    $.each(result, function (index, val) {
                        // $("#component_ids").append(new Option(this.name,this.id));
                        $(".component_divs").append("<div class='form-group'><input type='checkbox' value='" + this.id + "' class='checkbox' name='component_ids[]' id='component_ids[]'>  " + this.name + "</div>");
                    });

                } else {
                    alert("Error No Components Got !")
                }

            }).catch(function (reason) {
                var error = reason.message;
                console.warn(error);
            });


        },
        _get_sales_order: function (self, val) {
            //  var    self=this;
            return self._rpc({
                route: '/my/operation/getSalesOrders',
                params: {
                    'sale_order': val
                }
            }).then(function (result) {
                var msg = result;
                if (result.length > 0) {
                    let founds = result.map(g => ({'id': g['id'], 'label': g['name']}));
                    return founds;

                } else {
                    return [];
                }

            }).catch(function (reason) {
                var error = reason.message;
                console.warn(error);
            });
        },
        _change_sale_order: function (ev) {
            //var self=this;
            //this._super.apply(this);
            var self = this;
            $("#sale_order").autocomplete({
                //classes: {'ui-autocomplete': 'o_social_twitter_users_autocomplete'},
                source: function (request, response) {
                    // var accountId = self.getParent().state.data.account_id.data.id;

                    return self._rpc({
                        route: '/my/operation/getSalesOrders',
                        params: {
                            'sale_order': $("#sale_order").val()
                        }
                    }).then(function (suggestions) {
                        $("#sale_order_id").val("");
                        response($.map(suggestions, function (item) {
                            return {
                                label: item.name,
                                value: item.id
                            };
                        }));
                    });
                },
                select: function (ev, ui) {
                    $("#sale_order").val(ui.item.label);
                    $("#sale_order_id").val(ui.item.value);
                    // self._selectTwitterUser(ui.item);
                    ev.preventDefault();
                },
                html: true,
                minLength: 2,
                delay: 500,
            });
            // .data('ui-autocomplete')._renderItem = function (ul, item){
            //     return $(QWeb.render('social_twitter.users_autocomplete_element', {
            //         suggestion: item
            //     })).appendTo(ul);
            // };
            // $( "#sale_order" ).autocomplete({
            //     minLength: 0,
            //     source: function(){

            //         if($("#sale_order").val().length>3){
            //         }else{
            //             return [];
            //         }


            //     },
            //     focus: function( event, ui ) {
            //         $( "#sale_order" ).val( ui.item.name );
            //         return false;
            //     },
            //     select: function( event, ui ) {
            //         $( "#sale_order" ).val( ui.item.name );
            //         $( "#sale_order_id" ).val( ui.item.id );
            //         // $( "#project-description" ).html( ui.item.desc );
            //         // $( "#project-icon" ).attr( "src", "images/" + ui.item.icon );

            //         return false;
            //     }
            // })
            // .autocomplete( "instance" )._renderItem = function( ul, item ) {
            //     return $( "<li>" )
            //         .append( "<div>" + item.name + "</div>" )
            //         .appendTo( ul );
            // };


        },
        create_freez_items: function (ev) {

            // let freezeditems=[];
            // for(let i=0;i<=$("#opquant").length;i++){
            //     if ($("#opquant["+i+"]").is(':checked')){
            //     freezeditems.push($("#opquant["+i+"]").val());
            //     }
            // }
            // if(freezeditems.length<1){
            //     return ;
            // // }
            // return self._rpc({
            //     route: '/my/operation/getSalesOrders',
            //     params: {
            //         'freezed_items':freezeditems
            //     }
            //      }).then(function(result) {


            //      });


        }


    });
    publicWidget.registry.patientIDFile = publicWidget.Widget.extend({
        selector: '#patient_national_id_image',
        events: {
            'change ': 'update_attachment_1',
        },


        update_attachment_1: function (ev) {

            if (ev.currentTarget.value === '') {
                document.getElementById('base64').value = '';

            } else {
                var f = ev.currentTarget.files[0];
                var reader = new FileReader();

                reader.onload = (function (theFile) {
                    return function (e) {
                        var binaryData = e.target.result;
                        //Converting Binary Data to base 64
                        var base64String = window.btoa(binaryData);
                        //showing file converted to base64
                        document.getElementById('base64').value = base64String;
                    };
                })(f);
                // Read in the image file as a data URL.
                reader.readAsBinaryString(f);

            }
            var fullPath = ev.currentTarget.value;
            if (fullPath) {
                var startIndex = (fullPath.indexOf('\\') >= 0 ? fullPath.lastIndexOf('\\') : fullPath.lastIndexOf('/'));
                var filename = fullPath.substring(startIndex);
                if (filename.indexOf('\\') === 0 || filename.indexOf('/') === 0) {
                    filename = filename.substring(1);
                }
                document.getElementById('file_name2').value = filename;
                console.log(filename);
            }
        },


    });

    //return edit_operation;
    // $(document).ready(function(){
    //         console.warn("Get Component");
    //             $("#operation_type").on("change", function () {
    //              console.log("Operation Changes Happend");
    //              rpc.query({
    //                 model: 'operation.operation',
    //                 method: 'getOpComponent',
    //                 args:[{optype : $("#operation_type").val()}],
    //             }).then(function() {
    //                 console.log("Successed");
    //             }).catch(function(reason) {
    //                 var error = reason.message;
    //                 console.warn(error);
    //             });
    //     });

    // });

    // $(document).ready(function(){

    //     $("#operation_type").on("change", function () {
    //         console.log("Operation Changes Happend");
    //         var form = document.getElementById('form');
    //         var current_url = window.location.pathname;
    //         $.ajax({
    //             url: form.action,
    //             type: "POST",
    //             data: fd,
    //             dataType: 'json',
    //             cache: false,
    //             contentType: 'application/json; charset=utf-8',
    //             processData: false,
    //             success: function(data){
    //                 console.log('Success! ' + data);
    //                 form.submit();
    //             },
    //             error: function(data){
    //                 document.getElementById('form_error').innerHTML = "Stran je potrebno osvežit!";
    //                 console.log(data);
    //             }

    //         }); 
    //     });


    // });


    // var operation_form = new publicWidget.registry.operation_form(this);
    // operation_form.appendTo($(".op_form_ahmed"));
    // return publicWidget.registry.operation_form;


});

//Ahmed Abd Al Aziz Code


//     $(document).ready(function(){
//         console.warn("Get Component out");
//             $("#operation_type").on("change", function () {
//              console.log("Operation Changes Happend out");
//              rpc.query({
//                 model: 'operation.operation',
//                 method: 'getOpComponent',
//                 args:[{optype : $("#operation_type").val()}],
//             }).then(function() {
//                 console.log("Successed");
//             }).catch(function(reason) {
//                 var error = reason.message;
//                 console.warn(error);
//             });
//     });

// });


//     $(document).on('click', '.remove', function () {
//         var lenRow = $('#invoice tbody tr').length;

//         $(this).parents('tr').remove();

//     });
//     if ($('.op_edit_form').length || $('.op_new_form').length) {
//         function applyCheckboxEventListeners() {
//             var checkboxes = document.querySelectorAll('.checkbox');
//             checkboxes.forEach(function (checkbox) {
//                 var hiddenInput = checkbox.parentNode.querySelector('input[type="hidden"]');
//                 if (hiddenInput) {
//                     if (checkbox.checked) {
//                         hiddenInput.value = 'True';
//                     } else {
//                         hiddenInput.value = 'False';
//                     }
//                     checkbox.addEventListener('change', function () {
//                         if (this.checked) {
//                             hiddenInput.value = 'True';
//                         } else {
//                             hiddenInput.value = 'False';
//                         }
//                     });
//                 }
//             });
//         }

// // Call the function after the document has loaded
//         document.addEventListener('DOMContentLoaded', function () {
//             applyCheckboxEventListeners();
//         });

// // Call the function every time a new row is cloned

//         $("#addMoreProduct").click(function () {
//             var clone = $('#more_product > tbody #add_more_product:last').clone();
//             clone.find('input').val('');
//             clone.find(':checkbox').prop('checked', false); // uncheck all checkboxes
//             clone.find('.hidden_text').val('False');// uncheck all checkboxes
//             clone.insertAfter('#more_product > tbody #add_more_product:last');
//             applyCheckboxEventListeners();

//         });
//         $("#addProduct").click(function () {
//             var clone = $('#invoice > tbody #addPart:last').clone();

//             clone.insertAfter('#invoice > tbody #addPart:last');

//         });

//     }
//     ;


//     $(document).ready(function () {
//         if ($('.op_edit_form').length) {
//             var current_op_id = $('#current_op_id').val();
//             var component_ids_ids = $('#component_ids_ids').val();
//
//             if (component_ids_ids) {
//                 console.log('current_op_id', current_op_id);
//                 console.log('component_ids_ids', JSON.parse(component_ids_ids));
//                 console.log('edit operation');
//
//                 try {
//                     var componentIds = JSON.parse(component_ids_ids);
//                     rpc.query({
//                         model: 'product.product',
//                         method: 'search_read',
//                         args: [[['id', 'in', componentIds]]],
//                         kwargs: {
//                             fields: ['id', 'default_code', 'name'],
//                         },
//                     }).then(function (result) {
//                         var myList = result.map(function (record) {
//                             return {
//                                 id: record.id,
//                                 text: "[" + record.default_code + "]" + ' - ' + record.name
//                             };
//                         });
//                         console.log(myList);
//
//                         var $select = $('#component_ids');
//                         $.each(myList, function (index, item) {
//                             var option = new Option(item.text, item.id, true, true);
//                             $select.append(option);
//                         });
//
// // Set the initial values of the select2 control
// //                         $select.val(componentIds).trigger('change');
//
// // Only submit the selected ids
//                         $('#submit-button').click(function () {
//                             var selectedIds = $select.select2('data').map(function (item) {
//                                 return item.id;
//                             });
//                             $('#component_ids').val(JSON.stringify(selectedIds));
//                         });
//
//                     });
//                 } catch (error) {
//                     console.log('Error parsing JSON data:', error);
//                 }
//             }
//         }
//     });


//});


// Relate component to operation Types

// $(document).ready(function(){

//     $("#operation_type").on("change", function () {
//         console.log("Operation Changes Happend");
//     });


// });
