from odoo import fields, models, api


class StockInvCountLine(models.Model):
    _name = 'setu.stock.inventory.count.line'
    _description = 'Stock Inventory Count Line'

    inventory_count_id = fields.Many2one(
        comodel_name="setu.stock.inventory.count",
        string="Inventory Count"
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product"
    )
    tracking = fields.Selection(
        related="product_id.tracking",
        string="Tracking"
    )
    serial_number_ids = fields.Many2many('stock.lot', 'setu_stock_inventory_count_line_stock_lot_rel', 'setu_stock_inventory_count_line_id','stock_lot_id',string='Serial Numbers')
    not_found_serial_number_ids = fields.Many2many('stock.lot', 'not_found_stock_lot_rel','count_line_id','lot_id',string='Not Founded Serial Numbers')
    lot_id = fields.Many2one(
        comodel_name="stock.lot",
        string="Lot"
    )
    # theoretical_qty = fields.Float(compute='_get_theoretical_qty')
    theoretical_qty = fields.Float(
        string="Theoretical Qty"
    )
    is_discrepancy_found = fields.Boolean(
        compute="_compute_is_discrepancy_found",
        store=True,
        depends=['counted_qty'],
        string="Is Discrepancy Found"
    )
    qty_in_stock = fields.Float(
        string="Quantity In Stock"
    )
    counted_qty = fields.Float(
        string="Counted Quantity"
    )
    session_line_ids = fields.One2many('setu.inventory.count.session.line', 'inventory_count_line_id', string="Session Lines")
    user_calculation_mistake = fields.Boolean(
        default=False,
        string="User Calculation Mistake"
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Location"
    )
    is_multi_session = fields.Boolean(
        default=False,
        string="Is multi session"
    )
    state = fields.Selection([
        ('Pending Review', 'Pending Review'),
        ('Approve', 'Approve'),
        ('Reject', 'Reject')],
        default="Pending Review",
        string="State"
    )
    is_system_generated = fields.Boolean(
        string="System Generated Line"
    )

    def change_line_state_to_approve(self):
        self.state = 'Approve'

    def change_line_state_to_reject(self):
        self.state = 'Reject'

    # def _get_theoretical_qty(self):
    #     for line in self:
    #         if line.product_id:
    #             quants = self.env['stock.quant'].search(
    #                 [('location_id', '=', line.location_id.id), ('product_id', '=', line.product_id.id)])
    #             theoretical_qty = sum([x.quantity for x in quants])
    #             line.theoretical_qty = theoretical_qty
    #         else:
    #             line.theoretical_qty = 0

    def _compute_is_discrepancy_found(self):
        for line in self:
            line.is_discrepancy_found = False
            if line.product_id.tracking == 'serial':
                # if line.not_found_serial_number_ids:
                #     line.is_discrepancy_found = True
                #     continue
                quants = self.env['stock.quant'].sudo().search(
                    [('location_id', '=', line.location_id.id),
                     ('quantity', '=', 1),
                     ('product_id', '=', line.product_id.id)])
                if not quants:
                    line.is_discrepancy_found = True
                    continue
                additional_quants = list(set(quants.lot_id.ids) ^ set(line.serial_number_ids.ids))
                if additional_quants:
                    line.is_discrepancy_found = True
            elif line.counted_qty != line.qty_in_stock:
                line.is_discrepancy_found = True

        # else:
        #     line.is_discrepancy_found = line.is_discrepancy_found

    # def _compute_is_discrepancy_found(self):
    #     for line in self:
    #         if line.inventory_count_id.state == 'In Progress':
    #             if line.product_id.tracking == 'none':
    #                 if line.counted_qty != line.qty_in_stock:
    #                     line.is_discrepancy_found = True
    #                 else:
    #                     line.is_discrepancy_found = False
    #             else:
    #                 other_quant_at_the_location = self.env['stock.quant'].sudo().search(
    #                     [('location_id', '=', line.location_id.id), ('lot_id', 'not in', line.serial_number_ids.ids),
    #                      ('quantity', '>', 0), ('product_id', '=', line.product_id.id)])
    #                 if line.counted_qty != line.qty_in_stock or other_quant_at_the_location and other_quant_at_the_location.ids not in self.inventory_count_id.line_ids.mapped('lot_id').ids:
    #                     line.is_discrepancy_found = True
    #                 else:
    #                     line.is_discrepancy_found = False
    #         else:
    #             line.is_discrepancy_found = line.is_discrepancy_found
