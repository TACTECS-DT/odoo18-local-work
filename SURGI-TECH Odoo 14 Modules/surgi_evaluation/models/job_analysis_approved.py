from odoo import models, fields, api
class JobAnalysisApproved(models.Model):
    _name = 'job.analysis.approved'
#     _rec_name = 'job_id'

    # job_id = fields.Many2one(comodel_name="hr.job", string="Job Position",)
    #
    # questions_ids = fields.One2many(comodel_name="question.answer.approved", inverse_name="analysis_id",)
    # state = fields.Selection(selection=[('draft', 'Draft'), ('confirm', 'Confirm'), ],default='draft')
    #
    # def button_confirm(self):
    #     self.state = 'confirm'
    #     x=''
    #     for rec in self.questions_ids:
    #        # x = rec.question
    #        # if rec.question==x:
    #        #     print("######################",rec.answer)
    #
    #        if rec.is_approved==False:
    #            rec.unlink()
    #
    # def button_cancel(self):
    #     self.state='draft'
    #
    # @api.onchange('job_id')
    # def get_questions_ids(self):
    #     line_list=[(5,0,0)]
    #     rec_questions= self.env['job.analysis.evaluation'].search([('job_id','=',self.job_id.id)])
    #     if rec_questions:
    #        for question in rec_questions:
    #            for line in question.questions_ids:
    #                 line_list.append((0,0,{
    #                     'question':line.question,
    #                     'employee_id':question.employee_id.id,
    #                     'answer':line.answer,
    #                 }))
    #        self.questions_ids = line_list
    #     else:
    #         print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
    #         self.questions_ids = False







class QuestionAnswerApproved(models.Model):
    _name = 'question.answer.approved'
    #    _rec_name = 'question'

    #    question= fields.Text(string="Question")
    #   answer = fields.Text(string="Answer",)
    #    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False, )
    #    is_approved= fields.Boolean(string="Approved",  )
    #   analysis_id = fields.Many2one(comodel_name="job.analysis.approved", string="", required=False, )

