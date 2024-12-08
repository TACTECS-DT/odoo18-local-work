from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    is_surgi_printed = fields.Boolean(string="Is Surgi Printed")#, tracking=True
    is_printed = fields.Boolean(string="IS Printed", tracking=True)
    printed_num = fields.Integer(string="Report Number", required=False, )

    is_equal_total = fields.Boolean(string="IS Equal", store=True, compute='compute_is_equal_total2')
    is_equal_total2 = fields.Boolean(string="", compute='compute_is_equal_total21')
    totalprintedprice=fields.Float("Printed Total",compute="gettotalprintedinvoice")
    printedby=fields.Many2one("res.users", string="Printed By",track_visibility=True )
    def gettotalprintedinvoice(self):
        total=0.0
        for i in self.printinvoicetoline:
            total+=i.total
        self.totalprintedprice= total
        pass
    def surgi_invoice_print(self):
        if self.amount_total != round(self.totalprintedprice,2):
            raise Warning("Total in invoice Lines not Equal in print Invoice")
        #return {'type': 'ir.actions.report', 'report_name': 'surgi_invoice_print.report_invoice_demo','report_type': "qweb-pdf" } 
        self.printedby=self.env.user.id
        return self.env.ref("surgi_invoice_print.surgi_invoice_print_report").report_action(self, config=False)
    def surgi_credit_note_print(self):
        # if not self.ref :
        #     raise Warning("This Invoice not Reversed")
        #return {'type': 'ir.actions.report', 'report_name': 'surgi_invoice_print.report_invoice_demo','report_type': "qweb-pdf" }
        # self.printedby=self.env.user.id
        return self.env.ref("surgi_invoice_print.surgi_credit_note_print_report").report_action(self, config=False)

    @api.depends('amount_total', 'printinvoicetoline')
    def compute_is_equal_total2(self):
        for rec in self:
            rec.is_equal_total = False
            rec.is_equal_total2 = False
            total = 0.0
            for line in rec.printinvoicetoline:
                total += line.total
            #if rec.amount_total == total: 
            #rec.is_equal_total = (rec.amount_total-total>= -1 and rec.amount_total-total<=1 )
            if (rec.amount_total-total>= -1 and rec.amount_total-total<=1 ):
                rec.is_equal_total = True
                rec.is_equal_total2 = True
    @api.depends('amount_total', 'printinvoicetoline')
    def compute_is_equal_total21(self):
        for rec in self:
            rec.is_equal_total = False
            rec.is_equal_total2 = False
            total = 0.0
            for line in rec.printinvoicetoline:
                total += line.total
            #if rec.amount_total == total: 
            #rec.is_equal_total = (rec.amount_total-total>= -1 and rec.amount_total-total<=1 )
            if (rec.amount_total-total>= -1 and rec.amount_total-total<=1 ):
                rec.is_equal_total = True
                rec.is_equal_total2 = True           



class ReportAccountMovePrinted(models.AbstractModel):
    _name = 'report.surgi_invoice_print.report_invoice_demo'

    @api.model
    def _get_report_values(self, docids, data=None):

        docs = self.env['account.move'].browse(docids)

        docs.is_surgi_printed=True
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
        }

class ReportAccountHashIntegrity(models.AbstractModel):
    _name = 'report.account.report_invoice_with_payments'
    _description = 'Get hash integrity result as PDF.'

    @api.model
    def _get_report_values(self, docids, data=None):

        docs = self.env['account.move'].browse(docids)

        docs.is_printed=True
        docs.printed_num+=1
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
        }
class SaleOrder(models.Model):
    _inherit = "sale.order"

    force_invoiced = fields.Boolean(
        string="Force invoice",
        help="When you set this field, the sales order will be considered as "
        "fully invoiced, even when there may be ordered or delivered "
        "quantities pending to invoice.",
        readonly=True,
        states={"done": [("readonly", False)], "sale": [("readonly", False)]},
        copy=False,
    )


    @api.depends("force_invoiced")
    def _get_invoice_status(self):
        super(SaleOrder, self)._get_invoice_status()
        for order in self.filtered(
            lambda so: so.force_invoiced and so.state in ("sale", "done")
        ):
            order.invoice_status = "invoiced"

