from odoo import fields, models, api, exceptions


class stock_quant_inherit_wizard(models.Model):
    _inherit = 'stock.quant'
    location_id_warehouse_id = fields.Many2one(related='location_id.warehouse_id',string='Location/Warehouse',store=True)

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    stock_internal_date = fields.Date('Internal Date',store=True)

