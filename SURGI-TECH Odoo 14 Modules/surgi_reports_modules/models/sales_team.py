from odoo import models, fields, api
class CrmteamInherit(models.Model):
    _inherit = 'crm.team'

    product_line_id = fields.Many2one(comodel_name="res.users", string="Product Line Manager",)

