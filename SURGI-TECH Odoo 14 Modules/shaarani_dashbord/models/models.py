
from odoo import models, fields, api


class surgi_shaarani_pay_access(models.Model):
    _inherit = 'account.payment'

    @api.model
    def button_account_action(self):

        user = self.env.user
        domain = []

        if user.has_group('shaarani_dashbord.group_account_payment_shaarani'):
            domain.append(('user_id', '=', user.id))

        value = {
            'name': 'Payments',
            'view_type': 'form',
            'view_mode': 'tree,kanban,pivot,form',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'domain': domain,
            # 'context': context
        }
        return value
