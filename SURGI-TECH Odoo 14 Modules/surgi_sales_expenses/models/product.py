from odoo import models, fields, api
class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    department_ids = fields.Many2many(comodel_name="hr.department",string="Department", )

    is_sales_order = fields.Boolean(string="IS Sales",  )
    po_type = fields.Selection(
        [("Medical", "Medical"), ("Non-Medical", "Non-Medical"),
         ("Administrative", "Administrative")], store=True,string="PO Type")
