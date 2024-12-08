from odoo import models, fields, api
class NewModule(models.Model):
    _inherit = 'hr.job'

    section_id = fields.Many2one('hr.department', string="Section", domain=[('department_type', '=', 'section')])

    def cron_creat_all_job_position(self):
        for rec in self.search([]):
            approved_record=self.env['job.analysis.approved'].create({
                'job_id':rec.id,
            })
            approved_record.get_questions_ids()
            approved_record.compute_is_enter_user()
            # approved_record.is_enter_user2=True
            # for line in approved_record.questions_ids:
            #     print(line.employee_id.parent_id.user_id.name,line.employee_id.parent_id.user_id.id,"-----------",self.env.user.name,self.env.user.id)
            #     if line.employee_id.parent_id.user_id.id==self.env.user.id:
            #         print('------------------------------')
            #         approved_record.is_enter_user2 = True

