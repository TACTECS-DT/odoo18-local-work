from odoo import models, fields, api


class AccountPaymentRegisterInherit(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        res = super(AccountPaymentRegisterInherit, self).action_create_payments()
        context = self._context

        if context.get('active_ids'):
            for register in context.get('active_ids'):
                for move in self.env['account.move'].browse(register):

                    move.check_number_payment = self.check_number
                    move.date_payment = self.date_due
                    move.collection_receipt_number = self.collection_receipt_number
                    for line in move.invoice_line_ids:

                        line.check_number_payment = self.check_number
                        line.collection_receipt_number = self.collection_receipt_number
                        line.date_payment = self.date_due

        return res


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    cost_center_ids = fields.One2many(comodel_name="cost.center.lines", inverse_name="partner_id", string="",
                                      required=False, )


class CostCenterLines(models.Model):
    _name = 'cost.center.lines'
    _rec_name = 'analytic_account_id'

    product_line_id = fields.Many2one(comodel_name="product.lines", string="Product Line", )
    analytic_account_id = fields.Many2one(comodel_name="account.analytic.account", string="Account Analytic Account", )
    partner_id = fields.Many2one(comodel_name="res.partner", string="", required=False, )


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    user_id = fields.Many2one(comodel_name="res.users", string="Salesperson", )
    user_add_ids = fields.Many2many(comodel_name="res.users", string="Additional Users", )

    salesteam_id = fields.Many2one(comodel_name="crm.team", string="Sales Team", )
    product_id = fields.Many2one(comodel_name="product.lines", string="Product Line old", )
    product_line_id = fields.Many2one(comodel_name="product.lines", string="Product Line", )
    undefined_sales_person = fields.Boolean(string="Undefined Sales Person", )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_id = fields.Many2one(comodel_name="product.lines", string="Product Line old", )
    product_line_id = fields.Many2one(comodel_name="product.lines", string="Product Line", )


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'
    date_check_number = fields.Boolean(string="", compute='compute_date_check_number_move')

    @api.depends('move_id', 'check_number', 'date_due', 'collection_receipt_number')
    def compute_date_check_number_move(self):
        self.date_check_number = False
        # for rec in self:
        #     if rec.move_id:
        #         rec.move_id.check_number_payment = rec.check_number
        #         rec.move_id.date_payment = rec.date_due
        #         rec.move_id.collection_receipt_number = rec.collection_receipt_number
        #         rec.date_check_number = True
        #         rec.move_id.compute_date_check_number()


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    check_number_payment = fields.Char(string="Check Number(Payment)", )
    date_payment = fields.Date(string="Due Date(Payment)", )
    collection_receipt_number = fields.Integer(string="Receipt Number(Payment)", required=False, )
    date_check_number = fields.Boolean(string="", )
    product_line = fields.Many2one(comodel_name="product.lines", related='product_id.product_line_id',
                                   string="Product Line",
                                   readonly=True, store=True)
    product_line_parent = fields.Char(related='product_id.product_line_id.product_line_parent',
                                      string="Product Line Parent",
                                      readonly=True, store=True)
    analytic_account_group_id = fields.Many2one(comodel_name='account.analytic.group',
                                                related='analytic_account_id.group_id',
                                                string='AC. Group', readonly=True, store=True)
    analytic_account_group_parent_id = fields.Many2one(comodel_name='account.analytic.group',
                                                       related='analytic_account_group_id.parent_id',
                                                       string='AC. Group Parent', readonly=True, store=True)
    sales_balance = fields.Monetary(string='Sales Balance',
                                    store=True,
                              currency_field='company_currency_id',
                              compute='compute_sales_balance_new',
                              help="Technical field holding the credit - debit in order to open meaningful graph views from reports")
    
    @api.depends('credit', 'debit')
    def compute_sales_balance_new(self):
        for line in self:
            line.sales_balance = line.credit - line.debit

    # def cron_all_account_move(self):
    #     for rec in self.search([]):
    #         if rec.move_id:
    #             rec.move_id.compute_date_check_number()
    #             rec.check_number_payment = rec.move_id.check_number_payment
    #             rec.collection_receipt_number = rec.move_id.collection_receipt_number
    #             rec.date_payment = rec.move_id.date_payment


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_check = fields.Boolean(string="Check", )

    check_number_payment = fields.Char(string="Check Number(Payment)", )
    date_payment = fields.Date(string="Due Date(Payment)", )
    collection_receipt_number = fields.Integer(string="Receipt Number(Payment)", required=False, )

    date_check_number = fields.Boolean(string="" , compute='compute_date_check_number')#

    def compute_date_check_number(self):
        self.date_check_number = False
        # for rec in self:
        #     for pay in self.env['account.payment'].search([]):
        #         if pay.move_id.id == rec.id or pay.ref == rec.name or str(rec.name) in str(pay.ref):
        #
        #             rec.date_check_number = True
        #             rec.check_number_payment = pay.check_number
        #             rec.collection_receipt_number = pay.collection_receipt_number
        #             rec.date_payment = pay.date_due
        #             for line in rec.invoice_line_ids:
        #
        #                 line.check_number_payment = pay.check_number
        #                 line.collection_receipt_number = pay.collection_receipt_number
        #                 line.date_payment = pay.date_due

    # @api.onchange('is_check')
    def compute_analytic_account(self):

        analytic_account_obj = self.env['account.analytic.account'].search([])
        lines_list = []
        part2=False
        for line in self.invoice_line_ids:

            if self.partner_id.cost_center_ids:

                for cost in self.partner_id.cost_center_ids:

                    if line.product_id.product_id.id == cost.product_line_id.id:

                        line.analytic_account_id = cost.analytic_account_id.id
                        lines_list.append(line.product_id.product_id.id)

                if line.product_id.product_id.id not in lines_list:

                    for rec in analytic_account_obj:
                        if line.product_id.product_id.id == rec.product_id.id:
                            if rec.user_id.id == self.invoice_user_id.id:

                                line.analytic_account_id = rec.id
                                break
                            elif self.invoice_user_id.id in rec.user_add_ids.ids:

                                line.analytic_account_id = rec.id
                                break
                            elif rec.undefined_sales_person == True:

                                line.analytic_account_id = rec.id
                                break


                        else:

                            line.analytic_account_id = False
            else:
                for rec in analytic_account_obj:
                    if line.product_id.product_id.id == rec.product_id.id:
                        if rec.user_id.id == self.invoice_user_id.id:

                            line.analytic_account_id = rec.id
                            break
                        elif self.invoice_user_id.id in rec.user_add_ids.ids:

                            line.analytic_account_id = rec.id
                            break
                        elif rec.undefined_sales_person == True:

                            line.analytic_account_id = rec.id
                            break


                    else:

                        line.analytic_account_id = False


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # name = fields.Char
    # user_sales_id = fields.Many2one(comodel_name="res.users",related="location_id.is_operation_location",  string="Salesperson", required=False, )

    is_check = fields.Boolean(string="Check", )

    # @api.onchange('is_check')
    def compute_analytic_account(self):

        analytic_account_obj = self.env['account.analytic.account'].search([])
        lines_list = []
        for line in self.move_ids_without_package:
            if self.partner_id.cost_center_ids:

                for cost in self.partner_id.cost_center_ids:

                    if line.product_id.product_id.id == cost.product_line_id.id:

                        line.analytic_account_id = cost.analytic_account_id.id
                        lines_list.append(line.product_id.product_id.id)

                if line.product_id.product_id.id not in lines_list:

                    for rec in analytic_account_obj:
                        if line.product_id.product_id.id == rec.product_id.id:
                            if rec.user_id.id == self.user_id.id:
                                line.analytic_account_id = rec.id
                                break
                            elif self.user_id.id in rec.user_add_ids.ids:
                                line.analytic_account_id = rec.id
                                break

                            elif rec.undefined_sales_person == True:

                                line.analytic_account_id = rec.id
                                break
                        else:

                            line.analytic_account_id = False
            else:
                for rec in analytic_account_obj:
                    if line.product_id.product_id.id == rec.product_id.id:
                        if rec.user_id.id == self.user_id.id:
                            line.analytic_account_id = rec.id
                            break
                        elif self.user_id.id in rec.user_add_ids.ids:
                            line.analytic_account_id = rec.id
                            break
                        elif rec.undefined_sales_person == True:
                            line.analytic_account_id = rec.id
                            break
                    else:

                        line.analytic_account_id = False
