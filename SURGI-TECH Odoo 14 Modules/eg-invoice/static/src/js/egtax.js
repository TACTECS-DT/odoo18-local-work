odoo.define('eg-invoice.action_get_live_invoices', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var lcontroller = require("web.ListController");
    var lmodel = require("web.ListModel");
    var lview = require("web.ListView");
    var lreder = require("web.ListRenderer");
    //     lview.extend({});
    var rpc = require('web.rpc');
    var QWeb = core.qweb;


    var ClientAction = AbstractAction.extend({


        template: 'action_get_live_invoices',
        events:{
            "click .previouspage":"clickPrev",
            "click .clickNext":"clickNext",
            "change .query_list":"queryChanged",
            "keyup .o_searchview_input":"makeSearch",
            "click .cancelinv":"cancelinvclicked",
            "click .rejectinv":"rejectinvclick",
            "click .docancel":"docancel",
        
        },
        clickPrev:function(){
            var self = this;
           
            if(self.currentpage==1){
                alert("You Have Reached Last Page");
                
        }else{
            self.currentpage=self.currentpage-1;
      
            self._rpc({
                model: 'egytax.getdocuments',
                method: 'get_live_invoices',
                kwargs: {'direction':self.direction,'page':self.currentpage,'pagesize':self.numperpage},
            }).then(function (datas) {
               
                console.log("dataaaaaa", datas)
                //self.$('.o_list_table').html(
                //     QWeb.render('action_get_live_invoices', {
                //     invoice_lines: datas,
                // });//);
                // self.datas=datas;
                // alert(datas.metadata['totalPages']);
           //   var pages=datas.metadata['totalPages'];
            //   self.pages=pages;
             //  self.currentpage=1;
             //  var currentpage=Math.ceil(datas.metadata['totalCount']/self.numperpage);
                var pargs={
                    invoice_lines : datas.result,
                    
                    
                };
                pargs['direction']=self.direction;
                console.log(self.direction);
                
                $('.table_view').html(QWeb.render('liveinvoicetable', pargs));
                
                //self.$el.find('.pageseg').text(self.currentpage);
            });
            self.$el.find('.curpageseg').text(self.currentpage);
        }



        },
        clickNext:function(){
            var self = this;
            if(self.currentpage==self.pages){
                    alert("You Have Reached Last Page");
                    
            }else{
                self.currentpage=self.currentpage+1;
          
                self._rpc({
                    model: 'egytax.getdocuments',
                    method: 'get_live_invoices',
                    kwargs: {'direction':self.direction,'page':self.currentpage,'pagesize':self.numperpage},
                }).then(function (datas) {
                   
                    console.log("dataaaaaa", datas)
                    //self.$('.o_list_table').html(
                    //     QWeb.render('action_get_live_invoices', {
                    //     invoice_lines: datas,
                    // });//);
                    // self.datas=datas;
                    // alert(datas.metadata['totalPages']);
               //   var pages=datas.metadata['totalPages'];
                //   self.pages=pages;
                 //  self.currentpage=1;
                 //  var currentpage=Math.ceil(datas.metadata['totalCount']/self.numperpage);
                    var pargs={
                        invoice_lines : datas.result,
                        
                        
                    };
                    pargs['direction']=self.direction;
                    console.log(self.direction);
                    
                    $('.table_view').html(QWeb.render('liveinvoicetable', pargs));
                    
                    //self.$el.find('.pageseg').text(self.currentpage);
                });
                self.$el.find('.curpageseg').text(self.currentpage);
            }
            
        },

        queryChanged:function(){
           
        },
        cancelinvclicked:function(event){
            
            var self=event.target;
            let uuid=$(self).attr("datauuid");
            let name=$(self).attr("datauname");
            console.log(event);
            this.cancelwindow(self,uuid,name);
        },
        cancelwindow:function(self,uuid,name){
            
            $("#cancelmsg").text("Are U Sure U Want Cancel "+name);
            $("#invouuid").val(uuid);
        },
        docancel:function(){
            var self = this;
            self._rpc({
                model: 'egytax.getdocuments',
                method: 'cancelsentinvoice',
                kwargs: {
               
                
                'uuid':$("#invouuid").val(),
                'reason':$("#objreason").val()},
            }).then(function (datas) {
               
            });
        },
        rejectinvclick:function(){
            var self = this;
            self._rpc({
                model: 'egytax.getdocuments',
                method: 'Rejectinvoice',
                kwargs: {
               
                
                'uuid':$("#invouuid").val(),
                'reason':$("#objreason").val()},
            }).then(function (datas) {
               
            });
        },
        makeSearch:function(e){
            var event=e;
            if(e.originalEvent.key=="Enter"){
                var self = this;
            if(self.$el.find('.o_searchview_input').val()!=''){
            self._rpc({
                model: 'egytax.getdocuments',
                method: 'searchuuidinvoice',
                kwargs: {'uuid':self.$el.find('.o_searchview_input').val()},
            }).then(function (datas) {
                console.log("dataaaaaa", datas)
                //self.$('.o_list_table').html(
                //     QWeb.render('action_get_live_invoices', {
                //     invoice_lines: datas,
                // });//);
                // self.datas=datas;
                // alert(datas.metadata['totalPages']);
               
                var pargs={
                    invoice_lines : [datas],
                    
                    // pages:self.datas['pages'],
                    // currentpage:self.datas['currentpage']
                };
                pargs['direction']=self.direction;
               
                
                $('.table_view').html(QWeb.render('liveinvoicetable', pargs));
                self.$el.find('.curpageseg').text(1);
                self.$el.find('.pageseg').text(1);
            });
                }else{
                    self.load_data();
                }
            
        
        }
            
        },

        init: function (parent, action) {
            this._super.apply(this, arguments);
            var self = this;
            
            this._super(parent, action);
            this.direction="";
            
            if (this._title=="Live Submitted invoices"){
                self.direction="sent";
            }else{
                self.direction="received";
            }
           
            this.datas=[{'pages':1,'currentpage':1}];
            this.pages=0;
            this.currentpage=0;
            this.numperpage=50;
            
        },
        start: function () {
            var self = this;
            
            // alert("Hello")
            self.load_data(self);
        },
        load_data: function (self) {
            var self = this;
            console.log("DDDDDDDDDDDDDDDDDDDDD");
            console.log(self);
            self._rpc({
                model: 'egytax.getdocuments',
                method: 'get_live_invoices',
                kwargs: {'direction':self.direction,'page':1,pagesize:self.numperpage},
            }).then(function (datas) {
                console.log("dataaaaaa", datas)
                //self.$('.o_list_table').html(
                //     QWeb.render('action_get_live_invoices', {
                //     invoice_lines: datas,
                // });//);
                // self.datas=datas;
                // alert(datas.metadata['totalPages']);
               var pages=datas.metadata['totalPages'];
               self.pages=pages;
               self.currentpage=1;
               var currentpage=Math.ceil(datas.metadata['totalCount']/self.numperpage);
                var pargs={
                    invoice_lines : datas.result,
                    
                    // pages:self.datas['pages'],
                    // currentpage:self.datas['currentpage']
                };
                pargs['direction']=self.direction;
                console.log(self.direction);
                
                $('.table_view').html(QWeb.render('liveinvoicetable', pargs));
                self.$el.find('.curpageseg').text(self.currentpage);
                self.$el.find('.pageseg').text(self.pages);
            });
            // self.pages=pages;
            
            console.log("dd")
        },
    });
    // //listview=lview.extend({});
    // //core.form_widget_registry.add('action_get_live_invoices', listview);

    core.action_registry.add('action_get_live_invoices', ClientAction);
    return ClientAction;
});
