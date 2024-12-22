from odoo import api, fields, models



    
class StockInvCount(models.Model):
    _inherit  = 'setu.stock.inventory.count'
    

    inventory_reference= fields.Char(string="Inventory Reference")
    scanning_mode = fields.Selection(selection=[("internal_ref","By Internal reference"),("lot_serial_no","By Lot/Serial Number")],string="Scanning Mode")
    company_id = fields.Many2one("res.company",string="Company",required=True)
    is_lock = fields.Boolean(string="Lock")
