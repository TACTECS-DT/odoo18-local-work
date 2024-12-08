

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


class HiringApproval(models.Model):
    _name = 'hr.hiring.approval'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hiring Approval"


    name = fields.Char(string='Name', required=True, copy=False, store=True, index=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('hiring.approval'))
    applicant_id = fields.Many2one('hr.applicant',string='Application')
    partner_name = fields.Char('Applicant')
    partner_mobile = fields.Char('Mobile')
    job_id = fields.Many2one('hr.job', tracking=True)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department")
    address_ids = fields.Many2many(
        'res.partner', string="Job Location",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Address where employees are working")
    grade_id = fields.Many2one('grade.grade')
    rank_id = fields.Many2one('rank.rank', domain="[('grade_id','=',grade_id)]")
    rang_id = fields.Many2one('rang.rang', domain="[('rank_id','=',rank_id)]")
    salary = fields.Float('Gross Salary', compute='_compute_gross_salary')
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
    date = fields.Date('Joining Date')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    user_id = fields.Many2one('res.users',string='Prepaid By',required=False, default=lambda self: self.env.user)
    state = fields.Selection([
        ('new', 'New'),
        ('hr', 'HR Approved'),('gm', 'GM Approved')], string='Status',
        copy=False, default='new', required=True,tracking=True)

    @api.onchange('applicant_id')
    def onchange_applicant_id(self):
        if self.applicant_id:
            self.job_id = self.applicant_id.job_id.id
            self.partner_name = self.applicant_id.partner_name
            self.partner_mobile = self.applicant_id.partner_mobile or self.applicant_id.partner_phone

    @api.onchange('job_id')
    def onchange_job_id(self):
        if self.job_id:
            self.department_id = self.job_id.department_id.id
            self.grade_id = self.job_id.grade_id.id
            self.address_ids = self.job_id.address_id.ids

    @api.depends('basic', 'car_allowance', 'transport_allowance')
    def _compute_gross_salary(self):
        for rec in self:
            rec.salary = rec.basic + rec.car_allowance + rec.transport_allowance

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
        self.ensure_one()
        self.applicant_id.hiring_approval_id = self.id

    def hr_approval(self):
        self.ensure_one()
        self.state = 'hr'

    def gm_approval(self):
        self.ensure_one()
        self.state = 'gm'
