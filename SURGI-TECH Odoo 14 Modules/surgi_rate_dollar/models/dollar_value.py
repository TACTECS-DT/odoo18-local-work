from odoo import models, fields, api, _
from odoo.exceptions import UserError

class NewModule(models.Model):
    _name = 'dollar.rate'
    _description = 'Dollar Rate'

    value = fields.Float(string="Value")

# class Res_Currency(models.Model):
#     _inherit = 'res.currency'
#
#
#
#
#     @api.depends('rounding')
#
#
#
#     def _has_accounting_entries(self):
#         """ Returns True iff this currency has been used to generate (hence, round)
#         some move lines (either as their foreign currency, or as the main currency
#         of their company).
#         """
#         pass
#
