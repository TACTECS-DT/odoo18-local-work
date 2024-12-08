odoo.define("invoice_list.InvoiceList_Controller",function(require){
var abstractController=require("web.AbstractController");
var InvoiceList_Controller=abstractController.extend({
    custom_events: _.extend({}, AbstractController.prototype.custom_events, {}),
     /**
     * @override
     * @param parent
     * @param model
     * @param renderer
     * @param {Object} params
     */
    init: function (parent, model, renderer, params) {
      this._super.apply(this, arguments);
    }
  });

  return InvoiceList_Controller;
});
});