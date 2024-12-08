
from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class AccountMove(models.Model):
    _inherit = 'account.move'
    is_reciept=fields.Boolean("Is Pos Reciept")
    pos_reciept=fields.Many2one("pos.order","E-Reciept")
    reciept_name=fields.Char("Reciept Name")
    
    
    @api.model
    def create(self, values):
        if 'is_reciept' in values and values['is_reciept']:
            if not (self.pos_reciept or 'pos_reciept' in  values) and not (self.reciept_name or 'reciept_name' in values):
                raise ValidationError("Please Provide Reciept Name")
            else:
                if self.pos_reciept or 'pos_reciept' in values:
                    if self.pos_reciept:
                        values['name']=self.pos_reciept.name
                        #self.pos_reciept.invoiceassigned=True
                    else:
                        posorder=self.env['pos.order'].search([('id','=',values['pos_reciept'])])
                        values['name']=posorder[0].name
                        #values['pos_reciept'].invoiceassigned=True
                elif self.reciept_name or 'reciept_name' in  values:
                    if self.reciept_name:
                        values['name']=self.reciept_name
                    else:
                        values['name']=values['reciept_name']
                        
     
            
                
        
        res=super(AccountMove, self).create(values)
        if self.pos_reciept:
            self.pos_reciept.invoiceassigned=True
        else:
            self.pos_reciept.invoiceassigned=False
        return res
    
    
    def write(self, values):
        if 'is_reciept' in values and values['is_reciept']:
            if not (self.pos_reciept or 'pos_reciept' in  values) and not (self.reciept_name or 'reciept_name' in values):
                raise ValidationError("Please Provide Reciept Name")
            else:
                if self.pos_reciept or 'pos_reciept' in values:
                    if self.pos_reciept:
                        values['name']=self.pos_reciept.name
                        #self.pos_reciept.invoiceassigned=True
                    else:
                        posorder=self.env['pos.order'].search([('id','=',values['pos_reciept'])])
                        values['name']=posorder[0].name
                        #values['pos_reciept'].invoiceassigned=True
                elif self.reciept_name or 'reciept_name' in  values:
                    if self.reciept_name:
                        values['name']=self.reciept_name
                    else:
                        values['name']=values['reciept_name']
                        
     
            
                
        
        res=super(AccountMove, self).write(values)
        if self.pos_reciept:
            self.pos_reciept.invoiceassigned=True
        else:
            self.pos_reciept.invoiceassigned=False
        return res    
    
# class SaleOrderEreceipt(models.Model):
#     _inherit = 'sale.order'
        

    
    
    
    
#     @api.model
#     def create(self, values):
#         """
#             Create a new record for a model ModelName
#             @param values: provides a data for new record
    
#             @return: returns a id of new record
#         """
#         if 'eReceipt' in values and values['eReceipt'] not in ['',False,None]:
#             selectedreciept=self.env['sale.order'].search([('eReceipt','=',values['eReceipt'])])
#             if len(selectedreciept)>0:
#                 raise ValidationError("This Reciept Choosed Pefore")
#         result = super(SaleOrderEreceipt, self).create(values)
    
#         return result
    
    
#     def write(self, values):
#         """
#             Update all record(s) in recordset, with new value comes as {values}
#             return True on success, False otherwise
    
#             @param values: dict of new values to be set
    
#             @return: True on success, False otherwise
#         """
#         if 'eReceipt' in values and values['eReceipt'] not in ['',False,None]:
#             selectedreciept=self.env['sale.order'].search([('eReceipt','=',values['eReceipt'])])
#             if len(selectedreciept)>0:
#                 raise ValidationError("This Reciept Choosed Pefore")
        
#         result = super(SaleOrderEreceipt, self).write(values)
    
#         return result
    
#     def _get_related_model_domain(self):
#         # Fetch IDs of records that have been selected before
#         #selected_orders = self.env['pos.order'].search(['|','&',('sale_order', '=', []),('sale_order', '=', None), ('eta_status', 'in', ['valid', 'invalid'])])
#         selected_orders=self.env['sale.order'].search([('eReceipt','!=',False ),('eReceipt','!=',None ),('partner_id','=',self.partner_id.id)])
#         selected_ids = [order.eReceipt.id for order in selected_orders]
#         # Return domain to filter out these selected records
#         return [('id', 'not in', selected_ids), ('state', 'in', ['done']),('partner_id','=',self.partner_id.id)]

#     eReceipt = fields.Many2one(comodel_name="pos.order", string="E-Receipt", domain=lambda self: self._get_related_model_domain())
#     state=fields.Selection(
            
            
#             selection_add=[('fullpos', 'Fully Pos')]
            
#         )
    
#     def postReciept(self):
#         for rec in self:
#             rec.force_invoiced=True
#             rec.state='fullpos'
#     # def action_create_invoice(self):
#     #     for rec in self:
#     #         if not rec.partner_id.vat:
#     #             raise ValidationError("this customer not have tax number")
#     #         if rec.eReceipt and rec.force_invoiced and rec.status != 'fullpos':
#     #             rec.state='fullpos'
#     #             return True
#     #     return super(SaleOrderEreceipt,self).action_create_invoice()
    

    
    
# class AccountPayments(models.Model):
#     _inherit = 'account.payment'
    
#     def _get_related_model_domain(self):
#         for rec in self:
#             # Fetch IDs of records that have been selected before
#             #selected_orders = self.env['pos.order'].search(['|','&',('sale_order', '=', []),('sale_order', '=', None), ('state', 'in', ['done','paid'])])
#             selected_payments=self.env['account.payment'].search([('eReceipt','!=',False ),('eReceipt','!=',None ),('partner_id','=',rec.partner_id.id)])
#             selected_ids = [payment.eReceipt.id for payment in selected_payments]
#             # Return domain to filter out these selected records
#             # ('id', 'not in', selected_ids),('state', 'in', ['done','paid']),
#             #raise Warning(str([('id', 'not in', selected_ids),('state', 'in', ['done','paid']),('partner_id','=',rec.partner_id.id)]))
#             return [('id', 'not in', selected_ids),('partner_id','=',rec.partner_id.id)]


    
#     eReceipt=fields.Many2one(comodel_name="pos.order",string="E-Reciept", domain=lambda self: self._get_related_model_domain())
#     eReceiptpayment=fields.Selection(string="E-Reciept Payment Status",selection=[('paid','Paid')])
#     eReceiptPaid=fields.Boolean("E-Reciept Paid")
#     #eRecieptPaymentStatus=fields.Selection(string="Payment Status",selection=[('paid','Paid')])
#     eRecieptPaid=fields.Boolean(string="Payment Paid")
#     #@api.model
#     def setAsPaid(self):
        
#         for rec in self:
#             rec.amount=0
#             rec.move_id.payment_id=rec.id
#             rec.payment_state='paid'
#             rec.move_id.payment_state='paid'
#             rec.is_reconciled=True
#             rec.eRecieptPaid=True
#             rec.eReceipt.eRecieptPaid=True
#         pass
#     def action_draft(self):
#         for rec in self:
#             rec.amount=rec.eReceipt.amount_total
#             rec.move_id.payment_id=False
#             rec.payment_state='not_paid'
#             rec.move_id.payment_state='not_paid'
#             rec.is_reconciled=False
#             rec.eRecieptPaid=False
#             rec.eReceipt.eRecieptPaid=False
#         result = super(AccountPayments, self).action_draft()
    
#         return result    
#     @api.model
#     def create(self, values):
#         """
#             Create a new record for a model ModelName
#             @param values: provides a data for new record
    
#             @return: returns a id of new record
#         """
#         if 'eReceipt' in values and values['eReceipt'] not in ['',False,None]:
#             selectedreciept=self.env['account.payment'].search([('eReceipt','=',values['eReceipt'])])
#             if len(selectedreciept)>0:
#                 raise ValidationError("This Reciept Choosed Pefore")
#         result = super(AccountPayments, self).create(values)
    
#         return result
    
    
#     def write(self, values):
#         """
#             Update all record(s) in recordset, with new value comes as {values}
#             return True on success, False otherwise
    
#             @param values: dict of new values to be set
    
#             @return: True on success, False otherwise
#         """
#         if 'eReceipt' in values and values['eReceipt'] not in ['',False,None]:
#             selectedreciept=self.env['sale.order'].search([('eReceipt','=',values['eReceipt'])])
#             if len(selectedreciept)>0:
#                 raise ValidationError("This Reciept Choosed Pefore")
        
#         result = super(AccountPayments, self).write(values)
    
#         return result
    
    
    
    
class Ereciept(models.Model):
    _inherit = 'pos.order'
    eRecieptPaid=fields.Boolean(string="Reciept Paid")
    # @api.depends('erecieptpayments')
    # def get_paymentassigned(self):
    #     for rec in self:
    #         payments=self.env['account.payment'].search([('eReceipt','=',rec.id)])
    #         if len(payments.ids)>0:
    #             rec.paymentassigned= True
    #         else:
    #             rec.paymentassigned= False
    #     pass
    # paymentassigned=fields.Boolean(string="Payment Assigned",compute='get_paymentassigned',store=True)
    invoiceassigned=fields.Boolean("Assigned To invoice")
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s - %s' % (rec.name,rec.amount_total)))
        return result
    # sale_order=fields.One2many(
    #                 string='Sale Order',
    #                 comodel_name='sale.order',
    #                 inverse_name='eReceipt',
    #             )
    # erecieptpayments=fields.One2many(
    #                 string='Payments',
    #                 comodel_name='account.payment',
    #                 inverse_name='eReceipt',
    #             )
    
    
    
    

    
    

    
