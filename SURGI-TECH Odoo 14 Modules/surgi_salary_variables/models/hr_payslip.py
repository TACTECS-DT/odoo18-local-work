from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    shiftallownece=fields.Float(string="night shift allownece",compute='_get_night_allownece')
    def _get_night_allownece(self):
        attendence = self.env['attendance.sheet'].search(
            [('employee_id', '=', self.employee_id.id),
             ('accrual_date', '>=', self.date_from),
             ('accrual_date', '<=', self.date_to),
             
             ])
        self.shiftallownece= attendence.tot_shift_allowance

    # @api.model
    # def create(self, vals):
    #     res = super(HrPayslip, self).create(vals)
    #     variable_allowance = self.env['hr.variable.allowance.request'].search(
    #         [('employee_id', '=', res.employee_id.id),
    #          ('date', '>=', res.date_from),
    #          ('date', '<=', res.date_to),
    #          ('state','=','confirmed')
    #          ])
    #     print(variable_allowance,'LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL')
    #     data = {}
    #     for it in variable_allowance:
    #         tmp = data.get(it.rule_id.code, {})
    #         tmp = tmp.get('amount', 0) if tmp else 0
    #         data.update({
    #             it.rule_id.code: {
    #                 'amount': it.amount + tmp,
    #                 'input_type_id': it.rule_id.payslip_input_type_id.id
    #             }
    #         })
    #
    #     for key in data:
    #         self.env['hr.payslip.input'].create({
    #             'input_type_id': data[key].get('input_type_id'),
    #             'amount': data[key].get('amount'),
    #             'payslip_id': res.id
    #         })
    #     print(data,'KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK22222222222222222')
    #
    #     return res

    def compute_sheet(self):
        variable_allowance = self.env['hr.variable.allowance.request'].search(
            [('employee_id', '=', self.employee_id.id),
             ('date', '>=', self.date_from),
             ('date', '<=', self.date_to),
             ('state', '=', 'approved')
             ])
        data = {}



        if self.input_line_ids:
            for varrib in variable_allowance:
                for inp in self.input_line_ids:
                    if varrib.rule_id.payslip_input_type_id.id == inp.input_type_id.id:
                        inp.unlink()

        for it in variable_allowance:
            tmp = data.get(it.rule_id.code, {})
            tmp = tmp.get('amount', 0) if tmp else 0
            data.update({
                it.rule_id.code: {
                    'amount': it.amount + tmp,
                    'input_type_id': it.rule_id.payslip_input_type_id.id
                }
            })

        for key in data:
            self.env['hr.payslip.input'].create({
                'input_type_id': data[key].get('input_type_id'),
                'amount': data[key].get('amount'),
                'payslip_id': self.id
            })




        res = super(HrPayslip, self).compute_sheet()
        return res
