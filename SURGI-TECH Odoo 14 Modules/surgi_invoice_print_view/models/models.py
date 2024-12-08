from odoo import models, fields, api


class print_invoice_line_rel(models.Model):
    _inherit="account.move.printedinvoice.lines"


    invoice_state = fields.Selection(related='linestoprintinvoice.state',string='State',store=True)


    def name_get(self):
        res = []
        for rec in self:
            name = u"{} ({})".format(rec.linestoprintinvoice.name, rec.description)
            res.append((rec.id, name))
        return res



class AccountMove(models.Model):
    _inherit = "account.move"
    sale_order_op_id = fields.Many2one('sale.order',compute='get_sale_order_id_for_print_invoice',store=True)
    @api.depends('invoice_line_ids.sale_line_ids')
    def get_sale_order_id_for_print_invoice(self):
        for rec in self:
            if rec.invoice_line_ids:
                if rec.invoice_line_ids.sale_line_ids:
                    rec.sale_order_op_id = rec.invoice_line_ids.sale_line_ids[0].order_id.id

    po_type = fields.Char(string='PO Type',readonly=False,store=True)