# -*- coding: utf-8 -*-

from odoo import models, fields, api


class surgi_payment_access(models.Model):
    _inherit = 'account.payment'

    @api.model
    def button_account_action(self):

        user = self.env.user
        domain = []

        if user.has_group('surgi_payment_access.group_account_payment_purchese'):
            domain.append(('user_id', '=', user.id))

        value = {
            'name': 'Self Payments',
            'view_type': 'form',
            'view_mode': 'tree,kanban,pivot,form',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'domain': domain,
            # 'context': context
        }
        return value

class surgi_account_move_access(models.Model):
    _inherit = 'account.move'

    @api.model
    def button_account_move_action(self):

        user = self.env.user
        domain = []

        if user.has_group('surgi_payment_access.group_account_move_self'):
            domain.append(('invoice_user_id', '=', user.id))

        value = {
            'name': 'Self Invoices',
            'view_type': 'form',
            'view_mode': 'tree,kanban,pivot,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': domain,
            # 'context': context
        }
        return value

