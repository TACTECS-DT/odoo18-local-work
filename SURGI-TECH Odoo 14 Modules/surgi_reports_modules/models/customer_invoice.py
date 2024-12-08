from odoo import models, fields, api
class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    @api.model
    def button_invoice_action(self):

        users_team = []
        user = self.env.user
        domain = []
        operators=[]
        sales_teams_records=self.env['crm.team'].search([('product_line_id','=',self.env.user.id)])
        counter=1
        for rec in sales_teams_records:
            if rec.user_id:
                users_team.append(rec.user_id.id)
            for member in rec.member_ids:
                users_team.append(member.id)

        if user.has_group('surgi_reports_modules.access_group_product_manager'):
            domain.append('&')
            domain.append(('user_id', 'in', users_team))
            domain.append(('move_type', '=', 'out_invoice'))

            counter+=1
        if user.has_group('surgi_reports_modules.access_group_product_manager'):
            domain.append('&')
            domain.append(('user_id', '=', user.id))
            domain.append(('move_type', '=', 'out_invoice'))
            counter += 1
        else:
            domain.append('&')
            domain.append(('user_id', '=', user.id))
            domain.append(('move_type', '=', 'out_invoice'))


        value = {
            'name': 'Customer Invoice',
            'view_type': 'form',
            'view_mode': 'tree,kanban,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': domain,
            # 'context': context
        }
        return value
