from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class NewModule(models.Model):
    _inherit = 'account.move'

    seq_name = fields.Char(string="Exp Ref No.")


class HRExpenseSheetInherit(models.Model):
    _inherit = 'hr.expense.sheet'

    seq_name = fields.Char(string="Exp Ref No.")

    def action_sheet_move_create(self):
        res = super(HRExpenseSheetInherit, self).action_sheet_move_create()
        if self.account_move_id:
            self.account_move_id.seq_name = self.seq_name
        return res


class HRExpenseInherit(models.Model):
    _inherit = 'hr.expense'

    is_trusts = fields.Boolean(string="IS Trust", related='account_id.is_trusts')

    expense_type = fields.Selection(
        string="Expense Type",
        selection=[
            ('direct_expense', 'Direct Expense'),
            ('trust', 'Trust'),
            ('trust_recon', 'Trust Reconciliation')
        ]
    )

    seq_name = fields.Char(string="Exp Ref No.", default='NEW')

    expense_reconciliation_id = fields.Many2one(
        comodel_name="hr.expense", string="Expense Reconciliation"
    )

    @api.onchange('expense_type')
    def filter_expense_reconciliation_id(self):
        # lines will store the IDs of related expenses
        lines = []
        if self.expense_type == 'trust_recon':
            for rec in self.env['hr.expense'].search([]):
                if rec.expense_type == 'trust':
                    lines.append(rec.id)
            return {'domain': {'expense_reconciliation_id': [('id', 'in', lines)]}}

    @api.model_create_multi
    def create(self, values):
        for val in values:
            if val.get('expense_type') == 'direct_expense':
                val['seq_name'] = self.env['ir.sequence'].next_by_code('direct.expense.sequence') or _('New')
            elif val.get('expense_type') == 'trust':
                val['seq_name'] = self.env['ir.sequence'].next_by_code('trust.expense.sequence') or _('New')
            elif val.get('expense_type') == 'trust_recon':
                val['seq_name'] = self.env['ir.sequence'].next_by_code('reconciliation.trust.expense.sequence') or _('New')

        # The following commented-out section adjusts sequence behavior for partners
        # but is not used in the current implementation.
        # partners = super(HRExpenseInherit, self).create(values)
        # for partner in partners:
        #     if partner.customer_rank == 0 or partner.parent_id:
        #         for rec in self.env['ir.sequence'].search([]):
        #             if rec.code == 'library.card.number':
        #                 rec.number_next_actual -= 1
        #                 partner.ref = False
        #
        #             if rec.code in ['superMarket.cridit.number7', 'restaurants.cridit.number6', 'hotel.credit.number5',
        #                             'individuals.cash.number4', 'superMarket.cash.number3', 'li2.ca2.num2']:
        #
        #                 partner.ref = False
        #     else:
        #         partner.name = partner.name + "(" + str(partner.ref) + ")"

        res = super(HRExpenseInherit, self).create(values)
        return res

    def action_submit_expenses(self):
        res = super(HRExpenseInherit, self).action_submit_expenses()
        x = ''.join([rec.seq_name for rec in self])
        for rec in self:
            rec.sheet_id.seq_name = x
        return res

    def _create_sheet_from_expenses(self):
        if any(expense.state != 'draft' or expense.sheet_id for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report."))
        if any(not expense.product_id for expense in self):
            raise UserError(_("You cannot create a report without a product."))

        d = len(self.filtered(lambda rec: rec.expense_type == 'direct_expense'))
        t = len(self.filtered(lambda rec: rec.expense_type == 'trust'))
        r = len(self.filtered(lambda rec: rec.expense_type == 'trust_recon'))

        if not ((d >= 1 and t == 0 and r == 0) or (t >= 1 and d == 0 and r == 0) or (r >= 1 and d == 0 and t == 0)):
            raise UserError(_("Invalid combination of expense types."))

        todo = self.filtered(lambda x: x.payment_mode in ['own_account', 'company_account'])
        sheet = self.env['hr.expense.sheet'].create({
            'company_id': self.company_id.id,
            'employee_id': self[0].employee_id.id,
            'name': todo[0].name if len(todo) == 1 else '',
            'expense_line_ids': [(6, 0, todo.ids)]
        })
        return sheet


class AccountAccountInherit(models.Model):
    _inherit = 'account.account'

    is_trusts = fields.Boolean(string="Trust Account")


# Uncommented reporting logic for future integration
# class ReportAccountHashIntegrity(models.AbstractModel):
#     _name = 'report.account.report_invoice_with_payments'
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#
#         docs = self.env['hr.expense'].browse(docids)
#         print(docs, 'JJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ', docs)
#         return {
#             'doc_ids': docids,
#             'doc_model': 'hr.expense',
#             'docs': docs,
#         }
