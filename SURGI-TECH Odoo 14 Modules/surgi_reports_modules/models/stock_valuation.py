from odoo import models, fields, api
class StockValuationLayerInherit(models.Model):
    _inherit = 'stock.valuation.layer'

    @api.model
    def button_stock_action(self):

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
            domain.append(('product_id.categ_id.product_line_id', 'in', users_team))
            domain.append(('product_id.categ_id.product_line_id', '=', user.id))
        else:
            domain.append(('product_id.categ_id.product_line_id', '=', user.id))
        value = {
            'name': 'Stock Valuation',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.valuation.layer',
            'type': 'ir.actions.act_window',
            'domain': domain,
            # 'context': {'search_default_done': 1, 'search_default_groupby_product_id': 1, 'create': 0}
        }
        return value
