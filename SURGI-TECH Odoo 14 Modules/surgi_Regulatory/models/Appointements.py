from odoo import models, fields, api, _


class ScientificAppointment(models.Model):
    _name = 'scientific.appointment'
    name = fields.Char(string="System Name")
    appointmentType = fields.Selection([('sterile', 'Sterile'),
                                        ('non_sterile', 'Non Sterile'),],
                                       string="Type of Appointment", )
    acceptDate = fields.Date(string="Acceptance Date")
    expiryDate = fields.Date(string="Expiry date")
    request_id = fields.Char("Request ID", store=True)
    tempNum = fields.Char("Temporary Number", store=True)
    attachment_page = fields.One2many('product.appointment', "appointment")
    scopOfProduct = fields.One2many('product.appointment', "appointment")


class productAppointment(models.Model):
    _name = 'product.appointment'

    appointment = fields.Many2one("scientific.appointment", "Appointment")
    Product = fields.Many2one('product.product', string='product')
    ProductVendor = fields.Many2one(related="Product.seller_ids.name", string="Supplier",
                                    readonly=False)
    productCateg= fields.Many2one(related="Product.categ_id", string="Line")
    sterile = fields.Boolean(string="Sterile", related="Product.sterilizeField",readonly=False)
    productSerial = fields.Many2one('stock.production.lot', string='Serial Number',
                                                  domain="[('product_id','=',Product)]")
    certificateName = fields.Many2one("product.certificate",string="Certificate")
    certificateExpiry = fields.Date(related="certificateName.name.expiryDate",string="Expiry Date")
    certificateAttachment = fields.Many2many(related="certificateName.certificateAttachment", string='Attachments')
    @api.onchange('Product')
    def compute_display_name(self):
        self.productSerial = ""


