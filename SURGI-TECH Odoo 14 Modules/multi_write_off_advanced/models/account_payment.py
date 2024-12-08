# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2019. All rights reserved.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime,date



class payment_register(models.TransientModel):
    _inherit = 'account.payment.register'

    payment_option = fields.Selection(
        [('full', 'Full Payment without Deduction'), ('partial', 'Full Payment with Deduction')], default='full',
        required=True, string='Payment Option')
    amount_pay_total = fields.Float('Amount Total', readonly=1)
    # amount = fields.Float('Payment Amount', readonly=1)
    post_diff_acc = fields.Selection([('single', 'Single Account'), ('multi', 'Multiple Accounts')], default='single',
                                     string='Post Difference In To')
    writeoff_multi_acc_ids = fields.One2many('writeoff.multi', 'register_id', string='Write Off Accounts')

    @api.model
    def default_get(self, fields):
        rec = super(payment_register, self).default_get(fields)
        amount_pay_total = 0
        context = self._context
        if context.get('active_ids'):
            for inv in context.get('active_ids'):
                record = self.env['account.move'].browse(inv)
                amount_pay_total += record.amount_total
            rec.update({
                'amount_pay_total': amount_pay_total,
                'amount': amount_pay_total,
            })
        return rec

    @api.onchange('writeoff_multi_acc_ids')
    def onchange_writeoff_multi_accounts(self):
        if self.writeoff_multi_acc_ids:
            diff_amount = sum([line.amount_payment for line in self.writeoff_multi_acc_ids])
            self.amount = self.amount_pay_total - diff_amount

    def _prepare_payment_vals(self, invoices):
        res = super(payment_register, self)._prepare_payment_vals(invoices)
        if self.writeoff_multi_acc_ids:
            multi_accounts = []
            diff_amount = 0.0
            amount = res.get('amount')
            for line in self.writeoff_multi_acc_ids:
                write_off_percent = round(line.amount_payment / self.amount_pay_total,
                                          2) if self.amount_pay_total else 0
                write_off_amount = round(amount * write_off_percent, 2)
                multi_accounts.append((0, 0, {'writeoff_account_id': line.writeoff_account_id.id,
                                              'name': line.name or '',
                                              'amt_percent': line.amt_percent or '',
                                              'amount': write_off_amount,
                                              'currency_id': line.currency_id and line.currency_id.id or ''}))
                diff_amount += write_off_amount

            amount = round(amount - diff_amount, 2)
            res.update({
                'payment_option': 'partial',
                'payment_difference_handling': 'reconcile',
                'post_diff_acc': 'multi',
                'amount': amount,
                'payment_difference': round(diff_amount, 2),
                'writeoff_multi_acc_ids': multi_accounts
            })
        return res


    def _create_payment_vals_from_wizard(self):
        res =super(payment_register, self)._create_payment_vals_from_wizard()
        write_off_vals_lines = []

        if not self.currency_id.is_zero(self.payment_difference) and (self.post_diff_acc == 'multi' or self.post_diff_acc == 'single'):
            write_off_vals = []
            for woff_payment in self.writeoff_multi_acc_ids:
                write_off_vals.append({
                    'name': woff_payment.name,
                    'amount': woff_payment.amount_payment or 0.0,
                    'account_id': woff_payment.writeoff_account_id.id,
                    'is_multi_write_off': True
                })
                # write_off_vals_lines.append((0, 0, {
                #     'name': woff_payment.name,
                #     'amount': woff_payment.amount_payment or 0.0,
                #     'writeoff_account_id': woff_payment.writeoff_account_id.id,
                #     'currency_id': woff_payment.currency_id.id
                # }))


            res['multi_write_off_line_vals'] = write_off_vals
            # res['writeoff_multi_acc_ids'] = write_off_vals


        if self.post_diff_acc == 'single' or self.post_diff_acc == 'multi':
            diff_amount=0.0
            account_move_record = self.env['account.move'].browse(self._context.get('active_ids', []))
            for rec in account_move_record:
                for line in self.writeoff_multi_acc_ids:
                    if line.distribute_by_weight == True:

                        write_off_vals_lines.append((0, 0, {'writeoff_account_id': line.writeoff_account_id.id,
                                                      'name': line.name or '',
                                                      'amt_percent': line.amt_percent or '',
                                                      'invoice_name': rec.name or '',
                                                      'invoice_total_amount': rec.amount_total or '',
                                                      'remain_total_amount': rec.amount_total-((rec.amount_total / float(
                                                          self.amount_pay_total)) * line.amount_payment) or '',
                                                      'amount': (rec.amount_total / float(
                                                          self.amount_pay_total)) * line.amount_payment or '',
                                                      'currency_id': line.currency_id and line.currency_id.id or ''}))

                        diff_amount += (rec.amount_total / float(self.amount_pay_total) * line.amount_payment)

            amount = self.amount
            if amount > diff_amount:
                amount = self.amount - diff_amount
                        # write_off_vals_lines.append((0, 0, {
                        #         'name': woff.name,
                        #         'amount': woff.amount_payment or 0.0,
                        #         'writeoff_account_id': woff.writeoff_account_id.id,
                        #         'currency_id': woff.currency_id.id
                        #     }))
            for line in self.writeoff_multi_acc_ids:
                if not line.distribute_by_weight:
                    write_off_vals_lines.append((0, 0, {
                            'name': line.name,
                            'amount': line.amount_payment or 0.0,
                            'writeoff_account_id': line.writeoff_account_id.id,
                            'currency_id': line.currency_id.id
                        }))

            # res['writeoff_multi_acc_ids'] = write_off_vals_lines
            res.update({'writeoff_multi_acc_ids':write_off_vals_lines,
                        # 'amount':amount,
                        'check_number':self.check_number,
                        'date_due':self.date_due,
                        'collection_receipt_number':self.collection_receipt_number,
                        'collection_rep':self.collection_rep.id,
                        'collection_rep_name':self.collection_rep_name,
                        })
        return res

    def _create_payments(self):
        self.ensure_one()
        batches = self._get_batches()
        self._create_payment_vals_from_wizard()
        to_reconcile = []
        if self.can_edit_wizard and (len(batches[0]['lines']) == 1 or self.group_payment):
            payment_vals = self._create_payment_vals_from_wizard()
            payment_vals_list = [payment_vals]
            to_reconcile.append(batches[0]['lines'])
        else:
            # self._create_payment_vals_from_wizard()

            # Don't group payments: Create one batch per move.
            if not self.group_payment:
                new_batches = []
                for batch_result in batches:
                    for line in batch_result['lines']:
                        new_batches.append({
                            **batch_result,
                            'lines': line,
                        })
                batches = new_batches

            payment_vals_list = []
            for batch_result in batches:
                payment_vals_list.append(self._create_payment_vals_from_batch(batch_result))
                to_reconcile.append(batch_result['lines'])
        print("------------------------------------------------")

        payments = self.env['account.payment'].create(payment_vals_list)
        for pay in payments:
            pay.check_number = self.check_number
            pay.date_due = self.date_due
            pay.collection_receipt_number = self.collection_receipt_number
            pay.collection_rep = self.collection_rep
            pay.collection_rep_name = self.collection_rep_name
            if pay.move_id:
                pay.move_id.check_number_payment = self.check_number
                pay.move_id.date_payment = self.date_due
                pay.move_id.collection_receipt_number = self.collection_receipt_number


                for lin in pay.move_id.line_ids:
                    lin.check_number_payment = self.check_number
                    lin.date_payment = self.date_due
                    lin.collection_receipt_number = self.collection_receipt_number





        # payments.action_post()
        payments.state='posted'

        domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
        for payment, lines in zip(payments, to_reconcile):
            payment_lines = payment.line_ids.filtered_domain(domain)
            for account in payment_lines.account_id:
                (payment_lines + lines)\
                    .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
                    .reconcile()
        payments.state = 'draft'

        return payments




class account_payment(models.Model):
    _inherit = "account.payment"

    payment_option = fields.Selection(
        [('full', 'Full Payment without Deduction'), ('partial', 'Full Payment with Deduction')], default='full',
        required=True, string='Payment Option')
    post_diff_acc = fields.Selection([('single', 'Single Account'), ('multi', 'Multiple Accounts')], default='single',
                                     string='Post Difference In To')
    writeoff_multi_acc_ids = fields.One2many('writeoff.accounts', 'payment_id', string='Write Off Accounts')

    invoice_payment_ids = fields.One2many(comodel_name="invoice.payment.distribute",
                                          inverse_name="payment_id",)
    is_check_pay = fields.Boolean(string="",compute='compute_invoice_payment_ids'  )
    @api.depends('writeoff_multi_acc_ids')
    def compute_invoice_payment_ids(self):
        for rec in self:
            #raise UserWarning("ZZZZZZZZZZ")
            domain=[]
            if rec.partner_type=="customer":
                domain.append(('move_type','like','out%'))
            else:
                domain.append(('move_type','like','in%'))
            if rec.partner_id:   
                domain.append(('id','=',rec.partner_id.id))
            #domain.append(('move_type','=','entry'))        
            rec.is_check_pay=False
            rec.invoice_payment_ids=False
            total_invoice=0.0
            # total_payment=0.0
            lines_list=[(5,0,0)]
            name=''
            for invoice in self.env['account.move'].search(domain):
                rec.is_check_pay = False
                total_payment=0.0
                for line in rec.writeoff_multi_acc_ids:
                    if invoice.name==line.invoice_name:
                        rec.is_check_pay=True
                        total_payment+=line.amount
                        name=line.invoice_name
                        total_invoice = invoice.amount_total
                if rec.is_check_pay==True:
                    lines_list.append((0,0,{
                        'name':name,
                        'amount_total':invoice.amount_total,
                        'total_amount':total_invoice-total_payment,
                        'payment_amount':total_payment,
                    }))
            print(lines_list,'0000000000000000000000000000000000000000000000000000000000000000000')
            rec.invoice_payment_ids=lines_list
            # rec.update({'invoice_payment_ids':lines_list})



    def _synchronize_from_moves(self, changed_fields):
        ''' Update the account.payment regarding its related account.move.
        Also, check both models are still consistent.
        :param changed_fields: A set containing all modified fields on account.move.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):

            # After the migration to 14.0, the journal entry could be shared between the account.payment and the
            # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
            if pay.move_id.statement_line_id:
                continue

            move = pay.move_id
            move_vals_to_write = {}
            payment_vals_to_write = {}

            if 'journal_id' in changed_fields:
                if pay.journal_id.type not in ('bank', 'cash'):
                    raise UserError(_("A payment must always belongs to a bank or cash journal."))

            if 'line_ids' in changed_fields:
                all_lines = move.line_ids
                liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                if len(liquidity_lines) != 1 or len(counterpart_lines) != 1:
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal entry must always contains:\n"
                        "- one journal item involving the outstanding payment/receipts account.\n"
                        "- one journal item involving a receivable/payable account.\n"
                        "- optional journal items, all sharing the same account.\n\n"
                    ) % move.display_name)

                # if writeoff_lines and len(writeoff_lines.account_id) != 1:
                #     raise UserError(_(
                #         "The journal entry %s reached an invalid state relative to its payment.\n"
                #         "To be consistent, all the write-off journal items must share the same account."
                #     ) % move.display_name)

                if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal items must share the same currency."
                    ) % move.display_name)

                if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal items must share the same partner."
                    ) % move.display_name)

                if counterpart_lines.account_id.user_type_id.type == 'receivable':
                    partner_type = 'customer'
                else:
                    partner_type = 'supplier'

                liquidity_amount = liquidity_lines.amount_currency

                move_vals_to_write.update({
                    'currency_id': liquidity_lines.currency_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                payment_vals_to_write.update({
                    'amount': abs(liquidity_amount),
                    'payment_type': 'inbound' if liquidity_amount > 0.0 else 'outbound',
                    'partner_type': partner_type,
                    'currency_id': liquidity_lines.currency_id.id,
                    'destination_account_id': counterpart_lines.account_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })

            move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
            pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))

    @api.onchange('payment_option')
    def onchange_payment_option(self):
        if self.payment_option == 'full':
            self.payment_difference_handling = 'open'
            self.post_diff_acc = 'single'
        else:
            self.payment_difference_handling = 'reconcile'
            self.post_diff_acc = 'multi'

    @api.onchange('writeoff_multi_acc_ids')
    def onchange_writeoff_multi_accounts(self):
        if self.writeoff_multi_acc_ids:
            diff_amount = sum([line.amount for line in self.writeoff_multi_acc_ids])
            if self.reversal_move_id:
                self.amount = self.invoice_ids and self.invoice_ids[0].amount_residual - diff_amount
            else:
                pass

    @api.model_create_multi
    def create(self, vals_list):
        write_off_line_vals_list = []
        for vals in vals_list:
            # Hack to add a custom write-off line.
            # write_off_line_vals_list.append()
            context = self._context.copy()
            if context.get('woff_params'):
                context['woff_params'].update(vals.pop('multi_write_off_line_vals', None))
            else:
                context['woff_params'] = vals.pop('multi_write_off_line_vals', None)
            self.env.context = context
        return super(account_payment, self).create(vals_list)

    def post(self):
        for move in self:

            if move.payment_difference_handling == 'reconcile' and move.post_diff_acc == 'multi':
                amount = 0
                for payment in move.writeoff_multi_acc_ids:
                    amount += payment.amount
                if move.amount > amount:
                    if move.payment_type == 'inbound' and round(move.payment_difference, 2) != round(amount, 2):
                        raise UserError(_("The sum of write off amounts and payment difference amounts are not equal."))
                    elif move.payment_type == 'outbound' and round(move.payment_difference, 2) != -round(amount, 2):
                        raise UserError(_("The sum of write off amounts and payment difference amounts are not equal."))
        return super(account_payment, self).post()

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        self.ensure_one()
        print("TTTTTTTTTTTTTTT***********************************************")
        write_off_line_vals = write_off_line_vals or {}

        if not self.journal_id.payment_debit_account_id or not self.journal_id.payment_credit_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set on the %s journal.",
                self.journal_id.display_name))
        # Compute amounts.
        write_off_amount = write_off_line_vals.get('amount', 0.0)
        woff_params = self._context.get('woff_params')
        if woff_params:
            multi_write_off_amount = 0
            for rec in woff_params:
                multi_write_off_amount += rec.get('amount')
            write_off_amount = multi_write_off_amount

        if self.payment_type == 'inbound':
            # Receive money.
            counterpart_amount = -self.amount
            write_off_amount *= -1
        elif self.payment_type == 'outbound':
            # Send money.
            counterpart_amount = self.amount
        else:
            counterpart_amount = 0.0
            write_off_amount = 0.0

        balance = self.currency_id._convert(counterpart_amount, self.company_id.currency_id, self.company_id, self.date)
        counterpart_amount_currency = counterpart_amount
        write_off_balance = self.currency_id._convert(write_off_amount, self.company_id.currency_id, self.company_id, self.date)
        write_off_amount_currency = write_off_amount
        currency_id = self.currency_id.id
        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.journal_id.name)
            else: # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        else:
            liquidity_line_name = self.payment_reference

        # Compute a default label to set on the journal items.

        payment_display_name = {
            'outbound-customer': _("Customer Reimbursement"),
            'inbound-customer': _("Customer Payment"),
            'outbound-supplier': _("Vendor Payment"),
            'inbound-supplier': _("Vendor Reimbursement"),
        }

        default_line_name = self.env['account.move.line']._get_default_line_name(
            payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
            self.amount,
            self.currency_id,
            self.date,
            partner=self.partner_id,
        )
        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name or default_line_name,
                'date_maturity': self.date,
                'amount_currency': -counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': balance < 0.0 and -balance or 0.0,
                'credit': balance > 0.0 and balance or 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.journal_id.payment_debit_account_id.id if balance < 0.0 else self.journal_id.payment_credit_account_id.id,
            },
            # Receivable / Payable.
            {
                'name': self.payment_reference or default_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency + write_off_amount_currency if currency_id else 0.0,
                'currency_id': currency_id,
                'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.destination_account_id.id,
            },
        ]
        if write_off_balance:
            print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",woff_params)
            # Write-off line.
            if woff_params:
                for rec in self.writeoff_multi_acc_ids:
                    write_off_balance = self.currency_id._convert(rec.amount, self.company_id.currency_id,
                                                                  self.company_id, self.date)
                    write_off_amount_currency = rec.amount
                    if self.payment_type == 'inbound':
                        # Receive money.
                        write_off_balance *= -1
                    line_vals_list.append({
                        'name': rec.name or default_line_name,
                        'amount_currency': -write_off_amount_currency,
                        'currency_id': currency_id,
                        'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                        'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                        'partner_id': self.partner_id.id,
                        'account_id': rec.writeoff_account_id.id,
                    })
        else:
            total_write_amount=0
            if self.writeoff_multi_acc_ids:
                for rec in self.writeoff_multi_acc_ids:
                    total_write_amount+=rec.amount
                    write_off_balance = self.currency_id._convert(rec.amount, self.company_id.currency_id,
                                                                  self.company_id, self.date)
                    write_off_amount_currency = rec.amount
                    # if self.payment_type == 'inbound':
                    #     # Receive money.
                    #     write_off_balance *= -1
                    line_vals_list.append({
                        'name': rec.name or default_line_name,
                        'amount_currency': -write_off_amount_currency,
                        'currency_id': currency_id,
                        'credit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                        'debit': write_off_balance > 0.0 and write_off_balance or 0.0,
                        'partner_id': self.partner_id.id,
                        'account_id': rec.writeoff_account_id.id,
                    })
                for val in line_vals_list:
                    if val['credit']>0:

                        val['credit']+=total_write_amount

        return line_vals_list

    def action_post(self):
        res = super(account_payment, self).action_post()
        for rec in self:

            rec.move_id.date=date.today()
            # print(date.today(),'DDDDDDDDDDDDDDDDDDDDDDDDDD')

            if rec.move_id.check_number_payment==False or rec.date_payment==False or rec.collection_receipt_number==False:
                rec.move_id.check_number_payment=rec.check_number
                rec.move_id.date_payment=rec.date_due
                rec.move_id.collection_receipt_number=rec.collection_receipt_number


            rec.move_id.date_reconcile = rec.date
            rec.move_id.payment_name = rec.name
            for line in rec.move_id.line_ids:
                # line.date_pay = rec.date
                # line.payment_name = rec.name

                line.check_number_payment = rec.check_number
                line.date_payment = rec.date_due
                line.collection_receipt_number = rec.collection_receipt_number

            # for inv in rec.move_id.invoice_line_ids:
            #     inv.date_pay = rec.date
            #     inv.payment_name = rec.name



        return res


class writeoff_accounts(models.Model):
    _name = 'writeoff.accounts'

    writeoff_account_id = fields.Many2one('account.account', string="Difference Account",
                                          domain=[('deprecated', '=', False)], copy=False, required="1")
    name = fields.Char('Description')
    amt_percent = fields.Float(string='Amount(%)', digits=(16, 2))
    invoice_name = fields.Char(string="Invoice", )
    invoice_total_amount = fields.Float(string="Total Amount",  required=False, )
    remain_total_amount = fields.Float(string="Total",  required=False, )
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    payment_id = fields.Many2one('account.payment', string='Payment Record')

    @api.onchange('amt_percent')
    def _onchange_amt_percent(self):

        if self.amt_percent and self.amt_percent > 0:
            if self.payment_id.invoice_ids:
                self.amount = self.payment_id.invoice_ids[0].amount_total * self.amt_percent / 100


class RegisterWriteoffMulti(models.TransientModel):
    _name = 'writeoff.multi'

    writeoff_account_id = fields.Many2one('account.account', string="Difference Account",
                                          domain=[('deprecated', '=', False)], copy=False, required="1")
    name = fields.Char('Description')
    amt_percent = fields.Float(string='Amount(%)', digits=(16, 2))
    amount_payment = fields.Monetary(string='Payment Amount', required=True, )
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    register_id = fields.Many2one('account.payment.register', string='Register Record')
    distribute_by_weight = fields.Boolean(string="Distribute",  )

    @api.onchange('amt_percent')
    def _onchange_amt_percent(self):
        if self.amt_percent and self.amt_percent > 0:
            if self.register_id.amount_pay_total:
                self.amount_payment = self.register_id.amount_pay_total * self.amt_percent / 100

class InvoicePaymentDistribute(models.Model):
    _name = 'invoice.payment.distribute'
    _rec_name = 'name'

    name = fields.Char()
    amount_total = fields.Float(string="Invoice Total",  required=False, )
    payment_amount = fields.Float(string="Payment Amount",  required=False, )
    total_amount = fields.Float(string="Total",  required=False, )
    payment_id = fields.Many2one(comodel_name="account.payment", string="", required=False, )
