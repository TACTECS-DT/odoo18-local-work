# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Fields
    use_contract = fields.Selection(
        string='Use Contract',
        related='company_id.use_contract',
        readonly=True,
    )
    contract_id = fields.Many2one(
        string='Contract',
        comodel_name='xf.partner.contract',
        ondelete='restrict',
        domain=[('state', '=', 'running')],
    )

    # Compute and search fields, in the same order of fields declaration
    # Constraints and onchanges
    # Built-in methods overrides
    # Action methods

    def apply_contract(self):
        for move in self:
            if not move.contract_id:
                continue
            invoice_vals = move.contract_id._prepare_invoice(move.move_type)
            move.write(invoice_vals)
            move.apply_contract_lines()

    def apply_contract_lines(self):
        for move in self:
            if not move.contract_id:
                continue
            lines = self.env['account.move.line']
            for line in move.contract_id.line_ids:
                invoice_line_vals = line._prepare_invoice_line(move.id)
                invoice_line = lines.new(invoice_line_vals)
                invoice_line.account_id = invoice_line._get_computed_account()
                invoice_line._onchange_currency()
                invoice_line._onchange_price_subtotal()
                lines |= invoice_line
            move.with_context(check_move_validity=False).line_ids = lines
            move.with_context(check_move_validity=False)._onchange_invoice_line_ids()

    # Business methods

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'SaleOrder'
    contract_id = fields.Many2one(
            string='Contract',
            comodel_name='xf.partner.contract',
            ondelete='restrict',
            domain=[('state', '=', 'running')],
        ) 


    
