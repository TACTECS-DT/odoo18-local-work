from odoo import models, fields, api
class SaleOrderInherit(models.Model):
    _inherit = 'hr.expense'

    @api.model
    def button_expense_action(self):

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
            domain.append(('employee_id.user_id', 'in', users_team))
            domain.append(('employee_id.user_id', '=', user.id))
        else:
            domain.append(('employee_id.user_id', '=', user.id))
        value = {
            'name': 'HR Expense',
            'view_type': 'form',
            'view_mode': 'tree,kanban,form,graph,pivot,activity',
            'res_model': 'hr.expense',
            'type': 'ir.actions.act_window',
            'domain': domain,
            # 'context': context
        }
        return value
