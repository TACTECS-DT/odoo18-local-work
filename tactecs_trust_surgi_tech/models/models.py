# -- coding: utf-8 --

# from odoo import models, fields, api


# class tactecs_trust_surgi_tech(models.Model):
#     _name = 'tactecs_trust_surgi_tech.tactecs_trust_surgi_tech'
#     _description = 'tactecs_trust_surgi_tech.tactecs_trust_surgi_tech'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100