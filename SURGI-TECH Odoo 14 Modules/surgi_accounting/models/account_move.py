# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta,datetime
from itertools import groupby
from itertools import zip_longest
from hashlib import sha256
# from json import dumps
#
# import json
# import re

class AccountInvoiceInherit(models.Model):
    _inherit = 'account.move'

    customer_printed_name = fields.Char(string="Customer Printed Name")
    sales_area_manager = fields.Many2one(comodel_name='res.users', string="Area Manager", readonly=True)#related='team_id.user_id',
    collection_rep = fields.Many2one('res.users', 'Collection Rep', track_visibility='onchange')

    invoice_printing_description = fields.Text('Invoice Printing Description')
    print_description = fields.Boolean('Print Description', default=False)
    exchange_invoices = fields.Boolean("Exchanged invoices")
    exchange_invoices_id = fields.Many2one('account.move', 'Exchange invoices No.')

    date_reconcile = fields.Date(string="Date", )#compute='_compute_payments_widget_reconciled_info'
    payment_name = fields.Char(string="Payment Name",)#compute='_compute_payments_widget_reconciled_info'

    is_reviewed = fields.Boolean(string="IS Reviewed", tracking=True)
    close_edit = fields.Boolean(string="", compute='compute_close_edit')
    close_edit22 = fields.Char(string="", )

    payment_date_paid = fields.Date(string="Payment Date",)
    check_payment_date_paid= fields.Boolean(compute='compute_edit_invoice_payments_widget'  )
    creditNoteReason = fields.Char(string="Credit Note Reason",readonly=True,store=True)
    CreditNoteMethod = fields.Selection(selection=[
            ('refund', 'Partial Refund'),
            ('cancel', 'Full Refund'),
            ('modify', 'Full refund and new draft invoice')
        ], string='Credit Note Method',readonly=True,store=True)
    creditNoteOrginlMove = fields.Char(string="Orginal Move",readonly=True,store=True)
    entry_reviewed_on = fields.Char(string="Entry Reviewed On",readonly=True)
    entry_reviewed_by = fields.Char(string="Entry Reviewed By",readonly=True)
    def _get_reconciled_info_JSON_values(self):
        res=super(AccountInvoiceInherit, self)._get_reconciled_info_JSON_values()
        for rec in res:
            payment_account=self.env['account.payment'].search([('id','=',rec['account_payment_id'])],limit=1)
            if self.payment_date_paid:
                rec['date']=self.payment_date_paid
                payment_account.date=self.payment_date_paid
                payment_account.move_id.date=self.payment_date_paid

                return res
            else:
                return res



    @api.depends('payment_date_paid','invoice_payments_widget')
    def compute_edit_invoice_payments_widget(self):
        lines_dic={}
        for rec in self:
            rec.check_payment_date_paid=False
            if rec.payment_date_paid and rec.invoice_payments_widget:
                rec.check_payment_date_paid=True
                # rec._get_reconciled_info_JSON_values()



    @api.depends('is_reviewed')
    def compute_close_edit(self):
        for rec in self:
            rec.close_edit = False
            if rec.is_reviewed == True and not self.env.user.has_group('surgi_analytic_account.group_is_reviewed'):
                rec.close_edit = True
                rec.close_edit22 = '1'

    def button_reviewed(self):
        user = self.env.user
        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
        self.entry_reviewed_on = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.entry_reviewed_by = user_name
        self.is_reviewed = True

    def button_double_reviewed(self):
        self.is_reviewed = False








    # @api.depends('type', 'line_ids.amount_residual')
    # def _compute_payments_widget_reconciled_info(self):
    #     self.date_reconcile=False
    #     self.payment_name=""
    #     for move in self:
    #         if move.state != 'posted' or not move.is_invoice(include_receipts=True):
    #             move.invoice_payments_widget = json.dumps(False)
    #             continue
    #         reconciled_vals = move._get_reconciled_info_JSON_values()
    #         print("111111111111",reconciled_vals)
    #         for recs in reconciled_vals:
    #             move.date_reconcile = recs['date']
    #
    #         for pay in self.env['account.payment'].search([]):
    #             if move.id in pay.invoice_ids.ids:
    #                 print("1111111111111ffffffffffffffffffffffffffffffffffffffffffffffff",pay.name)
    #                 move.payment_name = pay.name
    #
    #         if reconciled_vals:
    #             info = {
    #                 'title': _('Less Payment'),
    #                 'outstanding': False,
    #                 'content': reconciled_vals,
    #             }
    #             move.invoice_payments_widget = json.dumps(info, default=date_utils.json_default)
    #         else:
    #             move.invoice_payments_widget = json.dumps(False)


class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'


    def _prepare_default_reversal(self, move):
        reverse_date = self.date if self.date_mode == 'custom' else move.date
        if move.printinvoicetoline:
            result = []
            print(move.id)
            invModel = self.env['account.move.printedinvoice.lines'].search([('linestoprintinvoice','=',move.id)])
            print(invModel)
            for inv in invModel:

                result.append((0, 0, {
                    'id':inv.id,
                    'sequance': inv.sequance,
                    'product_id': inv.product_id.id,
                    'description':inv.description,
                    'uquantity':inv.uquantity,
                    'uprice':inv.uprice,
                    'total':inv.total,
                    }))
        if len(result) <1:
            raise UserError("Please Provide Print Invoice Lines")
        return {
            'ref': _('Reversal of: %(move_name)s, %(reason)s', move_name=move.name, reason=self.reason)
                   if self.reason
                   else _('Reversal of: %s', move.name),
            'date': reverse_date,
            'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
            'journal_id': self.journal_id and self.journal_id.id or move.journal_id.id,
            'invoice_payment_term_id': None,
            'invoice_user_id': move.invoice_user_id.id,
            'auto_post': True if reverse_date > fields.Date.context_today(self) else False,
            'creditNoteReason' :self.reason,
            'CreditNoteMethod' : self.refund_method,
            'creditNoteOrginlMove' : move.name,
            'printinvoicetoline':result,
        }
