from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    overtime_budget = fields.Float()
class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    overtime_budget = fields.Float()
