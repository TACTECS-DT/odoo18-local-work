from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_join
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Questionnaire(models.Model):
    _inherit = 'job.analysis.questionnaire'
    _order = 'code asc'

    show_kpi = fields.Boolean('Show in KPI Report')

class Answer(models.Model):
    _inherit = 'answer.row'
    _order = 'code asc'

    code = fields.Char(related='question_id.code',store=True)


class Grade(models.Model):
    _inherit = 'grade.grade'

    replacement_period = fields.Integer('Replacement Period')
    max_application = fields.Integer('Max Applications')


class HRJob(models.Model):
    _inherit = 'hr.job'

    job_state = fields.Selection([
        ('draft', 'Draft'),
        ('hr', 'HR Approved'),
        ('gm', 'GM Approved')
    ], string='Status', readonly=True, required=True, tracking=True, copy=False, default='draft',
        help="Set whether the recruitment process for this job position.")
    grade_id = fields.Many2one(
        'grade.grade', string='Grade')
    replacement_period = fields.Integer(related='grade_id.replacement_period')
    state = fields.Selection([
        ('recruit', 'Recruitment in Progress'),
        ('open', 'Not Recruiting')
    ], string='Post Status', readonly=True, required=True, tracking=True, copy=False, default='open',
        help="Set whether the recruitment process is open or closed for this job position.")

    current_pipeline = fields.Integer('Current Pipeline', compute='_compute_current_pipeline')
    max_application = fields.Integer(related='grade_id.max_application')
    deduction = fields.Integer('Deduction')
    deduction_type = fields.Selection([
        ('percent', 'Salary %'),
        ('days', 'Days'),
    ])
    address_id = fields.Many2many(
        'res.partner', string="Job Location",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Address where employees are working")
    all_request_count = fields.Integer(compute='_compute_all_request_count', string="All Request Count")
    resource_id = fields.Many2one('request.resource', string='Request Resource')
    ceiling_count = fields.Integer('Ceiling')
    kpi_line_ids = fields.One2many('hr.job.kpi','job_id')
    history_line_ids = fields.One2many('hr.job.history', 'job_id')
    open_date = fields.Date('Opening Date')
    close_date = fields.Date('Closing Date')
    reject_count = fields.Integer(compute='_compute_all_reject_count')
    offering_count = fields.Integer(compute='_compute_all_offering_count')
    no_show_count = fields.Integer(compute='_compute_all_no_show_count')
    shortlisted_count = fields.Integer(compute='_compute_all_shortlisted_count')
    remaining_days = fields.Integer(compute='_compute_remaining_days')
    remaining_applications = fields.Integer(compute='_compute_remaining_applications')
    recruiter_ids = fields.One2many('hr.job.recruiter','job_id',string="Recruiters")
    is_edit_group = fields.Boolean(compute='_compute_is_edit_group')


    def _compute_is_edit_group(self):
        for rec in self:
            if self.env.user.has_group('surgi_recruitment_management.group_edit_job_position'):
                rec.is_edit_group = True
            else:
                rec.is_edit_group = False

    @api.constrains('recruiter_ids')
    def _constrains_recruiters(self):
        for rec in self:
            if rec.recruiter_ids:
                count = sum(rec.recruiter_ids.mapped('required_application'))
                if rec.max_application < count:
                    raise ValidationError(_('You cannot set application count above Max job Applications'))

    def _compute_remaining_days(self):
        for job in self:
            date_now = fields.Date.context_today(self)
            if job.close_date:
                job.remaining_days = (job.close_date - date_now).days
            else:
                job.remaining_days = 0.0

    def _compute_remaining_applications(self):
        for job in self:
            applications= self.env['hr.applicant'].sudo().search_count(
                [('job_id', '=', job.id), ('create_date', '>=', job.open_date), ('create_date', '<=', job.close_date)])
            job.remaining_applications = job.max_application - applications


    def _compute_all_application_count(self):
        for job in self:
            if job.open_date and job.close_date:
                job.all_application_count = self.env['hr.applicant'].sudo().search_count([('job_id', '=', job.id),('create_date', '>=', job.open_date),('create_date', '<=', job.close_date)])
            else:
                job.all_application_count = self.env['hr.applicant'].sudo().search_count([('job_id', '=', job.id)])


    def _compute_all_reject_count(self):
        for job in self:
            if job.open_date and job.close_date:
                job.reject_count = self.env['hr.applicant'].sudo().search_count([('job_id', '=', job.id), ('applicant_state', '=','rejected'),('create_date', '>=', job.open_date),('create_date', '<=', job.close_date)])
            else:
                job.reject_count = self.env['hr.applicant'].sudo().search_count([('job_id', '=', job.id),('applicant_state', '=','rejected')])


    def _compute_all_shortlisted_count(self):
        for job in self:
            if job.open_date and job.close_date:
                job.shortlisted_count = self.env['hr.applicant'].sudo().search_count([('job_id', '=', job.id), ('applicant_state', '=','shortlisted'),('create_date', '>=', job.open_date),('create_date', '<=', job.close_date)])
            else:
                job.shortlisted_count = self.env['hr.applicant'].sudo().search_count([('job_id', '=', job.id),('applicant_state', '=','shortlisted')])

    def _compute_all_no_show_count(self):
        for job in self:
            if job.open_date and job.close_date:
                job.no_show_count = self.env['hr.applicant'].sudo().search_count([('job_id', '=', job.id), ('applicant_state', '=','no_show'),('create_date', '>=', job.open_date),('create_date', '<=', job.close_date)])
            else:
                job.no_show_count = self.env['hr.applicant'].sudo().search_count(
                    [('job_id', '=', job.id), ('applicant_state', '=', 'no_show')])

    def _compute_all_offering_count(self):
        for job in self:
            if job.open_date and job.close_date:
                job.offering_count = self.env['hr.applicant'].sudo().search_count([('job_id', '=', job.id), ('applicant_state', '=','offering'),('create_date', '>=', job.open_date),('create_date', '<=', job.close_date)])
            else:
                job.offering_count = self.env['hr.applicant'].sudo().search_count(
                    [('job_id', '=', job.id), ('applicant_state', '=', 'offering')])


    def _compute_all_request_count(self):
        for job in self:
            job.all_request_count = self.env['hiring.request'].sudo().search_count([('job_id', '=', job.id)])

    def _compute_current_pipeline(self):
        for job in self:
            if job.open_date and job.close_date:
                job.current_pipeline = self.env['hr.applicant'].search_count(
                    [('job_id', '=', job.id), ('applicant_state', '=','accepted'),('create_date', '>=', job.open_date),('create_date', '<=', job.close_date)])
            else:
                job.current_pipeline = self.env['hr.applicant'].sudo().search_count(
                    [('job_id', '=', job.id), ('applicant_state', '=', 'accepted')])


    def _send_notification(self, state, partners):
        message = _('Job Position: %s is %s, Please approve') % (str(self.name), state)
        return self.message_post(body=message, partner_ids=partners)

    def action_hr_approve(self):
        group = self.env.ref('surgi_recruitment_management.group_gm_approve_job').sudo().users
        partners = []
        if group:
            for usr in group:
                partners.append(usr.partner_id.id)
            self._send_notification('HR approved', partners)
        self.write({
            'job_state': 'hr'})

    def action_hr_approve_multi(self):
        items = self.env['hr.job'].browse(self._context.get('active_ids', []))
        for item in items.filtered(lambda m: m.job_state == 'draft'):
            item.action_hr_approve()

    def action_create_request(self):
        for rec in self:
            request = self.env['hiring.request'].sudo().create(
                {
                    'active': True,
                    'job_id': rec.id,
                    'replacement_period': rec.replacement_period,
                    'department_id': rec.department_id.id,
                    'grade_id': rec.grade_id.id,
                    'resource_id': rec.resource_id.id,
                    'request_count': rec.no_of_recruitment,
                    'request_reason': 'manpower',
                    'address_id': [(6, 0, rec.address_id.ids)]})

    def action_create_request_multi(self):
        items = self.env['hr.job'].browse(self._context.get('active_ids', []))
        for item in items.filtered(lambda m: m.job_state == 'gm'):
            item.action_create_request()

    def action_gm_approve(self):
        self.ensure_one()
        self.write({
            'job_state': 'gm'
        })

    def action_gm_approve_multi(self):
        items = self.env['hr.job'].browse(self._context.get('active_ids', []))
        for item in items.filtered(lambda m: m.job_state == 'hr'):
            item.action_gm_approve()

    def show_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hiring Requests',
            'view_mode': 'tree,form',
            'res_model': 'hiring.request',
            'domain': [('job_id', '=', self.id)],
        }

    def show_job_analysis(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Job Analysis',
            'view_mode': 'tree',
            'view_id':self.env.ref('surgi_recruitment_management.show_job_analysis_tree_view').id,
            'res_model': 'answer.row',
            'context':{'search_default_batch': 1,'search_default_position':1,'search_default_question':1,'create': 0},
            'domain': [('state', '=', 'hr'),('question_id.show_kpi', '=', True),('position_id', '=', self.id)],
        }


    def write(self, values):
        """ keep history. """
        if 'open_date' in values or 'close_date' in values:
            for rec in self:
                self.env['hr.job.history'].sudo().create({
                    'job_id': rec.id,
                    'open_date': rec.open_date,
                    'close_date': rec.close_date,
                })
        return super(HRJob, self).write(values)

    @api.model
    def create(self, values):
        for rec in self:
            group = self.env.ref('surgi_recruitment_management.group_hr_approve_job').sudo().users
            partners = []
            if group:
                for usr in group:
                    partners.append(usr.partner_id.id)
                self._send_notification('created', partners)
        return super().create(values)

class Recruiter(models.Model):
    _name = 'hr.job.recruiter'
    _rec_name = "user_id"

    user_id = fields.Many2one('res.users', string='Recruiter')
    required_application = fields.Integer('No Application')
    job_id = fields.Many2one('hr.job')

class HRJobKPI(models.Model):
    _name = 'hr.job.kpi'

    name = fields.Char()
    measurement_id = fields.Many2one('kpi.measurement')
    target = fields.Float('Default Target')
    unit = fields.Many2one('uom.uom','Unit')
    job_id = fields.Many2one('hr.job')


class KPIMeasurement(models.Model):
    _name = 'kpi.measurement'

    name = fields.Char()
    code = fields.Char()


class HRJobHistory(models.Model):
    _name = 'hr.job.history'


    job_id = fields.Many2one('hr.job')
    open_date = fields.Date('Opening Date')
    close_date = fields.Date('Closing Date')