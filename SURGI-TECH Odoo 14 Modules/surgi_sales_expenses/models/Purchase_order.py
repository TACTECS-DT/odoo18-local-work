from odoo import models, fields, api


class account_move_po_type(models.Model):
    _inherit = 'account.move'
    po_type = fields.Char(string='PO Type',readonly=True)
    fillter_date =fields.Date(string="Filter Date",store=True)

class purchase_po_type(models.Model):
    _inherit = 'purchase.order'
    po_type = fields.Selection(
        [("Medical", "Medical"), ("Non-Medical", "Non-Medical"),
         ("Administrative", "Administrative")], store=True,string="PO Type")

    def _prepare_invoice(self):
        res = super(purchase_po_type, self)._prepare_invoice()
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'in_invoice')
        journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        partner_invoice_id = self.partner_id.address_get(['invoice'])['invoice']
        invoice_vals = {
            'ref': self.partner_ref or '',
            'move_type': move_type,
            'narration': self.notes,
            'po_type': self.po_type,
            'currency_id': self.currency_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'partner_id': partner_invoice_id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(partner_invoice_id)).id,
            'payment_reference': self.partner_ref or '',
            'partner_bank_id': self.partner_id.bank_ids[:1].id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
        }
        return invoice_vals

class stock_picking_po_type(models.Model):
    _inherit = 'stock.picking'
    po_type = fields.Char(string='PO Type',readonly=True,compute='po_type_form_purchase')

    def po_type_form_purchase(self):


        for objs in self:
            objs_av = ''

            obj_test = self.env['purchase.order'].search([('name', '=', objs.origin)])

            for val in obj_test:
                objs_av = val.po_type
                print(objs_av)
            print(objs_av)
            objs.po_type = objs_av
