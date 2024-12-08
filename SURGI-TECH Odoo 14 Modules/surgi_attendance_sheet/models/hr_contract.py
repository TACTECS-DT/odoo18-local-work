# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (C) 2020.
#    Author: Eng.Ramadan Khalil (<rkhalil1990@gmail.com>)
#    website': https://www.linkedin.com/in/ramadan-khalil-a7088164
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class HrContract(models.Model):
    _inherit = 'hr.contract'
    multi_shift = fields.Boolean('Planed Shifts', default=False)
    random_shift = fields.Boolean('Random Shifts', default=False)
    shiftslist=fields.One2many('surgi.hr.extrashifts','contract_id', string='Shifts')
    shift_allowance = fields.Boolean('Shift Allowance',default=False)
    @api.onchange('multi_shift')
    def change_multi_shift(self):
        if self.multi_shift :
            self.random_shift=False

    @api.onchange('random_shift')
    def change_random_shift(self):
        if self.random_shift:
            self.multi_shift=False
class extra_shifts(models.Model):
    _name="surgi.hr.extrashifts"
    contract_id=fields.Many2one("hr.contract",string="Employee")
    resource_calendar_id = fields.Many2one('resource.calendar', 'Working Hours', readonly=False)
    is_ramdan_shift=fields.Boolean(string="Is Ramdan Shift")
    
