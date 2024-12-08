from odoo import models, fields, api, _


class Check_Report_Regularity(models.Model):
    _name = 'check.report'
    name = fields.Many2one('purchase.order',string="Purchase Order")
    partner_id = fields.Many2one(related="name.partner_id",string="Customer")
    order_line = fields.One2many(related="name.order_line",string="Products")

class purchaseOrderLineRegularity(models.Model):
    _inherit = 'purchase.order.line'
    registrationLicense = fields.Char(string="Registration License",compute="registrationLicenseProduct")
    registrationLicenseExpiry = fields.Date(string="RL Expiry Date",compute="registrationLicenseExpiryproduct")

    importationPlanName = fields.Char(string="Importation Plan",compute="importationPlanProduct")
    importationPlanExpiry = fields.Date(string="IP Expiry Date",compute="importationPlanExpiryproduct")

    scientificCommitteeName = fields.Char(string="Scientific Committee",compute="scientificCommitteeNameProduct")

    appointmentName = fields.Char(string="Appointment",compute="appointmentProduct")
    appointmentaccept = fields.Date(string="Appointment Acceptance Date",compute="appointmentExpiryproduct")

    certificateName = fields.Char(string="Certificate",compute="certificateNameProduct")
    certificateExpiry = fields.Date(string="Certificate Expiry Date",compute="certificateExpiryProduct")
    certificatetype = fields.Char(string="Certificate Type",compute="certificateTypeProduct")

    def registrationLicenseProduct(self):
        for objs in self:
            obj_reg=""
            obj_test = self.env['product.registration'].search([('productTemplate', 'like', objs.product_id.id)])
            print (obj_test)
            print('--------------------------------')
            for val in obj_test:
                obj_reg = val.registrationLicense.registration_name+"#"+val.registrationLicense.name
                print(obj_reg)
            objs.registrationLicense = obj_reg
    def registrationLicenseExpiryproduct(self):

        for objs in self:
            obj_reg=""
            obj_test = self.env['product.registration'].search([('productTemplate', '=', objs.product_id.id)])
            print (obj_test)
            print('--------------------------------')
            for val in obj_test:
                obj_reg = val.registrationLicense.expiryDate
                print(obj_reg)
            objs.registrationLicenseExpiry = obj_reg


    def importationPlanProduct(self):
        for objs in self:
            obj_reg=""
            obj_test = self.env['importation.pages'].search([('productTemplate', '=', objs.product_id.id)])
            print (obj_test)
            print('--------------------------------')
            for val in obj_test:
                obj_reg = val.importationPlan.planYear+"#"+val.importationPlan.name
                print(obj_reg)
            objs.importationPlanName = obj_reg
    def importationPlanExpiryproduct(self):

        for objs in self:
            obj_reg=""
            obj_test = self.env['importation.pages'].search([('productTemplate', '=', objs.product_id.id)])
            print (obj_test)
            print('--------------------------------')
            for val in obj_test:
                obj_reg = val.importationPlan.expiryDate
                print(obj_reg)
            objs.importationPlanExpiry = obj_reg

    def scientificCommitteeNameProduct(self):
        for objs in self:
            obj_reg=""
            obj_test = self.env['product.scientificcommittee'].search([('productTemplate', '=', objs.product_id.id)])
            print (obj_test)
            print('--------------------------------')
            for val in obj_test:
                obj_reg =val.scientificCommittee.name
                print(obj_reg)
            objs.scientificCommitteeName = obj_reg

    def appointmentProduct(self):
        for objs in self:
            obj_reg=""
            obj_test = self.env['product.appointment'].search([('Product', '=', objs.product_id.id)])
            print (obj_test)
            print('--------------------------------')
            for val in obj_test:
                obj_reg = val.appointment.name
                print(obj_reg)
            objs.appointmentName = obj_reg
    def appointmentExpiryproduct(self):

        for objs in self:
            obj_reg=""
            obj_test = self.env['product.appointment'].search([('Product', '=', objs.product_id.id)])
            print (obj_test)
            print('--------------------------------')
            for val in obj_test:
                obj_reg = val.appointment.acceptDate
                print(obj_reg)
            objs.appointmentaccept = obj_reg



    def certificateNameProduct(self):
        for objs in self:
            obj_reg=""
            obj_test = self.env['product.certificate'].search([('productTemplate', '=', objs.product_id.id)])
            print (obj_test)
            print('--------------------------------')
            for val in obj_test:
                obj_reg = val.name.certificate_name + "#" + val.name.CertificateN
                print(obj_reg)
            objs.certificateName = obj_reg
    def certificateExpiryProduct(self):
        for objs in self:
            obj_reg=""
            obj_test = self.env['product.certificate'].search([('productTemplate', '=', objs.product_id.id)])
            print (obj_test)
            print('--------------------------------')
            for val in obj_test:
                obj_reg = val.name.expiryDate
                print(obj_reg)
            objs.certificateExpiry = obj_reg
    def certificateTypeProduct(self):
        for objs in self:
            obj_reg=""
            obj_test = self.env['product.certificate'].search([('productTemplate', '=', objs.product_id.id)])
            print (obj_test)
            print('--------------------------------')
            for val in obj_test:

                obj_reg = val.name.TypeOfCertificate
                print(obj_reg)
            objs.certificatetype = obj_reg
