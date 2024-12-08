#from stdnum.mx.rfc import _get_date

from odoo import models, fields, api
import datetime
from odoo.tools.translate import _

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    priceusd = fields.Float(
        string='Usd Cost',
        related='lot_id.priceusd',
        
    )
    #total_usdcost=
    total_usdcost= fields.Float(
        string='Total Usd Cost',
            compute='_usdcostTotal' )
        
    @api.depends('priceusd')
    def _usdcostTotal(self):
            for record in self:
                record.total_usdcost = record.priceusd*record.available_quantity
                
                
                
                
class CustomStockProductionLot(models.Model):
    _inherit = "stock.production.lot"
    
    
    lot_name = fields.Char(string='Lot Name',  help="Unique Serial Number", required=True)
    lot_no = fields.Char(string='Lot Fake no work with',  help="Unique Serial Number")
    expiration_date = fields.Date(string='Expiration Date', required=True)
    invoice_date = fields.Date(string='Invoice Date',)
    priceusd = fields.Float(
        string='Usd Cost',
    )
    
    
    effective_date = fields.Date(string='Effective Date' )
    @api.onchange('product_id')
    def _compute_effective_date(self):
        for record in self:
            record.effective_date = datetime.date.today()
    
            
    gs_mrn = fields.Char(string='GS MRN')
    import_ref = fields.Char(string='Import Ref.')
    isPacked=fields.Boolean("Is Packed")
    packedSerials=fields.One2many(string="Serials",comodel_name="surgi.packed.serial",inverse_name="lot_id")
    
    
    
    
class lot_packed(models.Model):
    _name="surgi.packed.serial"
    serialnumber=fields.Many2one(string="Serials",comodel_name="stock.production.lot")
    lot_id=fields.Many2one(string="lot_id",comodel_name="stock.production.lot")
    pass
    
    
    
    
    
class CustomStockPackOperation(models.Model):
    _inherit = "stock.move.line"

    lot_name = fields.Char(string='Serial Number', help="Unique Serial Number")
    expiration_date=fields.Date()

