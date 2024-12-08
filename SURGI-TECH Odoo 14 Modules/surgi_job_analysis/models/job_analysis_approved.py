from odoo import models, fields, api
class JobAnalysisApproved(models.Model):
    _name = 'job.analysis.approved'
    _rec_name = 'job_id'

    job_id = fields.Many2one(comodel_name="hr.job", string="Job Position",)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='job_id.department_id', store=True)

    questions_ids = fields.One2many(comodel_name="question.answer.approved", inverse_name="analysis_id",)
    state = fields.Selection(selection=[('manager-approval', 'Manager Approval'),('parent_approve', 'Parent Approved'),('hr_approval', 'HR Manager Approval'), ('done','Done') ],default='manager-approval',tracking=True)
    is_enter_user = fields.Boolean(string="",compute='compute_is_enter_user'  )
    is_enter_user2 = fields.Boolean(string="",)
    is_parent_manager = fields.Boolean(string="",  )


    @api.depends('job_id')
    def compute_is_enter_user(self):
        user_list=[]
        parent_list=[]
        for rec in self:
            rec.is_enter_user=False
            rec_questions = self.env['job.analysis.evaluation'].search([('job_id', '=', rec.job_id.id)])
            if rec_questions:
                for question in rec_questions:
                    if question.employee_id.parent_id.user_id:
                        user_list.append(question.employee_id.parent_id.user_id.id)
                    if question.employee_id.parent_id.parent_id.user_id:
                        user_list.append(question.employee_id.parent_id.parent_id.user_id.id)
                        parent_list.append(question.employee_id.parent_id.parent_id.user_id.id)

                    if question.employee_id.parent_id.parent_id.parent_id.user_id:
                        user_list.append(question.employee_id.parent_id.parent_id.parent_id.user_id.id)
                        parent_list.append(question.employee_id.parent_id.parent_id.parent_id.user_id.id)

                    if question.employee_id.parent_id.parent_id.parent_id.parent_id.user_id:
                        user_list.append(question.employee_id.parent_id.parent_id.parent_id.parent_id.user_id.id)
                        parent_list.append(question.employee_id.parent_id.parent_id.parent_id.parent_id.user_id.id)

                if self.env.user.id in user_list or self.env.user.has_group('surgi_evaluation.all_permission_group_redundancy'):
                    rec.is_enter_user = True
                    rec.is_enter_user2 = True

                else:
                    rec.is_enter_user = False
                    rec.is_enter_user2 = False

                print(user_list,'KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK')
                print(parent_list,'KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK')
                if  (parent_list and self.env.user.id in parent_list) or self.env.user.has_group('surgi_evaluation.all_permission_group_redundancy'):
                    rec.is_parent_manager=True
                    print("$$$$$$$$$$$$$$$$$$$$$$$$44")
                else:
                    print("YYYYYYYYYYYYYYYYYYYYYYYYYY")
                    rec.is_parent_manager=False

    def button_cancel(self):
        self.state='manager-approval'

    def button_manger_approval(self):
        self.state = 'hr_approval'

    def button_return_manger_approval(self):
        self.state = 'manager-approval'

    def button_hr_approval(self):
        self.state = 'done'


    @api.onchange('job_id')
    def get_questions_ids(self):
        line_list=[(5,0,0)]
        user_list=[]
        rec_questions= self.env['job.analysis.evaluation'].search([('job_id','=',self.job_id.id)])
        if rec_questions:
           for question in rec_questions:
               for line in question.questions_ids:
                    line_list.append((0,0,{
                        'question':line.question,
                        'employee_id':question.employee_id.id,
                        'answer':line.answer,
                    }))

           self.questions_ids = line_list
           # self.compute_is_enter_user()
        else:
            self.questions_ids = False







class QuestionAnswerApproved(models.Model):
    _name = 'question.answer.approved'
    _rec_name = 'question'

    question= fields.Text(string="Question")
    answer = fields.Text(string="Answer",)
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False, )
    type_id = fields.Many2one(comodel_name="job.analysis.type", string="Job Analysis Type", required=False, )
    is_approved= fields.Boolean(string="Approved",  )
    analysis_id = fields.Many2one(comodel_name="job.analysis.approved", string="", required=False, )

