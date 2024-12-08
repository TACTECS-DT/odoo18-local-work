from odoo import models, fields, api, _
from datetime import *
from dateutil.relativedelta import *
from odoo.exceptions import AccessError, ValidationError, MissingError, UserError
from collections import defaultdict

class RegularityCertificate(models.Model):
    _name = "regularity.certificate"
    _inherit = ['mail.thread','mail.activity.mixin']

    CertificateN = fields.Char(string="Certificate Number")
    certificate_name = fields.Char(stirng="Certificate Name",store=True)
    # TypeOfCertificate = fields.Selection(string="Type Of Certificate",
    #                                 selection=[('CFG', 'CFG'), ('FSC', 'FSC'), ('DE', 'DE'),
    #                                              ('CE', 'CE'), ('ISO', 'ISO'), ('DOC', 'DOC'),], )
    TypeOfCertificate = fields.Many2one('typeof.certificate',string="Type Of Certificate")
    IssuingAuthority = fields.Many2one('issuing.authority',string="Issuing Authority",store=True)
    IssuingAuthorityCountry = fields.Many2one(related="IssuingAuthority.country",string="Issuing Authority Country",store=True)
    LatestIssueCheckLink = fields.Char(string="Latest Issue Check Link",store=True)
    LatestLastIssueCheckDate = fields.Char(string="Latest Last Issue Check Date",store=True,readonly=True)
    LatestLastIssueCheckUser = fields.Char(string="Latest Last Issue Check User",store=True,readonly=True)
    LatestLastIssueCheckresult = fields.Selection(string="Latest issue Check Result",
                                    selection=[('Not_the_Latest', 'Not the Latest'),
                                               ('Latest_Issue', 'Latest Issue')],)

    countryOfOrigin = fields.Many2many(comodel_name='country.manufacturer', string="Country of Origin")
    legelManufacturer = fields.Many2one('legal.manufacturer',string="legal Manufacturer")
    legelManufacturerAddress = fields.Many2one('address.manufacturer',string="legal Manufacturer Address",domain="[('legal_maunfacture', '=', legelManufacturer)]")
    legelManufacturerCountry = fields.Many2one(related="legelManufacturerAddress.country")
    actualManufacturer = fields.Many2many('actual.manufacturer', string="Actual Manufacturer")
    actualManufacturerAddress = fields.Many2one('address.manufacturer',string="Actual Manufacturer Address",domain="[('actual_maunfacture', '=', actualManufacturer)]")
    actualManufacturerCountry = fields.Many2one(related="actualManufacturerAddress.country")

    IssueDate = fields.Date(string="Issue Date")
    expiryDate = fields.Date(string="Expiry date")
    Legalization = fields.Many2one('certificate.legalization',string="Legalization")
    refCountry = fields.Selection([
        ("yes", "Yes"), ("no", "No"),
    ], string="Reference Country")

    Product_class = fields.Many2one('classof.certificate',string="Class",domain="[('typeOfCertificate', '=', TypeOfCertificate)]")
    attachment_page = fields.One2many('product.certificate', "name","Attachment")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('expiry', 'Expiry'),('valid','Valid'),('renewal','Renewal'),

    ], string='Status', copy=False, index=True, readonly=True, default='draft', tracking=True,store=True,
        compute="_compute_Status")
    productForms = fields.One2many('product.certificate', "name")
    # check_report=fields.Many2one('check.report')
    Description = fields.Text(string="Description")
    checkURL = fields.Boolean(readonly=True)

    def UrlChecker(self):
        user = self.env.user
        user_name = user.name
        now = datetime.now() + timedelta(hours=2)
        self.checkURL = True
        self.LatestLastIssueCheckDate = now
        self.LatestLastIssueCheckUser = user_name
        url = self.LatestIssueCheckLink
        return{
            'type': 'ir.actions.act_url',
            'url':url,

        }
    # def notifyStatus(self):
    #     notification = {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'title': _('There are no expense reports to approve.'),
    #             'type': 'warning',
    #             'sticky': False,  #True/False will display for few seconds if false
    #         },

    def name_get(self):
        res = []
        for rec in self:
            name = u"{}#{}".format(rec.certificate_name, rec.CertificateN)
            res.append((rec.id, name))
        return res
    def _send_notification(self, state, partners):
        message = _('Certificate: %s is %s, Need Renewal') % (str(self.certificate_name),self.CertificateN )
        return self.message_notify(body=message, partner_ids=partners)
    # def action_hr_approve(self):
    #     group = self.env.ref('surgi_regularity.reg_viewer_group').sudo().users
    #     partners = []
    #     if group:
    #         for usr in group:
    #             partners.append(usr.partner_id.id)
    #         self._send_notification('test', partners)
    @api.depends('expiryDate')
    def _compute_Status(self):
        group = self.env.ref('surgi_Regulatory.reg_viewer_group').sudo().users
        partners = []
        now = date.today()
        time_threshold = ( now - relativedelta(months=+4))
        time_four_mounth_after = ( now + relativedelta(months=+4))

        for rec in self:
            if rec.expiryDate > time_four_mounth_after :
                rec.write({'state': 'valid'})
            elif rec.expiryDate > time_threshold:
                rec.write({'state': 'renewal'})
                if group:
                    for usr in group:
                        partners.append(usr.partner_id.id)
                    rec._send_notification('test', partners)
            else:
                rec.write({'state': 'expiry'})



class RegularityCertificateProduct(models.Model):
    _name = 'product.certificate'
    name = fields.Many2one("regularity.certificate", "Certificate")
    certificateAttachment = fields.Many2many('ir.attachment', 'class_certificate_attachments_rel', 'class_id','attachment_id', 'Attachments')
    certificateName = fields.Char("name")
    check_report = fields.Many2one("check.report", "Certificate")
    productTemplate = fields.Many2one('product.product', string='product')
    internalRef = fields.Char(related='productTemplate.regularityRef',readonly=False)
    productCateg = fields.Many2one(related='productTemplate.categ_id', string='Category')
    ProductVendor = fields.Many2one(related="productTemplate.seller_ids.name", string="Supplier",
                                    readonly=False)
    regularityLabelRef = fields.Char(related='productTemplate.regularityLabelRef', string='Label Ref',readonly=False)
    ProductClass = fields.Selection(related='productTemplate.ProductClass',readonly=False)


class Irattachment(models.Model):
    _inherit = 'ir.attachment'

