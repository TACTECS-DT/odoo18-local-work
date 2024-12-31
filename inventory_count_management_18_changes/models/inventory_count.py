from odoo import api, fields, models



class StockInvCount(models.Model):
    _inherit  = 'setu.stock.inventory.count'
 
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Location",
        domain="[('company_id','=',company_id),('usage', '=', 'internal'),('warehouse_id','=',warehouse_id)]"
    )

    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Warehouse",
          domain="[('company_id','=',company_id)]"
    )
    inventory_reference= fields.Char(string="Inventory Reference")
    scanning_mode = fields.Selection(selection=[("internal_ref","By Internal reference"),("lot_serial_no","By Lot/Serial Number"),("products","By Products"),("product_categories","By Products category")],string="Scanning Mode")
    allw_product_ids = fields.Many2many("product.product",    'setu_stock_inventory_allw_product_rel',string="Products",domain="[('company_id','in',[company_id,False])]")
    product_category_ids = fields.Many2many("product.category",string="Products Category")
    company_id = fields.Many2one("res.company",string="Company",required=True)
    is_lock = fields.Boolean(string="Lock")
    is_all_line_approved = fields.Boolean(string="is_all_line_approved")
    is_all_line_refused = fields.Boolean(string="is_all_line_refused")

    type = fields.Selection([
        ('Single Session', 'Single Session'),
        ('Multi Session', 'Multi Session')],
        default='Multi Session',
        required=True,
        string="Type"
    )
    
