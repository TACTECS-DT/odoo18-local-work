from copy import copy

from odoo import models
from odoo import fields
from odoo import api
from odoo.exceptions import UserError
import logging
import math

_logger = logging.getLogger(__name__)


# class PrintInvoice(models.Model):
# _name="account.move.printedinvoice"
##  _inherit=["account.move"]
##  letteralQuantity=fields.Char("Total Quantity")
#     printinvoicetoline=fields.One2many('account.move.printedinvoice.lines','linestoprintinvoice')
#   pass
# class PrintInvoice1(models.Model):
#     _name = "account.move.printedinvoice.lines"
#     sequance=fields.Integer("Sequance")
#     description=fields.Char("description")
#     uquantity=fields.Float("Quantity")
#     uprice=fields.Float("Price")
#     total=fields.Float("Total",compute='_computeTotal')
# #     linestoprintinvoice=fields.Many2one("account.move")
# #
#     @api.depends('uquantity','uprice')
#     def _computeTotal(self):
#         self.total=self.uquantity*self.uprice
#         pass
#     pass
class Tafneta():
    def __init__(self):
        self.ones = {
            '0': '', '1': 'وَاحِد', '2': 'اِثْنَان', '3': 'ثَلَاثَة', '4': 'أَرْبَعَة', '5': 'خَمْسَة', '6': 'سِتَّة',
            '7': 'سَبْعَة', '8': 'ثَمَانِيَة', '9': 'تِسْعَة', '10': 'عَشَرَة', '11': 'أَحَدَ عَشَرَ',
            '12': 'اِثْنَا عَشَرَ',
            '13': 'ثَلَاثَةَ عَشَرَ', '14': 'أَرْبَعَةَ عَشَرَ', '15': 'خَمْسَةَ عَشَرَ', '16': 'سِتَّةَ عَشَرَ',
            '17': 'سَبْعَةَ عَشَرَ', '18': 'ثَمَانِيَةَ عَشَرَ', '19': 'تِسْعَةَ عَشَرَ'}
        self.tens = {
            '1': 'عَشَرَ', '2': 'عِشْرُونَ', '3': 'ثَلَاثُونَ', '4': 'أَرْبَعُونَ', '5': 'خَمْسُونَ', '6': 'سِتُّونَ',
            '7': 'سَبْعُونَ', '8': 'ثَمَانُونَ', '9': 'تِسْعُونَ'}
        self.hunders = {
            '1': 'مِئَة', '2': 'مِا۟ئَتَان', '3': 'ثَلَاثُمِئَة', '4': 'أَرْبَعُمِئَة', '5': 'خمسمائة',
            '6': 'سِتُّمِئَة',
            '7': 'سَبْعُمِئَة', '8': 'ثَمَانِيُمِئَة', '9': 'تِسْعُمِئَة'
        }
        self.thousands = {'1': 'أَلف', '2': 'أَلفين', '3': 'ثَلَاثَة أَلاف', '4': 'أَرْبَعَة أَلاف',
                          '5': 'خَمْسَة أَلاف',
                          '6': 'سِتَّة أَلاف', '7': 'سَبْعَة أَلاف', '8': 'ثَمَانِيَة أَلاف', '9': 'تِسْعَة أَلاف'}
        self.illions = {
            1: 'مليون', 2: 'ملايين', 3: 'billion', 4: 'trillion', 5: 'quadrillion',
            6: 'quintillion', 7: 'sextillion', 8: 'septillion', 9: 'octillion',
            10: 'nonillion', 11: 'decillion'}
        pass

    def ahad(self, i):
        if len(i) == 2 and i[0] == '0':
            return self.ones[i[1]]

        return self.ones[i]

        pass

    def ashrat(self, i):
        if int(i) == 0:
            return ''
        if i[1] == '0':
            return self.tens[i[0]]
        elif i[0] == '0':
            return self.ahad(i[1])
        else:
            if (int(i) < 20):
                return self.ahad(i)
            else:
                return self.ones[i[1]] + " و " + self.tens[i[0]]
            pass

        pass

    def meat(self, i):
        if int(i) == 0:
            return ''
        if i[1:] == '00':
            return self.hunders[i[0]]
        if i[0:2] == "00":
            return self.ahad(i[2])
        if i[0] == '0':
            return self.ashrat(i[1:])
        else:

            return self.hunders[i[0]] + " و " + self.ashrat(i[1:])
            pass
        pass

    def oloaf(self, i):
        if int(i) == 0:
            return ''
        if i[1:] == '000':
            return self.thousands[i[0]]
        if i[1:2] == '00':
            return self.thousands[i[0]] + " و " + self.ahad(i[1:])
        if i[1] == '0':
            return self.thousands[i[0]] + " و " + self.ashrat(i[2:])
        if i[0:3] == '000':
            return self.ahad(i[3])
        if i[0:2] == '00':
            return self.ashrat(i[2:])
        if i[0] == '0':
            return self.meat(i[1:])

        else:
            return self.thousands[i[0]] + " و " + self.meat(i[1:])
        pass

    def meatoloaf(self, i):
        if int(i) == 0:
            return ''
        if len(i) == 5:  # 10001
            print(i[0:2])
            if int(i[2:]) == 0:
                return self.ashrat(i[0:2]) + " أَلف  "
            else:
                return self.ashrat(i[0:2]) + " أَلاف و " + self.meat(i[2:5])
        if len(i) == 6:  # 100000
            if int(i[3:]) == 0:
                print("----->")
                return self.meat(i[0:3]) + " أَلف  "
            else:
                print("#################")
                return self.meat(i[0:3]) + " أَلف و " + self.meat(i[3:6])
        pass

    def num2words(self, i):
        # 5 50 51 05 500 501 510 010 5000 5100 5010 5001 50000 50001 50010 50100 51000 51111 500000 500001 500011 500111 501111 511111

        if int(i) < 20:
            return self.ahad(str(i))
        elif int(i) < 100 and int(i) > 19:
            return self.ashrat(str(i))
        elif int(i) < 1000 and int(i) > 99:
            return self.meat(str(i))
        elif int(i) > 999 and int(i) < 10000:
            return self.oloaf(i)
        elif int(i) > 9999 and int(i) < 1000000:
            return self.meatoloaf(i)
        else:
            return "out of range"

        pass
        # end class

    pass


class PrintInvoice(models.Model):
    # _name="acount.move.printinvoice"
    _inherit = "account.move"
    nassar_state = fields.Char(string="nassar status")
    letteraltotal = fields.Text(string="Total Quantity in Letters", compute='_total2word')
    printinvoicetoline = fields.One2many('account.move.printedinvoice.lines', 'linestoprintinvoice',copy=True)

    # def write(self, vals):
    #     moves=super().write(vals)
    #     #self.write(vals)
    #     saleorder=self.env['sale.order'].search([('invoice_count','>',0)])
    #
    #     for s in saleorder:
    #         if self.id in s.invoice_ids.ids:
    #             sale_id=s.id
    #             break
    #
    #
    #
    #     for invo in self.printinvoicetoline:
    #
    #         invo.write({'linestoprintquation':sale_id,'linestoprintinvoice':self.id})
    #     if vals  and 'printinvoicetoline' in vals:
    #         for invo in vals['printinvoicetoline']:
    #             if invo[2]:
    #                 print("cccccccccccccc")
    #                 # data={'sequance': invo[2]['sequance'],
    #                 #       'description': invo[2]['description'],
    #                 #       'uquantity': invo[2]['uquantity'],
    #                 #       'uprice': invo[2]['uprice'],
    #                 #       'linestoprintquation':sale_id,
    #                 #       'linestoprintinvoice':self.id}
    #                 # self.printinvoicetoline.create({'sequance': invo[2]['sequance'],
    #                 #       'description': invo[2]['description'],
    #                 #       'uquantity': invo[2]['uquantity'],
    #                 #       'uprice': invo[2]['uprice'],
    #                 #       'linestoprintquation':sale_id,
    #                 #       'linestoprintinvoice':self.id})
    #                 #self.env.cr.execute("insert into account_move_printedinvoice_lines (sequance,description,uquantity,uprice,linestoprintquation,linestoprintinvoice) values("+str(invo[2]['sequance'])+",'"+invo[2]['description']+"',"+str(invo[2]['uquantity'])+","+str(invo[2]['uprice'])+","+str(sale_id)+","+str(self.id)+")")
    #                 print("kkkkkkkkkkkkkkkkkkk")
    #
    #     return True
    @api.depends('printinvoicetoline', 'letteraltotal')
    def _total2word(self):
        num = math.modf(sum([line.total for line in self.printinvoicetoline]))
        if (sum([line.total for line in self.printinvoicetoline]) == 0):
            self.letteraltotal = ''
        else:
            intnum = sum([line.total for line in self.printinvoicetoline])
            geneh = Tafneta().num2words(str(int(sum([line.total for line in self.printinvoicetoline]))))
            number = geneh + " جنيه مصري"
            frac, whole = math.modf(sum([line.total for line in self.printinvoicetoline]))
            kersh = str(sum([line.total for line in self.printinvoicetoline])).split('.')[1]
            print(sum([line.total for line in self.printinvoicetoline]))
            if int(kersh) > 0:
                if len(kersh) == 1:
                    kersh += "0"
                number += " و " + Tafneta().ashrat(kersh) + " قرشا "

            number += " فقط لا غير"
            self.letteraltotal = number
        pass

    pass


class PrintInvoice(models.Model):
    # _name="acount.move.printinvoice"
    _inherit = "sale.order"

    printquationtoline = fields.One2many('account.move.printedinvoice.lines', 'linestoprintquation')
    is_equal_total = fields.Boolean(string="IS Equal", store=True, compute='compute_is_equal_total2')
    customerType=fields.Selection(selection=[('patient','Patient'),('hospital','Hospital'),('doctor','Doctor')],string="Customer Type Is :")
    patientidimg=fields.Binary(string="Personal Id Photo")



    @api.depends('amount_total', 'printquationtoline')
    def compute_is_equal_total2(self):
        for rec in self:
            rec.is_equal_total = False
            total = 0.0
            for line in rec.printquationtoline:
                total += line.total
            rec.is_equal_total = (rec.amount_total - total >= -1 and rec.amount_total - total <= 1)

    pass
    lastinvoice = fields.Many2one ("account.move", compute='_getlastinvoice')

    def _getlastinvoice(self):
        if self.printquationtoline.ids and self.invoice_ids:
            ln=max(self.invoice_ids.ids)
            invo=self.env['account.move'].search([('id','=',ln)])
            if invo.state!='cancel':
                self.lastinvoice = invo.id
            else:
                self.lastinvoice = None
        else:
            self.lastinvoice = None

        # pass


class PrintInvoice1(models.Model):
    _name = "account.move.printedinvoice.lines"
    # _inherit = ['mail.thread']

    sequance = fields.Integer("Sequance")
    product_id=fields.Many2one(comodel_name="product.product",string="Product")
    description = fields.Char("description")
    uquantity = fields.Float("Quantity")
    uprice = fields.Float("Price")
    total = fields.Float("Total", compute='_computeTotal')
    linestoprintinvoice = fields.Many2one("account.move")
    linestoprintquation = fields.Many2one("sale.order")
    tax_ids=fields.Many2many(comodel_name="account.tax",string="Taxes")
    discount_amount=fields.Float("Discount Amount")
    #acctualitemprice=fields.Float("Actual Price",compute='get_actual_Price',store=True)#get pure item price without tax included

    def get_actual_Price(self):
        for rec in self:
            includedtax=0
            for tax in rec.tax_ids:
                if tax.price_include:
                    includedtax+=(rec.uprice)*tax.amount
            rec.acctualitemprice=rec.uprice-(includedtax/100)



    # designation = fields.Char(string='Designation', track_visibility='always')
    #
    @api.depends('total', 'uquantity', 'uprice','tax_ids','discount_amount')
    def _computeTotal(self):
        for record in self:
            includeTax=0
            for tax in record.tax_ids:
                if not tax.price_include:
                    includeTax+=((record.uquantity * record.uprice)-record.discount_amount)*tax.amount

            record.total = ((record.uquantity * record.uprice)-record.discount_amount)+(includeTax/100)
        pass

    pass


# class quationtoinvoice(models.Model):
#     _inherit = "sale.order"
#
#     def _prepare_invoice(self):
#         invoice_vals = super(sale_order, self)._prepare_invoice()
#         # for printquationtoline in self:
#         #     pass
#         #invoice_vals['printinvoicetoline'] = self.printquationtoline
#         #print(invoice_vals['printinvoicetoline'])
#         return invoice_vals
#         pass
#     pass
class sale_advance_payment_inv1(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice1(self, order, so_line, amount):#hashed
       # invoice = super(sale_advance_payment_inv1, self)._create_invoice(order, so_line, amount)
        # invoice.printinvoicetoline = order.printquationtoline.id
        for invo in order.printquationtoline:
            #     print("----------------->")
            #     print(invo)
            #     print("################")
            #     print(invo.sequence)
            orderinvoice = self.env['account.move.printedinvoice.lines'].search(
                [('linestoprintquation', '=', order.id)])
            orderinvoice.write({'linestoprintinvoice': invoice.id})
            # self.env['account.move.printedinvoice.lines'].create({'sequance':invo.sequence,'description':invo.description,'uquantity':invo.uquantity,'uprice':invo.uprice,'linestoprintinvoice':invoice.id,'linestoprintquation':invo.id});
            # self.env.cr.commit()
        #     pass

        #return invoice

    def _create_invoice(self, order, so_line, amount):
        invoice = super(sale_advance_payment_inv1, self)._create_invoice(order, so_line, amount)
        invoices=self.env['account.move.printedinvoice.lines'].search([('linestoprintquation','=',order.id)])
        if invoices:
            finvoice=min(invoices.ids)
        else:
            finvoice=invoice.id

        for invo in order.printquationtoline:
            invo.write({'linestoprintinvoice':finvoice})
        return invoice

        pass

    def create_invoices1(self):#hashed
        # super(self).create_invoices(self)
        #invoices = super().create_invoices()
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        print("")

        # invoice.printinvoicetoline = order.printquationtoline.id
        _logger.debug(sale_orders)
        #       #  invoid=invoices['domain'].split(",")

        # raise UserError(sale_orders.invoice_ids)
        #sale_orders.printquationtoline.write({'lastinv':sale_orders.invoice_ids[-1].id})
        for invo in sale_orders.printquationtoline:
            # raise UserError(invo.linestoprintinvoice)
            data = {
                # 'sequance': invo.sequance,
                # 'description': invo.description,
                # 'uquantity': invo.uquantity,
                # 'uprice': invo.uprice,
                # 'total': invo.total,
                'linestoprintinvoice': sale_orders.invoice_ids[-1].id,
                'linestoprintquation': sale_orders.id,
                #'lastinv': sale_orders.invoice_ids[-1].id
            }

            #             }
            # raise UserError(invo.linestoprintinvoice)
            #     print("----------------->")
            #     print(invo)
            #     print("################")
            # print(invo.sequence)
            # orderinvoice = self.env['account.move.printedinvoice.lines'].search([('linestoprintquation', '=', sale_orders.id)])
            # invo.write({'linestoprintinvoice':sale_orders.invoice_ids[-1].id})
            invo.write(data)
            # invo.write({'linestoprintinvoice':sale_orders.invoice_ids.id})
            # self.env['account.move.printedinvoice.lines'].create({'sequance':invo.sequence,'description':invo.description,'uquantity':invo.uquantity,'uprice':invo.uprice,'linestoprintinvoice':invoice.id,'linestoprintquation':invo.id});
            # self.env.cr.commit()
        #     pass


        #return invoices

    def create_invoices(self):#hashed
        currentinvoices = super().create_invoices()
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        invoices = self.env['account.move.printedinvoice.lines'].search([('linestoprintquation', '=', sale_orders.id)])

        if invoices.linestoprintinvoice.ids:
            finvoice = min(invoices.linestoprintinvoice.ids)
        else:
            finvoice = sale_orders.invoice_ids[0].id

        for invo in sale_orders.printquationtoline:
            invo.write({'linestoprintinvoice': finvoice})
        return currentinvoices
        pass

    pass
