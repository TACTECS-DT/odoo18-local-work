# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class HrJob(models.Model):
    _inherit = 'hr.job'

    position_manager_id = fields.Many2one(comodel_name="hr.employee", string="Manager")