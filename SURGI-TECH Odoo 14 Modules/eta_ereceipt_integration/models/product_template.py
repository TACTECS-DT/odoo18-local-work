# -*- coding: utf-8 -*-


from odoo import models, fields, api


class product_template(models.Model):
    _inherit = 'product.template'

    item_type = fields.Selection([('GS1', 'GS1'), ('EGS', 'EGS')],
                                 string='ETA Item Code Type',
                                 help='This is the type of item according to egyptian tax authority and default is GS1',
                                 default='GS1')
    item_code = fields.Char(string='ETA Item Code', help='This is the code of item according to egyptian tax authority')
