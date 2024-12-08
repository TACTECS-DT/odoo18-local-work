from odoo import models, fields, api
class OperationOperationInherit(models.Model):
    _inherit = 'operation.operation'

    @api.model
    def button_operation_action(self):

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
            domain.append('|')
            domain.append('|')
            domain.append(('responsible', 'in', users_team))
            domain.append(('op_area_manager', '=', user.id))
            domain.append(('op_area_manager', 'in', users_team))
            domain.append(('responsible', '=', user.id))
        else:
            domain.append('|')
            domain.append(('responsible', '=', user.id))
            domain.append(('op_area_manager', '=', user.id))

        print(domain,'----------------------------------')
        value = {
            'name': 'Operation',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'operation.operation',
            'type': 'ir.actions.act_window',
            'domain': domain,
            # 'context': context
        }
        return value
