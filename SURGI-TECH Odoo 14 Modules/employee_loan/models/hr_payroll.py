# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    loan_line_id = fields.Many2one('hr.loan.line', string="Loan Installment", help="Loan installment")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # @api.onchange('employee_id', 'date_from', 'date_to')
    # def onchange_employee(self):
    #     if (not self.employee_id) or (not self.date_from) or (not self.date_to):
    #         return
    #
    #     employee = self.employee_id
    #     date_from = self.date_from
    #     date_to = self.date_to
    #     contract_ids = []
    #
    #     ttyme = datetime.fromtimestamp(time.mktime(time.strptime(str(date_from), "%Y-%m-%d")))
    #     locale = self.env.context.get('lang') or 'en_US'
    #     self.name = _('Salary Slip of %s for %s') % (
    #         employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
    #     self.company_id = employee.company_id
    #
    #     if not self.env.context.get('contract') or not self.contract_id:
    #         contract_ids = self.get_contract(employee, date_from, date_to)
    #         if not contract_ids:
    #             return
    #         self.contract_id = self.env['hr.contract'].browse(contract_ids[0])
    #
    #     if not self.contract_id.struct_id:
    #         return
    #     self.struct_id = self.contract_id.struct_id
    #
    #     # computation of the salary input
    #     contracts = self.env['hr.contract'].browse(contract_ids)
    #     worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
    #     worked_days_lines = self.worked_days_line_ids.browse([])
    #     for r in worked_days_line_ids:
    #         worked_days_lines += worked_days_lines.new(r)
    #     self.worked_days_line_ids = worked_days_lines
    #     if contracts:
    #         input_line_ids = self.get_inputs(contracts, date_from, date_to)
    #         input_lines = self.input_line_ids.browse([])
    #         for r in input_line_ids:
    #             input_lines += input_lines.new(r)
    #         self.input_line_ids = input_lines
    #     return

    # def get_inputs(self, contract_ids, date_from, date_to):
    #     """This Compute the other inputs to employee payslip.
    #                        """
    #     res = super(HrPayslip, self).get_inputs(contract_ids, date_from, date_to)
    #     contract_obj = self.env['hr.contract']
    #     emp_id = contract_obj.browse(contract_ids[0].id).employee_id
    #     lon_obj = self.env['hr.loan'].search([('employee_id', '=', emp_id.id), ('state', '=', 'approve')])
    #     for loan in lon_obj:
    #         for loan_line in loan.loan_lines:
    #             if date_from <= loan_line.date <= date_to and not loan_line.paid:
    #                 for result in res:
    #                     if result.get('code') == 'LO':
    #                         result['amount'] = loan_line.amount
    #                         result['loan_line_id'] = loan_line.id
    #     return res

    # Added by me #########################
    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        res = []

        structure_ids = self.struct_id.id
        # rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        # sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]
        structures = self.env['hr.payroll.structure'].browse(structure_ids)

        for contract in contracts:
            for record in structures:
                for input in record.input_line_type_ids:
                    input_data = {
                        'name': input.name,
                        'code': input.code,
                        'contract_id': contract.id,
                        'input_type_id': input.id,
                    }
                    res += [input_data]

        contract_obj = self.env['hr.contract']
        emp_id = contract_obj.browse(contracts[0].id).employee_id
        lon_obj = self.env['hr.loan'].search([('employee_id', '=', emp_id.id), ('state', '=', 'approve')])
        for loan in lon_obj:
            for loan_line in loan.loan_lines:
                if date_from <= loan_line.date <= date_to and not loan_line.paid:
                    for result in res:
                        if result.get('code') == 'LO':
                            result['amount'] = loan_line.amount
                            result['loan_line_id'] = loan_line.id
        return res

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        super(HrPayslip, self)._onchange_employee()
        struct = self.struct_id
        contract = self.contract_id
        date_from = self.date_from
        date_to = self.date_to
        if contract:
            input_line_ids = self.get_inputs(contract, date_from, date_to)
            input_lines = self.input_line_ids.browse([])
            for r in input_line_ids:
                input_lines += input_lines.new(r)
            self.input_line_ids = input_lines
        return

    def action_payslip_done(self):
        for line in self.input_line_ids:
            if line.loan_line_id:
                line.loan_line_id.paid = True
        return super(HrPayslip, self).action_payslip_done()
