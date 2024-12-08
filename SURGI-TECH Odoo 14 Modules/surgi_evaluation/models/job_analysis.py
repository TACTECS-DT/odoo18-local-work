from odoo import models, fields, api
class JobAnalysisEvaluation(models.Model):
    _name = 'job.analysis.evaluation'
#     _rec_name = 'employee_id'
    # _description = 'New Description'
    #
    #
    # state = fields.Selection(selection=[('draft', 'Draft'), ('confirm', 'Confirm'), ],default='draft')
    #
    # employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False, )
    #
    # replacement = fields.Boolean(string="Replacement",  )
    #
    # job_title = fields.Char(string="Job Title",related='employee_id.job_title' )
    # department_id = fields.Many2one(comodel_name="hr.department", string="Department",related='employee_id.department_id' )
    # section_id = fields.Many2one(comodel_name="hr.department", string="Section",related='employee_id.section_id'  )
    # registration_number = fields.Char(string="Registration Number of the Employee",
    #                                   related='employee_id.registration_number')
    # job_id = fields.Many2one(comodel_name="hr.job", string="Job Position",related='employee_id.job_id' )
    # parent_id = fields.Many2one(comodel_name="hr.employee", string="Manager",related='employee_id.parent_id' )
    # certificate = fields.Selection(string="Certificate Level",related='employee_id.certificate' )
    # experience_y = fields.Integer(string="Experience",related='employee_id.experience_y' )
    # experience_m = fields.Integer(string="Experience",related='employee_id.experience_m' )
    # experience_d = fields.Integer(string="Experience",related='employee_id.experience_d' )
    # count_man_employee = fields.Integer(string="Counter",related='employee_id.parent_id.count_man_employee' )
    #
    # is_department_man = fields.Boolean(string="", compute='check_if_department_manager')
    #
    # grade_id = fields.Many2one(comodel_name="grade.grade", string="Grade",)
    # rank_id = fields.Many2one(comodel_name="rank.rank", string="Rank",)
    # rang_id = fields.Many2one(comodel_name="rang.rang", string="Range",)
    #
    # date_start = fields.Date(string="Start Date", required=False, )
    # date_end = fields.Date(string="End Date", required=False, )
    #
    #
    # questions_ids = fields.One2many(comodel_name="question.answer", inverse_name="analysis_id",)

    #
    # @api.onchange('employee_id')
    # def get_employee_grad(self):
    #     self.grade_id=self.employee_id.grade_id.id
    #     self.rank_id=self.employee_id.rank_id.id
    #     self.rang_id=self.employee_id.rang_id.id
    #
    #
    #
    # @api.depends('is_department_man', 'employee_id')
    # def check_if_department_manager(self):
    #     self.is_department_man = False
    #     for rec in self:
    #         if self.env.user.id == rec.employee_id.parent_id.user_id.id:
    #             rec.is_department_man = True
    #
    #         else:
    #             rec.is_department_man = False
    #
    # @api.onchange('employee_relation_id','employee_id')
    # def filters_employee_manager(self):
    #     categ_ids = []
    #     employee_rec = self.env['hr.employee'].search([])
    #     for emp in employee_rec:
    #         if emp.parent_id.user_id == self.env.user and not self.env.user.has_group('surgi_evaluation.all_permission_group_job_analysis') :
    #             categ_ids.append(emp.id)
    #         elif self.env.user.has_group('surgi_evaluation.all_permission_group_job_analysis') :
    #             categ_ids.append(emp.id)
    #
    #     return {
    #         'domain': {'employee_id': [('id', 'in', categ_ids)]}
    #     }
    #
    # def button_confirm(self):
    #     self.state = 'confirm'
    #
    # def button_cancel(self):
    #     self.state='draft'


class QuestionAnswer(models.Model):
    _name = 'question.answer'
#     _rec_name = 'question'
    #
    # question= fields.Text(string="Question")
    # answer = fields.Text(string="Answer",)
    # analysis_id = fields.Many2one(comodel_name="job.analysis.evaluation", string="", required=False, )