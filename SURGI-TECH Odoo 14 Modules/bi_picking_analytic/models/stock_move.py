# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from odoo.tools.float_utils import float_is_zero, float_compare
from datetime import datetime
from collections import namedtuple, OrderedDict, defaultdict


class StockMove(models.Model):
    _inherit = "stock.move"

    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')
    tag_ids  = fields.Many2many('account.analytic.tag', string= 'Tag')


    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id):
        # This method returns a dictonary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        rslt={}
        print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",debit_account_id,credit_account_id)

        self.ensure_one()
        if self._context.get('forced_ref'):
            ref = self._context['forced_ref']
        else:
            ref = self.picking_id.name

        tag_ids = []
        for tag in self.tag_ids:
            tag_ids.append(tag.id)

        if self.picking_id.picking_type_id.receipt_exchange==True:
            cridite_value=self.product_id.categ_id.property_stock_account_output_categ_id.id
        else:
            cridite_value=credit_account_id

        debit_line_vals = {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account_id,
            'analytic_account_id':self.analytic_account_id.id,
            'analytic_tag_ids': [(6,0,tag_ids)],
        }

        debit_line_vals22 = {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account_id,
            # 'analytic_account_id': self.analytic_account_id.id,
            # 'analytic_tag_ids': [(6, 0, tag_ids)],
        }

        credit_line_vals = {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': cridite_value,
        ### Hashed by Mostafa Nassar ###
            # 'analytic_account_id':self.analytic_account_id.id,
            # 'analytic_tag_ids': [(6,0,tag_ids)],
        }
        credit_line_vals22 = {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': credit_account_id,
            'analytic_account_id':self.analytic_account_id.id,
            'analytic_tag_ids': [(6,0,tag_ids)],
        }

        if self.picking_id.picking_type_id.code=='outgoing':
            rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
        if self.picking_id.picking_type_id.code=='incoming':
            rslt = {'credit_line_vals': credit_line_vals22, 'debit_line_vals': debit_line_vals22}

        if credit_value != debit_value:
            # for supplier returns of product in average costing method, in anglo saxon mode
            diff_amount = debit_value - credit_value
            price_diff_account = self.product_id.property_account_creditor_price_difference

            if not price_diff_account:
                price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
            if not price_diff_account:
                raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

            rslt['price_diff_line_vals'] = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': description,
                'partner_id': partner_id,
                'credit': diff_amount > 0 and diff_amount or 0,
                'debit': diff_amount < 0 and -diff_amount or 0,
                'account_id': price_diff_account.id,
            }
        return rslt

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, description):

        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        self.ensure_one()

        if self._context.get('force_valuation_amount'):
            valuation_amount = self._context.get('force_valuation_amount')
        else:
            valuation_amount = cost

        # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before creating the accounting entries.
        debit_value = self.company_id.currency_id.round(valuation_amount)

        # check that all data is correct
        if self.company_id.currency_id.is_zero(debit_value) and not self.env['ir.config_parameter'].sudo().get_param('stock_account.allow_zero_cost'):
            raise UserError(_("The cost of %s is currently equal to 0. Change the cost or the configuration of your product to avoid an incorrect valuation.") % (self.product_id.display_name,))
        credit_value = debit_value


        valuation_partner_id = self._get_partner_id_for_valuation_lines()
        res = [(0, 0, line_vals) for line_vals in self._generate_valuation_lines_data(valuation_partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id).values()]
        return res
