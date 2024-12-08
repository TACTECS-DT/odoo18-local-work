from odoo import models, fields, api
class HREmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    registration_number = fields.Char('Registration Number of the Employee', groups="hr.group_hr_user,base.group_user", copy=False)

    # @api.depends('registration_number')
    # def compute_registration_number_copy(self):
    #     for rec in self:
    #         if rec.registration_number:
    #             rec.registration_number_copy=rec.registration_number
    #         else:
    #             rec.registration_number_copy=''
