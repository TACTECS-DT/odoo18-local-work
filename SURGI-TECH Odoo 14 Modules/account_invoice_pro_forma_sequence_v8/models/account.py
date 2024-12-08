# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    pro_forma_number = fields.Char(string='Pro-forma number', readonly=True, copy=False)

    @api.multi
    def action_invoice_proforma2(self):
        sequence_obj = self.env['ir.sequence']
        for invoice in self:
            company = invoice.company_id
            if company.pro_forma_sequence:
                sequence = company.pro_forma_sequence
                invoice.pro_forma_number = sequence_obj.next_by_id(sequence.id)
                self.write({'state': 'proforma2'})
