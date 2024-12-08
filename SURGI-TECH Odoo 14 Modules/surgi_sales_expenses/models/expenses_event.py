from odoo import models, fields, api
class EpensesEventModel(models.Model):
    _name = 'hr.expenses.event'
    _rec_name = 'name'
    _description = 'Expenses Event'

    name = fields.Char(string="Event Name",required=True)
    date = fields.Date(string="Date", )
    event_code = fields.Char(string="Event Code",)
    event_country = fields.Char(string="Event Country",)