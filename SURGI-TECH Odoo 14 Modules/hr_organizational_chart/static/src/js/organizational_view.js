odoo.define('hr_organizational_chart.view_chart', function (require){
"use strict";
var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var rpc = require('web.rpc');
var ActionManager = require('web.ActionManager');
var _t = core._t;


var EmployeeOrganizationalChart =  AbstractAction.extend({

    contentTemplate: 'OrganizationalEmployeeChart',
    events: {
        'click img': '_getChild_data',
        'click .employee_name': 'view_employee',
        'click #print_tree': 'print_tree',
        'click #zoom_in': 'zoom_in',
        'click #zoom_reset': 'zoom_reset',
        'click #zoom_out': 'zoom_out',
        'change #departments':'dep_changed',
        'change #locations':'location_change',
    },

    init: function(parent, context) {
        //this.deps=this._getdepartments();
        this._super(parent, context);
        this.renderEmployeeDetails();
        this._getdepartments();
        this._getlocations();
        this.currentZoom=1;
    },
    print_tree:function(){
        window.print();

    },
    zoom_in:function(){
        self=this;
        self.currentZoom+=.1;
        $('.empchartclass').css('transform', 'scale('+self.currentZoom+')');

    },
    zoom_reset:function(){
        self.currentZoom=1;
        $('.empchartclass').css('transform', 'scale('+self.currentZoom+')');
    },
    zoom_out:function(){
        self.currentZoom-=.1;
        $('.empchartclass').css('transform', 'scale('+self.currentZoom+')');
    },
    

    renderEmployeeDetails: function (){
        var employee_id = 1
        var self = this;
        this._rpc({
            route: '/get/parent/employee',
        }).then(function (result) {
            self.parent_len = result[1];
            $.ajax({
                url: '/get/parent/child',
                type: 'POST',
                data: JSON.stringify(result[0]),
                success: function (value) {
                        $('#o_parent_employee').append(value);
                        },
            });

        });

    },
    _getdepartments:function(events){
      //  var departments=new Model('hr.organizational.chart');
        rpc.query({    
        model: 'hr.organizational.chart',//your model,

        method:'get_departments', //your method,,
   
       args: []
   
   }).then(function (result) {
       console.log(result);
     
     $.each( result, function( key, value ) {
        $("#departments").append(`<option value="${key}">
        ${value}
   </option>`);
       });
   
               

      
   
   });

    },
    _getlocations:function(events){
        //  var departments=new Model('hr.organizational.chart');
        if ($("#departments").val()==""){
            $("#locations").find('option').remove().end().append('<option value="">All</option>') ;

        }
        else{
          rpc.query({    
          model: 'hr.organizational.chart',//your model,
  
          method:'get_locations', //your method,,
     
         args: [{
             'dep_l_id':$("#departments").val(),
         }]
     
     }).then(function (result) {
         console.log(result);
       for(var i=0;i<=result.length;i++){
                 $("#locations").append(`<option value="${result[i]}">
          ${result[i]}
     </option>`);
       }
    //    $.each( result, function( key, value ) {
    //       $("#departments").append(`<option value="${key}">
    //       ${value}
    //  </option>`);
    //      });
     
                 
  
        
     
     });
                }
      },
    dep_changed:function(){
        var employee_id = 1
        var self = this;
        
        this._rpc({
            route: '/get/dep/employees',
            params: {
                dep_id:$('#departments').val(),
            },
        }).then(function (result) {
            self.parent_len = result[1];
            $.ajax({
                url: '/get/parent/child',
                type: 'POST',
                data: JSON.stringify(result[0]),
                success: function (value) {
                        $('#o_parent_employee').html(value);
                        $("#charttitle").html($('#departments option:selected').text());
                      //  self._getlocations();
                        },
            });

        });
        
    },
    location_change:function(){
        var employee_id = 1
        var self = this;
        
        this._rpc({
            route: '/get/dep/employees',
            params: {
                dep_id:$('#departments').val(),
            },
        }).then(function (result) {
            self.parent_len = result[1];
            $.ajax({
                url: '/get/parent/child?loc_id='+$('#locations').val(),
                type: 'POST',
                data: JSON.stringify(result[0]),
                success: function (value) {
                        $('#o_parent_employee').html(value);
                        $("#charttitle").html($('#departments option:selected').text());
                      //  self._getlocations();
                        },
            });

        });
        
    },
    _getChild_data: function(events){
        console.log(events)
        if(events.target.parentElement.className){
            var self = this
            this.id = events.target.parentElement.id;
            this.check_child =  $( "#"+this.id+".o_level_1" );
            if (this.check_child[0]){
                this.colspan_td = this.check_child[0].parentElement.parentElement
                this.tbody_child = this.colspan_td.parentElement.parentElement
                var child_length = this.tbody_child.children.length
                if (child_length == 1){
                    this._rpc({
                        route: '/get/parent/colspan',
                        params: {
                            emp_id: parseInt(this.id),
                        },
                    }).then(function (col_val){
                        if (col_val){
                            self.colspan_td.colSpan = col_val;
                        }
                    });
                    this._rpc({
                        route: '/get/child/data',
                        params: {
                            click_id: parseInt(this.id),
                        },
                    }).then(function (result){
                        if (result){
                        $(result).appendTo(self.tbody_child);
                        }
                    });
                }
                else{
                    for(var i = 0;i < 3; i++){
                        this.tbody_child.children[1].remove();
                    }
                    self.colspan_td.colSpan = 2;
                }

            }
        }
    },
    view_employee: function(ev){
        if (ev.target.parentElement.className){
            var id = parseInt(ev.target.parentElement.parentElement.children[0].id)
            this.do_action({
            name: _t("Employee"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            res_id: id,
            view_mode: 'form',
            views: [[false, 'form']],
            })
        }
    },
});
    core.action_registry.add('organization_dashboard', EmployeeOrganizationalChart);

});
