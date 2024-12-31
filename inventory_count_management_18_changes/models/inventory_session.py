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
    
    
    
    def action_view_session_history(self):
        return {
            'name': 'History',
            'view_mode': 'list',
            'view_id': self.sudo().env.ref('setu_inventory_count_management_18.inventory_session_details_tree_view').id,
            'res_model': 'inventory.session.details',
            'type': 'ir.actions.act_window',
            'domain': [('session_id', '=', self.id)]
        }
    def create(self, vals_list):
        quants_lines = []
        if 'location_id' in vals_list :
            inventory_count = self.env['setu.stock.inventory.count'].browse(int(vals_list['inventory_count_id']))
            company = inventory_count.company_id.id
            if inventory_count.scanning_mode == 'products' :
                
                quants = self.env["stock.quant"].search([("location_id","=",vals_list["location_id"]),("product_id",'in',inventory_count.allw_product_ids.ids),('company_id','=',company),('product_id.company_id','in',[company,False])])

            if inventory_count.scanning_mode == 'product_categories' :
                quants = self.env["stock.quant"].search([("location_id","=",vals_list["location_id"]),("product_id.categ_id",'in',inventory_count.product_category_ids.ids),('company_id','=',company),('product_id.company_id','in',[company,False])])
 
 
            if  inventory_count.scanning_mode in ['internal_ref','lot_serial_no',False]  :
                quants = self.env["stock.quant"].search([("location_id","=",vals_list["location_id"]),('company_id','=',company),('product_id.company_id','in',[company,False])])
 


            for i in quants :
                quants_lines.append((0, 0, {
                'product_id': i.product_id.id,
                'tracking': i.tracking,
                'location_id': i.location_id.id,
                'lot_id': i.lot_id.id if i.product_id.tracking  =='lot' else False,
                'theoretical_qty': i.inventory_quantity_auto_apply,
                'scanned_qty': 0,
            
            }))
                

            vals_list["session_line_ids"] = quants_lines 

        return super(InventoryCountSession,self).create(vals_list)
        
        

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
                                'lot_id': i['lot_id'], 
                                })
                
        msg = "done"
    
        return msg


    @api.model
    def get_lot_scan_data(self, active_id):

     
        if active_id != "":



            rec = self.env['setu.inventory.count.session'].search([('id', '=', active_id)])
            company = rec.inventory_count_id.company_id.id
            session_line_ids = rec.session_line_ids


            if rec.inventory_count_id.scanning_mode == 'products' :

                
                wanted_products = rec.inventory_count_id.allw_product_ids
                
                
                privet_lots = self.env["stock.lot"].search([("location_id","=",rec.
                location_id.id),("product_id.tracking","=","lot"),('company_id','=',company),("product_id",'in',wanted_products.ids),('product_id.company_id','in',[company,False])])

                all_lots = privet_lots
                
                privet_quants = self.env['stock.quant'].search([("location_id","=",rec.location_id.id),('company_id','=',company),("product_id",'in',wanted_products.ids),('product_id.company_id','in',[company,False])])
                
                all_products = [i.product_id for i in privet_quants]





            if rec.inventory_count_id.scanning_mode == 'product_categories' :

                product_categories = rec.inventory_count_id.product_category_ids

                # all_products = self.env["product.product"].search([("categ_id",'in',product_categories.ids),('company_id','in',[company,False])])
                
                privet_lots = self.env["stock.lot"].search([("location_id","=",rec.location_id.id),("product_id.tracking","=","lot"),('company_id','=',company),('product_id.company_id','in',[company,False]),("product_id.categ_id",'in',product_categories.ids)])

                all_lots = privet_lots

                privet_quants = self.env['stock.quant'].search([("location_id","=",rec.location_id.id),('company_id','=',company),("product_id.categ_id",'in',product_categories.ids),('product_id.company_id','in',[company,False])])


                all_products = [i.product_id for i in privet_quants]

            if rec.inventory_count_id.scanning_mode in ['internal_ref','lot_serial_no',False] :


                all_products = self.env["product.product"].search([('company_id','in',[company,False])])
                
                all_lots = self.env["stock.lot"].search([("product_id.tracking","=","lot"),('company_id','=',company),('product_id.company_id','in',[company,False])])

                privet_lots = self.env["stock.lot"].search([("location_id","=",rec.location_id.id),("product_id.tracking","=","lot"),('company_id','=',company),('product_id.company_id','in',[company,False])])

                privet_quants = self.env['stock.quant'].search([("location_id","=",rec.location_id.id),('company_id','=',company),('product_id.company_id','in',[company,False])])



            if not privet_lots :
                    raise ValidationError("no lots found  in  this location")
                

            if not privet_quants :
                    raise ValidationError("no quants found  in  this location")
                


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
                
            privet_products_ids = [i.product_id.id for i in privet_quants]
                

            all_lots_data = [{
                    "lot_id" :i.id ,
                    "lot_name" :i.name ,
                    "product" : {"product_id":i.product_id.id,"product_name":i.product_id.name ,"internal_reference" :i.product_id.default_code }    
                    } for i in all_lots]

            privet_lots_data = [{
                    "lot_id" :i.id ,
                    "lot_name" :i.name ,
                    "product" : {"product_id":i.product_id.id,"product_name":i.product_id.name ,"internal_reference" :i.product_id.default_code}    
                    } for i in privet_lots]

            privet_lots_ids = [i.id  for i in privet_lots]


            all_internal_reference_data = [{
                    "internal_reference" :i["internal_reference"] ,
                    "product" : {"product_id":i["product_id"],"product_name":i["product_name"]} ,
                
                    } for i in all_products_data if  i["tracking"] =='none']




            privet_internal_reference_data = [{
                    "internal_reference" :i["internal_reference"] ,
                    "product" : {"product_id":i["product_id"],"product_name":i["product_name"]} ,
                    } for i in privet_products_data if  i["tracking"] =='none']


            session_line_ids_Data = [{
                    "line_id" : i.id,
                    "is_all_code" : '0' if i.product_id.id in privet_products_ids or i.lot_id.id in  privet_lots_ids else '1',
                    "line_product" :{"product_id":i.product_id.id,"product_name":i.product_id.name},
                    "line_tracking" : i.tracking,
                    "line_lot" : {"lot_id": i.lot_id.id,"lot_name":i.lot_id.name},
                    "line_internal_refrence" : i.product_id.default_code if i.product_id.tracking =='none' else False ,
                    
                    "line_location" : {"location_id":i.location_id.id,"location_name": i.location_id.complete_name},
                    "line_quantity" : i.scanned_qty,
                    "line_theoretical_qty" : i.theoretical_qty,

                }for i in session_line_ids]
        


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

            print('#####')
            print('#####')
            print('#####')
            print('#####')
            print('data: ' ,data)
            print('#####')
            print('#####')
            print('#####')
            print('#####')
                            
                
        
            return json.dumps(data, ensure_ascii=False)
    
    
    
   
    # def refresh_theoretical_qty(self):
    #    for rec in self :
    #        for line in rec.session_line_ids : 
    #             domain =[("location_id","=",rec.location_id),("product_id","=",line.product_id)]
    #             if line.product_id.tracking == 'none' :
                    
                
                
    #             last_qty = self.env["stock.quant"].search(domain)
    #             line.theoretical_qty = last_qty
           
    #    issu with fitring to rich to each  line related  quant 
       
    
    
class InventoryCountSessionLine(models.Model):
    _inherit = 'setu.inventory.count.session.line'


    location_id = fields.Many2one(
        "stock.location",
        string="Location",
        required=False,
        readonly=True,
        store=True
    )




    product_id = fields.Many2one(
    comodel_name="product.product",
        string="Product",
    )

    domain_product_id = fields.Char(string="Product Domain", compute="_compute_product_domain")



    @api.depends("session_id")
    def _compute_product_domain(self):
        for line in self:
            if line.session_id and line.session_id.inventory_count_id:
                count = line.session_id.inventory_count_id
                company = line.session_id.inventory_count_id.company_id
                location= line.session_id.inventory_count_id.location_id

                if count.scanning_mode  in ["products" , "product_categories"] :


                    if count.scanning_mode == "products":
                        wanted_products= count.allw_product_ids.ids 

            
                    elif count.scanning_mode == "product_categories":
                    
                        wanted_products = self.env["product.product"].search([("categ_id", "in", count.product_category_ids.ids),('company_id','in',[company.id,False])]).ids
                        
                    products_that_in_lots = self.env["stock.lot"].search([("location_id","=",location.id),('company_id','=',company.id),("product_id",'in',wanted_products),('product_id.company_id','in',[company.id,False])])

            
                    
                    privet_quants = self.env['stock.quant'].search([("location_id","=",location.id),('company_id','=',company.id),("product_id",'in',wanted_products),('product_id.company_id','in',[company.id,False])])
                        
                    allwed_products = set([i.product_id.id for i in privet_quants] + [i.product_id.id for i in products_that_in_lots])
                    
                    disallwed_products = set([i for i in wanted_products if i not in allwed_products])

                    allwed_products = list(allwed_products)
                    disallwed_products = list(disallwed_products)

                    line.domain_product_id = str([("id", "in", allwed_products),('company_id','in',[company.id,False])])

                
                if count.scanning_mode not in ["products" , "product_categories"] :
                    line.domain_product_id = "[]"

            else:
                line.domain_product_id = "[]"






    @api.model
    def create(self, vals):
        # Set location_id automatically if not provided
        if not vals.get("location_id") and vals.get("session_id"):
            session = self.env["setu.inventory.count.session"].browse(vals["session_id"])
            vals["location_id"] = session.location_id.id
        return super(InventoryCountSessionLine, self).create(vals)
   

    def write(self, vals):
        if not self.session_id : 
            return super(InventoryCountSessionLine, self).write(vals)
        session = self.env["setu.inventory.count.session"].browse(self.session_id.id)
        vals["location_id"] = session.location_id.id
        return super(InventoryCountSessionLine, self).write(vals)


 