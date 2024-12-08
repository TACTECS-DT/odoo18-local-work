# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class odoo_core_accessrights(models.Model):
#     _name = 'odoo_core_accessrights.odoo_core_accessrights'
#     _description = 'odoo_core_accessrights.odoo_core_accessrights'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
