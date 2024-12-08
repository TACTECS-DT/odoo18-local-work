
from odoo import api,fields,models,_

class PR_RefuseReason(models.TransientModel):
    _name = "op.add.item"

    consumed_items_file = fields.Binary(string='Consumed Items', store=True, track_visibility='always', attachment=True)

    def refuse_reason(self):
        if self.env.context.get('active_model') == 'operation.operation':
            active_model_id = self.env.context.get('active_id')
            pr_obj = self.env['operation.operation'].search([('id','=',active_model_id)])
            if pr_obj:
                pr_obj.write({'consumed_items_file':self.consumed_items_file})
	
