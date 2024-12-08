# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class QuestionnairesAnswer(models.Model):
    _name = 'questionnaires.answer'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Questionnaires Answer'
    _rec_name = 'batch_id'

    batch_id = fields.Many2one('job.analysis.batch', readonly=True)
    from_date = fields.Date(related='batch_id.from_date')
    to_date = fields.Date(related='batch_id.to_date')
    active = fields.Boolean(string="Active", default=True)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', readonly=True)
    grade_id = fields.Many2one(
        'grade.grade', string='Grade', related='employee_id.grade_id', readonly=True,store=True)
    manager_id = fields.Many2one(comodel_name="hr.employee", string="Manager", readonly=True,
                                 related='employee_id.parent_id',store=True)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department", readonly=True,
                                    related='employee_id.department_id',store=True)
    position_id = fields.Many2one(comodel_name="hr.job", string="Position", readonly=True, related='employee_id.job_id',store=True)
    answer_line_ids = fields.One2many('answer.line', 'answer_id',tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed')
    ], string='Status', copy=False, index=True, readonly=True, default='draft',tracking=True)
    parent_manager_ids = fields.Many2many('res.users', string='Parent Managers')

    def _compute_parent_manager(self):
        for rec in self:
            record = rec.manager_id
            parents = []
            while record.parent_id.user_id:
                parents.append(record.parent_id.user_id.id)
                record = record.parent_id
            rec.write({'parent_manager_ids': parents})

    def confirm(self):
        self.ensure_one()
        self.write({'state': 'confirm'})
        self._compute_parent_manager()
        for line in self.answer_line_ids:
            if not line.row_answer_ids:
                raise ValidationError('Please add some answer to all question')
            line.send_collection()


    def reset(self):
        self.ensure_one()
        self.write({'state': 'draft'})


class AnswerLine(models.Model):
    _name = 'answer.line'

    question_id = fields.Many2one('job.analysis.questionnaire')

    question_description = fields.Text(related='question_id.description')
    row_answer_ids = fields.One2many('answer.row','answer_id')
    answer_id = fields.Many2one('questionnaires.answer')
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', related='answer_id.employee_id', readonly=True,store=True)
    manager_id = fields.Many2one(comodel_name="hr.employee", string="Manager", readonly=True,
                                 related='employee_id.parent_id',store=True)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department", readonly=True,
                                    related='employee_id.department_id',store=True)
    position_id = fields.Many2one(comodel_name="hr.job", string="Position", readonly=True, related='employee_id.job_id',store=True)
    batch_id = fields.Many2one(related='answer_id.batch_id', store=True)



    def send_collection(self):
        self.ensure_one()
        if not self.collection_id:
            collection = self.env['collection.job.analysis'].sudo().search(
                [('company_id', '=', self.env.user.company_id.id), ('batch_id', '=', self.batch_id.id),
                 ('position_id', '=', self.position_id.id)], limit=1)
            if collection:
                self.collection_id = collection.id






class Answer(models.Model):
    _name = 'answer.row'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Text('Employee Answer')
    collection_answer = fields.Text('Manager Comment')
    parent_answer = fields.Text('Parent Comment')
    hr_answer = fields.Text('HR Comment')
    answer_date = fields.Datetime(readonly=True)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', related='answer_id.employee_id', readonly=True)
    grade_id = fields.Many2one(
        'grade.grade', string='Grade', related='employee_id.grade_id', readonly=True)
    manager_id = fields.Many2one(comodel_name="hr.employee", string="Manager", readonly=True,
                                 related='employee_id.parent_id',store=True)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department", readonly=True,
                                    related='employee_id.department_id',store=True)
    position_id = fields.Many2one(comodel_name="hr.job", string="Position", readonly=True, related='employee_id.job_id',store=True)
    question_id = fields.Many2one(related='answer_id.question_id', store=True)
    question_description = fields.Text(related='question_id.description')
    batch_id = fields.Many2one(related='answer_id.batch_id', store=True)
    manager_check = fields.Boolean('Manager')
    parent_check = fields.Boolean('Parent')
    hr_check = fields.Boolean('HR')
    job_analysis_type_id = fields.Many2one('job.analysis.type', string='Job Analysis Type')
    answer_id = fields.Many2one('answer.line')
    is_manager = fields.Boolean(compute='_compute_groups')
    is_parent = fields.Boolean(compute='_compute_groups')
    is_hr = fields.Boolean(compute='_compute_groups')
    is_access = fields.Boolean(compute='_compute_groups')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('manager', 'Manager Approved'), ('parent', 'Parent Approved'), ('hr', 'HR Approved')
    ], string='Status', copy=False, index=True, readonly=True, default='draft', tracking=True)

    @api.onchange('name')
    def onchange_name_ans(self):
        if self.employee_id.user_id and self.employee_id.user_id.id == self.env.user.id:
            self.answer_date = fields.Datetime.today()
            self.collection_answer = self.name

    @api.onchange('collection_answer')
    def onchange_collection_answer(self):
        if self.collection_answer:
            self.parent_answer = self.collection_answer


    @api.onchange('parent_answer')
    def onchange_parent_answer(self):
        if self.parent_answer:
            self.hr_answer = self.parent_answer

    def _compute_groups(self):
        for rec in self:
            if self.env.user == rec.answer_id.manager_id.user_id and rec.answer_id.manager_id.user_id:
                rec.is_manager = True
                rec.is_access = True
            else:
                rec.is_manager = False
                rec.is_access = False
            if self.env.user in rec.answer_id.answer_id.parent_manager_ids and rec.answer_id.answer_id.parent_manager_ids:
                rec.is_parent = True
                rec.is_access = True
            else:
                rec.is_parent = False
                rec.is_access = False
            if self.env.user.has_group('job_analysis.group_job_analysis_manager'):
                rec.is_hr = True
                rec.is_access = True
            else:
                rec.is_hr = False
                rec.is_access = False


    def manager_approve(self):
        self.ensure_one()
        partners = []
        if self.answer_id.answer_id.parent_manager_ids:
            for par in self.answer_id.answer_id.parent_manager_ids:
                partners.append(par.partner_id.id)
            self._send_notification('Manager Approved', partners)
        self.write({'state': 'manager','manager_check':True})

    def manager_approve_multi(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        records = self.env['answer.row'].browse(active_ids)
        if not all(x.state == 'draft' for x in records):
            raise ValidationError(_('"Please Select in Draft'))
        if not all(x.is_manager for x in records):
            raise ValidationError(_('You can not convert to Manager Approve'))
        for rec in records:
            rec.manager_approve()


    def parent_approve(self):
        self.ensure_one()
        group = self.env.ref('job_analysis.group_job_analysis_manager').sudo().users
        partners = []
        if group:
            for usr in group:
                partners.append(usr.partner_id.id)
            self._send_notification('Parent Manager Approved', partners)
        self.write({'state': 'parent','parent_check':True})

    def parent_approve_multi(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        records = self.env['answer.row'].browse(active_ids)
        if not all(x.state == 'manager' for x in records):
            raise ValidationError(_('"Please Select in Manager Approved'))
        if not all(x.is_parent for x in records):
            raise ValidationError(_('You can not convert to Parent Approve'))
        for rec in records:
            rec.parent_approve()

    def hr_approve(self):
        self.ensure_one()
        self.write({'state': 'hr','hr_check':True})


    def hr_approve_multi(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        records = self.env['answer.row'].browse(active_ids)
        if not all(x.state == 'parent' for x in records):
            raise ValidationError(_('"Please Select in Parent Approved'))
        if not all(x.is_hr for x in records):
            raise ValidationError(_('You can not convert to Parent Approve'))
        for rec in records:
            rec.hr_approve()

    def reset(self):
        self.ensure_one()
        if self.state == 'manager':
            partners = []
            if self.answer_id.answer_id.parent_manager_ids:
                for par in self.answer_id.answer_id.parent_manager_ids:
                    partners.append(par.partner_id.id)
                self._send_notification('Draft', partners)
            self.write({'state': 'draft'})
        elif self.state == 'parent':
            partners = []
            if self.answer_id.answer_id.parent_manager_ids:
                for par in self.answer_id.answer_id.parent_manager_ids:
                    partners.append(par.partner_id.id)
                self._send_notification('Manager Approved', partners)
            self.write({'state': 'manager'})
        elif self.state == 'hr':
            group = self.env.ref('job_analysis.group_job_analysis_manager').sudo().users
            partners = []
            if group:
                for usr in group:
                    partners.append(usr.partner_id.id)
                self._send_notification('Parent Manager Approved', partners)
            self.write({'state': 'parent'})


    def reset_multi(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        records = self.env['answer.row'].browse(active_ids)
        for rec in records:
            rec.reset()

    def _send_notification(self, state, partners):
        message = _('Collection of Job Analysis: %s is convert to %s') % (
            str(self.batch_id.name + "/" + self.position_id.name), state)
        return self.message_post(body=message, partner_ids=partners)


