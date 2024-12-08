from odoo import fields, models, api
from . import EnvoConfig
from odoo.exceptions import UserError,Warning,ValidationError
class ModelName(models.Model):
    _name = 'egytax.getdocuments'
    _description = 'Description'


    publicUrl = fields.Char(string="URL")
    uuid=fields.Char(string="UUID")
    submissionUUID=fields.Char(string="Submission ID")
    longId=fields.Char(string="Long ID")
    internalId=fields.Char(string="Internal Id")
    typeName=fields.Char(string="Type")
    documentTypeNamePrimaryLang=fields.Char(string="Type EN")
    documentTypeNameSecondaryLang=fields.Char(string="Type AR")
    typeVersionName=fields.Char(string="Version")
    receiverId=fields.Char(string="Reciever ID")
    receiverName=fields.Char(string="Receiver Name")
    issuerId=fields.Char(string="Issuer ID")
    issuerName=fields.Char(string="Issuer Name")
    dateTimeIssued=fields.Datetime(string="Date Time Issued")
    dateTimeReceived=fields.Datetime(string="Date Time Recieved")
    totalSales=fields.Float(string="Total Sale")
    totalDiscount=fields.Float(string="Total Discount")
    netAmount=fields.Float(string="Net Ammount")
    total=fields.Float(string="Total")
    maxPercision=fields.Float(string="Max Precission")
    invoiceLineItemCodes=fields.Char(string="Invoice Lines Items Codes")
    cancelRequestDate=fields.Datetime(string="Cancel Request Date")
    rejectRequestDate=fields.Datetime(string="Reject Request Date")
    cancelRequestDelayedDate=fields.Datetime(string="Cancel Request DelayDate")
    rejectRequestDelayedDate=fields.Datetime(string="Reject Request Delay Date")
    declineCancelRequestDate = fields.Datetime(string="Decline Cancel Request Date")
    declineRejectRequestDate = fields.Datetime(string="Decline Reject Request Date")
    documentStatusReason=fields.Text(string="Status Reason")
    status=fields.Char(string="Status")
    createdByUserId=fields.Char(string="Created By")
    doctype=fields.Selection(string="Type",selection=[],selection_add = [('Recieved', 'Recieved'), ('Sent', 'Sent')],compute="computetype")
    @api.model
    def computetype(self):
        for rec in self:
            if rec.issuerId==self.env.company.registration_id:
                rec.doctype="Sent"
            else:
                rec.doctype="Recieved"

    @api.model            
    def get_live_invoices(self,page,direction,pagesize=100):
        return EnvoConfig.EnvoConfig.getlivedocuments(self,company_id=self.env.company,page=page,pagesize=pagesize,direction=direction)
        
        pass
    @api.model
    def searchuuidinvoice(self,uuid=None):
        return EnvoConfig.EnvoConfig.searchUuidDocuments(self,company_id=self.env.company,uuid=uuid)
        pass
    @api.model
    def cancelsentinvoice(self,uuid=None,reason=None):
        print("d")
        if(EnvoConfig.EnvoConfig.CancelDocument(document=uuid,reason=reason,company_id=self.env.company)):
            return{'res':True}
        else:
            return{'res':False}
        pass
    @api.model
    def Rejectinvoice(self,uuid=None,reason=None):
        print("d")
        if(EnvoConfig.EnvoConfig.RejectDocument(document=uuid,reason=reason,company_id=self.env.company)):
            return{'res':True}
        else:
            return{'res':False}
        pass
    @api.model
    def rejectCommingInvoice(self):
        pass            

    # def onchange(self,*args):
    #
    #
    #
    #     #mymodule = self.get_server_info(self.name)
    #     message_id = self.env['succesesswizerd.egtaxmodel'].create({'message': 'Your action was completed.'})
    #    # return {
    #     #    'name': 'Message',
    #      #   'type': 'ir.actions.act_window',
    #       #  'view_mode': 'form',
    #        # 'res_model': 'succesesswizerd.egtaxmodel',
    #        # 'res_id': message_id.id,
    #        # 'target': 'new'
    #     #}
    #     raise Warning('Creation of new record is not allowed.')
    #     return False
    #
    #     pass

    @api.model
    def action_update_recent_invoices(self):
        data = EnvoConfig.EnvoConfig.getRecentDocuments(self, company_id=self.env.company)
        datax = data[::-1]
        print("data")
        if data:
            self.create(data)

        try:
            form_view_id = self.env.ref("eg-invoice.list_egytax_recentmoves").id
        except Exception as e:
            form_view_id = False
        form_view_id = self.env.ref("eg-invoice.list_egytax_recentmoves").id
        return {
            'name': 'Online Taxes',
            'res_model': 'egytax.getdocuments',
            'type': 'ir.actions.act_window',
            # 'view_type': 'tree',
            'view_mode': 'tree',
            'view_id': form_view_id,
            #'domain': [('categ_id', 'in', categories)],

            'target': 'current'
        }

        pass


class SuccesessWizerdegtaxModel(models.TransientModel):
    _name = 'succesesswizerd.egtaxmodel'
    _description = "Show Message"

    message = fields.Text('Message', required=True)

    @api.model
    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}
