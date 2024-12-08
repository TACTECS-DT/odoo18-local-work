from odoo import models, fields, api
class NewModule(models.Model):
    _inherit = 'stock.valuation.layer'

    company_id = fields.Many2one('res.company', "Company", readonly=False, required=True,default=lambda self: self.env.company,)
    product_id = fields.Many2one('product.product', 'Product', readonly=False, required=True,)
    quantity = fields.Float('Quantity', digits=0, help='Quantity', readonly=False)
    unit_cost = fields.Monetary('Unit Value', readonly=False)
    value = fields.Monetary('Total Value', readonly=False)
    remaining_qty = fields.Float(digits=0, readonly=False)
    description = fields.Char('Description', readonly=False)


