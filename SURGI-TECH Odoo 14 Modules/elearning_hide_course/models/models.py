# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SlideChannel(models.Model):
    _inherit = 'slide.channel'


    not_listed = fields.Boolean(
        string='Not Listed ',
        required=False,default=False)





