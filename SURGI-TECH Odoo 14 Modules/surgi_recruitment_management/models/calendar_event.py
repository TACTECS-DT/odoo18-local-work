from odoo import models, fields, api, _


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    job_id = fields.Many2one('hr.job')
    applicant_id = fields.Many2one('hr.applicant')
    stage_id = fields.Many2one('hr.recruitment.stage')
    survey_ids = fields.Many2many('survey.survey')



    def action_send_meeting_mail(self):
        self.ensure_one()
        if self.job_id:
            mail_to = ','.join([p.email for p in self.partner_ids])
            ctx = dict(self.env.context)
            if mail_to:
                ctx.update({'mail_to': mail_to})
                template = self.env.ref('surgi_recruitment_management.email_template_data_applicant_meeting')
                template.sudo().with_context(**ctx).send_mail(self.id,force_send=True)

