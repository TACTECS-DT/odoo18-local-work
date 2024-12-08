# -*- coding: utf-8 -*-
################################################################################
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
################################################################################

from odoo.tools.translate import _
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class discount(models.Model):
    _name = 'discount.type'
    
    name = fields.Char('Discount Name')
    discount_value = fields.Float('Discount Value')
    