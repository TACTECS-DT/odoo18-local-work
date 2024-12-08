from odoo import models, fields, api, _




class ScientificCommittee(models.Model):
    _name = 'scientific.committee'

    name = fields.Char("SN")
    description = fields.Text("Description",help="Scientific Committee Description")
    IssueDate = fields.Date(string="Issue Date")
    expiryDate = fields.Date(string="Expiry date")
    productForms = fields.One2many('product.scientificcommittee', "scientificCommittee")
    attachmentPage = fields.One2many("product.scientificcommittee", "scientificCommittee")


class ProductScientificCommittee(models.Model):
    _name = 'product.scientificcommittee'
    scientificCommittee = fields.Many2one("scientific.committee", "Scientific Committee")
    productTemplate = fields.Many2one('product.product', string='product')
    ProductVendor = fields.Many2one(related='productTemplate.seller_ids.name', string="Supplier")
    productSterilizeField = fields.Boolean(related='productTemplate.sterilizeField')
    ProductClass = fields.Selection(related='productTemplate.ProductClass')
    certificateName = fields.Many2one("product.certificate",string="Certificate")
    certificateExpiry = fields.Date(related="certificateName.name.expiryDate",string="Expiry Date")
    certificateAttachment = fields.Many2many(related="certificateName.certificateAttachment", string='Attachments')