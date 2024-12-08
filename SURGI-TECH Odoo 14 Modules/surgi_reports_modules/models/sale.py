from odoo import models, fields, api

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    @api.model
    def button_sales_action(self):

        users_team = []
        user = self.env.user
        domain = []
        sales_teams_records=self.env['crm.team'].search([('product_line_id','=',self.env.user.id)])
        for rec in sales_teams_records:
            if rec.user_id:
                users_team.append(rec.user_id.id)
            for member in rec.member_ids:
                users_team.append(member.id)

        if user.has_group('surgi_reports_modules.access_group_product_manager'):
            domain.append('|')
            domain.append(('user_id', 'in', users_team))
            domain.append(('user_id', '=', user.id))
        else:
            domain.append(('user_id', '=', user.id))
        value = {
            'name': 'Sale Order',
            'view_type': 'form',
            'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': domain,
            # 'context': context
        }
        return value
