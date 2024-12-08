# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.addons.http_routing.models.ir_http import slug

from odoo import api, fields, models


class Menu(models.Model):
    _inherit = "website.menu"

    def _compute_visible(self):
        super(Menu, self)._compute_visible()
        for rec in self:
            xx = rec.clean_url()
            if rec.clean_url() == '/my/expense/requests'  :
                if not rec.env.user.has_group('base.group_user') and not rec.env.user.has_group('base.group_user'):
                    rec.is_visible = False



class ResUsers(models.Model):
    _inherit = 'res.users'

    expense_portal_access = fields.Boolean('Expense Portal Access')
