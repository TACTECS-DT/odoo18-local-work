from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EmployeesCertificate(models.Model):
    _name = 'employees.certificate'
    _description = 'Employees Certificates'

    name = fields.Char(required=True)
    code = fields.Char()
    institute = fields.Char()
    date = fields.Date()
    salary_allowance = fields.Float()