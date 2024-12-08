from odoo import models, fields, api

class AccountCashGroup(models.Model):
    _name = "account.cash.group"
    _description = 'Account Cash Group'
    # _parent_store = True
    # _order = 'code_prefix_start'

    # parent_id = fields.Many2one('account.group', index=True, ondelete='cascade', readonly=True)
    # parent_path = fields.Char(index=True)
    name = fields.Char(required=True)
    # code_prefix_start = fields.Char()
    # code_prefix_end = fields.Char()
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)

class AccountAccountInherit(models.Model):
    _inherit = 'account.account'

    cash_group_id = fields.Many2one('account.cash.group', string='Cash Group', store=True)
