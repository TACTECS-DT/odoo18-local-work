from odoo import models, fields, api
class JobAnalysisWizard(models.TransientModel):
    _name = 'job.analysis.wizard'

    # start_date = fields.Date(string="Start Date", required=False, )
    # end_date = fields.Date(string="End Date", required=False, )
    # employee_ids = fields.Many2many(comodel_name="hr.employee",string="Employee", )
    # job_line_ids = fields.One2many(comodel_name="job.job.analysis", inverse_name="job_id", )
    #
    # def job_analysis_create(self):
    #     list_line=[]
    #     for line in self.job_line_ids:
    #         list_line.append((0,0,{
    #             'question':line.question,
    #         }))
    #
    #
    #     for rec in self.employee_ids:
    #         job_analysis_rec = self.env['job.analysis.evaluation'].sudo().create({
    #             'employee_id': rec.id,
    #             'date_start': self.start_date,
    #             'date_end': self.end_date,
    #             'questions_ids': list_line,
    #         })
    #         job_analysis_rec.get_employee_grad()

class JobJobAnalysis(models.TransientModel):
    _name = 'job.job.analysis'
#     _rec_name = 'question'

    # question= fields.Text(string="Question")
    # job_id = fields.Many2one(comodel_name="job.analysis.wizard", string="", required=False, )
