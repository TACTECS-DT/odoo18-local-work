
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo import tools, _
import time
import babel
import logging



class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    sin_exist = fields.Boolean("Has Social Insurance")
    registration_number = fields.Char('Registration Number of the Employee', groups="hr.group_hr_user", copy=False)
    sin_no = fields.Char("Social Insurance No",tracking=True)
    sin_date = fields.Date("Social Insurance Start Date",tracking=True)
    sin_end_date = fields.Date("Social Insurance End Date",tracking=True)
    sin_title = fields.Char(string="Social Job Title",tracking=True)
    mi_exist = fields.Boolean("Has Medical Insurance",tracking=True)
    mi_company = fields.Selection(string="Medical Co.", selection=[('inaya', 'Inaya')])
    mi_no = fields.Char(string="Medical Insurance NO", help='Medical  Insurance No',tracking=True)
    mi_date = fields.Date(string="Medical Insurance Date", help='Medical  Insurance Date',tracking=True)
    sin_basic_salary = fields.Float(string="Basic Salary SIN", digits=dp.get_precision('Payroll'),tracking=True)
    sin_variable_salary = fields.Float(string="Variable Salary SIN", digits=dp.get_precision('Payroll'),tracking=True)
    allowances = fields.Float(string="Allowances", digits=dp.get_precision('Payroll'),tracking=True)
    prev_raise = fields.Float(string="previous Annual Raises", digits=dp.get_precision('Payroll'),tracking=True)
    phone_limit = fields.Float(string="Phone Limit", digits=dp.get_precision('Payroll'),tracking=True)
    payment_method = fields.Selection([('cash', 'Cash'), ('bank', 'Bank')], string='Payment Method')

    wage = fields.Monetary('Wage', required=True, tracking=True, help="Employee's monthly gross wage.",compute='calculate_wage')
    door_type = fields.Selection([('indoor', 'In Door'), ('outdoor', 'Out Door')], string='Door Type', copy=False)

    @api.depends('basic_salary','basic_salary_precent')
    def calculate_wage(self):
        self.wage=0
        for rec in self:
            rec.wage = rec.basic_salary + rec.basic_salary_precent


    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.registration_number = self.employee_id.registration_number


class HrPaySlip(models.Model):
    _inherit = 'hr.payslip'

    employee_code = fields.Char(string="Employee Code", related='employee_id.registration_number', readonly=True)
    grade_id = fields.Many2one('grade.grade', related='employee_id.contract_id.grade_id', readonly=True)
    rank_id = fields.Many2one('rank.rank', related='employee_id.contract_id.rank_id', readonly=True)
    rang_id = fields.Many2one('rang.rang', related='employee_id.contract_id.rang_id', readonly=True)
    
#     def _get_night_allownece(self):
#         attendence = self.env['attendance.sheet'].search(
#             [('employee_id', '=', self.employee_id.id),
#              ('accrual_date', '>=', self.date_from),
#              ('accrual_date', '<=', self.date_to),
             
#              ])
#         self.shiftallownece= attendence.tot_shift_allowance

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'
# disable UserError(_("Some part of %s's calendar is not covered by any work entry. Please complete the schedule.", contract.employee_id.name)
    def _check_undefined_slots(self, work_entries, payslip_run):
        """
        Check if a time slot in the contract's calendar is not covered by a work entry
        """
        # work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
        # for work_entry in work_entries:
            # work_entries_by_contract[work_entry.contract_id] |= work_entry

        # for contract, work_entries in work_entries_by_contract.items():
            # calendar_start = pytz.utc.localize(datetime.combine(max(contract.date_start, payslip_run.date_start), time.min))
            # calendar_end = pytz.utc.localize(datetime.combine(min(contract.date_end or date.max, payslip_run.date_end), time.max))
            # outside = contract.resource_calendar_id._attendance_intervals_batch(calendar_start, calendar_end)[False] - work_entries._to_intervals()
            # if outside:
                # raise UserError(_("Some part of %s's calendar is not covered by any work entry. Please complete the schedule.", contract.employee_id.name))

    def compute_sheet(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': from_date.strftime('%B %Y'),
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        employees = self.with_context(active_test=False).employee_ids
        if not employees:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']

        contracts = employees._get_contracts(
            payslip_run.date_start, payslip_run.date_end, states=['open', 'close']
        ).filtered(lambda c: c.active)
        contracts._generate_work_entries(payslip_run.date_start, payslip_run.date_end)
        work_entries = self.env['hr.work.entry'].search([
            ('date_start', '<=', payslip_run.date_end),
            ('date_stop', '>=', payslip_run.date_start),
            ('employee_id', 'in', employees.ids),
        ])
        self._check_undefined_slots(work_entries, payslip_run)

        if(self.structure_id.type_id.default_struct_id == self.structure_id):
            work_entries = work_entries.filtered(lambda work_entry: work_entry.state != 'validated')
        #     if work_entries._check_if_error():
        #         return {
        #             'type': 'ir.actions.client',
        #             'tag': 'display_notification',
        #             'params': {
        #                 'title': _('Some work entries could not be validated.'),
        #                 'sticky': False,
        #             }
        #         }


        default_values = Payslip.default_get(Payslip.fields_get())
        payslip_values = [dict(default_values, **{
            'name': 'Payslip - %s' % (contract.employee_id.name),
            'employee_id': contract.employee_id.id,
            'credit_note': payslip_run.credit_note,
            'payslip_run_id': payslip_run.id,
            'date_from': payslip_run.date_start,
            'date_to': payslip_run.date_end,
            'contract_id': contract.id,
            'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
        }) for contract in contracts]

        payslips = Payslip.with_context(tracking_disable=True).create(payslip_values)
        for payslip in payslips:
            payslip._onchange_employee()

        # payslips.compute_sheet()
        # payslip_run.state = 'verify'
        #
        # return {
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'hr.payslip.run',
        #     'views': [[False, 'form']],
        #     'res_id': payslip_run.id,
        # }
