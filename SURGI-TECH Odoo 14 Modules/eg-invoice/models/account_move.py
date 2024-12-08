from ast import Store
from email.policy import default
from odoo import fields, models, api
#from EnvoConfig import Connection
from . import EnvoConfig
from odoo.exceptions import UserError,Warning
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError

import requests,json
import time
import logging
_logger = logging.getLogger(__name__)

class account_move_line_inhert_e_invoice(models.Model):
    _inherit="account.move.line"
    disc_amount=fields.Float("Ammount of disc",compute="_compute_einvoice_disc")
    #einvoice_id = fields.Many2one('einvoice.lines', string='einvoice')
    @api.model
    def _compute_einvoice_disc(self):
        for rec in self:
            rec.disc_amount = (rec.discount * (rec.price_unit*rec.quantity)) / 100


    taxamount=fields.Float("Amount Tax",store=False,compute="_compute_taxable_ammount")
    def _compute_taxable_ammount(self):
        for rec in self:
            if rec.tax_ids.amount_type == "percent":
                rec.taxamount = (rec.tax_ids.amount * (rec.price_unit*rec.quantity)) / 100
            else:
                rec.taxamount = rec.tax_ids.amount

class account_move_einvoice(models.Model):

    _inherit = 'account.move'
    _description = 'Description'
    sendSign=fields.Boolean("Send To Sign",default=False)
    signedBy=fields.Many2one(comodel_name="res.users",string="Signed By")

    einvoice_itemstype=fields.Selection(string="Send E-Invoice in",selection=[('items','Items'),('pack','Pack')],default="pack")
    overalldiscount=fields.Float("Overall Discount For E-invoice")
    
    def get_printed_version(self):
        egytax_printout=EnvoConfig.EnvoConfig().getPrintedVersion(self.egtax_uuid, self.company_id)
        #return

    def update_move_status(self):
        #con=EnvoConfig.Connection(self.company_id)
        if not self.egtax_uuid:
           raise UserError('You Didt send invoice yet')
        env=EnvoConfig.EnvoConfig().getDocumentStatus(self.egtax_uuid,self.company_id)
        #raise UserError(str(env))

        res=env['res']
        err=""
        #res=json.loads(response.text)
        if res['validationResults'] and res['validationResults']['status'] and res['validationResults']['status']=="Invalid":
            for v in res['validationResults']['validationSteps']:
                if v['status']=='Invalid':
                    #
                    #err+=v['error']['errorAr']+str(" \n")
                    if v['error']:
                        for invoicerr in v['error']['innerError']:
                            err=err+invoicerr['errorAr']+"\n"

        else:
            err=""            
        self.eg_tax_error=err
        self.egtax_status=env['status']
        self.egtax_link=env['url']
        self.egytax_printout=env['url']+"/pdf"
        pass
    def _getinvoiceType(self):
        return [('i',"Invoice"),('c','Credit Note'),('d','Depit Note')]
        pass
    documenttype=fields.Selection(string="Invoice Type",selection=_getinvoiceType)

    documentversion=fields.Float(string="Document Version",default="0.9")
    submissionId=fields.Char("Submission ID")
    egtax_uuid=fields.Char("uuid")
    eg_tax_error=fields.Text("Errors")
    eg_tax_cancelreason=fields.Text("Cancel Reason")
    egytax_printout=fields.Char("PrintOut",attachment =True)
    egtax_longid=fields.Char("longId")
    egtax_status=fields.Char("Invoice Status")
    egtax_link=fields.Char("Preview Online")
    hashkey = fields.Char("Hash Key")
    eg_tax_status=fields.Selection("E-invoice State",[("Generated","Generated"),("Sent","Sent"),("Accepted","Accepted"),("Rejected","Rejected"),("Submitted","Submitted")])


    errordocuments=fields.Char("Errors")
    branch=fields.Selection(string="branch",selection=[('0',"19 شارع عامر الدور الارضى الدقى الجيزه"),('1',"ش سعد زغلول منشأه اباظه الزند الزقازيق شرقيه"),('2',"51ش فيكتور عمانويل امام زهران مول الاسكندريه"),('3',"18ش عامر ميدان المساحه الدقي")])
    eg_tax_lines=fields.One2many("einvoice.lines","account_move_id",string="Invoice Lines")
    eg_tax_totalSalesAmount=fields.Float("Total Sales Amount")
    #eg_tax_totalSalesAmount=fields.Float("Total Sales Amount",store=False,compute="compute_eg_tax_totalSalesAmount")
    eg_tax_cancelation_reason=fields.Text("Cancel Reason")
    def compute_eg_tax_totalSalesAmount(self):
        total=0.0
        for rec in self:
            for line in rec.eg_tax_lines:
                total+=line.salestotal
            return  round(total,5)   
            rec.eg_tax_totalSalesAmount=round(total,5)
    eg_tax_totalDiscountAmount=fields.Float("Total Discount Amount")
    #eg_tax_totalDiscountAmount=fields.Float("Total Discount Amount",store=False,compute="compute_eg_tax_totalDiscountAmount")
    def compute_eg_tax_totalDiscountAmount(self):
        total = 0.0

        for rec in self:
            for line in rec.eg_tax_lines:
                total += line.discount_amount
            return round(0,5)
            rec.eg_tax_totalDiscountAmount = round(0,5)
    #eg_tax_netamount=fields.Float("Net Amount",store=False,compute="compute_eg_tax_netamount")
    eg_tax_netamount=fields.Float("Net Amount")
    def compute_eg_tax_netamount(self):
        netamount=0
        for rec in self:
            netamount= rec.compute_eg_tax_totalSalesAmount()
            return netamount    
            #rec.eg_tax_netamount = rec.eg_tax_totalSalesAmount#-rec.eg_tax_totalDiscountAmount
    eg_tax_extradiscountammount=fields.Float("extra Discount Amount",default=0.0)#on the whole invoice
    #eg_tax_totalItemsDiscountAmount=fields.Float("Total Items Discount",store=False,compute="compute_total_discount")
    eg_tax_totalItemsDiscountAmount=fields.Float("Total Items Discount")
    def compute_total_discount(self):
        total = 0.0
        for rec in self:
            for line in rec.eg_tax_lines:
                if line.discount_amount:
                    total += line.discount_amount
            return  round(total,2)       
            rec.eg_tax_totalItemsDiscountAmount = round(total,2)
    #eg_tax_taxtotal=fields.Text("Value Added Tax Total",store=False,compute="compute_tax_total")
    eg_tax_taxtotal=fields.Text("Value Added Tax Total")
    def compute_tax_total(self):
        rate=1
        total = 0.0
        for rec in self:
            currencyexchange=rec.currency_id.rate_ids.search([ ('currencydate','=',rec.invoice_date)],limit=1,order="currencydate desc")
            if not currencyexchange and rec.currency_id.name != "EGP":
                raise Warning("there is no exchange rate for this currency after the invoice date")
            if  currencyexchange:
                rate=currencyexchange.currencyvalue
            taxes=[]
            for line in rec.eg_tax_lines:
                for tax in line.tax_ids:
                    taxes.append({"taxType":tax.eg_tax_type.code,"amount":(round(((tax.amount/100)*(line.salestotal))*rate,5))})
            
            result={}
            for k in taxes:
                if k['taxType'] in result.keys():               
                    result[k['taxType']]+=k['amount']
                else:
                    result[k['taxType']]=k['amount']

            taxtoal="["
            for k in result:
                taxtoal+='{"taxType":"'+str(k)+'","amount":'+str(result[k])+'}'
            taxtoal+="]"
        return taxtoal
        rec.eg_tax_taxtotal = taxtoal
    #eg_tax_totalAmount=fields.Float("Total Amount",store=False,compute="compute_total_amount")
    eg_tax_totalAmount=fields.Float("Total Amount")
    def compute_total_amount(self,netamount,totalItemsDiscountAmount):
        taxtotals=0.0
        for rec in self:
            for line in rec.eg_tax_lines:
                for tax in line.tax_ids:
                    taxtotals+=(round(((tax.amount/100)*(line.salestotal)),5))
            s=rec.eg_tax_netamount+taxtotals
        return round(round(netamount+taxtotals,5)-totalItemsDiscountAmount,5)#remove discount after tax    
            #rec.eg_tax_totalAmount=round(rec.eg_tax_netamount+taxtotals,5)-rec.eg_tax_totalItemsDiscountAmount#remove discount after tax
    eg_tax_status=fields.Char("Status")

    def copy(self,default=None):
        self.egtax_link=""
        self.egtax_status=""
        self.egtax_uuid=""
        self.eg_tax_error=""
        #self.eg_tax_lines=None
        res=super(account_move_einvoice,self).copy( default=None)
        return res
        pass
    def action_send_einvoice(self):
        #g=new Global()
        if len(self.company_id.ids)>1:
            raise UserError("Please Choose one Company")
        

        self.action_Generate_einvoice_line()
        c=EnvoConfig.EnvoConfig()
        c.DocumentSubmissions(self)
    def updatesignedmove(self,move):
        time.sleep(3)
        move.update_move_status()
    @api.model    
    def updateSignStatus(self,val=None,uuid=None,longId=None,internalId=None,hashKey=None,sendSign=None,status=None,*arg,**kw):
        #val = json.loads(submition)
        
        move=self.env['account.move'].search([("name", "=", val['internalId'])])
        if move.egtax_status=="Valid":
            return  json.dumps({"res":True})
            
        #raise UserError(str( val))
        move.write({'egtax_uuid':val['uuid'],'egtax_longid':val['longId'],'hashkey':val['hashKey'],'submissionId':val['submissionId'],'sendSign':val['sendSign'],'egtax_status':val['status']})
        time.sleep(3)
        #self.updatesignedmove(move)
        #move.update_move_status()
        #return json.dumps({"done":"done"})
        return  json.dumps({"res":True})
        pass
        
    def getDocumentToSign(self):
        for rec in self:
            needsign=self.env['account.move'].search([("sendSign", "=", True),("egtax_status","!=","Valid")])
            if needsign:
                c=EnvoConfig.EnvoConfig()
                strdoc='{ "error":""'
                strdoc+=',"doccount":"'+str(len(needsign))+'"'
                strdoc+=',"docs":['
                for doc in needsign:                
                        #try:
                    strdoc+='{"name":"'+str(doc.name)+'","doc":'+c.CreateInvoicenotsigned(doc)+'}'
                        #except:
                        #    raise Warning(str(doc.name))
                    if doc != needsign[-1]:
                        strdoc+=","
                strdoc+="]"
                strdoc+="}"
                _logger.info("===================================")
                #_logger.info(strdoc)
                _logger.info("===================================")
                return strdoc
            else:
                return "{'error':'No Invoice To Sign'}"    
    def prepare_egtax_einvoice(self):
        for rec in self:
            print("f")
            totalSalesAmount=rec.compute_eg_tax_totalSalesAmount()
            totalDiscountAmount=rec.compute_eg_tax_totalDiscountAmount()
            netamount=rec.compute_eg_tax_netamount()
            totalItemsDiscountAmount=rec.compute_total_discount()
            taxtotal=rec.compute_tax_total()
            totalAmount=rec.compute_total_amount(netamount,totalItemsDiscountAmount)
            #raise UserError(str(netamount))
            totals={ 'eg_tax_totalSalesAmount':totalSalesAmount,   
                 'eg_tax_totalDiscountAmount':totalDiscountAmount,                
                'eg_tax_netamount':netamount,
                'eg_tax_totalItemsDiscountAmount':totalItemsDiscountAmount,
                'eg_tax_taxtotal':taxtotal,
                'eg_tax_totalAmount':totalAmount

            }
            #raise UserError(str(totals))
            rec.sudo().write(totals)

        print("fff")
#     def updatenames(self):
#         products=self.env['product.template'].search([("eg_tax_namex","!=","")])
#         for product in products:
#             product.eg_tax_desc=product.eg_tax_namex    
    def action_send_tosign(self):
        if len(self.company_id.ids)>1:
            raise UserError("Please Choose one Company")
        
        for rec in self:
            
            rec.action_Generate_einvoice_line()
            rec.prepare_egtax_einvoice()
            c=EnvoConfig.EnvoConfig()
            c.CreateInvoicenotsigned(rec)
            rec.sendSign=True
    def action_cancel_send_tosign(self):
        if len(self.company_id.ids)>1:
            raise UserError("Please Choose one Company")
        for rec in self:
            rec.action_Generate_einvoice_line()
            rec.sendSign=False        

    def action_Generate_einvoice_line(self):
        
        for rec in self:
            rec.eg_tax_lines.write({'account_move_line_id':False,'print_invoice_line':False})
            #rec.eg_tax_lines.print_invoice_line=False
            rec.eg_tax_lines.unlink()
            if rec.einvoice_itemstype=="items":
                lines=rec.invoice_line_ids
                for line in lines:
                    if  line.product_id:
                        product_template=line.product_id.product_tmpl_id
                        if product_template.eg_tax_barcode_type=="" or product_template.eg_tax_barcode=="" or product_template.eg_tax_desc=="":
                           raise UserError('Please Check barcode type and barcode and product description')
                        newline={
                            "account_move_id":rec.id,
                            "account_move_line_id": line.id,
                            "print_invoice_line":False,
                            "product_id":line.product_id.id,
                            'quantitiy':line.quantity,
                            'description':line.description,
                            }
                        self.eg_tax_lines.create(newline)    
            
            else:
                lines=rec.printinvoicetoline
                for line in lines:
                    if  line.product_id:
                        product_template=line.product_id.product_tmpl_id
                        if product_template.eg_tax_barcode_type=="" or product_template.eg_tax_barcode=="" or product_template.eg_tax_desc=="":
                           raise UserError('Please Check barcode type and barcode and product description')
                        newline={
                            "account_move_id":rec.id,
                            "account_move_line_id":False,
                            "print_invoice_line":line.id,
                            "product_id":line.product_id.id,
                            'quantitiy':line.uquantity ,
                            'description':line.description,
                            # 'salestotal': round(line.uprice*line.uquantity,5) ,
                            # 'nettotal': round(line.uprice*line.uquantity,5) ,                  

                                }

                        self.eg_tax_lines.create(newline)
                    #self.env["einvoice.lines"].create(newline)


        pass
    def action_Cancel_Invoice(self):
        for rec in self:
            if not rec.eg_tax_cancelreason:
                raise UserError('Please Add Cancel Reason At E-invoice Tab')
            c=EnvoConfig.EnvoConfig()
            
            if c.CancelDocument(rec.egtax_uuid,rec.eg_tax_cancelreason,rec.company_id):
                self.update_move_status()
                raise UserError('Invoice Canceled')
        # c = EnvoConfig.EnvoConfig()
        # res=c.getDocumentDetail(self.company_id,self.egtax_uuid)

        # return {'type': 'ir.actions.act_window',
        #        'name': 'Are You Sure You Want To Cancel Document',
        #        'res_model': 'account.move',
        #        'target': 'new',
        #        'view_id': self.env.ref('eg-invoice.view_account_move_cancel_einvoice1_wizard').id,
        #        'view_mode': 'form',
        #         'res_id':self.id,
        #        'context': {'documentid': self.submissionId}
        #        }
    def action_Invoice_Cancel_Done(self,context=None):

        c=EnvoConfig.EnvoConfig()
        if c.CancelDocument(self.egtax_uuid,self.eg_tax_cancelation_reason,self.company_id):
            self.update_move_status()
        
        pass



class eg_Taxs(models.Model):
    _name="eg.tax"
    code=fields.Char("Tax Code")
    desc_en=fields.Char("Tax Name")
    name=fields.Char("Tax Name")
    nontaxble=fields.Boolean("Non Taxable Type")
    subtax=fields.One2many(comodel_name="eg.subtax",inverse_name ="tax")

    @api.depends('code')
    def _get_subtax(self):
        self.subtax=self.env['eg.subtax'].search([('taxrefrecnce','=',self.code)])
        print("c")

    pass
class Eg_SubTaxes(models.Model):
    _name="eg.subtax"
    code=fields.Char("Tax Code")
    desc_en=fields.Char("Tax Name")
    name=fields.Char("Tax Name")
    taxrefrecnce=fields.Char("Tax Refrence")
    tax=fields.Many2one(comodel_name="eg.tax")



    pass
class product_template_inhert_einvoice(models.Model):

    _inherit = 'product.template'
    eg_tax_name=fields.Char("Product Tax Name")
    eg_tax_namex = fields.Char("Product Tax Name")
    eg_tax_desc=fields.Text("Product Tax Description")
    eg_tax_barcode_type=fields.Selection(string="Barcode Type",selection=[("EGS","EGS"),("GS1","GS1")])
    eg_tax_barcode=fields.Char("Barcode")
    eg_tax_unittype=fields.Selection(string="Unit Of Measure",selection =EnvoConfig.Segnelton.getMeasureUnit(),default="C62")
    eg_tax_currency=fields.Char(string="currency Sold",default="EGP")
    def checknontaxable(self):
        for rec in self:
            if rec.eg_tax_type.nontaxble:
                rec.nonetaxabletype=True
            else:
                rec.nonetaxabletype = False


    @api.onchange('eg_tax_type')
    def getsubtax(self):
        for rec in self:
            if rec.eg_tax_type:
                return {'domain': {'eg_tax_subtype': [('taxrefrecnce', '=', rec.eg_tax_type.code)]}}
            else:
                return {'domain': {'eg_tax_subtype': [('taxrefrecnce', '=', "")]}}
    eg_tax_type=fields.Many2one(comodel_name ="eg.tax",string="Tax Type")
    nonetaxabletype=fields.Boolean(store=False,string="Non Taxable type",compute="checknontaxable")
    eg_tax_subtype = fields.Many2one(comodel_name="eg.subtax")
    pass

class Surgi_Einvoice_account_tax(models.Model):
    _inherit="account.tax"
    def checknontaxable(self):
        for rec in self:
            if rec.eg_tax_type.nontaxble:
                rec.nonetaxabletype=True
            else:
                rec.nonetaxabletype = False


    @api.onchange('eg_tax_type')
    def getsubtax(self):
        for rec in self:
            if rec.eg_tax_type:
                return {'domain': {'eg_tax_subtype': [('taxrefrecnce', '=', rec.eg_tax_type.code)]}}
            else:
                return {'domain': {'eg_tax_subtype': [('taxrefrecnce', '=', "")]}}
    eg_tax_type=fields.Many2one(comodel_name ="eg.tax",string="Tax Type")
    nonetaxabletype=fields.Boolean(related="eg_tax_type.nontaxble" ,store=False,string="Non Taxable type",compute="checknontaxable")
    eg_tax_subtype = fields.Many2one(comodel_name="eg.subtax")
class print_invoice_line_rel(models.Model):
    _inherit="account.move.printedinvoice.lines"
    #einvoice=fields.Many2one(comodel_name="einvoice.lines",string="E-Invoice line ID")









class Surgi_Einvoice_lines(models.Model):
    _name="einvoice.lines"
    account_move_id=fields.Many2one(comodel_name="account.move")
    account_move_line_id=fields.Many2one(string="account move line",comodel_name="account.move.line",default=False,ondelete="cascade")
    #account_move_line_id=fields.One2many(string="account move line",inverse_name="einvoice_id",comodel_name="account.move.line",default=False,store=False,computed='_get_einvoicetype')
    print_invoice_line=fields.Many2one(string="print invoice line",comodel_name="account.move.printedinvoice.lines",default=False,ondelete="cascade")
    #print_invoice_line=fields.One2many(string="print invoice line",inverse_name="einvoice",comodel_name="account.move.printedinvoice.lines",default=False,store=False,computed='_get_einvoicetype')
    product_id=fields.Many2one(comodel_name="product.product")
    @api.depends("account_move_id.einvoice_itemstype")
    def _get_einvoicetype(self):
        for rec in self:
            if rec.account_move_id.einvoice_itemstype=='items':
                rec.account_move_line_id=rec.account_move_id.invoice_line_ids
                rec.print_invoice_line=False
            else:
                rec.account_move_line_id=False
                rec.print_invoice_line=rec.account_move_id.printinvoicetoline
    # @api.depends('account_move_id.einvoice_itemstype','account_move_id.invoice_line_ids','account_move_id.printinvoicetoline')
    # def _getProduct(self):
    #     for rec in self:
    #         if rec.account_move_id.einvoice_itemstype=="items":
    #             rec.product_id=rec.account_move_id.invoice_line_ids.product_id
    #         else:
    #             rec.product_id=rec.account_move_id.printinvoicetoline.product_id
    #description=fields.Text("Product Desc.",related='product_id.product_tmpl_id.eg_tax_desc',store=True)
    description=fields.Text("Product Desc.")
    itemType=fields.Selection("Barcode Type",related='product_id.product_tmpl_id.eg_tax_barcode_type',store=True)
    itemCode=fields.Char("Barcode",related='product_id.product_tmpl_id.eg_tax_barcode',store=True)
    unittype=fields.Selection("Unit",related='product_id.product_tmpl_id.eg_tax_unittype',store=True)
    #unit valuedata
    currencysold=fields.Char("Currency",default="EGP")
    
  
      
    quantitiy=fields.Float("Quantitiy")

    @api.depends('quantitiy','account_move_line_id','print_invoice_line','discount_amount')
    def _computeUnitPrice(self):
        for rec in self:
            if rec.account_move_line_id:
                priceField=rec.account_move_line_id.price_unit
                taxField=rec.account_move_line_id.tax_ids
                q=rec.account_move_line_id.quantity
            else:
                priceField=rec.print_invoice_line.uprice
                taxField=rec.print_invoice_line.tax_ids
                q=rec.print_invoice_line.uquantity
            taxamount=0
            for tax in taxField:
                if tax.price_include:
                    taxamount+=(tax.amount/100)
            #raise UserError(str(rec.product_id.name)+" -> "+str(quantitiy))        
            
            itemdiscount=0
            if q>0:
                itemdiscount=self.get_line_discount(rec)/q
                
            unitprice=(priceField)-itemdiscount
            taxedamount=round((unitprice*taxamount),5)
            untaxedamount=round((unitprice - ((unitprice / (1 + taxamount)) * taxamount)),5) 
            rec.unitamountEGP=untaxedamount#-rec.itemsDiscount
            
            #rec.unitamountEGP=round((unitprice - ((unitprice / (1 + taxamount)) * taxamount)),4) 
            #rec.unitamountEGP=round(priceField,4) 
            #rec.unitamountEGP=round((unitprice -taxedamount),4) 
            x=1    
                    

    unitamountEGP=fields.Float("Unit Price",compute="_computeUnitPrice",store=True)
    #end there is fields for changinging currency
    
    
    
    

    internalcode=fields.Char("internal BarCode")
    
    valuedeffrence=fields.Float("value Difference")
    totaltaxablefees=fields.Float("Total Taxable Fees")
    def get_line_discount(self , rec):
        #for rec in self:
            if rec.account_move_line_id:
                return round(((rec.quantitiy*rec.total)*rec.discount_rate)/100,5)
                
            else:
                return rec.print_invoice_line.discount_amount
    def _compute_line_discount(self):
        for rec in self:
            if rec.account_move_line_id:
                rec.itemsDiscount=round(((rec.quantitiy*rec.total)*rec.discount_rate)/100,5)
                rec.discount_amount=rec.print_invoice_line.discount_amount
            else:
                rec.itemsDiscount=rec.print_invoice_line.discount_amount
                rec.discount_amount=rec.print_invoice_line.discount_amount
            rec.itemsDiscount=0
            rec.discount_amount=0            
    itemsDiscount=fields.Float("Items Discount",default="0.0",computed="_compute_line_discount",store=True)
    discount_amount=fields.Float("Discount_amount",default="0.0",compute="_compute_line_discount")
    @api.depends('quantitiy','unitamountEGP','discount_amount')
    def _computeDiscountRate(self):
        for rec in self:
            if rec.account_move_line_id:
                rec.discount_rate=rec.account_move_line_id.discount
            else:
                if rec.print_invoice_line.discount_amount:
                    q=rec.quantitiy
                    uam=rec.unitamountEGP
                    rec.discount_rate=round((rec.discount_amount/(q*uam))*100,5)
                    x=rec.discount_rate
                else:
                    rec.discount_rate=0
    discount_rate=fields.Float("Discount Rate",default="0.0",compute='_computeDiscountRate',store=True)
    

    
                

    #@api.depends('account_move_line_id','print_invoice_line')
    
    
    def _compute_number_of_item_discounted(self):
        for rec in self:
            if rec.itemsDiscount==0:
                rec.nodiscountitems=0
            else:
                rec.nodiscountitems=rec.quantitiy
    nodiscountitems=fields.Float(compute="_compute_number_of_item_discounted",store=True)


    @api.depends('unitamountEGP')
    def _compute_totaltaxperline(self):
        for rec in self:
            if rec.account_move_line_id:
                taxes = rec.account_move_line_id.tax_ids
            else:
                taxes = rec.print_invoice_line.tax_ids
            totaltax = 0.0
            for tax in taxes:
                totaltax += (((rec.unitamountEGP*rec.quantitiy )* tax.amount) / 100)
            #s = (rec.salestotal + rec.totaltaxablefees + totaltax) - rec.discount_amount
            rec.totaltaxperline =round(totaltax,5)

    totaltaxperline = fields.Float("Total Tax Per Line",store=True, compute="_compute_totaltaxperline")
    
    
    
    
    # taxtype=fields.Char("Tax  Type")
    # taxsubtype=fields.Char("Tax Sub Type")
    # taxableitem=fields.Boolean("Is Taxable")

    # @api.model
    # def _compute_totaltaxablefee(self):
    #     if self.product_id:
    #         self.totaltaxablefees="5"
    #         if self.account_move_line_id.product_id.product_tmpl_id.tax_ids.amount_type=="percent":
    #             self.totaltaxablefees= (self.account_move_line_id.product_id.product_tmpl_id.tax_ids.amount*self.nettotal)/100
    #         else:
    #             self.totaltaxablefees= self.account_move_line_id.product_id.product_tmpl_id.tax_ids.amount

    #@api.model
    @api.depends('quantitiy','discount_amount','salestotal')
    def _compute_net_total(self):
        for rec in self:
            # if rec.discount_amount:
            #     rec.nettotal=round(rec.salestotal-rec.discount_amount,4)
            # else:
            rec.nettotal=round(rec.salestotal,5)
    nettotal=fields.Float("Net Total",default=0.0,compute="_compute_net_total",store=True)



    @api.depends('quantitiy','nettotal','totaltaxperline')
    def _compute_total(self):
        for rec in self:
            taxes = rec.account_move_line_id.tax_ids
            totaltax=0.0
            for tax in taxes:                
                totaltax+=((rec.salestotal * tax.amount) / 100)
            s=(rec.salestotal + rec.totaltaxablefees + totaltax)# - rec.itemsDiscount
            #rec.total=rec.nettotal+totaltax
            #rec.total=(rec.salestotal+rec.totaltaxablefees+totaltax)-rec.itemsDiscount
            z=round(rec.nettotal+rec.totaltaxperline,5)
            rec.total=round(rec.nettotal+rec.totaltaxperline,5)#-rec.discount_amount
    total=fields.Float("Total",compute="_compute_total",default=0.0,store=True)




    @api.depends('quantitiy','unitamountEGP')
    def _compute_sale_total(self):
        for rec in self:
            rec.salestotal=round(rec.unitamountEGP*rec.quantitiy,5)
    salestotal=fields.Float("Sale Total",default=0.0,compute='_compute_sale_total',store=True)    



    
    @api.depends('account_move_line_id','print_invoice_line')
    def _gettaxes(self):
        for rec in self:
            if rec.account_move_line_id:
                rec.tax_ids=rec.account_move_line_id.tax_ids
            else:
                rec.tax_ids=rec.print_invoice_line.tax_ids    
    tax_ids=fields.Many2many(comodel_name="account.tax",string="Taxes",compute="_gettaxes",store=True)
