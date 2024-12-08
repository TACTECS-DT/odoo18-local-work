odoo.define('eg-invoice.NewButtonList', function(require) {
    'use strict';

    var ListController = require("web.ListController");
    var includebtn={
        renderButtons:function(){
            console.log("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDD");
            this._super.apply(this, arguments);
            var cancelbutton=this.$buttons.find(".o_icancelbtn");
            cancelbutton.on('click',this.proxy("cancel_button_click"));
            var rejectbutton=this.$buttons.find(".o_ibanbtn");
            rejectbutton.on('click',this.proxy("reject_button_click"));
        },//end render button

        cancel_button_click:function(e){
            console.log("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA");
        },
        reject_button_click:function(e){
            console.log("BBBBBBBBBBBBBBBBBBBBBBBBBBBBB");
        }
    };//ed list

   

    ListController.include(includebtn);

    
});

// odoo.define('eg-invoice.ButtonsInList', function (require) {
//     "use strict";

//     var ListController = require("web.ListController");
    
    
//     var includeDict = {
//         renderButtons: function () {
//             this._super.apply(this, arguments);
//             if (this.modelName === "account.account") {
//                 var coa_button = this.$buttons.find('.o_list_button');
//                 coa_button.on('click', this.proxy('o_button_click'));
//             }
//         },
//         o_button_click: function(e){
          
//                 var action = {
//                     type: 'ir.actions.client',
//                     name: 'New Custom View',
//                     tag: 'account_group_hierarchy',
                  
//                 };
//                 this.do_action(action);
           

    
//         }
//     };
//     ListController.include(includeDict);
    

// });
    