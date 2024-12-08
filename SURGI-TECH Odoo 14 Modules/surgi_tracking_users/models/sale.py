from odoo import models, fields, api,_
from datetime import date,datetime,time,timedelta
from dateutil.relativedelta import relativedelta



class surgi_tracking_order_users(models.Model):
    _inherit = "sale.order"
    order_created_on = fields.Char(string="Created On Date", readonly=True, store=True)
    order_created_by = fields.Char(string="Created by", readonly=True, store=True)
    order_confirmed_on = fields.Char(string="Confirmed On Date", readonly=True, store=True)
    order_confirmed_by = fields.Char(string="Confirmed by", readonly=True, store=True)




    deliverdToCustomer = fields.Boolean(string="Delivered To Customer", readonly=True, store=True)
    deliverdToCustomerDate = fields.Char(string="Delivered To Customer On Date", readonly=True, store=True)
    OrderReview = fields.Boolean(string="Order Revision", readonly=True, store=True)
    OrderReviewDate = fields.Char(string="Order Revision Date", readonly=True, store=True)
    price_delivery_attachments = fields.Binary(string='Priced Delivery Permission', store=True,  attachment=True)
    price_delivery_permission = fields.Boolean(string='Is Priced Delivery', readonly=True,compute="checkPriceAttach")

    invoiced_attachments = fields.Binary(string='Invoice', store=True,  attachment=True)
    invoiced_permission = fields.Boolean(string='Is Invoice', readonly=True,compute="checkInvoiceAttach")

    @api.model
    def create(self,vals):

        user = self.env.user

        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
                # self.started_op_date=datetime.now(),
        vals['order_created_on'] = now.strftime("%m/%d/%Y, %H:%M:%S")
        vals['order_created_by'] = user_name
        res = super(surgi_tracking_order_users, self).create(vals)

        return res
    def action_confirm(self):
        res = super(surgi_tracking_order_users, self).action_confirm()
        user = self.env.user
        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
            # self.started_op_date=datetime.now(),
        self.order_confirmed_on = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.order_confirmed_by = user_name
        return res

    def order_deliverd_To_Customer(self):
        user = self.env.user
        # user_name = user.name
        now = datetime.now() + timedelta(hours=2)
        self.deliverdToCustomerDate = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.deliverdToCustomer = True

    def order_revision(self):
        user = self.env.user
        # user_name = user.name
        now = datetime.now() + timedelta(hours=2)
        self.OrderReviewDate = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.OrderReview = True
    def checkPriceAttach(self):
        for obj in self :
            if obj.price_delivery_attachments:
                obj.price_delivery_permission = True
            else:
                obj.price_delivery_permission = False


    def checkInvoiceAttach(self):
        for obj in self :
            if obj.invoiced_attachments:
                obj.invoiced_permission = True
            else:
                obj.invoiced_permission = False