# -*- coding: utf-8 -*-
################################################################################
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
################################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError
import time
from odoo.tools import float_compare

class account_account(models.Model):
    _inherit = 'account.account'
    
    discount_account = fields.Boolean('Discount Account')
    
class account_move(models.Model):
    _inherit = 'account.move'   

    @api.onchange('purchase_vendor_bill_id', 'purchase_id')
    def _onchange_purchase_auto_complete(self):
 
        if self.purchase_vendor_bill_id.vendor_bill_id:
            self.invoice_vendor_bill_id = self.purchase_vendor_bill_id.vendor_bill_id
            self._onchange_invoice_vendor_bill()
        elif self.purchase_vendor_bill_id.purchase_order_id:
            self.purchase_id = self.purchase_vendor_bill_id.purchase_order_id
        self.purchase_vendor_bill_id = False
 
        if not self.purchase_id:
            return
 
        #Auto fill discount fields    
        if self.purchase_id.apply_discount:
            self.apply_discount = self.purchase_id.apply_discount
            self.discount_type_id = self.purchase_id.discount_type_id
            self.discount_value = self.purchase_id.discount_value
            self.discount_account = self.purchase_id.discount_account
            self.amount_after_discount = self.purchase_id.amount_after_discount    
 
        # Copy partner.
        self.partner_id = self.purchase_id.partner_id
        self.fiscal_position_id = self.purchase_id.fiscal_position_id
        self.invoice_payment_term_id = self.purchase_id.payment_term_id
        self.currency_id = self.purchase_id.currency_id
 
        # Copy purchase lines.
        po_lines = self.purchase_id.order_line - self.line_ids.mapped('purchase_line_id')
        new_lines = self.env['account.move.line']
        for line in po_lines.filtered(lambda l: not l.display_type):
            new_line = new_lines.new(line._prepare_account_move_line(self))
            new_line.account_id = new_line._get_computed_account()
            new_lines += new_line   
        new_lines._onchange_mark_recompute_taxes()
 
        # Compute invoice_origin.
        origins = set(self.line_ids.mapped('purchase_line_id.order_id.name'))
        self.invoice_origin = ','.join(list(origins))
 
        # Compute ref.
        refs = set(self.line_ids.mapped('purchase_line_id.order_id.partner_ref'))
        refs = [ref for ref in refs if ref]
        self.ref = ','.join(refs)
 
        # Compute _invoice_payment_ref.
        if len(refs) == 1:
            self._invoice_payment_ref = refs[0]
 
        self._onchange_currency()
        self.invoice_partner_bank_id = self.bank_partner_id.bank_ids and self.bank_partner_id.bank_ids[0]
 
        if self.apply_discount == True:
            res_x = self._compute_amount_after_discount()
            discount_price = res_x
            count = 0 
            for rec in self.line_ids:
                if rec.discount_line == True:
                    count+=1
            if count== 0: 
                discount_vals = {
                            'account_id' : self.purchase_id.discount_account.id,
                            'price_unit' : -discount_price,
                            'quantity': 1,
                            'name': self.discount_type_id.name,
                            'exclude_from_invoice_tab': True,
                            'discount_line':True,
                            }
                self.with_context(check_move_validity=False).update({
                            'line_ids' : [(0,0,discount_vals)],
                        })                         

    def _compute_amount_after_discount(self):
        res = discount = 0.0
        discount_type_percent = self.env['ir.model.data'].xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_percent_id')
        discount_type_fixed = self.env['ir.model.data'].xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_fixed_id')

        for self_obj in self:
            if not self_obj.apply_discount:
                self_obj.discount_value = 0.0
            if self_obj.discount_type_id.id == discount_type_fixed:
                res = self_obj.discount_value
            elif self_obj.discount_type_id.id == discount_type_percent:    
                res = self_obj.amount_untaxed * (self_obj.discount_value/ 100)
            else:
                res = discount    
            return res    

    @api.onchange('apply_discount')
    def onchange_apply_discount(self):
        if self.apply_discount:
            if self.move_type == 'out_invoice':
                account_search = self.env['account.account'].search([('user_type_id.internal_group','=','expense'),('discount_account', '=', True)])
                if account_search:
                    self.update( {'out_discount_account':account_search[0].id})
            if self.move_type == 'in_invoice':
                account_search = self.env['account.account'].search([('user_type_id.internal_group','=','income'),('discount_account', '=', True)])
                if account_search:
                    self.update( {'in_discount_account':account_search[0].id})
                
    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'discount_value',
        'amount_after_discount',
        'discount_type_id',)
    def _compute_amount(self):
        for move in self:

            if move.payment_state == 'invoicing_legacy':
                # invoicing_legacy state is set via SQL when setting setting field
                # invoicing_switch_threshold (defined in account_accountant).
                # The only way of going out of this state is through this setting,
                # so we don't recompute it here.
                move.payment_state = move.payment_state
                continue

            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_to_pay = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        value = 0 
                        total_value = 0
                        if self._context.get('default_move_type') in ('in_invoice','in_receipt'):
                            for val in move.line_ids:
                                if not val.exclude_from_invoice_tab:
                                    total_value += val.debit
                                if val.tax_tag_ids:
                                    value+= val.debit
                                    
                            for rec in move.line_ids:        
                                if rec.discount_line == True:
                                    res = self._compute_amount_after_discount()
                                    discount_amt = res
                                    rec.credit = discount_amt
                                    rec.name = move.discount_type_id.name
                                    line.credit = total_value + value - rec.credit + move.amount_tax
                                    line.debit = 0.0
                                    
                        elif self._context.get('default_move_type') == 'in_refund':
                            for val in move.line_ids:
                                if not val.exclude_from_invoice_tab:
                                   rec.total_value += val.credit
                                if val.tax_tag_ids:
                                    value+= val.credit
                             
                            for rec in move.line_ids:        
                                if rec.discount_line == True:
                                    res = self._compute_amount_after_discount()
                                    discount_amt = res      
                                    rec.debit = discount_amt
                                    rec.name = move.discount_type_id.name
                                    line.debit = total_value + value - rec.debit
 
                        elif self._context.get('default_move_type') in ('out_invoice','out_receipt'):
                            for val in move.line_ids:
                                if not val.exclude_from_invoice_tab:
                                    total_value += val.credit
                                if val.tax_tag_ids:
                                    value+= val.credit
                             
                            for rec in move.line_ids:        
                                if rec.discount_line == True:
                                    res = self._compute_amount_after_discount()
                                    discount_amt = res      
                                    rec.debit = discount_amt
                                    rec.name = move.discount_type_id.name
                                    line.debit = total_value + value - rec.debit
                                    line.credit = 0.0
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            res = self._compute_amount_after_discount()
            discount_amt = res
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)            
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total) - res
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = -total - res
            move.amount_residual_signed = total_residual - res
            move.amount_after_discount = move.amount_untaxed - discount_amt
            currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id
            is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual

            # Compute 'payment_state'.
            new_pmt_state = 'not_paid' if move.move_type != 'entry' else False

            if move.is_invoice(include_receipts=True) and move.state == 'posted':

                if currency.is_zero(move.amount_residual):
                    if all(payment.is_matched for payment in move._get_reconciled_payments()):
                        new_pmt_state = 'paid'
                    else:
                        new_pmt_state = move._get_invoice_in_payment_state()
                elif currency.compare_amounts(total_to_pay, total_residual) != 0:
                    new_pmt_state = 'partial'

            if new_pmt_state == 'paid' and move.move_type in ('in_invoice', 'out_invoice', 'entry'):
                reverse_type = move.move_type == 'in_invoice' and 'in_refund' or move.move_type == 'out_invoice' and 'out_refund' or 'entry'
                reverse_moves = self.env['account.move'].search([('reversed_entry_id', '=', move.id), ('state', '=', 'posted'), ('move_type', '=', reverse_type)])

                # We only set 'reversed' state in cas of 1 to 1 full reconciliation with a reverse entry; otherwise, we use the regular 'paid' state
                reverse_moves_full_recs = reverse_moves.mapped('line_ids.full_reconcile_id')
                if reverse_moves_full_recs.mapped('reconciled_line_ids.move_id').filtered(lambda x: x not in (reverse_moves + reverse_moves_full_recs.mapped('exchange_move_id'))) == move:
                    new_pmt_state = 'reversed'

            move.payment_state = new_pmt_state
        
 
    discount_type_id = fields.Many2one('discount.type', 'Discount Type',)
    discount_value = fields.Float('Discount Value',)
    out_discount_account = fields.Many2one('account.account', 'Discount Account')
    in_discount_account = fields.Many2one('account.account', 'Discount Account')
    amount_after_discount = fields.Monetary('Amount After Discount', store=True, readonly=True, tracking=True,
        compute='_compute_amount')
    apply_discount = fields.Boolean('Apply Discount')
    discount_move_line_id = fields.Many2one('account.move.line','Discount Line')
    purchase_order = fields.Boolean('is a PO',default=False)                        
        
    @api.onchange('amount_untaxed','invoice_line_ids','discount_value','discount_account','line_ids')
    def _onchange_invoice_line_ids(self):
        current_invoice_lines = self.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab)
        others_lines = self.line_ids - current_invoice_lines
        discount_lines = self.env['account.move.line']
                    
 
        if self.apply_discount:
            count= 0
            for line in self.line_ids:
                if line.discount_line == True:
                    count+=1
                else:
                    pass 
            for line in self.line_ids:
                if count==1:
                    pass   
                else:
                    move_line_obj = line.search([('account_id','=',self.out_discount_account.id)],limit=1)
                    if not move_line_obj:
                        res_x = self._compute_amount_after_discount()
                        discount_price = res_x
                        if self._context.get('default_move_type') in ['out_invoice']:
                            discount_vals = {
                                    'account_id' : self.out_discount_account.id,
                                    'price_unit' : -discount_price,
                                    'quantity': 1,
                                    'name': self.discount_type_id.name,
                                    'exclude_from_invoice_tab': True,
                                    'discount_line': True,
                                    }
                        
                        if self._context.get('default_move_type') in ['in_invoice']:
                            discount_vals = {
                                    'account_id' : self.in_discount_account.id,
                                    'price_unit' : -discount_price,
                                    'quantity': 1,
                                    'name': self.discount_type_id.name,
                                    'exclude_from_invoice_tab': True,
                                    'discount_line': True,
                                    }
                            discount_lines = self.line_ids.with_context(check_move_validity=False).new(discount_vals)            
                    else:
                        res_x = self._compute_amount_after_discount()
                        discount_price = res_x
                        if move_line_obj:
                            price = -discount_price + move_line_obj.debit
                        else:
                            price = -discount_price
                        if self._context.get('default_move_type') in ['out_invoice']:
                            discount_vals = {
                                    'account_id' : self.out_discount_account.id,
                                    'price_unit' : price,
                                    'quantity': 1,
                                    'name': self.discount_type_id.name,
                                    'exclude_from_invoice_tab': True,
                                    'discount_line': True,
                                    }
                        move_line_obj.with_context(check_move_validity=False).write(discount_vals) 

        if others_lines and current_invoice_lines - self.invoice_line_ids:
            others_lines[0].recompute_tax_line = True
        if self.invoice_line_ids:
            self.line_ids = others_lines + self.invoice_line_ids + discount_lines
        self._onchange_recompute_dynamic_lines()


    @api.model
    def create(self, vals_list):
        res = super(account_move,self).create(vals_list)
        for val in vals_list:
            if vals_list.get('invoice_origin'):
                purchase = self.env['purchase.order'].search([('name', '=', vals_list["invoice_origin"])],limit=1)
                if purchase:
                    res.write({'apply_discount':purchase.apply_discount,'in_discount_account':purchase.discount_account.id,
                    'discount_type_id':purchase.discount_type_id.id,
                    'discount_value':purchase.discount_value,
                    'amount_after_discount':purchase.amount_after_discount})
                sale = self.env['sale.order'].search([('name', '=', vals_list["invoice_origin"])],limit=1)
                if sale:
                    res.write({'apply_discount':sale.apply_discount,'out_discount_account':sale.discount_account.id,
                    'discount_type_id':sale.discount_type_id.id,
                    'discount_value':sale.discount_value,
                    'amount_after_discount':sale.amount_after_discount,})
            if res.apply_discount and (not res.discount_type_id or not res.discount_value):
                raise ValidationError(_('Please give the Discount Type and its values'))
            if res.apply_discount == True:
                sign = 1 if res.is_inbound() else -1
                name = []
                move_ids = []
                for line in res.line_ids:
                    move_ids.append(line.id)
                    name.append(line.name)
                if vals_list.get('invoice_origin'):
                    purchase = self.env['purchase.order'].search([('name', '=', vals_list["invoice_origin"])],limit=1)
                    if purchase:
                        move_line_obj = self.env['account.move.line'].search([('id', 'in', move_ids),('account_id','=',14)],limit=1)
                        if move_line_obj.purchase_line == False:
                            move_line_obj.with_context(check_move_validity=False).write({'credit':purchase.amount_total,'purchase_line':True})
                    sale = self.env['sale.order'].search([('name', '=', vals_list["invoice_origin"])],limit=1)
                    if sale:
                        move_line_obj = self.env['account.move.line'].search([('id', 'in', move_ids),('account_id','=',6)],limit=1)
                        if move_line_obj.sale_line == False:
                            move_line_obj.with_context(check_move_validity=False).write({'debit':sale.amount_total,'sale_line':True})

                if self._context.get('default_move_type') in ('out_invoice','out_receipt','in_refund'):
                    if res.discount_type_id.name not in name:
                        res_x = res._compute_amount_after_discount()
                        discount_price = res_x
                        discount_vals = {
                            'account_id' : res.out_discount_account.id,
                            'price_unit' : -discount_price,
                            'quantity': 1,
                            'name': res.discount_type_id.name,
                            'exclude_from_invoice_tab': True,
                            'discount_line': False,
                            }
                        res.with_context(check_move_validity=False).write({
                            'line_ids' : [(0,0,discount_vals)]
                            })
                    if name == False or name == '':
                        line.debit = res.amount_total

                elif self._context.get('default_move_type') in ('in_invoice','in_receipt','out_refund'):
                    if self._context.get('default_purchase_id'):
                        for rec in self.line_ids:
                            if rec.discount_line == True:
                                value = self.amount_untaxed - self.amount_after_discount
                                account = self.in_discount_account.id
                                rec.with_context(check_move_validity=False).write({'price_unit':-value, 'name': self.discount_type_id.name,'account_id': account,})        
                            else:
                                pass
                    else:
                        if res.discount_type_id.name not in name:
                            res_x = res._compute_amount_after_discount()
                            discount_price = res_x         
                            discount_vals = {
                                'account_id' : res.in_discount_account.id,
                                'price_unit' : -discount_price,
                                'quantity': 1,
                                'name': res.discount_type_id.name,
                                'exclude_from_invoice_tab': True,
                                'discount_line':True,
                                }
                            res.with_context(check_move_validity=False).write({
                                'line_ids' : [(0,0,discount_vals)]
                            }) 
                else:
                    pass                     
            else:
                pass    
        return res


    @api.onchange('discount_type_id')
    def onchange_type(self):
        if self._context.get('default_move_type') in ('in_invoice','in_receipt','out_refund'):
            for line in self.line_ids:
                name = line.name
                if name == False or name == '':
                    line.debit = 0.0      
        if self._context.get('default_move_type') in ('out_invoice','out_receipt','in_refund'):
            for line in self.line_ids:
                name = line.name
                if name == False or name == '':
                    line.credit = 0.0      

    
    def write(self,vals):
        res = super(account_move, self).write(vals)
        for move in self:
            if move.apply_discount and (not move.discount_type_id or not move.discount_value):
                raise ValidationError(_('Please give the Discount Type and its values'))
        return res


class account_move_line(models.Model):
    _inherit = 'account.move.line' 

    discount_line = fields.Boolean('is a discount line')
    purchase_line = fields.Boolean('is a purchase line',default=False)
    sale_line = fields.Boolean('is a sale line',default=False)                


