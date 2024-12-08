# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class surgi_collection_rep(models.Model):
#     _name = 'surgi_collection_rep.surgi_collection_rep'
#     _description = 'surgi_collection_rep.surgi_collection_rep'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
