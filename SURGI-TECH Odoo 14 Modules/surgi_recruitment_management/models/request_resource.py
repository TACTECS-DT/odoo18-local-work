from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RequestResource(models.Model):
    _name = 'request.resource'
    _description = 'Request Resource'

    name = fields.Char()