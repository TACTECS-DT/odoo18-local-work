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
from odoo.exceptions import ValidationError


# =============== A.Salama =============
class operation_operation(models.Model):
    _name = 'operation.operation'
    # _inherits = {'calendar.event': "event_id"} # Delegation
    _inherit = ['mail.thread','portal.mixin', 'utm.mixin']

    # ==================== Methods =========================


    patient_national_id_image = fields.Binary('Patient National ID image')
    have_emptybox=fields.Boolean("Have Empty Box")    
    nothaveempty=fields.Boolean("Not Have Empty Box")
    sale_order_id = fields.Many2one(comodel_name="sale.order", string="Sale Order")
    is_tenderx=fields.Boolean("is tender",related="operation_type.is_tender")
    DoctorPhoneNum = fields.Char(string="Doctor Phone Number")
    additional_file = fields.Binary('Additional File')
    additional_file_name = fields.Char(string="Additional")
    @api.constrains('DoctorPhoneNum' )
    def check_mobile_zise(self):
        for rec in self:
            if rec.DoctorPhoneNum:
                mobile = rec.DoctorPhoneNum
                if len(mobile)< 11:
                    raise ValidationError("Mobile Phone should be  11 digit")
                elif len(mobile)>11:
                    raise ValidationError("Mobile Phone should be 11 digit")
                else :
                    pass
    @api.onchange('payment_methods')
    def payment_method_change(self):
        for rec in self:
            if rec.hospital_id:
                 if rec.hospital_id.hospital_activation == False and rec.payment_methods != 'cash':
                     raise ValidationError("please make the hospital active to work with non cash method")
    @api.onchange('hospital_id')
    def _get_name(self):
        for rec in self:
            if rec.hospital_id:
                 if rec.hospital_id.hospital_activation == False and rec.payment_methods != 'cash':
                     raise ValidationError("please make the hospital active to work with non cash method")
            if rec.hospital_id:
                rec.name = "Operation - " + str(rec.hospital_id.name)

    # get attendese
    @api.onchange('responsible')
    def _create_attendese(self):
        for rec in self:
            rec.attend_ids = [[6, 0, [rec.responsible.id]]]

    # get location
    def get_default_stock_config(self):
        customers_operations_location = self.env['ir.default'].get('stock.config.settings',
                                                                   'customers_operations_location')
        return customers_operations_location

    # Set refrenced user
    def _get_currunt_loged_user(self):
        return self.env.user.id

    # def _get_default_state(self):
    #     if self.env.ref('surgi_operation.operation_default_stage'):
    #         return self.env.ref('surgi_operation.operation_default_stage')

    # This method is to calculate stop time

    # @api.onchange('start_datetime')
    # def get_stop_time(self):
    # for rec in self:
    # if rec.start_datetime:
    # rec.start = rec.start_datetime
    # start = datetime.datetime.strptime(rec.start_datetime, DEFAULT_SERVER_DATETIME_FORMAT)
    # rec.stop = rec.stop_datetime = (start + timedelta(hours=3))

    # /////////////////////////////////////////////////////////////////////////////////

    def action_done_sales(self):
        self.state = 'done'

    # button to recheck on the policy of confirmation flag for Tender Team  #
    def action_check_operation(self):
        if (self.responsible.name and self.responsible.name == 'Tender User'):
            self.flag = True
        else:
            self.flag = True

    def action_confirm_sales(self):
        for rec in self:
            aproved=False
            aprovemsg="this tender operation need to be aproved from one of \n"
            if rec.operation_type.is_tender:
                for aprove in rec.tenderaprove:
                    if  aprove.aproved:
                        aproved=True
                    else:    
                        aprovemsg+=aprove.username+"\n"
                if not aproved:
                    raise ValidationError(aprovemsg)
                        
        self.sequence = self.env['ir.sequence'].get('sale_operation_number')
        print('sequence ======================= ', self.sequence)
        values = {
            'name': self.sequence,
            'location_id': self.hospital_id.operations_location.id,
            'usage': "transit",
            'is_operation_location': True,
            'warehouse_id': self.warehouse_id.id,
            # 'company_id': False,
        }
        res_location = self.env['stock.location'].create(values)
        print('location ======================= ', res_location)
        picking_type = self.env['stock.picking.type'].search(
            [('warehouse_id', '=', self.warehouse_id.id), ('surgeries_supply', '=', True)])
        print("Picking type: " + str(picking_type.id))
        print(picking_type.default_location_src_id.id)
        vals = {
            'partner_id': self.hospital_id.id,
            'picking_type_id': picking_type.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': res_location.id,
            'origin': self.sequence,
            # 'min_date': self.start_datetime,
            'operation_id': self.id,
            'is_operation_move': True,
        }
        move_lines = []
        for component in self.component_ids:
            if component.pack == True:
                for ln in component.pack_line_ids:
                    line = [0, False, {
                        # 'qty_delivered': 0,
                        'product_id': ln.product_id.id,
                        'product_uom': ln.product_id.uom_id.id,
                        'sequence': ln.product_id.sequence,
                        'price_unit': ln.product_id.lst_price,
                        'product_uom_qty': ln.quantity,
                        # 'discount': 0,
                        'state': 'draft',
                        # 'qty_delivered_updateable': True,
                        # 'invoice_status': 'no',
                        'name': ln.product_id.name, }]
                    move_lines.append(line)
            elif component.pack == False:
                line = [0, False, {
                    # 'qty_delivered': 0,
                    'product_id': component.id,
                    'product_uom': component.uom_id.id,
                    'sequence': component.sequence,
                    'price_unit': component.lst_price,
                    'product_uom_qty': 1,
                    'state': 'draft',
                    # 'qty_delivered_updateable': True,
                    # 'invoice_status': 'no',
                    'name': component.name, }]
                move_lines.append(line)
        for product_line in self.product_lines:
            move_lines.append([0, 0, {
                'product_id': product_line.product_id.id,
                'product_uom_qty': product_line.quantity,
                'product_uom': product_line.product_id.uom_id.id,
                'name': product_line.product_id.name,
                # 'qty_delivered': 0,
                'sequence': product_line.product_id.sequence,
                'price_unit': product_line.product_id.lst_price,
                # 'discount': 0,
                'state': 'draft',
                # 'qty_delivered_updateable': True,
                # 'invoice_status': 'no',
            }])
        vals['move_lines'] = move_lines

        res = self.env['stock.picking'].create(vals)
        print('stock picking =============================== ', res)
        self.write({
            'state': 'confirm',
            'location_id': res_location.id,
            'name': self.sequence
        })


    #        operations = self.env['operation.operation'].search(['|', ('state', '=', 'confirm'), ('state', '=', 'done')])
    #        for operation in operations:
    #            operation.name = operation.sequence
    #        self.state = 'confirm'
    #        self.location_id = res_location

    # =================================== A.salama ==========================
    # get count of operation quant according to location id

    def get_operation_location_quant(self):
        print('Operations')
        for rec in self:
            if rec.location_id:
                operations = self.env['stock.quant'].search(
                    [('location_id', '=', rec.location_id.id), ('quantity', '>', 0)])
                if operations:
                    rec.oper_loc_quant = len(operations)
                else:
                    rec.oper_loc_quant = 0
            else:
                rec.oper_loc_quant = 0

    def get_sec_operation_location_quant(self):
        print('Operations')
        for rec in self:
            if rec.sec_location_id:
                operations = self.env['stock.quant'].search(
                    [('location_id', '=', rec.sec_location_id.id), ('quantity', '>', 0)])
                if operations:
                    rec.sec_oper_loc_quant = len(operations)
                else:
                    rec.sec_oper_loc_quant = 0
            else:
                rec.sec_oper_loc_quant = 0

    def get_operation_location_hanged_quant(self):
        for rec in self:
            if rec.location_id:
                operations = self.env['hanged.stock.quant'].search([('operation_location_id', '=', rec.location_id.id)])
                if operations:
                    rec.oper_loc_hanged_quant = len(operations)
                    rec.has_oper_loc_hanged_quant = len(operations) > 0
                else:
                    rec.oper_loc_hanged_quant = 0
                    rec.has_oper_loc_hanged_quant = 0


            else:
                rec.oper_loc_hanged_quant = 0
                rec.has_oper_loc_hanged_quant = 0

    def get_operation_location_quant(self):
        for rec in self:
            if rec.location_id:
                operations = self.env['stock.quant'].search([('location_id', '=', rec.location_id.id)])
                q = 0
                if operations:
                    for l in operations:
                        q += l.available_quantity
                    rec.oper_loc_quant = int(q)
                    rec.has_oper_loc_quant = q > 0
                else:
                    rec.oper_loc_quant = 0
                    rec.has_oper_loc_quant = 0


            else:
                rec.oper_loc_quant = 0
                rec.has_oper_loc_quant = 0

    def get_sec_operation_location_quant(self):
        for rec in self:
            if rec.sec_location_id:
                operations = self.env['stock.quant'].search([('location_id', '=', rec.sec_location_id.id)])
                q = 0
                if operations:
                    for l in operations:
                        q += l.available_quantity
                    rec.sec_oper_loc_quant = int(q)
                    rec.has_sec_oper_loc_quant = q > 0
                else:
                    rec.sec_oper_loc_quant = 0
                    rec.has_sec_oper_loc_quant = 0


            else:
                rec.sec_oper_loc_quant = 0
                rec.has_sec_oper_loc_quant = 0

    def get_operation_del(self):
        for rec in self:
            operation_location = self.env['stock.location'].search([('name', '=', rec.sequence)], limit=1)
            operationsDel = self.env['stock.picking'].search(['|', ('location_id', '=', operation_location.id),
                                                              ('location_dest_id', '=', operation_location.id), ])

            # ('operation_id', '=', rec.id)
            if operationsDel:
                rec.oper_loc_del = len(operationsDel)
            else:
                rec.oper_loc_del = 0

    def get_operation_so(self):
        for rec in self:
            operationsSO = self.env['sale.order'].search(
                [('operation_id', '=', rec.id), ('so_type', 'in', ['operation', 'tender', 'supply_order'])])
            if operationsSO:
                rec.oper_loc_so = len(operationsSO)
            else:
                rec.oper_loc_so = 0

    # Create sale order regarding to operation data in hanged
    def create_sales_order(self):
        quants = self.env['hanged.stock.quant'].search([('operation_location_id', '=', self.location_id.id)])
        if len(quants) > 0:
            hanged_location_id = quants[0].location_id.id
            pricelist=""
            if self.payment_methods=='cash':
                term = self.env['account.payment.term'].search([('name', 'like', 'Cash')])
                pricelist=self.surgeon_id.property_product_pricelist
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
                for item in pricelist.item_ids:
                    if quant.product_id.id == item.product_id.id:
                        price = item.fixed_price
                if quant.quantity > 0:
                    line = [0, False, {
                        'qty_delivered': 0,
                        'product_id': quant.product_id.id,
                        'product_uom': quant.product_id.uom_id.id,
                        'sequence': quant.product_id.sequence,
                        'price_unit': price,
                        'product_uom_qty': quant.quantity,
                        'state': 'draft',
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

    def check_need_x_rays(self):
        for i in self.component_ids:
            if i.product_tmpl_id.need_xrays == True:
                if not self.attachment_pre or not self.attachment_after or not self.attachment_paitent or not self.paitent_joint_pre_company:
                    return True
        pass

    def check_need_x_rays_operation_type(self):
        for i in self.operation_type:
            if i.need_xrays_op_type == True:
                if not self.attachment_pre or not self.attachment_after or not self.attachment_paitent or not self.paitent_joint_pre_company:
                    return True

        pass

    # Create sale order regarding to operation data not hanged
    def create_delivery_sales_order(self):
        if self.check_need_x_rays():
            raise exceptions.ValidationError('Please fill Pre Operative XRay & post Operative XRay')
        elif self.check_need_x_rays_operation_type():
            raise exceptions.ValidationError('Please fill Pre Operative XRay & post Operative XRay')

        quants = self.env['stock.quant'].search([('location_id', '=', self.location_id.id)])
        if len(quants) > 0:
            operation_location_id = quants[0].location_id.id
            pricelist=""
            if self.payment_methods=='cash':
                pricelist=self.surgeon_id.property_product_pricelist
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
                for item in pricelist.item_ids:
                    if quant.product_id.id == item.product_id.id and quant.quantity > 0:
                        price = item.fixed_price
                if quant.quantity > 0:
                    line = [0, False, {
                        'qty_delivered': 0,
                        'product_id': quant.product_id.id,
                        'product_uom': quant.product_id.uom_id.id,
                        'sequence': quant.product_id.sequence,
                        'price_unit': price,
                        'product_uom_qty': quant.quantity,
                        'state': 'draft',
                        # 'qty_delivered_updateable': True,
                        'invoice_status': 'no',
                        'name': quant.product_id.name, }]
                    order_lines.append(line)

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

    # To Make state='done' automatically ,once sales order have been created (pressed on "Create SO-OL"Button)
        self.state= 'done'

    # Create sale order regarding to operation data not hanged Tender
    def create_delivery_sales_order_tender(self):
        quants = self.env['stock.quant'].search([('location_id', '=', self.location_id.id)])
        if len(quants) > 0:
            pricelist=""
            if self.payment_methods=='cash':
                pricelist=self.surgeon_id.property_product_pricelist
            else:
                pricelist=self.hospital_id.property_product_pricelist
            operation_location_id = quants[0].location_id.id
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
                'user_id': self.env.user.id,
                'team_id': 277,
                'sales_area_manager': self.op_area_manager,
                # field updated by SURGI-TECH --- END--
                'warehouse_id': self.warehouse_id.id,
                'location_id': operation_location_id,
                'location_dest_id': self.hospital_id.property_stock_customer.id,
                'so_type': 'operation',
                'delivery_type': self.operation_delivery_type,
                'operation_id': self.id,
            }
            order_lines = []
            for quant in quants:
                price = quant.product_id.lst_price
                for item in pricelist.item_ids:
                    if quant.product_id.id == item.product_id.id:
                        price = item.fixed_price
                line = [0, False, {
                    'qty_delivered': 0,
                    'product_id': quant.product_id.id,
                    'product_uom': quant.product_id.uom_id.id,
                    'sequence': quant.product_id.sequence,
                    'price_unit': price,
                    'product_uom_qty': quant.quantity,
                    'state': 'draft',
                    # 'qty_delivered_updateable': True,
                    'invoice_status': 'no',
                    'name': quant.product_id.name, }]
                order_lines.append(line)

            values['order_line'] = order_lines
            print("vals: " + str(values))
            sale_order = self.env['sale.order'].create(values)
            self.so_created = True
            sale_order.action_confirm()
            sale_order.changed_line_ids()

            pickings = sale_order.mapped('picking_ids')
            scan_product_ids_lst = []
            for quant in quants:
                if quant.product_id.tracking == 'lot' or quant.product_id.tracking == 'serial':
                    line = [0, 0,
                            {'product_id': quant.product_id.id,
                             'product_uom_qty': quant.quantity,
                             'lot_no': quant.lot_id.name,
                             }]
                    scan_product_ids_lst.append(line)
            for picking in pickings:
                picking.scan_products_ids = scan_product_ids_lst
                picking.button_validate()
            print(sale_order)
            print("Sale_order: " + str(sale_order))
        else:
            raise exceptions.ValidationError('No Quants Available in  Location!')

    # Create Draft sale order  before operation
    def create_draft_sales_order(self):

        operation_location_id = self.location_id.id
        pricelist=""
        if self.payment_methods=='cash':
            pricelist=self.surgeon_id.property_product_pricelist
        else:
            pricelist=self.hospital_id.property_product_pricelist
        # Sales Order fields
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
            'location_id': operation_location_id,
            'location_dest_id': self.hospital_id.property_stock_customer.id,
            'delivery_type': self.operation_delivery_type,

            'so_type': 'operation',
            'operation_id': self.id,
        }

        self.so_created = True
        values['order_line'] = []
        print("vals: " + str(values))
        sale_order = self.env['sale.order'].create(values)
        self.sale_order_id = sale_order.id
        # sale_order.action_confirm()

    # open tree view of operation quantities using location of operation
    def action_view_operation_quant(self):
        for rec in self:
            compose_tree = self.env.ref('stock.view_stock_quant_tree', False)
            operations = self.env['stock.quant'].search(
                [('location_id', '=', rec.location_id.id), ('quantity', '>', 0)])
            list = []
            for op in operations:
                list.append(op.id)
            return {
                'name': "Operations Quantities",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                # 'field_parent': 'child_ids',
                'res_model': 'stock.quant',
                'views': [(compose_tree.id, 'tree')],
                'view_id': compose_tree.id,
                'target': 'current',
                'domain': [('id', 'in', list)],
            }

    def action_view_sec_operation_quant(self):
        for rec in self:
            compose_tree = self.env.ref('stock.view_stock_quant_tree', False)
            operations = self.env['stock.quant'].search(
                [('location_id', '=', rec.sec_location_id.id), ('quantity', '>', 0)])
            list = []
            for op in operations:
                list.append(op.id)
            return {
                'name': "Operations Quantities",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                # 'field_parent': 'child_ids',
                'res_model': 'stock.quant',
                'views': [(compose_tree.id, 'tree')],
                'view_id': compose_tree.id,
                'target': 'current',
                'domain': [('id', 'in', list)],
            }

    def action_view_operation_hanged_quant(self):
        for rec in self:
            compose_tree = self.env.ref('surgi_operation.hanged_stock_quant_tree_inherit', False)
            operations = self.env['hanged.stock.quant'].search([('operation_location_id', '=', rec.location_id.id)])
            list = []
            for op in operations:
                list.append(op.id)
            return {
                'name': "Operations Hanged Quantities",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'hanged.stock.quant',
                'views': [(compose_tree.id, 'tree')],
                'view_id': compose_tree.id,
                'target': 'current',
                'domain': [('id', 'in', list)],
            }

    def action_view_operation_del(self):
        for rec in self:
            operation_location = self.env['stock.location'].search([('name', '=', rec.sequence)], limit=1)
            operations = self.env['stock.picking'].search(
                ['|', ('location_id', '=', operation_location.id), ('location_dest_id', '=', operation_location.id), ])
            # ('operation_id', '=', rec.id)
            list = []
            for op in operations:
                list.append(op.id)
            return {
                'name': "Operations Delivery Orders",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'stock.picking',
                'target': 'current',
                'domain': [('id', 'in', list)],
            }

    def action_view_operation_SO(self):
        for rec in self:
            operations = self.env['sale.order'].search([('operation_id', '=', rec.id)])
            list = []
            for op in operations:
                list.append(op.id)
            return {
                'name': "Operations Sale Order",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'target': 'current',
                'domain': [('id', 'in', list)],
            }

    def action_view_operation_invoice(self):
        for rec in self:
            tree_id = self.env.ref('account.view_move_tree', False)
            form_id = self.env.ref('account.view_move_form', False)
            return {
                'name': "Operations Invoice",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(tree_id.id, 'tree'), (form_id.id, 'form')],
                'view_id': tree_id.id,
                'res_model': 'account.move',
                'target': 'current',
                'domain': [('id', 'in', [rec.invoice_id.id])],
            }

    @api.model
    def _get_confirm_states(self):
        states = self.STATE_SELECTION
        for rec in self.env['operation.stage'].search([]):
            states.append((rec.name, rec.name))
        return states

    # ==================== Fields ==========================
    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('freeze', 'Freezed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]

    name = fields.Char(string="name")
    # event_id = fields.Many2one("calendar.event", string="Customers", ondelete='cascade') #Delegation field
    start_datetime = fields.Datetime('Date Start', required=True,trucking=True,track_visibility=True,
                                     help="Start date of an event, without time for full days events")
    hospital_id = fields.Many2one('res.partner', string="Hospital", track_visibility='onchange')
    patient_national_id = fields.Char(string="Patient National ID",
                                      help="If patient not exist it will be create from exist data, but if it's on system his data will be loaded automatic.")
    sequence = fields.Char(string="Operation No.", size=16, readonly=True, track_visibility=True)
    attend_ids = fields.Many2many(comodel_name='res.users', relation='doctor_partner_patient_rel',
                                  coulmn1='responsible', coulmn2='patient', string='Attendees',
                                  compute='_create_attendese', readonly=True)
    is_patient = fields.Boolean(Default=False, invisible=True)
    patient_id = fields.Many2one('res.partner', string="Patient", track_visibility='onchange')
    patient_name = fields.Char(string="Patient Name")
    patient_gender = fields.Selection([('m', 'Male'), ('f', 'Female')], string="Patient Gender")
    surgeon_id = fields.Many2one('res.partner', string="Surgeon", track_visibility='onchange')
    side = fields.Selection([('r', 'Right'), ('l', 'Left')], string="Side", track_visibility='onchange')
    # internal_type = fields.Selection([('sale','Sale'),('stock','Stock')],string="Internal Type")
    notes = fields.Text(string="Notes")
    # picking_type = fields.Many2one('stock.picking.type',string="Picking Type")
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", track_visibility='onchange')
    operation_stock_branches = fields.Many2one(related='warehouse_id.stock_branches', string='Branch', store=True)
    is_to_bool = fields.Boolean()

    component_ids = fields.Many2many('product.product', string="Components")  # ,compute='_auto_gender_generate'
    component_ids_name = fields.Char(related='component_ids.name', string='com name')
    state = fields.Selection(selection=lambda self: [(x.state_name, x.name) for x in
                                                     self.env['operation.stage'].search([('is_active', '=', True)])],
                             string='Status', readonly=False, default="draft")
    # stage_id = fields.Many2one(comodel_name="operation.stage", string="Stage id", track_visibility='onchange', required=False, select=True,copy=False,
    #                          default=lambda self: self.env.ref('surgi_operation.operation_confirm_stage', False), domain=[('is_active', '=', True)])

    customers_operations_location = fields.Many2one('stock.location', string="Customers Operations Location",
                                                    default=get_default_stock_config)
    operation_type = fields.Many2one('product.operation.type', string="Operation Type", track_visibility='onchange',
                                     store=True)
    operation_type_track = fields.Char(related="operation_type.name", string="operation type Name")

    responsible = fields.Many2one(comodel_name='res.users', string="Responsible", default=_get_currunt_loged_user,
                                  track_visibility='onchange')
    op_sales_area = fields.Many2one('crm.team', string='Sales Channel', oldname='section_id',
                                    default=lambda self: self.env['crm.team'].search(
                                        ['|', ('user_id', '=', self.env.uid), ('member_ids', '=', self.env.uid)],
                                        limit=1))
    op_area_manager = fields.Many2one(comodel_name='res.users', string="Area Manager", related='op_sales_area.user_id',
                                      readonly=True)
    location_id = fields.Many2one(comodel_name='stock.location', string='Location')
    sec_location_id = fields.Many2one(comodel_name='stock.location', string='Secondary Location')
    is_operation_freeze = fields.Boolean(related="location_id.operation_location_freeze",
                                         string="Is Operation Location Freeze", store=True)
    product_lines = fields.One2many('product.operation.line', 'operation_id', string="products")
    # component_ids = fields.Many2many('product.product', string="Components", track_visibility='onchange')
    tags_ids = fields.Many2many('operation.tag', string="Tags")

    # Fileds created by Mostafa Nassar start
    gs_work_order = fields.Char(string="GS Work Order")
    hospital_sales_man = fields.Many2one(comodel_name="res.users", string="", related='hospital_id.user_id',
                                         readonly=True)
    recon_sales_channel = fields.Many2one(comodel_name="crm.team", string="", related='hospital_id.team_id',
                                          readonly=True)
    hospital_sales_users = fields.Many2many(comodel_name="res.users", relation="operation_operation_res_users_rel",
                                            column1="operation_operation_id", column2="res_users_id",
                                            related='hospital_id.direct_sales_users', string="Hospital Sales User",
                                            readonly=True)
    payment_methods = fields.Selection(string="Payment Methods", selection=[('cash', 'Cash'), ('credit', 'Credit'),
                                                                            ('replacement', 'Replacement'),('hospitalcash', 'Hospital Cash')])#, ('cashpatient', 'Cash Patient')
    operation_price = fields.Integer(string="Operation Price")
    authority = fields.Selection(string='Authority Type', related='hospital_id.authority')
    # Fileds created by Mostafa Nassar End

    message_com = fields.Char(string='Components', track_visibility=True)
    message_item = fields.Char(string='Operation Items', track_visibility=True)
    active = fields.Boolean(default=True)
    product_qunat_tab = fields.One2many('stock.items', 'operation_id', 'Related')

    invoice_id = fields.Many2one(comodel_name='account.move', string='Invoice', readonly=True)
    surgeon_id_first_confirmation = fields.Many2one('res.partner', string="Surgeon", track_visibility='onchange')
    # sender_responsible = fields.Many2one(comodel_name='res.users', string="Sender", default=_get_currunt_loged_user,track_visibility='onchange')
    surgeon_id_second_confirmation = fields.Many2one('res.partner', string="Surgeon", track_visibility='onchange')
    # returner_responsible = fields.Many2one(comodel_name='res.users', string="Returner", default=_get_currunt_loged_user,track_visibility='onchange')
    qunat = fields.One2many('hanged.stock.quant', 'operation_id', 'Quants')
    consumed_items_file = fields.Binary(string='Consumed Items',track_visibility='always', store=True,  attachment=True)#
    # delivery_type = fields.Selection(string="Delivery Type", selection=[('delivery_exchange', 'Delivery Exchange'), ('sale_delivery', 'Sales Delivery'),('load_delivery','Loaded Delivery') ], required=False, )
    operation_delivery_type = fields.Selection(string="Delivery Type ", tracking=True,
                                               selection=[('delivery2customer', 'Delivery To Customer')
                                                   , ('delivery2tender', 'Delivery To Tender')
                                                   , ('deliveryorder', 'Delivery Order')
                                                   , ('loading', 'Loading')
                                                   , ('exchange', 'Exchange ')
                                                   , ('replacement', 'Replacement')
                                                   , ('purchasereturn', 'Purchase Return')
                                                   , ('gov', 'Government Form')],
                                               help="Used ot show picking type delivery type")

    attachment_pre = fields.Binary(string="Pre Operative XRay", store=True)
    attachment_after = fields.Binary(string="Post Operative XRay", store=True)
    attachment_paitent = fields.Binary(string="Revised Implant", store=True)
    paitent_joint_pre_company = fields.Char(string='Joint Pre Company', store=True)
    emp_confirm = fields.Boolean(string="Reviewed")
    my_operation_confirm = fields.Boolean(string="My Operation Confirm", default=False)

    def confirm_my_operation(self):
        for rec in self:
            rec.write({'my_operation_confirm':True})
    def add_cons_item_wizard(self):
        return {
            'name': ('Add Item'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'op.add.item',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def button_emp_confirm(self):
        for rec in self:
            rec.emp_confirm=True
            self.write({'state': 'reviewed', })


    # @api.onchange("is_operation_freeze")
    # def check_field_is_operation_freeze_value(self):
    #     if self.is_operation_freeze:
    #         self.state = "confirm"
    #     else :
    #         self.write({'state': 'confirm', })


    #     def create_mass(self):
    #         vals={
    #         "user_id":self.user_id.id,
    #         "consumed_items_file":self.consumed_items_file
    #         }
    #         self.consumed_items_file.message_post(body="file has been edit")
    #         self.env('operation.operation').create(vals)

    @api.onchange("consumed_items_file")
    def check_field_xlsx_value(self):
        for rec in self:
            if rec.consumed_items_file:
                rec.write({'state': 'net' })
        # elif not self.consumed_items_file:
        #     self.write({'state': 'confirm', })


    def set_operation_location_freeze_from_operation(self):
        x = self.location_id.id
        if  not self.have_emptybox and not self.nothaveempty:
            raise ValidationError("Please Make Sure that there is no empty box")
        # self.location_id.operation_location_freeze = True
        self.write({'state': 'freezed', })

    # @api.onchange("is_operation_freeze")
    # def set_operation_location_unfreeze_from_operation(self):
    #     if self.is_operation_freeze:
    #         self.write({'state': 'freezed', })
    #     elif not self.is_operation_freeze:
    #         self.write({'state': 'confirm', })


        return {
            'name': 'You Will freeze Location with  these Products',
            'view_mode': 'form',
            'view_id': self.env.ref('surgi_inventory_changes.view_stock_quant_freeze', False).id,
            'res_model': 'stock.location',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.location_id.id,
        }
        print("ss")

    def create_Secondary_Location(self):
        values = {
            'name': self.location_id.name + '_Sec',
            'location_id': self.hospital_id.operations_location.id,
            'usage': "transit",
            'is_operation_location': True,
            'warehouse_id': self.warehouse_id.id,
            # 'company_id': False,
        }
        res_location = self.env['stock.location'].create(values)
        self.write({'sec_location_id': res_location.id})
        pass

    # @api.onchange('is_operation_freeze')
    # def _onchange_is_operation_freeze(self):
    #     self.write({
    #         'state': 'freeze',})

    def create_operation_invoice(self):
        for rec in self:
            vals = {
                'type': 'out_invoice',
                'operation_ids': [(6, 0, [rec.id])],
                'operation_id': rec.id,
                'patient_name': rec.patient_name,
                'surgeon_id': rec.surgeon_id and rec.surgeon_id.id,
                'partner_id': rec.hospital_id.id,
                'account_id': rec.hospital_id.property_account_receivable_id.id,
            }
            if rec.hospital_id.property_product_pricelist:
                vals['currency_id'] = rec.hospital_id.property_product_pricelist.currency_id.id
            if rec.hospital_id.property_payment_term_id:
                vals['payment_term_id'] = rec.hospital_id.property_payment_term_id.id
            res = self.env['account.move'].create(vals)

            if res:
                rec.invoice_id = res.id
                for component in rec.component_ids:
                    if component.pack == True:
                        for line in component.pack_line_ids:
                            price = 0
                            for item in rec.hospital_id.property_product_pricelist.item_ids:
                                if line.product_id.id == item.product_id.id:
                                    price = item.fixed_price
                                    account_id = item.product_id.property_account_income_id.id
                                    if not account_id:
                                        account_id = item.product_id.categ_id.property_account_income_categ_id.id
                            self.env['account.move.line'].create({
                                'payment_term_id': res.payment_term_id.id if res.payment_term_id else None,
                                'product_id': line.product_id.id,
                                'name': rec.name,
                                'account_id': account_id,
                                'quantity': line.quantity,
                                'uom_id': component.uom_id.id,
                                'price_unit': price,
                                'invoice_id': res.id,
                            })
                    else:
                        price = 0
                        for item in rec.hospital_id.property_product_pricelist.item_ids:
                            if component.id == item.product_id.id:
                                price = item.fixed_price
                                account_id = item.product_id.property_account_income_id.id
                                if not account_id:
                                    account_id = item.product_id.categ_id.property_account_income_categ_id.id
                        self.env['account.move.line'].create({
                            'payment_term_id': res.payment_term_id.id if res.payment_term_id else None,
                            'product_id': component.id,
                            'name': rec.name,
                            'account_id': account_id,
                            'quantity': 1,
                            'uom_id': component.uom_id.id,
                            'price_unit': price,
                            'invoice_id': res.id,
                        })
                for product_line in rec.product_lines:
                    price = 0
                    for item in rec.hospital_id.property_product_pricelist.item_ids:
                        if product_line.product_id.id == item.product_id.id:
                            price = item.fixed_price
                            account_id = item.product_id.property_account_income_id.id
                            if not account_id:
                                account_id = item.product_id.categ_id.property_account_income_categ_id.id
                    self.env['account.move.line'].create({
                        'payment_term_id': res.payment_term_id.id if res.payment_term_id else None,
                        'product_id': product_line.product_id.id,
                        'name': rec.name,
                        'account_id': account_id,
                        'quantity': product_line.quantity,
                        'uom_id': product_line.product_id.uom_id.id,
                        'price_unit': price,
                        'invoice_id': res.id,
                    })

    def update_operation_type(self):
        print('1')

    @api.onchange('authority')
    def get_partner_id(self):
        if (self.authority and self.authority == 'open' or self.authority == 'open_approval'):
            domain = {'surgeon_id': [('is_surgeon', '=', True), '|', '|', ('team_id', '=', self.op_sales_area.id),
                                     ('user_id', "=", self.env.user.id), ('direct_sales_users', "=", self.env.user.id)]}
            return {'domain': domain}
        else:
            domain = {'surgeon_id': [('is_surgeon', '=', True)]}
            return {'domain': domain}

    @api.onchange('component_ids')
    def get_component_ids(self):
        messagee = '( '
        for pro in self.component_ids:
            messagee += pro.name + '  /  '
        messagee += ' )'
        self.message_com = messagee

    @api.onchange('product_lines')
    def get_product_lines(self):
        messagee = '( '
        for line in self.product_lines:
            messagee += line.product_id.name + '  /  '
        messagee += ' )'
        self.message_item = messagee

    # ============= NewFields ================
    # for the new cycle (Operation type) By Zienab Morsy
    op_type = fields.Selection([
        ('private', 'Private'),
        ('tender', 'Waiting List'),
        ('supply_order', 'Supply Order'),
    ], string='Type', default="private")
    tender_so = fields.Many2one('sale.order', string='Tender SO', domain=[('so_type', '=', 'tender')])
    patient_national_identification = fields.Many2one('waiting.list.patients', string='Patient National ID',
                                                      domain=[('is_active', '=', True)], track_visibility='onchange')
    supply_so = fields.Many2one('sale.order', string='Supply SO', domain=[('so_type', '=', 'supply_order')])

    moh_approved_operation = fields.Char(string="MOH Approved Operation")

    @api.onchange('patient_national_identification', 'op_type')
    def _patient_name_get(self):
        if (self.patient_national_identification and self.op_type == 'tender'):
            self.patient_name = self.patient_national_identification.patient_name
            self.patient_national_id = self.patient_national_identification.patient_national_id
            self.moh_approved_operation = self.patient_national_identification.moh_approved_operation

    # ============= NewMethod ================
    # for the new cycle (Operation type) By Zienab Morsy
    # @api.onchange('responsible')
    # def _onchange_responsible_id(self):
    # self.tender_so = ""
    # if (self.hospital_id.direct_sales_users and self.hospital_id.direct_sales_users == self.env.user.id):
    #     self.flag = True
    # elif (self.hospital_id.user_id and self.hospital_id.user_id == self.env.user.id):
    #     self.flag=True
    # else:
    #    self.flag = False

    @api.onchange('hospital_id')
    def _onchange_hospital_id(self):
        self.tender_so = ""
        if (self.recon_sales_channel.id and self.recon_sales_channel.id == self.op_sales_area.id):
            self.flag = True
        elif (self.authority and self.authority == 'open'):
            self.flag = True
        else:
            self.flag = False
        if self.op_type == 'tender':
            ## Remove this fro domain ('partner_id', "=", self.hospital_id.id),
            domain = {
                'tender_so': [('so_type', '=', 'tender'), ('state', '=', 'sale')]}
            return {'domain': domain}
        elif self.op_type == 'supply_order':
            ## Remove this fro domain ('partner_id', "=", self.hospital_id.id),
            domain = {
                'tender_so': [('so_type', '=', 'supply_order'), ('state', '=', 'sale')]}
            return {'domain': domain}

    # =============== wizard fields ================
    reason = fields.Many2one(comodel_name='operation.cancel.reason', string="Reason")
    description = fields.Text(string="Description")
    oper_loc_quant = fields.Char("Operation Location Quant", compute='get_operation_location_quant')
    sec_oper_loc_quant = fields.Char("Operation Location Quant",
                                     compute='get_sec_operation_location_quant')  # , compute=get_operation_location_quant
    # , compute=get_operation_location_quant
    oper_loc_hanged_quant = fields.Char("Operation Hanged Quants",
                                        compute='get_operation_location_hanged_quant')  # , compute=get_operation_location_hanged_quant
    has_oper_loc_hanged_quant = fields.Boolean(
        compute='get_operation_location_hanged_quant')  # compute=get_operation_location_hanged_quant
    has_oper_loc_quant = fields.Boolean(
        compute='get_operation_location_quant')
    has_sec_oper_loc_quant = fields.Boolean(
        compute='get_sec_operation_location_quant')
    # compute=get_operation_location_hanged_quant
    oper_loc_del = fields.Char("Operation Delivery Orders", compute='get_operation_del')  # , compute=get_operation_del
    oper_loc_so = fields.Char("Operation Delivery Orders", compute='get_operation_so')  # , compute=get_operation_so
    so_created = fields.Boolean(default=False)

    # ================= Main methods =======================
    @api.model
    def create(self, vals):
        vals['name'] = "Operation"
        vals['state'] = "draft"
        operation = super(operation_operation, self).create(vals)
        return operation


    def write(self,vals):
        ###########################send mail on operation changes
        #mail_template = self.env.ref('surgi_operation.operation_edit_confirmation_mail')
        ##mail_template.send_mail(self.id, force_send=True)
        #mail_template.send_mail(self.ids[0], force_send=True)
        return super(operation_operation, self).write(vals)

    # def write(self, vals):
    #    states = [self.env.ref('surgi_operation.operation_default_stage').id, self.env.ref('surgi_operation.operation_confirm_stage').id, self.env.ref('surgi_operation.operation_done_stage').id, self.env.ref('surgi_operation.operation_cancel_stage').id]
    #    if "stage_id" in vals:
    #        if(vals['stage_id'] in states):
    #            raise Warning("This stage is not editable.")
    #        vals['state'] = self.env['operation.stage'].browse(vals['stage_id']).state_name
    #    if "state" in vals and vals["state"] == "cancel":
    #        vals["stage_id"] =  self.env.ref('surgi_operation.operation_cancel_stage').id
    #    return super(operation_operation, self).write(vals)

    _defaults = {
        'username_print': _get_currunt_loged_user,
    }

    flag = fields.Boolean(default=False)


class product_inherit_item(models.Model):
    _inherit = 'product.product'


class stock_items_inherit_wizard(models.Model):
    _name = 'stock.items'

    product_id = fields.Many2one('product.product', string='Product')
    internal = fields.Boolean(string='Internal')
    external = fields.Boolean(string='External')
    prod_replacement = fields.Boolean(string='Empties')

    operation_id = fields.Many2one('operation.operation', string="Operation")

