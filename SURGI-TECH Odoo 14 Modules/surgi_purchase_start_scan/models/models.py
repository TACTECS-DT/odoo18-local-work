# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning
import re
import time
import sys
# class surgi_purchase_start_scan(models.Model):
#     _name = 'surgi_purchase_start_scan.surgi_purchase_start_scan'
#     _description = 'surgi_purchase_start_scan.surgi_purchase_start_scan'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
class surgi_purchase_start_scan(models.Model):

    _inherit='stock.picking'
    lastscanned=fields.Text(string="Scan Lot")
    lastscannedtext=fields.Text("Last Scaned",compute="")
    def lastscanitem(self):
        pass
    #temp_scan_products_ids = fields.One2many('scan.product', 'stock_picking_id', string="Scanned Products")


    @api.onchange('lastscanned')
    def _getscannedlot(self):
        if len(self.env.companies.ids) >1:
            raise Warning("Please choose one company to Scan At !")
        scaneditem=self.lastscanned
        scantype=self.type_of_scaning
        if scaneditem :
            if self.picking_type_id.code=="incoming":
                if(scantype!='third_group'):
                    qty=1
                    expdate=""
                    lotname=""
                    productrefrence=""
                    if scaneditem[0] == '+':
                        cutteditem=scaneditem.split('/')
                        extractedlot1=cutteditem[0]
                        exteractedlot2=extractedlot1[5:-1].lstrip("0")
                        lotname=cutteditem[1][5:-4]
                        year="20"+cutteditem[1][0:2]
                        month='%02d'%int(round((int(cutteditem[1][2:5])/360)*12,0))
                        expdate=str(year)+"-"+str(month)+"-"+"01"
                        productrefrence=cutteditem[0][5:-1].lstrip("0")
                    else:
                        if '$' in scaneditem:
                            cutteditem=scaneditem.split('#')
                            expdate=cutteditem[1][0:7]
                            productrefrence=cutteditem[1].split(expdate)[1]
                            newexpdate = expdate.split("/")
                            expdate = newexpdate[1] + "-" + newexpdate[0] + "-01"
                            if len(cutteditem[0].split("$")[0])>4:
                                lotname = cutteditem[0].split("$")[0].lstrip("0")
                            else:
                                lotname=cutteditem[0].lstrip("0$")

                        elif '/' in scaneditem:
                            cutteditem = scaneditem.split('#')
                            expdate = cutteditem[1][0:7]
                            productrefrence = cutteditem[1].split(expdate)[1]
                            lotname=cutteditem[0].lstrip("0")
                            newexpdate=expdate.split("/")
                            expdate = newexpdate[1] +"-"+newexpdate[0]+"-01"
                    if productrefrence :
                        lotproduct=self.env['product.product'].search([('default_code','=',productrefrence)])
                        if(lotproduct):
                            found = False
                            #if scaneditem in self.scan_products_ids.lot_no:
                            for i in self.scan_products_ids:
                                    if scaneditem==i.lot_no:
                                        i.product_uom_qty+=1
                                        found=True
                            if not found:
                                self.scan_products_ids.create({
                                    'product_id':lotproduct.id,
                                    'product_uom_qty':1,
                                    'lot_no':scaneditem,
                                    'lot_name':lotname,
                                    'expiration_date':expdate,
                                    'stock_picking_id':self.id
                                })
                                self.env['stock.production.lot'].create({
                                    'product_id':lotproduct.id,
                                    'name':scaneditem,
                                    'company_id':self.company_id.id
                                })
                            self.lastscannedtext=scaneditem
                        else:
                            mess = {
                                'title': 'Product Refrence Not Registered',
                                'message': "Product Refrence Not Registered"
                            }
                            return {'warning': mess}

                    else:
                        mess = {
                            'title': 'barcode not recognized',
                            'message': "We Cant Recognize this barcode"
                        }
                        return {'warning': mess}


                    pass
                self.lastscanned=""
        pass


    def action_start_scanning_new(self):
        return {
            'name': 'Start Scan',
            'view_mode': 'form',
            'view_id': self.env.ref('surgi_purchase_start_scan.view_pruchase_start_scan_new',False).id,
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
            'context': {},
        }
        pass
    def addedscanned(self):
        pass
    pass
