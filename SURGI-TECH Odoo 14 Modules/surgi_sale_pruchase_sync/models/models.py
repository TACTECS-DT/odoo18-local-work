from odoo import api
from odoo import fields
from odoo import models

class sale_order(models.Model):
    _inherit = "sale.order"
    deliver_to = fields.Many2one(string="Dilver To ", comodel_name="stock.picking.type")
    def pruchase_interchange(self):
        sourcedocument = self.id
        porder = self.env['purchase.order'].search([['auto_sale_order_id', '=', sourcedocument]])
        sql = "update purchase_order set picking_type_id=%d , name =%s where id=%d" % (self.deliver_to.id,"'"+self.display_name+" - "+str(porder.name)+"'",porder.id)
        self.env.cr.execute(sql)
        #porder.update({'picking_type_id':sourcedocument})
        #porder.update({'name': self.display_name+" - "+str(porder.display_name)})

        porder.button_confirm()
        #print("d")

    def action_confirm(self):
        res = super(sale_order, self).action_confirm()
        if self.deliver_to.id:
            self.pruchase_interchange()