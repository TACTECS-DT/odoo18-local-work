# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class tactecs_trust_module(models.Model):
#     _name = 'tactecs_trust_module.tactecs_trust_module'
#     _description = 'tactecs_trust_module.tactecs_trust_module'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

