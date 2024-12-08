# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class surgi_sales_extend(models.Model):
#     _name = 'surgi_sales_extend.surgi_sales_extend'
#     _description = 'surgi_sales_extend.surgi_sales_extend'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
