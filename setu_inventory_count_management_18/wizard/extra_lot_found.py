from odoo import fields, models, api, _


class ExtraLotFound(models.TransientModel):
    _name = 'extra.lot.found.wizard'
    _description = "Open Wizard if you find unscanned lot/serial numbers"

    note = fields.Html(compute='_get_wizard_message')
    inventory_count_id = fields.Many2one('setu.stock.inventory.count')
    note_to_continue = fields.Char(string='Note',
                                   default='NOTE : Press Continue if you want to add these Lot lines in Inventory Count.')

    def _get_wizard_message(self):
        for record in self:
            msg = "Another Lot/Serial Numbers found which are not scanned yet : " + "<br/>" + "<br/>"
            location = ''
            extra_lot_lines = record.inventory_count_id.line_ids.filtered(
                lambda l: l.qty_in_stock == l.counted_qty and l.is_discrepancy_found)
            for line in extra_lot_lines:
                location += "-> Lots  '" + ', '.join(
                    self.env['stock.quant'].sudo().search([('location_id', '=', line.location_id.id),
                                                    ('product_id', '=',
                                                     line.product_id.id)]).filtered(
                        lambda l: l.lot_id not in extra_lot_lines.mapped('lot_id')).mapped('lot_id.name')) + \
                            "'  at the  '{}'  Location.".format(line.location_id.name) + "<br/>"
            record.note = msg + "\n" + location

    def add_the_extra_lot_lines_in_adj(self):
        extra_lot_lines = self.inventory_count_id.line_ids.filtered(
            lambda l: l.qty_in_stock == l.counted_qty and l.is_discrepancy_found)
        for line in extra_lot_lines:
            line.write({'is_discrepancy_found': False})
            extra_lots = self.env['stock.quant'].sudo().search([('location_id', '=', line.location_id.id),
                                                         ('product_id', '=',
                                                          line.product_id.id)]).filtered(
                lambda l: l.lot_id not in extra_lot_lines.mapped('lot_id')).mapped('lot_id')
            for lot in extra_lots:
                self.inventory_count_id.line_ids.create({
                    'inventory_count_id': line.inventory_count_id.id,
                    'product_id': line.product_id.id,
                    'tracking': line.tracking,
                    'lot_id': lot.id,
                    'location_id': line.location_id.id,
                    'theoretical_qty': lot.product_qty,
                    'qty_in_stock': lot.product_qty,
                    'counted_qty': 0,
                    'is_discrepancy_found': True,
                    'user_calculation_mistake': line.user_calculation_mistake
                })
