from odoo import fields, models, api, exceptions






class stock_quant_inherit_wizard(models.Model):
    _inherit = 'stock.quant'
    operation_id=fields.Many2one(comodel_name="operation.operation",string="Operation",compute="_get_stock_operation")#Note Dot Use @Any Logic Abdelaziz
    emptyreturned=fields.Boolean("Empty Item Returned")
    def return_empty_box(self):
        for rec in self:
            rec.operation_id.have_emptybox=True
            rec.emptyreturned=True
            # raise raise ("Empty Boxes Returned")
           #raise exceptions.ValidationError("Empty Boxes Returned") 
        pass
    def _get_stock_operation(self):
        for rec in self:
            # quant_line = self.env['stock.quant'].search(
            #             [('location_id', '=', line.location_id.id), ('product_id', '=', line.product_id.id),
            #              ('lot_id', '=', line.move_line_ids.lot_id.id)])
            #product_lines=self.env['product.operation.line'].search([('')])
            op=self.env['operation.operation'].search([('location_id','=',rec.location_id.id)])
            if op and len(op.ids)==1:
                rec.operation_id=op.id
            else:
                rec.operation_id=None



    @api.depends('location_id.warehouse_id.warehouse_users')
    def _get_wh_user(self):
        for obj in self:
            for user in obj.location_id.warehouse_id.warehouse_users:
                if(self.env.user.id == user.id):
                    obj.is_wh_user=True
                    break
                print ("WH result: ",obj.is_wh_user)

    def _get_is_hanged(self):
        for obj in self:
            dist_warehouse = self.env['stock.warehouse'].search([('is_hanged_warehouse', '=', True)])
            location = self.env['stock.location'].search(
                [('warehouse_id', '=', dist_warehouse.id), ('is_operation_location', '=', True),
                 ('usage', '=', 'internal')])
            obj.is_hanged = (obj.location_id.id == location.id)


    is_wh_user = fields.Boolean(default=False, compute=_get_wh_user,store=True)
    is_hanged = fields.Boolean(default=False, compute=_get_is_hanged)
    operation_location_id = fields.Many2one('stock.location', string="Operation Location", readonly=True)

class stock_hanged_quant_inherit(models.Model):
    _name = 'hanged.stock.quant'
    _inherit = 'stock.quant'

    invoice_id = fields.Many2one(comodel_name='account.move', string='Invoice', readonly=True)
    operation_id=fields.Many2one('operation.operation',string="Operation", readonly=True)

    def open_wizard_hanged_move_to_hanged_warehouse(self):
        action = self.env.ref('stock_quant.action_wizard_hanged_back_to_warehouse_quant')
        result = action.read()[0]
        res = self.env.ref('stock_quant.wizard_hanged_back_to_warehouse', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        return result

    def open_wizard_hanged_delivery(self):
        action = self.env.ref('stock_quant.action_wizard_hanged_delivery_quant')
        result = action.read()[0]
        res = self.env.ref('stock_quant.wizard_hanged_delivery', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        return result

    def open_wizard_hanged_invoice(self):
        action = self.env.ref('stock_quant.action_wizard_hanged_invoice_quant')
        result = action.read()[0]
        res = self.env.ref('stock_quant.wizard_hanged_invoice_stock_quant', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        return result



