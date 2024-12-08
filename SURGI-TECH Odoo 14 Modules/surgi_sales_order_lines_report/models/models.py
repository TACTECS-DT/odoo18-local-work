# -*- coding: utf-8 -*-


from odoo import models, fields, api



class sales_order_line_report_inhert(models.Model):
    _inherit="sale.order.line"
    _description = 'model.technical.name'
    invoiceStatus=fields.Selection(string="Invoice Status",related='order_id.invoice_status')
    orderDate=fields.Datetime("Order Date",related='order_id.date_order',search="_search_orderDate")
    priceList=fields.Many2one(string="Price List",comodel_name="product.pricelist",related='order_id.pricelist_id',search='_search_pricelist')
    priceInPriceList=fields.Float("Price In Price List",compute="_get_Price_in_pricelist", search='_search_priceinpricelist')
    diffPrice=fields.Float("Diffrence Price",compute="_calc_deff_price",search='_search_diffprice')
    salesPerson=fields.Many2one(string="Sales Person",comodel_name="res.users",related='order_id.user_id', search='_search_salesperson')
    salesTeam=fields.Many2one(comodel_name="crm.team",string="Sales Team",related='order_id.team_id', search='_search_salesteam')
    invoices=fields.Char("Invoices",compute='_get_invoices',search="_search_invoices")
    salesOrderTotal=fields.Monetary("Sales Order Total",related='order_id.amount_total', search='_search_salesoprdertotal')
    invoicedAmount=fields.Float(string="Invoiced Amount",compute="_compute_invoiced_amount", search='_search_invoicedamount')
    totalDiff=fields.Float("Totals Diffrence",compute="_getTotalsDeff", search='_search_totaldiff')
    #areaManager=fields.Many2one(string="Area Manager",comodel_name="res.users",related='order_id.sales_area_manager')	

    def _search_priceinpricelist(self, operator, value):
        return [('priceInPriceList', operator, value)]
    def _search_pricelist(self, operator, value):
        return [('priceList', operator, value)]
    def _search_diffprice(self, operator, value):
        return [('diffPrice', operator, value)] 
    def _search_salesperson(self, operator, value):
        return [('salesPerson', operator, value)] 
    def _search_salesteam(self, operator, value):
        return [('salesTeam', operator, value)]
    def _search_salesoprdertotal(self, operator, value):
        return [('salesOrderTotal', operator, value)]
    def _search_invoicedamount(self, operator, value):
        return [('invoicedAmount', operator, value)] 
    def _search_totaldiff(self, operator, value):
        return [('totalDiff', operator, value)] 
    def _search_orderDate(self, operator, value):
        return [('orderDate', operator, value)]
    def _search_invoices(self, operator, value):
        return [('invoices', operator, value)]                      


    
	
    def _get_invoices(self):
        for rec in self:
            invoice=""
            invoices=self.env['account.move'].search([('invoice_origin','=',rec.order_id.name)])
            for invo in invoices:
                invoice+=invo.name
                if invo==invoices[-1]:
                    invoice+=" , "
            rec.invoices= invoice   

    ### get item Price From Price List
    @api.depends("order_id","order_id.pricelist_id","product_id")
    def _get_Price_in_pricelist(self):
        for rec in self:
            if rec.order_id.pricelist_id:
                item=rec.order_id.pricelist_id.item_ids.search([('product_id','=',rec.product_id.id)])
                if item:
                    rec.priceInPriceList=item[0].fixed_price
                else:
                    rec.priceInPriceList=0.0
            else:
                rec.priceInPriceList=0.0
    @api.depends("price_unit","priceInPriceList")
    def _calc_deff_price(self):
        for rec in self:
            rec.diffPrice=rec.price_unit-rec.priceInPriceList
    @api.depends('salesOrderTotal','invoicedAmount')
    def _getTotalsDeff(self):
        for rec in self:
            rec.totalDiff= rec.salesOrderTotal- rec.invoicedAmount 

    @api.depends("order_id","order_id.name")
    def _compute_invoiced_amount(self):
        for record in self:
            invoice_id = record.env['account.move'].search(['&',('invoice_origin','=', record.order_id.name),'|',('state','=','draft'),('state','=','posted'),('payment_state', 'not in', ['reversed', 'invoicing_legacy'])])
            total = 0
            if invoice_id:
                for invoice in invoice_id:
                    total += invoice.amount_total
                    record.invoicedAmount = total
            else:
                record.invoicedAmount = total
    @api.model
    def recalc_all_computed(self):
        sql="update sale_order_line as s set priceInPriceList=(select fixed_price from product_pricelist_item where product_id=s.product_id and pricelist_id=(select pricelist_id from sale_order where id=s.order_id))"
        # for rec in self:
        #     #if rec.priceInPriceList:
        #         if rec.order_id.pricelist_id:
        #             item=rec.order_id.pricelist_id.item_ids.search([('product_id','=',rec.product_id.id)])
        #             if item:
        #                 rec.priceInPriceList=item[0].fixed_price
        #             else:
        #                 rec.priceInPriceList=0.0
        #         else:
        #             rec.priceInPriceList=0.0
            #    invoice_id = rec.env['account.move'].search(['&',('invoice_origin','=', rec.order_id.name),'|',('state','=','draft'),('state','=','posted'),('payment_state', 'not in', ['reversed', 'invoicing_legacy'])])
            #    total = 0
            #    if invoice_id:
            #        for invoice in invoice_id:
            #            total += invoice.amount_total
            #            rec.invoicedAmount = total
            #    else:
            #        rec.invoicedAmount = total
            #    rec.diffPrice=rec.price_unit-rec.priceInPriceList
            #    rec.totalDiff= rec.salesOrderTotal- rec.invoicedAmount


			           



    
