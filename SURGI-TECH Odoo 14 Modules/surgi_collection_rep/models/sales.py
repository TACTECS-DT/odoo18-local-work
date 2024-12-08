from odoo import models, fields, api
class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    city = fields.Char(related='partner_id.city', readonly=True)
    collection_rep = fields.Many2one('res.users', 'Collection Rep', track_visibility='onchange',)

    # account_moves_ids = fields.Many2many(comodel_name="", relation="", column1="", column2="", string="", )

    @api.onchange('partner_id')
    def compute_collection_rep(self):
        if self.partner_id:
            self.collection_rep=self.partner_id.collection_rep.id
        else:
            self.collection_rep =False


class RESPartnerInherit(models.Model):
    _inherit = 'res.partner'

    collection_rep = fields.Many2one('res.users', 'Collection Rep', track_visibility='onchange')

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'
    collection_rep = fields.Many2one('res.users', 'Collection Rep', track_visibility='onchange')
    # , related = 'partner_id.collection_rep',
    # field is selection(Deal - Problem - Permitted - Unpermitted)
    collection_state = fields.Selection(string="Collection Status", selection=[
        ('Deal', 'Deal'), ('Problem', 'Problem'),
        ('Permitted', 'Permitted'), ('Unpermitted', 'Unpermitted'),
    ],)
    is_collection_rep = fields.Boolean(string="",compute='compute_is_collection_rep'  )

    is_invoice_attach = fields.Boolean(string="Invoice Attach",defualt=False  )
    @api.depends('partner_id')
    def compute_is_collection_rep(self):
        for rec in self:
            rec.is_collection_rep=False
            if self.partner_id:
                rec.collection_rep = rec.partner_id.collection_rep.id
                rec.is_collection_rep = True
            else:
                self.collection_rep = False

    def button_invoice_attach(self):
        print("GGGGGGGGGGGGGGGGGGGGGGGG")
        self.is_invoice_attach=True




