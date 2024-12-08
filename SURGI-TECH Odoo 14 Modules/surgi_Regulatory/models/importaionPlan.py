from odoo import models, fields, api, _


class ImportationPlan(models.Model):
    _name = 'importation.plan'

    name = fields.Char("Importation Plan Number")
    planYear = fields.Char("Plan Year")
    registrationLicense = fields.Many2one('registration.license', string="Registration License")
    countryOfOrigin = fields.Many2many(comodel_name='country.manufacturer', string="Country of Origin")
    legelManufacturer = fields.Many2one('legal.manufacturer',string="legal Manufacturer")
    legelManufacturerAddress = fields.Many2one('address.manufacturer',string="legal Manufacturer Address",domain="[('legal_maunfacture', '=', legelManufacturer)]")
    legelManufacturerCountry = fields.Many2one(related="legelManufacturerAddress.country")
    actualManufacturer = fields.Many2many('actual.manufacturer', string="Actual Manufacturer")
    actualManufacturerAddress = fields.Many2one('address.manufacturer',string="Actual Manufacturer Address",domain="[('actual_maunfacture', '=', actualManufacturer)]")
    actualManufacturerCountry = fields.Many2one(related="actualManufacturerAddress.country")

    IssueDate = fields.Date(string="Issue Date")
    expiryDate = fields.Date(string="Expiry date")
    attachmentPage = fields.One2many("importation.pages", "importationPlan")
    planProduct = fields.One2many("importation.pages", "importationPlan")

    def name_get(self):
        res = []
        for rec in self:
            name = u"{}#{}".format(rec.planYear, rec.name)
            res.append((rec.id, name))
        return res


class RegularityImportationPages(models.Model):
    _name = "importation.pages"
    importationPlan = fields.Many2one("importation.plan", "Importation Plan")
    certificateName = fields.Char("Certificate")
    certificateExpiry = fields.Date("Expiry Date")
    # attachmentImportationPlan = fields.Many2many('ir.attachment', 'class_importation_attachments_rel', 'class_id', 'attachment_id', 'Attachments')
    ######################################################################################
    certificateName = fields.Many2one("product.certificate",string="Certificate")
    certificateExpiry = fields.Date(related="certificateName.name.expiryDate",string="Expiry Date")
    certificateAttachment = fields.Many2many(related="certificateName.certificateAttachment", string='Attachments')
    #######################################################################################
    productTemplate = fields.Many2one('product.product', string='product')
    internalRef = fields.Char(related='productTemplate.regularityRef',readonly=False)
    regularityLabelRef = fields.Char(related='productTemplate.regularityLabelRef', string='Label Ref',readonly=False)
    ProductClass = fields.Selection(related='productTemplate.ProductClass',readonly=False)
    productTypeRegularity = fields.Selection(related='productTemplate.productTypeRegularity',readonly=False)
    productSterilizeField = fields.Boolean(related='productTemplate.sterilizeField',readonly=False)
    ProductVendor = fields.Many2one(related="productTemplate.seller_ids.name", string="Supplier",
                                    readonly=False)