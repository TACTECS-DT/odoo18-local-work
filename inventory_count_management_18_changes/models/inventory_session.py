from odoo import models , fields , api ,_
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.exceptions import UserError as Warning
from odoo.tools.float_utils import float_compare, float_is_zero
import json
import logging
from odoo.exceptions import UserError, ValidationError


class InventoryCountSession(models.Model):
    _inherit = 'setu.inventory.count.session'
    


    @api.model
    def save_scanned_data(self, scannedData,current_id):
        msg = ""
        print(scannedData,"scannedData")
        current_record= self.browse(current_id)
        if not current_record :
            return "No  record found with id"
        location_id = current_record.location_id.id
        session_line_ids = current_record.session_line_ids
        

        for i in scannedData :
            if i["old_line_id"] != "none"  and isinstance(i["old_line_id"],int):
                current_line = session_line_ids.browse(i["old_line_id"])
                current_line.write({
                                'scanned_qty': i['qty'], 
                                })
            else :
                session_line_ids.create({
                                'session_id':current_record.id , 
                                'product_id': i['product_id'], 
                                'location_id': location_id, 
                                'scanned_qty': i['qty'], 
                                'theoretical_qty': i['theoretical_qty'], 
                                })
                
        msg = "done"
    
        return msg


    @api.model
    def get_lot_scan_data(self, active_id):

     
        if active_id != "":
            rec = self.env['setu.inventory.count.session'].search([('id', '=', active_id)])
            company = rec.inventory_count_id.company_id
            session_line_ids = rec.session_line_ids
            session_line_ids_Data = [{
                "line_id" : i.id,
                "line_product" :{"product_id":i.product_id.id,"product_name":i.product_id.name},
                "line_tracking" : i.tracking,
                "line_lot" : {"lot_id": i.lot_id.id,"lot_name":i.lot_id.name},
                "line_internal_refrence" : i.product_id.default_code if i.product_id.tracking =='none' else False ,
                
                "line_location" : {"location_id":i.location_id.id,"location_name": i.location_id.complete_name},
                "line_quantity" : i.scanned_qty,
                "line_theoretical_qty" : i.theoretical_qty,

            }for i in session_line_ids]
     
            
            all_lots = self.env["stock.lot"].search([])
            
            privet_lots = self.env["stock.lot"].search([("location_id","=",rec.location_id.id)])
            if not privet_lots :
                raise ValidationError("no lots found  in  this location")
            
            privet_quants = self.env['stock.quant'].search([("location_id","=",rec.location_id.id)])
            if not privet_quants :
                raise ValidationError("no quants found  in  this location")
            
            all_products = self.env["product.product"].search([])


            all_products_data = [{
                "product_id" :i.id ,
                "product_name" :i.name ,
                "tracking" :i.tracking ,
                "internal_reference" :i.default_code ,
                } for i in all_products]
            

            privet_products_data = [{
                "product_id" :i.product_id.id ,
                "product_name" :i.product_id.name ,
                "tracking" :i.product_id.tracking ,
                "quantity" :i.inventory_quantity_auto_apply ,
                "internal_reference" :i.product_id.default_code ,
                } for i in privet_quants]
            

            all_lots_data = [{
                "lot_id" :i.id ,
                "lot_name" :i.name ,
                 "product" : {"product_id":i.product_id.id,"product_name":i.product_id.name,"internal_reference":i.product_id.default_code}    
                } for i in all_lots]

            privet_lots_data = [{
                "lot_id" :i.id ,
                "lot_name" :i.name ,
                 "product" : {"product_id":i.product_id.id,"product_name":i.product_id.name,"internal_reference":i.product_id.default_code}    
                } for i in privet_lots]


            all_internal_reference_data = [{
                "internal_reference" :i["internal_reference"] ,
                "product" : {"product_id":i["product_id"],"product_name":i["product_name"]} ,
             
                } for i in all_products_data]




            privet_internal_reference_data = [{
                "internal_reference" :i["internal_reference"] ,
                "product" : {"product_id":i["product_id"],"product_name":i["product_name"]} ,
                } for i in privet_products_data]





            main_location ={
                'location_id':rec.location_id.id,
                'location_name':rec.location_id.complete_name,
            }
            data = {
                
                "all_products_data" : all_products_data ,
                "privet_products_data" : privet_products_data ,


                "all_lots_data" : all_lots_data ,
                "privet_lots_data" : privet_lots_data ,

                "all_internal_reference_data" : all_internal_reference_data ,
                "privet_internal_reference_data" : privet_internal_reference_data ,


                "session_line_ids_Data" : session_line_ids_Data ,
                "main_location" : main_location,
            }

            print('data: ' ,data)
                        
            
    
            return json.dumps(data, ensure_ascii=False)
   
   
   
