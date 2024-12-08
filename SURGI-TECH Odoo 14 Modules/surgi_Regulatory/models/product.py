from odoo import models, fields, api, _
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class ProductTemplateChange(models.Model):
    _inherit = 'product.product'

    productTypeRegularity = fields.Selection([('instrument','Instrument'),('implant','Implant'),('non-implant','Non-Implant'),
    ], string="Product Type")

    sterilizeField = fields.Boolean(string="Sterile")
    regularityRef = fields.Char("Reference")
    regularityLabelRef = fields.Char("Label Reference")
    ProductClass = fields.Selection([
        ("i", "I"), ("ii", "IIA"), ("iib", "IIB"), ("iii", "III"),
    ], string="Product Class")

    # registration_line_id = fields.One2many('product.regul', "product_form_id")
    @api.model
    def button_stock_action(self):
        # ctx = dict(
        #     create=False,
        # )
        value = {
            'name': 'Product',
            'view_type': 'form',
            'view_mode': 'kanban,tree,form',
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            'context': {'edit': 1, 'create': 0},

        }
        return value
