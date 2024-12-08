from odoo import models, fields, api, _
from datetime import datetime, date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_join
from odoo.exceptions import UserError
from odoo.tools import formataddr
from odoo.exceptions import ValidationError, UserError


class HRApplicant(models.Model):
    _inherit = 'hr.applicant'

    number = fields.Char()
    line_ids = fields.One2many('applicant.process.line', 'applicant_id')
    evaluation_ids = fields.One2many('applicant.survey.line', 'applicant_id')
    job_id = fields.Many2one('hr.job', "Applied Job",
                             domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),('job_state','=','gm')]",
                             tracking=True)
    open_date = fields.Date('Opening Date')
    close_date = fields.Date('Closing Date')
    salary_proposed = fields.Float("HR Proposed Salary", group_operator="avg",
                                   help="HR Salary Proposed by the Organisation", tracking=True)
    applicant_state = fields.Selection([
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('shortlisted', 'Shortlisted'),
        ('no_show', 'No Show'),
        ('offering', 'Offering')
    ], string='Interview Status', default='no_show', tracking=True)
    reviewer_ids = fields.Many2many('res.users', string='Reviewers')
    partner_national_id = fields.Char('National ID')
    notice_period = fields.Integer('Notice Period (Days)')
    history_count = fields.Integer()
    timing_ids = fields.One2many('applicant.stage.timing', 'applicant_id')
    hiring_approval_id = fields.Many2one('hr.hiring.approval')
    hr_hiring_date = fields.Date('HR Hiring Date')
    employee_date = fields.Datetime(related='emp_id.create_date', store=True)


    def _check_referral_fields_access(self, fields):
        pass


    @api.constrains('job_id','user_id')
    def _constrains_max_applications(self):
        for rec in self:
            if rec.job_id.open_date and rec.job_id.close_date and rec.job_id and rec.user_id:
                applications = self.search_count([('job_id', '=', rec.job_id.id),
                                                  ('user_id', '=', rec.user_id.id),
                                                  ('open_date', '=', rec.job_id.open_date),
                                                  ('close_date', '=', rec.job_id.close_date)])
                if rec.job_id.recruiter_ids and applications > 0:
                    max = rec.job_id.recruiter_ids.filtered(lambda m: m.user_id == rec.user_id).mapped(
                        'required_application')
                    if max and applications > max[0]:
                        raise ValidationError(_(
                            'You cannot create an applicant You have reached the maximum number of requests, please contact the Human Resources Manager.'))

    def action_show_hiring_approval(self):
        self.ensure_one()
        approval = self.hiring_approval_id
        action = {
            'name': _('Hiring Approval'),
            'view_mode': 'form,tree',
            'res_model': 'hr.hiring.approval',
            'type': 'ir.actions.act_window',
            'context': {'form_view_initial_mode': 'readonly'},
            'res_id': approval.id,
        }
        return action

    def action_show_employee(self):
        self.ensure_one()
        emp = self.emp_id
        action = {
            'name': _('Employee'),
            'view_mode': 'form,tree',
            'res_model': 'hr.employee',
            'type': 'ir.actions.act_window',
            'context': {'form_view_initial_mode': 'readonly'},
            'res_id': emp.id,
        }
        return action

    def print_evaluations(self):
        return self.env.ref('surgi_recruitment_management.action_evaluations_report').report_action(self, config=False)

    @api.constrains('partner_national_id')
    def _constrains_partner_national_id(self):
        for rec in self:
            if rec.partner_national_id:
                if len(rec.partner_national_id) != 14:
                    raise ValidationError(_('Please enter National ID content 14 digit'))

    @api.onchange('partner_national_id')
    def onchange_partner_national_id(self):
        if self.partner_national_id:
            history = self.search_count([('email_from', 'in', self.mapped('email_from'))])
            if history > 1:
                return {'warning': {
                    'title': _("Warning"),
                    'message': ('This applicant has an old applicantion')}}


    def _compute_reviewer_ids(self):
        for rec in self:
            users = []
            if rec.line_ids:
                for line in rec.line_ids:
                    users = [x.id for x in line.reviewer_ids]
                    users.append(line.user_id.id)
            rec.update({'reviewer_ids': users})



    @api.onchange('stage_id')
    def onchange_stage_id(self):
        if self.line_ids:
            self._compute_reviewer_ids()

    @api.constrains('job_id')
    def create_job_id_steps(self):
        for rec in self:
            if rec.job_id:
                rec.open_date = rec.job_id.open_date
                rec.close_date = rec.job_id.close_date
                rec.line_ids.unlink()
                rec.evaluation_ids.unlink()
                setup = self.env['interview.process'].search([('job_ids', 'in', rec.job_id.id)], limit=1)
                if setup:
                    sequences = []
                    evaluation = []
                    for line in setup.line_ids:
                        users = [x.id for x in line.reviewer_ids]
                        users.append(line.user_id.id)
                        sequences.append((0, 0, {
                            'name': line.name,
                            'stage_id': line.stage_id.id,
                            'user_id': line.user_id.id,
                            'survey_ids': line.survey_ids.ids,
                            'applicant_survey_ids': line.applicant_survey_ids.ids,
                            'reviewer_ids': line.reviewer_ids.ids,
                            'type': line.type}))
                        for su in line.survey_ids:
                            evaluation.append((0, 0, {'survey_id': su.id,
                                                      'partner_id': line.user_id.partner_id.id,
                                                      'user_ids': users,
                                                      'stage_id': line.stage_id.id,}))
                        for sur in line.applicant_survey_ids:
                            evaluation.append((0, 0, {'survey_id': sur.id,
                                               'partner_id': self.partner_id.id,
                                               'user_ids': users,
                                               'stage_id': line.stage_id.id,}))
                    rec.line_ids = sequences
                    rec.evaluation_ids = evaluation


    @api.model
    def create(self, values):
        values['number'] = self.env['ir.sequence'].next_by_code('hr.applicant') or '/'
        res = super().create(values)
        for rec in self:
            new_partner_id = self.env['res.partner'].search([('mobile', '=', rec.partner_mobile)],
                                                            limit=1)
            if not new_partner_id:
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'type': 'private',
                    'partner_national_id': rec.partner_national_id,
                    'name': rec.partner_name,
                    'email':rec.email_from,
                    'mobile': rec.partner_mobile,
                })
            values['partner_id'] = new_partner_id.id
        return res


    def show_surveys(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Interview Surveys',
            'view_mode': 'tree',
            'res_model': 'applicant.survey.line',
            'domain': [('applicant_id', '=', self.id)],
        }

    def action_makeMeeting(self):
        res = super(HRApplicant, self).action_makeMeeting()
        survey_ids = self.line_ids.filtered(lambda m: m.stage_id == self.stage_id).mapped('applicant_survey_ids')
        partners = [self.user_id.partner_id.id]
        if self.partner_id:
            partners.append(self.partner_id.id)
        if self.line_ids:
            for line in self.line_ids:
                if line.user_id.partner_id:
                    partners.append(line.user_id.partner_id.id)
        res['context'].update({
            'default_partner_ids': partners,
            'default_job_id': self.job_id.id,
            'default_applicant_id': self.id,
            'default_stage_id': self.stage_id.id,
            'default_survey_ids': survey_ids.ids if survey_ids else [],
        })
        return res

    def write(self, values):
        """ keep stage history. """
        if 'stage_id' in values:  # keep assignment history
            # no need to keep it in vals here
            for rec in self:
                olds = self.env['applicant.stage.timing'].sudo().search([('new_stage_id', '=', rec.stage_id.id)],
                                                                        limit=1)
                date_from = rec.create_date
                if olds:
                    date_from = olds.date_to
                self.env['applicant.stage.timing'].sudo().create({
                    'applicant_id': rec.id,
                    'user_id': self.env.user.id,
                    'old_stage_id': rec.stage_id.id,
                    'new_stage_id': values['stage_id'],
                    'date': date_from,
                    'date_to': datetime.today(),
                })
        return super(HRApplicant, self).write(values)


class ApplicantProcessLine(models.Model):
    _name = 'applicant.process.line'

    name = fields.Char('Sequence')
    stage_id = fields.Many2one('hr.recruitment.stage')
    user_id = fields.Many2one('res.users', string='Interviewer')
    survey_ids = fields.Many2many('survey.survey', 'applicant_process_line_rel', 'process_line_id', 'survey_id',
                                  string='Recruiter Surveys')
    applicant_survey_ids = fields.Many2many('survey.survey', string='Applicant Surveys')
    accepted = fields.Boolean()
    rejected = fields.Boolean()
    shortlisted = fields.Boolean()
    applicant_id = fields.Many2one('hr.applicant', ondelete='cascade')
    type = fields.Selection([
        ('zoom', 'Zoom'),
        ('physically ', 'Physically')
    ], string='Interview Type')
    reviewer_ids = fields.Many2many('res.users', string='Reviewers')

    def update_lines(self):
        self.env['applicant.survey.line'].search([('stage_id', '=', self.stage_id.id)]).sudo().unlink()
        for line in self:
            users = [x.id for x in line.reviewer_ids]
            users.append(line.user_id.id)
            for su in line.survey_ids:
                self.env['applicant.survey.line'].create({'survey_id': su.id,
                                                          'partner_id': line.user_id.partner_id.id,
                                                          'applicant_id': self.id,
                                                          'user_ids': users,
                                                          'stage_id': line.stage_id.id,})
            for sur in line.applicant_survey_ids:
                self.env['applicant.survey.line'].create({'survey_id': sur.id,
                                                          'partner_id': line.applicant_id.partner_id.id,
                                                          'applicant_id': self.id,
                                                          'user_ids': users,
                                                          'stage_id': line.stage_id.id,})

    def write(self, values):
        res = super().write(values)
        if 'user_id' in values:
            self.update_lines()
        if 'survey_ids' in values:
            self.update_lines()
        if 'applicant_survey_ids' in values:
            self.update_lines()
        if 'reviewer_ids' in values:
            self.update_lines()
        return res

    def unlink(self):
        for line in self:
            survey_history = self.env['applicant.survey.line'].search([('stage_id', '=', line.stage_id.id)])
            if survey_history:
                survey_history.sudo().unlink()
        return super(ApplicantProcessLine, self).unlink()


class ApplicantSurveyLine(models.Model):
    _name = 'applicant.survey.line'

    applicant_id = fields.Many2one('hr.applicant')
    is_print = fields.Boolean()
    process_line_id = fields.Many2one('applicant.process.line')
    stage_id = fields.Many2one('hr.recruitment.stage')
    job_id = fields.Many2one(related='applicant_id.job_id')
    user_ids = fields.Many2many('res.users')
    department_id = fields.Many2one(related='applicant_id.department_id')
    survey_id = fields.Many2one('survey.survey', string="Survey")
    response_id = fields.Many2one('survey.user_input', "Response", ondelete="set null")
    response_date = fields.Datetime(related='response_id.create_date')
    meeting_date = fields.Datetime(compute='_compute_meeting_date')
    state = fields.Selection(related='response_id.state')
    scoring_percentage = fields.Float(related='response_id.scoring_percentage', store=True)  # stored for perf reasons
    scoring_total = fields.Float(related='response_id.scoring_total', store=True)  # stored for perf reasons
    scoring_success = fields.Boolean(related='response_id.scoring_success', store=True)  # stored for perf reasons
    partner_id = fields.Many2one('res.partner')
    is_current_user = fields.Boolean(compute='_compute_is_current_user')
    comment = fields.Text()

    def _compute_is_current_user(self):
        for rec in self:
            if rec.partner_id and self.env.user.partner_id == rec.partner_id:
                rec.is_current_user = True
            else:
                rec.is_current_user = False

    @api.depends('applicant_id', 'stage_id')
    def _compute_meeting_date(self):
        for rec in self:
            event = self.env['calendar.event'].search(
                [('applicant_id', '=', rec.applicant_id.id), ('stage_id', '=', rec.stage_id.id)], limit=1)
            if event:
                rec.meeting_date = event.start
            else:
                rec.meeting_date = False

    def action_start_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.response_id:
            response = self.survey_id._create_answer(partner=self.partner_id)
            self.response_id = response.id
        else:
            response = self.response_id
        # grab the token of the response and start surveying
        return self.survey_id.action_start_survey(answer=response)

    def action_print_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        self.ensure_one()
        return self.survey_id.action_print_survey(answer=self.response_id)


class ApplicantStageTiming(models.Model):
    _name = 'applicant.stage.timing'

    applicant_id = fields.Many2one('hr.applicant', ondelete='cascade')
    user_id = fields.Many2one('res.users', 'User')
    old_stage_id = fields.Many2one('hr.recruitment.stage', 'Old Stage')
    new_stage_id = fields.Many2one('hr.recruitment.stage', 'New Stage')
    date = fields.Datetime('Date from')
    date_to = fields.Datetime('Date to')
    duration = fields.Float(compute='_compute_duration')

    @api.depends('date', 'date_to')
    def _compute_duration(self):
        for rec in self:
            if rec.date and rec.date_to:
                rec.duration = (rec.date_to - rec.date).total_seconds() / 3600.0
            else:
                rec.duration = 0.0
