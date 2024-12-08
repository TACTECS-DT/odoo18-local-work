# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)
import logging
import pytz

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_join

from odoo import api, fields, models, tools, _
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.exceptions import AccessError
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)


class ManPowerPlan(models.Model):
    _name = 'hr.manpower.plan'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Man Power Plan'

    name = fields.Char(default='New')
    date_from = fields.Date('Date from', tracking=True)
    date_to = fields.Date('Date to', tracking=True)
    active = fields.Boolean(string="Active", default=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsible', readonly=True, default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'HR Approved'), ('gm_approved', 'GM Approved')
    ], string='Status', readonly=True, required=True, tracking=True, copy=False, default='draft')
    line_ids = fields.One2many('manpower.plan.line', 'plan_id', string='Plan Lines')

    def post(self):
        for record in self:
            for line in record.line_ids:
                line.job_id.sudo().write(
                    {'state': 'recruit',
                     'no_of_recruitment': line.request_count,
                     'open_date': line.open_date,
                     'close_date': line.close_date})
                line.job_id.recruiter_ids.unlink()
                for recruiter in line.recruiter_ids:
                    line.job_id.recruiter_ids.create(
                        {'user_id': recruiter.user_id.id,
                         'job_id': line.job_id.id,
                         'required_application': recruiter.required_application})
        return True

    def _send_notification(self, state, partners):
        message = _('Man Power Plan: %s is %s, Please approve') % (str(self.name), state)
        return self.message_post(body=message, partner_ids=partners)

    def action_approved(self):
        return self.write({
            'state': 'approved',
        })

    def action_gm_approved(self):
        self.post()
        return self.write({
            'state': 'gm_approved',
        })

    def action_approve_multi(self):
        items = self.env['hr.manpower.plan'].browse(self._context.get('active_ids', []))
        for item in items.filtered(lambda m: m.state == 'draft'):
            item.action_hr_approve()

    def action_gm_approve_multi(self):
        items = self.env['hr.manpower.plan'].browse(self._context.get('active_ids', []))
        for item in items.filtered(lambda m: m.state == 'approved'):
            item.action_gm_approved()

    @api.constrains('date_from', 'date_to')
    def _constrains_date(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                if rec.date_to < rec.date_from:
                    raise ValidationError(_('You cannot enter date to  before date from'))

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('man.power') or '/'
        return super().create(values)


class ManPowerPlanLine(models.Model):
    _name = 'manpower.plan.line'

    name = fields.Char()
    job_id = fields.Many2one('hr.job', string='Job Position', tracking=True,
                             domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),('job_state','=','gm')]")

    ceiling_count = fields.Integer(related='job_id.ceiling_count')
    open_date = fields.Date('Opening Date')
    close_date = fields.Date('Estimated Closing Date')
    no_of_employee = fields.Integer(related='job_id.no_of_employee')
    grade_id = fields.Many2one(related='job_id.grade_id')
    department_id = fields.Many2one(related='job_id.department_id')
    address_id = fields.Many2many(
        'res.partner', string="Job Location",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Address where employees are working")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    resource_id = fields.Many2one(related='job_id.resource_id')
    request_count = fields.Integer('Count')
    plan_id = fields.Many2one('hr.manpower.plan')
    recruiter_ids = fields.One2many('manpower.plan.recruiter', 'plan_id')


    @api.onchange('open_date', 'job_id')
    def onchange_date(self):
        if self.open_date and self.job_id.replacement_period:
            self.close_date = self.open_date + relativedelta(days=self.job_id.replacement_period)


    @api.constrains('job_id', 'request_count')
    def _constrains_request_count(self):
        for rec in self:
            if rec.request_count > 0:
                count = (rec.job_id.no_of_employee + rec.request_count)
                if rec.job_id.ceiling_count < count:
                    raise ValidationError(_('You cannot request count above job ceiling'))

    @api.onchange('job_id')
    def onchange_job_id(self):
        if self.job_id:
            self.name = self.job_id.name
            self.address_id = [(6, 0, self.job_id.address_id.ids)]


class Recruiter(models.Model):
    _name = 'manpower.plan.recruiter'

    user_id = fields.Many2one('res.users', string='Recruiter')
    required_application = fields.Integer('No Application')
    plan_id = fields.Many2one('manpower.plan.line')