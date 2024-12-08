from odoo import models, fields, api

class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    registration_number = fields.Char(
        string='Employee Registration Number',
        compute='_compute_registration_number',
        store=True
    )

    @api.depends('employee_id.registration_number')
    def _compute_registration_number(self):
        for record in self:
            record.registration_number = record.employee_id.registration_number

class HrEmployeeInheritBase(models.AbstractModel):
    _inherit = 'hr.employee.base'
    medical_password = fields.Char(string="Password")
    medical_number_char = fields.Char(string="Medical No.", compute='_compute_medical_number_char',
                                      readonly=False, store=True)

    @api.depends('medical_number')
    def _compute_medical_number_char(self):
        for record in self:
            record.medical_number_char = str(record.medical_number) if record.medical_number else ''


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'
    medical_password = fields.Char(string="Password")
    is_current_user = fields.Boolean(compute='_compute_is_employee_current_user')
    medical_number_char = fields.Char(string="Medical No.", compute='_compute_medical_number_char',
                                      readonly=False, store=True)

    @api.depends('medical_number')
    def _compute_medical_number_char(self):
        for record in self:
            record.medical_number_char = str(record.medical_number) if record.medical_number else ''

    def _compute_is_employee_current_user(self):
        for rec in self:
            if rec.user_id:
                if rec.user_id == self.env.user.id:
                    rec.is_current_user = True
                else:
                    rec.is_current_user = False
            else:
                rec.is_current_user = False

class HrEmployeeInheritpublic(models.Model):
    _inherit = 'hr.employee.public'
    medical_password = fields.Char(string="Password")
    evaluation_method = fields.Selection(string="Evaluation Method", selection=[('dm', 'Direct Manager'), ('average', 'Average'),('pm','Parent Manager') ], required=False, )
    medical_number_char = fields.Char(string="Medical No.", compute='_compute_medical_number_char',
                                      readonly=False, store=True)

    @api.depends('medical_number')
    def _compute_medical_number_char(self):
        for record in self:
            record.medical_number_char = str(record.medical_number) if record.medical_number else ''
