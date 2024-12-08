# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

# class surgi_sales_discount(models.Model):
#     _name = 'surgi_sales_discount.surgi_sales_discount'
#     _description = 'surgi_sales_discount.surgi_sales_discount'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
class sale_order(models.Model):
    _inherit = 'sale.order'
    discount_options = fields.Selection(
        selection=[("No Discount", "No Discount"),
                   ("Trade Discount", "Trade Discount")],
     default="No Discount"   , string="Choose Discount Type", store=True, tracking=True)
    discount_value = fields.Float('Sale Discount')
    #discount_value_view = fields.Float(string='Sale Discount')
    #@api.onchange('discount_value')
    def change_discount_view(self):
        for rec in self:
            #if rec.discount_type_id=='Precent' and (rec.discount_value > 5 or rec.discount_value < 0):
            #    raise UserError('You Cant make discount more than 5%')
            if rec.discount_type_id=='Precent' and  rec.discount_value > 5 and not self.env.user.has_group('surgi_sales_discount.sales_discount_permissions'):
                raise UserError('You Need Permission make discount more than 5% which is '+str(rec.amount_total*.05))
                raise UserError(str(rec.discount_value)+"---------"+str(rec.amount_total*.05))
            if  rec.discount_type_id=='Fixed' and  rec.discount_value > (rec.amount_total*.05) and not self.env.user.has_group('surgi_sales_discount.sales_discount_permissions'):
                    raise UserError('You Need Permission make discount more than 5% which is '+str(rec.amount_total*.05))

            #rec.discount_value=float(rec.discount_value_view)
    # amount_after_discount = fields.Monetary('Amount After Discount', store=True, readonly=True,
    #                                         compute='_compute_amount_after_discount',
    #                                         )
    discount_type_id = fields.Selection(selection=[("Precent", "Precent"),("Fixed", "Fixed")],default="Fixed", string="Choose Discount Type", store=True, tracking=True)
    def calculate_tax_fixed_total(self,quantity,unitprice,totalammount,fixedammount):
        itemprice=(quantity*unitprice)/totalammount
        itemprice_fixed=round(fixedammount/totalammount,2)*100
        return (fixedammount/totalammount)*100
    
    #@api.model
    #@api.onchange("discount_value")
    def change_discount_value(self):
        for rec in self:
            if rec.discount_value <= 0  and not self.env.user.has_group('surgi_sales_discount.sales_discount_apply_negative'):
                raise UserError('You Cant Make Negative Discount Ask Permission First')
        self.change_discount_view()
        if self.discount_type_id=="Precent":
            self.reset_all_discount_lines(self.discount_value)
        elif self.discount_type_id=="Fixed":
            totalammountx=0
            for line in self.order_line:
                totalammountx += (line.price_unit * line.product_uom_qty)
            for line in self.order_line:
                discount=self.calculate_tax_fixed_total(line.product_uom_qty,line.price_unit,totalammountx,self.discount_value)
                line.discount = discount
        super(sale_order, self).changed_line_ids()        






    @api.onchange('discount_options')
    def change_discount_option(self):
        self.discount_value=0
        self.discount_type_id=False
        self.discount_value=0
        self.reset_all_discount_lines(0)
    @api.onchange('discount_type_id')
    def change_discount_type(self):
        self.discount_value=0
        self.reset_all_discount_lines(0)
    def reset_all_discount_lines(self,val=0):
        for line in self.order_line:
            line.discount=val

        pass
