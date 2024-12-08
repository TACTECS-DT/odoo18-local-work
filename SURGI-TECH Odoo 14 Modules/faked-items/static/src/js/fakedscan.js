odoo.define("stock_scan_faked.action_start_scanning", function(require){
   "use strict";
    var core = require("web.core");
    var Widget = require("web.Widget");
    var _t = core._t;
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
var AbstractAction = require('web.AbstractAction');

 var FakedScanningModel = Backbone.Model.extend({


             initialize: function (session, attributes) {
             var lochash = location.hash.substr(1);
        var activeid = lochash.substr(lochash.indexOf('id=')).split('&')[0].split('=')[1];

            var self = this;
            this.olditems={};
            this.active_id=activeid;
            this.updateditems={};
            this.newitems={};
            this.tquantity=0;
            this.allitems={};
            rpc.query({
                model:'stock.biking.faked.item',
                method: 'get_scanned_items',
                args: [self.active_id],
            // args:[],
            }).then(function (result) {
            result = JSON.parse(result);
           self.olditems=result.olditems;
           self.tquantity=result.tquantity;
          // $.extend(self.allitems,result.olditems);
            self.allitems=result.olditems;
           $(".totalQty").html(result.tquantity);
             $(".fakeditemsline").html("");
            let  itemslines="";
           $.each(self.allitems, function(key,value) {
               itemslines+="<tr><td>"+value.serial+"</td><td>"+value.quantity+"</td></tr>";
            });
           $(".fakeditemsline").append(itemslines);

           });





            },
 });

var ScanningFaked = AbstractAction.extend({
   template: "ScanningFake",
 xmlDependencies: ['/faked-items/static/src/xml/fakedtemplate.xml'],

        events: {
            "click .cancel_button": "cancel_button",
            "click .deleteScan": "deleteScan",
            "change .qty": "calculateTotalQty",
            "keyup .qty": "calculateTotalQty",
            "change #default_code": function () {
            $("#scan_box").focus();
            /*
            console.log("5x");
                var self = this;
                var modalShown = false;
                $("div[id$=Modal]").each(function () {
                    if (($(this).data('bs.modal') || {}).isShown) {
                        document.getElementById('audio').play();
                        $('#default_code').val('').blur().focus();
                        modalShown = true;
                    }
                });
                if (modalShown == false) {
                    var default_code = $('#default_code').val();
                    if (default_code.trim() != '') {
                        if (self.stock_data.codeProducts[default_code]) {
                            $('input#scan_box').focus();
                        } else {
                            document.getElementById('audio').play();
                            $('#default_code').val('').blur().focus();
                            $("#productNotFoundModal").modal();
                        }
                    }
                }
                */
               // alert("ddddddddd");
            },

            "change #scan_box": "search_product",
            "click .selectLine": "selectLine",
            "change #expiration_date": "search_product_third",
            "click .save_button": function () {
                var self = this;

console.log("6");
                var stock_picking = rpc.query({
                    model:'stock.biking.faked.item',
                    method: 'savescanned_items',
                    args: [self.stock_data.active_id, self.stock_data.newitems, self.stock_data.updateditems,self.stock_data.allitems,self.stock_data.tquantity],
                }).then(function (server_ids) {

                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'stock.picking',
                        res_id: parseInt(self.stock_data.active_id),
                        views: [[false, 'form']],
                        target: 'main',
                    });
                });
            }

        },

   init: function(parent, options) {
            this._super.apply(this, arguments);
            this.stock_data = new FakedScanningModel(require);
           /// this.filltable();
        },

         search_product:function(){
                if($("#default_code").val()==""){
                    console.log(this.stock_data);
                    if($("#scan_box")!=""){

                    this.checkserial();
                      $("#scan_box").val("");
                    $("#scan_box").focus();

                }

            }else{
                $("#expiration_date").focus();
                }





            },
            //},

            search_product_third:function(){

            var self = this;
            var expiration_date = $('input#expiration_date').val();
            if (expiration_date.trim() != '') {

            var dateArray = expiration_date.split('-');
                var dateCheck = new Date(expiration_date);
                if (dateArray.length == 2) {
                        expiration_date = expiration_date + "-01";
                    }
                    var scan_box = $('input#scan_box').val();
                    var default_code = $('input#default_code').val();

                self.checkserial();
                $('input#expiration_date').val("");
                $('input#scan_box').val("");
                $('input#default_code').val("");
                $('input#default_code').focus();
            }





            },
            checkserial:function(){
            var scan_box=$("#scan_box").val();
                    if(scan_box==""){
                    $("#scan_box").val();
                    $("#scan_box").focus();
                    }
                    else if(this.stock_data.allitems[scan_box]==null){
                      this.stock_data.newitems[scan_box]={
                        "serial":scan_box,"quantity":1,'stock_bikeid':this.stock_data.active_id
                        };
                        this.stock_data.allitems[scan_box]={
                        "serial":scan_box,"quantity":1
                        };
                    //this.stock_data.totalquantity+=1;
                    }else{
                           var  q=0;
                            if(this.stock_data.updateditems[scan_box]!=null){
                            q=this.stock_data.updateditems[scan_box].quantity+1;
                            this.stock_data.updateditems[scan_box].quantity=q;
                            this.stock_data.allitems[scan_box].quantity=q;
                            }
                            else if(this.stock_data.newitems[scan_box]!=null){
                            q=this.stock_data.newitems[scan_box].quantity+1;
                            this.stock_data.newitems[scan_box].quantity=q;
                            this.stock_data.allitems[scan_box].quantity=q;
                            }
                            else if(this.stock_data.olditems[scan_box]!=null){
                            q=this.stock_data.olditems[scan_box].quantity+1;
                            this.stock_data.allitems[scan_box].quantity=q;
                            this.stock_data.updateditems[scan_box]=this.stock_data.olditems[scan_box];
                            this.stock_data.updateditems[scan_box].quantity=q;
                            }
                    }
                    this.stock_data.tquantity+=1;
                    $(".totalQty").html(this.stock_data.tquantity);

                        this.filltable();
                    },
            filltable:function(){
                 var itemslines="";
                 $(".fakeditemsline").html("");
           $.each(this.stock_data.allitems, function(key,value) {
               itemslines+="<tr><td>"+value.serial+"</td><td>"+value.quantity+"</td></tr>";
            });
           $(".fakeditemsline").append(itemslines);
            },
            cancel_button: function (e) {
        console.log("14");
            var self = this;
            self.do_action({
                type: 'ir.actions.act_window',
                res_model: 'stock.picking',
               res_id: parseInt(self.stock_data.active_id),
                views: [[false, 'form']],
                target: 'main',
            });
        },

});
 core.action_registry.add("stock.biking.faked.item", ScanningFaked);
return ScanningFaked;

});