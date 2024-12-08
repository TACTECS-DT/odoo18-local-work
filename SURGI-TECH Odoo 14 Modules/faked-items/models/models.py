# -*- coding: utf-8 -*-
import json
from pprint import pprint
from datetime import datetime, timedelta

from odoo import models, fields, api


# class faked-items(models.Model):
#     _name = 'faked-items.faked-items'
#     _description = 'faked-items.faked-items'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

from odoo.exceptions import ValidationError

class product_template_inheret_2(models.Model):
    _inherit="product.template"
    isfakedproduct = fields.Boolean(string="Is Faked Product",default=False)
    pass

class product_product_inherit_1(models.Model):
    _inherit="product.product"
    faked_product_id=fields.One2many(comodel_name="stock.biking.faked.item",inverse_name="product")

    pass
class stock_biking_inherts(models.Model):
    _inherit="stock.picking"
    fakeditem=fields.One2many(comodel_name="stock.biking.faked.item",inverse_name="stock_bikeid")
    nofakeditems=fields.Integer(string="No. Faked Items")
    # remove this function if error happen
    def setoperationlocationfreeze(self):
        itesmq=0
        for i in self.fakeditem:
            itesmq+=i.quantity
            if not i.solved:
                raise ValidationError("u Need to Solve All Faked Product")
            if itesmq != self.nofakeditems:
                raise ValidationError("Please Add All Faked Items And Solve it Frist")

            return super("stock_biking_inherts").setoperationlocationfreeze()

        pass
    pass


class stock_biking_faked_item(models.Model):
    _name='stock.biking.faked.item'
    name=fields.Char("Lot Name")
    serial = fields.Char("Lot Serial")
    product = fields.Many2one(comodel_name="product.product",string="Product Name")
    expirartion=fields.Char("Expiration Date")
    quantity=fields.Integer("Quantity")
    solved=fields.Boolean(string="Solved")
    stock_bikeid=fields.Many2one(comodel_name="stock.picking")

    @api.model
    def get_scanned_items(self,active_id):
        print("ff")
        olditems={}
        #activeid=self.active_id
        items=self.env["stock.biking.faked.item"].search([('stock_bikeid', '=', int(active_id))])
        tquantity=0
        for i in items:
           productid=None
           if i.product:
               productid=i.product.id
           olditems[i.serial]={'id':i.id,
                               "serial":i.serial,
                               "quantity":i.quantity,
                               'name':i.name,
                               'product':productid,
                               'stock_bikeid':i.stock_bikeid.id,
                               'expirartion':i.expirartion}
           tquantity+=i.quantity
        returnData={"olditems":olditems,'tquantity':tquantity}
        return json.dumps(returnData, ensure_ascii=False)
        pass
    @api.model
    def savescanned_items(self,active_id,newitems,updateitems,allitems,totalquantity):
        print("x")
        stockpick=self.env["stock.picking"].search([('id', '=', int(active_id))])
        if totalquantity != stockpick.nofakeditems :
            raise ValidationError("Number Of Scanned Items Not Equal Faked Items.")
            raise exceptions.UserError('Number Of Scanned Items Not Equal Faked Items')

            #raise UserError("No Of Scanned Items Not Equal Faked Items!")
        for i in updateitems.values():
            item = self.env["stock.biking.faked.item"].search([('id', '=', int(i['id']))])
            item.quantity=i['quantity']
            pass
        if len(newitems):
            for i in newitems.values():
                product=self.env['stock.production.lot'].search([('name', '=', str(i['serial']))])
                if product:
                    i['product']=product[0].product_id.id
                self.env['stock.biking.faked.item'].create(i)
            pass
        pass
        productfake=self.env['product.product'].search([('isfakedproduct', '=',True)])
        if(productfake):
            fakeproduct=productfake[0]
        else:
            fakeproduct=self.env['product.template'].create({"name":"Faked Product","type":"product","isfakedproduct":True})
        x=True
        for i in stockpick.move_line_ids_without_package:
            if i.product_id.id == fakeproduct.id:
                i.product_uom_qty = totalquantity
                x = False
        if x:
            stockpick.move_line_ids_without_package.create(
                {'product_id':fakeproduct.id,'product_uom_qty':totalquantity,'picking_id':stockpick.id,'company_id':stockpick.company_id,"product_uom_id":fakeproduct.product_tmpl_id.uom_id.id,'location_id':stockpick.location_id.id,'location_dest_id':stockpick.location_dest_id.id}
            )
            pass

        # for i in stockpick.move_line_ids:
        #     if i.product_id.id == fakeproduct.id:
        #         i.product_uom_qty=totalquantity
        #         x=False
        # if x:
        #     move_id={
        #         "name":fakeproduct.name,
        #         "company_id":stockpick.company_id.id,
        #         "product_id":fakeproduct.id,
        #         #"product_qty":totalquantity,
        #         "product_uom_qty":totalquantity,
        #         'product_uom':fakeproduct.product_tmpl_id.uom_id.id,
        #         "location_id":stockpick.location_id.id,
        #         "location_dest_id":stockpick.location_dest_id.id,
        #         "picking_id":stockpick.id,
        #         "partner_id":stockpick.partner_id.id
        #     }
        #     moveids=self.env["stock.move"].create(move_id)
        #     if moveids:
        #         productuom=fakeproduct.product_tmpl_id.uom_id.id
        #         stockpick.move_line_ids.create({'product_id':fakeproduct.id,'move_id':moveids.id,'product_uom_qty':totalquantity,'picking_id':stockpick.id,'company_id':stockpick.company_id,"product_uom_id":fakeproduct.product_tmpl_id.uom_id.id,'location_id':stockpick.location_id.id,'location_dest_id':stockpick.location_dest_id.id})
        #     else:
        #         raise ValidationError("move not created")
        # print("x")
    pass
