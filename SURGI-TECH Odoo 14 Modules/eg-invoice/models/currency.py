from odoo import models, fields, api,_
class Res_currency_inhert(models.Model):
    _inherit = 'res.currency.rate'
    _description = 'model.einvoice.name'
    
    currencyvalue = fields.Float(string='Value',)
    
    currencydate = fields.Date(string='Date')
    
    
    
