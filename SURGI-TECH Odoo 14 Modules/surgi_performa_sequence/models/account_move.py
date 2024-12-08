
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"


    account_performa_sequence = fields.Char(string="Performa sequence" ,store=True,compute="_compute_account_performa_sequence")


    def surgi_invoice_print_performa(self):
        if self.amount_total != round(self.totalprintedprice,2):
            raise Warning("Total in invoice Lines not Equal in print Invoice")
        #return {'type': 'ir.actions.report', 'report_name': 'surgi_invoice_print.report_invoice_demo','report_type': "qweb-pdf" } 
        self.printedby=self.env.user.id
        return self.env.ref("surgi_performa_sequence.report_performa_invoice").report_action(self, config=False)
    
    
    
    @api.depends('partner_id','partner_id.create_performa_sequence')
    def _compute_account_performa_sequence(self):
        for rec in self:
            if self.env.context.get('stop_performa_sequence') == False:
                if rec.state == 'draft':
                    if rec.partner_id:
                        if rec.partner_id.create_performa_sequence:
                            rec.account_performa_sequence = self.env['ir.sequence'].next_by_code('account.move.performa') or ''
