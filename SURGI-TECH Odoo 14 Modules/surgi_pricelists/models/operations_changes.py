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

class operation_operation_inhert(models.Model):
    _inherit = ['operation.operation']
    #pricelists
    def checkPriceLists(self,quants):
        if self.op_type=='tender':
            pricelist=self.env['product.pricelist'].search([('op_type','=','tender')])
            if pricelist:
                return
            else:
                raise UserError("No price List With type Waiting List")
        if self.payment_methods=='cash':
                pricelists=self.surgeon_id.hospitalpricelists
               # term = self.env['account.payment.term'].search([('name', 'like', 'Cash')])
        elif self.payment_methods=='cashpatient':
                #pricelists=self.patient_id.hospitalpricelists
                pricelists=self.env['product.pricelist'].search([('paymenttype','=','cashpatient')])
        elif self.payment_methods=='hospitalcash':
                pricelists=self.env['product.pricelist'].search([('paymenttype','=','hospitalcash')])
        else:
                #term = self.env['account.payment.term'].search([('name', 'like', 'Credit')])

                pricelists=self.hospital_id.hospitalpricelists
        for rec in self:
            optype=rec.op_type
            pricelist=None
            for quant in quants:
                for price in pricelists:
                    if price.op_type==optype and price.product_line==quant.product_id.product_line_id:
                        pricelist=price
                        logging.warning("\n price list check\ n"+price.name)
                #pricelist=self.env['product.pricelist'].search([('op_type','=',optype),('product_line','=',quant.product_id.product_line_id)])
                if pricelist:
                   print("exist")                
                else:
                    raise UserError('No PriceList For Product'+quant.product_id.name)

    def getPriceList(self,quant):
        for rec in self:
            if rec.op_type=='tender':
                pricelist=self.env['product.pricelist'].search([('op_type','=','tender')])
                if pricelist:
                    return pricelist
                else:
                    raise UserError("No price List With type Waiting List")
            optype=rec.op_type
            pricelist=None
            if self.payment_methods=='cash':
                pricelists=self.surgeon_id.hospitalpricelists
            elif self.payment_methods=='cashpatient':
                #pricelists=self.patient_id.hospitalpricelists
                pricelists=self.env['product.pricelist'].search([('paymenttype','=','cashpatient')])
            elif self.payment_methods=='hospitalcash':
                pricelists=self.env['product.pricelist'].search([('paymenttype','=','hospitalcash')])        
            else:
                 pricelists=self.hospital_id.hospitalpricelists   
            #pricelist=self.env['product.pricelist'].search([('op_type','=',optype),('product_line','=',quant.product_id.product_line_id)])
            for price in pricelists:
                if price.op_type==optype and price.product_line==quant.product_id.product_line_id:
                    pricelist=price
            if pricelist:
                   logging.warning("\n getPriceList\ n"+price.name)
                   return pricelist
            else:
                    raise UserWarning('Product not found in any pricelists'+quant.product_id.name)


        pass
    def create_sales_order(self):
        super(operation_operation_inhert,self).create_sales_order()
        quants = self.env['hanged.stock.quant'].search([('operation_location_id', '=', self.location_id.id)])
        self.checkPriceLists(quants)
        if len(quants) > 0:
            hanged_location_id = quants[0].location_id.id
            pricelist=""
            if self.payment_methods=='cash':
                term = self.env['account.payment.term'].search([('name', 'like', 'Cash')])
                pricelist=self.surgeon_id.property_product_pricelist
            elif self.payment_methods=='cashpatient':
                pricelists=self.env['product.pricelist'].search([('paymenttype','=','cashpatient')])
                #pricelists=self.patient_id.hospitalpricelists
                term = self.env['account.payment.term'].search([('name', 'like', 'Cash')])
            elif self.payment_methods=='hospitalcash':
                pricelists=self.env['product.pricelist'].search([('paymenttype','=','hospitalcash')])
                term = self.env['account.payment.term'].search([('name', 'like', 'Cash')])    
            else:
                term = self.env['account.payment.term'].search([('name', 'like', 'Credit')])

                pricelist=self.hospital_id.property_product_pricelist
            # Main fields
            values = {
                'name': self.sequence,
                'pricelist_id': pricelist.id,
                'partner_id': self.hospital_id.id,
                # field updated by SURGI-TECH --- START--
                'hospital_id': self.hospital_id.id,
                'surgeon_id': self.surgeon_id.id,
                'patient_name': self.patient_name,
                'customer_printed_name': self.hospital_id.name,
                'user_id': self.responsible.id,
                'team_id': self.op_sales_area.id,
                'sales_area_manager': self.op_area_manager,
                # field updated by SURGI-TECH --- END--
                'warehouse_id': self.warehouse_id.id,
                'location_id': hanged_location_id,
                'location_dest_id': self.hospital_id.property_stock_customer.id,
                'delivery_type': self.operation_delivery_type,
                'payment_term_id': term.id,
                'so_type': 'operation',
                'operation_id': self.id,
            }
            order_lines = []
            for quant in quants:
                price = quant.product_id.lst_price
                pricelist=self.getPriceList(quant)
                for item in pricelist.item_ids:
                    if quant.product_id.id == item.product_id.id:
                        price = item.fixed_price
                        pricelist=self.getPriceList(quant)
                        #raise Warning(pricelist.name)
                        logging.warning("\n Entered order lines \n")
                        logging.warning("\n getPriceList orderlines\n"+pricelist.name)
                        logging.warning("\n getPriceList pricelist \n"+str(pricelist.item_ids))
                        for item in pricelist.item_ids:
                            
                            
                            if item:
                                logging.warning("\n getPriceList quant name>>>>>>>>>>>>>>>\n"+quant.product_id.name)
                                logging.warning("\n getPriceList quant id>>>>>>>>>>>>\n"+str(quant.product_id.id))
                                logging.warning("\n getPriceList item price>>>>>>>>>>>>>\n"+str(item.fixed_price))
                                logging.warning("\n getPriceList item id >>>>>>>>>>>>>>>>\n"+str(item.product_id.id))
                                logging.warning("\n getPriceList item name>>>>>>>>>>>>>>>>>>\n"+item.product_id.name)
                            
                            
                                logging.warning("\n getPriceList orderlines>>>>>>>>>>>>>>>>\n"+str(quant.quantity))
                                if quant.product_id.id == item.product_id.id:# and quant.quantity > 0:
                                    price = item.fixed_price
                                    logging.warning("\n getPriceList orderlines###########\n"+str(price))
                                    #raise Warning(str(price))
                if quant.quantity > 0:
                    line = [0, False, {
                        'qty_delivered': 0,
                        'product_id': quant.product_id.id,
                        'product_uom': quant.product_id.uom_id.id,
                        'sequence': quant.product_id.sequence,
                        'price_unit': price,
                        'product_uom_qty': quant.quantity,
                        'state': 'draft',
                        'pricelist':pricelist.id,
                        # 'qty_delivered_updateable': True,
                        'invoice_status': 'no',
                        'name': quant.product_id.name, }]
                    order_lines.append(line)

            values['order_line'] = order_lines
            print("vals: " + str(values))
            sale_order = self.env['sale.order'].create(values)
            self.sale_order_id=sale_order.id
            self.so_created = True
            sale_order.action_confirm()
            sale_order.changed_line_ids()
            pickings = sale_order.mapped('picking_ids')
            scan_product_ids_lst = []
            for quant in quants:
                if quant.product_id.tracking == 'lot' or quant.product_id.tracking == 'serial':
                    if quant.quantity > 0:
                        line = [0, 0,
                                {'product_id': quant.product_id.id,
                                 'product_uom_qty': quant.quantity,
                                 'lot_no': quant.lot_id.name,
                                 }]
                        scan_product_ids_lst.append(line)
            for picking in pickings:
                picking.scan_products_ids = scan_product_ids_lst
                picking.synchronize_scan()
                picking.compute_analytic_account()
                picking.button_validate()
                picking.change_state_delivery()

            print("Sale_order: " + str(sale_order))
        else:
            raise Warning('No Quants Available in Hanged Location!')    


    # Create sale order regarding to operation data not hanged
    def create_delivery_sales_order(self):
        #res=super(operation_operation_inhert,self).create_delivery_sales_order()
        #raise Warning('Entered Function')
        if self.check_need_x_rays():
            raise exceptions.ValidationError('Please fill Pre Operative XRay & post Operative XRay')
        elif self.check_need_x_rays_operation_type():
            raise exceptions.ValidationError('Please fill Pre Operative XRay & post Operative XRay')

        quants = self.env['stock.quant'].search([('location_id', '=', self.location_id.id)])
        logging.warning("\n getPriceList item price>>>>>>>>>>>>>\n"+str(quants))
        self.checkPriceLists(quants)
        if len(quants) > 0:
            operation_location_id = quants[0].location_id.id
            pricelist=""
            if self.payment_methods=='cash':
                pricelist=self.surgeon_id.property_product_pricelist
                term = self.env['account.payment.term'].search([('name', 'like', 'Cash')])

            elif self.payment_methods=='cashpatient':
                pricelists=self.env['product.pricelist'].search([('paymenttype','=','cashpatient')])
                #pricelists=self.patient_id.hospitalpricelists
                term = self.env['account.payment.term'].search([('name', 'like', 'Cash')])
            elif self.payment_methods=='hospitalcash':
                pricelists=self.env['product.pricelist'].search([('paymenttype','=','hospitalcash')])
                term = self.env['account.payment.term'].search([('name', 'like', 'Cash')])    
            else:
                term = self.env['account.payment.term'].search([('name', 'like', 'Credit')])

                pricelist=self.hospital_id.property_product_pricelist
            # Main fields

            values = {
                'name': self.sequence,
               # 'pricelist_id': pricelist.id,
                'partner_id': self.hospital_id.id,
                # field updated by SURGI-TECH --- START--
                'hospital_id': self.hospital_id.id,
                'surgeon_id': self.surgeon_id.id,
                'patient_name': self.patient_name,
                'customer_printed_name': self.hospital_id.name,
                'user_id': self.responsible.id,
                'team_id': self.op_sales_area.id,
                'sales_area_manager': self.op_area_manager,
                # field updated by SURGI-TECH --- END--
                'warehouse_id': self.warehouse_id.id,
                'location_id': operation_location_id,
                'location_dest_id': self.hospital_id.property_stock_customer.id,
                'so_type': 'operation',
                'delivery_type': self.operation_delivery_type,
                'operation_id': self.id,
                'payment_term_id': term.id,

            }
            order_lines = []
            for quant in quants:
                price = quant.product_id.lst_price
                pricelist=self.getPriceList(quant)
                #raise Warning(pricelist.name)
                logging.warning("\n Entered order lines \n")
                logging.warning("\n getPriceList orderlines\n"+pricelist.name)
                logging.warning("\n getPriceList pricelist \n"+str(pricelist.item_ids))
                for item in pricelist.item_ids:
                    
                    
                    if item:
                        logging.warning("\n getPriceList quant name>>>>>>>>>>>>>>>\n"+quant.product_id.name)
                        logging.warning("\n getPriceList quant id>>>>>>>>>>>>\n"+str(quant.product_id.id))
                        logging.warning("\n getPriceList item price>>>>>>>>>>>>>\n"+str(item.fixed_price))
                        logging.warning("\n getPriceList item id >>>>>>>>>>>>>>>>\n"+str(item.product_id.id))
                        logging.warning("\n getPriceList item name>>>>>>>>>>>>>>>>>>\n"+item.product_id.name)
                    
                    
                        logging.warning("\n getPriceList orderlines>>>>>>>>>>>>>>>>\n"+str(quant.quantity))
                        if quant.product_id.id == item.product_id.id:# and quant.quantity > 0:
                            price = item.fixed_price
                            logging.warning("\n getPriceList orderlines###########\n"+str(price))
                            #raise Warning(str(price))
                if quant.quantity > 0:
                    line = [0, False, {
                        'qty_delivered': 0,
                        'product_id': quant.product_id.id,
                        'product_uom': quant.product_id.uom_id.id,
                        'sequence': quant.product_id.sequence,
                        'price_unit': price,
                        'product_uom_qty': quant.quantity,
                        'state': 'draft',
                        'pricelist':pricelist.id,
                        # 'qty_delivered_updateable': True,
                        'invoice_status': 'no',
                        'name': quant.product_id.name, }]
                    order_lines.append(line)
                    logging.warning("\n  KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK \n"+str(price))    

            values['order_line'] = order_lines
            print("vals: " + str(values))
            sale_order = self.env['sale.order'].create(values)
            self.sale_order_id = sale_order.id
            self.so_created = True
            sale_order.action_confirm()
            sale_order.changed_line_ids()

            pickings = sale_order.mapped('picking_ids')
            scan_product_ids_lst = []
            for quant in quants:
                if quant.product_id.tracking == 'lot' or quant.product_id.tracking == 'serial':
                    if quant.quantity > 0:
                        line = [0, 0,
                                {'product_id': quant.product_id.id,
                                 'product_uom_qty': quant.quantity,
                                 'lot_no': quant.lot_id.name,
                                 }]
                        scan_product_ids_lst.append(line)
            for picking in pickings:
                picking.scan_products_ids = scan_product_ids_lst
                picking.synchronize_scan()
                picking.compute_analytic_account()
                picking.button_validate()
                picking.change_state_delivery()
            print(sale_order)
            print("Sale_order: " + str(sale_order))
            self.write({'state': 'so_created', })
        else:
            raise exceptions.ValidationError('No Quants Available in  Location!')


    # def create_delivery_sales_order_tender(self):
    #     super(operation_operation_inhert,self).create_delivery_sales_order_tender()
    #     quants = self.env['stock.quant'].search([('location_id', '=', self.location_id.id)])
    #     self.checkPriceLists(quants)
    #     if len(quants) > 0:
    #         pricelist=""
    #         if self.payment_methods=='cash':
    #             pricelist=self.surgeon_id.property_product_pricelist
    #         else:
    #             pricelist=self.hospital_id.property_product_pricelist
    #         operation_location_id = quants[0].location_id.id
    #         # Main fields
    #         values = {
    #             'name': self.sequence,
    #             'pricelist_id': pricelist.id,
    #             'partner_id': self.hospital_id.id,
    #             # field updated by SURGI-TECH --- START--
    #             'hospital_id': self.hospital_id.id,
    #             'surgeon_id': self.surgeon_id.id,
    #             'patient_name': self.patient_name,
    #             'customer_printed_name': self.hospital_id.name,
    #             'user_id': self.env.user.id,
    #             'team_id': 277,
    #             'sales_area_manager': self.op_area_manager,
    #             # field updated by SURGI-TECH --- END--
    #             'warehouse_id': self.warehouse_id.id,
    #             'location_id': operation_location_id,
    #             'location_dest_id': self.hospital_id.property_stock_customer.id,
    #             'so_type': 'operation',
    #             'delivery_type': self.operation_delivery_type,
    #             'operation_id': self.id,
    #         }
    #         order_lines = []
    #         for quant in quants:
    #             price = quant.product_id.lst_price
    #             pricelist=self.getPriceList(quant)
    #             for item in pricelist.item_ids:
    #                 if quant.product_id.id == item.product_id.id:
    #                     price = item.fixed_price
    #             line = [0, False, {
    #                 'qty_delivered': 0,
    #                 'product_id': quant.product_id.id,
    #                 'product_uom': quant.product_id.uom_id.id,
    #                 'sequence': quant.product_id.sequence,
    #                 'price_unit': price,
    #                 'product_uom_qty': quant.quantity,
    #                 'state': 'draft',
    #                 'pricelist':pricelist.id,
    #                 # 'qty_delivered_updateable': True,
    #                 'invoice_status': 'no',
    #                 'name': quant.product_id.name, }]
    #             order_lines.append(line)

    #         values['order_line'] = order_lines
    #         print("vals: " + str(values))
    #         sale_order = self.env['sale.order'].create(values)
    #         self.so_created = True
    #         sale_order.action_confirm()
    #         sale_order.changed_line_ids()

    #         pickings = sale_order.mapped('picking_ids')
    #         scan_product_ids_lst = []
    #         for quant in quants:
    #             if quant.product_id.tracking == 'lot' or quant.product_id.tracking == 'serial':
    #                 line = [0, 0,
    #                         {'product_id': quant.product_id.id,
    #                          'product_uom_qty': quant.quantity,
    #                          'lot_no': quant.lot_id.name,
    #                          }]
    #                 scan_product_ids_lst.append(line)
    #         for picking in pickings:
    #             picking.scan_products_ids = scan_product_ids_lst
    #             picking.button_validate()
    #         print(sale_order)
    #         print("Sale_order: " + str(sale_order))
    #     else:
    #         raise exceptions.ValidationError('No Quants Available in  Location!')


