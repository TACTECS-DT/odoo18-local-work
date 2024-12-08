# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Operation_operation_qulity(models.Model):
    _inherit = 'operation.operation'

    quality_check = fields.Boolean(string='Quality' , store=True,readonly=True,tracking=True,default=False)





    def quality_check_button(self):
        self.quality_check =True


    def quality_uncheck_button(self):
        self.quality_check =False




class stock_quant_quality(models.Model):
    _inherit = 'stock.quant'

    expiration_date_quality = fields.Date(related="lot_id.expiration_date", string="Expiration Date", index=True,store=True)


# class lot_id_quality(models.Model):
#     _inherit = 'stock.production.lot'

# class purchase_quality(models.Model):
#     _inherit = 'purchase.order'



class StockInherit(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def button_stock_action(self):
        # ctx = dict(
        #     create=False,
        # )
        value = {
            'name': 'Stock Transfer',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'context': {'edit':0, 'create': 0}
        }
        return value

class stock_operation_qulity(models.Model):
    _inherit = 'stock.picking'

    quality_check = fields.Boolean(string='Quality' , store=True,readonly=True,tracking=True,default=False)





    def quality_check_button(self):
        self.quality_check =True


    def quality_uncheck_button(self):
        self.quality_check =False

