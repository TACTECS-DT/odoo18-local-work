from odoo import models, fields, api,_
from datetime import date,datetime,time,timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class HrExpensesExpenses(models.Model):
    _name = 'hr.expenses.expenses'
    _rec_name = 'expensescc_id'

    expensescc_id = fields.Many2one(comodel_name="hr.expense", string="Expenses",)
    date = fields.Date(string="Date", required=False, )
    total_amount = fields.Float(string="Total Amount",  required=False, )
    expen_id = fields.Many2one(comodel_name="hr.expense", string="", required=False, )




class HRExpensesInherit(models.Model):
    _inherit = 'hr.expense'
    product_id = fields.Many2one('product.product', string='Product', readonly=True, tracking=True, states={'draft': [('readonly', False)], 'reported': [('readonly', False)], 'refused': [('readonly', False)], 'approved': [('readonly', False)]}, domain="[('can_be_expensed', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", ondelete='restrict')

    sales_id = fields.Many2one(comodel_name="operation.operation", string="Operation",)
    sales_state = fields.Char(string="Sales State",compute='compute_sales_state')
    operations_type = fields.Many2one(comodel_name="product.operation.type", string="Operation Type",)
    is_sales = fields.Boolean(string="IS Sales",related='product_id.is_sales_order')

    # expenses_ids = fields.Many2many(comodel_name="hr.expense", relation="expenses_relation", column1="expenses_col1", column2="expenses_col2", string="Expenses",)
    expenses_lines_ids = fields.One2many(comodel_name="hr.expenses.expenses", inverse_name="expen_id", string="", required=False, )
    is_expenses_ids = fields.Boolean(string="",compute='filter_sales_id'  )

    partner_surgeon_id = fields.Many2one(comodel_name="res.partner", string="Surgeon")
    event_id = fields.Many2one(comodel_name="hr.expenses.event", string="Event", )
    sale_order_mandatory = fields.Boolean(string="Sale Order Mandatory",related='product_id.property_account_expense_id.sale_order_mandatory')

    total_expense_amount = fields.Float(string="Total Amount",compute='compute_total_expense_amount')

    num_day_expire = fields.Integer(compute='compute_num_day_expire' )



    @api.model
    def default_get(self,fields):
        res = super(HRExpensesInherit,self).default_get(fields)
        res['payment_mode']='company_account'
        return res


    def _get_account_move_line_values(self):
        res = super(HRExpensesInherit,self)._get_account_move_line_values()
        move_line_values_by_expense = {}
        for expense in self:
            move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:256]
            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id

            move_line_values = []
            taxes = expense.tax_ids.with_context(round=True).compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            partner_id = expense.employee_id.sudo().address_home_id.commercial_partner_id.id

            # source move line
            balance = expense.currency_id._convert(taxes['total_excluded'], company_currency, expense.company_id, account_date)
            amount_currency = taxes['total_excluded']
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': balance if balance > 0 else 0,
                'credit': -balance if balance < 0 else 0,
                'amount_currency': amount_currency,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'tax_tag_ids': [(6, 0, taxes['base_tags'])],
                'currency_id': expense.currency_id.id,
            }
            move_line_values.append(move_line_src)
            total_amount -= balance
            total_amount_currency -= move_line_src['amount_currency']

            # taxes move lines
            for tax in taxes['taxes']:
                balance = expense.currency_id._convert(tax['amount'], company_currency, expense.company_id, account_date)
                amount_currency = tax['amount']

                if tax['tax_repartition_line_id']:
                    rep_ln = self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
                    base_amount = self.env['account.move']._get_base_amount_to_display(tax['base'], rep_ln)
                else:
                    base_amount = None

                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': balance if balance > 0 else 0,
                    'credit': -balance if balance < 0 else 0,
                    'amount_currency': amount_currency,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_repartition_line_id': tax['tax_repartition_line_id'],
                    'tax_tag_ids': tax['tag_ids'],
                    'tax_base_amount': base_amount,
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id,
                    'analytic_account_id': expense.analytic_account_id.id if tax['analytic'] else False,
                    'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)] if tax['analytic'] else False,
                }
                total_amount -= balance
                total_amount_currency -= move_line_tax_values['amount_currency']
                move_line_values.append(move_line_tax_values)

            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount_currency,
                'currency_id': expense.currency_id.id,
                'expense_id': expense.id,
                'partner_id': partner_id,
            }
            move_line_values.append(move_line_dst)

            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense












    def get_all_operation_type(self):
        for rec in self.search([]):
            if not rec.operations_type:
                rec.operations_type = rec.sales_id.operation_type

    @api.onchange('sales_id')
    def compute_operations_type(self):
        self.operations_type = self.sales_id.operation_type

    # # def write(self, vals):
    # #     res=super(HRExpensesInherit, self).write(vals)
    # #     if self.env.user.has_group('surgi_sales_expenses.expenses_only_view_group') and vals:
    # #         print(res,"HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
    # #         raise UserError(_('Permission Denied.'))
    # #
    # #     return res

    def compute_num_day_expire(self):
        expiration_rec = self.env['hr.expense.expiration'].search([],limit=1)
        for rec in self:
            rec.num_day_expire=expiration_rec.num_day_expire
            if rec.num_day_expire:

                rec.filter_value_sales()

    #@api.depends('sales_id','expenses_lines_ids')
    def compute_total_expense_amount(self):
        for rec in self:
            total_expense_amount=0.0
            for line in rec.expenses_lines_ids:
                total_expense_amount+=line.total_amount
            rec.total_expense_amount=total_expense_amount
    @api.depends('sales_id')
    def compute_sales_state(self):
        for rec in self:
            rec.sales_state=''
            if rec.sales_id:
                rec.sales_state =rec.sales_id.state



    @api.onchange('name','date','sales_id')
    def filter_value_sales(self):
        sales_list=[]
        # pass
        # Ahmed Edit "%Y-%m-%d 00:00:00"
        today_date = datetime.strptime(str(date.today()), '%Y-%m-%d').date()
        operation_rec = self.env['operation.operation'].search([('create_date','>=','2023-01-01 00:00:00')])
        expiration_rec = self.env['hr.expense.expiration'].search([],limit=1)
        for rec in operation_rec:
            if rec.start_datetime:
                date_order = datetime.strptime(str(rec.start_datetime).split(".")[0],
                                                      '%Y-%m-%d %H:%M:%S').date()

                if expiration_rec and int(str((today_date - date_order).days))<=expiration_rec.num_day_expire:
                    sales_list.append(rec.id)
        return {
            'domain': {'sales_id': [('id', 'in',sales_list )]}
        }

    # @api.depends('sales_id')
    def filter_sales_id(self):
        # pass
        # ahmed Edit
        for expen in self:
            line_list = [(5,0,0)]
            expen.is_expenses_ids=False
            for rec in self.search([('create_date','>=','2023-01-01 00:00:00')]):
                if expen._origin.id !=rec.id and expen.sales_id.id==rec.sales_id.id:
                    line_list.append((0,0,{
                        'expensescc_id': rec.id,
                        'date': rec.date,
                        'total_amount': rec.total_amount,
                    }))
                    expen.is_expenses_ids=True
            if expen.sales_id and line_list:
                expen.update({'expenses_lines_ids':line_list})
            else:
                expen.expenses_lines_ids=False

    @api.onchange('employee_id','product_id')
    def filter_product_id(self):
        product_list=[]
        #ahmed Edit
        for rec in self.env['product.product'].search([('can_be_expensed', '=', True)]):
            if self.employee_id.department_id.id in rec.department_ids.ids:
                product_list.append(rec.id)

        return {
            'domain': {'product_id': [('id', 'in', product_list)]}
        }

class HrExpenseSheetInherit(models.Model):
    _inherit = 'hr.expense.sheet'

    account_reviewed= fields.Boolean(string="Account Reviewed",  readonly=True)
    treasury_manager= fields.Boolean(string="Treasury Manager",readonly=True  )
    check_access_expense = fields.Boolean(compute="compute_check_access_expense")
    
    secend_user_id = fields.Many2one('res.users', 'Seceond Approve', store=True,default="", readonly=False, copy=False, tracking=True, domain=lambda self: [('groups_id', 'in', self.env.ref('hr_expense.group_hr_expense_team_approver').id)])
    show_secend_approve= fields.Boolean(string="Secend Approve",store=True)
    secend_approved_done=fields.Boolean(readonly=True,store=True)


    cfo_user_id = fields.Many2one('res.users', string='CFO Approve', store=True,default="", domain=lambda self: [('groups_id', 'in', self.env.ref('hr_expense.group_hr_expense_team_approver').id)] ,readonly=False, copy=False, tracking=True)
    show_CFO_approve= fields.Boolean(string="CFO Approve",store=True)
    CFO_approved_done=fields.Boolean(string="CFO Approve Done",readonly=True,store=True)

    secend_approved_on= fields.Char(string="Second Approve On", readonly=True)
    secend_approved_by=fields.Char(string='Second Approve by', readonly=True)

    cfo_approved_on= fields.Char(string="CFO Approve On", readonly=True)
    cfo_approved_by=fields.Char(string='CFO Approve by', readonly=True)

    expenses_created_on = fields.Char(string="Created On Date", readonly=True)
    expenses_created_by = fields.Char(string="Created by", readonly=True)

    expenses_approve_on = fields.Char(string="Approved On",readonly=True)
    expenses_approve_by = fields.Char(string="Approved By",readonly=True)
    account_reviewed_on = fields.Char(string="Account Reviewed On",readonly=True)
    account_reviewed_by = fields.Char(string="Account Reviewed By",readonly=True)
    treasury_manager_on = fields.Char(string="Treasury Manager On",readonly=True)
    treasury_manager_by = fields.Char(string="Treasury Manager By",readonly=True)
    submitted_on = fields.Char(string="Submitted On",readonly=True)
    submitted_by = fields.Char(string="Submitted By",readonly=True)
    post_on = fields.Char(string="Posted On",readonly=True)
    post_by = fields.Char(string="Posted By",readonly=True)
    reset_on =fields.Char(string="Reset To Draft On",readonly=True)
    reset_by = fields.Char(string="Reset To Draf By", readonly=True)
    state = fields.Selection(selection_add=[('secend_approve', 'Second Approved'),('cfo_approve', 'CFO Approved'),("post",)], ondelete={'secend_approve': 'set default','cfo_approve': 'set default'}  )

    is_have_operation_record = fields.Boolean(compute='check_is_have_operation_record')

    def check_is_have_operation_record(self):
        for rec in self:
            is_have = False
            for res in rec.expense_line_ids:
                if res.sales_id:
                    is_have = True
            rec.is_have_operation_record = is_have
    @api.model
    def button_secend_approve_view_action(self):

        user = self.env.user
        operators = []
        domain = []
        counter = 0
        if user.has_group('surgi_sales_expenses.expenses_menu_sceond'):
            domain = [
                ('secend_user_id','=',user.id),
                ('state', 'in', ['approve']),
                ('show_secend_approve', '=', True),
            ]

        value = {
            'name': 'Reportes To Second Approve',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense.sheet',
            'type': 'ir.actions.act_window',
            'domain': domain,
            # 'context': context
        }
        return value

    @api.model
    def button_cfo_approve_view_action(self):

        user = self.env.user
        operators = []
        domain = []
        counter = 0
        if user.has_group('surgi_sales_expenses.expenses_cfo_sceond'):
            domain = [
                ('cfo_user_id','=',user.id),
                ('state', 'in', ['approve']),
                ('show_CFO_approve', '=', True),
            ]

        value = {
            'name': 'CFO Approve',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense.sheet',
            'type': 'ir.actions.act_window',
            'domain': domain,
            # 'context': context
        }
        return value




    def _get_responsible_for_approval(self):
        res = super(HrExpenseSheetInherit, self)._get_responsible_for_approval()

        if self.user_id:
            return self.user_id
        elif self.employee_id.parent_id.user_id:
            return self.employee_id.parent_id.user_id
        elif self.employee_id.department_id.manager_id.user_id:
            return self.employee_id.department_id.manager_id.user_id
        elif self.secend_user_id:
            return self.secend_user_id
        elif self.cfo_user_id:
            return self.cfo_user_id
        return self.env['res.users']

    @api.model
    def create(self,vals):
        if not (vals.get('expenses_created_on') and vals.get('expenses_created_by')) :

            user = self.env.user

            user_name = user.name
            now = datetime.now() + timedelta(hours=2)
                # self.started_op_date=datetime.now(),
            vals['expenses_created_on'] = now.strftime("%m/%d/%Y, %H:%M:%S")
            vals['expenses_created_by'] = user_name
        res = super(HrExpenseSheetInherit, self).create(vals)

        return res
    def secend_approve_expense_sheets(self):
        if not self.env.user.has_group('surgi_sales_expenses.expenses_menu_sceond'):
            raise UserError('You Not Allowed To Second Approve')
        responsible_id = self.secend_user_id.id or self.env.user.id
        self.secend_approved_done= True
        self.show_secend_approve = False
        user = self.env.user
        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
            # self.started_op_date=datetime.now(),
        self.secend_approved_on = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.secend_approved_by = user_name
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no expense reports to approve.'),
                'type': 'warning',
                'sticky': False,  #True/False will display for few seconds if false
            },
        }
        sheet_to_approve = self.filtered(lambda s: s.state in ['submit', 'draft','approve'])
        if sheet_to_approve:
            notification['params'].update({
                'title': _('The expense reports were successfully approved.'),
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            })
            sheet_to_approve.write({'state': 'approve', 'secend_user_id': responsible_id})
        self.activity_update()
        return notification

    def cfo_approve_expense_sheets(self):

        responsible_id = self.cfo_user_id.id or self.env.user.id
        self.CFO_approved_done= True
        self.show_CFO_approve = False
        user = self.env.user
        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
            # self.started_op_date=datetime.now(),
        self.cfo_approved_on = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.cfo_approved_by = user_name
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no expense reports to approve.'),
                'type': 'warning',
                'sticky': False,  #True/False will display for few seconds if false
            },
        }
        sheet_to_approve = self.filtered(lambda s: s.state in ['submit', 'draft','approve','post',])
        if sheet_to_approve:
            notification['params'].update({
                'title': _('The expense reports were successfully approved.'),
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            })
            sheet_to_approve.write({'state': 'approve', 'cfo_user_id': responsible_id})
        self.activity_update()
        return notification

    def approve_expense_sheets(self):
        if not self.user_has_groups('hr_expense.group_hr_expense_team_approver'):
            raise UserError(_("Only Managers and HR Officers can approve expenses"))

        elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
            current_managers = self.employee_id.expense_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own expenses"))

            if not self.env.user in current_managers and not self.user_has_groups('hr_expense.group_hr_expense_user') and self.employee_id.expense_manager_id != self.env.user:
                raise UserError(_("You can only approve your department expenses"))
        if self.user_id == self.env.user:
            pass
        user = self.env.user
        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
            # self.started_op_date=datetime.now(),
        self.expenses_approve_on = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.expenses_approve_by = user_name
        res = super(HrExpenseSheetInherit, self).approve_expense_sheets()

        return res


    def action_submit_sheet(self):

        user = self.env.user
        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
            # self.started_op_date=datetime.now(),
        self.submitted_on = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.submitted_by = user_name

        res = super(HrExpenseSheetInherit, self).action_submit_sheet()

        self.write({'state': 'submit'})
        self.activity_update()
        return  res

    @api.depends('state')
    def compute_check_access_expense(self):
        for rec in self:

            if rec.state in ['draft','submit']:

                rec.check_access_expense = True
            elif not self.env.user.has_group('surgi_sales_expenses.expenses_add_line_group') and rec.state=='approve' :

                rec.check_access_expense = False
            elif self.env.user.has_group('surgi_sales_expenses.expenses_add_line_group') :

                rec.check_access_expense = True
            else:

                rec.check_access_expense = False

    def button_account_reviewed(self):
        user = self.env.user
        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
            # self.started_op_date=datetime.now(),
        self.account_reviewed_on = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.account_reviewed_by = user_name


        self.account_reviewed=True
    def button_treasury_manager(self):
        user = self.env.user
        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
            # self.started_op_date=datetime.now(),
        self.treasury_manager_on = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.treasury_manager_by = user_name


        self.treasury_manager=True

    def action_sheet_move_create(self):
        res=super(HrExpenseSheetInherit, self).action_sheet_move_create()

        user = self.env.user
        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
            # self.started_op_date=datetime.now(),
        self.post_on = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.post_by = user_name

        if self.account_move_id:
            self.account_move_id.date=date.today()
            self.account_move_id.expenses_created_on = self.expenses_created_on
            self.account_move_id.expenses_created_by = self.expenses_created_by
            self.account_move_id.expenses_approve_on=self.expenses_approve_on
            self.account_move_id.expenses_approve_by=self.expenses_approve_by
            self.account_move_id.account_reviewed_on=self.account_reviewed_on
            self.account_move_id.account_reviewed_by=self.account_reviewed_by
            self.account_move_id.treasury_manager_on=self.treasury_manager_on
            self.account_move_id.treasury_manager_by=self.treasury_manager_by
            self.account_move_id.submitted_on=self.submitted_on
            self.account_move_id.submitted_by=self.submitted_by
            self.account_move_id.post_on=self.post_on
            self.account_move_id.post_by=self.post_by
            self.account_move_id.reset_on=self.reset_on
            self.account_move_id.reset_by=self.reset_by
            self.account_move_id.secend_approved_on=self.secend_approved_on
            self.account_move_id.secend_approved_by=self.secend_approved_by
            self.account_move_id.cfo_approved_on=self.cfo_approved_on
            self.account_move_id.cfo_approved_by=self.cfo_approved_by

            # for rec in self.expense_line_ids:
            #     for line in self.account_move_id.line_ids:
            #         # if rec.product_id==line.product_id:
            #             line.name= "["+rec.product_id.default_code+"]" +" " +rec.product_id.name
        return res
    def reset_expense_sheets(self):
        user = self.env.user
        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
            # self.started_op_date=datetime.now(),
        self.reset_on = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.reset_by = user_name
        res = super(HrExpenseSheetInherit, self).reset_expense_sheets()

        return res

class AccountAccountInherit(models.Model):
    _inherit = 'account.account'

    sale_order_mandatory = fields.Boolean(string="Sale Order Mandatory",  )
