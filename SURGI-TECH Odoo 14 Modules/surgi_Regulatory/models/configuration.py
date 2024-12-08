from odoo import models, fields, api, _

class countryMaunfacture(models.Model):
    _name = 'country.manufacturer'
    name = fields.Char(string="Code",store=True)
    countryName = fields.Char(string='Country Name',store=True)
    # actual_maunfacture = fields.Many2many('actual.manufacturer',string="Actual Manufacturer")
    # legal_maunfacture = fields.Many2many('legal.manufacturer',string="Legal Manufacturer")

class AddressMaunfacture(models.Model):
    _name = 'address.manufacturer'
    legal_maunfacture = fields.Many2one('legal.manufacturer',string="Legal Manufacturer")
    actual_maunfacture = fields.Many2one('actual.manufacturer',string="Actual Manufacturer")
    country = fields.Many2one('country.manufacturer', string="Country")
    name = fields.Char(string="Address",store=True)


class productActualManufacturer(models.Model):
    _name = 'actual.manufacturer'
    name = fields.Char(store=True,string="Actual Manufacturer")
    address = fields.One2many('address.manufacturer','actual_maunfacture', string="Address")



class productLegalManufacturer(models.Model):
    _name = 'legal.manufacturer'
    name = fields.Char(store=True,string="Legal Manufacturer")
    address = fields.One2many('address.manufacturer','legal_maunfacture', string="Address")



class regularitySterilizeMethod(models.Model):
    _name = 'sterilize.method'
    name = fields.Char(store=True, string="Sterilize Method")

class regularitystorgeConditions(models.Model):
    _name = 'storge.conditions'
    name = fields.Char(string="Storge Conditions", store=True)

class IssuingAuthority(models.Model):
    _name = 'issuing.authority'
    name = fields.Char("Issuing Authority")
    country = fields.Char("Issuing Authority Country")
    country = fields.Many2one('country.manufacturer', string="Issuing Authority Country")




class certificateLegalization(models.Model):
    _name = 'certificate.legalization'
    name = fields.Char("Legalization")



class typeOfCertificate(models.Model):
    _name = 'typeof.certificate'
    name = fields.Char( string="Type Of Certificate")
class CertificateClass(models.Model):
    _name = 'classof.certificate'
    name = fields.Char(string="Class Name")
    typeOfCertificate = fields.Many2many('typeof.certificate',string="Type Of Certificate")

class MedicalDeviceCategory(models.Model):
    _name = 'medical.category'
    name = fields.Char(string="Medical Device Category", store=True)

class nomenClatureType(models.Model):
    _name = 'nomen.clature'
    name = fields.Char(string="Nomen Clature Type", store=True)

class AdoptedRegulation(models.Model):
    _name = 'adopted.regulation'
    name = fields.Char(string="Adopted Regulation", store=True)
    NameClass = fields.Char(string="Class", store=True)
