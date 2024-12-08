# -*- coding: utf-8 -*-
################################################################################
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
################################################################################

from odoo.osv import osv
import odoo.addons.decimal_precision as dp
from odoo.tools.translate import _
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

class purchase_order_line(models.Model):
    _inherit  = 'purchase.order.line'

    discount_in_per =  fields.Float('Discount (%)')
   
    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount_in_per')
    def _compute_amount(self):
        for line in self:
            price_discount = line.price_unit * (1 - (line.discount_in_per or 0.0) / 100.0)
            taxes = line.taxes_id.compute_all(price_discount, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': '%s: %s' % (self.order_id.name, self.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'analytic_account_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'purchase_line_id': self.id,
            'discount':self.discount_in_per,
        }
        if not move:
            return res

        if self.currency_id == move.company_id.currency_id:
            currency = False
        else:
            currency = move.currency_id

        res.update({
            'move_id': move.id,
            'currency_id': currency and currency.id or False,
            'date_maturity': move.invoice_date_due,
            'partner_id': move.partner_id.id,
            
        })
        return res
       

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        res = super(purchase_order, self).create(vals)
        discount_type_obj = self.env['discount.type']
        discount_type_percent = self.env['ir.model.data'].xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_percent_id')
        discount_type_fixed = self.env['ir.model.data'].xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_fixed_id')
        if vals.get('discount_value'):
            if vals.get('discount_type_id') == discount_type_percent:
                brw_type = discount_type_obj.browse(discount_type_percent).discount_value
                if brw_type > 0.0:
                    if vals.get('discount_value',0.00) > brw_type:
                        raise UserError(
                    _('You can not set Discount Value more then %s . \n Maximum Discount value is %s \n Set maximum value Purchase-> Configuration-> Discount Type') % \
                        (brw_type , brw_type))
            elif vals.get('discount_type_id') == discount_type_fixed:
                brw_type = discount_type_obj.browse(discount_type_fixed).discount_value
                if brw_type > 0.0:
                    if vals.get('discount_value',0.00) > brw_type:
                        raise UserError(
                    _('You can not set Discount Value more then %s. \n Maximum Discount value is %s \n Set maximum value Purchase-> Configuration-> Discount Type' ) % \
                        (brw_type ,brw_type ))
        return res
    
    
    def write(self, vals):
        res = super(purchase_order, self).write(vals)
        discount_type_percent = self.env['ir.model.data'].xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_percent_id')
        discount_type_fixed = self.env['ir.model.data'].xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_fixed_id')
        discount_type_obj = self.env['discount.type']
        if vals.get('discount_type_id') == discount_type_percent or self.discount_type_id.id == discount_type_percent:
            brw_type = discount_type_obj.browse(discount_type_percent).discount_value
            if brw_type > 0.0:
                if vals.get('discount_value',0.00) > brw_type:
                    raise UserError(
                _('You can not set Discount Value more then %s . \n Maximum Discount value is %s \n Set maximum value Purchase-> Configuration-> Discount Type') % \
                    (brw_type , brw_type))
        if vals.get('discount_type_id') == discount_type_fixed or self.discount_type_id.id == discount_type_fixed:
            brw_type = discount_type_obj.browse(discount_type_fixed).discount_value
            if brw_type > 0.0:
                if vals.get('discount_value',0.00) > brw_type:
                    raise UserError(
                _('You can not set Discount Value more then %s. \n Maximum Discount value is %s \n Set maximum value Purchase-> Configuration-> Discount Type' ) % \
                    (brw_type ,brw_type ))
        if vals.get('discount_value'):
            if self.discount_type_id.id == discount_type_percent:
                brw_type = discount_type_obj.browse(discount_type_percent).discount_value
                if brw_type > 0.0:
                    if vals.get('discount_value',0.00) > brw_type:
                        raise UserError(
                    _('You can not set Discount Value more then %s. \n Maximum Discount value is %s \n Set maximum value Purchase-> Configuration-> Discount Type') % \
                        (brw_type , brw_type))
            elif self.discount_type_id.id == discount_type_fixed:
                brw_type = discount_type_obj.browse(discount_type_fixed).discount_value
                if brw_type > 0.0:
                    if vals.get('discount_value',0.00) > brw_type:
                        raise UserError(
                    _('You can not set Discount Value more then %s. \n Maximum Discount value is %s \n Set maximum value Purchase-> Configuration-> Discount Type' ) % \
                        (brw_type ,brw_type ))
        return res

    @api.onchange('apply_discount')
    def onchange_apply_discount(self):
        if self.apply_discount:
            account_search = self.env['account.account'].search([('discount_account', '=', True),('user_type_id.internal_group','=','income')])
            if account_search:
                self.discount_account = account_search[0].id
    
    @api.depends('order_line.price_total', 'discount_value', 'discount_type_id', 'apply_discount')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            if not order.apply_discount:
                order.amount_after_discount = 0.0
            if order.amount_after_discount:
                order.update({
                    'amount_untaxed': order.currency_id.round(amount_untaxed),
                    'amount_tax': order.currency_id.round(amount_tax),
                    'amount_total': order.amount_after_discount + order.currency_id.round(amount_tax) ,
                })
            else:
                order.update({
                    'amount_untaxed': order.currency_id.round(amount_untaxed),
                    'amount_tax': order.currency_id.round(amount_tax),
                    'amount_total': amount_untaxed + amount_tax ,
                })
                
    @api.depends('discount_value', 'order_line.price_total','discount_type_id')
    def _compute_amount_after_discount(self):
        discount = 0.0
        amount_untaxed = 0.0
        discount_type_percent = self.env['ir.model.data'].xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_percent_id')
        
        discount_type_fixed = self.env['ir.model.data'].xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_fixed_id')
        for self_obj in self:
            for line in self_obj.order_line:
                amount_untaxed += line.price_subtotal
            if self_obj.discount_type_id.id == discount_type_fixed:
                discount = amount_untaxed - self_obj.discount_value
                self_obj.amount_after_discount = discount
            elif self_obj.discount_type_id.id == discount_type_percent:
                discount_percent = amount_untaxed * ((self_obj.discount_value or 0.0) / 100.0)
                discount = amount_untaxed - discount_percent
                self_obj.amount_after_discount = discount
            else:
                self_obj.amount_after_discount = discount
    
    apply_discount = fields.Boolean('Apply Discount')
    discount_type_id = fields.Many2one('discount.type', 'Discount Type')
    discount_value = fields.Float('Purchase Discount')
    discount_account = fields.Many2one('account.account', 'Discount Account')
    amount_after_discount = fields.Monetary('Amount After Discount' , store=True, readonly=True, compute='_compute_amount_after_discount')
