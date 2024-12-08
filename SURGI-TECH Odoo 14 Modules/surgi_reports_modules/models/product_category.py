from odoo import models, fields, api
class ProductCategoryInherit(models.Model):
    _inherit = 'product.category'

    product_line_id = fields.Many2one(comodel_name="res.users", string="Product Line Manager",)

