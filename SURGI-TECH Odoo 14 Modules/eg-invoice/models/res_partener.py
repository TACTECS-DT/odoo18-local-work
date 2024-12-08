from odoo import fields, models, api


class res_partner_inhert_einvoice(models.Model):
    _inherit="res.partner"
    tax_reg_no = fields.Char(string="Tax Registration No.")
    building_no=fields.Char(string="Building No.")
    einvoice_partener=fields.Boolean(string="IS E-invoice Partner",default=False)
    is_foriegn=fields.Boolean(string="IS Foriegn",default=False)
    
