# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Loan Request"

    @api.model
    def default_get(self, field_list):
        result = super(HrLoan, self).default_get(field_list)
        if result.get('user_id'):
            ts_user_id = result['user_id']
        else:
            ts_user_id = self.env.context.get('user_id', self.env.user.id)
        result['employee_id'] = self.env['hr.employee'].search([('user_id', '=', ts_user_id)], limit=1).id
        return result

    def _compute_loan_amount(self):
        total_paid = 0.0
        for loan in self:
            for line in loan.loan_lines:
                if line.paid:
                    total_paid += line.amount
            balance_amount = loan.loan_amount - total_paid
            self.total_amount = loan.loan_amount
            self.balance_amount = balance_amount
            self.total_paid_amount = total_paid

    name = fields.Char(string="Loan Name", default="/", readonly=True, help="Name of the loan")
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True, help="Date")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, help="Employee")
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,
                                    string="Department", help="Employee")
    installment = fields.Integer(string="No Of Installments", default=1, help="Number of installments")
    payment_date = fields.Date(string="Payment Start Date", required=True, default=fields.Date.today(), help="Date of "
                                                                                                             "the "
                                                                                                             "paymemt")
    loan_lines = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True, help="Company",
                                 default=lambda self: self.env.user.company_id,
                                 states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position",
                                   help="Job position")
    loan_amount = fields.Float(string="Loan Amount", required=True, help="Loan amount")
    total_amount = fields.Float(string="Total Amount", readonly=True, compute='_compute_loan_amount',
                                help="Total loan amount")
    balance_amount = fields.Float(string="Balance Amount", compute='_compute_loan_amount', help="Balance amount")
    total_paid_amount = fields.Float(string="Total Paid Amount", compute='_compute_loan_amount',
                                     help="Total paid amount")

    check_submit = fields.Boolean(compute='compute_check_submit')


    # check_states = fields.Boolean(compute='compute_check_states')
    # def compute_check_states(self):
    #     for rec in self:
    #         rec.check_states=False
            # part=False
            # if (self.env.user.id==rec.employee_id.parent_id.user_id.id or self.env.user.id==rec.employee_id.parent_id.parent_id.user_id.id)  and rec.state !='waiting_approval_1':
            #     rec.check_states = True
            #     print("11111111111111111111111111111111111111111111")
            #     part=True
            # elif self.env.user.id==rec.employee_id.user_id.id and rec.state !='draft' and part==False:
            #     print("22222222222222222222222222222222222222222")
            #     rec.check_states = True
            # elif  self.env.user.has_group('hr.group_hr_manager') and rec.state !='approve':
            #     print("333333333333333333333333333333333333")
            #     rec.check_states=True
            #
            # elif  self.env.user.has_group('employee_loan.access_finance_approve') and rec.state !='finance_approval':
            #     rec.check_states=True
            #     print("44444444444444444444444444444444")





    @api.depends('state')
    def compute_check_submit(self):
        for rec in self:
            if rec.state=='draft' and (rec.employee_id.parent_id.user_id.id==self.env.user.id or rec.employee_id.parent_id.parent_id.user_id.id==self.env.user.id or rec.employee_id.parent_id.parent_id.user_id.id==self.env.user.id):
                rec.check_submit=True
            else:
                rec.check_submit = False






    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Manager Approval'),
        ('approve', 'HR Approved'),
        ('finance_approval', 'Finance Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )

    @api.model
    def create(self, values):
        loan_count = self.env['hr.loan'].search_count(
            [('employee_id', '=', values['employee_id']), ('state', '=', 'approve'),
             ('balance_amount', '!=', 0)])
        if loan_count:
            raise ValidationError(_("The employee has already a pending installment"))
        else:
            values['name'] = self.env['ir.sequence'].get('hr.loan.seq') or ' '
            res = super(HrLoan, self).create(values)
            return res

    def compute_installment(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        for loan in self:
            loan.loan_lines.unlink()
            date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
            amount = loan.loan_amount / loan.installment
            for i in range(1, loan.installment + 1):
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)
        return True

    def action_refuse(self):
        return self.write({'state': 'refuse'})

    def action_submit(self):
        self.write({'state': 'waiting_approval_1'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_approve(self):
        for data in self:
            if not data.loan_lines:
                raise ValidationError(_("Please Compute installment"))
            else:
                self.write({'state': 'approve'})

    def unlink(self):
        for loan in self:
            if loan.state not in ('draft', 'cancel'):
                raise UserError(
                    'You cannot delete a loan which is not in draft or cancelled state')
        return super(HrLoan, self).unlink()

    def finance_approval_button(self):
        self.state = 'finance_approval'
        self.action_approve_finance()


class InstallmentLine(models.Model):
    _name = "hr.loan.line"
    _description = "Installment Line"

    date = fields.Date(string="Payment Date", required=True, help="Date of the payment")
    employee_id = fields.Many2one('hr.employee', string="Employee", help="Employee")
    amount = fields.Float(string="Amount", required=True, help="Amount")
    paid = fields.Boolean(string="Paid", help="Paid")
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.", help="Loan")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.", help="Payslip")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_employee_loans(self):
        """This compute the loan amount and total loans count of an employee.
            """
        self.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', self.id)])

    loan_count = fields.Integer(string="Loan Count", compute='_compute_employee_loans')
