from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    create_performa_sequence = fields.Boolean('Create Perform Sequence')
