from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_is_zero


# ACTIVE_STOCK_INVENTORY = []


class StockMove(models.Model):
    _inherit = 'stock.move'

    inventory_adj_id = fields.Many2one(
        comodel_name="setu.stock.inventory",
        string="Inventory Adjustment"
    )

    inventory_count_id = fields.Many2one(
        comodel_name="setu.stock.inventory.count",
        string="Inventory Count"
    )

    @api.model_create_multi
    def create(self, vals_list):
        inventory_adj_id = self._context.get('adj_context', False)
        if inventory_adj_id:
            inventory_adj_id = self.env['setu.stock.inventory'].sudo().browse(inventory_adj_id)
            for vals in vals_list:
                vals.update({'inventory_adj_id': inventory_adj_id.id,
                             'inventory_count_id': inventory_adj_id.inventory_count_id.id,
                             'origin': inventory_adj_id.name})
        return super().create(vals_list)

    # def create(self, vals):
    #     res = super(StockMove, self).create(vals)
    #
    #     adj = ACTIVE_STOCK_INVENTORY and ACTIVE_STOCK_INVENTORY[0]
    #     if adj:
    #         adj_id = self.sudo().env['setu.stock.inventory'].browse(adj)
    #         res.inventory_adj_id = adj_id
    #         res.origin = adj_id.name
    #     return res

    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        self.ensure_one()
        inventory_count_id = self.sudo().inventory_adj_id and self.sudo().inventory_adj_id.inventory_count_id or False
        if inventory_count_id and inventory_count_id.name:
            svl = self.env['stock.valuation.layer'].sudo().browse(svl_id)
            description = 'Inventory Adjustment - ' + inventory_count_id.name + ' - ' + svl.product_id.name
        res = super()._prepare_account_move_vals(credit_account_id=credit_account_id,
                                                 debit_account_id=debit_account_id,
                                                 journal_id=journal_id,
                                                 qty=qty,
                                                 description=description,
                                                 svl_id=svl_id,
                                                 cost=cost)
        return res


class StockInventoryLine(models.Model):
    _name = 'setu.stock.inventory.line'
    _description = 'Setu Stock Inventory Line'

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Owner",
        check_company=True
    )
    package_id = fields.Many2one( 
        comodel_name="stock.quant.package",
        string="Package",
        index=True,
        check_company=True,
        domain="[('location_id', '=', location_id)]",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product"
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Product Unit of Measure",
        required=True,
        readonly=True
    )
    theoretical_qty = fields.Float(
        string="Theoretical QTY"
    )
    product_qty = fields.Float(
        string="Counted QTY"
    )
    inventory_id = fields.Many2one(
        comodel_name="setu.stock.inventory",
        string="Inventory"
    )
    quant_id = fields.Many2one(
        comodel_name="stock.quant",
        string="Quant"
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Location"
    )
    prod_lot_id = fields.Many2one(
        comodel_name="stock.lot",
        string="Lot/Serial Number",
        check_company=True,
        domain="[('product_id','=',product_id), ('company_id', '=', company_id)]"
    )
    serial_number_ids = fields.Many2many('stock.lot', 'setu_stock_inventory_line_stock_lot_rel', 'setu_stock_inventory_line_id', 'stock_lot_id', string="Serial Numbers")
    not_found_serial_number_ids = fields.Many2many('stock.lot', 'setu_not_found_line_stock_lot_rel', 'inventory_line_id', 'lot_id', string="Missing Serial Numbers")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        related="inventory_id.company_id",
        index=True,
        readonly=True,
        store=True
    )
    # new_serial_count = fields.Float('New Serial QTY')
    new_serial_number_ids = fields.Many2many('stock.lot', 'setu_new_serial_stock_lot_rel', 'inventory_line_id', 'lot_id',
                                                   string="New Serial Numbers")
    difference_qty = fields.Float(
        string="Difference",
        compute="_compute_difference",
        help="Indicates the gap between the product's theoretical quantity and its newest quantity.",
        readonly=True,
        digits="Product Unit of Measure",
        search="_search_difference_qty"
    )

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        for rec in self:
            if rec.product_id and rec.product_id.tracking == 'serial' and rec.product_qty > 1:
                raise ValidationError(_("Serial number product should not have more than 1 quantity."))

    @api.depends('product_qty', 'theoretical_qty')
    def _compute_difference(self):
        for line in self:
            # if line.product_id.tracking == 'serial':
            #     # if (line.new_serial_number_ids and not line.not_found_serial_number_ids) or (not line.serial_number_ids and line.not_found_serial_number_ids) or (line.serial_number_ids and line.not_found_serial_number_ids and not line.new_serial_number_ids):
            #     #     difference = line.product_qty - line.theoretical_qty
            #     if (line.new_serial_number_ids and line.not_found_serial_number_ids):
            #         difference = line.product_qty - len(line.new_serial_number_ids) - line.theoretical_qty
            #     else:
            #         difference = line.product_qty - line.theoretical_qty
            # else:
            if line.theoretical_qty < 0:
                difference = line.product_qty
            else:
                difference = line.product_qty - line.theoretical_qty
            line.difference_qty = difference

    def _get_virtual_location(self):
        return self.product_id.with_company(self.company_id).property_stock_inventory

    def _generate_moves(self):
        vals_list = []
        sn_vals = []
        vals = {}
        for line in self:
            virtual_location = line._get_virtual_location()
            rounding = line.product_id.uom_id.rounding
            if float_is_zero(line.difference_qty, precision_rounding=rounding):
                continue
            if line.difference_qty > 0:  # found more than expected
                if line.serial_number_ids:
                    for serial_number in line.serial_number_ids:
                        serial_number_vals = line._get_move_values(1, virtual_location.id,
                                                                                     line.location_id.id,
                                                                                     False, serial_number)
                        sn_vals.append(serial_number_vals)
                else:
                    vals = line._get_move_values(line.difference_qty, virtual_location.id, line.location_id.id, False, False)
            else:
                vals = line._get_move_values(abs(line.difference_qty), line.location_id.id, virtual_location.id, True, False)
            if sn_vals:
                vals_list.extend(sn_vals)
            if vals:
                vals_list.append(vals)
                vals = {}
        return self.env['stock.move'].create(vals_list)

    def _get_move_values(self, qty, location_id, location_dest_id, out, serial_number=False):
        self.ensure_one()
        return {
            'name': _('INV:') + (self.inventory_id.name or ''),
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': qty,
            'date': self.inventory_id.date,
            'company_id': self.inventory_id.company_id.id,
            'inventory_adj_id': self.inventory_id.id,
            'state': 'confirmed',
            'restrict_partner_id': self.partner_id.id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'lot_id': self.prod_lot_id.id if self.product_id.tracking == 'lot' and self.prod_lot_id else serial_number.id if self.product_id.tracking == 'serial' and serial_number else False,
                'reserved_uom_qty': 0,  # bypass reservation here
                'product_uom_id': self.product_uom_id.id,
                'qty_done': qty,
                'package_id': out and self.package_id.id or False,
                'result_package_id': (not out) and self.package_id.id or False,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'owner_id': self.partner_id.id,
            })]
        }

    # def create(self, vals):
        # if vals:
        #     product_location_pair = list(
        #         map(lambda line: {'product_id': line['product_id'], 'location_id': line['location_id']}, vals))
        #     products = self.env['product.product'].sudo().browse(product_ids)
        #     location = self.env['stock.location'].sudo().browse(vals['location_id'])
        #     for pair in product_location_pair:
        #         duplicate_record = self.sudo().search(
        #             [('product_id', 'in', product_ids), ('inventory_id.state', 'not in', ('cancel', 'done')),
        #              ('location_id', '=', vals['location_id'])])
        #     if duplicate_record:
        #         raise ValidationError(
        #             "You cannot have two inventory adjustments In Progress with the same product "
        #             "(%s) and same location (%s)."
        #             "Please validate the first inventory adjustment with this product before creating another one." % (
        #                 ", ".join(products.mapped('display_name')), location.display_name))

        # res = super(StockInventoryLine, self).create(vals)

        # for line in res:
        #     quant = self.env['stock.quant'].sudo().search(
        #         [('location_id', '=', line.location_id.id), ('product_id', '=', line.product_id.id)], limit=1)
        #     if quant:
        #         quant.inventory_quantity = line.product_qty
        #     else:
        #         quant = self.env['stock.quant'].sudo().create(
        #             {'product_id': line.product_id.id, 'location_id': line.location_id.id,
        #              'inventory_quantity': line.product_qty})
        #     line.quant_id = quant
        # return res


class StockInventory(models.Model):
    _name = 'setu.stock.inventory'
    _description = 'Setu Stock Inventory'

    name = fields.Char(
        string="Name"
    )
    inventory_count_id = fields.Many2one(
        comodel_name="setu.stock.inventory.count",
        string="Inventory Count"
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        required=True,
        string="Location"
    )
    date = fields.Date(
        string="Inventory Date",
    )
    line_ids = fields.One2many(
        'setu.stock.inventory.line', 'inventory_id', string='Inventories',
        copy=True,
        readonly=False,
        states={'done': [('readonly', True)]}
    )
    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'In Progress'),
        ('done', 'Validated')], copy=False, index=True, readonly=True, default='draft')
    partner_id = fields.Many2one(
        comodel_name="res.users",
        string="Inventoried Owner",
        readonly=True,
        help="Specify Owner to focus your inventory on a particular Owner.")
    move_ids = fields.One2many('stock.move', 'inventory_adj_id', readonly=True, string="Moves")
    product_ids = fields.Many2many(
        'product.product', string='Products', check_company=True,
        domain="[('type', '=', 'product'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Specify Products to focus your inventory on particular Products.")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        readonly=True, index=True, required=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env.company)

    # def create(self, vals):
        # if vals and 'line_ids' in vals and vals['line_ids']:
        #     product_location_pair = list(set(list(
        #         map(lambda line: {'product_id': line[2]['product_id'], 'location_id': line[2]['location_id']},
        #             vals['line_ids']))))
        #     products = self.env['product.product'].sudo().browse(product_ids)
        #     location = self.env['stock.location'].sudo().browse(vals['location_id'])
        #     duplicate_record = self.env['setu.stock.inventory.line'].sudo().search(
        #         [('product_id', 'in', product_ids), ('inventory_id.state', 'not in', ('cancel', 'done')),
        #          ('location_id', '=', vals['location_id'])])
        #     if duplicate_record:
        #         raise ValidationError(
        #             "You cannot have two inventory adjustments In Progress with the same product "
        #             "(%s) and same location (%s)."
        #             "Please validate the first inventory adjustment with this product before creating another one." % (
        #                 ", ".join(products.mapped('display_name')), location.display_name))
        # res = super(StockInventory, self).create(vals)
        # return res

    def action_cancel(self):
        """
        This method will unlink the Inventory Adjustment record with Inventory
        Count if Inventory Adjustment is cancelled.
        :return:
        """
        if self.inventory_count_id:
            try:
                self.inventory_count_id.message_post(
                    body=f"""<div style='color:grey; margin:10px 30px;'>&bull;  <strong> Inventory Adjustment</strong> is cancelled. Please start new Inventory if you want to adjust it.</div>"""
                )
            except Exception as e:
                pass
            self.inventory_count_id = False
        self.state = 'cancel'

    def action_validate(self):
        serial_lot_dict = {}
        auto_inventory_adjustment = self.env['ir.config_parameter'].sudo().get_param(
            'setu_inventory_count_management_18.auto_inventory_adjustment')
        auto_inventory_adjustment = True if auto_inventory_adjustment == 'True' else False
        for line in self.line_ids:
            if line.product_id.tracking == 'serial':
                if not serial_lot_dict.get((line.product_id, line.location_id), False):
                    serial_lot_dict.update({(line.product_id, line.location_id):line.serial_number_ids})
                else:
                    old_lots = serial_lot_dict.get((line.product_id, line.location_id), False)
                    old_lots += line.serial_number_ids
                    serial_lot_dict.update({(line.product_id, line.location_id): old_lots})
                for sr_num in line.serial_number_ids:
                    quant = self.env['stock.quant'].sudo().search(
                        [('location_id', '=', line.location_id.id), ('lot_id', '=', sr_num.id),
                         ('product_id', '=', line.product_id.id),
                         ('quantity', '>', 0)], limit=1)
                    if quant:
                        if line.product_qty == 0:
                            quant.with_context(inventory_mode=True).write({'inventory_quantity': 0})
                        continue
                    quant_on_another_location = self.env['stock.quant'].sudo().search(
                        [('lot_id', '=', sr_num.id),
                         ('product_id', '=', line.product_id.id),
                         ('location_id.usage', '=', 'internal'),
                         ('quantity', '>', 0)], limit=1)
                    if quant_on_another_location:
                        quant_on_another_location.with_context(inventory_mode=True).write({'inventory_quantity': 0})
                        if auto_inventory_adjustment:
                            quant_on_another_location.with_context(adj_context=self.id).action_apply_inventory()

                    quant = self.env['stock.quant'].with_context(inventory_mode=True).sudo().create(
                        {'product_id': line.product_id.id, 'location_id': line.location_id.id,
                         'lot_id': sr_num.id,
                         'inventory_quantity': 1})
            elif line.product_id.tracking == 'lot':
                quant = self.env['stock.quant'].sudo().search([('lot_id', '=', line.prod_lot_id.id),
                                                               ('location_id', '=', line.location_id.id),
                                                               ('product_id', '=', line.product_id.id)], limit=1)
                if quant:
                    quant.inventory_quantity = line.product_qty
                else:
                    #quant_on_another_location = self.env['stock.quant'].sudo().search(
                    #    [('lot_id', '=', line.prod_lot_id.id),
                    #     ('product_id', '=', line.product_id.id)], limit=1)
                    #if quant_on_another_location:
                    #    quant_on_another_location.with_context(inventory_mode=True).write({'inventory_quantity': 0})
                    quant = self.env['stock.quant'].with_context(inventory_mode=True).sudo().create(
                        {'product_id': line.product_id.id, 'location_id': line.location_id.id,
                         'lot_id': line.prod_lot_id.id,
                         'inventory_quantity': line.product_qty})
            else:
                quant = self.env['stock.quant'].sudo().search(
                    [('location_id', '=', line.location_id.id), ('product_id', '=', line.product_id.id)], limit=1)
                if quant:
                    quant.with_context(inventory_mode=True).write({'inventory_quantity': line.product_qty})
                else:
                    quant = self.env['stock.quant'].with_context(inventory_mode=True).sudo().create(
                        {'product_id': line.product_id.id, 'location_id': line.location_id.id,
                         'inventory_quantity': line.product_qty})
            if quant:
                line.quant_id = quant
                if auto_inventory_adjustment:
                    quant.with_context(adj_context=self.id).action_apply_inventory()


            # ACTIVE_STOCK_INVENTORY.clear()
            # ACTIVE_STOCK_INVENTORY.append(self.id)

            # #user will apply the quant record manually
            # if auto_inventory_adjustment and line.quant_id:
            #     line.quant_id.with_context(adj_context=self.id).action_apply_inventory()
        if serial_lot_dict:
            for k,v in serial_lot_dict.items():
                if not v:
                    continue
                found_numbers = self.inventory_count_id.line_ids.filtered(lambda x:x.location_id.id == k[1].id and x.product_id.id == k[0].id).mapped('serial_number_ids')
                total_found_numbers = v + found_numbers
                if total_found_numbers:
                    other_quant_at_the_location = self.env['stock.quant'].sudo().search(
                        [('location_id', '=', k[1].id), ('lot_id', 'not in', total_found_numbers.ids),
                         ('product_id', '=', k[0].id),('quantity','>',0)])
                    if other_quant_at_the_location:
                        for q in other_quant_at_the_location:
                            q.with_context(inventory_mode=True).write({'inventory_quantity': 0})
                            if auto_inventory_adjustment:
                                q.with_context(adj_context=self.id).action_apply_inventory()

        # self.action_check()
        self.state = 'done'
        if self.inventory_count_id:
            self.inventory_count_id.state = 'Inventory Adjusted'

    def action_start(self):
        self.state = 'confirm'

    def action_check(self):
        """ Checks the inventory and computes the stock move to do """
        # tde todo: clean after _generate_moves
        for inventory in self.filtered(lambda x: x.state not in ('done', 'cancel')):
            # first remove the existing stock moves linked to this inventory
            inventory.with_context(prefetch_fields=False).mapped('move_ids').unlink()
            inventory.line_ids._generate_moves()
