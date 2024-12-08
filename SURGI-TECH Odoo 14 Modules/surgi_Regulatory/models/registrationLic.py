from odoo import models, fields, api, _


class RegistrationLicenseModel(models.Model):
    _name = "registration.license"
    @api.onchange('actualManufacturer')
    def get_actualManufacturer_domain(self):
        obj = self.env["address.manufacturer"].search([( "actual_maunfacture", "=", self.actualManufacturer.ids)])
        print(obj)
        res = []
        for reco in obj :
            if  reco.actual_maunfacture :
                res.append(reco.country.id)
                print(res)
            else :
                res = []
        print(res)

        return {'domain': {'countryOfOrigin': [('id', '=', res)]}}

    name = fields.Char("Registration Number",store=True)
    registration_name = fields.Char("Registration Name",store=True)
    sterilizeMethod = fields.Many2one('sterilize.method',store=True,string="Sterilization method")

    legelManufacturer = fields.Many2one('legal.manufacturer',store=True,string="legal Manufacturer")
    legelManufacturerAddress = fields.Many2one('address.manufacturer',store=True,string="legal Manufacturer Address",domain="[('legal_maunfacture', '=', legelManufacturer)]")
    actualManufacturer = fields.Many2many('actual.manufacturer', store=True,string="Actual Manufacturer")
    actualManufacturerAddress = fields.Many2many ('address.manufacturer',store=True,string="Actual Manufacturer Address",domain="[('actual_maunfacture', '=', actualManufacturer)]")

    TradeName = fields.Char(string="Trade Name",store=True)
    MedicalDeviceName = fields.Char(string="Medical Device Name",store=True)
    MedicalDeviceDesc = fields.Char(string="Medical Device Description" ,store=True)
    MedicalDeviceCateg = fields.Many2one('medical.category',string="Medical Device Category",store=True)
    NomenClature = fields.Many2one('nomen.clature',string="NomenClature Type",store=True)
    NomenClatureCode = fields.Char(string="NomenClature Code" ,store=True)
    AdoptedRegulation = fields.Many2one('adopted.regulation',string="Adopted Regulation name",store=True)
    AdoptedRegulationClass = fields.Char(related='AdoptedRegulation.NameClass',string="Adopted Regulation Class",store=True)


    PackingDesc = fields.Text(string="Packing Description",store=True)
    intendedUse = fields.Text(string="Description",store=True)

    Material = fields.Char(string="Material Of Primary Pack",store=True)
    NumOfunit = fields.Char(string="Number Of Unit Primary Pack",store=True)
    MaterialOfScendPack = fields.Char(string="Material Of second Pack",store=True)
    numUnitPerSec = fields.Char(string="Number Unit Per Second Repack")
    countryOfOrigin = fields.Many2many(comodel_name='country.manufacturer', store=True,string="Country of Origin")
    sterilize = fields.Selection(
            [('sterilize', 'Sterile'),('nonsterilize', 'Non-Sterile')
             ], store=True,string='Sterilize')
    isDosage = fields.Boolean(string="Is Dosage Form")
    IssueDate = fields.Date(store=True,string="Issue Date")
    expiryDate = fields.Date(store=True,string="Expiry Date")
    registrationProduct = fields.One2many("product.registration", "registrationLicense")
    attachmentPage = fields.One2many("product.registration", "registrationLicense")
    variationNum = fields.One2many("product.registration", "registrationLicense")
    RowMatrial = fields.One2many("product.registration", "registrationLicense")
    regLicAttachment = fields.One2many("product.registration", "registrationLicense")


    dateDiff = fields.Char("Registration Shelf Life", compute="_computeShelfLife")
    storgeConditions = fields.Many2one('storge.conditions',store=True,string="Storage Conditions")
    year = fields.Selection([
            ('0 Years', '0 Year'),
            ('1 Year', '1 Year'),
            ('2 Year', '2 Year'),
            ('3 Years', '3 Years'),
            ('4 Years', '4 Years'),
            ('5 Years', '5 Years'),
            ('6 Year', '6 Year'),
            ('7 Years', '7 Years'),
            ('8 Years', '8 Years'),
            ('9 Years', '9 Years'),
            ('10 Years', '10 Years'),

        ], store=True,string='Years')

    month = fields.Selection(
            [('0 Month', '0 Month'),('1 Month', '1 Month'), ('2 Month', '2 Month'), ('3 Months', '3 Months'), ('4 Months', '4 Months'),
             ('5 Months', '5 Months'), ('6 Months', '6 Months'), ('7 Months', '7 Months'), ('8 Months', '8 Months'),
             ('9 Months', '9 Months'),
             ('10 Months', '10 Months'), ('11 Months', '11 Months'), ('12 Months', '12 Months')
             ], store=True,string='Months')


    ######################################################################################################
    def name_get(self):
        res = []
        for rec in self:
            name = u"{}#{}".format(rec.registration_name, rec.name)
            res.append((rec.id, name))
        return res
    #########################################################################################################
    @api.onchange("year", "month")
    def _computeShelfLife(self):
        year_val = ''
        mounth_val = ''
        if self.year:
            year_val = self.year
        if self.month:
            mounth_val = self.month
        if not self.year:
            self.dateDiff = "Not Provided"
        if not self.month:
            self.dateDiff = "Not Provided"
        self.dateDiff = year_val + ", " + mounth_val


class ProductForms(models.Model):
    _name = "product.registration"
    registrationLicense = fields.Many2one('registration.license', store=True,string="Registration License")
    productTemplate = fields.Many2one('product.product', store=True,string='product')
    internalRef = fields.Char(related='productTemplate.regularityRef',string='internal ref',readonly=False)
    regularityLabelRef = fields.Char(related='productTemplate.regularityLabelRef', string='Label Ref',readonly=False)
    ProductClass = fields.Selection(related='productTemplate.ProductClass',readonly=False)
    productSterilizeField = fields.Boolean(related='productTemplate.sterilizeField',readonly=False)
    productDescription = fields.Char("Description")
    productTypeRegularity = fields.Selection(related='productTemplate.productTypeRegularity',readonly=False)
    ProductVendor = fields.Many2one(related="productTemplate.seller_ids.name",string="Supplier",
                                    readonly=False)
    ######################################################################################
    certificateName = fields.Many2one("product.certificate",store=True,string="Certificate")
    certificateExpiry = fields.Date(related="certificateName.name.expiryDate",string="Expiry Date")
    certificateAttachment = fields.Many2many(related="certificateName.certificateAttachment",string='Attachments')
    RegistrationAttachmentName = fields.Char("Name")
    RegistrationAttachment = fields.Binary('Attachments')

    ####################################################################
    variationNum = fields.Char("Variation Number")
    variationType = fields.Char("Variation Type")
    variationDate = fields.Date("Variation Date")

    ###################################################
    CompanyName = fields.Char("Component Name",store=True)
    CompanyMatrial= fields.Char("Component Material",store=True)