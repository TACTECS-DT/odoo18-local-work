from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class InventoryCountSession(models.Model):
    _name = 'setu.inventory.count.session'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin', 'barcodes.barcode_events_mixin']
    _description = 'Inventory Count Session'

    name = fields.Char(
        string="Name"
    )
    color = fields.Integer(
        compute="_compute_color",
        string="Color"
    )
    time_taken = fields.Char(
        compute="_compute_time_taken",
        string="Time Taken"
    )
    inventory_count_id = fields.Many2one(
        comodel_name="setu.stock.inventory.count",
        string="Inventory Count"
    )
    total_products = fields.Integer(
        compute="_compute_scanned_products",
        store=True,
        string="Total Products"
    )
    total_scanned_products = fields.Integer(
        compute="_compute_scanned_products",
        store=True,
        string="Total Scanned Products"
    )
    to_be_scanned = fields.Integer(
        compute="_compute_scanned_products",
        store=True,
        string="To be scanned"
    )
    session_line_ids = fields.One2many('setu.inventory.count.session.line', 'session_id', string="Inventory Session Count Lines")
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Location"
    )
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Warehouse"
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="warehouse_id.company_id",
        string="Company"
    )
    state = fields.Selection(
        selection=[('Draft', 'Draft'),
                   ('In Progress', 'In Progress'),
                   ('Submitted', 'Submitted'),
                   ('Done', 'Done'), ('Cancel', 'Cancel')],
        default="Draft",
        string="State"
    )
    current_state = fields.Selection(
        selection=[('Created', 'Created'),
                   ('Start', 'Start'),
                   ('Pause', 'Pause'),
                   ('Resume', 'Resume'),
                   ('End', 'End')],
        default='Created',
        string="Current State"
    )
    count_state = fields.Selection(
        related='inventory_count_id.state',
        string="Count State"
    )
    user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Users"
    )
    session_start_date = fields.Datetime(
        string="Session start date"
    )
    session_end_date = fields.Datetime(
        string="Session end date"
    )
    session_submit_date = fields.Datetime(
        string="Session submit date"
    )
    session_history_count = fields.Integer(
        compute="_compute_session_history_count",
        string="Session history count"
    )
    open_session_again = fields.Boolean(
        compute="_compute_open_session_again",
        string="Open session again"
    )
    session_id = fields.Many2one(
        comodel_name="setu.inventory.count.session",
        string="Session"
    )
    session_ids = fields.One2many('setu.inventory.count.session', 'session_id', string='Sessions')
    count_child_session_ids = fields.Integer(
        compute="_compute_child_session_ids",
        string="Child Sessions"
    )
    rejected_lines_count = fields.Integer(
        compute="_compute_rejected_lines_count",
        string="Rejected count lines"
    )
    is_session_approved = fields.Boolean(
        default=False,
        string="Is session approved"
    )
    re_open_session_bool = fields.Boolean(
        compute="_compute_re_open_session",
        string="Re-open session"
    )
    user_ids_count = fields.Integer(
        compute="_compute_user_ids_count",
        string="User Count"
    )
    approver_id = fields.Many2one(
        related="inventory_count_id.approver_id",
        string="Approver"
    )
    current_scanning_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Current scanning location"
    )
    current_scanning_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Current scanning product"
    )
    current_scanning_lot_id = fields.Many2one(
        comodel_name="stock.lot",
        string="Current scanning lot"
    )
    use_barcode_scanner = fields.Boolean(
        default=False,
        string="Use barcode scanner"
    )
    is_multi_session = fields.Boolean(
        default=False,
        string="Is multi session"
    )
    type = fields.Selection(
        related="inventory_count_id.type",
        string="Type"
    )

    # @api.model
    # def get_views(self):
    #     super(InventoryCountSession, self).get_views()

    @api.constrains('session_line_ids')
    def check_session_line_ids(self):
        if not self.session_line_ids:
            self.current_scanning_location_id = self.current_scanning_product_id = self.current_scanning_lot_id = False

    def messege_return(self, msg_type, message):
        return {
            'warning': {
                'title': _(msg_type),
                'message': _(message)
            }
        }

    # def on_barcode_scanned(self, barcode):
    #     if self.use_barcode_scanner:
    #         if self.current_state in ('Start', 'Resume'):
    #             location = self.env['stock.location'].sudo().search([('barcode', '=', barcode)], limit=1)
    #             if location:
    #                 if location in self.session_line_ids.mapped('location_id'):
    #                     self.current_scanning_location_id = location
    #                     # self.env['bus.bus']._sendone(self, 'res.users/connection', {'type': 'user_connection', 'title': 'Notification',
    #                     #       'message': 'Location changed!!', 'partner_id': self.env.user.partner_id.id})
    #                     # self.env['bus.bus']._sendone(
    #                     #     (self._cr.dbname, 'setu.inventory.count.session', self.id),
    #                     #     {'type': 'user_connection', 'title': 'Notification',
    #                     #      'message': 'Location changed!!', 'partner_id': self.env.user.partner_id.id}
    #                     # )
    #                 else:
    #                     return self.messege_return("Warning", "Location scanned is not part of this session.")
    #             else:
    #                 product = self.env['product.product'].sudo().search([('barcode', '=', barcode)], limit=1)
    #                 if product:
    #                     if product not in self.session_line_ids.mapped('product_id'):
    #                         return self.messege_return("Warning",
    #                                                    f"Product [{product.display_name}] is not to be counted in {self.current_scanning_location_id.display_name} for this session.")
    #
    #                     if self.current_scanning_location_id:
    #                         session_line = self.session_line_ids.filtered(
    #                             lambda
    #                                 l: l.location_id == self.current_scanning_location_id and l.product_id == product)
    #                         if session_line:
    #                             if session_line.product_scanned:
    #                                 return self.messege_return("Warning",
    #                                                            f"{product.display_name} is marked scanned in location {self.current_scanning_location_id.display_name} for this session. "
    #                                                            f"Please uncheck the Scanned checkbox.")
    #                             session_line.scanned_qty += 1
    #                         else:
    #                             return self.messege_return("Warning",
    #                                                        f"{product.display_name} is not to be calculated in location {self.current_scanning_location_id.display_name} for this session.")
    #                     else:
    #                         return self.messege_return("Warning",
    #                                                    "Please set the current location, then scan the products.")
    #
    #                 else:
    #                     return self.messege_return("Warning",
    #                                                "Product or Location with scanned barcode is not found.")
    #     else:
    #
    #         return self.messege_return("Notification",
    #                                    "Contact your approver to enable the barcode scanning for this session.")

    def on_barcode_scanned(self, barcode):
        if self.use_barcode_scanner:
            if self.current_state in ('Start', 'Resume'):
                vals = {}
                scanning_done = False
                location = self.env['stock.location'].sudo().search([('barcode', '=ilike', barcode)], limit=1)
                if location:
                    child_of_location_ids = self.env['stock.location'].sudo().search(
                        [('id', 'child_of', self.location_id.id)])
                    if location not in child_of_location_ids:
                        return self.messege_return("Warning",
                                                   "Scanned location is not belongs to the current Inventory Count "
                                                   "Warehouse. Kindly select an appropriate location.")
                    self.current_scanning_location_id = location
                    # if self.current_scanning_location_id.id not in child_of_location_ids.ids:
                    self.current_scanning_product_id = False
                    self.current_scanning_lot_id = False
                if not self.current_scanning_location_id:
                    return self.messege_return("Warning",
                                               "Please scan the Location first.")
                lot = self.env['stock.lot'].sudo().search([('name', '=ilike', barcode)], limit=1)
                if lot:
                    # if not self.current_scanning_location_id:
                    #     return self.messege_return("Warning",
                    #                                "Please scan the Location first.")
                    self.current_scanning_lot_id = lot
                    self.current_scanning_product_id = lot.product_id.id
                    if not self.session_id and not self.session_id.inventory_count_id.count_id:
                        session_lines = self.inventory_count_id.sudo().session_ids.mapped('session_line_ids')
                        if self.current_scanning_product_id.tracking == 'serial' and self.current_scanning_product_id and self.current_scanning_location_id:
                            if self.current_scanning_product_id.id in session_lines.filtered(
                                    lambda x: x.product_id == self.current_scanning_product_id and x.location_id != self.current_scanning_location_id
                                              and lot.id in x.serial_number_ids.ids
                                              and x.session_id.state != 'Cancel'
                                              and x.inventory_count_id == self.inventory_count_id).mapped(
                                    'product_id').ids: #and x.session_id.id != self._origin.id and x.location_id == self.current_scanning_location_id
                                raise UserError('Serial Number "{}" is already scanned in another location or by another user in '
                                                'another session for this Count.'.format(lot.name))
                        elif self.current_scanning_product_id.tracking == 'lot' and self.current_scanning_product_id and self.current_scanning_location_id and lot:
                            if self.current_scanning_product_id.id in session_lines.filtered(
                                    lambda x: x.product_id == self.current_scanning_product_id
                                              and x.session_id.state != 'Cancel'
                                              and x.location_id == self.current_scanning_location_id and x.lot_id.id == lot.id and x.inventory_count_id == self.inventory_count_id and x.session_id.id == self._origin.id).mapped(
                                    'product_id').ids:
                                raise UserError(
                                    'Lot "{}" is already scanned for the same location in the same session for this Count.'.format(
                                        lot.name))
                    vals.update({'location_id': self.current_scanning_location_id.sudo().id,
                                 'product_id': self.current_scanning_product_id.id,
                                 'session_id': self._origin.id,
                                 'date_of_scanning': datetime.now(),
                                 'inventory_count_id': self.inventory_count_id.id})
                if self.current_scanning_location_id and self.current_scanning_product_id and self.current_scanning_product_id.tracking != 'none' and not self.current_scanning_lot_id:
                    return self.messege_return("Warning",
                                               "Please scan the Lot/Serial Number.")
                if self.current_scanning_product_id.tracking == 'lot':
                    quants_lot = self.env['stock.quant'].sudo().search(
                        [('location_id', '=', self.current_scanning_location_id.id),
                         ('lot_id','=',lot.id),
                         ('product_id', '=', lot.product_id.id)])
                    vals.update({'lot_id': lot.id, 'theoretical_qty':sum([x.quantity for x in quants_lot])})#

                if self.current_scanning_product_id.tracking == 'serial':
                    quants = self.env['stock.quant'].sudo().search(
                        [('location_id', '=', self.current_scanning_location_id.id),
                         ('quantity', '=', 1),
                         # ('lot_id', '=', lot.id),
                         ('product_id', '=', lot.product_id.id)])
                    qty_available = sum([x.quantity for x in quants])
                    # qty_available = lot.product_id.with_context(location=self.current_scanning_location_id.id).qty_available
                    vals.update({'serial_number_ids': [(4, lot.id)],'theoretical_qty':qty_available})#,


                product = self.env['product.product'].sudo().search([('barcode', '=ilike', barcode)], limit=1)
                if product:
                    if not self.current_scanning_lot_id and product.tracking == 'lot':
                        return self.messege_return("Warning",
                                                   "Please scan the Lot of the Product first!")
                    if product.tracking in ['lot',
                                            'serial'] and self.current_scanning_lot_id and self.current_scanning_lot_id.sudo().product_id != product:
                        return self.messege_return("Warning",
                                                   "Please select an appropriate lot number as current lot is not belongs to the product you have scanned.")
                    if product.tracking == 'none':
                        self.current_scanning_product_id = product
                        self.current_scanning_lot_id = False
                        #session_lines = self.inventory_count_id.sudo().session_ids.mapped('session_line_ids')
                        #if self.current_scanning_product_id.tracking == 'none' and self.current_scanning_product_id and self.current_scanning_location_id:
                            #if self.current_scanning_product_id.id in session_lines.filtered(
                                    #lambda x: x.product_id == self.current_scanning_product_id
                                              #and x.session_id.state != 'Cancel'
                                              #and x.location_id == self.current_scanning_location_id and x.inventory_count_id == self.inventory_count_id and x.session_id.id == self._origin.id).mapped(
                                    #'product_id').ids:
                                #raise UserError('Product "{}" is already scanned for the same location '
                                                #'in the same session for this Count.'.format(self.current_scanning_product_id.name))
                        # none_type_product_line_already_exist = self.session_line_ids.search(
                        #     [('location_id', '=', self.current_scanning_location_id.id),
                        #      ('product_id', '=', product.id),
                        #      ('session_id', '=', self._origin.id)])
                        none_type_product_line_already_exist = self.session_line_ids.filtered(
                            lambda x: x.location_id == self.current_scanning_location_id and x.product_id == product)
                        if not none_type_product_line_already_exist:
                            quants = self.env['stock.quant'].sudo().search(
                                [('location_id', '=', self.current_scanning_location_id.id),
                                 ('product_id', '=', product.id)])
                            qty_available = sum([x.quantity for x in quants])
                            # qty_available = product.with_context(
                            #     location=self.current_scanning_location_id.id).qty_available
                            self.write({'session_line_ids': [(0, 0, {
                                'location_id': self.current_scanning_location_id.sudo().id,
                                'product_id': product.id,
                                'date_of_scanning': datetime.now(),
                                'session_id': self._origin.id,
                                'inventory_count_id': self.inventory_count_id.id,
                                'scanned_qty': 1,
                                'theoretical_qty': qty_available
                            })]})
                            # self.env['setu.inventory.count.session.line'].create()
                        else:
                            none_type_product_line_already_exist.write(
                                {'scanned_qty': none_type_product_line_already_exist.scanned_qty + 1})
                            # new_scan_qty = none_type_product_line_already_exist.scanned_qty + 1
                        scanning_done = True
                    if product and product.tracking != 'none':
                        # if not self.current_scanning_location_id:
                        #     return self.messege_return("Warning",
                        #                                "Please scan the Location first.")
                        self.current_scanning_product_id = product
                        new_product = product not in self.session_line_ids.mapped('product_id')
                        if new_product:
                            self.current_scanning_product_id = product
                            self.current_scanning_lot_id = False
                        if self.current_scanning_location_id and self.current_scanning_product_id:
                            # session_line = self.session_line_ids.search(
                            #     [('location_id', '=', self.current_scanning_location_id.id),
                            #      '|', ('lot_id', '=', self.current_scanning_lot_id.id),
                            #      ('serial_number_ids', 'in', self.session_line_ids.serial_number_ids.ids),
                            #      ('product_id', '=', product.id), ('session_id', '=', self._origin.id)])
                            session_line = self.session_line_ids.filtered(
                                lambda x: x.location_id == self.current_scanning_location_id and (
                                        x.lot_id == self.current_scanning_lot_id or x.serial_number_ids in self.session_line_ids.serial_number_ids) and x.product_id == product)
                            if session_line:
                                if session_line.product_scanned:
                                    return self.messege_return("Warning",
                                                               f"{product.display_name} is marked scanned in location {self.current_scanning_location_id.sudo().display_name} for this session. "
                                                               f"Please uncheck the Scanned checkbox.")
                                new_scan_qty = session_line.scanned_qty + 1
                                session_line.write({'scanned_qty': new_scan_qty})
                                scanning_done = True
                            else:
                                vals.update({'location_id': self.current_scanning_location_id.sudo().id,
                                             'product_id': self.current_scanning_product_id.id,
                                             'session_id': self._origin.id,
                                             'inventory_count_id': self.inventory_count_id.id})
                        else:
                            self.current_scanning_product_id = False
                            return self.messege_return("Warning",
                                                       "Please set the current location, then scan the products.")
                    if self.current_scanning_location_id and not product:
                        return self.messege_return("Warning",
                                                   "Product or Location with scanned barcode is not found.")
                if not scanning_done and self.current_scanning_location_id and self.current_scanning_product_id and self.current_scanning_lot_id:
                    if product.tracking in ['lot',
                                            'serial'] and self.current_scanning_lot_id and self.current_scanning_lot_id.sudo().product_id != product:
                        return self.messege_return("Warning",
                                                   "Please select an appropriate lot number as current lot is not belongs to the product you have scanned.")
                    # line_already_exist = self.session_line_ids.search(
                    #     [('location_id', '=', self.current_scanning_location_id.id),
                    #      '|', ('lot_id', '=', self.current_scanning_lot_id.id),
                    #      ('serial_number_ids', 'in', self.session_line_ids.serial_number_ids.ids),
                    #      ('product_id', '=', self.current_scanning_product_id.id),
                    #      ('session_id', '=', self._origin.id)])
                    line_already_exist = False
                    if self.current_scanning_product_id.tracking == 'lot':
                        line_already_exist = self.session_line_ids.filtered(
                            lambda x: x.location_id == self.current_scanning_location_id and (
                                    x.lot_id == self.current_scanning_lot_id) and x.product_id == self.current_scanning_product_id)
                    elif self.current_scanning_product_id.tracking == 'serial':
                        line_already_exist = self.session_line_ids.filtered(
                            lambda
                                x: x.location_id == self.current_scanning_location_id and x.product_id == self.current_scanning_product_id)

                    if line_already_exist and self.current_scanning_product_id.tracking == 'serial':
                        if self.current_scanning_lot_id.id not in line_already_exist.serial_number_ids.ids:
                            count = len(line_already_exist.serial_number_ids) + 1
                            line_already_exist.write({'serial_number_ids': [(4, self.current_scanning_lot_id.id)],
                                                      'scanned_qty': count})
                    if not line_already_exist:
                        if self.current_scanning_product_id.tracking == 'lot':
                            vals.update({'lot_id': lot.id})
                        if self.current_scanning_product_id.tracking == 'serial':
                            vals.update({'serial_number_ids': [(4, lot.id)],
                                         'scanned_qty': 1})
                        if not self.current_scanning_lot_id:
                            return self.messege_return("Warning",
                                                       "Please scan the Lot/Serial Number.")
                        # self.env['setu.inventory.count.session.line'].create(vals)
                        self.write({'session_line_ids': [(0, 0, vals)]})
                # self._cr.commit()
                if not lot and not location and not product:
                    return self.messege_return("Warning",
                                               "Product, Lot/Serial Number or Location with scanned barcode is not found!")
                if not lot and location and product and product.tracking == 'serial':
                    return self.messege_return("Warning",
                                               "Please scan Serial Number of the product.")
                # if self.session_line_ids:
                #     self.session_line_ids._get_theoretical_qty()
            else:
                return self.messege_return("Warning",
                                           "Please Start/Resume the session to continue.")
        else:
            return self.messege_return("Notification",
                                       "Contact your approver to enable the barcode scanning for this session.")
        # self._cr.commit()
        # a=0

    def _compute_user_ids_count(self):
        for rec in self:
            rec.user_ids_count = len(rec.user_ids)

    def _compute_color(self):
        for rec in self:
            if rec.state == 'In Progress':
                if rec.current_state in ('Start', 'Resume'):
                    rec.color = 2
                elif rec.current_state == 'Pause':
                    rec.color = 3
            if rec.session_ids:
                rec.color = 1
            else:
                rec.color = 0

    def _compute_time_taken(self):
        for rec in self:
            if rec.state in ('In Progress', 'Done', 'Submitted'):
                session_details = self.env['inventory.session.details'].search([('session_id', '=', rec.id)])
                duration_in_seconds = sum(session_details.mapped('duration_seconds'))
                whole_minutes = int(duration_in_seconds / 60)
                seconds = duration_in_seconds % 60
                hours = int(whole_minutes / 60)
                minutes = whole_minutes % 60
                time_stamp = str(hours).zfill(2) + ':' + str(minutes).zfill(2) + ':' + str(seconds).zfill(2)
                rec.time_taken = time_stamp
            else:
                rec.time_taken = ''

    def _compute_rejected_lines_count(self):
        for rec in self:
            rejected_lines = rec.session_line_ids.filtered(lambda l: l.state == 'Reject')
            rec.rejected_lines_count = len(rejected_lines) if rejected_lines else 0

    def _compute_child_session_ids(self):
        for rec in self:
            rec.count_child_session_ids = len(self.session_ids)

    def _compute_open_session_again(self):
        for session in self:
            if session.session_line_ids.filtered(lambda s: s.state == 'Reject'):
                session.open_session_again = True
            else:
                session.open_session_again = False

    def create_re_session(self):
        return {
            'name': 'Rejected Lines Found!!!',
            'view_mode': 'form',
            'view_id': self.sudo().env.ref(
                'setu_inventory_count_management_18.inventory_count_session_re_create_form_view').id,
            'res_model': 'setu.inventory.session.validate.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def open_new_session(self):
        if self.session_line_ids.filtered(lambda s: s.state == 'Pending Review'):
            raise ValidationError(
                _('Please check and set the state in all session lines of this session to open this session again.'))
        rejected_lines = self.session_line_ids.filtered(lambda s: s.state == 'Reject')
        new_session = self.env['setu.inventory.count.session'].create({
            'inventory_count_id': self.inventory_count_id.id,
            'location_id': self.location_id.id,
            'warehouse_id': self.warehouse_id.id,
            'use_barcode_scanner': self.use_barcode_scanner
        })
        for line in rejected_lines:
            new_session_line = line.copy()
            new_session_line.session_id = new_session
            new_session_line.scanned_qty = 0
            new_session_line.serial_number_ids = False
        new_session.session_id = self
        new_session.user_ids = self.user_ids

    def _compute_session_history_count(self):
        for rec in self:
            if rec.current_state == 'Created':
                rec.session_history_count = 0
            else:
                session_details = self.env['inventory.session.details'].search([('session_id', '=', self.id)])
                rec.session_history_count = len(session_details)

    def action_view_session_history(self):
        return {
            'name': 'History',
            'view_mode': 'tree',
            'view_id': self.sudo().env.ref('setu_inventory_count_management_18.inventory_session_details_tree_view').id,
            'res_model': 'inventory.session.details',
            'type': 'ir.actions.act_window',
            'domain': [('session_id', '=', self.id)]
        }

    @api.depends('session_line_ids.product_scanned')
    def _compute_scanned_products(self):
        for session in self:
            lines = session.session_line_ids
            session.total_products = len(lines.mapped('product_id'))
            product_dict = {product_id.id: [0, 0] for product_id in lines.mapped('product_id')}
            for line in lines:
                if product_dict.get(line.product_id.id, False):
                    product_dict[line.product_id.id][0] += 1
                    if line.product_scanned:
                        product_dict[line.product_id.id][1] += 1
            total_scanned_products = 0
            for product, scan_value in product_dict.items():
                if lines.mapped('product_id') and scan_value[0] == scan_value[1]:
                    total_scanned_products += 1
            to_be_scanned = session.total_products - total_scanned_products
            session.total_scanned_products = total_scanned_products
            session.to_be_scanned = to_be_scanned

    def write(self, vals):
        res = super(InventoryCountSession, self).write(vals)
        if vals.get('name'):
            raise ValidationError(_("You cannot change 'Name' of the Session"))
        if vals.get('inventory_count_id'):
            raise ValidationError(_("You cannot change the Reference Inventory Count of the Session"))
        else:
            return res

    @api.model
    def create(self, vals_list):
        seq = self.env['ir.sequence'].next_by_code('setu.inventory.count.session.seq')
        vals_list.update({
            'name': seq
        })
        return super(InventoryCountSession, self).create(vals_list)

    def start(self):
        if self.state == 'Cancel':
            raise ValidationError(_("Administrator has already Cancelled the Session."))
        if self.current_state == 'Start':
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        running_session = self.sudo().search(
            [('user_ids', '=', self.user_ids.ids), ('current_state', 'in', ['Start', 'Resume'])])
        if running_session:
            for session in running_session:
                if len(session.user_ids) == 1 and len(self.user_ids) == 1:
                    raise ValidationError(_("Another session for the same User is Running. "
                                            "You cannot Start/Resume more than one session at a time."))
        self.current_state = 'Start'
        date_today = datetime.now()
        self.session_start_date = date_today
        self.sudo().env['inventory.session.details'].create({
            'session_id': self.id,
            'start_date': date_today
        })
        self.state = 'In Progress'
        self.sudo().inventory_count_id.state = 'In Progress'
        if not self.session_id:
            # for line in self.session_line_ids:
            #     line.qty_in_stock = line.theoretical_qty

            for line in self.inventory_count_id.line_ids:
                line.sudo().qty_in_stock = line.theoretical_qty

    def pause(self):
        if self.current_state == 'Pause':
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        if self.current_state == 'End':
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
            # raise ValidationError(_("The session is already submitted."))
        else:
            self.current_state = 'Pause'
            unfinished_history = self.env['inventory.session.details'].search(
                [('session_id', '=', self.id), ('end_date', '=', False)])
            date_today = datetime.now()
            unfinished_history.end_date = date_today

    def resume(self):
        if self.current_state in ['Resume', 'End']:
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        running_session = self.sudo().search(
            [('user_ids', '=', self.user_ids.ids), ('current_state', 'in', ['Start', 'Resume'])])
        if running_session:
            for session in running_session:
                if len(session.user_ids) == 1 and len(self.user_ids) == 1:
                    raise ValidationError(_("Another session for the same User is Running. "
                                            "You cannot Start/Resume more than one session at a time."))
        self.current_state = 'Resume'
        date_today = datetime.now()
        self.env['inventory.session.details'].create({
            'session_id': self.id,
            'start_date': date_today
        })

    def end(self):
        if self.current_state in ['End']:
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        self.current_state = 'End'
        date_today = datetime.now()
        # self.session_end_date = date_today
        unfinished_history = self.env['inventory.session.details'].search(
            [('session_id', '=', self.id), ('end_date', '=', False)])
        unfinished_history.end_date = date_today

    def submit(self):
        self.end()
        self.current_scanning_location_id = False
        self.current_scanning_product_id = False
        self.current_scanning_lot_id = False
        date_today = datetime.now()
        self.session_submit_date = date_today
        if self.is_multi_session:
            self.validate_session()
        else:
            self.state = 'Submitted'
        session_lines = self.inventory_count_id.session_ids.mapped('session_line_ids')
        not_found_serial = {}
        for line in self.session_line_ids:
            line.product_scanned = True
            if line.tracking == 'serial':
                same_found = session_lines.filtered(lambda x: x.product_id == line.product_id
                                                and x.id != line.id
                                                and x.session_id.state != 'Cancel'
                                                and x.state != 'Reject'
                                                and (x.location_id != line.location_id or x.location_id == line.location_id)
                                                and any(b in x.serial_number_ids.ids for b in line.serial_number_ids.ids)
                                                and x.session_id.inventory_count_id == line.session_id.inventory_count_id)
                if same_found:
                    same_found = list(set(same_found.mapped('serial_number_ids').ids) & set(line.serial_number_ids.ids))
                    same_found = self.env['stock.lot'].sudo().browse(same_found)
                    same_found_str = ", ".join(same_found.mapped('name'))
                    raise UserError('Serial Number "{}" is/are scanned multiple times in same or in an another '
                                    'session for this Count.'.format(same_found_str))

                count_line_exists_already = self.inventory_count_id.line_ids.filtered(
                    lambda l: l.location_id.id == line.location_id.id and l.product_id.id == line.product_id.id)
                new_line = False

                if count_line_exists_already:
                    count_line_exists_already.write(
                        {'serial_number_ids': [(6, 0, line.serial_number_ids.ids)] if self.session_id else line._get_serial_number_ids(line),
                         'not_found_serial_number_ids': [],
                         'theoretical_qty': line._get_theoretical_qty(count_line_exists_already),
                         'qty_in_stock': line._get_theoretical_qty(count_line_exists_already),
                         'counted_qty': line.scanned_qty if self.session_id else line._get_counted_qty(line)})
                else:
                    new_line = self.create_new_count_line(line)

                if new_line:
                    found_lots = new_line.serial_number_ids + count_line_exists_already.serial_number_ids
                else:
                    found_lots = count_line_exists_already.serial_number_ids
                quants = self.env['stock.quant'].sudo().search(
                    [('location_id', '=', line.location_id.id),
                     ('quantity', '=', 1),
                     ('product_id', '=', line.product_id.id)])
                total_lots = quants.mapped('lot_id')
                not_found_lot_ids = total_lots - found_lots

                if not_found_lot_ids:
                    if not not_found_serial.get((line.product_id,line.location_id), False):
                        not_found_serial.update({(line.product_id,line.location_id): not_found_lot_ids})
                    else:
                        dict_lots = not_found_serial.get((line.product_id,line.location_id))
                        if dict_lots:
                            dict_lots -= found_lots
                            not_found_serial.update({(line.product_id,line.location_id): dict_lots})

            elif line.tracking == 'none':

                same_found = session_lines.filtered(lambda x: x.product_id == line.product_id
                                                              and x.id != line.id
                                                              and x.session_id.state != 'Cancel'
                                                              and (x.location_id == line.location_id)
                                                              and x.session_id.id == line.session_id.id
                                                              and x.session_id.inventory_count_id == line.session_id.inventory_count_id)
                if same_found:
                    raise UserError('Product "{}" is scanned multiple times for the same location  in same session for this Count.'.format(line.product_id.name))


                count_line_exists_already = self.inventory_count_id.line_ids.filtered(
                    lambda l: l.location_id.id == line.location_id.id and l.product_id.id == line.product_id.id)
                if self.session_id:
                    if count_line_exists_already:
                        count_line_exists_already.write(
                            {'theoretical_qty': line._get_theoretical_qty(count_line_exists_already),
                             'qty_in_stock': line._get_theoretical_qty(count_line_exists_already),
                             'counted_qty': line.scanned_qty})
                    else:
                        self.create_new_count_line(line)
                else:
                    if not count_line_exists_already:
                        self.create_new_count_line(line)
                    else:
                        count_line_exists_already.write(
                            {'theoretical_qty': line._get_theoretical_qty(count_line_exists_already),
                             'qty_in_stock': line._get_theoretical_qty(count_line_exists_already),
                             'counted_qty': line._get_counted_qty(line, count_line_exists_already)})
            elif line.tracking == 'lot':
                same_found = session_lines.filtered(lambda x: x.product_id == line.product_id
                                                             and x.id != line.id
                                                             and x.lot_id.id == line.lot_id.id
                                                             and x.session_id.id == line.session_id.id
                                                             and x.location_id.id == line.location_id.id)

                if same_found:
                    same_found = line.lot_id#list(set(same_found.mapped('lot_id').ids) & set(line.lot_id.ids))
                    # same_found = self.env['stock.lot'].sudo().browse(same_found)
                    same_found_str = ", ".join(same_found.mapped('name'))
                    raise UserError('Lot Number "{}" is scanned multiple times for the same '
                                    'location in same session for this Count.'.format(same_found_str))

                count_line_exists_already = self.inventory_count_id.line_ids.filtered(
                                            lambda l: l.location_id.id == line.location_id.id
                                                   and l.product_id.id == line.product_id.id
                                                   and l.lot_id.id == line.lot_id.id)
                if count_line_exists_already:
                    count_line_exists_already.write(
                        {'theoretical_qty': line._get_theoretical_qty(count_line_exists_already),
                         'qty_in_stock': line._get_theoretical_qty(count_line_exists_already),
                         'is_system_generated': False,
                         'counted_qty': line.scanned_qty if self.session_id else
                         line._get_counted_qty(line,count_line_exists_already)})
                else:
                    self.create_new_count_line(line)

                locations = self.inventory_count_id.session_ids.session_line_ids.filtered(
                                                            lambda x: x.lot_id == line.lot_id).mapped('location_id')

                domain = [('location_id', 'child_of', line.session_id.location_id.id),
                          ('location_id.usage', '=', 'internal'),
                          ('lot_id', '=', line.lot_id.id),('product_id', '=', line.product_id.id),
                          ('location_id', 'not in', locations.ids if locations else [])]

                # if line.theoretical_qty == 0:
                lot_quants = self.env['stock.quant'].sudo().search(domain)
                for quant in lot_quants:
                    if not self.inventory_count_id.count_id:
                        already_existing_line = self.inventory_count_id.line_ids.filtered(lambda l: l.product_id.id == quant.product_id.id and
                                              l.lot_id.id == quant.lot_id.id and l.location_id.id == quant.location_id.id)
                    else:
                        counts = self.inventory_count_id.get_all_counts()
                        count_ids = self.env['setu.stock.inventory.count'].sudo().browse(counts)
                        already_existing_line = count_ids.line_ids.filtered(
                            lambda l: l.product_id.id == quant.product_id.id and
                                      l.lot_id.id == quant.lot_id.id and l.location_id.id == quant.location_id.id)
                    if not already_existing_line:
                        self.env['setu.stock.inventory.count.line'].create({
                            'inventory_count_id': self.inventory_count_id.id,
                            'product_id': line.product_id.id,
                            'tracking': line.tracking,
                            'lot_id': quant.lot_id.id,
                            'location_id': quant.location_id.id,
                            'is_system_generated': True,
                            'theoretical_qty': line._get_theoretical_qty(location=quant.location_id),
                            'qty_in_stock': line._get_theoretical_qty(location=quant.location_id),
                            'counted_qty': 0,
                            'user_calculation_mistake': line.user_calculation_mistake
                        })
                    if self.type == 'Single Session':
                        self.write({'session_line_ids': [(0, 0, {'product_id': line.product_id.id,
                                                                  'tracking': line.tracking,
                                                                  'lot_id': quant.lot_id.id,
                                                                  'location_id': quant.location_id.id,
                                                                  'is_system_generated': True,
                                                                  'theoretical_qty': line._get_theoretical_qty(
                                                                      location=quant.location_id),
                                                                  'scanned_qty': 0})]})
        current_session_serial_ids = self.session_line_ids.serial_number_ids
        if current_session_serial_ids:
            found_serial_in_count = self.inventory_count_id.line_ids.filtered(lambda x: any(b in x.not_found_serial_number_ids.ids for b in current_session_serial_ids.ids))
            for count_line in found_serial_in_count:
                need_to_link = set(count_line.not_found_serial_number_ids.ids) - set(current_session_serial_ids.ids)
                count_line.write({'not_found_serial_number_ids': [(6, 0, need_to_link)]})

        if not_found_serial:
            added_serial_number_ids = self.inventory_count_id.line_ids.filtered(
                lambda x: x.product_id.tracking == 'serial').serial_number_ids
            for key, value in not_found_serial.items():
                final_lots = value - added_serial_number_ids
                count_line_exists_already = self.inventory_count_id.line_ids.filtered(
                    lambda l: l.location_id.id == key[1].id and l.product_id.id == key[0].id)
                if count_line_exists_already and final_lots:
                    count_line_exists_already.write({'not_found_serial_number_ids': [(6, 0, final_lots.ids)],
                                                     'is_system_generated': True})
                if self.type == 'Single Session':
                    session_line_exists_already = self.session_line_ids.filtered(
                        lambda l: l.location_id.id == key[1].id and l.product_id.id == key[0].id)
                    if session_line_exists_already and final_lots:
                        session_line_exists_already.write({'not_found_serial_number_ids': [(6, 0, final_lots.ids)],
                                                           'is_system_generated': True
                                                           })

    def _create_new_line(self, line):
        new_line = self.env['setu.stock.inventory.count.line'].create({
            'inventory_count_id': self.inventory_count_id.id,
            'product_id': line.product_id.id,
            'tracking': line.tracking,
            'serial_number_ids': [(6, 0, line.serial_number_ids.ids)] if line.serial_number_ids else False,
            'lot_id': line.lot_id.id,
            'location_id': line.location_id.id,
            'theoretical_qty': 0,
            'qty_in_stock': 0,
            'counted_qty': 0,
            'user_calculation_mistake': line.user_calculation_mistake
        })
        return new_line

    def create_new_count_line(self, line):
        new_count_line = self._create_new_line(line)
        qty = line.scanned_qty
        if line.tracking == 'lot':
            moves = self.env['stock.move.line'].sudo().search([('state', '=', 'done'),
                                                       ('product_id', '=', line.product_id.id),
                                                       ('move_id.picking_type_id.code', '=', 'outgoing'),
                                                       ('lot_id', '=', line.lot_id.id),
                                                       ('date', '>=', line.date_of_scanning)])
            # moves = self.env['stock.move.line'].search([]).filtered(
            #     lambda
            #         m: m.state == 'done' and m.product_id.id == line.product_id.id and m.move_id.picking_type_id.code == 'outgoing' and m.lot_id.id == line.lot_id.id and m.date >= line.date_of_scanning)
        elif line.tracking == 'serial':
            moves = self.env['stock.move.line'].sudo().search([('state', '=', 'done'),
                                                               ('product_id', '=', line.product_id.id),
                                                               ('move_id.picking_type_id.code', '=', 'outgoing'),
                                                               ('lot_id.id', 'in', line.serial_number_ids.ids),
                                                               ('date', '>=', line.date_of_scanning)])
            # moves = self.env['stock.move.line'].search([]).filtered(
            #     lambda
            #         m: m.state == 'done' and m.product_id.id == line.product_id.id and m.move_id.picking_type_id.code == 'outgoing' and m.lot_id.id in line.serial_number_ids.ids and m.date >= line.date_of_scanning)
        elif line.tracking == 'none':
            moves = self.env['stock.move.line'].sudo().search([('state', '=', 'done'),
                                                               ('product_id', '=', line.product_id.id),
                                                               ('move_id.picking_type_id.code', '=', 'outgoing'),
                                                               ('date', '>=', line.date_of_scanning)])
            # moves = self.env['stock.move.line'].search([]).filtered(
            #     lambda
            #         m: m.state == 'done' and m.product_id.id == line.product_id.id and m.move_id.picking_type_id.code == 'outgoing' and m.date >= line.date_of_scanning)
        if qty > sum([x.qty_done for x in moves]):
            qty -= sum([x.qty_done for x in moves])
        else:
            qty += 0
        moves.write({'count_id': line.session_id.inventory_count_id.id})
        theoretical_qty = line._get_theoretical_qty(new_count_line)
        new_count_line.write({
            'theoretical_qty': theoretical_qty,
            'qty_in_stock': theoretical_qty,
            'counted_qty': qty
        })
        return new_count_line
        # self.env['setu.stock.inventory.count.line'].create({
        #     'inventory_count_id': self.inventory_count_id.id,
        #     'product_id': line.product_id.id,
        #     'tracking': line.tracking,
        #     'serial_number_ids': [(6, 0, line.serial_number_ids.ids)] if line.serial_number_ids else False,
        #     'lot_id': line.lot_id.id,
        #     'location_id': line.location_id.id,
        #     'theoretical_qty': line.theoretical_qty,
        #     'qty_in_stock': line.theoretical_qty,
        #     'counted_qty': line.scanned_qty,
        #     'user_calculation_mistake': line.user_calculation_mistake
        # })

    def approve_all_lines(self):
        wiz = self.env['inventory.warning.message.wizard'].create({
            'message': "Are you sure that you want to Approve all session lines? (Even rejected lines will also be approved)"
        })
        return {
            'name': 'Warning!!!',
            'view_mode': 'form',
            'view_id': self.sudo().env.ref(
                'setu_inventory_count_management_18.inventory_warning_message_approve_wizard_form_view').id,
            'res_model': 'inventory.warning.message.wizard',
            'type': 'ir.actions.act_window',
            'res_id': wiz.id,
            'target': 'new'
        }

    def action_open_child_sessions(self):
        sessions_to_open = self.session_ids
        action = \
            self.sudo().env.ref('setu_inventory_count_management_18.inventory_count_session_act_window').read()[0]
        if len(sessions_to_open) > 1:
            action['domain'] = [('id', 'in', sessions_to_open.ids)]
        elif len(sessions_to_open) == 1:
            action['views'] = [
                (self.sudo().env.ref('setu_inventory_count_management_18.inventory_count_session_form_view').id, 'form')]
            action['res_id'] = sessions_to_open.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def _set_calculation_mistake_value(self, line, parent, count_line, real_quantity=False):
        if type(real_quantity) == bool and not real_quantity:
            real_quantity = line.scanned_qty
        if parent:
            tracking = line.product_id.tracking
            if tracking == 'lot':
                parent_session_line = parent.session_line_ids.filtered(
                    lambda l: l.product_id == line.product_id and l.location_id == line.location_id
                              and l.lot_id == line.lot_id)
            elif tracking == 'serial':
                parent_session_line = parent.session_line_ids.filtered(
                    lambda l: l.product_id == line.product_id and l.location_id == line.location_id
                              and any(b in l.serial_number_ids.ids for b in line.serial_number_ids.ids))
            else:
                parent_session_line = parent.session_line_ids.filtered(
                    lambda l: l.product_id == line.product_id and l.location_id == line.location_id)

            # parent_session_line = parent.session_line_ids.filtered(
            #     lambda l: l.product_id == line.product_id and l.location_id == line.location_id)
            if parent_session_line:
                if real_quantity != parent_session_line.scanned_qty:
                    parent_session_line.user_calculation_mistake = True
                else:
                    parent_session_line.user_calculation_mistake = False

                self._set_calculation_mistake_value(parent_session_line, parent.session_id, count_line, real_quantity)
        else:
            if 0 <= real_quantity != line.scanned_qty:
                line.user_calculation_mistake = True
                line.inventory_count_line_id.user_calculation_mistake = True
            else:
                line.user_calculation_mistake = False

    # def set_user_calculation_mistake_in_count_lines(self):
    #     count_line_ids = self.inventory_count_id.line_ids
    #     for line in count_line_ids:
    #         session_line_ids = line.session_line_ids.filtered(lambda l: l.session_id.state != 'Cancel')
    #         if session_line_ids:
    #             lines_with_user_mistake = session_line_ids.filtered(lambda l: l.user_calculation_mistake)
    #             if lines_with_user_mistake:
    #                 line.user_calculation_mistake = True

    def _validate_session(self):
        if self.state == 'Done':
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        session_lines = self.session_line_ids.filtered(lambda x:x.product_id)
        # approved_lines = session_lines.filtered(lambda l: l.state == 'Approve')
        parent = self.session_id
        for line in session_lines:
            tracking = line.product_id.tracking
            if tracking == 'lot':
                count_line = self.inventory_count_id.line_ids.filtered(
                    lambda l: l.product_id == line.product_id and l.location_id == line.location_id and l.lot_id == line.lot_id)
            elif tracking == 'serial':
                count_line = self.inventory_count_id.line_ids.filtered(
                    lambda l: l.product_id == line.product_id and l.location_id == line.location_id
                              and any(b in l.serial_number_ids.ids for b in line.serial_number_ids.ids))
            else:
                count_line = self.inventory_count_id.line_ids.filtered(
                    lambda l: l.product_id == line.product_id and l.location_id == line.location_id)

            # count_line = self.inventory_count_id.line_ids.filtered(
            #     lambda l: l.product_id == line.product_id and l.location_id == line.location_id)

            self._set_calculation_mistake_value(line, parent, count_line)
        self.state = 'Done'
        rejected_lines = self.session_line_ids.filtered(lambda line: line.state == 'Reject')
        for line in rejected_lines:
            self.env['setu.stock.inventory.count.line'].search(
                [('inventory_count_id', '=', self.inventory_count_id.id), ('product_id', '=', line.product_id.id),
                 ('location_id', '=', line.location_id.id)
                 ]).unlink()

    def validate_session(self):
        session_lines = self.session_line_ids
        if self.type == 'Single Session':
            if session_lines.filtered(lambda l: l.state == 'Pending Review'):
                raise ValidationError(_('There are some lines with Pending Review. Please check and set the state '
                                                'in all session lines of this session to validate this session.'))
            system_generated_lines = session_lines.filtered(lambda l: l.state == 'Approve' and l.is_system_generated)
            for sg_line in system_generated_lines:
                count_line = self.inventory_count_id.line_ids.filtered(
                                                        lambda line: line.product_id.id == sg_line.product_id.id
                                                                     and line.is_system_generated
                                                                     and line.location_id.id == sg_line.location_id.id
                                                                     and line.lot_id == sg_line.lot_id)
                if count_line:
                    count_line.counted_qty = sg_line.scanned_qty
                    if count_line.product_id.tracking == 'serial':
                        count_line.write({
                        'serial_number_ids': [(6, 0, count_line.serial_number_ids.ids + sg_line.serial_number_ids.ids)],
                        'not_found_serial_number_ids': [(6, 0, list(set(count_line.not_found_serial_number_ids.ids) - set(sg_line.serial_number_ids.ids)))]
                        })
                    # count_line._compute_is_discrepancy_found()

        rejected_lines = session_lines.filtered(lambda l: l.state == 'Reject')

        if rejected_lines and self.re_open_session_bool:
            return {
                'name': 'Rejected Lines Found!!!',
                'view_mode': 'form',
                'view_id': self.sudo().env.ref(
                    'setu_inventory_count_management_18.inventory_count_session_validate_form_view').id,
                'res_model': 'setu.inventory.session.validate.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
        else:
            self._validate_session()

    def reject_all_lines(self):
        wiz = self.env['inventory.warning.message.wizard'].create({
            'message': "Are you sure that you want to Reject all session lines? (Even approved lines will also be rejected)"
        })
        return {
            'name': 'Warning!!!',
            'view_mode': 'form',
            'view_id': self.sudo().env.ref(
                'setu_inventory_count_management_18.inventory_warning_message_reject_wizard_form_view').id,
            'res_model': 'inventory.warning.message.wizard',
            'type': 'ir.actions.act_window',
            'res_id': wiz.id,
            'target': 'new'
        }

    def cancel_session(self):
        if self.state not in ('Submitted', 'Done'):
            self.state = 'Cancel'
            cousin_sessions = self.sudo().search(
                [('inventory_count_id', '=', self.inventory_count_id.id), ('state', '!=', 'Cancel')])
            if not cousin_sessions:
                self.inventory_count_id.state = 'Draft'

        else:
            raise ValidationError(_('Cannot cancel session in Done or Submitted stage.'))

    def _compute_re_open_session(self):
        for rec in self:
            if self.state in ('Submitted', 'Done') and self.rejected_lines_count > 0:
                if rec.session_ids and rec.session_ids.filtered(lambda s: s.state != 'Cancel'):
                    rec.re_open_session_bool = False
                else:
                    rec.re_open_session_bool = True
            else:
                rec.re_open_session_bool = False

    def unlink(self):
        from_count = self.env.context.get('from_count', False)
        if from_count:
            return super(InventoryCountSession, self).unlink()
        raise ValidationError(
            _('You cannot delete Inventory Count Sessions. To delete Inventory Count Sessions, delete their Inventory Count. Deleting the Inventory Count will delete all its sessions.'))

    def return_product_action(self, ids, products_type):
        action = {
            'name': self.name + ' --> ' + products_type,
            'view_mode': 'tree,form',
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', ids)]
        }
        # if len(ids) == 1:
        #     action.update({
        #         'view_mode': 'form',
        #         'domain': [],
        #         'res_id': ids[0]
        #     })

        return action

    def open_total_products(self):
        ids = self.session_line_ids.mapped('product_id').ids
        return self.return_product_action(ids, 'All Products')

    def get_product_dict(self):
        lines = self.session_line_ids
        product_dict = {product_id.id: [0, 0] for product_id in lines.mapped('product_id')}
        for line in lines:
            product_dict[line.product_id.id][0] += 1
            if line.product_scanned:
                product_dict[line.product_id.id][1] += 1
        return product_dict

    def open_products_to_be_scanned(self):
        ids = set()
        product_dict = self.get_product_dict()
        for product, scan_value in product_dict.items():
            if scan_value[0] != scan_value[1]:
                ids.add(product)
        return self.return_product_action(list(ids), 'Products To Be Scanned')

    def open_scanned_products(self):
        ids = set()
        product_dict = self.get_product_dict()
        for product, scan_value in product_dict.items():
            if scan_value[0] == scan_value[1]:
                ids.add(product)
        return self.return_product_action(list(ids), 'Scanned Products')

    def open_location(self):
        self._compute_time_taken()
        loc_id = self.location_id.id
        return {
            'name': self.name + ' --> ' + 'Location',
            'view_mode': 'form',
            'res_model': 'stock.location',
            'type': 'ir.actions.act_window',
            'res_id': loc_id
        }

    def open_inventory_count(self):
        count_id = self.inventory_count_id.id
        return {
            'name': self.name + ' --> ' + 'Inventory Count',
            'view_mode': 'form',
            'views': [(self.sudo().env.ref('setu_inventory_count_management_18.setu_stock_inventory_count_form_view').id,
                       'form')],
            'res_model': 'setu.stock.inventory.count',
            'type': 'ir.actions.act_window',
            'res_id': count_id
        }

    def open_user(self):
        users = self.user_ids.ids
        action = {
            'name': self.name + ' --> ' + 'Users',
            'view_mode': 'tree,form',
            'res_model': 'res.users',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', users)]
        }
        # if len(users) > 1:
        # return action
        # action['view_mode'] = 'form'
        # action['res_id'] = users[0]
        # action['domain'] = []
        return action

    def open_approver_id(self):
        action = self.open_user()
        action.update({
            'domain': [('id', 'in', [self.approver_id.id])]
        })
        return action
