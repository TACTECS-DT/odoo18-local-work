from odoo import models, fields, api


class HRApplicant(models.Model):
    _inherit = 'hr.applicant'

    address = fields.Char(string="Address", required=False, )
    qualification = fields.Char(string="Qualification", required=False, )
    training_courses = fields.Text(string="Training Courses", required=False, )
    previous_experience = fields.Text(string="Previous Experience ", required=False, )
    age = fields.Char(string="Age ", required=False, )
    gender = fields.Selection(string="Gender", selection=[('Male', 'Male'), ('Female', 'Female'), ], required=False, )
    nominee = fields.Char(string="Nominee", required=False)
    previous_experience_ids = fields.One2many('applicant.previous.experience', 'applicant_id')
    company_name1 = fields.Char()
    date_from1 = fields.Date()
    date_to1 = fields.Date()
    job_position1 = fields.Char()
    company_name2 = fields.Char()
    date_from2 = fields.Date()
    date_to2 = fields.Date()
    job_position2 = fields.Char()
    company_name3 = fields.Char()
    date_from3 = fields.Date()
    date_to3 = fields.Date()
    job_position3 = fields.Char()


    @api.onchange('company_name1')
    @api.constrains('company_name1')
    def onchange_company_name1(self):
        if self.company_name1:
            self.env['applicant.previous.experience'].sudo().create(
                {'applicant_id': self.id, 'company_name': self.company_name1, 'date_from': self.date_from1,
                 'date_to': self.date_to1, 'job_position': self.job_position1})

    @api.onchange('company_name2')
    @api.constrains('company_name2')
    def onchange_company_name2(self):
        if self.company_name2:
            self.env['applicant.previous.experience'].sudo().create(
                {'applicant_id': self.id, 'company_name': self.company_name2, 'date_from': self.date_from2,
                 'date_to': self.date_to2, 'job_position': self.job_position2})

    @api.onchange('company_name3')
    @api.constrains('company_name3')
    def onchange_company_name3(self):
        if self.company_name3:
            self.env['applicant.previous.experience'].sudo().create(
                {'applicant_id': self.id, 'company_name': self.company_name3, 'date_from': self.date_from3,
                 'date_to': self.date_to3, 'job_position': self.job_position3})


class PreviousExperience(models.Model):
    _name = 'applicant.previous.experience'

    applicant_id = fields.Many2one('hr.applicant')
    company_name = fields.Char()
    date_from = fields.Date()
    date_to = fields.Date()
    job_position = fields.Char()
    notes = fields.Text()
