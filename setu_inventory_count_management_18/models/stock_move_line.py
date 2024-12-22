from odoo import fields, models, api, _


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    count_id = fields.Many2one(
        comodel_name="setu.stock.inventory.count",
        string="Count"
    )
    inventory_adj_id = fields.Many2one(
        comodel_name="setu.stock.inventory",
        string="Inventory Adjustment"
    )

    @api.model_create_multi
    def create(self, vals_list):
        inventory_adj_id = self._context.get('adj_context', False)
        if inventory_adj_id:
            inventory_adj_id = self.env['setu.stock.inventory'].sudo().browse(inventory_adj_id)
            for vals in vals_list:
                vals.update({'inventory_adj_id': inventory_adj_id.id,
                             'count_id': inventory_adj_id.inventory_count_id.id,
                             'origin': inventory_adj_id.name})
        return super().create(vals_list)
