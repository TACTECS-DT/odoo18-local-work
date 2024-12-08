from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime , date


class HrVariableAllowanceRequest(models.Model):
    _name = 'hr.variable.allowance.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    date = fields.Date()
    tmp_amount = fields.Float(compute='_compute_amount', store=True)
    amount_rate_multiplier = fields.Float(default=1.0)
    amount = fields.Float()

    rule_id = fields.Many2one('hr.variable.allowance.rule')
    rule_id_allowance_type = fields.Selection(related='rule_id.allowance_type', store=False)
    employee_id = fields.Many2one('hr.employee', default=lambda self: self.env.user.employee_id.id)

    registration_number = fields.Char(string="Employee Registration Number", required=False, )
    job_id = fields.Many2one(comodel_name="hr.job", string="Job",)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",)
    creation_date = fields.Date(string="Creation Date",default=date.today() )
    contract_id = fields.Many2one('hr.contract', compute='_get_contract_id', store=True)
    payslip_id = fields.Many2one('hr.payslip')
    allowance_approvals = fields.One2many('variable.allow.valid.status', 'variable_allowance_request_id',
                                          string='Allowance Validators',)
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('approved', 'Approved'),
                              ('refused', 'Refused'), ('hr_refused', 'HR Refused')], string='Status', copy=False, default='draft')

    type = fields.Selection([('var_internal_travel_exp_allow', 'Travel Allow Internal'),
                             ('var_external_travel_reward_allow', 'External Travel Reward Allow'),
                             ('var_accomod_allow', 'Accomod Allow'),
                             ('var_overtime_allow', 'Over Time Allow'),
                             ('var_collection_comm_allow', 'Collections Commissions'),
                             ('var_sales_comm_allow', 'Sales Commissions'),
                             ('var_manufacturing_comm_allow', 'Manufacturing Commissions'),
                             ('var_night_shift_allow', 'Night Shifts')],
                            string='Type', copy=False)
    check_allowance_type = fields.Selection(selection=[('my_request', 'My Request'),
                                                       ('manager_request', 'Manager Request'),
                                                       ('all_request', 'All Request'),

                                                       ], required=False, )



    def action_all_request(self):
        user = self.env.user
        domain = []
        if user.has_group('surgi_salary_variables.access_group_admin_request'):
            domain=[]
        elif user.has_group('surgi_salary_variables.access_group_user_request'):
            domain.append(('rule_id.administrator_ids','in',[user.id]))

        value = {
            'name': 'All Request',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.variable.allowance.request',
            'type': 'ir.actions.act_window',
            'domain': domain,
            'context':{'default_check_allowance_type':'all_request'}
        }
        return value

    @api.onchange('creation_date')
    def get_puplish_rules(self):
        allowance_rule_record = self.env['hr.variable.allowance.rule'].search([])
        lines_list=[]
        for rec in allowance_rule_record:

            if self.check_allowance_type == 'all_request' and self.env.user.has_group(
                'surgi_salary_variables.access_group_admin_request'):
                lines_list.append(rec.id)

            elif self.env.user.id in rec.administrator_ids.ids and self.check_allowance_type=='all_request' and self.env.user.has_group('surgi_salary_variables.access_group_user_request'):
                lines_list.append(rec.id)
                print("11111111111111111111111111111111")
            elif self.check_allowance_type != 'all_request':
                if rec.publish==True:
                    print("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
                    lines_list.append(rec.id)
            elif not lines_list:
                print("GGGGGGGGGGGGGGGGGGGGGGGGG")
                lines_list=[]


        return {'domain': {'rule_id': [('id', 'in',lines_list )]}}





    @api.depends('employee_id')
    def _get_contract_id(self):
        running_contracts = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                            ('state', '=', 'open')])
        if running_contracts:
            self.contract_id = running_contracts[0].id
        else:
            self.contract_id = False

    # by nextera start
    @api.depends('contract_id', 'rule_id', 'amount_rate_multiplier', 'type')
    def _compute_amount(self):
        for rec in self:
            # if rec.employee_id and rec.contract_id and rec.rule_id and rec.rule_id.allowance_type == 'rule':
            #     try:
            #         rec.tmp_amount = rec.amount_rate_multiplier * eval(rec.rule_id.rule, {'contract': rec.contract_id, 'employee': rec.employee_id})
            #         if rec.rule_id.allowance_or_deduction == 'deduction':
            #             rec.tmp_amount = abs(rec.tmp_amount) * -1
            #         rec.amount = rec.tmp_amount
            #     except:
            #         raise ValidationError("Wrong rule's syntax, please fix it and try again.")
            # else:
            #     rec.tmp_amount = 0
            if rec.type:
                if rec.type == 'var_internal_travel_exp_allow':
                    rec.tmp_amount = rec.contract_id.grade_id.var_internal_travel_exp_allow
                    rec.amount = rec.tmp_amount
                elif rec.type == 'var_external_travel_reward_allow':
                    rec.tmp_amount = rec.contract_id.grade_id.var_external_travel_reward_allow
                    rec.amount = rec.tmp_amount
                elif rec.type == 'var_accomod_allow':
                    rec.tmp_amount = rec.contract_id.grade_id.var_accomod_allow
                    rec.amount = rec.tmp_amount
                elif rec.type == 'var_overtime_allow':
                    rec.tmp_amount = rec.contract_id.grade_id.var_overtime_allow
                    rec.amount = rec.tmp_amount
                elif rec.type == 'var_collection_comm_allow':
                    rec.tmp_amount = rec.contract_id.grade_id.var_collection_comm_allow
                    rec.amount = rec.tmp_amount
                elif rec.type == 'var_sales_comm_allow':
                    rec.tmp_amount = rec.contract_id.grade_id.var_sales_comm_allow
                    rec.amount = rec.tmp_amount
                elif rec.type == 'var_manufacturing_comm_allow':
                    rec.tmp_amount = rec.contract_id.grade_id.var_manufacturing_comm_allow
                    rec.amount = rec.tmp_amount
                elif rec.type == 'var_night_shift_allow':
                    rec.tmp_amount = rec.contract_id.grade_id.var_night_shift_allow
                    rec.amount = rec.tmp_amount
            else:
                rec.tmp_amount = 0
    # by nextera end
    def write(self, vals):
        if self.rule_id.allowance_or_deduction == 'deduction':
            amount = vals.get('amount', None)
            if amount:
                vals['amount'] = abs(amount) * 1
                #vals['amount'] = abs(amount) * -1
        res = super(HrVariableAllowanceRequest, self).write(vals)
        return res

    # by kh.hb
    @api.onchange('employee_id','rule_id')
    def load_allowance_approvals(self):
        if self.employee_id:
            self.department_id=self.employee_id.department_id.id
            self.job_id=self.employee_id.job_id.id
            self.registration_number=self.employee_id.registration_number


            current_manager = None
            arr = [(5, 0, 0)]
            if self.employee_id.parent_id:
                current_manager = self.employee_id.parent_id
                arr.append((0, 0, {
                    'validating_user': self.employee_id.parent_id.user_id.id,
                }))
            # count = 0
            # while current_manager != self.employee_id.department_id.manager_id:
            #     if current_manager and current_manager.parent_id:
            #         arr.append((0, 0, {
            #             'validating_user': current_manager.parent_id.user_id.id,
            #         }))
            #         current_manager = current_manager.parent_id
            #     count += 1
                # if count == 15:
                #     raise UserError(_("the hierarchy position for this employee not specified correctly"))

            if arr:
                self.allowance_approvals = arr
                # self.update({'allowance_approvals': arr})
                # return arr

    # @api.model
    # def create(self, values):
    #     result = super(HrVariableAllowanceRequest, self).create(values)
    #     validators = self.load_allowance_approvals()
    #     result.allowance_approvals = validators
    #     return result

    def approval_check(self):
        # current_employee = self.employee_id
        if self.rule_id.need_approve == False:
            self.state='confirmed'
        elif not self.employee_id.department_id.manager_id and self.rule_id.need_approve == True:
            raise UserError(_("this employee Department not have a Manager plz set manager to this department"))

        elif self.rule_id.need_approve == True and self.env.user.id != self.employee_id.department_id.manager_id.user_id.id:
            raise UserError(_("Not Allow For You"))



        # active_id = self.env.context.get('active_id') if self.env.context.get(
        #     'active_id') else self.id
        #
        # allowance = self.env['hr.variable.allowance.request'].search([('id', '=', active_id)], limit=1)
        # is_validator = False
        # for user_obj in allowance.allowance_approvals.mapped(
        #         'validating_user').filtered(lambda l: l.id == self.env.uid):
        #     validation_obj = allowance.allowance_approvals.search(
        #         [('variable_allowance_request_id', '=', allowance.id),
        #          ('validating_user', '=', self.env.uid)])
        #     validation_obj.validating_state = 'accepted'
            is_validator = True
        # if not is_validator:
        #     raise UserError(_("you are not allowed to confirm to this employee"))
        # approval_flag = True
        # for user_obj in allowance.allowance_approvals:
        #     if not user_obj.validating_state == 'accepted':
        #         approval_flag = False
        # if approval_flag:
        #     allowance.write({'state': 'confirmed'})
        # else:
        #     return False

    def action_refuse(self):
        current_employee = self.employee_id
        approval_access = False
        for user in self.allowance_approvals:
            if user.validating_user.id == self.env.uid:
                approval_access = True
        if approval_access:
            is_refused = False
            for user_obj in self.allowance_approvals.mapped(
                    'validating_user').filtered(lambda l: l.id == self.env.uid):
                validation_obj = self.allowance_approvals.search(
                    [('variable_allowance_request_id', '=', self.id),
                     ('validating_user', '=', self.env.uid)])
                validation_obj.validating_state = 'refused'
                is_refused = True
            if is_refused:
                self.state = 'refused'
        # else:
        #     raise UserError(_("you are not allowed to Refuse to this employee"))

    def hr_approve(self):
        if self.state == 'confirmed':
            self.state = 'approved'
        else:
            raise UserError(_("the allowance should be in confirmed State"))

    def hr_refuse(self):
        if self.state == 'confirmed':
            self.state = 'hr_refused'

            ## For employee and department budget
            request_date = self.date
            if not self.budget_id.date_from <= request_date <= self.budget_id.date_to:
                raise ValidationError("Request date is out budget period.")

            employee_budget_line = self.env['allowance.employee.budget'].search(
                [('employee_id', '=', self.employee_id.id),
                 ('budget_id', '=', self.budget_id.id)])
            department_budget_line = self.env['allowance.department.budget'].search(
                [('department_id', '=', self.department_id.id),
                 ('budget_id', '=', self.budget_id.id)])

            flag1 = flag2 = False
            if employee_budget_line and (employee_budget_line[0].consumed_amount + self.amount) <= employee_budget_line[0].amount:
                flag1 = True

            if department_budget_line and (department_budget_line[0].consumed_amount + self.amount) <= department_budget_line[0].amount:
                flag2 = True

            if flag1 and flag2:
                employee_budget_line[0].consumed_amount += self.amount
                department_budget_line[0].consumed_amount += self.amount
                self.budget_id.consumed_budget += self.amount
            elif not flag1:
                raise ValidationError("This Employee is not added to this budget or have exceeded his limit")

            elif not flag2:
                raise ValidationError("This Employee's department is not added to this budget or have exceeded the department limit.")
        else:
            raise UserError(_("the allowance should be in confirmed State"))

    def send_notify(self):
        to_x = []
        to_x.append(self.allowance_approvals[0].validating_user.partner_id.id)
        self.message_post(body='This Allowance has been Notified!', message_type='snailmail',
                            subtype_xmlid='mail.mt_note', author_id=self.employee_id.user_id.partner_id.id,
                            partner_ids=to_x)


class LeaveValidationStatus(models.Model):
    _name = 'variable.allow.valid.status'

    variable_allowance_request_id = fields.Many2one('hr.variable.allowance.request')

    validating_user = fields.Many2one('res.users', string='Allowance Validators')
    validating_state = fields.Selection([('accepted', 'Accepted'), ('refused', 'Refused')])
    note = fields.Text(string='Comments', help="Comments")

    @api.onchange('validating_user')
    def prevent_change(self):
        raise UserError(_(
            "Changing Allowance validators is not permitted. You can only change "))
