from datetime import date
from datetime import datetime
from odoo import api, _
from odoo import exceptions
from odoo import fields
from odoo import models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import pytz
# from odoo.tools import timedelta
from datetime import timedelta
# from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError,UserError
import logging

class sale_order_pricelist_inhert(models.Model):
    _inherit = ['sale.order']
    _description = 'model.technical.name'
    def checkPriceLists(self):
        if self.so_type=='tender':
            pricelist=self.env['product.pricelist'].search([('op_type','=','tender')])
            if pricelist:
                return
            else:
                raise UserError("No price List With type Waiting List")
        if self.payment_term_id.name=='Cash':
                pricelists=self.surgeon_id.hospitalpricelists
               # term = self.env['account.payment.term'].search([('name', 'like', 'Cash')])

        else:
                #term = self.env['account.payment.term'].search([('name', 'like', 'Credit')])

                pricelists=self.hospital_id.hospitalpricelists
        for rec in self:
            if rec.so_type != 'operation':
               pricelist=rec.pricelist_id
            return True
            optype=rec.operation_id.op_type
            pricelist=None
            for quant in rec.order_line:
                for price in pricelists:
                    if price.op_type==optype and price.product_line==quant.product_id.product_line_id:
                        pricelist=price
                        logging.warning("\n price list check\ n"+price.name)
                #pricelist=self.env['product.pricelist'].search([('op_type','=',optype),('product_line','=',quant.product_id.product_line_id)])
                if pricelist:
                   print("exist")                
                else:
                    raise UserError('No PriceList For Product '+quant.product_id.name)
    def setPriceList(self,quant):
        for rec in self:
            optype=rec.operation_id.op_type
            pricelist=None
            price=None
            if self.so_type=='tender':
                pricelist=self.env['product.pricelist'].search([('op_type','=','tender')])
                if pricelist:
                    for item in pricelist.item_ids:
                        if quant.product_id.id == item.product_id.id:
                            price = item.fixed_price
                    quant.write({'pricelist':pricelist.id,'price_unit':price})
                    return        
                        
                else:
                    raise UserError("No price List With type Waiting List")
            if self.so_type!='operation':
                pricelists=[self.pricelist_id]
            elif self.payment_term_id.name=='Cash':
                pricelists=self.surgeon_id.hospitalpricelists
            else:
                 pricelists=self.hospital_id.hospitalpricelists   
            #pricelist=self.env['product.pricelist'].search([('op_type','=',optype),('product_line','=',quant.product_id.product_line_id)])
            for pricelistx in pricelists:
                if pricelistx.op_type==optype and pricelistx.product_line==quant.product_id.product_line_id:
                    pricelist=pricelistx
                    for item in pricelist.item_ids:
                        if quant.product_id.id == item.product_id.id:
                            price = item.fixed_price
                    
            if pricelist :#and price:
                quant.write({'pricelist':pricelist.id,'price_unit':price})
                logging.warning("\n getPriceList\ n"+pricelist.name)
                   #return pricelist
            else:
                    raise UserError('Product not found in any pricelists'+quant.product_id.name)


        pass
    
    def update_price_list_hospital(self):
        for rec in self:
            rec.checkPriceLists()
            for quant in rec.order_line:
                rec.setPriceList(quant)

        pass

    
