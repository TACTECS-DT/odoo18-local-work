# -*- coding: utf-8 -*-
import json
from pprint import pprint
from datetime import datetime, timedelta

from odoo import models, fields, api
from odoo.exceptions import UserError


# class surgi-dummy-items(models.Model):
#     _name = 'surgi-dummy-items.surgi-dummy-items'
#     _description = 'surgi-dummy-items.surgi-dummy-items'

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
from dateutil.parser import parse



class product_template_inheret_2(models.Model):
    _inherit="product.template"
    isfakedproduct = fields.Boolean(string="Is Dummy Product",default=False)
    pass

    obsolete = fields.Boolean(string="Obsolete",default=False)
class product_product_inherit_1(models.Model):
    _inherit="product.product"
    faked_product_id=fields.One2many(comodel_name="stock.biking.faked.item",inverse_name="product")

    pass
class stock_biking_inherts_dummy(models.Model):
    #_name = "stock.biking.inherts.dummy"
    _inherit = "stock.picking"

    fakeditem=fields.One2many(comodel_name="stock.biking.faked.item",inverse_name="stock_bikeid")
    nofakeditems=fields.Integer(string="No. Dummy Items")


    @api.model
    def _getnumberoffakedline(self):

        x=0
        for i in self.fakeditem:
            x+=1
            self.nofakedlines= True
            return
        self.nofakedlines= False

    nofakedlines = fields.Boolean(compute="_getnumberoffakedline")
    # remove this function if error happen
    #@api.model

    def check_location_for_dummies(self):
        # pickings=self.env['stock.picking'].search([('operation_id','=',self.operation_id.id)])
        # pickingerrmsg=""
        # for picking in pickings:
        #     if  picking.nofakeditems > 0:
        #         pickingerrmsg+=" === "+str(picking.name)
        #         #raise ValidationError("u Can't Freez Location You have dummy product in "+str(picking.name))
        # if pickingerrmsg :
        #     raise ValidationError("u Can't Freez Location You have dummy product in " + pickingerrmsg)
        operations = self.env['stock.quant'].search([('location_id', '=', self.location_id.id), ('quantity', '>', 0)])
        for op in operations:
            if op.product_id.isfakedproduct:
                raise UserError("this Location has Dummy Item In Operation ")

        pass
    def setoperationlocationfreeze(self):

        self.check_location_for_dummies()
        res = super(stock_biking_inherts_dummy, self).setoperationlocationfreeze()
        return res

        pass

    def synchronize_scan(self):

        res=super(stock_biking_inherts_dummy, self).synchronize_scan()

        ##res=super("stock_biking_inherts_dummy",self).synchronize_scan()
        nofak = 0
        for i in self.fakeditem:
            nofak += i.quantity
            pass
        if nofak >0:

             productfake = self.env['product.product'].search([('isfakedproduct', '=', True)])
             fakeproduct=productfake[0]

             mov_id_var = {
                 'name': fakeproduct.name,
                 'location_id': self.location_id.id,
                 'picking_id': self.id,
                 'location_dest_id': self.location_dest_id.id,
                 'product_id': fakeproduct.id,
                 'product_uom': fakeproduct.uom_id.id,
                 'product_uom_qty': 0,
                 # 'ordered_qty': 0,
             }
             move_id = self.env['stock.move'].create(mov_id_var)

             stock_move_var = {
                 'picking_id': self.id,
                 'move_id': move_id.id,
                 'qty_done': nofak,
                 # 'lot_id': lot_id.id,
                 # 'lot_name': lot_id.name,
                 'location_dest_id': self.location_dest_id.id,
                 'location_id': self.location_id.id,
                 'product_id': fakeproduct.id,
                 'product_uom_id': move_id.product_uom.id,
                 'product_uom_qty': 0,
             }
             self.env['stock.move.line'].create(stock_move_var)
             if self.state == 'draft':
                 self.action_confirm()
        moves = self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
        if not moves:
            raise UserError('Nothing to check the availability for.')
        for move in moves:
            if move.product_tmpl_id.tracking == 'none':
                #move.quantity_done = move.product_uom_qty
                v = move.quantity_done
                z = move.product_uom_qty
            if move.state == 'assigned':
                move.state = 'confirmed'
                print("s")
            move.state = 'assigned'

        return res
        pass# finished sync



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
    company_id=fields.Many2one(string="Company",comodel_name="res.company")
    lotexist=fields.Boolean("Lot Exist")

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
    def getfakeditemdata(self,scaneditem,scantype):
        data={'name':"",'serial':"",'product':"",'expiration':"","lotexist":False}
        if scaneditem:
            if (scantype != 'third_group'):
                qty = 1
                expdate = ""
                lotname = ""
                productrefrence = ""
                if scaneditem[0] == '+':
                    cutteditem = scaneditem.split('/')
                    extractedlot1 = cutteditem[0]
                    exteractedlot2 = extractedlot1[5:-1].lstrip("0")
                    lotname = cutteditem[1][5:-4]
                    year = "20" + cutteditem[1][0:2]
                    month = '%02d' % int(round((int(cutteditem[1][2:5]) / 360) * 12, 0))
                    expdate = str(year) + "-" + str(month) + "-" + "01"
                    productrefrence = cutteditem[0][5:-1].lstrip("0")
                else:
                    if '$' in scaneditem:
                        cutteditem = scaneditem.split('#')
                        expdate = cutteditem[1][0:7]
                        productrefrence = cutteditem[1].split(expdate)[1]
                        newexpdate = expdate.split("/")
                        expdate = newexpdate[1] + "-" + newexpdate[0] + "-01"
                        if len(cutteditem[0].split("$")[0]) > 4:
                            lotname = cutteditem[0].split("$")[0].lstrip("0")
                        else:
                            lotname = cutteditem[0].lstrip("0$")

                    elif '/' in scaneditem:
                        cutteditem = scaneditem.split('#')
                        expdate = cutteditem[1][0:7]
                        productrefrence = cutteditem[1].split(expdate)[1]
                        lotname = cutteditem[0].lstrip("0")
                        newexpdate = expdate.split("/")
                        expdate = newexpdate[1] + "-" + newexpdate[0] + "-01"
                lotproduct=None

                if productrefrence:
                    lotproduct = self.env['product.product'].search([('default_code', '=', productrefrence)])
                data['name']=lotname
                data['serial']=scaneditem
                if lotproduct:
                    data['product']=lotproduct.id
                    data['lotexist'] = True
                data['expiration']=expdate

            pass
        return data
        pass
    @api.model
    def savescanned_items(self,active_id,newitems,updateitems,allitems,totalquantity):
        print("x")
        stockpick=self.env["stock.picking"].search([('id', '=', int(active_id))])
        if totalquantity != stockpick.nofakeditems :
            raise ValidationError("Number Of Scanned Items Not Equal Faked Items.")
            raise UserError('Number Of Scanned Items Not Equal Faked Items')

            #raise UserError("No Of Scanned Items Not Equal Faked Items!")
        for i in updateitems.values():
            item = self.env["stock.biking.faked.item"].search([('id', '=', int(i['id']))])
            item.quantity=i['quantity']
            pass
        if len(newitems):
            for i in newitems.values():
                data={}
                product=self.env['stock.production.lot'].search([('name', '=', str(i['serial']))])
                data['lotexist'] =False
                if product:
                    data['lotexist'] =True
                    i['product']=product[0].product_id.id
                serial=i['serial']
                if not i['expirartion']:
                    data={}
                    cdata=self.getfakeditemdata(serial,"oo")
                    data['name']=cdata['name']
                    data['serial'] = cdata['serial']
                    data['product'] = cdata['product']
                    data['expirartion'] = cdata['expiration']
                    data['quantity'] = i['quantity']
                    data['stock_bikeid']=i['stock_bikeid']
                    data['company_id']=stockpick.company_id.id
                    data['lotexist'] = cdata['lotexist']
                else:
                    data=i
                    data['company_id'] = stockpick.company_id.id

                    print("c")
                self.env['stock.biking.faked.item'].create(data)
            pass
        pass
        productfake=self.env['product.product'].search([('isfakedproduct', '=',True)])
        if(productfake):
            fakeproduct=productfake[0]
        else:
            fakeproduct=self.env['product.template'].create({"name":"Dummy Product","type":"product","isfakedproduct":True})
        x=True
        for i in stockpick.move_line_ids_without_package:
            if i.product_id.id == fakeproduct.id:
                i.product_uom_qty = totalquantity
                x = False
        if x:
            mov_id_var = {
                'name': fakeproduct.name,
                'location_id': stockpick.location_id.id,
                'picking_id': stockpick.id,
                'location_dest_id': stockpick.location_dest_id.id,
                'product_id': fakeproduct.id,
                'product_uom': fakeproduct.uom_id.id,
                'product_uom_qty': 0,
                # 'ordered_qty': 0,
            }
            move_id = self.env['stock.move'].create(mov_id_var)
            stock_move_var = {
                'picking_id': stockpick.id,
                'move_id': move_id.id,
                'qty_done': totalquantity,
                #'lot_id': lot_id.id,
                #'lot_name': lot_id.name,
                'location_dest_id': stockpick.location_dest_id.id,
                'location_id': stockpick.location_id.id,
                'product_id': fakeproduct.id,
                'product_uom_id': move_id.product_uom.id,
                'product_uom_qty': 0,
            }
            self.env['stock.move.line'].create(stock_move_var)
            # stockpick.move_line_ids_without_package.create(
            #     {'product_id':fakeproduct.id,'qty_done':totalquantity,'picking_id':stockpick.id,'company_id':stockpick.company_id,"product_uom_id":fakeproduct.product_tmpl_id.uom_id.id,'location_id':stockpick.location_id.id,'location_dest_id':stockpick.location_dest_id.id}
            # )
            pass


        
    pass

    @api.model
    def solve_items(self):
        for record in self:
            record.solved=True
        pass

    def is_date(self,s=""):
        try:
            s=str(s)
            datetime.strptime(s, '%Y-%m-%d')
            return True
        except ValueError:
            raise UserError("Incorrect data format, should be YYYY-MM-DD")




    @api.model
    def dummyToLot(self):
        print("xx")
        for record in self:
            d=record.expirartion
            self.is_date(d)

            if record.company_id:
                companyid=record.company_id.id
            else:
                companyid=record.stock_bikeid.company_id.id
            data={'product_id':record.product.id,'lot_no':record.serial,'stock_picking_id':record.stock_bikeid.id,'product_uom_qty':record.quantity,'lot_name':record.name,'expiration_date':record.expirartion}
            self.env['scan.product'].create(data)
            data={'name':record.name,'ref':record.product.default_code,'product_id':record.product.id,'company_id':companyid}
            self.env['stock.production.lot'].create(data)
        pass

class Operation_Dummy_inhert(models.Model):
    _inherit="operation.operation"
    def checkDummyItems(self):
        operations = self.env['stock.quant'].search([('location_id', '=', self.location_id.id), ('quantity', '>', 0)])
        for op in operations:
            if op.product_id.isfakedproduct:
                raise UserError("this Location has Dummy Item In Operation ")
        #for line in

        pass
    def create_draft_sales_order(self):
        self.checkDummyItems()
        return super(Operation_Dummy_inhert,self).create_draft_sales_order()
        pass
    def create_sales_order(self):
        self.checkDummyItems()
        return super(Operation_Dummy_inhert, self).create_sales_order()
        pass
    def create_delivery_sales_order(self):
        self.checkDummyItems()
        return super(Operation_Dummy_inhert, self).create_delivery_sales_order()
        pass
    def set_operation_location_freeze_from_operation(self):
        self.checkDummyItems()
        return super(Operation_Dummy_inhert, self).set_operation_location_freeze_from_operation()
