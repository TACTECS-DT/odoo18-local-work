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


class HiringRequest(models.Model):
    _name = 'hiring.request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Hiring Request'

    name = fields.Char(default='New')
    date = fields.Date('Opening Date', tracking=True)
    close_date = fields.Date('Estimated Closing Date', tracking=True)
    active = fields.Boolean(string="Active", default=True)
    job_id = fields.Many2one('hr.job', string='Job Position', tracking=True,
                             domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),('job_state','=','gm')]")
    grade_id = fields.Many2one(
        'grade.grade', string='Grade')
    ceiling_count = fields.Integer(related='job_id.ceiling_count')
    no_of_employee = fields.Integer(related='job_id.no_of_employee')
    replacement_period = fields.Integer('Replacement Period')
    department_id = fields.Many2one(comodel_name="hr.department", string="Department")
    resource_id = fields.Many2one('request.resource', string='Request Resource')
    request_count = fields.Integer('Count')
    address_id = fields.Many2many(
        'res.partner', string="Job Location",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Address where employees are working")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsible',readonly=True, default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('hr', 'HR Approved'),
        ('manager', 'Manager Approved')
    ], string='Status', readonly=True, required=True, tracking=True, copy=False, default='draft')
    request_reason = fields.Selection([
        ('replacement', 'Replacement'),
        ('manpower', 'Manpower Planning')
    ], string='Request Reason', default='manpower')
    is_publish = fields.Boolean()
    recruiter_ids = fields.One2many('hiring.recruiter', 'request_id')

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
            self.replacement_period = self.job_id.replacement_period
            self.department_id = self.job_id.department_id.id
            self.request_count = self.job_id.no_of_recruitment
            self.grade_id = self.job_id.grade_id.id
            self.resource_id = self.job_id.resource_id.id
            self.address_id = [(6, 0, self.job_id.address_id.ids)]

    @api.onchange('date', 'replacement_period')
    @api.constrains('date', 'replacement_period')
    def onchange_date(self):
        if self.date:
            self.close_date = self.date + relativedelta(days=self.replacement_period)

    def post(self):
        for record in self:
            record.is_publish = True
            no_of_recruitment = 1 if record.request_count == 0 else record.request_count
            record.job_id.sudo().write(
                {'state': 'recruit',
                 'no_of_recruitment': no_of_recruitment,
                 'open_date': record.date,
                 'address_id':record.address_id.ids,
                 'close_date': record.close_date})
            record.job_id.recruiter_ids.unlink()
            for line in record.recruiter_ids:
                record.job_id.recruiter_ids.create(
                    {'user_id': line.user_id.id,
                     'job_id':record.job_id.id,
                     'required_application': line.required_application})
        return True

    def action_post_multi(self):
        items = self.env['hiring.request'].browse(self._context.get('active_ids', []))
        for item in items.filtered(lambda m: m.state == 'manager'):
            item.post()

    def _send_notification(self, state, partners):
        message = _('Hiring Request: %s is %s, Please approve') % (str(self.name), state)
        return self.message_post(body=message, partner_ids=partners)

    def action_hr_approve(self):
        group = self.env.ref('surgi_recruitment_management.group_gm_approve_job').sudo().users
        partners = []
        if group:
            for usr in group:
                partners.append(usr.partner_id.id)
            self._send_notification('HR approved', partners)
        return self.write({
            'state': 'hr',
        })

    def action_hr_approve_multi(self):
        items = self.env['hiring.request'].browse(self._context.get('active_ids', []))
        for item in items.filtered(lambda m: m.state == 'draft'):
            item.action_hr_approve()

    def action_gm_approve(self):
        return self.write({
            'state': 'manager',
            'date': fields.Date.today(),
        })

    @api.constrains('date', 'close_date')
    def _constrains_date(self):
        for rec in self:
            if rec.close_date and rec.date:
                if rec.close_date < rec.date:
                    raise ValidationError(_('You cannot add close date before opening date'))

    def action_gm_approve_multi(self):
        items = self.env['hiring.request'].browse(self._context.get('active_ids', []))
        for item in items.filtered(lambda m: m.state == 'hr'):
            item.action_gm_approve()

    @api.model
    def create(self, values):
        for rec in self:
            group = self.env.ref('surgi_recruitment_management.group_hr_approve_job').sudo().users
            partners = []
            if group:
                for usr in group:
                    partners.append(usr.partner_id.id)
                rec._send_notification('created', partners)
        values['name'] = self.env['ir.sequence'].next_by_code('hiring.request') or '/'
        return super().create(values)


class Recruiter(models.Model):
    _name = 'hiring.recruiter'

    user_id = fields.Many2one('res.users', string='Recruiter')
    required_application = fields.Integer('Required Application')
    request_id = fields.Many2one('hiring.request')
