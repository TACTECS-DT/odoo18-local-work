from openerp import models, fields, api
from datetime import date,datetime
class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    is_collection = fields.Boolean(string="IS Collection")
    is_deposit=is_new_field = fields.Boolean(string="IS Deposit")
    collection_date = fields.Date(string="Collection Date")
    deposit_date = fields.Date(string="Deposit Date")

    def button_collection_date(self):
        self.collection_date=date.today()
        self.is_collection=True

        for rec in self.env['operation.operation'].search([]):

            for inv in rec.invoice_ids:
                if self.ref == inv.name:
                    rec.collection_date=self.collection_date

    def button_deposit_date(self):
        self.deposit_date = date.today()
        self.is_deposit=True
        for rec in self.env['operation.operation'].search([]):
            for inv in rec.invoice_ids:
                if self.ref == inv.name:
                    rec.deposit_date = self.deposit_date
