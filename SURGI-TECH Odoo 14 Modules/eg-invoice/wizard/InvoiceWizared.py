from odoo import fields, models, api


class InvoiceWizared(models.TransientModel):
    _name = 'egytax.invoicewizared'
    _description = 'Description'

    uuid = fields.Char("uuid")
    internalId=fields.Char("internalId")
    documentTypeNamePrimaryLang=fields.Char("Type")
    issuerName=fields.Char("issuer Name")
    receiverName=fields.Char("receiver Name")
    dateTimeIssued=fields.Char("date Issued")
    dateTimeReceived=fields.Char("date Received")
    totalSales=fields.Float("Total Sales")
    totalDiscount=fields.Float("Total Discount")
    netAmount=fields.Float("Net Amount")
    total=fields.Float("Total")
    cancelRequestDate=fields.Char("Cancel Request Date")
    rejectRequestDate=fields.Char("Reject Request Date")
    status=fields.Char("Status")

class View(models.Model):
    _inherit = "ir.ui.view"

    type = fields.Selection(selection_add=[("invoice_list", "Invoice List Vizualisation")])