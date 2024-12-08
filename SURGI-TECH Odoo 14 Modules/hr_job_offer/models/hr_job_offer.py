from odoo import models, fields, api
import logging
import uuid
import base64
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)

_logger = logging.getLogger(__name__)


class HRJobOffer(models.Model):
    _name = 'hr.job.offer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Job Offer"

    name = fields.Char(string='Name', required=True, copy=False, store=True, index=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('offer'))
    date = fields.Date('Expire Date', default=fields.Date.today())
    applicant_id = fields.Many2one('hr.applicant', string='Application')
    partner_name = fields.Char('Applicant')
    partner_mobile = fields.Char('Mobile')
    availability = fields.Date()
    hr_hiring_date = fields.Date()
    notice_period = fields.Integer('Notice Period (Days)')
    job_id = fields.Many2one('hr.job', tracking=True)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department")
    address_ids = fields.Many2many(
        'res.partner', string="Job Location",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Address where employees are working")
    grade_id = fields.Many2one('grade.grade')
    rank_id = fields.Many2one('rank.rank', domain="[('grade_id','=',grade_id)]")
    rang_id = fields.Many2one('rang.rang', domain="[('rank_id','=',rank_id)]")
    basic = fields.Float('Basic Salary', track_visibility='onchange', digits=dp.get_precision('Payroll'))
    variable_incentive = fields.Float(string="Variable Incentive", track_visibility='onchange',
                                      digits=dp.get_precision('Payroll'))
    is_car_allowance = fields.Boolean('Eligible Car Allowance')
    car_allowance = fields.Float('Car Allowance', track_visibility='onchange', digits=dp.get_precision('Payroll'))
    attendance_type = fields.Selection([
        ('indoor', 'In Door'),
        ('outdoor', 'Out Door')])
    transport_allowance = fields.Float('Transportation Allowance', track_visibility='onchange',
                                       digits=dp.get_precision('Payroll'))
    mobile_package = fields.Float()
    salary = fields.Float('Gross Salary', compute='_compute_gross_salary')
    social_insurance = fields.Float(compute='_compute_social_insurance')
    tax_amount = fields.Float(compute='_compute_tax_amount')
    net_salary = fields.Float(compute='_compute_net_salary')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    user_id = fields.Many2one('res.users', string='Prepaid By', required=False, default=lambda self: self.env.user)
    prepaid_date = fields.Date(string='Prepaid Date', default=fields.Date.today())
    other_allowance_ids = fields.One2many('offer.allowance', 'offer_id')
    state = fields.Selection([
        ('new', 'New'),
        ('progress', 'In Progress'),
        ('to_employee', 'Given to Employee'), ('accepted', 'Accepted'), ('refused', 'Refused')], string='Status',
        copy=False, default='new', required=True)

    def _compute_social_insurance(self):
        for rec in self:
            if rec.salary < 8000:
                rec.social_insurance = rec.salary * (11 / 100)
            else:
                rec.social_insurance = 8000 * (11 / 100)

    def _compute_net_salary(self):
        for rec in self:
            rec.net_salary = rec.salary - (rec.tax_amount + rec.social_insurance)

    def _compute_tax_amount(self):
        for rec in self:
            result = 0.0
            gross = rec.salary - rec.social_insurance
            if ((gross * 12) - 9000) <= 15000:
                result = 0.0
            elif 15000 < ((gross * 12) - 9000) <= 30000:
                result = round(
                    (((((gross * 12) - 9000) - 15000) * 0.025)) / 12, 2)
            elif 30000 < ((gross * 12) - 9000) <= 45000:
                result = round((375 + ((((gross * 12) - 9000) - 30000) * 0.1)) / 12, 2)
            elif 45000 < ((gross * 12) - 9000) <= 60000:
                result = round(((375 + 1500 + (((gross * 12) - 9000) - 45000) * 0.15)) / 12, 2)
            elif 60000 < ((gross * 12) - 9000) <= 200000:
                result = round(((375 + 1500 + 2250 + (((gross * 12) - 9000) - 60000) * 0.2)) / 12, 2)
            elif 200000 < ((gross * 12) - 9000) <= 400000:
                result = round(((375 + 1500 + 2250 + 28000 + (((gross * 12) - 9000) - 200000) * 0.225)) / 12, 2)
            elif 400000 < ((gross * 12) - 9000) <= 600000:
                result = round(
                    ((375 + 1500 + 2250 + 28000 + 45000 + (((gross * 12) - 9000) - 400000) * 0.25)) / 12, 2)
            elif 600000 < ((gross * 12) - 9000) <= 700000:
                result = round(
                    ((750 + 1500 + 2250 + 28000 + 45000 + (((gross * 12) - 9000) - 400000) * 0.25)) / 12, 2)
            elif 700000 < ((gross * 12) - 9000) <= 800000:
                result = round(((4500 + 2250 + 28000 + 45000 + (((gross * 12) - 9000) - 400000) * 0.25)) / 12, 2)
            elif 800000 < ((gross * 12) - 9000) <= 900000:
                result = round(((9000 + 28000 + 45000 + (((gross * 12) - 9000) - 400000) * 0.25)) / 12, 2)
            elif 900000 < ((gross * 12) - 9000) <= 1000000:
                result = round(((40000 + 45000 + (((gross * 12) - 9000) - 400000) * 0.25)) / 12, 2)
            elif 1000000 < ((gross * 12) - 9000) <= 10000000:
                result = round(((90000 + (((gross * 12) - 9000) - 400000) * 0.25)) / 12, 2)
            rec.tax_amount = result

    @api.onchange('applicant_id')
    def onchange_applicant_id(self):
        if self.applicant_id:
            self.job_id = self.applicant_id.job_id.id
            self.partner_name = self.applicant_id.partner_name
            self.partner_mobile = self.applicant_id.partner_mobile or self.applicant_id.partner_phone

    @api.onchange('applicant_id')
    def onchange_job_id(self):
        if self.applicant_id:
            self.department_id = self.applicant_id.hiring_approval_id.department_id.id
            self.grade_id = self.applicant_id.hiring_approval_id.grade_id.id
            self.address_ids = self.applicant_id.hiring_approval_id.address_ids.ids
            self.rank_id = self.applicant_id.hiring_approval_id.rank_id.id
            self.rang_id = self.applicant_id.hiring_approval_id.rang_id.id
            self.attendance_type = self.applicant_id.hiring_approval_id.attendance_type
            self.is_car_allowance = self.applicant_id.hiring_approval_id.is_car_allowance

    @api.depends('basic', 'car_allowance', 'transport_allowance','other_allowance_ids')
    def _compute_gross_salary(self):
        for rec in self:
            other_allow = sum(rec.other_allowance_ids.mapped('allowance'))
            rec.salary = rec.basic +rec.variable_incentive+ rec.car_allowance + rec.transport_allowance + other_allow

    @api.onchange('rang_id')
    def onchange_rang_id(self):
        if self.rang_id:
            self.basic = (self.rang_id.total_salary) * 70 / 100
            self.variable_incentive = (self.rang_id.total_salary) * 30 / 100

    @api.onchange('is_car_allowance')
    def onchange_is_car_allowance(self):
        if self.is_car_allowance:
            self.car_allowance = self.grade_id.car_allow

    @api.onchange('attendance_type')
    def onchange_attendance_type(self):
        if self.attendance_type == 'indoor':
            self.transport_allowance = self.grade_id.transport_allow_in
        if self.attendance_type == 'outdoor':
            self.transport_allowance = self.grade_id.transport_allow_out

    def set_new(self):
        self.ensure_one()
        self.state = 'new'

    def set_progress(self):
        self.state = 'progress'
        self.ensure_one()
        self.applicant_id.write(
            {'job_offer_id': self.id,
             'availability': self.availability,
             'hr_hiring_date': self.hr_hiring_date,
             'notice_period': self.notice_period})

    def set_to_employee(self):
        self.ensure_one()
        self.applicant_id.write(
            {'applicant_state': 'offering',
             'availability': self.availability,
             'hr_hiring_date': self.hr_hiring_date,
             'notice_period': self.notice_period})
        self.state = 'to_employee'

    def do_accept(self):
        self.ensure_one()
        self.state = 'accepted'
        self.applicant_id.applicant_state ='accepted'

    def do_refuse(self):
        self.ensure_one()
        self.state = 'refused'

    def action_offer_send(self):
        self.ensure_one()
        if self.applicant_id.email_from:
            mail_to = self.applicant_id.email_from
            partners = [self.user_id.partner_id]
            if self.applicant_id.line_ids:
                for line in self.applicant_id.line_ids:
                    if line.user_id.partner_id.email:
                        partners.append(line.user_id.partner_id)
            mail_cc = ','.join([p.email for p in partners])
            ctx = dict(self.env.context)
            if mail_to:
                ctx.update({'mail_to': mail_to, 'mail_cc': mail_cc})
                template = self.env.ref('hr_job_offer.email_template_job_offer')
                template.sudo().with_context(**ctx).send_mail(self.id, force_send=True)


class JobOfferAllowance(models.Model):
    _name = 'offer.allowance'

    name = fields.Char()
    allowance = fields.Float('Allowance Amount')
    offer_id = fields.Many2one('hr.job.offer')
