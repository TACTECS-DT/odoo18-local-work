# -*- coding: utf-8 -*-
##############################################################################
#
#
#    Copyright (C) 2019-TODAY .
#    Author: Plementus <https://plementus.com>
#    Contributor: Mario Roshdy <m.roshdy@plementus.com>
#    Contributor: Karim Jaber <kareem@plementus.com>
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
##############################################################################

from odoo import models, fields, api


class uom_uom(models.Model):
    _inherit = 'uom.uom'

    unit_type = fields.Char(string='ETA Unit Code', help='This is the type of unit according to egyptian tax authority')
