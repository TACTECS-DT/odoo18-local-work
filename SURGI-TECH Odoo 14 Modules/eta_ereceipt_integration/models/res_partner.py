from odoo import fields, models, api


class Partner(models.Model):
    _inherit = 'res.partner'

    building_no = fields.Char('Building No.')
    floor = fields.Char('Floor')
    room = fields.Char('Room')
    landmark = fields.Char('Landmark')
    additional_information = fields.Char('Additional Information')
