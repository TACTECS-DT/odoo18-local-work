# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from . import EnvoConfig
# response = requests.post("https://ptsv2.com/t/z4za5-1610576490/post", data=vals)
# response.raise_for_status()
#
# class Eg_Invoice_Inhert_Account_move(models.Model):
#
#     _description = 'eg-invoice.eg-invoice'
#     _inherit="account.move"
#     cc=fields.Char(string="Exp Ref No.",)
#
#
#
#     @api.model
#     def action_send_einvoice(self):
#         raise Warning("Your record is too old")
#         print("XXXXXXXXXXXXXXXX")
#         #einvoice =EnvoConfig()
#
#         print("VVVVVVVVVVVVVVVVVV")
#         pass

#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

