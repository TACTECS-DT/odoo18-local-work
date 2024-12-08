# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class ResUser(models.Model):
    _inherit = 'res.users'

    admin_request_portal_access = fields.Boolean('Admin Request portal access')

